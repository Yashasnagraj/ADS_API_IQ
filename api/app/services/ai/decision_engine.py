"""
Decision Management System
3-Pillar Framework: Prediction + Optimization + Rules

Synthesizes PIE, Shapley, LTV, and Anomaly Detection into ONE unified action
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import numpy as np
from app.db import models

# Import AI engines
from .anomaly_detector import AnomalyDetectionEngine
from .pie_model import PredictiveIncrementalityEngine
from .attribution_analyzer import ShapleyAttributionEngine
from .ltv_predictor import LTVPredictionEngine, CustomerSegment


class UnifiedRecommendation:
    """Represents a unified AI recommendation"""
    def __init__(
        self,
        action_type: str,
        title: str,
        message: str,
        expected_outcome: str,
        confidence_score: float,
        priority: str,
        supporting_data: Dict[str, Any],
        actionable_steps: List[str]
    ):
        self.action_type = action_type  # "BUDGET_SHIFT", "PAUSE_CAMPAIGN", "SCALE_UP", etc.
        self.title = title
        self.message = message
        self.expected_outcome = expected_outcome
        self.confidence_score = confidence_score
        self.priority = priority  # "critical", "high", "medium", "low"
        self.supporting_data = supporting_data
        self.actionable_steps = actionable_steps

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type,
            "title": self.title,
            "message": self.message,
            "expected_outcome": self.expected_outcome,
            "confidence_score": round(self.confidence_score, 2),
            "priority": self.priority,
            "supporting_data": self.supporting_data,
            "actionable_steps": self.actionable_steps,
            "generated_at": datetime.now().isoformat()
        }


class DecisionManagementSystem:
    """
    Central decision-making engine that reconciles all AI models

    Priority Hierarchy:
    1. Anomaly Check (HIGHEST) - Safety first
    2. Causal Prioritization (PIE) - True incremental impact
    3. Value Filtering (LAROAS) - Long-term customer value
    4. Behavioral Context (Shapley) - Journey insights
    5. Constraint Validation - Business rules
    """

    def __init__(self, db: Session):
        self.db = db
        self.anomaly_detector = AnomalyDetectionEngine(db)
        self.pie_engine = PredictiveIncrementalityEngine(db)
        self.attribution_engine = ShapleyAttributionEngine(db)
        self.ltv_engine = LTVPredictionEngine(db)

    def generate_unified_recommendation(
        self,
        customer_id: int,
        date: Optional[datetime.date] = None
    ) -> UnifiedRecommendation:
        """
        Generate THE unified recommendation by synthesizing all AI models

        Returns: Single, definitive action with high confidence
        """
        if date is None:
            date = datetime.now().date()

        # === STEP 1: ANOMALY CHECK (HIGHEST PRIORITY) ===
        anomalies = self.anomaly_detector.detect_anomalies(customer_id, date)

        if anomalies["has_critical_anomalies"]:
            # CRITICAL ANOMALY DETECTED - PAUSE EVERYTHING
            critical_alert = [a for a in anomalies["alerts"] if a["severity"] == "critical"][0]

            return UnifiedRecommendation(
                action_type="PAUSE_AND_INVESTIGATE",
                title="🚨 Critical Issue Detected",
                message=critical_alert["message"],
                expected_outcome="Prevent potentially costly decisions based on corrupted data",
                confidence_score=1.0,
                priority="critical",
                supporting_data={
                    "anomaly_details": critical_alert,
                    "total_anomalies": anomalies["total_anomalies"]
                },
                actionable_steps=[
                    "Investigate the anomaly immediately",
                    "Check tracking pixels and conversion setup",
                    "Verify no unauthorized campaign changes",
                    "Pause affected campaigns if needed"
                ]
            )

        # === STEP 2: GET CAUSAL INSIGHTS (PRIMARY - PIE MODEL) ===
        pie_predictions = self.pie_engine.predict_incremental_roas(customer_id, date=date)

        if not pie_predictions["predictions"]:
            # No data available
            return self._generate_no_data_recommendation(customer_id)

        # === STEP 3: GET VALUE INSIGHTS (LAROAS - LTV MODEL) ===
        ltv_predictions = self.ltv_engine.predict_ltv(customer_id)

        # === STEP 4: GET BEHAVIORAL CONTEXT (SHAPLEY ATTRIBUTION) ===
        attribution = self.attribution_engine.analyze_attribution(customer_id)

        # === STEP 5: DECISION LOGIC - SYNTHESIZE ALL MODELS ===
        recommendation = self._synthesize_models(
            customer_id,
            pie_predictions,
            ltv_predictions,
            attribution,
            anomalies
        )

        return recommendation

    def _synthesize_models(
        self,
        customer_id: int,
        pie_predictions: Dict[str, Any],
        ltv_predictions: Dict[str, Any],
        attribution: Dict[str, Any],
        anomalies: Dict[str, Any]
    ) -> UnifiedRecommendation:
        """
        Core synthesis logic - combines PIE, LTV, Shapley into one action

        Decision Priority:
        1. If PIE shows negative/low incremental ROAS → Recommend pausing
        2. If LAROAS shows opportunity → Recommend budget shift
        3. If both PIE and LAROAS are good → Recommend scaling
        4. If warnings exist → Recommend optimization
        """
        campaigns = pie_predictions["predictions"]

        # Sort by predicted incremental ROAS
        sorted_by_pie = sorted(campaigns, key=lambda x: x["predicted_incremental_roas"], reverse=True)

        best_campaign = sorted_by_pie[0]
        worst_campaign = sorted_by_pie[-1]

        # Check if we have LTV segment data
        ltv_segments = ltv_predictions.get("segments", {})

        # === DECISION SCENARIO 1: NEGATIVE INCREMENTAL ROAS (CRITICAL) ===
        if worst_campaign["predicted_incremental_roas"] < 0.5:
            # Campaign is mostly non-incremental (Generosity Flaw)
            incremental_pct = worst_campaign["incremental_percentage"]

            return UnifiedRecommendation(
                action_type="PAUSE_CAMPAIGN",
                title="⚠️ Non-Incremental Campaign Detected",
                message=(
                    f"Campaign '{worst_campaign['campaign_name']}' has only {incremental_pct:.0f}% incremental conversions. "
                    f"Most sales would have happened anyway. Pausing can save ₹{self._estimate_savings(worst_campaign):,.0f}/day."
                ),
                expected_outcome=f"Save ~₹{self._estimate_savings(worst_campaign) * 30:,.0f} per month without losing real revenue",
                confidence_score=worst_campaign["confidence_score"],
                priority="high",
                supporting_data={
                    "campaign_id": worst_campaign["campaign_id"],
                    "incremental_roas": worst_campaign["predicted_incremental_roas"],
                    "incremental_percentage": incremental_pct,
                    "pie_explanation": worst_campaign["explanation"]
                },
                actionable_steps=[
                    f"Pause campaign '{worst_campaign['campaign_name']}'",
                    "Run a holdout test to confirm non-incrementality",
                    "Reallocate budget to high-incremental campaigns",
                    "Review targeting - may be capturing existing customers"
                ]
            )

        # === DECISION SCENARIO 2: LAROAS OPTIMIZATION OPPORTUNITY ===
        # Find if any high-LAROAS campaign exists
        if ltv_segments:
            # Check if best PIE campaign has good LAROAS potential
            # In production: Would calculate actual LAROAS for each campaign
            # Simplified: Check if campaign targets high-LTV segments

            if CustomerSegment.WHALE in ltv_segments or CustomerSegment.FUTURE_WHALE in ltv_segments:
                high_ltv_segment = CustomerSegment.WHALE if CustomerSegment.WHALE in ltv_segments else CustomerSegment.FUTURE_WHALE
                high_ltv_data = ltv_segments[high_ltv_segment]

                # Budget shift recommendation
                budget_to_shift = 50000  # ₹50K
                expected_ltv_revenue = budget_to_shift * best_campaign["predicted_incremental_roas"] * (high_ltv_data["avg_ltv"] / 5000)

                return UnifiedRecommendation(
                    action_type="BUDGET_SHIFT",
                    title="💡 High-LTV Opportunity Detected",
                    message=(
                        f"Campaign '{best_campaign['campaign_name']}' has {best_campaign['predicted_incremental_roas']:.2f}x Incremental ROAS "
                        f"and acquires '{high_ltv_segment}' customers (₹{high_ltv_data['avg_ltv']:,.0f} avg LTV). "
                        f"Shift ₹{budget_to_shift:,.0f} from low-incremental campaigns for maximum long-term value."
                    ),
                    expected_outcome=f"+₹{expected_ltv_revenue:,.0f} net new revenue (lifetime value)",
                    confidence_score=best_campaign["confidence_score"] * 0.85,
                    priority="high",
                    supporting_data={
                        "best_campaign": best_campaign,
                        "worst_campaign": worst_campaign,
                        "target_segment": high_ltv_segment,
                        "segment_ltv": high_ltv_data["avg_ltv"],
                        "attribution_context": attribution.get("attribution", {})
                    },
                    actionable_steps=[
                        f"Increase budget for '{best_campaign['campaign_name']}' by ₹{budget_to_shift:,.0f}",
                        f"Decrease budget for '{worst_campaign['campaign_name']}' by ₹{budget_to_shift:,.0f}",
                        "Monitor ROAS and LTV metrics daily",
                        f"Create lookalike audiences based on '{high_ltv_segment}' segment"
                    ]
                )

        # === DECISION SCENARIO 3: SCALE UP BEST PERFORMER ===
        if best_campaign["predicted_incremental_roas"] >= 2.0:
            # Strong incremental performance - recommend scaling
            scale_amount = 30000  # ₹30K increase
            expected_revenue = scale_amount * best_campaign["predicted_incremental_roas"]

            return UnifiedRecommendation(
                action_type="SCALE_UP",
                title="🚀 High-Performance Campaign - Scale Up",
                message=(
                    f"Campaign '{best_campaign['campaign_name']}' has exceptional {best_campaign['predicted_incremental_roas']:.2f}x Incremental ROAS "
                    f"with {best_campaign['confidence_score']*100:.0f}% confidence. Increasing budget will drive net new revenue."
                ),
                expected_outcome=f"+₹{expected_revenue:,.0f} net new revenue from ₹{scale_amount:,.0f} additional spend",
                confidence_score=best_campaign["confidence_score"],
                priority="high",
                supporting_data={
                    "campaign": best_campaign,
                    "attribution_contribution": attribution.get("attribution", {})
                },
                actionable_steps=[
                    f"Increase daily budget by ₹{scale_amount:,.0f}",
                    "Monitor CPC and impression share",
                    "Ensure sufficient inventory (check Shopify stock)",
                    "Prepare for 30-50% traffic increase"
                ]
            )

        # === DECISION SCENARIO 4: WARNINGS - OPTIMIZE ===
        if anomalies["warning_count"] > 0:
            warning_alert = [a for a in anomalies["alerts"] if a["severity"] == "warning"][0]

            return UnifiedRecommendation(
                action_type="OPTIMIZE",
                title="⚠️ Optimization Opportunity",
                message=warning_alert["message"],
                expected_outcome="Improve campaign efficiency and prevent performance degradation",
                confidence_score=0.75,
                priority="medium",
                supporting_data={
                    "warning_details": warning_alert,
                    "pie_summary": pie_predictions["summary"],
                    "attribution": attribution.get("attribution", {})
                },
                actionable_steps=[
                    "Review and refresh ad creatives",
                    "Adjust bidding strategy",
                    "Analyze competitor activity",
                    "Consider A/B testing new messaging"
                ]
            )

        # === DEFAULT: ALL GOOD - MAINTAIN STRATEGY ===
        return UnifiedRecommendation(
            action_type="MAINTAIN",
            title="✅ Campaigns Performing Well",
            message=(
                f"Your top campaign '{best_campaign['campaign_name']}' maintains {best_campaign['predicted_incremental_roas']:.2f}x Incremental ROAS. "
                f"Current strategy is effective. Continue monitoring for changes."
            ),
            expected_outcome="Sustained profitable growth",
            confidence_score=best_campaign["confidence_score"],
            priority="low",
            supporting_data={
                "top_campaign": best_campaign,
                "pie_summary": pie_predictions["summary"],
                "attribution": attribution.get("attribution", {})
            },
            actionable_steps=[
                "Monitor daily performance trends",
                "Test minor optimizations incrementally",
                "Prepare for seasonal demand changes",
                "Continue collecting data for model improvement"
            ]
        )

    def _generate_no_data_recommendation(self, customer_id: int) -> UnifiedRecommendation:
        """Generate recommendation when no campaign data is available"""
        return UnifiedRecommendation(
            action_type="SETUP_REQUIRED",
            title="📋 Getting Started",
            message="No campaign data available yet. Let's set up your marketing campaigns.",
            expected_outcome="Begin tracking and optimizing your marketing performance",
            confidence_score=1.0,
            priority="high",
            supporting_data={},
            actionable_steps=[
                "Launch your first campaign in Google Ads or Meta Ads",
                "Ensure conversion tracking is properly set up",
                "Run campaigns for at least 7 days to gather data",
                "Return here for AI-powered optimization insights"
            ]
        )

    def _estimate_savings(self, campaign_data: Dict[str, Any]) -> float:
        """Estimate daily savings from pausing a non-incremental campaign"""
        # Savings = Non-incremental spend (would have gotten those conversions anyway)
        # This is a simplified calculation
        return campaign_data.get("non_incremental_conversions", 0) * 100  # Rough estimate


def get_unified_recommendation(
    db: Session,
    customer_id: int,
    date: Optional[datetime.date] = None
) -> Dict[str, Any]:
    """Helper function to get unified recommendation"""
    engine = DecisionManagementSystem(db)
    recommendation = engine.generate_unified_recommendation(customer_id, date)
    return recommendation.to_dict()
