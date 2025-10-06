"""
Trend analysis tools for Insight Agent
"""
from typing import Dict, List, Any, Optional, Tuple
from langchain.tools import Tool
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller


class TrendAnalyzer:
    """Analyzes trends and patterns in Google Ads data"""

    def __init__(self):
        logger.info("Trend Analyzer initialized")

    def analyze_performance_trends(
        self,
        performance_data: List[Dict[str, Any]],
        metrics: List[str] = None,
        period: str = 'daily'
    ) -> Dict[str, Any]:
        """
        Analyze performance trends over time

        Args:
            performance_data: Historical performance data
            metrics: Metrics to analyze
            period: Analysis period (daily, weekly, monthly)

        Returns:
            Trend analysis with predictions
        """
        try:
            if not performance_data:
                return {"error": "No performance data provided"}

            df = pd.DataFrame(performance_data)

            if 'date' not in df.columns:
                return {"error": "Date column required for trend analysis"}

            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # Default metrics
            if not metrics:
                metrics = ['impressions', 'clicks', 'conversions', 'cost', 'ctr', 'conversion_rate']
                metrics = [m for m in metrics if m in df.columns]

            analysis = {
                'period': period,
                'date_range': {
                    'start': df['date'].min().strftime('%Y-%m-%d'),
                    'end': df['date'].max().strftime('%Y-%m-%d'),
                    'days': (df['date'].max() - df['date'].min()).days
                },
                'metrics': {}
            }

            # Aggregate by period
            df_period = self._aggregate_by_period(df, period)

            for metric in metrics:
                if metric not in df_period.columns:
                    continue

                metric_analysis = {
                    'current_value': round(df_period[metric].iloc[-1], 2),
                    'trend': self._calculate_trend(df_period, metric),
                    'momentum': self._calculate_momentum(df_period, metric),
                    'volatility': self._calculate_volatility(df_period, metric),
                    'seasonality': self._detect_seasonality(df_period, metric),
                    'forecast': self._forecast_trend(df_period, metric),
                    'growth_rate': self._calculate_growth_rate(df_period, metric),
                    'turning_points': self._detect_turning_points(df_period, metric)
                }

                analysis['metrics'][metric] = metric_analysis

            # Overall trend summary
            analysis['summary'] = self._generate_trend_summary(analysis['metrics'])

            # Key insights
            analysis['insights'] = self._generate_trend_insights(analysis['metrics'])

            # Recommendations
            analysis['recommendations'] = self._generate_trend_recommendations(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")
            return {"error": str(e)}

    def analyze_keyword_trends(
        self,
        keyword_data: List[Dict[str, Any]],
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Analyze keyword performance trends

        Args:
            keyword_data: Keyword performance data
            top_n: Number of top keywords to analyze

        Returns:
            Keyword trend analysis
        """
        try:
            if not keyword_data:
                return {"error": "No keyword data provided"}

            df = pd.DataFrame(keyword_data)

            analysis = {
                'rising_keywords': [],
                'declining_keywords': [],
                'stable_keywords': [],
                'volatile_keywords': [],
                'opportunity_keywords': []
            }

            # Group by keyword
            keyword_groups = df.groupby('keyword_text')

            for keyword, group in keyword_groups:
                if len(group) < 7:  # Need minimum data points
                    continue

                group = group.sort_values('date')

                # Calculate trend
                trend = self._calculate_keyword_trend(group)

                keyword_info = {
                    'keyword': keyword,
                    'current_performance': {
                        'impressions': group['impressions'].iloc[-1] if 'impressions' in group else 0,
                        'clicks': group['clicks'].iloc[-1] if 'clicks' in group else 0,
                        'conversions': group['conversions'].iloc[-1] if 'conversions' in group else 0,
                        'ctr': group['ctr'].iloc[-1] if 'ctr' in group else 0,
                        'conversion_rate': group['conversion_rate'].iloc[-1] if 'conversion_rate' in group else 0,
                        'avg_position': group['avg_position'].iloc[-1] if 'avg_position' in group else 0
                    },
                    'trend_score': trend['score'],
                    'trend_direction': trend['direction'],
                    'volatility': trend['volatility']
                }

                # Categorize keywords
                if trend['score'] > 0.3:
                    analysis['rising_keywords'].append(keyword_info)
                elif trend['score'] < -0.3:
                    analysis['declining_keywords'].append(keyword_info)
                elif trend['volatility'] > 0.5:
                    analysis['volatile_keywords'].append(keyword_info)
                else:
                    analysis['stable_keywords'].append(keyword_info)

                # Identify opportunities
                if self._is_opportunity_keyword(group):
                    analysis['opportunity_keywords'].append({
                        **keyword_info,
                        'opportunity_reason': self._get_opportunity_reason(group)
                    })

            # Sort and limit results
            for category in ['rising_keywords', 'declining_keywords', 'opportunity_keywords']:
                analysis[category] = sorted(
                    analysis[category],
                    key=lambda x: abs(x['trend_score']),
                    reverse=True
                )[:top_n]

            # Add summary statistics
            analysis['summary'] = {
                'total_keywords_analyzed': len(keyword_groups),
                'rising_count': len(analysis['rising_keywords']),
                'declining_count': len(analysis['declining_keywords']),
                'opportunities_found': len(analysis['opportunity_keywords'])
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing keyword trends: {e}")
            return {"error": str(e)}

    def analyze_competitive_trends(
        self,
        market_data: Dict[str, Any],
        competitor_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze competitive and market trends

        Args:
            market_data: Market-level data
            competitor_data: Competitor performance data (if available)

        Returns:
            Competitive trend analysis
        """
        try:
            analysis = {
                'market_trends': {},
                'competitive_position': {},
                'share_of_voice_trend': {},
                'opportunities': [],
                'threats': []
            }

            # Analyze market trends
            if 'search_volume_trends' in market_data:
                analysis['market_trends'] = self._analyze_market_trends(
                    market_data['search_volume_trends']
                )

            # Analyze impression share trends
            if 'impression_share_data' in market_data:
                share_analysis = self._analyze_impression_share_trends(
                    market_data['impression_share_data']
                )
                analysis['share_of_voice_trend'] = share_analysis

                # Identify opportunities and threats
                if share_analysis.get('lost_share_budget', 0) > 10:
                    analysis['opportunities'].append({
                        'type': 'budget_increase',
                        'impact': f"Could gain {share_analysis['lost_share_budget']:.1f}% more impressions",
                        'recommendation': 'Consider increasing campaign budgets'
                    })

                if share_analysis.get('lost_share_rank', 0) > 15:
                    analysis['threats'].append({
                        'type': 'ranking_loss',
                        'impact': f"Losing {share_analysis['lost_share_rank']:.1f}% impressions to competitors",
                        'recommendation': 'Improve ad rank through bid and quality optimizations'
                    })

            # Analyze competitor trends if data available
            if competitor_data:
                analysis['competitive_position'] = self._analyze_competitor_trends(
                    competitor_data
                )

            # Generate competitive insights
            analysis['insights'] = self._generate_competitive_insights(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing competitive trends: {e}")
            return {"error": str(e)}

    def _aggregate_by_period(
        self,
        df: pd.DataFrame,
        period: str
    ) -> pd.DataFrame:
        """Aggregate data by specified period"""
        if period == 'daily':
            return df

        elif period == 'weekly':
            df['week'] = df['date'].dt.to_period('W')
            return df.groupby('week').agg({
                col: 'sum' if col in ['impressions', 'clicks', 'conversions', 'cost'] else 'mean'
                for col in df.columns if col not in ['date', 'week']
            }).reset_index()

        elif period == 'monthly':
            df['month'] = df['date'].dt.to_period('M')
            return df.groupby('month').agg({
                col: 'sum' if col in ['impressions', 'clicks', 'conversions', 'cost'] else 'mean'
                for col in df.columns if col not in ['date', 'month']
            }).reset_index()

        return df

    def _calculate_trend(
        self,
        df: pd.DataFrame,
        metric: str
    ) -> Dict[str, Any]:
        """Calculate trend statistics for a metric"""
        if metric not in df.columns or len(df) < 2:
            return {}

        values = df[metric].values
        x = np.arange(len(values)).reshape(-1, 1)
        y = values.reshape(-1, 1)

        # Linear regression
        model = LinearRegression()
        model.fit(x, y)

        slope = model.coef_[0][0]
        r_squared = model.score(x, y)

        # Mann-Kendall trend test
        mk_result = self._mann_kendall_test(values)

        return {
            'direction': 'increasing' if slope > 0 else 'decreasing',
            'slope': round(slope, 4),
            'r_squared': round(r_squared, 4),
            'strength': self._classify_trend_strength(r_squared, slope),
            'mann_kendall': mk_result,
            'is_significant': mk_result['p_value'] < 0.05 if mk_result else False
        }

    def _calculate_momentum(
        self,
        df: pd.DataFrame,
        metric: str,
        period: int = 7
    ) -> Dict[str, Any]:
        """Calculate momentum indicators"""
        if metric not in df.columns or len(df) < period:
            return {}

        values = df[metric].values

        # Rate of change
        roc = ((values[-1] - values[-period]) / values[-period] * 100) if values[-period] != 0 else 0

        # Moving average convergence
        ma_short = np.mean(values[-period:])
        ma_long = np.mean(values) if len(values) > period * 2 else ma_short

        macd = ma_short - ma_long

        return {
            'rate_of_change': round(roc, 2),
            'macd': round(macd, 2),
            'signal': 'bullish' if macd > 0 and roc > 0 else 'bearish' if macd < 0 and roc < 0 else 'neutral'
        }

    def _calculate_volatility(
        self,
        df: pd.DataFrame,
        metric: str
    ) -> Dict[str, Any]:
        """Calculate volatility metrics"""
        if metric not in df.columns or len(df) < 2:
            return {}

        values = df[metric].values

        # Standard deviation
        std_dev = np.std(values)

        # Coefficient of variation
        cv = (std_dev / np.mean(values) * 100) if np.mean(values) != 0 else 0

        # Daily changes
        pct_changes = pd.Series(values).pct_change().dropna()
        volatility = pct_changes.std() * 100

        return {
            'standard_deviation': round(std_dev, 2),
            'coefficient_variation': round(cv, 2),
            'volatility_pct': round(volatility, 2),
            'stability': 'stable' if cv < 20 else 'moderate' if cv < 50 else 'volatile'
        }

    def _detect_seasonality(
        self,
        df: pd.DataFrame,
        metric: str
    ) -> Dict[str, Any]:
        """Detect seasonality in the data"""
        if metric not in df.columns or len(df) < 14:
            return {'detected': False}

        try:
            values = df[metric].values

            # Need at least 2 complete cycles for seasonal decomposition
            if len(values) < 14:
                return {'detected': False}

            # Perform seasonal decomposition
            decomposition = seasonal_decompose(
                values,
                model='additive',
                period=min(7, len(values) // 2)
            )

            seasonal_strength = np.std(decomposition.seasonal) / np.std(values)

            return {
                'detected': seasonal_strength > 0.1,
                'strength': round(seasonal_strength, 3),
                'pattern': 'weekly' if len(values) >= 14 else 'short-term',
                'seasonal_factor': round(np.max(np.abs(decomposition.seasonal)), 2)
            }

        except Exception:
            return {'detected': False}

    def _forecast_trend(
        self,
        df: pd.DataFrame,
        metric: str,
        periods: int = 7
    ) -> List[Dict[str, Any]]:
        """Forecast future values"""
        if metric not in df.columns or len(df) < 3:
            return []

        values = df[metric].values
        x = np.arange(len(values)).reshape(-1, 1)
        y = values.reshape(-1, 1)

        # Fit model
        model = LinearRegression()
        model.fit(x, y)

        # Generate forecast
        forecast = []
        last_date = df.index[-1] if isinstance(df.index, pd.DatetimeIndex) else len(df)

        for i in range(1, periods + 1):
            future_x = len(values) + i - 1
            predicted_value = model.predict([[future_x]])[0][0]

            forecast.append({
                'period': i,
                'predicted_value': round(max(0, predicted_value), 2),
                'confidence_interval': {
                    'lower': round(max(0, predicted_value * 0.8), 2),
                    'upper': round(predicted_value * 1.2, 2)
                }
            })

        return forecast

    def _calculate_growth_rate(
        self,
        df: pd.DataFrame,
        metric: str
    ) -> Dict[str, Any]:
        """Calculate growth rates"""
        if metric not in df.columns or len(df) < 2:
            return {}

        values = df[metric].values

        # Period-over-period growth
        if len(values) >= 2:
            pop_growth = ((values[-1] - values[-2]) / values[-2] * 100) if values[-2] != 0 else 0
        else:
            pop_growth = 0

        # Compound growth rate
        if len(values) >= 7 and values[0] > 0:
            periods = len(values) - 1
            cagr = ((values[-1] / values[0]) ** (1 / periods) - 1) * 100
        else:
            cagr = 0

        # Average growth rate
        growth_rates = []
        for i in range(1, len(values)):
            if values[i-1] != 0:
                growth = ((values[i] - values[i-1]) / values[i-1] * 100)
                growth_rates.append(growth)

        avg_growth = np.mean(growth_rates) if growth_rates else 0

        return {
            'period_over_period': round(pop_growth, 2),
            'compound_annual': round(cagr, 2),
            'average_growth': round(avg_growth, 2)
        }

    def _detect_turning_points(
        self,
        df: pd.DataFrame,
        metric: str
    ) -> List[Dict[str, Any]]:
        """Detect turning points in the trend"""
        if metric not in df.columns or len(df) < 5:
            return []

        values = df[metric].values
        turning_points = []

        # Find local maxima and minima
        for i in range(1, len(values) - 1):
            if values[i] > values[i-1] and values[i] > values[i+1]:
                turning_points.append({
                    'index': i,
                    'type': 'peak',
                    'value': round(values[i], 2)
                })
            elif values[i] < values[i-1] and values[i] < values[i+1]:
                turning_points.append({
                    'index': i,
                    'type': 'trough',
                    'value': round(values[i], 2)
                })

        return turning_points

    def _mann_kendall_test(self, values: np.ndarray) -> Dict[str, Any]:
        """Perform Mann-Kendall trend test"""
        n = len(values)
        s = 0

        for i in range(n):
            for j in range(i + 1, n):
                s += np.sign(values[j] - values[i])

        # Calculate variance
        var_s = n * (n - 1) * (2 * n + 5) / 18

        # Calculate z-score
        if var_s > 0:
            if s > 0:
                z = (s - 1) / np.sqrt(var_s)
            elif s < 0:
                z = (s + 1) / np.sqrt(var_s)
            else:
                z = 0
        else:
            z = 0

        # Calculate p-value
        p_value = 2 * (1 - stats.norm.cdf(abs(z)))

        return {
            'statistic': s,
            'z_score': round(z, 3),
            'p_value': round(p_value, 4),
            'trend': 'increasing' if s > 0 else 'decreasing' if s < 0 else 'no trend'
        }

    def _classify_trend_strength(self, r_squared: float, slope: float) -> str:
        """Classify trend strength"""
        if r_squared > 0.8:
            return 'strong'
        elif r_squared > 0.5:
            return 'moderate'
        elif r_squared > 0.3:
            return 'weak'
        else:
            return 'no_trend'

    def _calculate_keyword_trend(self, group: pd.DataFrame) -> Dict[str, Any]:
        """Calculate trend for a specific keyword"""
        metrics = ['clicks', 'conversions', 'ctr']
        scores = []

        for metric in metrics:
            if metric in group.columns:
                values = group[metric].values
                if len(values) >= 2 and np.std(values) > 0:
                    # Normalize and calculate slope
                    x = np.arange(len(values))
                    slope, _, r_value, _, _ = stats.linregress(x, values)

                    # Weight by r-squared
                    score = slope * (r_value ** 2)
                    scores.append(score)

        overall_score = np.mean(scores) if scores else 0
        volatility = np.std(scores) if len(scores) > 1 else 0

        return {
            'score': round(overall_score, 3),
            'direction': 'rising' if overall_score > 0 else 'declining',
            'volatility': round(volatility, 3)
        }

    def _is_opportunity_keyword(self, group: pd.DataFrame) -> bool:
        """Check if keyword represents an opportunity"""
        if len(group) < 7:
            return False

        # High CTR but low volume
        if 'ctr' in group.columns and 'impressions' in group.columns:
            avg_ctr = group['ctr'].mean()
            avg_impressions = group['impressions'].mean()

            if avg_ctr > 5 and avg_impressions < 1000:
                return True

        # Improving performance
        if 'conversions' in group.columns:
            recent = group.tail(3)['conversions'].mean()
            historical = group.head(len(group) - 3)['conversions'].mean()

            if historical > 0 and recent / historical > 1.5:
                return True

        return False

    def _get_opportunity_reason(self, group: pd.DataFrame) -> str:
        """Get reason why keyword is an opportunity"""
        reasons = []

        if 'ctr' in group.columns:
            avg_ctr = group['ctr'].mean()
            if avg_ctr > 5:
                reasons.append(f"High CTR ({avg_ctr:.1f}%)")

        if 'conversions' in group.columns:
            recent = group.tail(3)['conversions'].mean()
            historical = group.head(len(group) - 3)['conversions'].mean()

            if historical > 0:
                improvement = (recent / historical - 1) * 100
                if improvement > 50:
                    reasons.append(f"Conversions up {improvement:.0f}%")

        if 'quality_score' in group.columns:
            qs = group['quality_score'].iloc[-1]
            if qs >= 8:
                reasons.append(f"High quality score ({qs}/10)")

        return ', '.join(reasons) if reasons else 'Positive trend detected'

    def _analyze_market_trends(self, search_volume_data: List[Dict]) -> Dict[str, Any]:
        """Analyze market-level trends"""
        df = pd.DataFrame(search_volume_data)

        return {
            'search_volume_trend': self._calculate_trend(df, 'search_volume'),
            'seasonality': self._detect_seasonality(df, 'search_volume'),
            'growth_rate': self._calculate_growth_rate(df, 'search_volume')
        }

    def _analyze_impression_share_trends(self, share_data: List[Dict]) -> Dict[str, Any]:
        """Analyze impression share trends"""
        df = pd.DataFrame(share_data)

        analysis = {}

        if 'impression_share' in df.columns:
            analysis['impression_share'] = df['impression_share'].iloc[-1]
            analysis['trend'] = self._calculate_trend(df, 'impression_share')

        if 'lost_impression_share_budget' in df.columns:
            analysis['lost_share_budget'] = df['lost_impression_share_budget'].iloc[-1]

        if 'lost_impression_share_rank' in df.columns:
            analysis['lost_share_rank'] = df['lost_impression_share_rank'].iloc[-1]

        return analysis

    def _analyze_competitor_trends(self, competitor_data: List[Dict]) -> Dict[str, Any]:
        """Analyze competitor performance trends"""
        df = pd.DataFrame(competitor_data)

        return {
            'auction_insights': {
                'overlap_rate_trend': self._calculate_trend(df, 'overlap_rate') if 'overlap_rate' in df else {},
                'outranking_share_trend': self._calculate_trend(df, 'outranking_share') if 'outranking_share' in df else {},
                'top_of_page_rate_trend': self._calculate_trend(df, 'top_of_page_rate') if 'top_of_page_rate' in df else {}
            }
        }

    def _generate_trend_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of all trends"""
        summary = {
            'improving_metrics': [],
            'declining_metrics': [],
            'stable_metrics': [],
            'volatile_metrics': []
        }

        for metric, data in metrics.items():
            if not data.get('trend'):
                continue

            trend = data['trend']
            volatility = data.get('volatility', {})

            if volatility.get('stability') == 'volatile':
                summary['volatile_metrics'].append(metric)
            elif trend.get('direction') == 'increasing' and trend.get('is_significant'):
                summary['improving_metrics'].append(metric)
            elif trend.get('direction') == 'decreasing' and trend.get('is_significant'):
                summary['declining_metrics'].append(metric)
            else:
                summary['stable_metrics'].append(metric)

        return summary

    def _generate_trend_insights(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate insights from trend analysis"""
        insights = []

        # Check conversion trends
        if 'conversions' in metrics:
            conv_trend = metrics['conversions'].get('trend', {})
            if conv_trend.get('direction') == 'increasing' and conv_trend.get('strength') == 'strong':
                insights.append("Strong positive conversion trend indicates effective optimization")
            elif conv_trend.get('direction') == 'decreasing':
                insights.append("Declining conversion trend requires immediate attention")

        # Check cost efficiency
        if 'cost' in metrics and 'conversions' in metrics:
            cost_growth = metrics['cost'].get('growth_rate', {}).get('average_growth', 0)
            conv_growth = metrics['conversions'].get('growth_rate', {}).get('average_growth', 0)

            if conv_growth > cost_growth + 10:
                insights.append("Conversions growing faster than costs - excellent efficiency")
            elif cost_growth > conv_growth + 20:
                insights.append("Costs growing faster than conversions - review efficiency")

        # Check volatility
        volatile_count = sum(
            1 for m in metrics.values()
            if m.get('volatility', {}).get('stability') == 'volatile'
        )

        if volatile_count > len(metrics) / 2:
            insights.append("High volatility across metrics - stabilization needed")

        return insights[:5]

    def _generate_trend_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations from trend analysis"""
        recommendations = []

        summary = analysis.get('summary', {})

        if summary.get('declining_metrics'):
            recommendations.append(
                f"Address declining metrics: {', '.join(summary['declining_metrics'])}"
            )

        if summary.get('volatile_metrics'):
            recommendations.append(
                "Stabilize volatile metrics through consistent optimization"
            )

        # Check specific metrics
        metrics = analysis.get('metrics', {})

        if 'ctr' in metrics:
            ctr_trend = metrics['ctr'].get('trend', {})
            if ctr_trend.get('direction') == 'decreasing':
                recommendations.append("Refresh ad copy to reverse CTR decline")

        if 'conversion_rate' in metrics:
            cvr_momentum = metrics['conversion_rate'].get('momentum', {})
            if cvr_momentum.get('signal') == 'bearish':
                recommendations.append("Conversion rate showing negative momentum - review landing pages")

        return recommendations[:5]

    def _generate_competitive_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate competitive insights"""
        insights = []

        if analysis.get('share_of_voice_trend'):
            sov = analysis['share_of_voice_trend']
            if sov.get('trend', {}).get('direction') == 'decreasing':
                insights.append("Losing market share to competitors")

        if analysis.get('opportunities'):
            insights.append(f"Found {len(analysis['opportunities'])} competitive opportunities")

        if analysis.get('threats'):
            insights.append(f"Identified {len(analysis['threats'])} competitive threats")

        return insights

    def get_tools(self) -> List[Tool]:
        """Get LangChain tools for trend analysis"""
        return [
            Tool(
                name="analyze_performance_trends",
                func=self.analyze_performance_trends,
                description="Analyze performance trends with forecasting and seasonality detection"
            ),
            Tool(
                name="analyze_keyword_trends",
                func=self.analyze_keyword_trends,
                description="Analyze keyword performance trends and identify opportunities"
            ),
            Tool(
                name="analyze_competitive_trends",
                func=self.analyze_competitive_trends,
                description="Analyze competitive and market trends"
            )
        ]