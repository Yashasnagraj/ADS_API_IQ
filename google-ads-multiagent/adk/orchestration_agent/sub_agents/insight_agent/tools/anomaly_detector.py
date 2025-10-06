"""
Anomaly detection tools for Insight Agent
"""
from typing import Dict, List, Any, Optional, Tuple
from langchain.tools import Tool
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AnomalyDetector:
    """Detects anomalies in Google Ads performance data"""

    def __init__(self):
        logger.info("Anomaly Detector initialized")
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)

    def detect_metric_anomalies(
        self,
        time_series_data: List[Dict[str, Any]],
        metrics: List[str] = None,
        sensitivity: float = 2.0
    ) -> Dict[str, Any]:
        """
        Detect anomalies in time series metrics

        Args:
            time_series_data: Time series performance data
            metrics: List of metrics to analyze
            sensitivity: Standard deviations for anomaly detection (lower = more sensitive)

        Returns:
            Anomalies with severity and recommendations
        """
        try:
            if not time_series_data:
                return {"error": "No time series data provided"}

            df = pd.DataFrame(time_series_data)

            if 'date' not in df.columns:
                return {"error": "Date column required for time series analysis"}

            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # Default metrics if not specified
            if not metrics:
                metrics = ['impressions', 'clicks', 'cost', 'conversions', 'ctr', 'conversion_rate']
                metrics = [m for m in metrics if m in df.columns]

            anomalies = {
                'summary': {
                    'total_anomalies': 0,
                    'critical_anomalies': 0,
                    'warning_anomalies': 0
                },
                'by_metric': {},
                'by_date': {},
                'recommendations': []
            }

            for metric in metrics:
                if metric not in df.columns:
                    continue

                # Statistical anomaly detection
                metric_anomalies = self._detect_statistical_anomalies(
                    df, metric, sensitivity
                )

                # Isolation Forest for multivariate anomalies
                if len(df) > 10:  # Need sufficient data
                    isolation_anomalies = self._detect_isolation_anomalies(
                        df, metric
                    )
                    metric_anomalies['isolation_forest'] = isolation_anomalies

                # Classify anomaly severity
                for anomaly in metric_anomalies.get('anomalies', []):
                    severity = self._classify_anomaly_severity(
                        anomaly['deviation'], metric
                    )
                    anomaly['severity'] = severity

                    # Group by date
                    date_str = anomaly['date']
                    if date_str not in anomalies['by_date']:
                        anomalies['by_date'][date_str] = []
                    anomalies['by_date'][date_str].append({
                        'metric': metric,
                        'value': anomaly['value'],
                        'expected': anomaly['expected'],
                        'severity': severity
                    })

                    # Update counters
                    anomalies['summary']['total_anomalies'] += 1
                    if severity == 'critical':
                        anomalies['summary']['critical_anomalies'] += 1
                    elif severity == 'warning':
                        anomalies['summary']['warning_anomalies'] += 1

                anomalies['by_metric'][metric] = metric_anomalies

            # Generate recommendations
            anomalies['recommendations'] = self._generate_anomaly_recommendations(
                anomalies
            )

            # Detect patterns
            anomalies['patterns'] = self._detect_anomaly_patterns(df, anomalies)

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting metric anomalies: {e}")
            return {"error": str(e)}

    def detect_campaign_anomalies(
        self,
        campaign_data: List[Dict[str, Any]],
        baseline_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect anomalies at campaign level

        Args:
            campaign_data: Campaign performance data
            baseline_period_days: Days to use for baseline calculation

        Returns:
            Campaign-level anomalies
        """
        try:
            if not campaign_data:
                return {"error": "No campaign data provided"}

            df = pd.DataFrame(campaign_data)

            # Group by campaign and date
            if 'campaign_id' not in df.columns or 'date' not in df.columns:
                return {"error": "campaign_id and date columns required"}

            df['date'] = pd.to_datetime(df['date'])

            anomalies = {
                'campaigns': {},
                'cross_campaign_anomalies': [],
                'sudden_changes': [],
                'recommendations': []
            }

            # Analyze each campaign
            for campaign_id in df['campaign_id'].unique():
                campaign_df = df[df['campaign_id'] == campaign_id].sort_values('date')

                if len(campaign_df) < 7:  # Need minimum data
                    continue

                campaign_name = campaign_df['campaign_name'].iloc[0] if 'campaign_name' in campaign_df else str(campaign_id)

                # Detect sudden changes
                sudden_changes = self._detect_sudden_changes(campaign_df)

                # Detect spending anomalies
                spending_anomalies = self._detect_spending_anomalies(campaign_df)

                # Detect performance drops
                performance_drops = self._detect_performance_drops(campaign_df)

                anomalies['campaigns'][campaign_id] = {
                    'campaign_name': campaign_name,
                    'sudden_changes': sudden_changes,
                    'spending_anomalies': spending_anomalies,
                    'performance_drops': performance_drops
                }

                # Add to sudden changes list
                for change in sudden_changes:
                    anomalies['sudden_changes'].append({
                        'campaign_id': campaign_id,
                        'campaign_name': campaign_name,
                        **change
                    })

            # Detect cross-campaign anomalies
            anomalies['cross_campaign_anomalies'] = self._detect_cross_campaign_anomalies(df)

            # Generate recommendations
            anomalies['recommendations'] = self._generate_campaign_recommendations(anomalies)

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting campaign anomalies: {e}")
            return {"error": str(e)}

    def detect_budget_anomalies(
        self,
        budget_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect budget-related anomalies

        Args:
            budget_data: Budget and spending data

        Returns:
            Budget anomalies and alerts
        """
        try:
            if not budget_data:
                return {"error": "No budget data provided"}

            df = pd.DataFrame(budget_data)

            anomalies = {
                'overspending': [],
                'underspending': [],
                'pace_issues': [],
                'budget_efficiency': [],
                'alerts': []
            }

            # Check each campaign's budget utilization
            for _, row in df.iterrows():
                campaign_id = row.get('campaign_id')
                campaign_name = row.get('campaign_name', 'Unknown')
                budget = row.get('budget', 0)
                spent = row.get('cost', 0)

                if budget <= 0:
                    continue

                utilization = (spent / budget) * 100
                days_in_month = 30
                current_day = row.get('day_of_month', 15)
                expected_utilization = (current_day / days_in_month) * 100

                # Overspending detection
                if utilization > expected_utilization + 20:
                    anomalies['overspending'].append({
                        'campaign_id': campaign_id,
                        'campaign_name': campaign_name,
                        'utilization': round(utilization, 2),
                        'expected': round(expected_utilization, 2),
                        'severity': 'high' if utilization > 90 else 'medium',
                        'recommendation': 'Consider reducing bids or daily budget'
                    })

                # Underspending detection
                elif utilization < expected_utilization - 30:
                    anomalies['underspending'].append({
                        'campaign_id': campaign_id,
                        'campaign_name': campaign_name,
                        'utilization': round(utilization, 2),
                        'expected': round(expected_utilization, 2),
                        'severity': 'medium',
                        'recommendation': 'Increase bids or expand targeting'
                    })

                # Pace issues
                if abs(utilization - expected_utilization) > 15:
                    anomalies['pace_issues'].append({
                        'campaign_id': campaign_id,
                        'campaign_name': campaign_name,
                        'current_pace': round(utilization / current_day, 2),
                        'required_pace': round(100 / days_in_month, 2),
                        'adjustment_needed': 'decrease' if utilization > expected_utilization else 'increase'
                    })

                # Budget efficiency
                if 'conversions' in row and row['conversions'] > 0:
                    cpa = spent / row['conversions']
                    if 'target_cpa' in row and row['target_cpa'] > 0:
                        cpa_variance = ((cpa - row['target_cpa']) / row['target_cpa']) * 100

                        if abs(cpa_variance) > 20:
                            anomalies['budget_efficiency'].append({
                                'campaign_id': campaign_id,
                                'campaign_name': campaign_name,
                                'actual_cpa': round(cpa, 2),
                                'target_cpa': round(row['target_cpa'], 2),
                                'variance': round(cpa_variance, 2),
                                'status': 'over_target' if cpa_variance > 0 else 'under_target'
                            })

            # Generate alerts
            if anomalies['overspending']:
                critical_overspend = [c for c in anomalies['overspending'] if c['severity'] == 'high']
                if critical_overspend:
                    anomalies['alerts'].append({
                        'type': 'critical',
                        'message': f"{len(critical_overspend)} campaigns at risk of exhausting budget",
                        'affected_campaigns': [c['campaign_name'] for c in critical_overspend]
                    })

            if len(anomalies['pace_issues']) > 5:
                anomalies['alerts'].append({
                    'type': 'warning',
                    'message': f"{len(anomalies['pace_issues'])} campaigns have pacing issues",
                    'recommendation': 'Review budget allocation across campaigns'
                })

            return anomalies

        except Exception as e:
            logger.error(f"Error detecting budget anomalies: {e}")
            return {"error": str(e)}

    def _detect_statistical_anomalies(
        self,
        df: pd.DataFrame,
        metric: str,
        sensitivity: float
    ) -> Dict[str, Any]:
        """Detect statistical anomalies using z-score"""
        values = df[metric].values

        # Calculate rolling statistics for dynamic baseline
        window = min(7, len(df) // 4)
        df[f'{metric}_rolling_mean'] = df[metric].rolling(window=window, min_periods=1).mean()
        df[f'{metric}_rolling_std'] = df[metric].rolling(window=window, min_periods=1).std()

        anomalies = []

        for idx, row in df.iterrows():
            value = row[metric]
            mean = row[f'{metric}_rolling_mean']
            std = row[f'{metric}_rolling_std']

            if std > 0:
                z_score = (value - mean) / std

                if abs(z_score) > sensitivity:
                    anomalies.append({
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'value': round(value, 2),
                        'expected': round(mean, 2),
                        'z_score': round(z_score, 2),
                        'deviation': round(abs(z_score), 2),
                        'direction': 'above' if z_score > 0 else 'below'
                    })

        return {
            'metric': metric,
            'anomalies': anomalies,
            'total_anomalies': len(anomalies),
            'detection_method': 'statistical_zscore'
        }

    def _detect_isolation_anomalies(
        self,
        df: pd.DataFrame,
        metric: str
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using Isolation Forest"""
        try:
            # Prepare features
            features = [metric]

            # Add lag features if enough data
            if len(df) > 7:
                df[f'{metric}_lag1'] = df[metric].shift(1)
                df[f'{metric}_lag7'] = df[metric].shift(7)
                features.extend([f'{metric}_lag1', f'{metric}_lag7'])

            # Remove rows with NaN
            df_clean = df[features].dropna()

            if len(df_clean) < 10:
                return []

            # Scale features
            X = self.scaler.fit_transform(df_clean[features])

            # Detect anomalies
            predictions = self.isolation_forest.fit_predict(X)

            # Get anomaly scores
            scores = self.isolation_forest.score_samples(X)

            anomalies = []
            for idx, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:  # Anomaly
                    row_idx = df_clean.index[idx]
                    anomalies.append({
                        'date': df.loc[row_idx, 'date'].strftime('%Y-%m-%d'),
                        'anomaly_score': round(score, 3),
                        'is_anomaly': True
                    })

            return anomalies

        except Exception as e:
            logger.error(f"Error in isolation forest detection: {e}")
            return []

    def _detect_sudden_changes(
        self,
        df: pd.DataFrame,
        threshold_pct: float = 30
    ) -> List[Dict[str, Any]]:
        """Detect sudden changes in metrics"""
        changes = []

        metrics = ['cost', 'clicks', 'conversions', 'ctr', 'conversion_rate']
        metrics = [m for m in metrics if m in df.columns]

        for metric in metrics:
            df[f'{metric}_pct_change'] = df[metric].pct_change() * 100

            sudden = df[abs(df[f'{metric}_pct_change']) > threshold_pct]

            for _, row in sudden.iterrows():
                changes.append({
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'metric': metric,
                    'change_pct': round(row[f'{metric}_pct_change'], 2),
                    'value': round(row[metric], 2)
                })

        return changes

    def _detect_spending_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in spending patterns"""
        anomalies = []

        if 'cost' not in df.columns:
            return anomalies

        # Daily spending variance
        daily_avg = df['cost'].mean()
        daily_std = df['cost'].std()

        for _, row in df.iterrows():
            if row['cost'] > daily_avg + 2 * daily_std:
                anomalies.append({
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'type': 'high_spending',
                    'amount': round(row['cost'], 2),
                    'expected': round(daily_avg, 2),
                    'variance': round((row['cost'] - daily_avg) / daily_avg * 100, 2)
                })
            elif row['cost'] < daily_avg - 2 * daily_std:
                anomalies.append({
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'type': 'low_spending',
                    'amount': round(row['cost'], 2),
                    'expected': round(daily_avg, 2),
                    'variance': round((row['cost'] - daily_avg) / daily_avg * 100, 2)
                })

        return anomalies

    def _detect_performance_drops(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect significant performance drops"""
        drops = []

        metrics = ['conversions', 'clicks', 'ctr', 'conversion_rate']
        metrics = [m for m in metrics if m in df.columns]

        for metric in metrics:
            # Calculate 7-day moving average
            df[f'{metric}_ma7'] = df[metric].rolling(window=7, min_periods=1).mean()

            # Detect drops below 70% of moving average
            for idx, row in df.iterrows():
                if row[metric] < 0.7 * row[f'{metric}_ma7']:
                    drops.append({
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'metric': metric,
                        'value': round(row[metric], 2),
                        'expected': round(row[f'{metric}_ma7'], 2),
                        'drop_pct': round((1 - row[metric] / row[f'{metric}_ma7']) * 100, 2)
                    })

        return drops

    def _detect_cross_campaign_anomalies(
        self,
        df: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Detect anomalies across multiple campaigns"""
        anomalies = []

        # Group by date to find system-wide anomalies
        daily = df.groupby('date').agg({
            'cost': 'sum',
            'clicks': 'sum',
            'conversions': 'sum',
            'impressions': 'sum'
        }).reset_index()

        # Detect days with unusual total metrics
        for metric in ['cost', 'clicks', 'conversions']:
            if metric not in daily.columns:
                continue

            mean = daily[metric].mean()
            std = daily[metric].std()

            for _, row in daily.iterrows():
                z_score = (row[metric] - mean) / std if std > 0 else 0

                if abs(z_score) > 2.5:
                    # Find affected campaigns
                    date_data = df[df['date'] == row['date']]
                    affected = date_data.nlargest(3, metric)['campaign_id'].tolist()

                    anomalies.append({
                        'date': row['date'].strftime('%Y-%m-%d'),
                        'type': 'system_wide',
                        'metric': metric,
                        'total_value': round(row[metric], 2),
                        'z_score': round(z_score, 2),
                        'affected_campaigns': affected
                    })

        return anomalies

    def _classify_anomaly_severity(
        self,
        deviation: float,
        metric: str
    ) -> str:
        """Classify anomaly severity"""
        # Critical metrics
        critical_metrics = ['conversions', 'roas', 'conversion_rate']

        if metric in critical_metrics:
            if deviation > 3:
                return 'critical'
            elif deviation > 2:
                return 'warning'
            else:
                return 'info'
        else:
            if deviation > 4:
                return 'critical'
            elif deviation > 2.5:
                return 'warning'
            else:
                return 'info'

    def _generate_anomaly_recommendations(
        self,
        anomalies: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on anomalies"""
        recommendations = []

        if anomalies['summary']['critical_anomalies'] > 0:
            recommendations.append(
                "Critical anomalies detected. Immediate investigation required."
            )

        # Check for specific patterns
        for metric, data in anomalies['by_metric'].items():
            if not data.get('anomalies'):
                continue

            if metric == 'cost' and len(data['anomalies']) > 0:
                recommendations.append(
                    "Cost anomalies detected. Review bidding strategies and budget settings."
                )

            elif metric == 'conversions' and len(data['anomalies']) > 0:
                recommendations.append(
                    "Conversion anomalies found. Check tracking implementation and landing pages."
                )

            elif metric == 'ctr' and len(data['anomalies']) > 0:
                recommendations.append(
                    "CTR anomalies identified. Review ad copy and keyword relevance."
                )

        return recommendations[:5]

    def _generate_campaign_recommendations(
        self,
        anomalies: Dict[str, Any]
    ) -> List[str]:
        """Generate campaign-specific recommendations"""
        recommendations = []

        if anomalies['sudden_changes']:
            recommendations.append(
                f"Found {len(anomalies['sudden_changes'])} sudden changes. Review recent optimizations."
            )

        overspending = sum(
            1 for c_data in anomalies['campaigns'].values()
            if c_data.get('spending_anomalies')
        )

        if overspending > 0:
            recommendations.append(
                f"{overspending} campaigns show spending anomalies. Adjust budget pacing."
            )

        return recommendations

    def _detect_anomaly_patterns(
        self,
        df: pd.DataFrame,
        anomalies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect patterns in anomalies"""
        patterns = {
            'recurring': [],
            'seasonal': [],
            'trending': []
        }

        # Check for recurring anomalies (same day of week)
        anomaly_dates = []
        for date_str in anomalies['by_date'].keys():
            anomaly_dates.append(pd.to_datetime(date_str))

        if anomaly_dates:
            df_anomalies = pd.DataFrame({'date': anomaly_dates})
            df_anomalies['day_of_week'] = df_anomalies['date'].dt.dayofweek

            # Count anomalies by day of week
            dow_counts = df_anomalies['day_of_week'].value_counts()

            for dow, count in dow_counts.items():
                if count >= 3:
                    day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][dow]
                    patterns['recurring'].append({
                        'pattern': 'day_of_week',
                        'day': day_name,
                        'frequency': count
                    })

        return patterns

    def get_tools(self) -> List[Tool]:
        """Get LangChain tools for anomaly detection"""
        return [
            Tool(
                name="detect_metric_anomalies",
                func=self.detect_metric_anomalies,
                description="Detect anomalies in time series metrics using statistical methods"
            ),
            Tool(
                name="detect_campaign_anomalies",
                func=self.detect_campaign_anomalies,
                description="Detect anomalies at campaign level including sudden changes"
            ),
            Tool(
                name="detect_budget_anomalies",
                func=self.detect_budget_anomalies,
                description="Detect budget-related anomalies and pacing issues"
            )
        ]