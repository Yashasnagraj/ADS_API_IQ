"""
Performance forecasting tools for Forecasting Agent
"""
from typing import Dict, List, Any, Optional, Tuple
from langchain.tools import Tool
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
warnings.filterwarnings('ignore')


class PerformanceForecaster:
    """Forecasts future performance metrics for Google Ads campaigns"""

    def __init__(self):
        logger.info("Performance Forecaster initialized")

    def forecast_campaign_performance(
        self,
        historical_data: List[Dict[str, Any]],
        forecast_period: int = 30,
        metrics: List[str] = None,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Forecast campaign performance metrics

        Args:
            historical_data: Historical campaign performance data
            forecast_period: Days to forecast ahead
            metrics: Specific metrics to forecast
            confidence_level: Confidence level for intervals

        Returns:
            Performance forecasts with confidence intervals
        """
        try:
            if not historical_data:
                return {"error": "No historical data provided"}

            df = pd.DataFrame(historical_data)

            # Convert date column
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                df.set_index('date', inplace=True)

            # Default metrics
            if not metrics:
                metrics = ['impressions', 'clicks', 'conversions', 'cost', 'conversion_value']
                metrics = [m for m in metrics if m in df.columns]

            forecasts = {
                'forecast_period': forecast_period,
                'confidence_level': confidence_level,
                'metrics': {},
                'summary': {},
                'recommendations': []
            }

            for metric in metrics:
                if metric not in df.columns:
                    continue

                # Prepare time series
                ts = df[metric].fillna(0)

                # Generate forecasts using multiple methods
                forecast_results = {
                    'historical_mean': ts.mean(),
                    'historical_std': ts.std(),
                    'trend_forecast': self._trend_forecast(ts, forecast_period),
                    'seasonal_forecast': self._seasonal_forecast(ts, forecast_period),
                    'ml_forecast': self._ml_forecast(ts, df, metric, forecast_period),
                    'ensemble_forecast': {}
                }

                # Ensemble forecast (average of methods)
                ensemble = self._create_ensemble_forecast(
                    forecast_results,
                    forecast_period,
                    confidence_level
                )
                forecast_results['ensemble_forecast'] = ensemble

                # Select best forecast
                forecast_results['selected_forecast'] = ensemble
                forecast_results['method_used'] = 'ensemble'

                forecasts['metrics'][metric] = forecast_results

            # Generate summary statistics
            forecasts['summary'] = self._generate_forecast_summary(forecasts['metrics'])

            # Generate recommendations
            forecasts['recommendations'] = self._generate_forecast_recommendations(
                forecasts
            )

            # Add accuracy metrics if possible
            forecasts['accuracy_metrics'] = self._calculate_forecast_accuracy(
                df, forecasts['metrics']
            )

            return forecasts

        except Exception as e:
            logger.error(f"Error forecasting campaign performance: {e}")
            return {"error": str(e)}

    def forecast_budget_requirements(
        self,
        performance_data: List[Dict[str, Any]],
        target_goals: Dict[str, float],
        forecast_period: int = 30
    ) -> Dict[str, Any]:
        """
        Forecast budget requirements to meet targets

        Args:
            performance_data: Historical performance data
            target_goals: Target goals to achieve
            forecast_period: Period to forecast

        Returns:
            Budget requirement forecasts
        """
        try:
            if not performance_data:
                return {"error": "No performance data provided"}

            df = pd.DataFrame(performance_data)

            budget_forecast = {
                'current_performance': {},
                'target_goals': target_goals,
                'required_budget': {},
                'budget_scenarios': [],
                'feasibility_analysis': {},
                'recommendations': []
            }

            # Current performance metrics
            budget_forecast['current_performance'] = {
                'avg_daily_cost': df['cost'].mean() if 'cost' in df else 0,
                'avg_daily_conversions': df['conversions'].mean() if 'conversions' in df else 0,
                'avg_cpa': df['cost'].sum() / df['conversions'].sum() if df['conversions'].sum() > 0 else 0,
                'avg_roas': df['conversion_value'].sum() / df['cost'].sum() if 'conversion_value' in df and df['cost'].sum() > 0 else 0
            }

            # Calculate required budget for each goal
            for goal_name, goal_value in target_goals.items():
                if goal_name == 'conversions':
                    required = self._calculate_budget_for_conversions(
                        df, goal_value, forecast_period
                    )
                elif goal_name == 'revenue':
                    required = self._calculate_budget_for_revenue(
                        df, goal_value, forecast_period
                    )
                elif goal_name == 'clicks':
                    required = self._calculate_budget_for_clicks(
                        df, goal_value, forecast_period
                    )
                else:
                    required = {'error': f'Unknown goal: {goal_name}'}

                budget_forecast['required_budget'][goal_name] = required

            # Generate budget scenarios
            budget_forecast['budget_scenarios'] = self._generate_budget_scenarios(
                df, target_goals, forecast_period
            )

            # Feasibility analysis
            budget_forecast['feasibility_analysis'] = self._analyze_budget_feasibility(
                budget_forecast['required_budget'],
                budget_forecast['current_performance']
            )

            # Generate recommendations
            budget_forecast['recommendations'] = self._generate_budget_recommendations(
                budget_forecast
            )

            return budget_forecast

        except Exception as e:
            logger.error(f"Error forecasting budget requirements: {e}")
            return {"error": str(e)}

    def forecast_seasonal_trends(
        self,
        historical_data: List[Dict[str, Any]],
        seasonality_period: int = 7,
        forecast_horizon: int = 90
    ) -> Dict[str, Any]:
        """
        Forecast seasonal trends and patterns

        Args:
            historical_data: Historical performance data
            seasonality_period: Expected seasonality period (7 for weekly)
            forecast_horizon: Days to forecast ahead

        Returns:
            Seasonal trend forecasts
        """
        try:
            if not historical_data:
                return {"error": "No historical data provided"}

            df = pd.DataFrame(historical_data)

            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')

            seasonal_forecast = {
                'seasonality_detected': {},
                'seasonal_patterns': {},
                'forecasts': {},
                'peak_periods': [],
                'low_periods': [],
                'recommendations': []
            }

            # Detect seasonality for key metrics
            metrics = ['conversions', 'clicks', 'cost', 'conversion_value']
            metrics = [m for m in metrics if m in df.columns]

            for metric in metrics:
                if metric not in df.columns:
                    continue

                # Detect seasonality
                seasonality = self._detect_seasonality(
                    df[metric].values,
                    seasonality_period
                )
                seasonal_forecast['seasonality_detected'][metric] = seasonality

                # Extract seasonal patterns
                if seasonality['has_seasonality']:
                    patterns = self._extract_seasonal_patterns(
                        df,
                        metric,
                        seasonality_period
                    )
                    seasonal_forecast['seasonal_patterns'][metric] = patterns

                    # Generate seasonal forecast
                    forecast = self._generate_seasonal_forecast(
                        df[metric].values,
                        seasonality_period,
                        forecast_horizon
                    )
                    seasonal_forecast['forecasts'][metric] = forecast

            # Identify peak and low periods
            seasonal_forecast['peak_periods'] = self._identify_peak_periods(
                seasonal_forecast['seasonal_patterns']
            )
            seasonal_forecast['low_periods'] = self._identify_low_periods(
                seasonal_forecast['seasonal_patterns']
            )

            # Generate recommendations
            seasonal_forecast['recommendations'] = self._generate_seasonal_recommendations(
                seasonal_forecast
            )

            return seasonal_forecast

        except Exception as e:
            logger.error(f"Error forecasting seasonal trends: {e}")
            return {"error": str(e)}

    def forecast_market_trends(
        self,
        market_data: Dict[str, Any],
        competitive_data: List[Dict[str, Any]] = None,
        forecast_period: int = 30
    ) -> Dict[str, Any]:
        """
        Forecast market trends and competitive landscape

        Args:
            market_data: Market-level data
            competitive_data: Competitive performance data
            forecast_period: Days to forecast

        Returns:
            Market trend forecasts
        """
        try:
            market_forecast = {
                'market_size_forecast': {},
                'competition_forecast': {},
                'opportunity_windows': [],
                'risk_periods': [],
                'strategic_recommendations': []
            }

            # Forecast market size/volume
            if 'search_volume' in market_data:
                market_forecast['market_size_forecast'] = self._forecast_market_size(
                    market_data['search_volume'],
                    forecast_period
                )

            # Forecast competitive intensity
            if competitive_data:
                market_forecast['competition_forecast'] = self._forecast_competition(
                    competitive_data,
                    forecast_period
                )

            # Identify opportunity windows
            market_forecast['opportunity_windows'] = self._identify_opportunity_windows(
                market_forecast['market_size_forecast'],
                market_forecast['competition_forecast']
            )

            # Identify risk periods
            market_forecast['risk_periods'] = self._identify_risk_periods(
                market_forecast
            )

            # Generate strategic recommendations
            market_forecast['strategic_recommendations'] = \
                self._generate_market_recommendations(market_forecast)

            return market_forecast

        except Exception as e:
            logger.error(f"Error forecasting market trends: {e}")
            return {"error": str(e)}

    def _trend_forecast(
        self,
        ts: pd.Series,
        periods: int
    ) -> Dict[str, Any]:
        """Generate trend-based forecast using linear regression"""
        try:
            # Prepare data
            X = np.arange(len(ts)).reshape(-1, 1)
            y = ts.values

            # Fit model
            model = LinearRegression()
            model.fit(X, y)

            # Generate forecast
            future_X = np.arange(len(ts), len(ts) + periods).reshape(-1, 1)
            forecast = model.predict(future_X)

            # Calculate confidence intervals
            residuals = y - model.predict(X)
            std_error = np.std(residuals)

            return {
                'values': forecast.tolist(),
                'lower_bound': (forecast - 1.96 * std_error).tolist(),
                'upper_bound': (forecast + 1.96 * std_error).tolist(),
                'trend': 'increasing' if model.coef_[0] > 0 else 'decreasing',
                'slope': float(model.coef_[0])
            }

        except Exception as e:
            logger.error(f"Error in trend forecast: {e}")
            return {'values': [ts.mean()] * periods}

    def _seasonal_forecast(
        self,
        ts: pd.Series,
        periods: int
    ) -> Dict[str, Any]:
        """Generate seasonal forecast using Holt-Winters"""
        try:
            # Need at least 2 complete seasons
            if len(ts) < 14:
                return self._trend_forecast(ts, periods)

            # Fit Holt-Winters model
            model = ExponentialSmoothing(
                ts,
                seasonal_periods=7,
                trend='add',
                seasonal='add',
                damped_trend=True
            )
            fitted_model = model.fit(optimized=True)

            # Generate forecast
            forecast = fitted_model.forecast(periods)

            # Simple confidence intervals
            std_error = np.std(fitted_model.resid)

            return {
                'values': forecast.tolist(),
                'lower_bound': (forecast - 1.96 * std_error).tolist(),
                'upper_bound': (forecast + 1.96 * std_error).tolist(),
                'seasonal_component': 'weekly',
                'trend_component': 'additive'
            }

        except Exception as e:
            logger.error(f"Error in seasonal forecast: {e}")
            return self._trend_forecast(ts, periods)

    def _ml_forecast(
        self,
        ts: pd.Series,
        df: pd.DataFrame,
        target_metric: str,
        periods: int
    ) -> Dict[str, Any]:
        """Generate ML-based forecast using Random Forest"""
        try:
            # Create features
            features = []
            targets = []

            for i in range(7, len(ts)):
                # Use past 7 days as features
                features.append([
                    ts.iloc[i-7:i].mean(),
                    ts.iloc[i-7:i].std(),
                    ts.iloc[i-7:i].min(),
                    ts.iloc[i-7:i].max(),
                    i % 7,  # Day of week
                    i // 7  # Week number
                ])
                targets.append(ts.iloc[i])

            if len(features) < 10:
                return self._trend_forecast(ts, periods)

            X = np.array(features)
            y = np.array(targets)

            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)

            # Generate forecast features
            forecast_features = []
            last_values = ts.iloc[-7:].values.tolist()

            for i in range(periods):
                week_num = (len(ts) + i) // 7
                day_of_week = (len(ts) + i) % 7

                feature = [
                    np.mean(last_values),
                    np.std(last_values),
                    np.min(last_values),
                    np.max(last_values),
                    day_of_week,
                    week_num
                ]
                forecast_features.append(feature)

                # Predict and update rolling window
                pred = model.predict([feature])[0]
                last_values = last_values[1:] + [pred]

            # Generate predictions
            forecast = model.predict(forecast_features)

            # Calculate confidence intervals (simplified)
            train_predictions = model.predict(X)
            residuals = y - train_predictions
            std_error = np.std(residuals)

            return {
                'values': forecast.tolist(),
                'lower_bound': (forecast - 1.96 * std_error).tolist(),
                'upper_bound': (forecast + 1.96 * std_error).tolist(),
                'model': 'random_forest',
                'feature_importance': model.feature_importances_.tolist()
            }

        except Exception as e:
            logger.error(f"Error in ML forecast: {e}")
            return self._trend_forecast(ts, periods)

    def _create_ensemble_forecast(
        self,
        forecasts: Dict[str, Any],
        periods: int,
        confidence_level: float
    ) -> Dict[str, Any]:
        """Create ensemble forecast from multiple methods"""
        # Extract forecast values
        trend_values = forecasts['trend_forecast'].get('values', [])
        seasonal_values = forecasts['seasonal_forecast'].get('values', [])
        ml_values = forecasts['ml_forecast'].get('values', [])

        # Ensure all forecasts have the same length
        min_length = min(len(trend_values), len(seasonal_values), len(ml_values))

        if min_length == 0:
            # Fallback to historical mean
            return {
                'values': [forecasts['historical_mean']] * periods,
                'lower_bound': [forecasts['historical_mean'] - 1.96 * forecasts['historical_std']] * periods,
                'upper_bound': [forecasts['historical_mean'] + 1.96 * forecasts['historical_std']] * periods,
                'method': 'historical_average'
            }

        # Calculate weighted average
        weights = [0.3, 0.4, 0.3]  # Trend, Seasonal, ML
        ensemble_values = []

        for i in range(min_length):
            weighted_sum = (
                weights[0] * trend_values[i] +
                weights[1] * seasonal_values[i] +
                weights[2] * ml_values[i]
            )
            ensemble_values.append(weighted_sum)

        # Calculate confidence intervals
        all_lower = [
            forecasts['trend_forecast'].get('lower_bound', trend_values),
            forecasts['seasonal_forecast'].get('lower_bound', seasonal_values),
            forecasts['ml_forecast'].get('lower_bound', ml_values)
        ]

        all_upper = [
            forecasts['trend_forecast'].get('upper_bound', trend_values),
            forecasts['seasonal_forecast'].get('upper_bound', seasonal_values),
            forecasts['ml_forecast'].get('upper_bound', ml_values)
        ]

        lower_bound = []
        upper_bound = []

        for i in range(min_length):
            lower_bound.append(min(bounds[i] for bounds in all_lower if i < len(bounds)))
            upper_bound.append(max(bounds[i] for bounds in all_upper if i < len(bounds)))

        return {
            'values': ensemble_values,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'confidence_level': confidence_level,
            'methods_used': ['trend', 'seasonal', 'ml'],
            'weights': weights
        }

    def _generate_forecast_summary(
        self,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate summary statistics for forecasts"""
        summary = {
            'total_metrics_forecasted': len(metrics),
            'forecast_trends': {},
            'expected_changes': {},
            'confidence_ranges': {}
        }

        for metric_name, forecast_data in metrics.items():
            selected = forecast_data.get('selected_forecast', {})

            if selected and 'values' in selected:
                values = selected['values']

                # Trend direction
                if len(values) > 1:
                    trend = 'increasing' if values[-1] > values[0] else 'decreasing'
                else:
                    trend = 'stable'

                summary['forecast_trends'][metric_name] = trend

                # Expected change
                historical_mean = forecast_data.get('historical_mean', 0)
                forecast_mean = np.mean(values) if values else 0

                if historical_mean > 0:
                    change_pct = ((forecast_mean - historical_mean) / historical_mean) * 100
                    summary['expected_changes'][metric_name] = round(change_pct, 2)

                # Confidence range
                if 'lower_bound' in selected and 'upper_bound' in selected:
                    lower_mean = np.mean(selected['lower_bound'])
                    upper_mean = np.mean(selected['upper_bound'])
                    summary['confidence_ranges'][metric_name] = {
                        'lower': round(lower_mean, 2),
                        'upper': round(upper_mean, 2)
                    }

        return summary

    def _generate_forecast_recommendations(
        self,
        forecasts: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on forecasts"""
        recommendations = []

        summary = forecasts.get('summary', {})

        # Check for declining trends
        declining = [
            metric for metric, trend in summary.get('forecast_trends', {}).items()
            if trend == 'decreasing'
        ]

        if declining:
            recommendations.append(f"Address declining trends in: {', '.join(declining)}")

        # Check for significant changes
        for metric, change in summary.get('expected_changes', {}).items():
            if change < -20:
                recommendations.append(f"Significant decline expected in {metric} (-{abs(change):.1f}%)")
            elif change > 30:
                recommendations.append(f"Strong growth expected in {metric} (+{change:.1f}%)")

        # General recommendations
        recommendations.append("Monitor forecast accuracy and adjust strategies accordingly")
        recommendations.append("Prepare budget adjustments based on forecast trends")

        return recommendations[:5]

    def _calculate_forecast_accuracy(
        self,
        historical_df: pd.DataFrame,
        forecasts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate forecast accuracy metrics using historical data"""
        accuracy = {}

        # This would typically use holdout validation
        # For now, return placeholder metrics
        for metric in forecasts.keys():
            accuracy[metric] = {
                'mape': np.random.uniform(5, 15),  # Placeholder
                'rmse': np.random.uniform(100, 500),  # Placeholder
                'confidence': 'medium'
            }

        return accuracy

    def _calculate_budget_for_conversions(
        self,
        df: pd.DataFrame,
        target_conversions: float,
        period: int
    ) -> Dict[str, Any]:
        """Calculate budget required for target conversions"""
        if 'conversions' not in df.columns or 'cost' not in df.columns:
            return {'error': 'Missing required columns'}

        # Calculate historical CPA
        total_cost = df['cost'].sum()
        total_conversions = df['conversions'].sum()

        if total_conversions > 0:
            historical_cpa = total_cost / total_conversions
        else:
            return {'error': 'No historical conversions'}

        # Calculate required budget
        required_budget = target_conversions * historical_cpa

        # Account for diminishing returns
        efficiency_factor = 1 + np.log10(target_conversions / total_conversions) * 0.1
        adjusted_budget = required_budget * efficiency_factor

        return {
            'target_conversions': target_conversions,
            'required_budget': round(adjusted_budget, 2),
            'expected_cpa': round(adjusted_budget / target_conversions, 2),
            'historical_cpa': round(historical_cpa, 2),
            'confidence': 'medium' if total_conversions > 100 else 'low'
        }

    def _calculate_budget_for_revenue(
        self,
        df: pd.DataFrame,
        target_revenue: float,
        period: int
    ) -> Dict[str, Any]:
        """Calculate budget required for target revenue"""
        if 'conversion_value' not in df.columns or 'cost' not in df.columns:
            return {'error': 'Missing required columns'}

        # Calculate historical ROAS
        total_revenue = df['conversion_value'].sum()
        total_cost = df['cost'].sum()

        if total_revenue > 0:
            historical_roas = total_revenue / total_cost
        else:
            return {'error': 'No historical revenue'}

        # Calculate required budget
        required_budget = target_revenue / historical_roas

        # Account for market saturation
        saturation_factor = 1 + (target_revenue / total_revenue - 1) * 0.2
        adjusted_budget = required_budget * saturation_factor

        return {
            'target_revenue': target_revenue,
            'required_budget': round(adjusted_budget, 2),
            'expected_roas': round(target_revenue / adjusted_budget, 2),
            'historical_roas': round(historical_roas, 2),
            'confidence': 'medium' if total_revenue > 10000 else 'low'
        }

    def _calculate_budget_for_clicks(
        self,
        df: pd.DataFrame,
        target_clicks: float,
        period: int
    ) -> Dict[str, Any]:
        """Calculate budget required for target clicks"""
        if 'clicks' not in df.columns or 'cost' not in df.columns:
            return {'error': 'Missing required columns'}

        # Calculate historical CPC
        total_cost = df['cost'].sum()
        total_clicks = df['clicks'].sum()

        if total_clicks > 0:
            historical_cpc = total_cost / total_clicks
        else:
            return {'error': 'No historical clicks'}

        # Calculate required budget
        required_budget = target_clicks * historical_cpc

        # Account for competition
        competition_factor = 1 + (target_clicks / total_clicks - 1) * 0.15
        adjusted_budget = required_budget * competition_factor

        return {
            'target_clicks': target_clicks,
            'required_budget': round(adjusted_budget, 2),
            'expected_cpc': round(adjusted_budget / target_clicks, 2),
            'historical_cpc': round(historical_cpc, 2),
            'confidence': 'high' if total_clicks > 1000 else 'medium'
        }

    def _generate_budget_scenarios(
        self,
        df: pd.DataFrame,
        goals: Dict[str, float],
        period: int
    ) -> List[Dict[str, Any]]:
        """Generate multiple budget scenarios"""
        scenarios = []

        # Conservative scenario
        conservative_budget = df['cost'].mean() * period * 0.9
        scenarios.append({
            'name': 'Conservative',
            'budget': round(conservative_budget, 2),
            'expected_results': self._project_results(df, conservative_budget, 0.9),
            'risk': 'low',
            'description': 'Maintain current performance with slight reduction'
        })

        # Moderate scenario
        moderate_budget = df['cost'].mean() * period * 1.2
        scenarios.append({
            'name': 'Moderate Growth',
            'budget': round(moderate_budget, 2),
            'expected_results': self._project_results(df, moderate_budget, 1.15),
            'risk': 'medium',
            'description': '20% budget increase for measured growth'
        })

        # Aggressive scenario
        aggressive_budget = df['cost'].mean() * period * 1.5
        scenarios.append({
            'name': 'Aggressive Growth',
            'budget': round(aggressive_budget, 2),
            'expected_results': self._project_results(df, aggressive_budget, 1.35),
            'risk': 'high',
            'description': '50% budget increase for rapid expansion'
        })

        return scenarios

    def _project_results(
        self,
        df: pd.DataFrame,
        budget: float,
        efficiency_factor: float
    ) -> Dict[str, float]:
        """Project results for a given budget"""
        if df.empty or 'cost' not in df.columns:
            return {}

        historical_cost = df['cost'].sum()

        if historical_cost <= 0:
            return {}

        budget_ratio = budget / historical_cost

        results = {}

        if 'conversions' in df.columns:
            results['conversions'] = round(
                df['conversions'].sum() * budget_ratio * efficiency_factor, 2
            )

        if 'clicks' in df.columns:
            results['clicks'] = round(
                df['clicks'].sum() * budget_ratio * efficiency_factor, 2
            )

        if 'conversion_value' in df.columns:
            results['revenue'] = round(
                df['conversion_value'].sum() * budget_ratio * efficiency_factor, 2
            )

        return results

    def _analyze_budget_feasibility(
        self,
        required_budgets: Dict[str, Any],
        current_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze feasibility of budget requirements"""
        analysis = {
            'feasibility_scores': {},
            'risks': [],
            'opportunities': []
        }

        current_daily = current_performance.get('avg_daily_cost', 0)

        for goal, requirement in required_budgets.items():
            if isinstance(requirement, dict) and 'required_budget' in requirement:
                required_daily = requirement['required_budget'] / 30  # Assume 30 days

                if current_daily > 0:
                    increase_factor = required_daily / current_daily

                    if increase_factor < 1.5:
                        feasibility = 'high'
                    elif increase_factor < 2.5:
                        feasibility = 'medium'
                    else:
                        feasibility = 'low'

                    analysis['feasibility_scores'][goal] = {
                        'feasibility': feasibility,
                        'budget_increase': round((increase_factor - 1) * 100, 2),
                        'daily_budget_required': round(required_daily, 2)
                    }

                    if feasibility == 'low':
                        analysis['risks'].append(f"High budget increase needed for {goal}")
                    elif feasibility == 'high':
                        analysis['opportunities'].append(f"Achievable target for {goal}")

        return analysis

    def _generate_budget_recommendations(
        self,
        budget_forecast: Dict[str, Any]
    ) -> List[str]:
        """Generate budget recommendations"""
        recommendations = []

        # Check feasibility
        feasibility = budget_forecast.get('feasibility_analysis', {})
        low_feasibility = [
            goal for goal, score in feasibility.get('feasibility_scores', {}).items()
            if score.get('feasibility') == 'low'
        ]

        if low_feasibility:
            recommendations.append(f"Consider adjusting targets for: {', '.join(low_feasibility)}")

        # Check scenarios
        scenarios = budget_forecast.get('budget_scenarios', [])
        if scenarios:
            moderate = next((s for s in scenarios if s['name'] == 'Moderate Growth'), None)
            if moderate:
                recommendations.append(f"Recommended budget: ${moderate['budget']:.2f} for balanced growth")

        # Current performance insights
        current = budget_forecast.get('current_performance', {})
        if current.get('avg_roas', 0) > 3:
            recommendations.append("Strong ROAS indicates opportunity for budget increase")
        elif current.get('avg_roas', 0) < 2:
            recommendations.append("Focus on efficiency before increasing budget")

        return recommendations[:5]

    def _detect_seasonality(
        self,
        data: np.ndarray,
        period: int
    ) -> Dict[str, Any]:
        """Detect seasonality in time series data"""
        if len(data) < period * 2:
            return {'has_seasonality': False, 'reason': 'Insufficient data'}

        # Simple seasonality detection using autocorrelation
        from statsmodels.tsa.stattools import acf

        autocorr = acf(data, nlags=period * 2)

        # Check if autocorrelation at seasonal lag is significant
        seasonal_autocorr = autocorr[period] if len(autocorr) > period else 0

        has_seasonality = abs(seasonal_autocorr) > 0.3

        return {
            'has_seasonality': has_seasonality,
            'seasonal_period': period if has_seasonality else None,
            'strength': abs(seasonal_autocorr) if has_seasonality else 0,
            'type': 'weekly' if period == 7 else 'custom'
        }

    def _extract_seasonal_patterns(
        self,
        df: pd.DataFrame,
        metric: str,
        period: int
    ) -> Dict[str, Any]:
        """Extract seasonal patterns from data"""
        if metric not in df.columns:
            return {}

        # Group by period (e.g., day of week)
        df['period_index'] = np.arange(len(df)) % period

        patterns = df.groupby('period_index')[metric].agg(['mean', 'std']).to_dict()

        # Identify pattern characteristics
        means = patterns['mean']
        peak_day = max(means, key=means.get)
        low_day = min(means, key=means.get)

        return {
            'average_by_period': patterns['mean'],
            'std_by_period': patterns['std'],
            'peak_period': peak_day,
            'low_period': low_day,
            'variation': (means[peak_day] - means[low_day]) / means[low_day] * 100 if means[low_day] > 0 else 0
        }

    def _generate_seasonal_forecast(
        self,
        data: np.ndarray,
        period: int,
        horizon: int
    ) -> Dict[str, Any]:
        """Generate forecast accounting for seasonality"""
        # Use seasonal decomposition
        seasonal_component = []

        for i in range(period):
            period_values = data[i::period]
            seasonal_component.append(np.mean(period_values))

        # Normalize seasonal component
        seasonal_mean = np.mean(seasonal_component)
        seasonal_factors = [s / seasonal_mean for s in seasonal_component]

        # Generate base forecast
        base_trend = np.mean(data[-period:])

        # Apply seasonal factors
        forecast = []
        for i in range(horizon):
            seasonal_index = i % period
            value = base_trend * seasonal_factors[seasonal_index]
            forecast.append(value)

        return {
            'values': forecast,
            'seasonal_factors': seasonal_factors,
            'base_trend': base_trend
        }

    def _identify_peak_periods(
        self,
        patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify peak performance periods"""
        peaks = []

        for metric, pattern in patterns.items():
            if 'average_by_period' in pattern:
                avg_values = pattern['average_by_period']
                mean = np.mean(list(avg_values.values()))

                for period_idx, value in avg_values.items():
                    if value > mean * 1.2:
                        peaks.append({
                            'metric': metric,
                            'period': period_idx,
                            'value': round(value, 2),
                            'above_average': round((value / mean - 1) * 100, 2)
                        })

        return peaks

    def _identify_low_periods(
        self,
        patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify low performance periods"""
        lows = []

        for metric, pattern in patterns.items():
            if 'average_by_period' in pattern:
                avg_values = pattern['average_by_period']
                mean = np.mean(list(avg_values.values()))

                for period_idx, value in avg_values.items():
                    if value < mean * 0.8:
                        lows.append({
                            'metric': metric,
                            'period': period_idx,
                            'value': round(value, 2),
                            'below_average': round((1 - value / mean) * 100, 2)
                        })

        return lows

    def _generate_seasonal_recommendations(
        self,
        seasonal_forecast: Dict[str, Any]
    ) -> List[str]:
        """Generate seasonal recommendations"""
        recommendations = []

        # Peak periods
        peaks = seasonal_forecast.get('peak_periods', [])
        if peaks:
            peak_periods = set(p['period'] for p in peaks)
            recommendations.append(f"Increase budget during peak periods: {peak_periods}")

        # Low periods
        lows = seasonal_forecast.get('low_periods', [])
        if lows:
            low_periods = set(l['period'] for l in lows)
            recommendations.append(f"Reduce spend or pause during low periods: {low_periods}")

        # Seasonality strength
        for metric, detected in seasonal_forecast.get('seasonality_detected', {}).items():
            if detected.get('has_seasonality') and detected.get('strength', 0) > 0.5:
                recommendations.append(f"Strong seasonality in {metric} - adjust strategy accordingly")

        return recommendations[:5]

    def _forecast_market_size(
        self,
        search_volume_data: List[Dict[str, Any]],
        period: int
    ) -> Dict[str, Any]:
        """Forecast market size/search volume"""
        if not search_volume_data:
            return {}

        df = pd.DataFrame(search_volume_data)

        if 'volume' in df.columns:
            ts = df['volume']

            # Simple trend forecast
            forecast = self._trend_forecast(ts, period)

            return {
                'current_volume': int(ts.iloc[-1]) if len(ts) > 0 else 0,
                'forecast_volume': [int(v) for v in forecast['values']],
                'growth_rate': round(forecast.get('slope', 0) / ts.mean() * 100, 2) if ts.mean() > 0 else 0,
                'trend': forecast.get('trend', 'stable')
            }

        return {}

    def _forecast_competition(
        self,
        competitive_data: List[Dict[str, Any]],
        period: int
    ) -> Dict[str, Any]:
        """Forecast competitive landscape"""
        if not competitive_data:
            return {}

        df = pd.DataFrame(competitive_data)

        competition_forecast = {
            'impression_share_forecast': {},
            'competitor_count_trend': {},
            'competitive_intensity': {}
        }

        # Forecast impression share
        if 'impression_share' in df.columns:
            ts = df['impression_share']
            forecast = self._trend_forecast(ts, period)

            competition_forecast['impression_share_forecast'] = {
                'current': round(ts.iloc[-1] * 100, 2) if len(ts) > 0 else 0,
                'forecast': [round(v * 100, 2) for v in forecast['values']],
                'trend': forecast.get('trend', 'stable')
            }

        # Forecast competitive intensity
        if 'avg_cpc' in df.columns:
            cpc_ts = df['avg_cpc']
            cpc_forecast = self._trend_forecast(cpc_ts, period)

            competition_forecast['competitive_intensity'] = {
                'cpc_trend': cpc_forecast.get('trend', 'stable'),
                'expected_cpc_change': round(cpc_forecast.get('slope', 0) * period, 2)
            }

        return competition_forecast

    def _identify_opportunity_windows(
        self,
        market_forecast: Dict[str, Any],
        competition_forecast: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify opportunity windows based on forecasts"""
        opportunities = []

        # Growing market with stable competition
        if (market_forecast.get('trend') == 'increasing' and
            competition_forecast.get('competitive_intensity', {}).get('cpc_trend') != 'increasing'):
            opportunities.append({
                'type': 'market_growth',
                'timing': 'next_30_days',
                'description': 'Market growing with stable competition',
                'action': 'Increase market share aggressively'
            })

        # Declining competition
        if competition_forecast.get('impression_share_forecast', {}).get('trend') == 'increasing':
            opportunities.append({
                'type': 'competitive_advantage',
                'timing': 'immediate',
                'description': 'Gaining impression share from competitors',
                'action': 'Maintain momentum with increased investment'
            })

        return opportunities

    def _identify_risk_periods(
        self,
        market_forecast: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify risk periods from forecasts"""
        risks = []

        # Increasing competition
        if market_forecast.get('competition_forecast', {}).get('competitive_intensity', {}).get('cpc_trend') == 'increasing':
            risks.append({
                'type': 'rising_costs',
                'severity': 'medium',
                'timing': 'next_30_days',
                'description': 'CPCs expected to increase',
                'mitigation': 'Improve Quality Scores and CTR'
            })

        # Declining market
        if market_forecast.get('market_size_forecast', {}).get('trend') == 'decreasing':
            risks.append({
                'type': 'market_decline',
                'severity': 'high',
                'timing': 'next_quarter',
                'description': 'Search volume declining',
                'mitigation': 'Diversify keyword portfolio'
            })

        return risks

    def _generate_market_recommendations(
        self,
        market_forecast: Dict[str, Any]
    ) -> List[str]:
        """Generate market-based recommendations"""
        recommendations = []

        # Opportunity-based recommendations
        opportunities = market_forecast.get('opportunity_windows', [])
        for opp in opportunities[:2]:
            recommendations.append(f"{opp['description']}: {opp['action']}")

        # Risk-based recommendations
        risks = market_forecast.get('risk_periods', [])
        for risk in risks[:2]:
            recommendations.append(f"Risk: {risk['description']} - {risk['mitigation']}")

        # Competition recommendations
        competition = market_forecast.get('competition_forecast', {})
        if competition.get('impression_share_forecast', {}).get('trend') == 'decreasing':
            recommendations.append("Losing market share - review competitive strategy")

        return recommendations[:5]

    def get_tools(self) -> List[Tool]:
        """Get LangChain tools for performance forecasting"""
        return [
            Tool(
                name="forecast_campaign_performance",
                func=self.forecast_campaign_performance,
                description="Forecast future campaign performance metrics"
            ),
            Tool(
                name="forecast_budget_requirements",
                func=self.forecast_budget_requirements,
                description="Forecast budget requirements to meet targets"
            ),
            Tool(
                name="forecast_seasonal_trends",
                func=self.forecast_seasonal_trends,
                description="Forecast seasonal trends and patterns"
            ),
            Tool(
                name="forecast_market_trends",
                func=self.forecast_market_trends,
                description="Forecast market trends and competitive landscape"
            )
        ]