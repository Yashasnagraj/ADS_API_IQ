"""
Customer Lifetime Value (LTV) Prediction Engine
Enables LAROAS (LTV-Adjusted ROAS) optimization

Combines RFM segmentation with predictive modeling
Ensures budget prioritizes campaigns acquiring high-value customers
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np
from app.db import models


class CustomerSegment:
    """Customer segment classification"""
    WHALE = "Whale"  # High LTV, high engagement
    LOYALIST = "Loyalist"  # Regular, consistent purchaser
    FUTURE_WHALE = "Future Whale"  # High engagement, growing LTV
    AT_RISK = "At Risk"  # Previously active, declining
    ONE_TIME_BUYER = "One-Time Buyer"  # Single purchase
    DORMANT = "Dormant"  # Churned customer


class RFMScore:
    """RFM (Recency, Frequency, Monetary) scoring result"""
    def __init__(
        self,
        recency_score: int,
        frequency_score: int,
        monetary_score: int,
        recency_days: float,
        purchase_frequency: float,
        avg_order_value: float
    ):
        self.recency_score = recency_score  # 1-5 (5 = most recent)
        self.frequency_score = frequency_score  # 1-5 (5 = most frequent)
        self.monetary_score = monetary_score  # 1-5 (5 = highest value)
        self.recency_days = recency_days
        self.purchase_frequency = purchase_frequency
        self.avg_order_value = avg_order_value

        # Combined score
        self.rfm_score = f"{recency_score}{frequency_score}{monetary_score}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recency_score": self.recency_score,
            "frequency_score": self.frequency_score,
            "monetary_score": self.monetary_score,
            "rfm_score": self.rfm_score,
            "recency_days": round(self.recency_days, 1),
            "purchase_frequency": round(self.purchase_frequency, 2),
            "avg_order_value": round(self.avg_order_value, 2)
        }


class LTVPredictionEngine:
    """
    Predicts customer lifetime value using ML-enhanced RFM analysis
    Segments customers and calculates LAROAS for campaigns
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_rfm_scores(
        self,
        customer_id: int,
        days_lookback: int = 365
    ) -> Dict[str, RFMScore]:
        """
        Calculate RFM scores for all customers

        Returns: Dict mapping customer identifiers to RFM scores
        Note: Simplified version using campaign-level data
        In production: Would use Shopify customer transaction data
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_lookback)

        # Get all campaign performance data with conversions
        campaigns = self.db.query(models.CampaignKeyword).filter(
            models.CampaignKeyword.customer_id == customer_id,
            models.CampaignKeyword.date >= str(start_date),
            models.CampaignKeyword.date <= str(end_date),
            models.CampaignKeyword.conversions > 0
        ).all()

        if not campaigns:
            return {}

        # Group by campaign to simulate customer segments
        # In production: Would group by actual Shopify customer_id
        campaign_groups = {}
        for campaign in campaigns:
            campaign_key = campaign.campaign_id
            if campaign_key not in campaign_groups:
                campaign_groups[campaign_key] = []
            campaign_groups[campaign_key].append(campaign)

        rfm_scores = {}

        for campaign_key, campaign_list in campaign_groups.items():
            # Calculate Recency (days since last conversion)
            latest_date = max(c.date for c in campaign_list)
            recency_days = (end_date - latest_date).days

            # Calculate Frequency (number of conversion events)
            frequency = len(campaign_list)

            # Calculate Monetary (average conversion value)
            total_value = sum(c.conversion_value or 0 for c in campaign_list)
            total_conversions = sum(c.conversions or 0 for c in campaign_list)
            avg_order_value = total_value / total_conversions if total_conversions > 0 else 0

            # Score each dimension (1-5)
            recency_score = self._score_recency(recency_days)
            frequency_score = self._score_frequency(frequency)
            monetary_score = self._score_monetary(avg_order_value)

            rfm_scores[campaign_key] = RFMScore(
                recency_score=recency_score,
                frequency_score=frequency_score,
                monetary_score=monetary_score,
                recency_days=recency_days,
                purchase_frequency=frequency / 365.0,  # Annual frequency
                avg_order_value=avg_order_value
            )

        return rfm_scores

    def _score_recency(self, days: float) -> int:
        """Score recency (1-5, higher = more recent)"""
        if days <= 7:
            return 5
        elif days <= 30:
            return 4
        elif days <= 90:
            return 3
        elif days <= 180:
            return 2
        else:
            return 1

    def _score_frequency(self, count: int) -> int:
        """Score frequency (1-5, higher = more frequent)"""
        if count >= 20:
            return 5
        elif count >= 10:
            return 4
        elif count >= 5:
            return 3
        elif count >= 2:
            return 2
        else:
            return 1

    def _score_monetary(self, value: float) -> int:
        """Score monetary value (1-5, higher = more valuable)"""
        if value >= 10000:
            return 5
        elif value >= 5000:
            return 4
        elif value >= 2000:
            return 3
        elif value >= 500:
            return 2
        else:
            return 1

    def segment_customers(self, rfm_score: RFMScore) -> str:
        """
        Segment customers using ML-enhanced RFM analysis

        Segments:
        - Whale: R5F5M5, R5F5M4, R5F4M5
        - Loyalist: R4-5, F4-5, M3-4
        - Future Whale: Low M but high R+F (high engagement, growing value)
        - At Risk: High M+F but low R (valuable but inactive)
        - One-Time Buyer: F1, any R+M
        - Dormant: R1-2, F1-2
        """
        r = rfm_score.recency_score
        f = rfm_score.frequency_score
        m = rfm_score.monetary_score

        # Whale: Top tier across all dimensions
        if r >= 5 and f >= 4 and m >= 4:
            return CustomerSegment.WHALE

        # Future Whale: High engagement but growing value
        if r >= 4 and f >= 4 and m <= 3:
            return CustomerSegment.FUTURE_WHALE

        # Loyalist: Consistent and valuable
        if r >= 4 and f >= 3 and m >= 3:
            return CustomerSegment.LOYALIST

        # At Risk: Was valuable but becoming inactive
        if r <= 2 and f >= 3 and m >= 3:
            return CustomerSegment.AT_RISK

        # One-Time Buyer
        if f == 1:
            return CustomerSegment.ONE_TIME_BUYER

        # Dormant: Inactive
        if r <= 2 and f <= 2:
            return CustomerSegment.DORMANT

        # Default
        return CustomerSegment.ONE_TIME_BUYER

    def predict_ltv(
        self,
        customer_id: int,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Predict LTV for customer segments acquired by campaigns

        Returns LTV predictions, segments, and LAROAS calculations
        """
        # Calculate RFM scores
        rfm_scores = self.calculate_rfm_scores(customer_id)

        if not rfm_scores:
            return {
                "customer_id": customer_id,
                "segments": {},
                "ltv_predictions": {},
                "note": "No customer data available for LTV prediction"
            }

        # Segment customers and predict LTV
        segment_analysis = {}

        for campaign_key, rfm_score in rfm_scores.items():
            segment = self.segment_customers(rfm_score)

            # Predict LTV using historical patterns
            predicted_ltv = self._predict_ltv_value(rfm_score, segment)

            # Calculate churn probability
            churn_probability = self._predict_churn_probability(rfm_score)

            if segment not in segment_analysis:
                segment_analysis[segment] = {
                    "count": 0,
                    "avg_ltv": 0,
                    "total_ltv": 0,
                    "avg_recency_days": 0,
                    "avg_purchase_frequency": 0,
                    "avg_order_value": 0,
                    "avg_churn_probability": 0
                }

            segment_analysis[segment]["count"] += 1
            segment_analysis[segment]["total_ltv"] += predicted_ltv
            segment_analysis[segment]["avg_recency_days"] += rfm_score.recency_days
            segment_analysis[segment]["avg_purchase_frequency"] += rfm_score.purchase_frequency
            segment_analysis[segment]["avg_order_value"] += rfm_score.avg_order_value
            segment_analysis[segment]["avg_churn_probability"] += churn_probability

        # Calculate averages
        for segment, data in segment_analysis.items():
            count = data["count"]
            data["avg_ltv"] = round(data["total_ltv"] / count, 2)
            data["avg_recency_days"] = round(data["avg_recency_days"] / count, 1)
            data["avg_purchase_frequency"] = round(data["avg_purchase_frequency"] / count, 2)
            data["avg_order_value"] = round(data["avg_order_value"] / count, 2)
            data["avg_churn_probability"] = round(data["avg_churn_probability"] / count, 2)

        # Sort by LTV (descending)
        sorted_segments = dict(sorted(
            segment_analysis.items(),
            key=lambda x: x[1]["avg_ltv"],
            reverse=True
        ))

        return {
            "customer_id": customer_id,
            "total_customers": len(rfm_scores),
            "segments": sorted_segments,
            "insights": self._generate_ltv_insights(sorted_segments)
        }

    def _predict_ltv_value(self, rfm_score: RFMScore, segment: str) -> float:
        """
        Predict LTV value using simplified model

        In production: Would use trained ML model (regression/deep learning)
        Current: Uses RFM-based heuristics
        """
        base_ltv = rfm_score.avg_order_value * rfm_score.purchase_frequency * 365 * 3  # 3 year horizon

        # Segment multipliers
        segment_multipliers = {
            CustomerSegment.WHALE: 2.5,
            CustomerSegment.LOYALIST: 2.0,
            CustomerSegment.FUTURE_WHALE: 2.2,
            CustomerSegment.AT_RISK: 1.2,
            CustomerSegment.ONE_TIME_BUYER: 0.8,
            CustomerSegment.DORMANT: 0.3
        }

        multiplier = segment_multipliers.get(segment, 1.0)
        predicted_ltv = base_ltv * multiplier

        return predicted_ltv

    def _predict_churn_probability(self, rfm_score: RFMScore) -> float:
        """Predict probability of customer churning (0.0 - 1.0)"""
        # Higher recency days = higher churn probability
        recency_factor = min(rfm_score.recency_days / 365, 1.0)

        # Lower frequency = higher churn probability
        frequency_factor = max(0, 1.0 - (rfm_score.purchase_frequency * 10))

        churn_prob = (recency_factor + frequency_factor) / 2
        return min(max(churn_prob, 0.0), 1.0)

    def calculate_laroas(
        self,
        customer_id: int,
        campaign_id: str,
        date: Optional[datetime.date] = None
    ) -> Dict[str, Any]:
        """
        Calculate LTV-Adjusted ROAS (LAROAS) for a campaign

        LAROAS = Incremental ROAS × Average LTV of acquired customers

        This ensures budget prioritizes campaigns acquiring high-value customers,
        not just campaigns with high short-term ROAS
        """
        if date is None:
            date = datetime.now().date()

        # Get campaign performance
        campaign = self.db.query(models.CampaignKeyword).filter(
            models.CampaignKeyword.customer_id == customer_id,
            models.CampaignKeyword.campaign_id == campaign_id,
            models.CampaignKeyword.date == str(date)
        ).first()

        if not campaign:
            return {
                "error": "Campaign not found",
                "campaign_id": campaign_id
            }

        # Get LTV prediction for customers acquired by this campaign
        ltv_prediction = self.predict_ltv(customer_id, campaign_id)

        # Find which segment this campaign primarily acquires
        # In production: Would track actual customer acquisition by campaign
        # Simplified: Use campaign performance to infer segment
        rfm_scores = self.calculate_rfm_scores(customer_id)
        if campaign_id in rfm_scores:
            segment = self.segment_customers(rfm_scores[campaign_id])
            avg_ltv = ltv_prediction["segments"].get(segment, {}).get("avg_ltv", 0)
        else:
            # Default to middle segment
            segment = CustomerSegment.ONE_TIME_BUYER
            avg_ltv = 5000  # Default

        # Calculate standard ROAS (cost is in micros)
        campaign_cost = (campaign.cost_micros / 1000000) if campaign.cost_micros else 0
        standard_roas = (
            (campaign.conversion_value / campaign_cost)
            if campaign_cost > 0 and campaign.conversion_value else 0
        )

        # Calculate LAROAS
        # LAROAS = Standard ROAS × (LTV / First Purchase Value)
        first_purchase_value = campaign.conversion_value / campaign.conversions if campaign.conversions > 0 else 0
        ltv_multiplier = avg_ltv / first_purchase_value if first_purchase_value > 0 else 1.0

        laroas = standard_roas * ltv_multiplier

        return {
            "campaign_id": campaign_id,
            "campaign_name": f"Campaign {campaign_id}",
            "date": str(date),
            "standard_roas": round(standard_roas, 2),
            "laroas": round(laroas, 2),
            "acquired_segment": segment,
            "avg_customer_ltv": round(avg_ltv, 2),
            "ltv_multiplier": round(ltv_multiplier, 2),
            "explanation": (
                f"This campaign acquires '{segment}' customers with avg LTV of ₹{avg_ltv:,.0f}. "
                f"LAROAS ({laroas:.2f}x) adjusts for long-term value vs standard ROAS ({standard_roas:.2f}x)."
            )
        }

    def _generate_ltv_insights(self, segments: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate actionable insights from LTV segmentation"""
        insights = []

        if not segments:
            return insights

        # Insight 1: Best segment
        top_segment = list(segments.keys())[0]
        top_ltv = segments[top_segment]["avg_ltv"]
        top_count = segments[top_segment]["count"]

        insights.append(
            f"🏆 Your '{top_segment}' segment has the highest LTV at ₹{top_ltv:,.0f} "
            f"({top_count} customers)"
        )

        # Insight 2: At Risk customers
        if CustomerSegment.AT_RISK in segments:
            at_risk_data = segments[CustomerSegment.AT_RISK]
            insights.append(
                f"⚠️ {at_risk_data['count']} '{CustomerSegment.AT_RISK}' customers "
                f"(₹{at_risk_data['avg_ltv']:,.0f} avg LTV) need reactivation campaigns"
            )

        # Insight 3: Future Whales
        if CustomerSegment.FUTURE_WHALE in segments:
            future_whales = segments[CustomerSegment.FUTURE_WHALE]
            insights.append(
                f"🚀 {future_whales['count']} '{CustomerSegment.FUTURE_WHALE}' customers show high growth potential - "
                f"nurture with exclusive offers"
            )

        # Insight 4: One-Time Buyers
        if CustomerSegment.ONE_TIME_BUYER in segments:
            one_time = segments[CustomerSegment.ONE_TIME_BUYER]
            if one_time["count"] > len(segments) * 0.3:  # More than 30%
                insights.append(
                    f"📈 {one_time['count']} '{CustomerSegment.ONE_TIME_BUYER}' customers - "
                    f"focus on retention campaigns to increase repeat purchases"
                )

        return insights


def predict_ltv(db: Session, customer_id: int, campaign_id: Optional[str] = None) -> Dict[str, Any]:
    """Helper function for LTV prediction"""
    engine = LTVPredictionEngine(db)
    return engine.predict_ltv(customer_id, campaign_id)


def calculate_laroas(
    db: Session,
    customer_id: int,
    campaign_id: str,
    date: Optional[datetime.date] = None
) -> Dict[str, Any]:
    """Helper function for LAROAS calculation"""
    engine = LTVPredictionEngine(db)
    return engine.calculate_laroas(customer_id, campaign_id, date)
