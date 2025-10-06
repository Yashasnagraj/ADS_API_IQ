#!/usr/bin/env python3
"""
Advanced KPI Calculation Algorithms for MarketingIQ Dashboard
Industry-standard formulas and intelligent calculations
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class KPICalculator:
    """Advanced KPI calculation engine with industry-standard algorithms"""

    def __init__(self, db_path: str = 'google_ads_data.db'):
        self.db_path = db_path
        self.conn = None
        self.industry_benchmarks = {
            'ctr': {'excellent': 5.0, 'good': 3.0, 'average': 2.0, 'poor': 1.0},
            'conversion_rate': {'excellent': 5.0, 'good': 3.0, 'average': 2.0, 'poor': 1.0},
            'cpc': {'excellent': 1.0, 'good': 2.0, 'average': 3.0, 'poor': 5.0},
            'roas': {'excellent': 400, 'good': 300, 'average': 200, 'poor': 100},
            'quality_score': {'excellent': 8, 'good': 6, 'average': 5, 'poor': 3}
        }

    def get_connection(self):
        """Get database connection"""
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
        return self.conn

    # ==================== CORE KPI ALGORITHMS ====================

    def calculate_realtime_metrics(self, customer_id: Optional[int] = None) -> Dict:
        """
        Calculate real-time metrics from actual database data
        Uses last 24 hours for "real-time" approximation
        """
        conn = self.get_connection()

        # Build WHERE clause
        where_conditions = ["datetime(ck.date) >= datetime('now', '-1 day')"]
        if customer_id:
            where_conditions.append(f"ck.customer_id = {customer_id}")
        where_clause = " AND ".join(where_conditions)

        query = f"""
        WITH hourly_metrics AS (
            SELECT
                strftime('%Y-%m-%d %H', datetime(ck.date)) as hour,
                SUM(ck.impressions) as impressions,
                SUM(ck.clicks) as clicks,
                SUM(ck.conversions) as conversions,
                SUM(ck.cost_micros) / 1000000.0 as cost,
                SUM(ck.conversion_value) as revenue,
                AVG(ck.ctr) as ctr,
                AVG(ck.conversion_rate) as conversion_rate,
                AVG(ck.avg_cpc_micros) / 1000000.0 as avg_cpc
            FROM campaign_keywords ck
            WHERE {where_clause}
            GROUP BY hour
            ORDER BY hour DESC
            LIMIT 24
        )
        SELECT
            COALESCE(SUM(impressions), 0) as total_impressions,
            COALESCE(SUM(clicks), 0) as total_clicks,
            COALESCE(SUM(conversions), 0) as total_conversions,
            COALESCE(SUM(cost), 0) as total_cost,
            COALESCE(SUM(revenue), 0) as total_revenue,
            COALESCE(AVG(ctr), 0) as avg_ctr,
            COALESCE(AVG(conversion_rate), 0) as avg_conversion_rate,
            COALESCE(AVG(avg_cpc), 0) as avg_cpc,
            COUNT(*) as data_points
        FROM hourly_metrics
        """

        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        if result and result[8] > 0:  # Has data points
            # Calculate velocity (rate of change)
            velocity_query = f"""
            SELECT
                (SUM(CASE WHEN datetime(ck.date) >= datetime('now', '-1 hour') THEN ck.clicks END) -
                 SUM(CASE WHEN datetime(ck.date) < datetime('now', '-1 hour')
                     AND datetime(ck.date) >= datetime('now', '-2 hours') THEN ck.clicks END)) as click_velocity,
                (SUM(CASE WHEN datetime(ck.date) >= datetime('now', '-1 hour') THEN ck.conversions END) -
                 SUM(CASE WHEN datetime(ck.date) < datetime('now', '-1 hour')
                     AND datetime(ck.date) >= datetime('now', '-2 hours') THEN ck.conversions END)) as conv_velocity
            FROM campaign_keywords ck
            WHERE {where_clause}
            """

            cursor.execute(velocity_query)
            velocity = cursor.fetchone()

            return {
                'timestamp': datetime.now().isoformat(),
                'impressions': int(result[0]),
                'clicks': int(result[1]),
                'conversions': int(result[2]),
                'cost': round(result[3], 2),
                'revenue': round(result[4], 2),
                'ctr': round(result[5], 2),
                'conversion_rate': round(result[6], 2),
                'avg_cpc': round(result[7], 2),
                'click_velocity': velocity[0] if velocity[0] else 0,
                'conversion_velocity': velocity[1] if velocity[1] else 0,
                'data_freshness': 'live' if result[8] >= 20 else 'partial'
            }
        else:
            # No recent data - use projections from historical data
            return self._calculate_projected_realtime(customer_id)

    def _calculate_projected_realtime(self, customer_id: Optional[int] = None) -> Dict:
        """Calculate projected real-time metrics based on historical patterns"""
        conn = self.get_connection()

        # Get same hour from last 7 days
        current_hour = datetime.now().hour
        where_conditions = [f"CAST(strftime('%H', ck.date) AS INTEGER) = {current_hour}"]
        if customer_id:
            where_conditions.append(f"ck.customer_id = {customer_id}")
        where_clause = " AND ".join(where_conditions)

        query = f"""
        SELECT
            AVG(ck.impressions) as avg_impressions,
            AVG(ck.clicks) as avg_clicks,
            AVG(ck.conversions) as avg_conversions,
            AVG(ck.cost_micros) / 1000000.0 as avg_cost,
            AVG(ck.conversion_value) as avg_revenue,
            MAX(ck.impressions) - MIN(ck.impressions) as range_impressions,
            MAX(ck.clicks) - MIN(ck.clicks) as range_clicks
        FROM campaign_keywords ck
        WHERE {where_clause}
        AND ck.date >= date('now', '-7 days')
        """

        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        if result and result[0]:
            # Add some controlled randomness based on standard deviation
            impressions = max(0, int(result[0] + np.random.normal(0, result[5] if result[5] else result[0] * 0.1)))
            clicks = max(0, int(result[1] + np.random.normal(0, result[6] if result[6] else result[1] * 0.1)))

            return {
                'timestamp': datetime.now().isoformat(),
                'impressions': impressions,
                'clicks': clicks,
                'conversions': max(0, int(result[2])),
                'cost': round(result[3], 2) if result[3] else 0,
                'revenue': round(result[4], 2) if result[4] else 0,
                'ctr': round((clicks / impressions * 100) if impressions > 0 else 0, 2),
                'conversion_rate': round((result[2] / clicks * 100) if clicks > 0 else 0, 2),
                'avg_cpc': round((result[3] / clicks) if clicks > 0 else 0, 2),
                'data_freshness': 'projected'
            }

        return {
            'timestamp': datetime.now().isoformat(),
            'impressions': 0,
            'clicks': 0,
            'conversions': 0,
            'cost': 0,
            'revenue': 0,
            'ctr': 0,
            'conversion_rate': 0,
            'avg_cpc': 0,
            'data_freshness': 'no_data'
        }

    def calculate_roas(self, customer_id: Optional[int] = None, period_days: int = 30) -> Dict:
        """
        Calculate Return on Ad Spend (ROAS)
        Formula: Revenue / Ad Spend * 100
        """
        conn = self.get_connection()

        where_conditions = [f"ck.date >= date('now', '-{period_days} days')"]
        if customer_id:
            where_conditions.append(f"ck.customer_id = {customer_id}")
        where_clause = " AND ".join(where_conditions)

        query = f"""
        SELECT
            SUM(ck.conversion_value) as total_revenue,
            SUM(ck.cost_micros) / 1000000.0 as total_cost,
            COUNT(DISTINCT ck.campaign_id) as campaign_count,
            AVG(c.optimization_score) as avg_optimization_score
        FROM campaign_keywords ck
        JOIN campaigns c ON ck.campaign_id = c.campaign_id
        WHERE {where_clause}
        """

        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        if result and result[1] and result[1] > 0:
            roas = (result[0] / result[1]) * 100 if result[0] else 0

            # Determine performance level
            if roas >= self.industry_benchmarks['roas']['excellent']:
                performance = 'excellent'
            elif roas >= self.industry_benchmarks['roas']['good']:
                performance = 'good'
            elif roas >= self.industry_benchmarks['roas']['average']:
                performance = 'average'
            else:
                performance = 'poor'

            return {
                'roas': round(roas, 2),
                'revenue': round(result[0], 2) if result[0] else 0,
                'spend': round(result[1], 2),
                'profit': round(result[0] - result[1], 2) if result[0] else -round(result[1], 2),
                'campaign_count': result[2],
                'optimization_score': round(result[3], 1) if result[3] else 0,
                'performance': performance,
                'benchmark': self.industry_benchmarks['roas'][performance]
            }

        return {
            'roas': 0,
            'revenue': 0,
            'spend': 0,
            'profit': 0,
            'campaign_count': 0,
            'optimization_score': 0,
            'performance': 'no_data'
        }

    def calculate_customer_lifetime_value(self, customer_id: Optional[int] = None) -> Dict:
        """
        Calculate Customer Lifetime Value (CLV/LTV)
        Formula: (Average Order Value × Purchase Frequency) × Customer Lifespan
        """
        conn = self.get_connection()

        where_clause = f"WHERE ck.customer_id = {customer_id}" if customer_id else ""

        # Get customer metrics
        query = f"""
        WITH customer_metrics AS (
            SELECT
                ck.customer_id,
                MIN(ck.date) as first_purchase,
                MAX(ck.date) as last_purchase,
                COUNT(DISTINCT ck.date) as purchase_days,
                SUM(ck.conversion_value) as total_revenue,
                SUM(ck.conversions) as total_conversions,
                AVG(ck.conversion_value / NULLIF(ck.conversions, 0)) as avg_order_value
            FROM campaign_keywords ck
            {where_clause}
            GROUP BY ck.customer_id
        )
        SELECT
            customer_id,
            julianday(last_purchase) - julianday(first_purchase) as customer_age_days,
            purchase_days,
            total_revenue,
            total_conversions,
            avg_order_value,
            total_revenue / NULLIF(purchase_days, 0) as revenue_per_day
        FROM customer_metrics
        """

        df = pd.read_sql_query(query, conn)

        if not df.empty:
            # Calculate average metrics across customers
            avg_lifespan_days = df['customer_age_days'].mean()
            avg_purchase_frequency = df['purchase_days'].mean()
            avg_order_value = df['avg_order_value'].mean()

            # Projected lifetime (typically 2-3 years for digital)
            projected_lifetime_days = max(avg_lifespan_days, 730)  # At least 2 years

            # Calculate CLV
            if avg_order_value and avg_purchase_frequency:
                purchase_rate = avg_purchase_frequency / max(avg_lifespan_days, 1)
                clv = avg_order_value * (purchase_rate * projected_lifetime_days)

                # Calculate retention rate
                active_customers = len(df[df['customer_age_days'] > 30])
                total_customers = len(df)
                retention_rate = (active_customers / total_customers * 100) if total_customers > 0 else 0

                return {
                    'clv': round(clv, 2),
                    'avg_order_value': round(avg_order_value, 2),
                    'purchase_frequency': round(avg_purchase_frequency, 1),
                    'avg_customer_lifespan_days': round(avg_lifespan_days, 0),
                    'projected_lifetime_days': projected_lifetime_days,
                    'retention_rate': round(retention_rate, 1),
                    'total_customers': total_customers,
                    'revenue_per_customer': round(df['total_revenue'].mean(), 2)
                }

        return {
            'clv': 0,
            'avg_order_value': 0,
            'purchase_frequency': 0,
            'avg_customer_lifespan_days': 0,
            'retention_rate': 0,
            'total_customers': 0
        }

    def calculate_customer_acquisition_cost(self, customer_id: Optional[int] = None, period_days: int = 30) -> Dict:
        """
        Calculate Customer Acquisition Cost (CAC)
        Formula: Total Marketing Spend / Number of New Customers
        """
        conn = self.get_connection()

        where_conditions = [f"ck.date >= date('now', '-{period_days} days')"]
        if customer_id:
            where_conditions.append(f"ck.customer_id = {customer_id}")
        where_clause = " AND ".join(where_conditions)

        query = f"""
        WITH acquisition_metrics AS (
            SELECT
                SUM(ck.cost_micros) / 1000000.0 as total_spend,
                COUNT(DISTINCT CASE
                    WHEN ck.conversions > 0 THEN ck.customer_id
                END) as converting_customers,
                SUM(ck.conversions) as total_conversions,
                AVG(ck.conversion_rate) as avg_conversion_rate
            FROM campaign_keywords ck
            WHERE {where_clause}
        )
        SELECT
            total_spend,
            converting_customers,
            total_conversions,
            avg_conversion_rate,
            total_spend / NULLIF(converting_customers, 0) as cac,
            total_spend / NULLIF(total_conversions, 0) as cost_per_conversion
        FROM acquisition_metrics
        """

        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        if result and result[1] and result[1] > 0:
            cac = result[4] if result[4] else 0

            # Get CLV for CAC:CLV ratio
            clv_data = self.calculate_customer_lifetime_value(customer_id)
            clv = clv_data['clv']

            cac_to_clv_ratio = (cac / clv) if clv > 0 else 0

            # Determine if CAC is healthy (typically CAC:CLV should be 1:3 or better)
            if cac_to_clv_ratio <= 0.33 and cac_to_clv_ratio > 0:
                health = 'excellent'
            elif cac_to_clv_ratio <= 0.5:
                health = 'good'
            elif cac_to_clv_ratio <= 1:
                health = 'acceptable'
            else:
                health = 'poor'

            return {
                'cac': round(cac, 2),
                'total_spend': round(result[0], 2),
                'new_customers': result[1],
                'total_conversions': result[2],
                'avg_conversion_rate': round(result[3], 2) if result[3] else 0,
                'cost_per_conversion': round(result[5], 2) if result[5] else 0,
                'clv': round(clv, 2),
                'cac_to_clv_ratio': round(cac_to_clv_ratio, 2),
                'health_status': health,
                'payback_period_days': round((cac / (clv / 730)) if clv > 0 else 0, 0)  # Days to recover CAC
            }

        return {
            'cac': 0,
            'total_spend': 0,
            'new_customers': 0,
            'total_conversions': 0,
            'health_status': 'no_data'
        }

    def calculate_attribution_weighted_conversions(self, customer_id: Optional[int] = None) -> Dict:
        """
        Calculate attribution-weighted conversions using data-driven attribution
        Considers multiple touchpoints in the customer journey
        """
        conn = self.get_connection()

        where_clause = f"WHERE ck.customer_id = {customer_id}" if customer_id else ""

        # Get conversion paths
        query = f"""
        WITH conversion_paths AS (
            SELECT
                ck.customer_id,
                ck.campaign_id,
                ck.keyword_id,
                ck.date,
                ck.clicks,
                ck.conversions,
                ck.conversion_value,
                ROW_NUMBER() OVER (PARTITION BY ck.customer_id ORDER BY ck.date) as touchpoint_order,
                COUNT(*) OVER (PARTITION BY ck.customer_id) as total_touchpoints
            FROM campaign_keywords ck
            {where_clause}
            AND ck.clicks > 0
        )
        SELECT
            campaign_id,
            keyword_id,
            touchpoint_order,
            total_touchpoints,
            clicks,
            conversions,
            conversion_value,
            CASE
                WHEN total_touchpoints = 1 THEN 1.0
                WHEN touchpoint_order = 1 THEN 0.4  -- First touch
                WHEN touchpoint_order = total_touchpoints THEN 0.4  -- Last touch
                ELSE 0.2 / (total_touchpoints - 2)  -- Middle touches
            END as attribution_weight
        FROM conversion_paths
        WHERE conversions > 0
        """

        df = pd.read_sql_query(query, conn)

        if not df.empty:
            # Calculate weighted conversions
            df['weighted_conversions'] = df['conversions'] * df['attribution_weight']
            df['weighted_value'] = df['conversion_value'] * df['attribution_weight']

            # Aggregate by campaign
            campaign_attribution = df.groupby('campaign_id').agg({
                'weighted_conversions': 'sum',
                'weighted_value': 'sum',
                'conversions': 'sum',
                'attribution_weight': 'mean'
            }).round(2)

            return {
                'total_weighted_conversions': round(df['weighted_conversions'].sum(), 2),
                'total_weighted_value': round(df['weighted_value'].sum(), 2),
                'total_raw_conversions': df['conversions'].sum(),
                'attribution_model': 'data_driven',
                'touchpoints_analyzed': len(df),
                'campaign_attribution': campaign_attribution.to_dict(),
                'avg_touchpoints_per_conversion': round(df['total_touchpoints'].mean(), 1)
            }

        return {
            'total_weighted_conversions': 0,
            'total_weighted_value': 0,
            'attribution_model': 'data_driven',
            'touchpoints_analyzed': 0
        }

    def calculate_quality_score_impact(self, customer_id: Optional[int] = None) -> Dict:
        """
        Calculate the financial impact of Quality Score on campaigns
        Lower Quality Score = Higher CPC
        """
        conn = self.get_connection()

        where_clause = f"AND k.customer_id = {customer_id}" if customer_id else ""

        query = f"""
        SELECT
            k.quality_score,
            COUNT(*) as keyword_count,
            AVG(ck.avg_cpc_micros) / 1000000.0 as avg_cpc,
            SUM(ck.cost_micros) / 1000000.0 as total_cost,
            SUM(ck.clicks) as total_clicks,
            AVG(ck.ctr) as avg_ctr,
            AVG(ck.conversion_rate) as avg_conversion_rate
        FROM keywords k
        JOIN campaign_keywords ck ON k.keyword_id = ck.keyword_id
        WHERE k.quality_score IS NOT NULL
        {where_clause}
        GROUP BY k.quality_score
        ORDER BY k.quality_score
        """

        df = pd.read_sql_query(query, conn)

        if not df.empty:
            # Calculate potential savings if all keywords had QS >= 7
            high_qs_cpc = df[df['quality_score'] >= 7]['avg_cpc'].mean() if len(df[df['quality_score'] >= 7]) > 0 else df['avg_cpc'].min()

            potential_savings = 0
            improvement_opportunities = []

            for _, row in df.iterrows():
                if row['quality_score'] < 7 and row['avg_cpc'] > high_qs_cpc:
                    savings = (row['avg_cpc'] - high_qs_cpc) * row['total_clicks']
                    potential_savings += savings
                    improvement_opportunities.append({
                        'quality_score': int(row['quality_score']),
                        'keyword_count': int(row['keyword_count']),
                        'current_cpc': round(row['avg_cpc'], 2),
                        'potential_cpc': round(high_qs_cpc, 2),
                        'potential_savings': round(savings, 2)
                    })

            return {
                'avg_quality_score': round(df['quality_score'].mean(), 1),
                'total_keywords_analyzed': int(df['keyword_count'].sum()),
                'potential_monthly_savings': round(potential_savings, 2),
                'high_qs_keywords': int(df[df['quality_score'] >= 7]['keyword_count'].sum()),
                'low_qs_keywords': int(df[df['quality_score'] < 5]['keyword_count'].sum()),
                'improvement_opportunities': improvement_opportunities[:5],  # Top 5
                'avg_cpc_by_qs': df[['quality_score', 'avg_cpc']].round(2).to_dict('records')
            }

        return {
            'avg_quality_score': 0,
            'potential_monthly_savings': 0,
            'improvement_opportunities': []
        }

    def calculate_anomaly_scores(self, customer_id: Optional[int] = None, sensitivity: float = 2.0) -> Dict:
        """
        Detect anomalies in KPIs using statistical methods
        Uses z-score for anomaly detection
        """
        conn = self.get_connection()

        where_conditions = ["ck.date >= date('now', '-30 days')"]
        if customer_id:
            where_conditions.append(f"ck.customer_id = {customer_id}")
        where_clause = " AND ".join(where_conditions)

        query = f"""
        SELECT
            date,
            SUM(impressions) as impressions,
            SUM(clicks) as clicks,
            SUM(conversions) as conversions,
            SUM(cost_micros) / 1000000.0 as cost,
            AVG(ctr) as ctr,
            AVG(conversion_rate) as conversion_rate,
            AVG(avg_cpc_micros) / 1000000.0 as cpc
        FROM campaign_keywords ck
        WHERE {where_clause}
        GROUP BY date
        ORDER BY date
        """

        df = pd.read_sql_query(query, conn)

        if len(df) > 7:  # Need enough data for statistics
            anomalies = {}

            for col in ['impressions', 'clicks', 'conversions', 'cost', 'ctr', 'conversion_rate', 'cpc']:
                if col in df.columns:
                    # Calculate z-scores
                    mean = df[col].mean()
                    std = df[col].std()

                    if std > 0:
                        df[f'{col}_zscore'] = (df[col] - mean) / std

                        # Identify anomalies (z-score > sensitivity)
                        anomaly_dates = df[abs(df[f'{col}_zscore']) > sensitivity]

                        if not anomaly_dates.empty:
                            anomalies[col] = {
                                'dates': anomaly_dates['date'].tolist(),
                                'values': anomaly_dates[col].tolist(),
                                'z_scores': anomaly_dates[f'{col}_zscore'].tolist(),
                                'mean': round(mean, 2),
                                'std': round(std, 2),
                                'anomaly_count': len(anomaly_dates)
                            }

            # Check for today's anomalies
            if not df.empty:
                latest = df.iloc[-1]
                alerts = []

                for col in anomalies:
                    if f'{col}_zscore' in latest and abs(latest[f'{col}_zscore']) > sensitivity:
                        direction = 'above' if latest[f'{col}_zscore'] > 0 else 'below'
                        alerts.append({
                            'metric': col,
                            'value': round(latest[col], 2),
                            'z_score': round(latest[f'{col}_zscore'], 2),
                            'direction': direction,
                            'severity': 'high' if abs(latest[f'{col}_zscore']) > 3 else 'medium'
                        })

                return {
                    'anomalies_detected': len(anomalies) > 0,
                    'metrics_with_anomalies': list(anomalies.keys()),
                    'anomaly_details': anomalies,
                    'current_alerts': alerts,
                    'sensitivity_level': sensitivity,
                    'analysis_period_days': len(df)
                }

        return {
            'anomalies_detected': False,
            'message': 'Insufficient data for anomaly detection'
        }

    def calculate_trend_analysis(self, customer_id: Optional[int] = None, period_days: int = 90) -> Dict:
        """
        Perform trend analysis using linear regression and moving averages
        """
        conn = self.get_connection()

        where_conditions = [f"ck.date >= date('now', '-{period_days} days')"]
        if customer_id:
            where_conditions.append(f"ck.customer_id = {customer_id}")
        where_clause = " AND ".join(where_conditions)

        query = f"""
        SELECT
            date,
            SUM(conversion_value) as revenue,
            SUM(cost_micros) / 1000000.0 as cost,
            SUM(conversions) as conversions,
            AVG(conversion_rate) as conversion_rate,
            AVG(ctr) as ctr
        FROM campaign_keywords ck
        WHERE {where_clause}
        GROUP BY date
        ORDER BY date
        """

        df = pd.read_sql_query(query, conn)

        if len(df) > 14:  # Need at least 2 weeks of data
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

            trends = {}

            for col in ['revenue', 'cost', 'conversions', 'conversion_rate', 'ctr']:
                if col in df.columns:
                    # Calculate moving averages
                    df[f'{col}_ma7'] = df[col].rolling(window=7, min_periods=1).mean()
                    df[f'{col}_ma30'] = df[col].rolling(window=30, min_periods=1).mean()

                    # Linear regression for trend
                    X = np.arange(len(df)).reshape(-1, 1)
                    y = df[col].values

                    model = LinearRegression()
                    model.fit(X, y)

                    # Calculate trend direction and strength
                    slope = model.coef_[0]
                    r_squared = model.score(X, y)

                    # Determine trend
                    if abs(slope) < 0.01:
                        trend = 'stable'
                    elif slope > 0:
                        trend = 'increasing'
                    else:
                        trend = 'decreasing'

                    # Forecast next 7 days
                    future_X = np.arange(len(df), len(df) + 7).reshape(-1, 1)
                    forecast = model.predict(future_X)

                    trends[col] = {
                        'current_value': round(df[col].iloc[-1], 2),
                        'ma7': round(df[f'{col}_ma7'].iloc[-1], 2),
                        'ma30': round(df[f'{col}_ma30'].iloc[-1], 2) if len(df) >= 30 else None,
                        'trend': trend,
                        'slope': round(slope, 4),
                        'r_squared': round(r_squared, 3),
                        'forecast_7day': [round(f, 2) for f in forecast],
                        'percent_change_7day': round(((df[col].iloc[-1] - df[col].iloc[-8]) / df[col].iloc[-8] * 100) if len(df) > 7 and df[col].iloc[-8] != 0 else 0, 2),
                        'volatility': round(df[col].std() / df[col].mean() * 100 if df[col].mean() != 0 else 0, 2)
                    }

            return {
                'analysis_period_days': period_days,
                'data_points': len(df),
                'trends': trends,
                'overall_health': self._determine_overall_health(trends)
            }

        return {
            'analysis_period_days': period_days,
            'message': 'Insufficient data for trend analysis'
        }

    def _determine_overall_health(self, trends: Dict) -> str:
        """Determine overall health based on trends"""
        positive_indicators = 0
        negative_indicators = 0

        # Check revenue trend
        if 'revenue' in trends:
            if trends['revenue']['trend'] == 'increasing':
                positive_indicators += 2
            elif trends['revenue']['trend'] == 'decreasing':
                negative_indicators += 2

        # Check conversion rate trend
        if 'conversion_rate' in trends:
            if trends['conversion_rate']['trend'] == 'increasing':
                positive_indicators += 1
            elif trends['conversion_rate']['trend'] == 'decreasing':
                negative_indicators += 1

        # Check cost efficiency (cost should be stable or decreasing)
        if 'cost' in trends:
            if trends['cost']['trend'] in ['stable', 'decreasing']:
                positive_indicators += 1
            else:
                negative_indicators += 1

        # Determine overall health
        if positive_indicators > negative_indicators * 2:
            return 'excellent'
        elif positive_indicators > negative_indicators:
            return 'good'
        elif positive_indicators == negative_indicators:
            return 'stable'
        else:
            return 'needs_attention'

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Example usage and testing
if __name__ == "__main__":
    calculator = KPICalculator()

    print("=" * 60)
    print("KPI CALCULATION ENGINE TEST")
    print("=" * 60)

    # Test real-time metrics
    print("\n1. Real-time Metrics:")
    realtime = calculator.calculate_realtime_metrics()
    for key, value in realtime.items():
        print(f"   {key}: {value}")

    # Test ROAS
    print("\n2. ROAS Calculation:")
    roas = calculator.calculate_roas()
    for key, value in roas.items():
        print(f"   {key}: {value}")

    # Test CLV
    print("\n3. Customer Lifetime Value:")
    clv = calculator.calculate_customer_lifetime_value()
    for key, value in clv.items():
        print(f"   {key}: {value}")

    # Test CAC
    print("\n4. Customer Acquisition Cost:")
    cac = calculator.calculate_customer_acquisition_cost()
    for key, value in cac.items():
        if key != 'health_status':
            print(f"   {key}: {value}")

    # Test Quality Score Impact
    print("\n5. Quality Score Impact:")
    qs = calculator.calculate_quality_score_impact()
    print(f"   Average QS: {qs['avg_quality_score']}")
    print(f"   Potential Savings: ${qs['potential_monthly_savings']}")

    # Test Anomaly Detection
    print("\n6. Anomaly Detection:")
    anomalies = calculator.calculate_anomaly_scores()
    print(f"   Anomalies Detected: {anomalies['anomalies_detected']}")
    if anomalies.get('current_alerts'):
        print(f"   Current Alerts: {len(anomalies['current_alerts'])}")

    # Test Trend Analysis
    print("\n7. Trend Analysis:")
    trends = calculator.calculate_trend_analysis()
    if 'trends' in trends:
        print(f"   Overall Health: {trends.get('overall_health', 'N/A')}")
        for metric, data in trends['trends'].items():
            print(f"   {metric}: {data['trend']} (R²: {data['r_squared']})")

    calculator.close()
    print("\n" + "=" * 60)