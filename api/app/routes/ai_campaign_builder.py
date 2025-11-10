"""
AI Campaign Builder API Endpoints
Assists in creating optimized campaign structures
"""
from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class CampaignBuildRequest(BaseModel):
    customer_id: int
    business_type: str
    goal: str
    budget: float
    target_location: str
    product_service: str
    use_best_practices: bool = True

@router.get("/campaign-builder/templates")
async def get_campaign_templates():
    """Get pre-built campaign templates"""

    templates = [
        {
            "id": "ecommerce_sales",
            "name": "E-commerce Sales Campaign",
            "description": "Optimized for online stores driving product sales",
            "structure": {
                "campaigns": 2,
                "ad_groups_per_campaign": 5,
                "keywords_per_ad_group": 15,
                "ads_per_ad_group": 3
            },
            "budget_range": "₹500-5000/day",
            "best_for": ["Online stores", "Product sales", "Shopping campaigns"],
            "features": [
                "Product-focused ad groups",
                "Shopping feed integration",
                "Dynamic remarketing",
                "Conversion tracking"
            ]
        },
        {
            "id": "lead_generation",
            "name": "Lead Generation Campaign",
            "description": "Capture qualified leads with form submissions",
            "structure": {
                "campaigns": 1,
                "ad_groups_per_campaign": 8,
                "keywords_per_ad_group": 12,
                "ads_per_ad_group": 3
            },
            "budget_range": "₹300-3000/day",
            "best_for": ["B2B services", "Consultations", "Free trials"],
            "features": [
                "Lead form extensions",
                "Call-to-action focus",
                "Quality score optimization",
                "Remarketing lists"
            ]
        },
        {
            "id": "brand_awareness",
            "name": "Brand Awareness Campaign",
            "description": "Maximize reach and brand visibility",
            "structure": {
                "campaigns": 2,
                "ad_groups_per_campaign": 4,
                "keywords_per_ad_group": 20,
                "ads_per_ad_group": 5
            },
            "budget_range": "₹1000-10000/day",
            "best_for": ["New product launch", "Brand building", "Market expansion"],
            "features": [
                "Display network campaigns",
                "Video campaigns",
                "Broad reach targeting",
                "Frequency capping"
            ]
        },
        {
            "id": "local_business",
            "name": "Local Business Campaign",
            "description": "Drive foot traffic to physical locations",
            "structure": {
                "campaigns": 1,
                "ad_groups_per_campaign": 6,
                "keywords_per_ad_group": 10,
                "ads_per_ad_group": 3
            },
            "budget_range": "₹200-2000/day",
            "best_for": ["Restaurants", "Retail stores", "Local services"],
            "features": [
                "Location extensions",
                "Call extensions",
                "Local inventory ads",
                "Store visit tracking"
            ]
        }
    ]

    return {
        "success": True,
        "templates": templates
    }

@router.post("/campaign-builder/generate")
async def generate_campaign_structure(request: CampaignBuildRequest):
    """Generate AI-powered campaign structure"""

    # Generate campaign structure based on business type
    campaign_structure = {
        "campaign_name": f"{request.product_service} - {request.goal.title()} Campaign",
        "budget": {
            "daily": request.budget,
            "monthly": request.budget * 30,
            "allocation": "Even distribution recommended"
        },
        "targeting": {
            "location": request.target_location,
            "language": "English",
            "network": "Search + Display Select"
        },
        "ad_groups": [
            {
                "name": f"{request.product_service} - Best Sellers",
                "bid_strategy": "Maximize conversions",
                "keywords": [f"best {request.product_service}", f"top {request.product_service}"],
                "match_types": ["broad", "phrase", "exact"]
            },
            {
                "name": f"{request.product_service} - Deals & Offers",
                "bid_strategy": "Target ROAS",
                "keywords": [f"{request.product_service} sale", f"{request.product_service} discount"],
                "match_types": ["phrase", "exact"]
            }
        ]
    }

    predictions = {
        "estimated_daily_clicks": round(request.budget / 15, 0),
        "estimated_daily_impressions": round((request.budget / 15) * 50, 0),
        "estimated_conversions": round((request.budget / 15) * 0.03 * 30, 1),
        "estimated_cpa": round(request.budget / (request.budget / 15 * 0.03), 2),
        "confidence": 75
    }

    best_practices = [
        "Use responsive search ads with 3+ headlines and 2+ descriptions",
        "Add sitelink extensions for better visibility",
        "Enable conversion tracking from day 1",
        "Set up negative keyword lists",
        "Create separate campaigns for brand and non-brand terms"
    ]

    return {
        "success": True,
        "campaign_structure": campaign_structure,
        "best_practices": best_practices if request.use_best_practices else [],
        "predictions": predictions,
        "historical_insights": {
            "top_keywords": [],
            "message": "No historical data available - starting fresh!"
        }
    }

@router.get("/campaign-builder/recommendations")
async def get_campaign_recommendations(customer_id: int):
    """Get campaign optimization recommendations"""

    return {
        "success": True,
        "total_campaigns": 0,
        "recommendations": [
            "Start with 2-3 campaigns focusing on your best products/services",
            "Use responsive search ads for better performance",
            "Set daily budgets conservatively and scale up based on data",
            "Enable conversion tracking before launching"
        ]
    }
