from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class ResultAggregator:
    def __init__(self):
        self.aggregation_methods = {
            "sum": self._aggregate_sum,
            "average": self._aggregate_average,
            "median": self._aggregate_median,
            "max": self._aggregate_max,
            "min": self._aggregate_min,
            "merge": self._aggregate_merge,
            "concat": self._aggregate_concat,
            "weighted_average": self._aggregate_weighted_average
        }

    def aggregate_results(self, results: List[Dict[str, Any]], method: str = "merge") -> Dict[str, Any]:
        if not results:
            return {}

        if method not in self.aggregation_methods:
            logger.warning(f"Unknown aggregation method: {method}. Using 'merge' instead.")
            method = "merge"

        try:
            aggregated = self.aggregation_methods[method](results)
            aggregated["aggregation_method"] = method
            aggregated["aggregation_timestamp"] = datetime.now().isoformat()
            aggregated["source_count"] = len(results)
            return aggregated
        except Exception as e:
            logger.error(f"Error aggregating results: {str(e)}")
            return {
                "error": str(e),
                "raw_results": results
            }

    def _aggregate_sum(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        aggregated = defaultdict(float)

        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    aggregated[key] += value
                elif isinstance(value, dict):
                    if key not in aggregated:
                        aggregated[key] = defaultdict(float)
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, (int, float)):
                            aggregated[key][sub_key] += sub_value

        return dict(aggregated)

    def _aggregate_average(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        summed = self._aggregate_sum(results)
        count = len(results)

        averaged = {}
        for key, value in summed.items():
            if isinstance(value, (int, float)):
                averaged[key] = value / count
            elif isinstance(value, dict):
                averaged[key] = {
                    sub_key: sub_value / count
                    for sub_key, sub_value in value.items()
                }

        return averaged

    def _aggregate_median(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        values_by_key = defaultdict(list)

        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    values_by_key[key].append(value)

        medians = {}
        for key, values in values_by_key.items():
            if values:
                medians[key] = float(np.median(values))

        return medians

    def _aggregate_max(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        max_values = {}

        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    if key not in max_values or value > max_values[key]:
                        max_values[key] = value

        return max_values

    def _aggregate_min(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        min_values = {}

        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    if key not in min_values or value < min_values[key]:
                        min_values[key] = value

        return min_values

    def _aggregate_merge(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        merged = {}

        for result in results:
            for key, value in result.items():
                if key not in merged:
                    merged[key] = value
                elif isinstance(value, dict) and isinstance(merged[key], dict):
                    merged[key] = {**merged[key], **value}
                elif isinstance(value, list) and isinstance(merged[key], list):
                    merged[key].extend(value)
                elif key == "error" and value:
                    if "errors" not in merged:
                        merged["errors"] = []
                    merged["errors"].append(value)

        return merged

    def _aggregate_concat(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        concatenated = defaultdict(list)

        for result in results:
            for key, value in result.items():
                if isinstance(value, list):
                    concatenated[key].extend(value)
                else:
                    concatenated[key].append(value)

        return dict(concatenated)

    def _aggregate_weighted_average(self, results: List[Dict[str, Any]], weights: List[float] = None) -> Dict[str, Any]:
        if weights is None:
            weights = [1.0] * len(results)

        if len(weights) != len(results):
            raise ValueError("Number of weights must match number of results")

        total_weight = sum(weights)
        weighted_sum = defaultdict(float)

        for result, weight in zip(results, weights):
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    weighted_sum[key] += value * weight

        weighted_average = {
            key: value / total_weight
            for key, value in weighted_sum.items()
        }

        return weighted_average

    def aggregate_campaign_metrics(self, campaign_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_metrics = {
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "cost": 0,
            "campaign_count": 0,
            "active_campaigns": 0
        }

        campaign_details = []

        for result in campaign_results:
            if "campaigns" in result:
                campaigns = result["campaigns"]
                if isinstance(campaigns, list):
                    for campaign in campaigns:
                        metrics = campaign.get("metrics", {})
                        total_metrics["impressions"] += metrics.get("impressions", 0)
                        total_metrics["clicks"] += metrics.get("clicks", 0)
                        total_metrics["conversions"] += metrics.get("conversions", 0)
                        total_metrics["cost"] += metrics.get("cost_micros", 0) / 1000000

                        total_metrics["campaign_count"] += 1
                        if campaign.get("status") == "ENABLED":
                            total_metrics["active_campaigns"] += 1

                        campaign_details.append({
                            "name": campaign.get("name"),
                            "id": campaign.get("id"),
                            "performance": {
                                "ctr": (metrics.get("clicks", 0) / metrics.get("impressions", 1)) * 100
                                if metrics.get("impressions", 0) > 0 else 0,
                                "conversion_rate": (metrics.get("conversions", 0) / metrics.get("clicks", 1)) * 100
                                if metrics.get("clicks", 0) > 0 else 0,
                                "cpc": (metrics.get("cost_micros", 0) / 1000000) / metrics.get("clicks", 1)
                                if metrics.get("clicks", 0) > 0 else 0
                            }
                        })

        calculated_metrics = {}
        if total_metrics["impressions"] > 0:
            calculated_metrics["overall_ctr"] = (total_metrics["clicks"] / total_metrics["impressions"]) * 100

        if total_metrics["clicks"] > 0:
            calculated_metrics["overall_conversion_rate"] = (total_metrics["conversions"] / total_metrics["clicks"]) * 100
            calculated_metrics["overall_cpc"] = total_metrics["cost"] / total_metrics["clicks"]

        if total_metrics["conversions"] > 0:
            calculated_metrics["cost_per_conversion"] = total_metrics["cost"] / total_metrics["conversions"]

        return {
            "total_metrics": total_metrics,
            "calculated_metrics": calculated_metrics,
            "campaign_details": campaign_details,
            "aggregation_timestamp": datetime.now().isoformat()
        }

    def aggregate_insights(self, insight_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        all_insights = {
            "performance_insights": [],
            "anomalies": [],
            "trends": [],
            "recommendations": [],
            "risk_factors": []
        }

        insight_summary = {
            "total_anomalies": 0,
            "critical_issues": 0,
            "improvement_opportunities": 0
        }

        for result in insight_results:
            if "anomalies" in result:
                anomalies = result["anomalies"]
                if isinstance(anomalies, list):
                    all_insights["anomalies"].extend(anomalies)
                    insight_summary["total_anomalies"] += len(anomalies)

            if "trends" in result:
                trends = result["trends"]
                if isinstance(trends, list):
                    all_insights["trends"].extend(trends)

            if "performance" in result:
                performance = result["performance"]
                if isinstance(performance, dict):
                    all_insights["performance_insights"].append(performance)

            if "recommendations" in result:
                recommendations = result["recommendations"]
                if isinstance(recommendations, list):
                    all_insights["recommendations"].extend(recommendations)
                    insight_summary["improvement_opportunities"] += len(recommendations)

        all_insights["anomalies"] = self._deduplicate_insights(all_insights["anomalies"])
        all_insights["trends"] = self._deduplicate_insights(all_insights["trends"])
        all_insights["recommendations"] = self._prioritize_recommendations(all_insights["recommendations"])

        return {
            "insights": all_insights,
            "summary": insight_summary,
            "aggregation_timestamp": datetime.now().isoformat()
        }

    def _deduplicate_insights(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique_insights = []

        for insight in insights:
            insight_key = str(insight.get("type", "")) + str(insight.get("metric", ""))
            if insight_key not in seen:
                seen.add(insight_key)
                unique_insights.append(insight)

        return unique_insights

    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        priority_map = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        }

        recommendations.sort(key=lambda x: priority_map.get(x.get("priority", "low"), 5))

        return recommendations[:10]

    def create_executive_summary(self, aggregated_results: Dict[str, Any]) -> Dict[str, Any]:
        summary = {
            "overview": {},
            "key_metrics": {},
            "top_insights": [],
            "critical_actions": [],
            "performance_score": 0
        }

        if "campaign_data" in aggregated_results:
            campaign_data = aggregated_results["campaign_data"]
            if isinstance(campaign_data, dict) and "total_metrics" in campaign_data:
                metrics = campaign_data["total_metrics"]
                summary["key_metrics"] = {
                    "total_spend": metrics.get("cost", 0),
                    "total_conversions": metrics.get("conversions", 0),
                    "roi": self._calculate_roi(metrics)
                }

        if "insights" in aggregated_results:
            insights = aggregated_results["insights"]
            if isinstance(insights, dict):
                if "anomalies" in insights and insights["anomalies"]:
                    summary["top_insights"].extend(insights["anomalies"][:3])
                if "recommendations" in insights and insights["recommendations"]:
                    summary["critical_actions"].extend(insights["recommendations"][:3])

        summary["performance_score"] = self._calculate_performance_score(aggregated_results)

        return summary

    def _calculate_roi(self, metrics: Dict[str, Any]) -> float:
        cost = metrics.get("cost", 0)
        conversion_value = metrics.get("conversions", 0) * 50
        if cost > 0:
            return ((conversion_value - cost) / cost) * 100
        return 0

    def _calculate_performance_score(self, results: Dict[str, Any]) -> int:
        score = 50

        if "campaign_data" in results:
            campaign_data = results.get("campaign_data", {})
            if isinstance(campaign_data, dict):
                calculated = campaign_data.get("calculated_metrics", {})

                if calculated.get("overall_ctr", 0) > 2:
                    score += 10
                if calculated.get("overall_conversion_rate", 0) > 3:
                    score += 15
                if calculated.get("cost_per_conversion", float('inf')) < 50:
                    score += 10

        if "insights" in results:
            insights = results.get("insights", {})
            if isinstance(insights, dict):
                summary = insights.get("summary", {})
                if summary.get("total_anomalies", 0) == 0:
                    score += 10
                if summary.get("critical_issues", 0) == 0:
                    score += 5

        return min(100, max(0, score))