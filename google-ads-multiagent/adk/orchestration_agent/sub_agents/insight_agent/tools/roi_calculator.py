"""
ROI calculation tools for Insight Agent
"""
from typing import Dict, List, Any, Optional, Tuple
from langchain.tools import Tool
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class ROICalculator:
    """Calculates ROI, ROAS, and other financial metrics for Google Ads"""

    def __init__(self):
        logger.info("ROI Calculator initialized")

    def calculate_campaign_roi(
        self,
        campaign_data: List[Dict[str, Any]],
        attribution_model: str = 'last_click',
        include_lifetime_value: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate ROI metrics for campaigns

        Args:
            campaign_data: Campaign performance data
            attribution_model: Attribution model to use
            include_lifetime_value: Include LTV in calculations

        Returns:
            ROI analysis with profitability metrics
        """
        try:
            if not campaign_data:
                return {"error": "No campaign data provided"}

            df = pd.DataFrame(campaign_data)

            analysis = {
                'overall_metrics': {},
                'campaign_roi': [],
                'profitability_analysis': {},
                'attribution_impact': {},
                'recommendations': []
            }

            # Calculate overall metrics
            total_cost = df['cost'].sum() if 'cost' in df.columns else 0
            total_revenue = df['conversion_value'].sum() if 'conversion_value' in df.columns else 0
            total_conversions = df['conversions'].sum() if 'conversions' in df.columns else 0

            # Core ROI metrics
            roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
            roas = (total_revenue / total_cost) if total_cost > 0 else 0
            profit = total_revenue - total_cost
            profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else 0

            analysis['overall_metrics'] = {
                'total_spend': round(total_cost, 2),
                'total_revenue': round(total_revenue, 2),
                'total_profit': round(profit, 2),
                'roi_percentage': round(roi, 2),
                'roas': round(roas, 2),
                'profit_margin': round(profit_margin, 2),
                'average_order_value': round(total_revenue / total_conversions, 2) if total_conversions > 0 else 0,
                'cost_per_conversion': round(total_cost / total_conversions, 2) if total_conversions > 0 else 0
            }

            # Calculate ROI for each campaign
            for _, campaign in df.iterrows():
                campaign_cost = campaign.get('cost', 0)
                campaign_revenue = campaign.get('conversion_value', 0)
                campaign_conversions = campaign.get('conversions', 0)

                if campaign_cost > 0:
                    campaign_roi = ((campaign_revenue - campaign_cost) / campaign_cost * 100)
                    campaign_roas = campaign_revenue / campaign_cost
                else:
                    campaign_roi = 0
                    campaign_roas = 0

                campaign_analysis = {
                    'campaign_id': campaign.get('campaign_id'),
                    'campaign_name': campaign.get('campaign_name', 'Unknown'),
                    'cost': round(campaign_cost, 2),
                    'revenue': round(campaign_revenue, 2),
                    'profit': round(campaign_revenue - campaign_cost, 2),
                    'roi': round(campaign_roi, 2),
                    'roas': round(campaign_roas, 2),
                    'conversions': campaign_conversions,
                    'profitability_status': self._classify_profitability(campaign_roi, campaign_roas),
                    'efficiency_score': self._calculate_efficiency_score(campaign_roi, campaign_roas, campaign_conversions)
                }

                # Add lifetime value if requested
                if include_lifetime_value:
                    ltv = self._estimate_lifetime_value(campaign)
                    campaign_analysis['estimated_ltv'] = ltv
                    campaign_analysis['ltv_roi'] = ((ltv - campaign_cost) / campaign_cost * 100) if campaign_cost > 0 else 0

                analysis['campaign_roi'].append(campaign_analysis)

            # Sort campaigns by ROI
            analysis['campaign_roi'] = sorted(
                analysis['campaign_roi'],
                key=lambda x: x['roi'],
                reverse=True
            )

            # Profitability analysis
            analysis['profitability_analysis'] = self._analyze_profitability(analysis['campaign_roi'])

            # Attribution model impact
            if attribution_model != 'last_click':
                analysis['attribution_impact'] = self._calculate_attribution_impact(
                    df,
                    attribution_model
                )

            # Break-even analysis
            analysis['break_even_analysis'] = self._calculate_break_even(df)

            # Generate recommendations
            analysis['recommendations'] = self._generate_roi_recommendations(analysis)

            # Investment optimization
            analysis['investment_optimization'] = self._optimize_investment_allocation(
                analysis['campaign_roi'],
                total_cost
            )

            return analysis

        except Exception as e:
            logger.error(f"Error calculating campaign ROI: {e}")
            return {"error": str(e)}

    def calculate_keyword_profitability(
        self,
        keyword_data: List[Dict[str, Any]],
        cost_adjustments: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate profitability metrics for keywords

        Args:
            keyword_data: Keyword performance data
            cost_adjustments: Additional costs to factor in

        Returns:
            Keyword profitability analysis
        """
        try:
            if not keyword_data:
                return {"error": "No keyword data provided"}

            df = pd.DataFrame(keyword_data)

            analysis = {
                'profitable_keywords': [],
                'unprofitable_keywords': [],
                'marginal_keywords': [],
                'keyword_value_analysis': {},
                'optimization_opportunities': []
            }

            # Apply cost adjustments if provided
            if cost_adjustments:
                for adjustment_type, percentage in cost_adjustments.items():
                    df['cost'] = df['cost'] * (1 + percentage / 100)

            # Analyze each keyword
            for _, keyword in df.iterrows():
                keyword_text = keyword.get('keyword_text', 'unknown')
                cost = keyword.get('cost', 0)
                revenue = keyword.get('conversion_value', 0)
                conversions = keyword.get('conversions', 0)
                clicks = keyword.get('clicks', 0)

                # Calculate profitability metrics
                profit = revenue - cost
                roi = ((revenue - cost) / cost * 100) if cost > 0 else 0
                roas = (revenue / cost) if cost > 0 else 0
                value_per_click = (revenue / clicks) if clicks > 0 else 0
                profit_per_conversion = (profit / conversions) if conversions > 0 else 0

                keyword_analysis = {
                    'keyword': keyword_text,
                    'cost': round(cost, 2),
                    'revenue': round(revenue, 2),
                    'profit': round(profit, 2),
                    'roi': round(roi, 2),
                    'roas': round(roas, 2),
                    'value_per_click': round(value_per_click, 2),
                    'profit_per_conversion': round(profit_per_conversion, 2),
                    'match_type': keyword.get('match_type', 'unknown'),
                    'quality_score': keyword.get('quality_score', 0)
                }

                # Categorize keywords
                if roi > 50 and roas > 3:
                    analysis['profitable_keywords'].append(keyword_analysis)
                elif roi < 0:
                    analysis['unprofitable_keywords'].append(keyword_analysis)
                else:
                    analysis['marginal_keywords'].append(keyword_analysis)

                # Value analysis
                analysis['keyword_value_analysis'][keyword_text] = {
                    'lifetime_value_potential': self._estimate_keyword_ltv(keyword),
                    'competitive_value': self._calculate_competitive_value(keyword),
                    'strategic_value': self._assess_strategic_value(keyword)
                }

            # Sort by profitability
            analysis['profitable_keywords'] = sorted(
                analysis['profitable_keywords'],
                key=lambda x: x['roi'],
                reverse=True
            )[:50]  # Top 50

            analysis['unprofitable_keywords'] = sorted(
                analysis['unprofitable_keywords'],
                key=lambda x: x['roi']
            )[:50]  # Bottom 50

            # Identify optimization opportunities
            analysis['optimization_opportunities'] = self._identify_keyword_opportunities(
                analysis
            )

            # Summary statistics
            analysis['summary'] = {
                'total_keywords': len(df),
                'profitable_count': len(analysis['profitable_keywords']),
                'unprofitable_count': len(analysis['unprofitable_keywords']),
                'marginal_count': len(analysis['marginal_keywords']),
                'avg_keyword_roi': df['roi'].mean() if 'roi' in df.columns else 0,
                'total_keyword_profit': df['profit'].sum() if 'profit' in df.columns else 0
            }

            return analysis

        except Exception as e:
            logger.error(f"Error calculating keyword profitability: {e}")
            return {"error": str(e)}

    def calculate_customer_value(
        self,
        customer_data: List[Dict[str, Any]],
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """
        Calculate customer lifetime value metrics

        Args:
            customer_data: Customer conversion and value data
            include_predictions: Include CLV predictions

        Returns:
            Customer value analysis
        """
        try:
            if not customer_data:
                return {"error": "No customer data provided"}

            df = pd.DataFrame(customer_data)

            analysis = {
                'clv_metrics': {},
                'customer_segments': {},
                'acquisition_efficiency': {},
                'retention_metrics': {},
                'value_predictions': {}
            }

            # Basic CLV metrics
            avg_purchase_value = df['conversion_value'].mean() if 'conversion_value' in df.columns else 0
            purchase_frequency = df.groupby('customer_id').size().mean() if 'customer_id' in df.columns else 1
            customer_lifespan = self._estimate_customer_lifespan(df)

            # Calculate CLV
            basic_clv = avg_purchase_value * purchase_frequency * customer_lifespan

            analysis['clv_metrics'] = {
                'average_order_value': round(avg_purchase_value, 2),
                'purchase_frequency': round(purchase_frequency, 2),
                'estimated_lifespan_months': round(customer_lifespan, 1),
                'basic_clv': round(basic_clv, 2),
                'clv_to_cac_ratio': self._calculate_clv_to_cac(df, basic_clv)
            }

            # Segment customers by value
            analysis['customer_segments'] = self._segment_customers_by_value(df)

            # Acquisition efficiency
            analysis['acquisition_efficiency'] = self._calculate_acquisition_efficiency(df)

            # Retention metrics
            if 'first_purchase_date' in df.columns and 'last_purchase_date' in df.columns:
                analysis['retention_metrics'] = self._calculate_retention_metrics(df)

            # CLV predictions
            if include_predictions:
                analysis['value_predictions'] = self._predict_customer_values(df)

            # ROI by customer segment
            analysis['segment_roi'] = self._calculate_segment_roi(
                analysis['customer_segments']
            )

            # Recommendations
            analysis['recommendations'] = self._generate_clv_recommendations(analysis)

            return analysis

        except Exception as e:
            logger.error(f"Error calculating customer value: {e}")
            return {"error": str(e)}

    def calculate_budget_efficiency(
        self,
        budget_data: List[Dict[str, Any]],
        targets: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate budget efficiency and optimization opportunities

        Args:
            budget_data: Budget and performance data
            targets: Performance targets

        Returns:
            Budget efficiency analysis
        """
        try:
            if not budget_data:
                return {"error": "No budget data provided"}

            df = pd.DataFrame(budget_data)

            # Default targets if not provided
            if not targets:
                targets = {
                    'target_roas': 3.0,
                    'target_cpa': 50.0,
                    'target_roi': 100.0
                }

            analysis = {
                'efficiency_metrics': {},
                'budget_allocation': {},
                'waste_analysis': {},
                'optimization_potential': {},
                'reallocation_recommendations': []
            }

            # Calculate efficiency metrics
            total_budget = df['budget'].sum() if 'budget' in df.columns else 0
            total_spent = df['cost'].sum() if 'cost' in df.columns else 0
            total_revenue = df['conversion_value'].sum() if 'conversion_value' in df.columns else 0

            utilization_rate = (total_spent / total_budget * 100) if total_budget > 0 else 0
            efficiency_score = self._calculate_budget_efficiency_score(df, targets)

            analysis['efficiency_metrics'] = {
                'total_budget': round(total_budget, 2),
                'total_spent': round(total_spent, 2),
                'utilization_rate': round(utilization_rate, 2),
                'efficiency_score': efficiency_score,
                'cost_per_result': round(total_spent / df['conversions'].sum(), 2) if df['conversions'].sum() > 0 else 0,
                'revenue_per_dollar_spent': round(total_revenue / total_spent, 2) if total_spent > 0 else 0
            }

            # Analyze budget allocation
            analysis['budget_allocation'] = self._analyze_budget_allocation(df)

            # Identify waste
            analysis['waste_analysis'] = self._identify_budget_waste(df, targets)

            # Calculate optimization potential
            analysis['optimization_potential'] = self._calculate_optimization_potential(
                df,
                targets
            )

            # Generate reallocation recommendations
            analysis['reallocation_recommendations'] = self._generate_reallocation_plan(
                df,
                targets
            )

            # Marginal ROI analysis
            analysis['marginal_roi'] = self._calculate_marginal_roi(df)

            return analysis

        except Exception as e:
            logger.error(f"Error calculating budget efficiency: {e}")
            return {"error": str(e)}

    def _classify_profitability(self, roi: float, roas: float) -> str:
        """Classify profitability status"""
        if roi > 100 and roas > 4:
            return 'highly_profitable'
        elif roi > 50 and roas > 3:
            return 'profitable'
        elif roi > 0 and roas > 2:
            return 'marginally_profitable'
        elif roi > -20:
            return 'break_even'
        else:
            return 'unprofitable'

    def _calculate_efficiency_score(
        self,
        roi: float,
        roas: float,
        conversions: int
    ) -> int:
        """Calculate efficiency score (0-100)"""
        score = 0

        # ROI contribution (0-40 points)
        if roi > 200:
            score += 40
        elif roi > 100:
            score += 30
        elif roi > 50:
            score += 20
        elif roi > 0:
            score += 10

        # ROAS contribution (0-40 points)
        if roas > 5:
            score += 40
        elif roas > 3:
            score += 30
        elif roas > 2:
            score += 20
        elif roas > 1:
            score += 10

        # Conversion volume contribution (0-20 points)
        if conversions > 100:
            score += 20
        elif conversions > 50:
            score += 15
        elif conversions > 20:
            score += 10
        elif conversions > 5:
            score += 5

        return min(score, 100)

    def _estimate_lifetime_value(self, campaign: pd.Series) -> float:
        """Estimate lifetime value for campaign conversions"""
        # Simplified LTV estimation
        avg_order_value = campaign.get('conversion_value', 0) / max(campaign.get('conversions', 1), 1)
        retention_rate = 0.4  # Assumed retention rate
        purchase_frequency = 2.5  # Assumed average purchases per year
        customer_lifespan = 2  # Assumed 2 years

        ltv = avg_order_value * purchase_frequency * customer_lifespan * retention_rate
        return round(ltv, 2)

    def _analyze_profitability(
        self,
        campaign_roi: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze profitability distribution"""
        profitable = [c for c in campaign_roi if c['roi'] > 0]
        unprofitable = [c for c in campaign_roi if c['roi'] <= 0]

        total_profit = sum(c['profit'] for c in campaign_roi)
        total_cost = sum(c['cost'] for c in campaign_roi)

        return {
            'profitable_campaigns': len(profitable),
            'unprofitable_campaigns': len(unprofitable),
            'profitability_rate': round(len(profitable) / len(campaign_roi) * 100, 2) if campaign_roi else 0,
            'profit_concentration': self._calculate_profit_concentration(campaign_roi),
            'risk_assessment': self._assess_profitability_risk(profitable, unprofitable),
            'efficiency_ratio': round(total_profit / total_cost, 2) if total_cost > 0 else 0
        }

    def _calculate_attribution_impact(
        self,
        df: pd.DataFrame,
        model: str
    ) -> Dict[str, Any]:
        """Calculate impact of attribution model on ROI"""
        # Simplified attribution impact calculation
        impact = {
            'model': model,
            'estimated_impact': {}
        }

        if model == 'first_click':
            # First-click typically increases top-funnel campaign value
            impact['estimated_impact'] = {
                'awareness_campaigns': '+15-25%',
                'conversion_campaigns': '-10-20%'
            }
        elif model == 'linear':
            # Linear distributes credit evenly
            impact['estimated_impact'] = {
                'all_campaigns': 'More balanced distribution',
                'mid_funnel': '+5-10%'
            }
        elif model == 'time_decay':
            # Time decay favors recent interactions
            impact['estimated_impact'] = {
                'retargeting_campaigns': '+10-20%',
                'awareness_campaigns': '-5-15%'
            }

        return impact

    def _calculate_break_even(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate break-even analysis"""
        total_cost = df['cost'].sum() if 'cost' in df.columns else 0
        total_revenue = df['conversion_value'].sum() if 'conversion_value' in df.columns else 0
        total_conversions = df['conversions'].sum() if 'conversions' in df.columns else 0

        avg_order_value = total_revenue / total_conversions if total_conversions > 0 else 0
        cost_per_conversion = total_cost / total_conversions if total_conversions > 0 else 0

        break_even_roas = 1.0  # ROAS of 1 means break-even
        current_roas = total_revenue / total_cost if total_cost > 0 else 0

        return {
            'break_even_roas': break_even_roas,
            'current_roas': round(current_roas, 2),
            'above_break_even': current_roas > break_even_roas,
            'margin_of_safety': round((current_roas - break_even_roas) / break_even_roas * 100, 2) if break_even_roas > 0 else 0,
            'break_even_cpa': round(avg_order_value, 2),
            'current_cpa': round(cost_per_conversion, 2),
            'conversions_to_break_even': int(total_cost / avg_order_value) if avg_order_value > 0 else 0
        }

    def _generate_roi_recommendations(
        self,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate ROI improvement recommendations"""
        recommendations = []

        # Check overall ROI
        overall_roi = analysis['overall_metrics']['roi_percentage']
        if overall_roi < 50:
            recommendations.append("Overall ROI below 50% - review campaign efficiency")

        # Check unprofitable campaigns
        unprofitable_count = analysis['profitability_analysis']['unprofitable_campaigns']
        if unprofitable_count > 0:
            recommendations.append(f"Pause or optimize {unprofitable_count} unprofitable campaigns")

        # Check profit concentration
        concentration = analysis['profitability_analysis'].get('profit_concentration', {})
        if concentration.get('top_20_percent_contribution', 0) > 80:
            recommendations.append("High profit concentration - diversify successful strategies")

        # Budget efficiency
        if analysis['overall_metrics']['roas'] < 3:
            recommendations.append("ROAS below 3x - improve targeting and ad relevance")

        # Break-even analysis
        break_even = analysis.get('break_even_analysis', {})
        if break_even.get('margin_of_safety', 0) < 20:
            recommendations.append("Low margin of safety - focus on conversion rate optimization")

        return recommendations[:5]

    def _optimize_investment_allocation(
        self,
        campaign_roi: List[Dict[str, Any]],
        total_budget: float
    ) -> Dict[str, Any]:
        """Optimize budget allocation based on ROI"""
        optimization = {
            'current_allocation': {},
            'recommended_allocation': {},
            'expected_improvement': {}
        }

        # Calculate current allocation
        for campaign in campaign_roi:
            optimization['current_allocation'][campaign['campaign_name']] = {
                'budget': campaign['cost'],
                'roi': campaign['roi']
            }

        # Recommend reallocation based on efficiency
        total_efficiency_score = sum(c['efficiency_score'] for c in campaign_roi)

        for campaign in campaign_roi:
            if total_efficiency_score > 0:
                # Allocate proportionally to efficiency score
                recommended_budget = (campaign['efficiency_score'] / total_efficiency_score) * total_budget
            else:
                recommended_budget = total_budget / len(campaign_roi)

            optimization['recommended_allocation'][campaign['campaign_name']] = {
                'budget': round(recommended_budget, 2),
                'change': round(recommended_budget - campaign['cost'], 2)
            }

        # Estimate improvement
        current_weighted_roi = sum(
            c['roi'] * (c['cost'] / total_budget)
            for c in campaign_roi
            if total_budget > 0
        )

        estimated_weighted_roi = sum(
            c['roi'] * (optimization['recommended_allocation'][c['campaign_name']]['budget'] / total_budget)
            for c in campaign_roi
            if total_budget > 0
        )

        optimization['expected_improvement'] = {
            'current_weighted_roi': round(current_weighted_roi, 2),
            'estimated_weighted_roi': round(estimated_weighted_roi, 2),
            'improvement_percentage': round((estimated_weighted_roi - current_weighted_roi), 2)
        }

        return optimization

    def _calculate_profit_concentration(
        self,
        campaign_roi: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate profit concentration (Pareto analysis)"""
        if not campaign_roi:
            return {}

        sorted_campaigns = sorted(campaign_roi, key=lambda x: x['profit'], reverse=True)
        total_profit = sum(c['profit'] for c in sorted_campaigns)

        if total_profit <= 0:
            return {'concentrated': False}

        # Calculate cumulative profit percentages
        cumulative_profit = 0
        top_20_percent_count = max(1, len(sorted_campaigns) // 5)

        for i, campaign in enumerate(sorted_campaigns[:top_20_percent_count]):
            cumulative_profit += campaign['profit']

        top_20_contribution = (cumulative_profit / total_profit * 100) if total_profit > 0 else 0

        return {
            'top_20_percent_contribution': round(top_20_contribution, 2),
            'concentrated': top_20_contribution > 80,
            'pareto_efficient': top_20_contribution >= 70 and top_20_contribution <= 85
        }

    def _assess_profitability_risk(
        self,
        profitable: List[Dict],
        unprofitable: List[Dict]
    ) -> str:
        """Assess profitability risk level"""
        if not profitable:
            return 'critical'

        profitability_rate = len(profitable) / (len(profitable) + len(unprofitable))

        if profitability_rate < 0.3:
            return 'high'
        elif profitability_rate < 0.5:
            return 'moderate'
        elif profitability_rate < 0.7:
            return 'low'
        else:
            return 'minimal'

    def _estimate_keyword_ltv(self, keyword: pd.Series) -> float:
        """Estimate lifetime value for keyword"""
        conversion_value = keyword.get('conversion_value', 0)
        conversions = keyword.get('conversions', 1)

        if conversions > 0:
            avg_value = conversion_value / conversions
            # Simple multiplier based on keyword quality
            quality_score = keyword.get('quality_score', 5)
            ltv_multiplier = 1 + (quality_score / 10)
            return round(avg_value * ltv_multiplier * 2.5, 2)  # 2.5 average purchases

        return 0

    def _calculate_competitive_value(self, keyword: pd.Series) -> str:
        """Calculate competitive value of keyword"""
        competition = keyword.get('competition', 'MEDIUM')
        impression_share = keyword.get('search_impression_share', 0)

        if competition == 'HIGH' and impression_share > 0.5:
            return 'high_strategic_value'
        elif competition == 'LOW' and impression_share > 0.7:
            return 'dominant_position'
        else:
            return 'standard_value'

    def _assess_strategic_value(self, keyword: pd.Series) -> str:
        """Assess strategic value of keyword"""
        # Brand keywords
        if keyword.get('is_brand_keyword', False):
            return 'brand_protection'

        # High converting keywords
        conversion_rate = keyword.get('conversion_rate', 0)
        if conversion_rate > 10:
            return 'high_conversion_driver'

        # Volume drivers
        impressions = keyword.get('impressions', 0)
        if impressions > 10000:
            return 'volume_driver'

        return 'standard'

    def _identify_keyword_opportunities(
        self,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify keyword optimization opportunities"""
        opportunities = []

        # Marginal keywords that could be profitable
        for keyword in analysis['marginal_keywords'][:10]:
            if keyword['quality_score'] < 7:
                opportunities.append({
                    'keyword': keyword['keyword'],
                    'action': 'improve_quality_score',
                    'potential_roi_increase': '10-30%',
                    'current_roi': keyword['roi']
                })

        # High-cost keywords with low conversion
        for keyword in analysis['unprofitable_keywords'][:5]:
            if keyword['cost'] > 100:
                opportunities.append({
                    'keyword': keyword['keyword'],
                    'action': 'pause_or_reduce_bid',
                    'potential_savings': keyword['cost'],
                    'current_loss': abs(keyword['profit'])
                })

        return opportunities

    def _estimate_customer_lifespan(self, df: pd.DataFrame) -> float:
        """Estimate average customer lifespan in months"""
        # Simplified estimation
        if 'customer_retention_rate' in df.columns:
            retention_rate = df['customer_retention_rate'].mean()
            if retention_rate > 0 and retention_rate < 1:
                return 1 / (1 - retention_rate)

        return 12  # Default 12 months

    def _calculate_clv_to_cac(self, df: pd.DataFrame, clv: float) -> float:
        """Calculate CLV to CAC ratio"""
        if 'cost' in df.columns and 'conversions' in df.columns:
            total_cost = df['cost'].sum()
            total_conversions = df['conversions'].sum()

            if total_conversions > 0:
                cac = total_cost / total_conversions
                if cac > 0:
                    return round(clv / cac, 2)

        return 0

    def _segment_customers_by_value(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Segment customers by value tiers"""
        if 'conversion_value' not in df.columns:
            return {}

        values = df['conversion_value'].values
        quartiles = np.percentile(values, [25, 50, 75])

        return {
            'high_value': {
                'threshold': round(quartiles[2], 2),
                'count': len(values[values > quartiles[2]]),
                'avg_value': round(values[values > quartiles[2]].mean(), 2) if any(values > quartiles[2]) else 0
            },
            'medium_value': {
                'threshold': round(quartiles[0], 2),
                'count': len(values[(values > quartiles[0]) & (values <= quartiles[2])]),
                'avg_value': round(values[(values > quartiles[0]) & (values <= quartiles[2])].mean(), 2) if any((values > quartiles[0]) & (values <= quartiles[2])) else 0
            },
            'low_value': {
                'threshold': 0,
                'count': len(values[values <= quartiles[0]]),
                'avg_value': round(values[values <= quartiles[0]].mean(), 2) if any(values <= quartiles[0]) else 0
            }
        }

    def _calculate_acquisition_efficiency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate customer acquisition efficiency"""
        if 'cost' not in df.columns or 'conversions' not in df.columns:
            return {}

        total_cost = df['cost'].sum()
        total_conversions = df['conversions'].sum()
        total_value = df['conversion_value'].sum() if 'conversion_value' in df.columns else 0

        cac = total_cost / total_conversions if total_conversions > 0 else 0
        payback_period = cac / (total_value / total_conversions) if total_conversions > 0 and total_value > 0 else 0

        return {
            'customer_acquisition_cost': round(cac, 2),
            'payback_period_months': round(payback_period * 12, 1),
            'acquisition_efficiency_score': self._score_acquisition_efficiency(cac, payback_period)
        }

    def _calculate_retention_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate retention metrics"""
        # Simplified retention calculation
        df['first_purchase_date'] = pd.to_datetime(df['first_purchase_date'])
        df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'])

        active_customers = len(df[df['last_purchase_date'] > df['first_purchase_date']])
        total_customers = len(df)

        retention_rate = (active_customers / total_customers * 100) if total_customers > 0 else 0

        return {
            'retention_rate': round(retention_rate, 2),
            'churn_rate': round(100 - retention_rate, 2),
            'avg_customer_lifespan_days': round(
                (df['last_purchase_date'] - df['first_purchase_date']).dt.days.mean(),
                1
            )
        }

    def _predict_customer_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Predict future customer values"""
        # Simplified prediction
        current_avg_value = df['conversion_value'].mean() if 'conversion_value' in df.columns else 0
        growth_rate = 0.1  # Assumed 10% growth

        return {
            '3_month_prediction': round(current_avg_value * (1 + growth_rate * 0.25), 2),
            '6_month_prediction': round(current_avg_value * (1 + growth_rate * 0.5), 2),
            '12_month_prediction': round(current_avg_value * (1 + growth_rate), 2)
        }

    def _calculate_segment_roi(
        self,
        segments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate ROI by customer segment"""
        segment_roi = {}

        for segment_name, segment_data in segments.items():
            if 'avg_value' in segment_data and segment_data['avg_value'] > 0:
                # Simplified ROI calculation per segment
                segment_roi[segment_name] = {
                    'estimated_roi': round(segment_data['avg_value'] * 2.5 - 50, 2),  # Simplified
                    'segment_size': segment_data['count']
                }

        return segment_roi

    def _generate_clv_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate CLV improvement recommendations"""
        recommendations = []

        clv_to_cac = analysis['clv_metrics'].get('clv_to_cac_ratio', 0)

        if clv_to_cac < 3:
            recommendations.append("CLV:CAC ratio below 3:1 - focus on retention or reduce acquisition costs")

        if analysis['retention_metrics'].get('retention_rate', 0) < 40:
            recommendations.append("Low retention rate - implement retention marketing strategies")

        high_value_segment = analysis['customer_segments'].get('high_value', {})
        if high_value_segment.get('count', 0) < 20:
            recommendations.append("Small high-value segment - identify and target similar prospects")

        return recommendations[:5]

    def _calculate_budget_efficiency_score(
        self,
        df: pd.DataFrame,
        targets: Dict[str, float]
    ) -> int:
        """Calculate budget efficiency score"""
        score = 50  # Start at neutral

        # Check ROAS against target
        if 'conversion_value' in df.columns and 'cost' in df.columns:
            actual_roas = df['conversion_value'].sum() / df['cost'].sum() if df['cost'].sum() > 0 else 0
            roas_performance = (actual_roas / targets['target_roas']) * 100 if targets['target_roas'] > 0 else 0

            if roas_performance > 150:
                score += 30
            elif roas_performance > 100:
                score += 20
            elif roas_performance > 80:
                score += 10
            else:
                score -= 10

        # Check CPA against target
        if 'conversions' in df.columns:
            actual_cpa = df['cost'].sum() / df['conversions'].sum() if df['conversions'].sum() > 0 else 999
            cpa_performance = (targets['target_cpa'] / actual_cpa) * 100 if actual_cpa > 0 else 0

            if cpa_performance > 120:
                score += 20
            elif cpa_performance > 100:
                score += 10
            elif cpa_performance > 80:
                score += 5
            else:
                score -= 10

        return max(0, min(100, score))

    def _analyze_budget_allocation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze how budget is allocated"""
        if 'budget' not in df.columns:
            return {}

        total_budget = df['budget'].sum()

        allocation = {
            'by_campaign_type': {},
            'concentration': {},
            'efficiency_by_allocation': {}
        }

        # Group by campaign type if available
        if 'campaign_type' in df.columns:
            for campaign_type in df['campaign_type'].unique():
                type_data = df[df['campaign_type'] == campaign_type]
                allocation['by_campaign_type'][campaign_type] = {
                    'budget': round(type_data['budget'].sum(), 2),
                    'percentage': round(type_data['budget'].sum() / total_budget * 100, 2),
                    'roas': round(
                        type_data['conversion_value'].sum() / type_data['cost'].sum(),
                        2
                    ) if type_data['cost'].sum() > 0 else 0
                }

        # Calculate concentration
        sorted_budgets = df.sort_values('budget', ascending=False)['budget'].values
        top_20_percent = int(len(sorted_budgets) * 0.2) or 1
        top_20_budget = sorted_budgets[:top_20_percent].sum()

        allocation['concentration'] = {
            'top_20_percent_budget_share': round(top_20_budget / total_budget * 100, 2)
        }

        return allocation

    def _identify_budget_waste(
        self,
        df: pd.DataFrame,
        targets: Dict[str, float]
    ) -> Dict[str, Any]:
        """Identify wasted budget"""
        waste = {
            'total_waste': 0,
            'waste_categories': [],
            'campaigns_with_waste': []
        }

        for _, row in df.iterrows():
            campaign_waste = 0
            waste_reasons = []

            # No conversions
            if row.get('conversions', 0) == 0 and row.get('cost', 0) > 50:
                campaign_waste += row['cost']
                waste_reasons.append('No conversions')

            # High CPA
            if row.get('conversions', 0) > 0:
                cpa = row['cost'] / row['conversions']
                if cpa > targets['target_cpa'] * 2:
                    campaign_waste += (cpa - targets['target_cpa']) * row['conversions']
                    waste_reasons.append('CPA 2x above target')

            # Low ROAS
            if row.get('cost', 0) > 0:
                roas = row.get('conversion_value', 0) / row['cost']
                if roas < targets['target_roas'] * 0.5:
                    campaign_waste += row['cost'] * 0.5  # Consider 50% as waste
                    waste_reasons.append('ROAS below 50% of target')

            if campaign_waste > 0:
                waste['campaigns_with_waste'].append({
                    'campaign': row.get('campaign_name', 'Unknown'),
                    'waste_amount': round(campaign_waste, 2),
                    'reasons': waste_reasons
                })
                waste['total_waste'] += campaign_waste

        waste['waste_percentage'] = round(
            waste['total_waste'] / df['cost'].sum() * 100,
            2
        ) if df['cost'].sum() > 0 else 0

        return waste

    def _calculate_optimization_potential(
        self,
        df: pd.DataFrame,
        targets: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate potential improvements from optimization"""
        current_revenue = df['conversion_value'].sum() if 'conversion_value' in df.columns else 0
        current_cost = df['cost'].sum() if 'cost' in df.columns else 0
        current_conversions = df['conversions'].sum() if 'conversions' in df.columns else 0

        # Estimate potential improvements
        potential = {
            'current_metrics': {
                'revenue': round(current_revenue, 2),
                'cost': round(current_cost, 2),
                'roas': round(current_revenue / current_cost, 2) if current_cost > 0 else 0
            },
            'optimized_potential': {}
        }

        # If all campaigns hit target ROAS
        potential_revenue = current_cost * targets['target_roas']
        potential['optimized_potential']['target_roas_scenario'] = {
            'potential_revenue': round(potential_revenue, 2),
            'revenue_increase': round(potential_revenue - current_revenue, 2),
            'improvement_pct': round((potential_revenue / current_revenue - 1) * 100, 2) if current_revenue > 0 else 0
        }

        # If all campaigns hit target CPA
        if current_conversions > 0:
            optimal_cost = current_conversions * targets['target_cpa']
            potential['optimized_potential']['target_cpa_scenario'] = {
                'optimal_cost': round(optimal_cost, 2),
                'cost_savings': round(current_cost - optimal_cost, 2) if optimal_cost < current_cost else 0,
                'efficiency_gain': round((1 - optimal_cost / current_cost) * 100, 2) if current_cost > 0 else 0
            }

        return potential

    def _generate_reallocation_plan(
        self,
        df: pd.DataFrame,
        targets: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Generate budget reallocation recommendations"""
        recommendations = []

        # Identify high and low performers
        for _, row in df.iterrows():
            if row.get('cost', 0) > 0:
                roas = row.get('conversion_value', 0) / row['cost']

                if roas > targets['target_roas'] * 1.5:
                    recommendations.append({
                        'campaign': row.get('campaign_name', 'Unknown'),
                        'action': 'increase_budget',
                        'reason': f"ROAS {roas:.2f}x exceeds target by 50%",
                        'recommended_increase': '20-30%'
                    })
                elif roas < targets['target_roas'] * 0.5:
                    recommendations.append({
                        'campaign': row.get('campaign_name', 'Unknown'),
                        'action': 'decrease_budget',
                        'reason': f"ROAS {roas:.2f}x below 50% of target",
                        'recommended_decrease': '30-50%'
                    })

        return recommendations[:10]  # Top 10 recommendations

    def _calculate_marginal_roi(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate marginal ROI for budget changes"""
        marginal = {
            'analysis': [],
            'optimal_point': {}
        }

        # Simplified marginal ROI calculation
        for _, row in df.iterrows():
            if row.get('cost', 0) > 0 and row.get('conversions', 0) > 0:
                current_roi = (row.get('conversion_value', 0) - row['cost']) / row['cost'] * 100

                # Estimate marginal ROI (simplified)
                marginal_roi = current_roi * 0.8  # Assume 80% efficiency on additional spend

                marginal['analysis'].append({
                    'campaign': row.get('campaign_name', 'Unknown'),
                    'current_roi': round(current_roi, 2),
                    'estimated_marginal_roi': round(marginal_roi, 2),
                    'recommendation': 'increase' if marginal_roi > 50 else 'maintain'
                })

        # Sort by marginal ROI
        marginal['analysis'] = sorted(
            marginal['analysis'],
            key=lambda x: x['estimated_marginal_roi'],
            reverse=True
        )[:10]

        return marginal

    def _score_acquisition_efficiency(self, cac: float, payback_period: float) -> int:
        """Score acquisition efficiency (0-100)"""
        score = 50

        # CAC scoring
        if cac < 25:
            score += 25
        elif cac < 50:
            score += 15
        elif cac < 100:
            score += 5
        else:
            score -= 10

        # Payback period scoring
        if payback_period < 3:
            score += 25
        elif payback_period < 6:
            score += 15
        elif payback_period < 12:
            score += 5
        else:
            score -= 10

        return max(0, min(100, score))

    def get_tools(self) -> List[Tool]:
        """Get LangChain tools for ROI calculations"""
        return [
            Tool(
                name="calculate_campaign_roi",
                func=self.calculate_campaign_roi,
                description="Calculate comprehensive ROI metrics for campaigns"
            ),
            Tool(
                name="calculate_keyword_profitability",
                func=self.calculate_keyword_profitability,
                description="Analyze keyword-level profitability and value"
            ),
            Tool(
                name="calculate_customer_value",
                func=self.calculate_customer_value,
                description="Calculate customer lifetime value metrics"
            ),
            Tool(
                name="calculate_budget_efficiency",
                func=self.calculate_budget_efficiency,
                description="Analyze budget efficiency and optimization opportunities"
            )
        ]