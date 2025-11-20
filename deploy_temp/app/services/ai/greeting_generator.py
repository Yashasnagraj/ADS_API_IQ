"""
Personalized Greeting Generator
Generates context-aware greetings based on time of day and campaign performance
"""
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db import models


class GreetingGenerator:
    """Generate personalized greetings based on user and campaign status"""

    def __init__(self, db: Session):
        self.db = db

    def get_time_of_day_greeting(self) -> str:
        """Get greeting based on time of day"""
        hour = datetime.now().hour

        if 5 <= hour < 12:
            return "Good morning"
        elif 12 <= hour < 17:
            return "Good afternoon"
        elif 17 <= hour < 21:
            return "Good evening"
        else:
            return "Hey there"

    def analyze_campaign_health(self, customer_id: int) -> Dict[str, Any]:
        """
        Analyze overall campaign health for the customer
        Returns status and key metrics
        """
        # Get today's date
        today = datetime.now().date()

        # Get campaign performance data
        campaigns = self.db.query(models.CampaignKeyword).filter(
            models.CampaignKeyword.customer_id == customer_id,
            models.CampaignKeyword.date == str(today)
        ).all()

        if not campaigns:
            # Check yesterday if today has no data
            from datetime import timedelta
            yesterday = today - timedelta(days=1)
            campaigns = self.db.query(models.CampaignKeyword).filter(
                models.CampaignKeyword.customer_id == customer_id,
                models.CampaignKeyword.date == str(yesterday)
            ).all()

        if not campaigns:
            return {
                "status": "no_data",
                "total_campaigns": 0,
                "message": "I'm ready to help you set up your campaigns!"
            }

        # Calculate metrics (cost is stored in micros, divide by 1,000,000)
        total_campaigns = len(campaigns)
        total_spend = sum((c.cost_micros or 0) / 1000000 for c in campaigns)
        total_conversions = sum(c.conversions or 0 for c in campaigns)
        total_conv_value = sum(c.conversion_value or 0 for c in campaigns)

        # Calculate ROAS
        roas = (total_conv_value / total_spend) if total_spend > 0 else 0

        # Calculate average CTR
        total_clicks = sum(c.clicks or 0 for c in campaigns)
        total_impressions = sum(c.impressions or 0 for c in campaigns)
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0

        # Determine health status
        healthy_campaigns = sum(
            1 for c in campaigns
            if c.conversion_value and c.cost_micros and (c.conversion_value / (c.cost_micros / 1000000)) > 1
        )

        health_ratio = healthy_campaigns / total_campaigns if total_campaigns > 0 else 0

        if roas >= 2.0 and health_ratio >= 0.7:
            status = "excellent"
            message = "Your campaigns are crushing it today! 🚀"
        elif roas >= 1.0 and health_ratio >= 0.5:
            status = "good"
            message = "Things are looking solid! Keep up the good work."
        elif roas >= 0.5:
            status = "needs_attention"
            message = "We've got some optimization opportunities today. Let's work on them together!"
        else:
            status = "critical"
            message = "I've spotted some issues that need immediate attention. Don't worry, I'm here to help you fix them!"

        return {
            "status": status,
            "total_campaigns": total_campaigns,
            "healthy_campaigns": healthy_campaigns,
            "roas": round(roas, 2),
            "avg_ctr": round(avg_ctr, 2),
            "total_spend": round(total_spend, 2),
            "total_conversions": total_conversions,
            "total_revenue": round(total_conv_value, 2),
            "message": message
        }

    def generate_personalized_greeting(
        self,
        user_name: str,
        customer_id: int
    ) -> Dict[str, Any]:
        """
        Generate a complete personalized greeting with context

        Example outputs:
        - "Good morning, Yashas! ☀️ Your campaigns are crushing it today! You're going to have a great day."
        - "Hey Yashas! 👋 We've got some work to do today, but I'm here to assist you. Let's get it done!"
        """
        time_greeting = self.get_time_of_day_greeting()
        campaign_health = self.analyze_campaign_health(customer_id)

        # Build personalized message
        if campaign_health["status"] == "no_data":
            greeting = f"{time_greeting}, {user_name}! 👋"
            mood = "neutral"
            call_to_action = "What would you like to work on today?"
            tone_message = campaign_health["message"]

        elif campaign_health["status"] == "excellent":
            greeting = f"{time_greeting}, {user_name}! ☀️"
            mood = "positive"
            tone_message = campaign_health["message"]
            call_to_action = "You're going to have a great day! Want to see what's working best?"

        elif campaign_health["status"] == "good":
            greeting = f"{time_greeting}, {user_name}! 👋"
            mood = "positive"
            tone_message = campaign_health["message"]
            call_to_action = "Let's see if we can make it even better!"

        elif campaign_health["status"] == "needs_attention":
            greeting = f"{time_greeting}, {user_name}! 💼"
            mood = "focused"
            tone_message = campaign_health["message"]
            call_to_action = "I'm here to assist you. Let's get it done!"

        else:  # critical
            greeting = f"{time_greeting}, {user_name}! 🚨"
            mood = "alert"
            tone_message = campaign_health["message"]
            call_to_action = "I'm here to help you turn things around. Let's dive in!"

        return {
            "greeting": greeting,
            "mood": mood,
            "message": tone_message,
            "call_to_action": call_to_action,
            "metrics_summary": {
                "total_campaigns": campaign_health.get("total_campaigns", 0),
                "healthy_campaigns": campaign_health.get("healthy_campaigns", 0),
                "roas": campaign_health.get("roas", 0),
                "total_spend": campaign_health.get("total_spend", 0),
                "total_revenue": campaign_health.get("total_revenue", 0)
            },
            "status": campaign_health["status"]
        }


def get_greeting(db: Session, user_name: str, customer_id: int) -> Dict[str, Any]:
    """Helper function to get personalized greeting"""
    generator = GreetingGenerator(db)
    return generator.generate_personalized_greeting(user_name, customer_id)
