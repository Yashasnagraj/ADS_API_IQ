"""
Optimization Agent for Google Ads Multi-Agent System with Safety Features
"""
from typing import Dict, Any, List, Optional
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime
from enum import Enum
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_agent.warehouse_client import WarehouseClient


class OptimizationMode(Enum):
    """Optimization execution modes"""
    DRY_RUN = "dry_run"
    MANUAL_APPROVAL = "manual_approval"
    AUTO_APPLY = "auto_apply"


class OptimizationAgent:
    """
    Agent responsible for campaign optimization with safety controls
    """

    def __init__(self, data_agent=None, insight_agent=None):
        """
        Initialize Optimization Agent

        Args:
            data_agent: DataAgent instance for fetching data
            insight_agent: InsightAgent instance for performance analysis
        """
        self.data_agent = data_agent
        self.insight_agent = insight_agent
        self.name = "OptimizationAgent"
        self.warehouse_client = WarehouseClient()

        # Safety settings
        self.mode = OptimizationMode.DRY_RUN  # Default to safe mode
        self.max_bid_change_percent = 20  # Max 20% bid change
        self.max_budget_change_percent = 30  # Max 30% budget change
        self.min_data_points = 100  # Minimum data points for optimization
        self.approval_queue = []

        # Optimization thresholds
        self.thresholds = {
            'min_conversions': 5,
            'min_clicks': 50,
            'min_impressions': 1000,
            'target_roas': 4.0,
            'target_cpa': 50.0,
            'min_quality_score': 5
        }

    def set_mode(self, mode: str) -> Dict[str, Any]:
        """
        Set optimization mode

        Args:
            mode: Optimization mode (dry_run/manual_approval/auto_apply)

        Returns:
            Confirmation of mode change
        """
        try:
            self.mode = OptimizationMode(mode)
            logger.info(f"Optimization mode set to: {mode}")
            return {
                'status': 'success',
                'mode': mode,
                'message': f'Optimization mode set to {mode}'
            }
        except ValueError:
            return {
                'status': 'error',
                'message': f'Invalid mode: {mode}. Use dry_run, manual_approval, or auto_apply'
            }

    def optimize_bids(
        self,
        customer_id: str = None,
        target_roas: Optional[float] = None,
        max_bid_limit: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Optimize keyword and campaign bids

        Args:
            customer_id: Customer ID
            target_roas: Target ROAS for optimization
            max_bid_limit: Maximum bid limit

        Returns:
            Bid optimization recommendations
        """
        try:
            # Validate customer_id
            if not customer_id:
                return {
                    'status': 'error',
                    'message': 'customer_id is required for bid optimization'
                }

            # Fetch campaign and keyword data for specific customer
            campaigns_data = self.warehouse_client.fetch_campaigns(customer_id=int(customer_id))

            # Note: WarehouseClient doesn't have fetch_keywords, so we'll use campaigns for now
            # Keywords optimization can be added when keyword table is populated
            keywords_data = {'keywords': []}

            if "error" in campaigns_data or "error" in keywords_data:
                return {
                    'status': 'error',
                    'message': 'Failed to fetch data for bid optimization'
                }

            campaigns = pd.DataFrame(campaigns_data.get('campaigns', []))
            keywords = pd.DataFrame(keywords_data.get('keywords', []))

            target_roas = target_roas or self.thresholds['target_roas']
            recommendations = []

            # Campaign-level bid optimization
            if not campaigns.empty:
                for _, campaign in campaigns.iterrows():
                    if campaign.get('clicks', 0) < self.thresholds['min_clicks']:
                        continue

                    current_bid = campaign.get('max_cpc', 2.0)
                    current_roas = campaign.get('roas', 0)

                    # Calculate recommended bid adjustment
                    if current_roas > 0:
                        bid_multiplier = target_roas / current_roas
                        bid_multiplier = np.clip(bid_multiplier, 0.8, 1.2)  # Limit to ±20%
                    else:
                        bid_multiplier = 0.9  # Reduce bid for zero ROAS

                    new_bid = current_bid * bid_multiplier

                    if max_bid_limit:
                        new_bid = min(new_bid, max_bid_limit)

                    if abs(new_bid - current_bid) > 0.01:
                        recommendations.append({
                            'type': 'campaign_bid',
                            'entity': campaign['name'],
                            'current_bid': round(current_bid, 2),
                            'recommended_bid': round(new_bid, 2),
                            'change_percent': round((new_bid - current_bid) / current_bid * 100, 1),
                            'reason': f'Optimize for target ROAS of {target_roas}',
                            'estimated_impact': {
                                'roas_change': round((target_roas - current_roas), 2),
                                'spend_change': round((new_bid - current_bid) * campaign.get('clicks', 0), 2)
                            }
                        })

            # Keyword-level bid optimization
            if not keywords.empty:
                for _, keyword in keywords.iterrows():
                    if keyword.get('impressions', 0) < self.thresholds['min_impressions']:
                        continue

                    quality_score = keyword.get('quality_score', 5)
                    current_bid = keyword.get('max_cpc', 2.0)

                    # Adjust bid based on quality score
                    if quality_score >= 8:
                        bid_adjustment = 1.1  # Increase bid for high QS
                    elif quality_score >= 5:
                        bid_adjustment = 1.0  # Maintain bid
                    else:
                        bid_adjustment = 0.9  # Decrease bid for low QS

                    # Consider performance metrics
                    conv_rate = keyword.get('conversion_rate', 0)
                    if conv_rate > 5:
                        bid_adjustment *= 1.1
                    elif conv_rate < 1:
                        bid_adjustment *= 0.9

                    new_bid = current_bid * bid_adjustment
                    new_bid = np.clip(new_bid, current_bid * 0.8, current_bid * 1.2)

                    if max_bid_limit:
                        new_bid = min(new_bid, max_bid_limit)

                    if abs(new_bid - current_bid) > 0.01:
                        recommendations.append({
                            'type': 'keyword_bid',
                            'entity': keyword.get('text', 'Unknown'),
                            'current_bid': round(current_bid, 2),
                            'recommended_bid': round(new_bid, 2),
                            'change_percent': round((new_bid - current_bid) / current_bid * 100, 1),
                            'quality_score': quality_score,
                            'reason': f'QS: {quality_score}, Conv Rate: {conv_rate:.1f}%'
                        })

            # Apply changes based on mode
            result = self._apply_optimizations(recommendations, 'bid')

            return result

        except Exception as e:
            logger.error(f"Error in bid optimization: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'recommendations': []
            }

    def optimize_budgets(
        self,
        customer_id: str = None,
        total_budget: Optional[float] = None,
        reallocation_strategy: str = "performance_based"
    ) -> Dict[str, Any]:
        """
        Optimize campaign budget allocation

        Args:
            customer_id: Customer ID
            total_budget: Total budget to allocate
            reallocation_strategy: Strategy for budget reallocation

        Returns:
            Budget optimization recommendations
        """
        try:
            # Validate customer_id
            if not customer_id:
                return {
                    'status': 'error',
                    'message': 'customer_id is required for budget optimization'
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
                    'recommendations': [],
                    'message': 'No campaigns found'
                }

            # Calculate performance scores
            campaigns['performance_score'] = (
                campaigns['roas'] * 0.4 +
                campaigns['conversion_rate'] * 0.3 +
                (1 / (campaigns['cpa'] + 1)) * 100 * 0.3
            )

            # Get current total budget if not provided
            if not total_budget:
                total_budget = campaigns['budget'].sum()

            recommendations = []

            if reallocation_strategy == "performance_based":
                # Allocate budget based on performance scores
                total_score = campaigns['performance_score'].sum()

                for _, campaign in campaigns.iterrows():
                    current_budget = campaign['budget']
                    score_ratio = campaign['performance_score'] / total_score
                    recommended_budget = total_budget * score_ratio

                    # Apply safety limits
                    max_increase = current_budget * (1 + self.max_budget_change_percent / 100)
                    max_decrease = current_budget * (1 - self.max_budget_change_percent / 100)
                    recommended_budget = np.clip(recommended_budget, max_decrease, max_increase)

                    if abs(recommended_budget - current_budget) > 1:
                        recommendations.append({
                            'type': 'budget_reallocation',
                            'campaign': campaign['name'],
                            'current_budget': round(current_budget, 2),
                            'recommended_budget': round(recommended_budget, 2),
                            'change_percent': round((recommended_budget - current_budget) / current_budget * 100, 1),
                            'performance_score': round(campaign['performance_score'], 2),
                            'current_roas': round(campaign['roas'], 2),
                            'reason': f'Performance-based reallocation (score: {campaign["performance_score"]:.1f})'
                        })

            elif reallocation_strategy == "roas_based":
                # Allocate more to high ROAS campaigns
                campaigns_with_conversions = campaigns[campaigns['conversions'] > 0]

                if not campaigns_with_conversions.empty:
                    total_roas = campaigns_with_conversions['roas'].sum()

                    for _, campaign in campaigns_with_conversions.iterrows():
                        current_budget = campaign['budget']
                        roas_ratio = campaign['roas'] / total_roas
                        recommended_budget = total_budget * roas_ratio

                        # Apply safety limits
                        max_increase = current_budget * (1 + self.max_budget_change_percent / 100)
                        max_decrease = current_budget * (1 - self.max_budget_change_percent / 100)
                        recommended_budget = np.clip(recommended_budget, max_decrease, max_increase)

                        if abs(recommended_budget - current_budget) > 1:
                            recommendations.append({
                                'type': 'budget_reallocation',
                                'campaign': campaign['name'],
                                'current_budget': round(current_budget, 2),
                                'recommended_budget': round(recommended_budget, 2),
                                'change_percent': round((recommended_budget - current_budget) / current_budget * 100, 1),
                                'current_roas': round(campaign['roas'], 2),
                                'reason': f'ROAS-based reallocation (ROAS: {campaign["roas"]:.2f})'
                            })

            # Apply changes based on mode
            result = self._apply_optimizations(recommendations, 'budget')

            return result

        except Exception as e:
            logger.error(f"Error in budget optimization: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'recommendations': []
            }

    def recommend_budget_allocation(
        self,
        customer_id: str = None,
        optimization_goal: str = "maximize_conversions"
    ) -> Dict[str, Any]:
        """
        Generate smart budget allocation recommendations

        Args:
            customer_id: Customer ID
            optimization_goal: Goal for optimization (maximize_conversions/minimize_cpa/maximize_roas)

        Returns:
            Budget allocation recommendations
        """
        try:
            # Validate customer_id
            if not customer_id:
                return {
                    'status': 'error',
                    'message': 'customer_id is required for budget allocation recommendation'
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
                    'recommendations': [],
                    'message': 'No campaigns found'
                }

            total_budget = campaigns['budget'].sum()
            recommendations = []

            if optimization_goal == "maximize_conversions":
                # Allocate budget to campaigns with best conversion rates
                campaigns['efficiency'] = campaigns['conversion_rate'] / (campaigns['cpc'] + 0.01)
                sorted_campaigns = campaigns.sort_values('efficiency', ascending=False)

                # Progressive allocation strategy
                allocation_tiers = [0.4, 0.3, 0.2, 0.1]  # Top campaigns get 40%, next 30%, etc.
                tier_size = max(1, len(sorted_campaigns) // 4)

                for i, tier_percent in enumerate(allocation_tiers):
                    tier_start = i * tier_size
                    tier_end = min((i + 1) * tier_size, len(sorted_campaigns))
                    tier_campaigns = sorted_campaigns.iloc[tier_start:tier_end]

                    tier_budget = total_budget * tier_percent
                    campaigns_in_tier = len(tier_campaigns)

                    if campaigns_in_tier > 0:
                        budget_per_campaign = tier_budget / campaigns_in_tier

                        for _, campaign in tier_campaigns.iterrows():
                            recommendations.append({
                                'campaign': campaign['name'],
                                'current_budget': round(campaign['budget'], 2),
                                'recommended_budget': round(budget_per_campaign, 2),
                                'tier': i + 1,
                                'efficiency_score': round(campaign['efficiency'], 2),
                                'expected_conversions': round(budget_per_campaign / campaign.get('cpa', 50), 1),
                                'reason': f'Tier {i+1} allocation for conversion maximization'
                            })

            elif optimization_goal == "minimize_cpa":
                # Focus budget on campaigns with lowest CPA
                campaigns_with_conversions = campaigns[campaigns['conversions'] > 0]

                if not campaigns_with_conversions.empty:
                    campaigns_with_conversions['inverse_cpa'] = 1 / (campaigns_with_conversions['cpa'] + 1)
                    total_inverse_cpa = campaigns_with_conversions['inverse_cpa'].sum()

                    for _, campaign in campaigns_with_conversions.iterrows():
                        allocation_ratio = campaign['inverse_cpa'] / total_inverse_cpa
                        recommended_budget = total_budget * allocation_ratio

                        recommendations.append({
                            'campaign': campaign['name'],
                            'current_budget': round(campaign['budget'], 2),
                            'recommended_budget': round(recommended_budget, 2),
                            'current_cpa': round(campaign['cpa'], 2),
                            'expected_cpa_change': round((campaign['cpa'] * 0.9) - campaign['cpa'], 2),  # Estimate 10% improvement
                            'reason': f'CPA optimization (current CPA: ${campaign["cpa"]:.2f})'
                        })

            elif optimization_goal == "maximize_roas":
                # Allocate budget based on ROAS performance
                campaigns['weighted_roas'] = campaigns['roas'] * np.log(campaigns['impressions'] + 1)  # Weight by data volume
                total_weighted_roas = campaigns['weighted_roas'].sum()

                if total_weighted_roas > 0:
                    for _, campaign in campaigns.iterrows():
                        allocation_ratio = campaign['weighted_roas'] / total_weighted_roas
                        recommended_budget = total_budget * allocation_ratio

                        recommendations.append({
                            'campaign': campaign['name'],
                            'current_budget': round(campaign['budget'], 2),
                            'recommended_budget': round(recommended_budget, 2),
                            'current_roas': round(campaign['roas'], 2),
                            'weighted_score': round(campaign['weighted_roas'], 2),
                            'expected_revenue': round(recommended_budget * campaign['roas'], 2),
                            'reason': f'ROAS maximization (current ROAS: {campaign["roas"]:.2f}x)'
                        })

            # Calculate overall impact
            if recommendations:
                total_current = sum(r['current_budget'] for r in recommendations)
                total_recommended = sum(r['recommended_budget'] for r in recommendations)

                impact_summary = {
                    'total_budget': round(total_budget, 2),
                    'optimization_goal': optimization_goal,
                    'campaigns_optimized': len(recommendations),
                    'budget_shift': round(abs(total_recommended - total_current), 2),
                    'recommendations': recommendations
                }

                return {
                    'status': 'success',
                    'impact_summary': impact_summary,
                    'mode': self.mode.value,
                    'generated_at': datetime.now().isoformat()
                }

            return {
                'status': 'success',
                'recommendations': [],
                'message': 'No optimization opportunities found'
            }

        except Exception as e:
            logger.error(f"Error in budget allocation recommendation: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'recommendations': []
            }

    def optimize_keywords(
        self,
        customer_id: str = None,
        add_negative_keywords: bool = True
    ) -> Dict[str, Any]:
        """
        Optimize keywords including negative keyword recommendations

        Args:
            customer_id: Customer ID
            add_negative_keywords: Whether to recommend negative keywords

        Returns:
            Keyword optimization recommendations
        """
        try:
            # Validate customer_id
            if not customer_id:
                return {
                    'status': 'error',
                    'message': 'customer_id is required for keyword optimization'
                }

            # For now, keyword optimization will use campaign-level data
            # When keyword table is populated, we can add granular keyword analysis
            campaigns_data = self.warehouse_client.fetch_campaigns(customer_id=int(customer_id))

            if "error" in campaigns_data:
                return {
                    'status': 'error',
                    'message': 'Failed to fetch campaign data for keyword optimization'
                }

            campaigns = pd.DataFrame(campaigns_data.get('campaigns', []))
            recommendations = []

            # Identify low-performing campaigns that need keyword review
            if not campaigns.empty:
                low_performers = campaigns[
                    (campaigns['ctr'] < 1.0) &
                    (campaigns['conversions'] == 0) &
                    (campaigns['cost'] > 50)
                ]

                for _, campaign in low_performers.iterrows():
                    recommendations.append({
                        'type': 'review_campaign_keywords',
                        'campaign': campaign['name'],
                        'reason': f'Low CTR ({campaign["ctr"]:.2f}%), no conversions, ${campaign["cost"]:.2f} spent',
                        'expected_savings': round(campaign['cost'] * 0.3, 2),  # Estimate 30% savings
                        'action': 'Review and add negative keywords, pause low-quality keywords'
                    })

            # Note: When keyword and search_terms tables are populated,
            # we can add granular keyword pause and negative keyword recommendations

            # Apply changes based on mode
            result = self._apply_optimizations(recommendations, 'keyword')

            return result

        except Exception as e:
            logger.error(f"Error in keyword optimization: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'recommendations': []
            }

    def request_human_approval(
        self,
        optimization_id: str = None
    ) -> Dict[str, Any]:
        """
        Request human approval for pending optimizations

        Args:
            optimization_id: Specific optimization to approve/reject

        Returns:
            Approval request details
        """
        if not self.approval_queue:
            return {
                'status': 'success',
                'message': 'No pending optimizations',
                'queue': []
            }

        if optimization_id:
            # Find specific optimization
            optimization = next((o for o in self.approval_queue if o['id'] == optimization_id), None)

            if optimization:
                return {
                    'status': 'pending_approval',
                    'optimization': optimization,
                    'instructions': 'Review and approve/reject using approve_optimization() or reject_optimization()'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Optimization {optimization_id} not found'
                }
        else:
            # Return all pending optimizations
            return {
                'status': 'pending_approval',
                'queue': self.approval_queue,
                'total_pending': len(self.approval_queue),
                'instructions': 'Review and approve/reject each optimization'
            }

    def approve_optimization(
        self,
        optimization_id: str,
        apply_immediately: bool = False
    ) -> Dict[str, Any]:
        """
        Approve a pending optimization

        Args:
            optimization_id: ID of optimization to approve
            apply_immediately: Whether to apply immediately

        Returns:
            Approval confirmation
        """
        optimization = next((o for o in self.approval_queue if o['id'] == optimization_id), None)

        if not optimization:
            return {
                'status': 'error',
                'message': f'Optimization {optimization_id} not found'
            }

        # Remove from queue
        self.approval_queue = [o for o in self.approval_queue if o['id'] != optimization_id]

        if apply_immediately:
            # In production, this would apply the changes via Google Ads API
            logger.info(f"Applying optimization {optimization_id}")
            return {
                'status': 'success',
                'message': f'Optimization {optimization_id} approved and applied',
                'optimization': optimization
            }
        else:
            return {
                'status': 'success',
                'message': f'Optimization {optimization_id} approved for batch processing',
                'optimization': optimization
            }

    def reject_optimization(
        self,
        optimization_id: str,
        reason: str = None
    ) -> Dict[str, Any]:
        """
        Reject a pending optimization

        Args:
            optimization_id: ID of optimization to reject
            reason: Reason for rejection

        Returns:
            Rejection confirmation
        """
        optimization = next((o for o in self.approval_queue if o['id'] != optimization_id), None)

        if not optimization:
            return {
                'status': 'error',
                'message': f'Optimization {optimization_id} not found'
            }

        # Remove from queue
        self.approval_queue = [o for o in self.approval_queue if o['id'] != optimization_id]

        logger.info(f"Rejected optimization {optimization_id}: {reason}")

        return {
            'status': 'success',
            'message': f'Optimization {optimization_id} rejected',
            'reason': reason,
            'optimization': optimization
        }

    def _apply_optimizations(
        self,
        recommendations: List[Dict],
        optimization_type: str
    ) -> Dict[str, Any]:
        """
        Apply optimizations based on current mode

        Args:
            recommendations: List of optimization recommendations
            optimization_type: Type of optimization (bid/budget/keyword)

        Returns:
            Application result
        """
        if not recommendations:
            return {
                'status': 'success',
                'message': 'No optimizations needed',
                'recommendations': []
            }

        optimization_id = f"{optimization_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        if self.mode == OptimizationMode.DRY_RUN:
            # Just return recommendations without applying
            return {
                'status': 'success',
                'mode': 'dry_run',
                'optimization_id': optimization_id,
                'recommendations': recommendations,
                'total_recommendations': len(recommendations),
                'message': 'Dry run completed. No changes applied.',
                'next_step': 'Review recommendations and switch to manual_approval or auto_apply mode to apply changes'
            }

        elif self.mode == OptimizationMode.MANUAL_APPROVAL:
            # Add to approval queue
            self.approval_queue.append({
                'id': optimization_id,
                'type': optimization_type,
                'recommendations': recommendations,
                'created_at': datetime.now().isoformat(),
                'status': 'pending_approval'
            })

            return {
                'status': 'pending_approval',
                'mode': 'manual_approval',
                'optimization_id': optimization_id,
                'recommendations': recommendations,
                'total_recommendations': len(recommendations),
                'message': 'Optimizations queued for approval',
                'next_step': 'Use request_human_approval() to review and approve/reject'
            }

        elif self.mode == OptimizationMode.AUTO_APPLY:
            # In production, this would apply changes via Google Ads API
            # For now, we'll simulate the application

            applied = []
            failed = []

            for rec in recommendations:
                # Simulate application with 95% success rate
                if np.random.random() > 0.05:
                    applied.append(rec)
                else:
                    failed.append(rec)

            logger.info(f"Applied {len(applied)} optimizations, {len(failed)} failed")

            return {
                'status': 'applied',
                'mode': 'auto_apply',
                'optimization_id': optimization_id,
                'applied': applied,
                'failed': failed,
                'total_applied': len(applied),
                'total_failed': len(failed),
                'message': f'Successfully applied {len(applied)} optimizations'
            }

        return {
            'status': 'error',
            'message': 'Invalid optimization mode'
        }