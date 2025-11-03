"""
Predictive Incrementality by Experimentation (PIE) Model
PRIMARY causal measurement engine

Predicts TRUE incremental impact (net new revenue) of campaigns
Solves the "Generosity Flaw" - eliminates sales that would have happened anyway
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np
from app.db import models


class IncrementalityPrediction:
    """Represents a PIE model prediction"""
    def __init__(
        self,
        campaign_id: str,
        campaign_name: str,
        predicted_incremental_roas: float,
        confidence_score: float,
        total_conversions: float,
        incremental_conversions: float,
        non_incremental_conversions: float,
        explanation: str
    ):
        self.campaign_id = campaign_id
        self.campaign_name = campaign_name
        self.predicted_incremental_roas = predicted_incremental_roas
        self.confidence_score = confidence_score
        self.total_conversions = total_conversions
        self.incremental_conversions = incremental_conversions
        self.non_incremental_conversions = non_incremental_conversions
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "campaign_id": self.campaign_id,
            "campaign_name": self.campaign_name,
            "predicted_incremental_roas": round(self.predicted_incremental_roas, 2),
            "confidence_score": round(self.confidence_score, 2),
            "total_conversions": round(self.total_conversions, 2),
            "incremental_conversions": round(self.incremental_conversions, 2),
            "non_incremental_conversions": round(self.non_incremental_conversions, 2),
            "incremental_percentage": round(
                (self.incremental_conversions / self.total_conversions * 100) if self.total_conversions > 0 else 0,
                1
            ),
            "explanation": self.explanation
        }


class PredictiveIncrementalityEngine:
    """
    Predicts causal effect (ICPD - Incremental Conversions per Dollar) for campaigns

    Method: Uses post-campaign features + historical patterns to estimate incrementality
    Note: In production, this should be trained on RCT data. This is a baseline implementation.
    """

    def __init__(self, db: Session):
        self.db = db

    def estimate_baseline_conversion_rate(self, customer_id: int) -> float:
        """
        Estimate the organic/baseline conversion rate (conversions that would happen anyway)

        This represents the "Generosity Flaw" - conversions incorrectly attributed to ads
        In a full PIE model, this would come from holdout RCT groups
        """
        # Get historical data from periods with varying ad spend
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)

        campaigns = self.db.query(models.CampaignKeyword).filter(
            models.CampaignKeyword.customer_id == customer_id,
            models.CampaignKeyword.date >= str(start_date),
            models.CampaignKeyword.date <= str(end_date)
        ).all()

        if not campaigns:
            # Default baseline: assume 30% of conversions would have happened anyway
            return 0.30

        # Group by date to find low-spend days (proxy for baseline)
        daily_data = {}
        for c in campaigns:
            date_str = str(c.date)
            if date_str not in daily_data:
                daily_data[date_str] = {"spend": 0, "conversions": 0, "clicks": 0}
            daily_data[date_str]["spend"] += (c.cost_micros or 0) / 1000000
            daily_data[date_str]["conversions"] += c.conversions or 0
            daily_data[date_str]["clicks"] += c.clicks or 0

        # Find days in bottom quartile of spend (low ad activity)
        daily_list = list(daily_data.values())
        if not daily_list:
            return 0.30

        spends = [d["spend"] for d in daily_list if d["spend"] > 0]
        if not spends:
            return 0.30

        low_spend_threshold = np.percentile(spends, 25)

        low_spend_days = [d for d in daily_list if d["spend"] <= low_spend_threshold and d["clicks"] > 0]

        if low_spend_days:
            # Baseline conversion rate = average conversion rate on low-spend days
            avg_baseline_rate = np.mean([
                d["conversions"] / d["clicks"] if d["clicks"] > 0 else 0
                for d in low_spend_days
            ])
            return min(avg_baseline_rate, 0.50)  # Cap at 50%

        return 0.30  # Default

    def calculate_campaign_incrementality(
        self,
        campaign_data: models.CampaignKeyword,
        baseline_conversion_rate: float,
        customer_id: int
    ) -> IncrementalityPrediction:
        """
        Calculate predicted incrementality for a single campaign

        Incrementality = Total Conversions - Non-Incremental Conversions
        Non-Incremental = Conversions that would have happened without the ad
        """
        campaign_name = f"Campaign {campaign_data.campaign_id}"

        total_conversions = campaign_data.conversions or 0
        total_clicks = campaign_data.clicks or 0
        total_cost = (campaign_data.cost_micros or 0) / 1000000
        total_revenue = campaign_data.conversion_value or 0

        if total_cost == 0 or total_clicks == 0:
            return IncrementalityPrediction(
                campaign_id=campaign_data.campaign_id,
                campaign_name=campaign_name,
                predicted_incremental_roas=0.0,
                confidence_score=0.0,
                total_conversions=total_conversions,
                incremental_conversions=0.0,
                non_incremental_conversions=total_conversions,
                explanation="Insufficient data for incrementality prediction"
            )

        # Calculate non-incremental conversions (would have happened anyway)
        # These are conversions driven by baseline intent, not by the ad
        non_incremental_conversions = total_clicks * baseline_conversion_rate

        # Incremental conversions = conversions truly caused by the ad
        incremental_conversions = max(0, total_conversions - non_incremental_conversions)

        # Calculate incremental revenue
        revenue_per_conversion = total_revenue / total_conversions if total_conversions > 0 else 0
        incremental_revenue = incremental_conversions * revenue_per_conversion

        # Predicted Incremental ROAS = Incremental Revenue / Total Cost
        predicted_incremental_roas = incremental_revenue / total_cost if total_cost > 0 else 0

        # Calculate confidence score based on data quality
        confidence_score = self._calculate_confidence(campaign_data, customer_id)

        # Generate explanation
        incremental_pct = (incremental_conversions / total_conversions * 100) if total_conversions > 0 else 0

        if predicted_incremental_roas >= 2.0:
            performance = "excellent incremental"
            explanation = (
                f"{incremental_pct:.0f}% of conversions are truly incremental. "
                f"This campaign is driving strong net new revenue."
            )
        elif predicted_incremental_roas >= 1.0:
            performance = "positive incremental"
            explanation = (
                f"{incremental_pct:.0f}% of conversions are incremental. "
                f"Campaign is profitable after removing baseline conversions."
            )
        elif predicted_incremental_roas >= 0.5:
            performance = "weak incremental"
            explanation = (
                f"Only {incremental_pct:.0f}% of conversions are incremental. "
                f"Many conversions would have happened without this ad."
            )
        else:
            performance = "non-incremental"
            explanation = (
                f"Only {incremental_pct:.0f}% of conversions are incremental. "
                f"This campaign may be taking credit for organic conversions (Generosity Flaw)."
            )

        return IncrementalityPrediction(
            campaign_id=campaign_data.campaign_id,
            campaign_name=campaign_name,
            predicted_incremental_roas=predicted_incremental_roas,
            confidence_score=confidence_score,
            total_conversions=total_conversions,
            incremental_conversions=incremental_conversions,
            non_incremental_conversions=non_incremental_conversions,
            explanation=explanation
        )

    def _calculate_confidence(self, campaign_data: models.CampaignKeyword, customer_id: int) -> float:
        """
        Calculate confidence score for the prediction
        Based on data quality: sample size, conversion volume, historical consistency

        Returns: 0.0 to 1.0 (higher = more confident)
        """
        confidence_factors = []

        # Factor 1: Conversion volume (more conversions = higher confidence)
        conversions = campaign_data.conversions or 0
        if conversions >= 100:
            confidence_factors.append(1.0)
        elif conversions >= 50:
            confidence_factors.append(0.9)
        elif conversions >= 20:
            confidence_factors.append(0.75)
        elif conversions >= 10:
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.4)

        # Factor 2: Click volume (more data = better prediction)
        clicks = campaign_data.clicks or 0
        if clicks >= 1000:
            confidence_factors.append(1.0)
        elif clicks >= 500:
            confidence_factors.append(0.85)
        elif clicks >= 100:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.5)

        # Factor 3: Historical consistency (check if campaign has stable performance)
        # Get past 30 days of this campaign
        from datetime import datetime as dt
        if isinstance(campaign_data.date, str):
            end_date = dt.strptime(campaign_data.date, "%Y-%m-%d").date()
        else:
            end_date = campaign_data.date
        start_date = end_date - timedelta(days=30)

        historical = self.db.query(models.CampaignKeyword).filter(
            models.CampaignKeyword.customer_id == customer_id,
            models.CampaignKeyword.campaign_id == campaign_data.campaign_id,
            models.CampaignKeyword.date >= str(start_date),
            models.CampaignKeyword.date < str(end_date)
        ).all()

        if len(historical) >= 7:  # At least 7 days of history
            conversion_rates = [
                (h.conversions / h.clicks) if h.clicks > 0 else 0
                for h in historical
            ]
            if conversion_rates:
                cv_rate_std = np.std(conversion_rates)
                cv_rate_mean = np.mean(conversion_rates)
                # Low variance = high consistency = high confidence
                if cv_rate_mean > 0:
                    coefficient_of_variation = cv_rate_std / cv_rate_mean
                    if coefficient_of_variation < 0.3:
                        confidence_factors.append(1.0)
                    elif coefficient_of_variation < 0.5:
                        confidence_factors.append(0.8)
                    else:
                        confidence_factors.append(0.6)
                else:
                    confidence_factors.append(0.5)
        else:
            confidence_factors.append(0.6)  # Medium confidence for new campaigns

        # Overall confidence = weighted average
        return np.mean(confidence_factors)

    def predict_incremental_roas(
        self,
        customer_id: int,
        campaign_id: Optional[str] = None,
        date: Optional[datetime.date] = None
    ) -> Dict[str, Any]:
        """
        Predict Incremental ROAS for campaigns

        Returns predictions for all campaigns or a specific campaign
        """
        if date is None:
            date = datetime.now().date()

        # Get baseline conversion rate for this customer
        baseline_rate = self.estimate_baseline_conversion_rate(customer_id)

        # Get campaigns to analyze
        query = self.db.query(models.CampaignKeyword).filter(
            models.CampaignKeyword.customer_id == customer_id,
            models.CampaignKeyword.date == str(date)
        )

        if campaign_id:
            query = query.filter(models.CampaignKeyword.campaign_id == campaign_id)

        campaigns = query.all()

        if not campaigns:
            return {
                "customer_id": customer_id,
                "date": str(date),
                "baseline_conversion_rate": round(baseline_rate, 3),
                "predictions": [],
                "summary": {
                    "total_campaigns": 0,
                    "avg_incremental_roas": 0,
                    "total_incremental_revenue": 0,
                    "total_non_incremental_revenue": 0
                }
            }

        # Calculate incrementality for each campaign
        predictions = []
        total_incremental_revenue = 0
        total_non_incremental_revenue = 0

        for campaign in campaigns:
            prediction = self.calculate_campaign_incrementality(
                campaign,
                baseline_rate,
                customer_id
            )
            predictions.append(prediction.to_dict())

            # Aggregate metrics
            revenue_per_conversion = (
                (campaign.conversion_value / campaign.conversions)
                if campaign.conversions and campaign.conversions > 0 else 0
            )
            total_incremental_revenue += prediction.incremental_conversions * revenue_per_conversion
            total_non_incremental_revenue += prediction.non_incremental_conversions * revenue_per_conversion

        # Calculate summary metrics
        avg_incremental_roas = np.mean([p["predicted_incremental_roas"] for p in predictions]) if predictions else 0

        return {
            "customer_id": customer_id,
            "date": str(date),
            "baseline_conversion_rate": round(baseline_rate, 3),
            "baseline_explanation": (
                f"{baseline_rate*100:.0f}% of conversions estimated as baseline "
                f"(would have happened without ads)"
            ),
            "predictions": sorted(predictions, key=lambda x: x["predicted_incremental_roas"], reverse=True),
            "summary": {
                "total_campaigns": len(predictions),
                "avg_incremental_roas": round(avg_incremental_roas, 2),
                "total_incremental_revenue": round(total_incremental_revenue, 2),
                "total_non_incremental_revenue": round(total_non_incremental_revenue, 2),
                "incremental_percentage": round(
                    (total_incremental_revenue / (total_incremental_revenue + total_non_incremental_revenue) * 100)
                    if (total_incremental_revenue + total_non_incremental_revenue) > 0 else 0,
                    1
                )
            },
            "note": (
                "PIE Model estimates causal impact by removing baseline conversions. "
                "For higher accuracy, run RCT experiments and retrain the model."
            )
        }


def predict_incrementality(
    db: Session,
    customer_id: int,
    campaign_id: Optional[str] = None,
    date: Optional[datetime.date] = None
) -> Dict[str, Any]:
    """Helper function for PIE predictions"""
    engine = PredictiveIncrementalityEngine(db)
    return engine.predict_incremental_roas(customer_id, campaign_id, date)
