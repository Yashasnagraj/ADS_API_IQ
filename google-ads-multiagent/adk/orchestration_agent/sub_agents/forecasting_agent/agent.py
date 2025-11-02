"""
Forecasting Agent for Google Ads Multi-Agent System with ML Integration
"""
from typing import Dict, Any, List, Optional
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_agent.warehouse_client import WarehouseClient


class ForecastingAgent:
    """
    Agent responsible for performance forecasting and predictive analytics
    """

    def __init__(self, data_agent=None):
        """
        Initialize Forecasting Agent

        Args:
            data_agent: DataAgent instance for fetching data
        """
        self.data_agent = data_agent
        self.name = "ForecastingAgent"
        self.warehouse_client = WarehouseClient()

        # ML models cache
        self.models = {}

        # Forecast confidence levels
        self.confidence_levels = {
            'high': 0.95,
            'medium': 0.85,
            'low': 0.70
        }

    def predict_ctr(
        self,
        customer_id: str = None,
        forecast_days: int = 7,
        use_ml: bool = True
    ) -> Dict[str, Any]:
        """
        Predict CTR for campaigns using ML models

        Args:
            customer_id: Customer ID
            forecast_days: Number of days to forecast
            use_ml: Whether to use ML models

        Returns:
            CTR predictions
        """
        try:
            # Validate customer_id
            if not customer_id:
                return {
                    'status': 'error',
                    'message': 'customer_id is required for CTR prediction'
                }

            # Note: WarehouseClient doesn't have fetch_ml_features yet
            # Fall back to campaign-based forecasting
            campaigns_data = self.warehouse_client.fetch_campaigns(customer_id=int(customer_id))

            if "error" in campaigns_data:
                return {
                    'status': 'error',
                    'message': 'Failed to fetch data for CTR prediction'
                }

            campaigns = pd.DataFrame(campaigns_data.get('campaigns', []))

            if campaigns.empty:
                return {
                    'status': 'success',
                    'predictions': [],
                    'message': 'No campaigns found for this customer'
                }

            # Simple moving average prediction
            predictions = []
            for _, campaign in campaigns.iterrows():
                current_ctr = campaign.get('ctr', 0)

                # Simple trend estimation
                if current_ctr > 2.5:
                    trend = -0.05  # Likely to decrease
                elif current_ctr < 1.0:
                    trend = 0.05  # Likely to increase
                else:
                    trend = 0  # Stable

                predicted_ctr = current_ctr + (trend * forecast_days)
                predicted_ctr = max(0.1, min(10.0, predicted_ctr))  # Bound between 0.1% and 10%

                predictions.append({
                    'campaign': campaign['name'],
                    'current_ctr': round(current_ctr, 2),
                    'predicted_ctr': round(predicted_ctr, 2),
                    'change_percent': round(trend * forecast_days / current_ctr * 100, 1) if current_ctr > 0 else 0,
                    'confidence': 'medium',
                    'method': 'simple_trend'
                })

            # Note: ML-based predictions will be enabled when ml_features table is populated
            # For now, using statistical trend forecasting

            return {
                'status': 'success',
                'predictions': predictions,
                'forecast_period': f'{forecast_days} days',
                'method': 'statistical',
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error predicting CTR: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'predictions': []
            }

    def forecast_spend(
        self,
        customer_id: str = None,
        forecast_days: int = 30,
        include_seasonality: bool = True
    ) -> Dict[str, Any]:
        """
        Forecast advertising spend using historical data and ML

        Args:
            customer_id: Customer ID
            forecast_days: Number of days to forecast
            include_seasonality: Whether to include seasonal adjustments

        Returns:
            Spend forecast
        """
        try:
            # Validate customer_id
            if not customer_id:
                return {
                    'status': 'error',
                    'message': 'customer_id is required for spend forecasting'
                }

            # Fetch campaign performance data for specific customer
            campaigns_data = self.warehouse_client.fetch_campaigns(customer_id=int(customer_id))

            if "error" in campaigns_data:
                return {
                    'status': 'error',
                    'message': 'Failed to fetch campaign data'
                }

            campaigns = pd.DataFrame(campaigns_data.get('campaigns', []))

            if campaigns.empty:
                return {
                    'status': 'success',
                    'forecast': {},
                    'message': 'No campaigns found for this customer'
                }

            # Calculate current spend metrics
            total_current_spend = campaigns['cost'].sum()
            daily_spend = total_current_spend / 30  # Assuming 30-day data

            # Campaign-level forecasts
            campaign_forecasts = []

            for _, campaign in campaigns.iterrows():
                current_spend = campaign['cost']
                current_budget = campaign.get('budget', current_spend * 1.2)

                # Calculate spend velocity
                spend_velocity = current_spend / 30  # Daily spend rate

                # Apply growth/decline factors
                if campaign['roas'] > 4:
                    growth_factor = 1.1  # Increase spend for high ROAS
                elif campaign['roas'] < 2:
                    growth_factor = 0.9  # Decrease spend for low ROAS
                else:
                    growth_factor = 1.0  # Maintain

                # Seasonality adjustment
                if include_seasonality:
                    # Simple seasonality model (higher spend on weekdays)
                    weekday_factor = 1.1
                    weekend_factor = 0.9
                    avg_seasonality = (weekday_factor * 5 + weekend_factor * 2) / 7
                    growth_factor *= avg_seasonality

                # Calculate forecasted spend
                forecasted_spend = spend_velocity * forecast_days * growth_factor

                # Cap at budget
                max_spend = min(forecasted_spend, current_budget * (forecast_days / 30))

                campaign_forecasts.append({
                    'campaign': campaign['name'],
                    'current_monthly_spend': round(current_spend, 2),
                    'forecasted_spend': round(max_spend, 2),
                    'daily_spend_rate': round(spend_velocity * growth_factor, 2),
                    'growth_factor': round(growth_factor, 2),
                    'budget_utilization': round(max_spend / (current_budget * forecast_days / 30) * 100, 1) if current_budget > 0 else 0,
                    'confidence': self._calculate_spend_confidence(campaign)
                })

            # Overall forecast
            total_forecasted = sum(cf['forecasted_spend'] for cf in campaign_forecasts)

            # Calculate confidence intervals
            confidence_interval_low = total_forecasted * 0.85
            confidence_interval_high = total_forecasted * 1.15

            # Weekly breakdown
            weekly_forecast = []
            weeks = forecast_days // 7
            for week in range(weeks):
                week_spend = total_forecasted / weeks
                if include_seasonality:
                    # Add some variation
                    week_spend *= np.random.uniform(0.9, 1.1)

                weekly_forecast.append({
                    'week': week + 1,
                    'forecasted_spend': round(week_spend, 2),
                    'cumulative_spend': round(sum(wf['forecasted_spend'] for wf in weekly_forecast[:week+1]), 2) if weekly_forecast else round(week_spend, 2)
                })

            forecast_summary = {
                'forecast_period': f'{forecast_days} days',
                'current_monthly_spend': round(total_current_spend, 2),
                'forecasted_total_spend': round(total_forecasted, 2),
                'daily_average_forecast': round(total_forecasted / forecast_days, 2),
                'confidence_interval': {
                    'low': round(confidence_interval_low, 2),
                    'high': round(confidence_interval_high, 2)
                },
                'spend_change_percent': round((total_forecasted - total_current_spend) / total_current_spend * 100, 1) if total_current_spend > 0 else 0,
                'weekly_breakdown': weekly_forecast,
                'campaign_forecasts': campaign_forecasts,
                'seasonality_applied': include_seasonality
            }

            return {
                'status': 'success',
                'forecast': forecast_summary,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error forecasting spend: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'forecast': {}
            }

    def predict_conversions(
        self,
        customer_id: str = None,
        forecast_days: int = 7,
        scenario: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Predict future conversions based on current performance

        Args:
            customer_id: Customer ID
            forecast_days: Number of days to forecast
            scenario: Optional scenario parameters (budget changes, bid adjustments)

        Returns:
            Conversion predictions
        """
        try:
            # Validate customer_id
            if not customer_id:
                return {
                    'status': 'error',
                    'message': 'customer_id is required for conversion prediction'
                }

            # Fetch campaign data for specific customer
            campaigns_data = self.warehouse_client.fetch_campaigns(customer_id=int(customer_id))

            if "error" in campaigns_data:
                return {
                    'status': 'error',
                    'message': 'Failed to fetch campaign data'
                }

            campaigns = pd.DataFrame(campaigns_data.get('campaigns', []))

            if campaigns.empty:
                return {
                    'status': 'success',
                    'predictions': [],
                    'message': 'No campaigns found for this customer'
                }

            # Apply scenario adjustments if provided
            if scenario:
                if 'budget_multiplier' in scenario:
                    campaigns['budget'] *= scenario['budget_multiplier']
                if 'bid_multiplier' in scenario:
                    campaigns['max_cpc'] = campaigns.get('max_cpc', 2.0) * scenario['bid_multiplier']

            predictions = []

            for _, campaign in campaigns.iterrows():
                current_conversions = campaign['conversions']
                conversion_rate = campaign.get('conversion_rate', 0)
                clicks = campaign.get('clicks', 0)

                # Estimate daily conversion rate
                daily_conversions = current_conversions / 30

                # Apply trend factors
                if conversion_rate > 5:
                    trend_factor = 1.05  # High performers likely to continue
                elif conversion_rate < 1:
                    trend_factor = 0.95  # Low performers may decline
                else:
                    trend_factor = 1.0

                # Scenario adjustments impact
                if scenario:
                    if 'budget_multiplier' in scenario:
                        # More budget = more clicks = more conversions
                        trend_factor *= scenario['budget_multiplier'] ** 0.5  # Square root for diminishing returns
                    if 'bid_multiplier' in scenario:
                        # Higher bids = better position = higher conversion rate
                        trend_factor *= 1 + (scenario['bid_multiplier'] - 1) * 0.3  # 30% impact

                predicted_conversions = daily_conversions * forecast_days * trend_factor

                # Calculate confidence based on data volume
                if clicks > 1000:
                    confidence = 'high'
                elif clicks > 100:
                    confidence = 'medium'
                else:
                    confidence = 'low'

                predictions.append({
                    'campaign': campaign['name'],
                    'current_conversions': int(current_conversions),
                    'predicted_conversions': int(predicted_conversions),
                    'daily_forecast': round(predicted_conversions / forecast_days, 1),
                    'conversion_rate': round(conversion_rate, 2),
                    'trend_factor': round(trend_factor, 2),
                    'confidence': confidence
                })

            # Calculate totals
            total_current = sum(p['current_conversions'] for p in predictions)
            total_predicted = sum(p['predicted_conversions'] for p in predictions)

            return {
                'status': 'success',
                'predictions': predictions,
                'summary': {
                    'total_current_conversions': total_current,
                    'total_predicted_conversions': total_predicted,
                    'change_percent': round((total_predicted - total_current) / total_current * 100, 1) if total_current > 0 else 0,
                    'forecast_period': f'{forecast_days} days',
                    'scenario_applied': scenario is not None
                },
                'scenario': scenario or {},
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error predicting conversions: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'predictions': []
            }

    def analyze_scenarios(
        self,
        customer_id: str = None,
        scenarios: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple what-if scenarios

        Args:
            customer_id: Customer ID
            scenarios: List of scenario configurations

        Returns:
            Scenario analysis results
        """
        try:
            # Validate customer_id
            if not customer_id:
                return {
                    'status': 'error',
                    'message': 'customer_id is required for scenario analysis'
                }

            # Default scenarios if none provided
            if not scenarios:
                scenarios = [
                    {
                        'name': 'Baseline',
                        'budget_multiplier': 1.0,
                        'bid_multiplier': 1.0
                    },
                    {
                        'name': 'Aggressive Growth',
                        'budget_multiplier': 1.5,
                        'bid_multiplier': 1.2
                    },
                    {
                        'name': 'Conservative',
                        'budget_multiplier': 0.8,
                        'bid_multiplier': 0.9
                    },
                    {
                        'name': 'High Efficiency',
                        'budget_multiplier': 1.0,
                        'bid_multiplier': 0.8
                    }
                ]

            scenario_results = []

            for scenario in scenarios:
                # Predict conversions for each scenario
                conversion_result = self.predict_conversions(
                    customer_id=customer_id,
                    forecast_days=30,
                    scenario=scenario
                )

                # Forecast spend for each scenario
                spend_result = self.forecast_spend(
                    customer_id=customer_id,
                    forecast_days=30
                )

                if conversion_result['status'] == 'success' and spend_result['status'] == 'success':
                    total_conversions = conversion_result['summary']['total_predicted_conversions']
                    total_spend = spend_result['forecast']['forecasted_total_spend']

                    # Apply scenario multipliers to spend
                    adjusted_spend = total_spend * scenario.get('budget_multiplier', 1.0)

                    # Calculate metrics
                    cpa = adjusted_spend / total_conversions if total_conversions > 0 else 0
                    roas = (total_conversions * 50) / adjusted_spend if adjusted_spend > 0 else 0  # Assume $50 per conversion

                    scenario_results.append({
                        'scenario_name': scenario['name'],
                        'parameters': scenario,
                        'predicted_conversions': total_conversions,
                        'predicted_spend': round(adjusted_spend, 2),
                        'predicted_cpa': round(cpa, 2),
                        'predicted_roas': round(roas, 2),
                        'efficiency_score': round(roas * 10 + (100 / (cpa + 1)), 2),  # Combined efficiency metric
                        'risk_level': self._assess_risk(scenario)
                    })

            # Rank scenarios by efficiency
            scenario_results = sorted(scenario_results, key=lambda x: x['efficiency_score'], reverse=True)

            # Find optimal scenario
            optimal_scenario = scenario_results[0] if scenario_results else None

            return {
                'status': 'success',
                'scenario_results': scenario_results,
                'optimal_scenario': optimal_scenario,
                'recommendation': self._generate_scenario_recommendation(scenario_results),
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing scenarios: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'scenario_results': []
            }

    def _train_ctr_model(self, features_df: pd.DataFrame):
        """
        Train ML model for CTR prediction

        Args:
            features_df: DataFrame with features
        """
        try:
            # Prepare features and target
            feature_cols = [col for col in features_df.columns if col not in ['campaign_id', 'campaign_name', 'ctr']]
            X = features_df[feature_cols].fillna(0)
            y = features_df['ctr'].fillna(0)

            # Train Random Forest model
            model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
            model.fit(X, y)

            # Store model
            self.models['ctr_model'] = model

            # Calculate accuracy (simplified)
            predictions = model.predict(X)
            mse = np.mean((predictions - y) ** 2)
            self.models['ctr_model_accuracy'] = round(1 - mse / np.var(y), 2) if np.var(y) > 0 else 0

            logger.info(f"CTR model trained with accuracy: {self.models['ctr_model_accuracy']}")

        except Exception as e:
            logger.error(f"Error training CTR model: {str(e)}")
            self.models['ctr_model'] = None

    def _statistical_ctr_forecast(self, features_df: pd.DataFrame, forecast_days: int) -> List[Dict]:
        """
        Statistical CTR forecast without ML

        Args:
            features_df: Features DataFrame
            forecast_days: Days to forecast

        Returns:
            List of predictions
        """
        predictions = []

        for _, row in features_df.iterrows():
            current_ctr = row.get('ctr', 0)

            # Simple linear trend
            impressions = row.get('impressions_sum', 0)
            clicks = row.get('clicks_sum', 0)

            if impressions > 1000:
                # Calculate trend based on volume
                if clicks / impressions > 0.025:  # High CTR
                    trend = -0.002  # Likely to regress
                elif clicks / impressions < 0.01:  # Low CTR
                    trend = 0.001  # Room for improvement
                else:
                    trend = 0

                predicted_ctr = current_ctr + (trend * forecast_days)
                predicted_ctr = max(0.1, min(10.0, predicted_ctr))

                predictions.append({
                    'campaign': row.get('campaign_name', f'Campaign_{row.get("campaign_id")}'),
                    'current_ctr': round(current_ctr, 2),
                    'predicted_ctr': round(predicted_ctr, 2),
                    'change_percent': round((predicted_ctr - current_ctr) / current_ctr * 100, 1) if current_ctr > 0 else 0,
                    'confidence': 'medium',
                    'method': 'statistical_trend'
                })

        return predictions

    def _calculate_confidence(self, row: pd.Series, metric: str) -> str:
        """
        Calculate confidence level for predictions

        Args:
            row: Data row
            metric: Metric being predicted

        Returns:
            Confidence level (high/medium/low)
        """
        impressions = row.get('impressions_sum', 0)
        clicks = row.get('clicks_sum', 0)

        if impressions > 10000 and clicks > 100:
            return 'high'
        elif impressions > 1000 and clicks > 10:
            return 'medium'
        else:
            return 'low'

    def _calculate_spend_confidence(self, campaign: pd.Series) -> str:
        """
        Calculate confidence for spend forecasts

        Args:
            campaign: Campaign data

        Returns:
            Confidence level
        """
        spend = campaign.get('cost', 0)
        clicks = campaign.get('clicks', 0)

        if spend > 1000 and clicks > 500:
            return 'high'
        elif spend > 100 and clicks > 50:
            return 'medium'
        else:
            return 'low'

    def _assess_risk(self, scenario: Dict) -> str:
        """
        Assess risk level of a scenario

        Args:
            scenario: Scenario parameters

        Returns:
            Risk level (low/medium/high)
        """
        budget_mult = scenario.get('budget_multiplier', 1.0)
        bid_mult = scenario.get('bid_multiplier', 1.0)

        total_change = abs(budget_mult - 1.0) + abs(bid_mult - 1.0)

        if total_change > 0.5:
            return 'high'
        elif total_change > 0.2:
            return 'medium'
        else:
            return 'low'

    def _generate_scenario_recommendation(self, scenario_results: List[Dict]) -> str:
        """
        Generate recommendation based on scenario analysis

        Args:
            scenario_results: List of scenario results

        Returns:
            Recommendation text
        """
        if not scenario_results:
            return "No scenarios analyzed"

        optimal = scenario_results[0]

        if optimal['risk_level'] == 'low' and optimal['predicted_roas'] > 4:
            return f"Recommend implementing '{optimal['scenario_name']}' scenario for optimal performance with low risk"
        elif optimal['risk_level'] == 'high' and optimal['predicted_roas'] > 5:
            return f"'{optimal['scenario_name']}' offers best returns but with high risk - consider gradual implementation"
        else:
            # Find balanced option
            balanced = next((s for s in scenario_results if s['risk_level'] == 'medium'), optimal)
            return f"Recommend balanced approach with '{balanced['scenario_name']}' scenario"