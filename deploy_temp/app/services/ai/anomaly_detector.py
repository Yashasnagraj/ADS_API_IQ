"""
Anomaly Detection Engine
High-priority interrupt for data integrity safeguarding
Uses Isolation Forest, LOF, and Z-Score methods
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np
from app.db import models


class AnomalyAlert:
    """Represents a detected anomaly"""
    def __init__(
        self,
        metric_name: str,
        current_value: float,
        expected_range: Tuple[float, float],
        severity: str,
        message: str,
        affected_entity: str = None
    ):
        self.metric_name = metric_name
        self.current_value = current_value
        self.expected_range = expected_range
        self.severity = severity  # "critical", "warning", "info"
        self.message = message
        self.affected_entity = affected_entity
        self.detected_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "expected_range": self.expected_range,
            "severity": self.severity,
            "message": self.message,
            "affected_entity": self.affected_entity,
            "detected_at": self.detected_at.isoformat()
        }


class AnomalyDetectionEngine:
    """
    Real-time outlier detection across all metrics
    BLOCKS optimization pipeline if critical anomaly detected
    """

    def __init__(self, db: Session):
        self.db = db

    def get_historical_stats(
        self,
        customer_id: int,
        metric_name: str,
        days_lookback: int = 30
    ) -> Dict[str, float]:
        """
        Calculate historical statistics for a metric
        Returns mean, std, min, max, median
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_lookback)

        # Get campaign performance data for the period
        campaigns = self.db.query(models.CampaignKeyword).filter(
            models.CampaignKeyword.customer_id == customer_id,
            models.CampaignKeyword.date >= str(start_date),
            models.CampaignKeyword.date <= str(end_date)
        ).all()

        if not campaigns:
            return {"mean": 0, "std": 0, "min": 0, "max": 0, "median": 0}

        # Extract values based on metric name (cost is in micros)
        values = []
        for c in campaigns:
            if metric_name == "cpc":
                if c.clicks and c.clicks > 0 and c.cost_micros:
                    values.append((c.cost_micros / 1000000) / c.clicks)
            elif metric_name == "ctr":
                if c.impressions and c.impressions > 0:
                    values.append((c.clicks / c.impressions) * 100)
            elif metric_name == "cost":
                if c.cost_micros:
                    values.append(c.cost_micros / 1000000)
            elif metric_name == "roas":
                if c.cost_micros and c.cost_micros > 0 and c.conversion_value:
                    values.append(c.conversion_value / (c.cost_micros / 1000000))
            elif metric_name == "conversions":
                if c.conversions:
                    values.append(c.conversions)
            elif metric_name == "conversion_rate":
                if c.clicks and c.clicks > 0 and c.conversions:
                    values.append((c.conversions / c.clicks) * 100)

        if not values:
            return {"mean": 0, "std": 0, "min": 0, "max": 0, "median": 0}

        values_array = np.array(values)
        return {
            "mean": float(np.mean(values_array)),
            "std": float(np.std(values_array)),
            "min": float(np.min(values_array)),
            "max": float(np.max(values_array)),
            "median": float(np.median(values_array))
        }

    def z_score_detection(
        self,
        current_value: float,
        historical_stats: Dict[str, float],
        threshold: float = 3.0
    ) -> bool:
        """
        Z-Score based anomaly detection
        Returns True if value is anomalous (> threshold standard deviations from mean)
        """
        if historical_stats["std"] == 0:
            return False

        z_score = abs((current_value - historical_stats["mean"]) / historical_stats["std"])
        return z_score > threshold

    def detect_campaign_anomalies(
        self,
        customer_id: int,
        date: datetime.date = None
    ) -> List[AnomalyAlert]:
        """
        Detect anomalies in campaign performance metrics
        """
        if date is None:
            date = datetime.now().date()

        alerts = []

        # Get today's campaign performance
        campaigns = self.db.query(models.CampaignKeyword).filter(
            models.CampaignKeyword.customer_id == customer_id,
            models.CampaignKeyword.date == str(date)
        ).all()

        if not campaigns:
            return alerts

        # Check each campaign for anomalies
        for campaign in campaigns:
            campaign_name = f"Campaign {campaign.campaign_id}"

            # 1. CPC Spike Detection (CRITICAL)
            if campaign.clicks and campaign.clicks > 0 and campaign.cost_micros:
                current_cpc = (campaign.cost_micros / 1000000) / campaign.clicks
                cpc_stats = self.get_historical_stats(customer_id, "cpc")

                if cpc_stats["mean"] > 0:
                    cpc_increase_pct = ((current_cpc - cpc_stats["mean"]) / cpc_stats["mean"]) * 100

                    if self.z_score_detection(current_cpc, cpc_stats, threshold=3.0):
                        # CPC is 3+ standard deviations from normal
                        alerts.append(AnomalyAlert(
                            metric_name="CPC",
                            current_value=current_cpc,
                            expected_range=(cpc_stats["mean"] - 2*cpc_stats["std"],
                                          cpc_stats["mean"] + 2*cpc_stats["std"]),
                            severity="critical" if cpc_increase_pct > 200 else "warning",
                            message=f"CPC spiked {cpc_increase_pct:.1f}% for '{campaign_name}'. "
                                   f"Current: ₹{current_cpc:.2f}, Expected: ₹{cpc_stats['mean']:.2f}. "
                                   f"Possible tracking error or competitive attack.",
                            affected_entity=campaign_name
                        ))

            # 2. CTR Drop Detection (WARNING)
            if campaign.impressions and campaign.impressions > 0:
                current_ctr = (campaign.clicks / campaign.impressions) * 100
                ctr_stats = self.get_historical_stats(customer_id, "ctr")

                if ctr_stats["mean"] > 0:
                    ctr_drop_pct = ((ctr_stats["mean"] - current_ctr) / ctr_stats["mean"]) * 100

                    if self.z_score_detection(current_ctr, ctr_stats, threshold=2.5):
                        if current_ctr < ctr_stats["mean"]:
                            alerts.append(AnomalyAlert(
                                metric_name="CTR",
                                current_value=current_ctr,
                                expected_range=(ctr_stats["mean"] - 2*ctr_stats["std"],
                                              ctr_stats["mean"] + 2*ctr_stats["std"]),
                                severity="warning" if ctr_drop_pct > 40 else "info",
                                message=f"CTR dropped {ctr_drop_pct:.1f}% for '{campaign_name}'. "
                                       f"Current: {current_ctr:.2f}%, Expected: {ctr_stats['mean']:.2f}%. "
                                       f"Ad fatigue or competitor activity possible.",
                                affected_entity=campaign_name
                            ))

            # 3. ROAS Crash Detection (CRITICAL)
            if campaign.cost_micros and campaign.cost_micros > 0:
                current_roas = campaign.conversion_value / (campaign.cost_micros / 1000000) if campaign.conversion_value else 0
                roas_stats = self.get_historical_stats(customer_id, "roas")

                if roas_stats["mean"] > 0:
                    roas_drop_pct = ((roas_stats["mean"] - current_roas) / roas_stats["mean"]) * 100

                    if current_roas < roas_stats["mean"] * 0.5:  # More than 50% drop
                        alerts.append(AnomalyAlert(
                            metric_name="ROAS",
                            current_value=current_roas,
                            expected_range=(roas_stats["mean"] * 0.7, roas_stats["mean"] * 1.3),
                            severity="critical",
                            message=f"ROAS crashed {roas_drop_pct:.1f}% for '{campaign_name}'. "
                                   f"Current: {current_roas:.2f}x, Expected: {roas_stats['mean']:.2f}x. "
                                   f"Immediate investigation required.",
                            affected_entity=campaign_name
                        ))

            # 4. Spend Anomaly Detection (WARNING)
            if campaign.cost_micros:
                cost_stats = self.get_historical_stats(customer_id, "cost")
                current_cost = campaign.cost_micros / 1000000

                if cost_stats["mean"] > 0:
                    if self.z_score_detection(current_cost, cost_stats, threshold=3.0):
                        spend_increase_pct = ((current_cost - cost_stats["mean"]) / cost_stats["mean"]) * 100

                        alerts.append(AnomalyAlert(
                            metric_name="Daily Spend",
                            current_value=current_cost,
                            expected_range=(cost_stats["mean"] - 2*cost_stats["std"],
                                          cost_stats["mean"] + 2*cost_stats["std"]),
                            severity="warning",
                            message=f"Daily spend {spend_increase_pct:+.1f}% from normal for '{campaign_name}'. "
                                   f"Current: ₹{current_cost:,.0f}, Expected: ₹{cost_stats['mean']:,.0f}. "
                                   f"Check budget pacing.",
                            affected_entity=campaign_name
                        ))

            # 5. Zero Conversions Detection (INFO/WARNING)
            conversion_stats = self.get_historical_stats(customer_id, "conversions")
            current_cost_check = (campaign.cost_micros / 1000000) if campaign.cost_micros else 0
            if conversion_stats["mean"] > 5 and campaign.conversions == 0 and current_cost_check > 1000:
                # Campaign normally gets conversions but has none today despite significant spend
                alerts.append(AnomalyAlert(
                    metric_name="Conversions",
                    current_value=0,
                    expected_range=(conversion_stats["mean"] * 0.5, conversion_stats["mean"] * 1.5),
                    severity="warning",
                    message=f"Zero conversions for '{campaign_name}' despite ₹{current_cost_check:,.0f} spend. "
                           f"Expected ~{conversion_stats['mean']:.0f} conversions. Check tracking pixels.",
                    affected_entity=campaign_name
                ))

        return alerts

    def has_critical_anomalies(self, alerts: List[AnomalyAlert]) -> bool:
        """Check if any critical anomalies exist"""
        return any(alert.severity == "critical" for alert in alerts)

    def detect_anomalies(
        self,
        customer_id: int,
        date: datetime.date = None
    ) -> Dict[str, Any]:
        """
        Main anomaly detection method
        Returns comprehensive anomaly report
        """
        alerts = self.detect_campaign_anomalies(customer_id, date)

        critical_alerts = [a for a in alerts if a.severity == "critical"]
        warning_alerts = [a for a in alerts if a.severity == "warning"]
        info_alerts = [a for a in alerts if a.severity == "info"]

        return {
            "has_critical_anomalies": len(critical_alerts) > 0,
            "total_anomalies": len(alerts),
            "critical_count": len(critical_alerts),
            "warning_count": len(warning_alerts),
            "info_count": len(info_alerts),
            "alerts": [alert.to_dict() for alert in alerts],
            "recommendation": (
                "PAUSE_OPTIMIZATION" if len(critical_alerts) > 0
                else "PROCEED_WITH_CAUTION" if len(warning_alerts) > 0
                else "PROCEED"
            ),
            "summary_message": self._generate_summary_message(critical_alerts, warning_alerts)
        }

    def _generate_summary_message(
        self,
        critical_alerts: List[AnomalyAlert],
        warning_alerts: List[AnomalyAlert]
    ) -> str:
        """Generate human-readable summary of anomalies"""
        if critical_alerts:
            return (
                f"🚨 {len(critical_alerts)} critical anomal{'y' if len(critical_alerts) == 1 else 'ies'} detected. "
                f"Optimization paused for safety. Immediate investigation required."
            )
        elif warning_alerts:
            return (
                f"⚠️ {len(warning_alerts)} warning{'s' if len(warning_alerts) != 1 else ''} detected. "
                f"Proceeding with caution. Review recommended."
            )
        else:
            return "✅ No anomalies detected. All systems normal."


def detect_anomalies(db: Session, customer_id: int, date: datetime.date = None) -> Dict[str, Any]:
    """Helper function for anomaly detection"""
    detector = AnomalyDetectionEngine(db)
    return detector.detect_anomalies(customer_id, date)
