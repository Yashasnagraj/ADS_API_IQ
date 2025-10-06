"""
Performance analysis tools for Insight Agent
"""
from typing import Dict, List, Any, Optional, Tuple
from langchain.tools import Tool
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats


class PerformanceAnalyzer:
    """Tools for analyzing performance metrics and trends"""

    def __init__(self):
        """Initialize performance analyzer"""
        pass

    def analyze_campaign_performance(
        self,
        campaign_data: Dict[str, Any],
        performance_threshold: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Analyze campaign performance metrics

        Args:
            campaign_data: Campaign data from Data Agent
            performance_threshold: Performance thresholds for evaluation

        Returns:
            Dictionary with performance analysis
        """
        try:
            # Default thresholds
            if not performance_threshold:
                performance_threshold = {
                    'min_ctr': 2.0,  # 2% CTR
                    'max_cpc': 5.0,  # $5 CPC
                    'min_conversion_rate': 2.0,  # 2% conversion rate
                    'min_roas': 3.0,  # 3x ROAS
                    'max_cost_per_conversion': 50.0  # $50 CPA
                }

            # Extract campaign performance data
            campaigns = campaign_data.get('campaigns', [])
            if not campaigns:
                return {'error': 'No campaign data provided'}

            df = pd.DataFrame(campaigns)

            # Calculate performance scores
            analysis = {
                'summary': {},
                'top_performers': [],
                'underperformers': [],
                'opportunities': [],
                'metrics_breakdown': {}
            }

            # Overall metrics
            analysis['summary'] = {
                'total_campaigns': len(df),
                'total_spend': df['cost'].sum() if 'cost' in df else 0,
                'total_conversions': df['conversions'].sum() if 'conversions' in df else 0,
                'average_ctr': df['ctr'].mean() if 'ctr' in df else 0,
                'average_conversion_rate': df['conversion_rate'].mean() if 'conversion_rate' in df else 0,
                'overall_roas': (df['conversion_value'].sum() / df['cost'].sum()) if 'cost' in df and df['cost'].sum() > 0 else 0
            }

            # Identify top performers
            if 'roas' in df.columns:
                top_performers = df.nlargest(5, 'roas')[['campaign_id', 'campaign_name', 'roas', 'conversions', 'cost']]
                analysis['top_performers'] = top_performers.to_dict('records')

            # Identify underperformers
            underperformers = []

            if 'ctr' in df.columns:
                low_ctr = df[df['ctr'] < performance_threshold['min_ctr']]
                for _, row in low_ctr.iterrows():
                    underperformers.append({
                        'campaign_id': row['campaign_id'],
                        'campaign_name': row['campaign_name'],
                        'issue': 'Low CTR',
                        'current_value': row['ctr'],
                        'threshold': performance_threshold['min_ctr'],
                        'recommendation': 'Review ad copy and targeting'
                    })

            if 'conversion_rate' in df.columns:
                low_conv_rate = df[df['conversion_rate'] < performance_threshold['min_conversion_rate']]
                for _, row in low_conv_rate.iterrows():
                    underperformers.append({
                        'campaign_id': row['campaign_id'],
                        'campaign_name': row['campaign_name'],
                        'issue': 'Low Conversion Rate',
                        'current_value': row['conversion_rate'],
                        'threshold': performance_threshold['min_conversion_rate'],
                        'recommendation': 'Optimize landing pages and targeting'
                    })

            if 'roas' in df.columns:
                low_roas = df[df['roas'] < performance_threshold['min_roas']]
                for _, row in low_roas.iterrows():
                    underperformers.append({
                        'campaign_id': row['campaign_id'],
                        'campaign_name': row['campaign_name'],
                        'issue': 'Low ROAS',
                        'current_value': row['roas'],
                        'threshold': performance_threshold['min_roas'],
                        'recommendation': 'Review bidding strategy and audience targeting'
                    })

            analysis['underperformers'] = underperformers

            # Identify opportunities
            opportunities = []

            # Budget utilization opportunities
            if 'budget' in df.columns and 'cost' in df.columns:
                df['budget_utilization'] = (df['cost'] / df['budget'] * 100).fillna(0)

                # Under-utilized budget with good performance
                under_utilized = df[(df['budget_utilization'] < 80) & (df['roas'] > performance_threshold['min_roas'])]
                for _, row in under_utilized.iterrows():
                    opportunities.append({
                        'campaign_id': row['campaign_id'],
                        'campaign_name': row['campaign_name'],
                        'opportunity': 'Increase Budget',
                        'reason': f"Budget utilization at {row['budget_utilization']:.1f}% with ROAS of {row['roas']:.2f}",
                        'potential_impact': 'Increase conversions while maintaining efficiency'
                    })

            # Bid optimization opportunities
            if 'avg_cpc' in df.columns and 'conversion_rate' in df.columns:
                # High conversion rate with low CPC - opportunity to bid more aggressively
                high_performing = df[(df['conversion_rate'] > performance_threshold['min_conversion_rate'] * 1.5) &
                                   (df['avg_cpc'] < performance_threshold['max_cpc'] * 0.5)]
                for _, row in high_performing.iterrows():
                    opportunities.append({
                        'campaign_id': row['campaign_id'],
                        'campaign_name': row['campaign_name'],
                        'opportunity': 'Increase Bids',
                        'reason': f"High conversion rate ({row['conversion_rate']:.1f}%) with low CPC (${row['avg_cpc']:.2f})",
                        'potential_impact': 'Capture more high-quality traffic'
                    })

            analysis['opportunities'] = opportunities

            # Performance distribution
            if not df.empty:
                analysis['metrics_breakdown'] = {
                    'ctr_distribution': self._get_distribution_stats(df, 'ctr'),
                    'conversion_rate_distribution': self._get_distribution_stats(df, 'conversion_rate'),
                    'roas_distribution': self._get_distribution_stats(df, 'roas'),
                    'cost_distribution': self._get_distribution_stats(df, 'cost')
                }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing campaign performance: {str(e)}")
            return {'error': str(e)}

    def analyze_performance_trends(
        self,
        performance_data: List[Dict[str, Any]],
        metric: str = 'conversions'
    ) -> Dict[str, Any]:
        """
        Analyze performance trends over time

        Args:
            performance_data: Time-series performance data
            metric: Metric to analyze

        Returns:
            Dictionary with trend analysis
        """
        try:
            if not performance_data:
                return {'error': 'No performance data provided'}

            df = pd.DataFrame(performance_data)

            if 'date' not in df.columns or metric not in df.columns:
                return {'error': f'Required columns (date, {metric}) not found'}

            # Convert date to datetime
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # Calculate trend
            x = np.arange(len(df))
            y = df[metric].values

            # Linear regression for trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

            # Moving averages
            df['ma_7'] = df[metric].rolling(window=7, min_periods=1).mean()
            df['ma_30'] = df[metric].rolling(window=30, min_periods=1).mean()

            # Volatility
            df['daily_change'] = df[metric].pct_change()
            volatility = df['daily_change'].std()

            # Detect anomalies (values beyond 2 standard deviations)
            mean = df[metric].mean()
            std = df[metric].std()
            df['is_anomaly'] = (np.abs(df[metric] - mean) > 2 * std)
            anomalies = df[df['is_anomaly']][['date', metric]].to_dict('records')

            # Week-over-week and month-over-month changes
            current_week = df.tail(7)[metric].sum()
            previous_week = df.tail(14).head(7)[metric].sum()
            wow_change = ((current_week - previous_week) / previous_week * 100) if previous_week > 0 else 0

            current_month = df.tail(30)[metric].sum()
            previous_month = df.tail(60).head(30)[metric].sum()
            mom_change = ((current_month - previous_month) / previous_month * 100) if previous_month > 0 else 0

            # Forecast next 7 days (simple linear extrapolation)
            forecast_days = 7
            last_x = len(df) - 1
            forecast_x = np.arange(last_x + 1, last_x + forecast_days + 1)
            forecast_y = slope * forecast_x + intercept

            forecast = []
            last_date = df['date'].max()
            for i, value in enumerate(forecast_y):
                forecast.append({
                    'date': (last_date + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                    'predicted_value': max(0, value)  # Ensure non-negative
                })

            analysis = {
                'metric': metric,
                'trend': {
                    'direction': 'increasing' if slope > 0 else 'decreasing',
                    'slope': slope,
                    'r_squared': r_value ** 2,
                    'p_value': p_value,
                    'is_significant': p_value < 0.05
                },
                'current_performance': {
                    'latest_value': df[metric].iloc[-1],
                    'average_7_days': df.tail(7)[metric].mean(),
                    'average_30_days': df.tail(30)[metric].mean(),
                    'total_30_days': df.tail(30)[metric].sum()
                },
                'changes': {
                    'week_over_week': round(wow_change, 2),
                    'month_over_month': round(mom_change, 2)
                },
                'volatility': {
                    'std_deviation': std,
                    'coefficient_of_variation': (std / mean * 100) if mean > 0 else 0,
                    'volatility_score': volatility
                },
                'anomalies': anomalies,
                'forecast': forecast,
                'recommendation': self._get_trend_recommendation(slope, r_value, volatility)
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing performance trends: {str(e)}")
            return {'error': str(e)}

    def compare_performance(
        self,
        entity_data_1: Dict[str, Any],
        entity_data_2: Dict[str, Any],
        comparison_metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Compare performance between two entities or time periods

        Args:
            entity_data_1: First entity/period data
            entity_data_2: Second entity/period data
            comparison_metrics: Metrics to compare

        Returns:
            Dictionary with comparison analysis
        """
        try:
            if not comparison_metrics:
                comparison_metrics = ['impressions', 'clicks', 'cost', 'conversions', 'roas', 'ctr', 'conversion_rate']

            comparison = {
                'metrics': {},
                'winner': {},
                'insights': []
            }

            for metric in comparison_metrics:
                val1 = entity_data_1.get(metric, 0)
                val2 = entity_data_2.get(metric, 0)

                if val1 == 0 and val2 == 0:
                    change_pct = 0
                elif val1 == 0:
                    change_pct = 100
                else:
                    change_pct = ((val2 - val1) / val1) * 100

                comparison['metrics'][metric] = {
                    'entity_1': val1,
                    'entity_2': val2,
                    'difference': val2 - val1,
                    'change_percentage': round(change_pct, 2)
                }

                # Determine winner for each metric
                if metric in ['cost', 'avg_cpc']:  # Lower is better
                    comparison['winner'][metric] = 'entity_1' if val1 < val2 else 'entity_2'
                else:  # Higher is better
                    comparison['winner'][metric] = 'entity_1' if val1 > val2 else 'entity_2'

            # Generate insights
            if comparison['metrics'].get('roas', {}).get('change_percentage', 0) > 20:
                comparison['insights'].append('Significant ROAS improvement detected')

            if comparison['metrics'].get('cost', {}).get('change_percentage', 0) < -20:
                comparison['insights'].append('Significant cost reduction achieved')

            if comparison['metrics'].get('conversion_rate', {}).get('change_percentage', 0) > 15:
                comparison['insights'].append('Notable conversion rate improvement')

            return comparison

        except Exception as e:
            logger.error(f"Error comparing performance: {str(e)}")
            return {'error': str(e)}

    def _get_distribution_stats(self, df: pd.DataFrame, column: str) -> Dict:
        """
        Get distribution statistics for a column

        Args:
            df: DataFrame
            column: Column name

        Returns:
            Distribution statistics
        """
        if column not in df.columns:
            return {}

        return {
            'mean': df[column].mean(),
            'median': df[column].median(),
            'std': df[column].std(),
            'min': df[column].min(),
            'max': df[column].max(),
            'q25': df[column].quantile(0.25),
            'q75': df[column].quantile(0.75)
        }

    def _get_trend_recommendation(self, slope: float, r_value: float, volatility: float) -> str:
        """
        Generate recommendation based on trend analysis

        Args:
            slope: Trend slope
            r_value: Correlation coefficient
            volatility: Volatility score

        Returns:
            Recommendation string
        """
        if abs(r_value) < 0.3:
            return "No clear trend detected. Monitor closely for pattern emergence."
        elif slope > 0 and r_value > 0.7:
            return "Strong positive trend. Consider increasing investment to capitalize on momentum."
        elif slope < 0 and r_value < -0.7:
            return "Strong negative trend. Immediate optimization required to reverse decline."
        elif volatility > 0.5:
            return "High volatility detected. Stabilize performance before scaling."
        else:
            return "Stable performance. Focus on incremental optimizations."

    def get_tools(self) -> List[Tool]:
        """
        Get LangChain tools for performance analysis

        Returns:
            List of Tool objects
        """
        return [
            Tool(
                name="analyze_campaign_performance",
                func=self.analyze_campaign_performance,
                description="""Analyze campaign performance metrics and identify opportunities.
                Args: campaign_data (dict), performance_threshold (dict)
                Returns: Dictionary with performance analysis, top/under performers, and opportunities"""
            ),
            Tool(
                name="analyze_performance_trends",
                func=self.analyze_performance_trends,
                description="""Analyze performance trends over time with forecasting.
                Args: performance_data (list), metric (str)
                Returns: Dictionary with trend analysis, anomalies, and forecast"""
            ),
            Tool(
                name="compare_performance",
                func=self.compare_performance,
                description="""Compare performance between entities or time periods.
                Args: entity_data_1 (dict), entity_data_2 (dict), comparison_metrics (list)
                Returns: Dictionary with comparison analysis and insights"""
            )
        ]