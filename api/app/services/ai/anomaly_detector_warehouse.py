"""
Warehouse-compatible Anomaly Detection
Queries from warehouse star schema
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np


def detect_anomalies_from_warehouse(
    db: Session,
    customer_id: int,
    date: datetime = None
) -> Dict[str, Any]:
    """
    Detect anomalies in campaign performance using warehouse data
    """
    if date is None:
        date = datetime.now().date()

    # Get campaign performance metrics from warehouse
    query = text("""
        SELECT
            c.campaign_id,
            c.campaign_name,
            SUM(f.clicks) as clicks,
            SUM(f.impressions) as impressions,
            SUM(f.spend_micros) / 1000000.0 as cost,
            SUM(f.conversions) as conversions,
            SUM(f.conversion_value_micros) / 1000000.0 as conversion_value,
            CASE WHEN SUM(f.clicks) > 0
                THEN (SUM(f.spend_micros) / 1000000.0) / SUM(f.clicks)
                ELSE 0 END as cpc,
            CASE WHEN SUM(f.impressions) > 0
                THEN (SUM(f.clicks) * 100.0) / SUM(f.impressions)
                ELSE 0 END as ctr,
            CASE WHEN SUM(f.spend_micros) > 0
                THEN (SUM(f.conversion_value_micros) / 1000000.0) / (SUM(f.spend_micros) / 1000000.0)
                ELSE 0 END as roas
        FROM dim_google_ads_campaign c
        LEFT JOIN fact_campaign_performance_daily f
            ON c.google_campaign_id = f.google_campaign_id
            AND c.customer_id = f.customer_id
        WHERE c.customer_id = :customer_id
        GROUP BY c.campaign_id, c.campaign_name
        HAVING clicks > 0
    """)

    result = db.execute(query, {"customer_id": customer_id})
    campaigns = result.fetchall()

    if not campaigns:
        return {
            "customer_id": customer_id,
            "date": str(date),
            "total_anomalies": 0,
            "critical_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "alerts": [],
            "summary": {
                "campaigns_affected": 0,
                "metrics_flagged": [],
                "most_common_issue": "No data available"
            }
        }

    # Calculate metrics and detect anomalies
    alerts = []
    campaigns_with_anomalies = set()
    metrics_flagged = set()

    # Industry benchmarks
    benchmarks = {
        "cpc": {"min": 0.50, "max": 5.00, "ideal": 1.50},  # CPC in dollars
        "ctr": {"min": 1.0, "max": 10.0, "ideal": 3.0},    # CTR in %
        "roas": {"min": 1.5, "max": 10.0, "ideal": 3.0},   # ROAS multiplier
        "conversion_rate": {"min": 1.0, "max": 15.0, "ideal": 5.0}  # % of clicks
    }

    for camp in campaigns:
        campaign_id, campaign_name, clicks, impressions, cost, conversions, conversion_value, cpc, ctr, roas = camp

        # Check CPC anomalies
        if cpc > 0:
            if cpc > benchmarks["cpc"]["max"]:
                alerts.append({
                    "campaign_id": campaign_id,
                    "campaign_name": campaign_name,
                    "metric_name": "CPC",
                    "severity": "critical",
                    "message": f"CPC spike detected: ${cpc:.2f} (expected: $0.50-$5.00)",
                    "current_value": float(cpc),
                    "expected_value": benchmarks["cpc"]["ideal"],
                    "expected_range": f"${benchmarks['cpc']['min']:.2f}-${benchmarks['cpc']['max']:.2f}",
                    "deviation_percentage": float((cpc - benchmarks["cpc"]["ideal"]) / benchmarks["cpc"]["ideal"] * 100),
                    "detected_at": datetime.now().isoformat()
                })
                campaigns_with_anomalies.add(campaign_id)
                metrics_flagged.add("CPC")
            elif cpc > benchmarks["cpc"]["ideal"] * 1.5:
                alerts.append({
                    "campaign_id": campaign_id,
                    "campaign_name": campaign_name,
                    "metric_name": "CPC",
                    "severity": "warning",
                    "message": f"CPC above ideal: ${cpc:.2f} (target: ${benchmarks['cpc']['ideal']:.2f})",
                    "current_value": float(cpc),
                    "expected_value": benchmarks["cpc"]["ideal"],
                    "expected_range": f"${benchmarks['cpc']['min']:.2f}-${benchmarks['cpc']['max']:.2f}",
                    "deviation_percentage": float((cpc - benchmarks["cpc"]["ideal"]) / benchmarks["cpc"]["ideal"] * 100),
                    "detected_at": datetime.now().isoformat()
                })
                campaigns_with_anomalies.add(campaign_id)
                metrics_flagged.add("CPC")

        # Check CTR anomalies
        if ctr > 0:
            if ctr < benchmarks["ctr"]["min"]:
                alerts.append({
                    "campaign_id": campaign_id,
                    "campaign_name": campaign_name,
                    "metric_name": "CTR",
                    "severity": "critical",
                    "message": f"CTR drop detected: {ctr:.2f}% (expected: >{benchmarks['ctr']['min']}%)",
                    "current_value": float(ctr),
                    "expected_value": benchmarks["ctr"]["ideal"],
                    "expected_range": f"{benchmarks['ctr']['min']:.1f}%-{benchmarks['ctr']['max']:.1f}%",
                    "deviation_percentage": float((ctr - benchmarks["ctr"]["ideal"]) / benchmarks["ctr"]["ideal"] * 100),
                    "detected_at": datetime.now().isoformat()
                })
                campaigns_with_anomalies.add(campaign_id)
                metrics_flagged.add("CTR")
            elif ctr < benchmarks["ctr"]["ideal"] * 0.7:
                alerts.append({
                    "campaign_id": campaign_id,
                    "campaign_name": campaign_name,
                    "metric_name": "CTR",
                    "severity": "warning",
                    "message": f"CTR below ideal: {ctr:.2f}% (target: {benchmarks['ctr']['ideal']:.1f}%)",
                    "current_value": float(ctr),
                    "expected_value": benchmarks["ctr"]["ideal"],
                    "expected_range": f"{benchmarks['ctr']['min']:.1f}%-{benchmarks['ctr']['max']:.1f}%",
                    "deviation_percentage": float((ctr - benchmarks["ctr"]["ideal"]) / benchmarks["ctr"]["ideal"] * 100),
                    "detected_at": datetime.now().isoformat()
                })
                campaigns_with_anomalies.add(campaign_id)
                metrics_flagged.add("CTR")

        # Check ROAS anomalies
        if roas > 0:
            if roas < benchmarks["roas"]["min"]:
                alerts.append({
                    "campaign_id": campaign_id,
                    "campaign_name": campaign_name,
                    "metric_name": "ROAS",
                    "severity": "critical",
                    "message": f"ROAS crash detected: {roas:.2f}x (expected: >{benchmarks['roas']['min']}x)",
                    "current_value": float(roas),
                    "expected_value": benchmarks["roas"]["ideal"],
                    "expected_range": f"{benchmarks['roas']['min']:.1f}x-{benchmarks['roas']['max']:.1f}x",
                    "deviation_percentage": float((roas - benchmarks["roas"]["ideal"]) / benchmarks["roas"]["ideal"] * 100),
                    "detected_at": datetime.now().isoformat()
                })
                campaigns_with_anomalies.add(campaign_id)
                metrics_flagged.add("ROAS")
            elif roas < benchmarks["roas"]["ideal"] * 0.7:
                alerts.append({
                    "campaign_id": campaign_id,
                    "campaign_name": campaign_name,
                    "metric_name": "ROAS",
                    "severity": "warning",
                    "message": f"ROAS below target: {roas:.2f}x (target: {benchmarks['roas']['ideal']:.1f}x)",
                    "current_value": float(roas),
                    "expected_value": benchmarks["roas"]["ideal"],
                    "expected_range": f"{benchmarks['roas']['min']:.1f}x-{benchmarks['roas']['max']:.1f}x",
                    "deviation_percentage": float((roas - benchmarks["roas"]["ideal"]) / benchmarks["roas"]["ideal"] * 100),
                    "detected_at": datetime.now().isoformat()
                })
                campaigns_with_anomalies.add(campaign_id)
                metrics_flagged.add("ROAS")

        # Check for zero conversions
        if clicks > 100 and conversions == 0:
            alerts.append({
                "campaign_id": campaign_id,
                "campaign_name": campaign_name,
                "metric_name": "Conversions",
                "severity": "critical",
                "message": f"Zero conversions with {int(clicks)} clicks - possible tracking issue",
                "current_value": 0.0,
                "expected_value": float(clicks * 0.03),  # Expect ~3% conversion
                "expected_range": f">0 (expect ~{int(clicks * 0.03)} conversions)",
                "deviation_percentage": -100.0,
                "detected_at": datetime.now().isoformat()
            })
            campaigns_with_anomalies.add(campaign_id)
            metrics_flagged.add("Conversions")

    # Count by severity
    critical_count = len([a for a in alerts if a["severity"] == "critical"])
    warning_count = len([a for a in alerts if a["severity"] == "warning"])
    info_count = len([a for a in alerts if a["severity"] == "info"])

    # Determine most common issue
    if metrics_flagged:
        metric_counts = {}
        for metric in metrics_flagged:
            metric_counts[metric] = len([a for a in alerts if a["metric_name"] == metric])
        most_common_issue = max(metric_counts, key=metric_counts.get)
    else:
        most_common_issue = "No anomalies detected"

    return {
        "customer_id": customer_id,
        "date": str(date),
        "total_anomalies": len(alerts),
        "critical_count": critical_count,
        "warning_count": warning_count,
        "info_count": info_count,
        "alerts": alerts,
        "summary": {
            "campaigns_affected": len(campaigns_with_anomalies),
            "metrics_flagged": list(metrics_flagged),
            "most_common_issue": most_common_issue
        }
    }
