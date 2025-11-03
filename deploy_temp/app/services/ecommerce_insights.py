"""
E-commerce Insights Service
AI-powered insights generation for e-commerce dashboard
"""
from typing import List, Dict, Any, Optional
from datetime import datetime


class EcommerceInsightsService:
    """Generate AI insights for e-commerce metrics"""

    @staticmethod
    def generate_funnel_insights(stages: List[Dict[str, Any]]) -> List[str]:
        """
        Analyze funnel drop-offs and generate insights

        Args:
            stages: List of funnel stages with dropoff percentages

        Returns:
            List of insights for each stage
        """
        insights = []

        for i, stage in enumerate(stages):
            if i == 0:
                insights.append(f"{stage['value']:,} visitors entered the funnel")
                continue

            dropoff = stage.get('dropoff', 0)

            # High drop-off (>40%)
            if dropoff > 40:
                if stage['stage'] == 'Add to Cart':
                    insights.append(
                        f"High {dropoff:.1f}% drop between Product Views → Cart. "
                        "Consider: improving product images, adding reviews, or offering discounts."
                    )
                elif stage['stage'] == 'Checkout':
                    insights.append(
                        f"Critical {dropoff:.1f}% cart abandonment. "
                        "Likely causes: shipping costs, slow loading, or complex checkout flow."
                    )
                elif stage['stage'] == 'Purchase':
                    insights.append(
                        f"Very high {dropoff:.1f}% drop at final step. "
                        "Check: payment options, security badges, or unexpected fees."
                    )
                else:
                    insights.append(f"{dropoff:.1f}% drop-off at {stage['stage']}")

            # Moderate drop-off (20-40%)
            elif dropoff > 20:
                insights.append(
                    f"Moderate {dropoff:.1f}% drop at {stage['stage']}. "
                    "Monitor and optimize user experience."
                )

            # Low drop-off (<20%)
            else:
                insights.append(
                    f"Healthy {dropoff:.1f}% drop-off at {stage['stage']}. "
                    "Performance is good."
                )

        return insights

    @staticmethod
    def generate_channel_insight(channels: List[Dict[str, Any]]) -> str:
        """
        Analyze channel performance and generate insights

        Args:
            channels: List of channel metrics with ROAS

        Returns:
            AI-generated insight string
        """
        if not channels:
            return "No channel data available"

        # Sort by ROAS
        sorted_channels = sorted(channels, key=lambda x: x.get('roas', 0), reverse=True)

        best_channel = sorted_channels[0]
        worst_channel = sorted_channels[-1]

        total_spend = sum(ch.get('spend', 0) for ch in channels)
        total_revenue = sum(ch.get('revenue', 0) for ch in channels)
        overall_roas = total_revenue / total_spend if total_spend > 0 else 0

        insight_parts = []

        # Best performer
        if best_channel.get('roas', 0) > 2:
            insight_parts.append(
                f"{best_channel['channel']} delivers exceptional {best_channel['roas']:.1f}x ROAS"
            )
        else:
            insight_parts.append(
                f"{best_channel['channel']} is top performer with {best_channel['roas']:.1f}x ROAS"
            )

        # Worst performer
        if worst_channel.get('roas', 0) < 1:
            insight_parts.append(
                f"{worst_channel['channel']} is losing money at {worst_channel['roas']:.1f}x ROAS - consider pausing or optimizing"
            )
        elif worst_channel.get('roas', 0) < overall_roas * 0.7:
            insight_parts.append(
                f"{worst_channel['channel']} underperforms at {worst_channel['roas']:.1f}x ROAS"
            )

        # Overall performance
        if overall_roas > 3:
            insight_parts.append(f"Overall ROAS of {overall_roas:.1f}x is excellent")
        elif overall_roas > 2:
            insight_parts.append(f"Overall ROAS of {overall_roas:.1f}x is healthy")
        elif overall_roas > 1:
            insight_parts.append(f"Overall ROAS of {overall_roas:.1f}x is profitable but can improve")
        else:
            insight_parts.append(f"Overall ROAS of {overall_roas:.1f}x is below breakeven - urgent optimization needed")

        return ". ".join(insight_parts) + "."

    @staticmethod
    def generate_product_insight(
        products: List[Dict[str, Any]],
        top_products: List[str],
        bottom_products: List[str]
    ) -> str:
        """
        Analyze product performance and generate insights

        Args:
            products: List of product metrics
            top_products: Top 3 product names
            bottom_products: Bottom 3 product names

        Returns:
            AI-generated insight string
        """
        if not products:
            return "No product data available"

        total_revenue = sum(p.get('revenue', 0) for p in products)
        top_3_revenue = sum(
            p.get('revenue', 0) for p in products
            if p.get('product_name') in top_products
        )

        top_contribution = (top_3_revenue / total_revenue * 100) if total_revenue > 0 else 0

        # Find products with high refund rate
        high_refund_products = [
            p for p in products
            if p.get('refund_rate', 0) > 10
        ]

        insight_parts = []

        # Top performers
        insight_parts.append(
            f"Top 3 products ({', '.join(top_products[:2])}...) contribute "
            f"{top_contribution:.0f}% of total revenue"
        )

        # Refund issues
        if high_refund_products:
            refund_product_names = [p['product_name'] for p in high_refund_products[:2]]
            insight_parts.append(
                f"Quality alert: {', '.join(refund_product_names)} have elevated refund rates (>10%)"
            )

        # Bottom performers
        if bottom_products:
            insight_parts.append(
                f"Bottom performers ({', '.join(bottom_products[:2])}...) need review or removal"
            )

        return ". ".join(insight_parts) + "."

    @staticmethod
    def generate_segment_insight(segments: List[Dict[str, Any]]) -> str:
        """
        Analyze customer segmentation and generate insights

        Args:
            segments: List of customer segment metrics

        Returns:
            AI-generated insight string
        """
        if not segments:
            return "No segmentation data available"

        # Find returning customer segment
        returning_segment = next(
            (s for s in segments if s.get('segment') == 'RETURNING'),
            None
        )

        new_segment = next(
            (s for s in segments if s.get('segment') == 'NEW'),
            None
        )

        if not returning_segment or not new_segment:
            return "Insufficient segment data"

        returning_pct = returning_segment.get('percentage', 0)
        returning_revenue_pct = returning_segment.get('revenue_percentage', 0)
        returning_aov = returning_segment.get('avg_order_value', 0)
        new_aov = new_segment.get('avg_order_value', 0)

        insight_parts = []

        # Revenue concentration
        if returning_revenue_pct > 60:
            insight_parts.append(
                f"Returning customers ({returning_pct:.0f}% of users) drive "
                f"{returning_revenue_pct:.0f}% of revenue - focus on retention campaigns"
            )
        elif returning_revenue_pct < 30:
            insight_parts.append(
                f"New customers dominate revenue - improve retention to increase LTV"
            )
        else:
            insight_parts.append(
                f"Balanced revenue split: {returning_revenue_pct:.0f}% from returning users"
            )

        # AOV comparison
        if returning_aov > new_aov * 1.3:
            insight_parts.append(
                f"Returning customers spend {(returning_aov/new_aov - 1)*100:.0f}% more per order"
            )

        return ". ".join(insight_parts) + "."

    @staticmethod
    def detect_anomalies(
        current_metrics: Dict[str, float],
        historical_avg: Dict[str, float],
        threshold: float = 0.15
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in e-commerce metrics

        Args:
            current_metrics: Current metric values
            historical_avg: Historical average values
            threshold: Deviation threshold (default 15%)

        Returns:
            List of detected anomalies
        """
        anomalies = []

        metric_names = {
            'mobile_cvr': 'Mobile Conversion Rate',
            'desktop_cvr': 'Desktop Conversion Rate',
            'checkout_abandonment': 'Checkout Abandonment',
            'avg_session_duration': 'Average Session Duration',
            'bounce_rate': 'Bounce Rate'
        }

        for metric, current_value in current_metrics.items():
            if metric not in historical_avg:
                continue

            expected = historical_avg[metric]
            if expected == 0:
                continue

            deviation = abs((current_value - expected) / expected)

            if deviation > threshold:
                # Determine severity
                if deviation > 0.3:
                    severity = 'CRITICAL'
                elif deviation > 0.2:
                    severity = 'HIGH'
                else:
                    severity = 'MEDIUM'

                # Generate recommendation
                if current_value < expected:
                    direction = 'dropped'
                    if 'cvr' in metric.lower():
                        recommendation = f"Optimize checkout UX and payment options"
                    elif 'duration' in metric.lower():
                        recommendation = f"Improve content engagement and site speed"
                    else:
                        recommendation = f"Investigate and address declining {metric_names.get(metric, metric)}"
                else:
                    direction = 'increased'
                    if 'abandonment' in metric.lower() or 'bounce' in metric.lower():
                        recommendation = f"Urgent: Fix issues causing elevated {metric_names.get(metric, metric)}"
                    else:
                        recommendation = f"Monitor unusually high {metric_names.get(metric, metric)}"

                anomalies.append({
                    'severity': severity,
                    'title': f"{metric_names.get(metric, metric)} Anomaly Detected",
                    'description': f"{metric_names.get(metric, metric)} {direction} {deviation*100:.1f}% from expected value",
                    'metric': metric,
                    'value': current_value,
                    'expected_value': expected,
                    'deviation_percentage': deviation * 100,
                    'recommendation': recommendation,
                    'detected_at': datetime.now()
                })

        return sorted(anomalies, key=lambda x: {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(x['severity'], 0), reverse=True)
