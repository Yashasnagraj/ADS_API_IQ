"""
AI Ad Creator API Routes
Generate and launch Meta ads using AI
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import json
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import CustomerProfile, Customer
from app.services.ai.text_generator import AITextGenerator
from app.services.ai.image_generator import AIImageGenerator
from app.services.meta_ads_service import get_meta_ads_service

logger = logging.getLogger(__name__)

router = APIRouter()

# ==========================================
# Request/Response Models
# ==========================================

class BrandProfileRequest(BaseModel):
    """Request to create/update brand profile"""
    customer_id: int
    company_name: str
    industry: Optional[str] = None
    website_url: Optional[str] = None
    brand_voice: str = "professional"
    tone_attributes: List[str] = []
    key_values: List[str] = []
    unique_selling_points: List[str] = []
    target_audience_description: str
    audience_demographics: Dict[str, Any] = {}
    audience_pain_points: List[str] = []
    product_category: Optional[str] = None
    price_range: str = "mid-range"
    primary_benefits: List[str] = []
    preferred_ctas: List[str] = ["Shop Now", "Learn More"]
    prohibited_words: List[str] = []
    sample_headlines: List[str] = []
    sample_descriptions: List[str] = []
    meta_page_id: Optional[str] = None
    meta_pixel_id: Optional[str] = None
    logo_url: Optional[str] = None
    brand_colors: List[str] = []
    image_style_preference: str = "professional"


class AdGenerationRequest(BaseModel):
    """Request to generate ad variations"""
    customer_id: int
    product_name: str
    product_description: str
    campaign_goal: str = "sales"  # sales, leads, traffic, awareness
    landing_url: str
    daily_budget_usd: float = 10.0
    num_variations: int = Field(5, ge=1, le=10)
    generate_images: bool = True


class AdVariationResponse(BaseModel):
    """Single ad variation"""
    variation_id: int
    primary_text: str
    headline: str
    description: str
    cta: str
    image_url: Optional[str] = None
    confidence_score: float
    focus_usp: str


class AdLaunchRequest(BaseModel):
    """Request to launch selected ad to Meta"""
    customer_id: int
    meta_account_id: str  # format: act_123456789
    campaign_name: str
    product_name: str
    landing_url: str
    daily_budget_usd: float

    # Selected ad variation
    primary_text: str
    headline: str
    description: str
    cta: str
    image_url: Optional[str] = None

    # Targeting
    target_countries: List[str] = ["US"]
    target_age_min: int = 18
    target_age_max: int = 65
    target_genders: List[int] = [1, 2]  # 1=male, 2=female


# ==========================================
# Brand Profile Endpoints
# ==========================================

@router.post("/brand-profile")
async def create_or_update_brand_profile(
    request: BrandProfileRequest,
    db: Session = Depends(get_db)
):
    """
    Create or update brand profile for a customer
    This is the one-time setup wizard data
    """
    try:
        # Check if profile exists
        profile = db.query(CustomerProfile).filter(
            CustomerProfile.customer_id == request.customer_id
        ).first()

        if profile:
            # Update existing profile
            profile.company_name = request.company_name
            profile.industry = request.industry
            profile.website_url = request.website_url
            profile.brand_voice = request.brand_voice
            profile.tone_attributes = json.dumps(request.tone_attributes)
            profile.key_values = json.dumps(request.key_values)
            profile.unique_selling_points = json.dumps(request.unique_selling_points)
            profile.target_audience_description = request.target_audience_description
            profile.audience_demographics = json.dumps(request.audience_demographics)
            profile.audience_pain_points = json.dumps(request.audience_pain_points)
            profile.product_category = request.product_category
            profile.price_range = request.price_range
            profile.primary_benefits = json.dumps(request.primary_benefits)
            profile.preferred_ctas = json.dumps(request.preferred_ctas)
            profile.prohibited_words = json.dumps(request.prohibited_words)
            profile.sample_headlines = json.dumps(request.sample_headlines)
            profile.sample_descriptions = json.dumps(request.sample_descriptions)
            profile.meta_page_id = request.meta_page_id
            profile.meta_pixel_id = request.meta_pixel_id
            profile.logo_url = request.logo_url
            profile.brand_colors = json.dumps(request.brand_colors)
            profile.image_style_preference = request.image_style_preference
            profile.is_complete = True
        else:
            # Create new profile
            profile = CustomerProfile(
                customer_id=request.customer_id,
                company_name=request.company_name,
                industry=request.industry,
                website_url=request.website_url,
                brand_voice=request.brand_voice,
                tone_attributes=json.dumps(request.tone_attributes),
                key_values=json.dumps(request.key_values),
                unique_selling_points=json.dumps(request.unique_selling_points),
                target_audience_description=request.target_audience_description,
                audience_demographics=json.dumps(request.audience_demographics),
                audience_pain_points=json.dumps(request.audience_pain_points),
                product_category=request.product_category,
                price_range=request.price_range,
                primary_benefits=json.dumps(request.primary_benefits),
                preferred_ctas=json.dumps(request.preferred_ctas),
                prohibited_words=json.dumps(request.prohibited_words),
                sample_headlines=json.dumps(request.sample_headlines),
                sample_descriptions=json.dumps(request.sample_descriptions),
                meta_page_id=request.meta_page_id,
                meta_pixel_id=request.meta_pixel_id,
                logo_url=request.logo_url,
                brand_colors=json.dumps(request.brand_colors),
                image_style_preference=request.image_style_preference,
                is_complete=True
            )
            db.add(profile)

        db.commit()
        db.refresh(profile)

        logger.info(f"Brand profile saved for customer {request.customer_id}")

        return {
            "success": True,
            "message": "Brand profile saved successfully",
            "profile_id": profile.profile_id
        }

    except Exception as e:
        logger.error(f"Error saving brand profile: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save brand profile: {str(e)}")


@router.get("/brand-profile/{customer_id}")
async def get_brand_profile(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Get brand profile for a customer"""
    try:
        profile = db.query(CustomerProfile).filter(
            CustomerProfile.customer_id == customer_id
        ).first()

        if not profile:
            raise HTTPException(status_code=404, detail="Brand profile not found")

        return {
            "profile_id": profile.profile_id,
            "customer_id": profile.customer_id,
            "company_name": profile.company_name,
            "industry": profile.industry,
            "website_url": profile.website_url,
            "brand_voice": profile.brand_voice,
            "tone_attributes": json.loads(profile.tone_attributes or "[]"),
            "key_values": json.loads(profile.key_values or "[]"),
            "unique_selling_points": json.loads(profile.unique_selling_points or "[]"),
            "target_audience_description": profile.target_audience_description,
            "audience_demographics": json.loads(profile.audience_demographics or "{}"),
            "audience_pain_points": json.loads(profile.audience_pain_points or "[]"),
            "product_category": profile.product_category,
            "price_range": profile.price_range,
            "primary_benefits": json.loads(profile.primary_benefits or "[]"),
            "preferred_ctas": json.loads(profile.preferred_ctas or "[]"),
            "prohibited_words": json.loads(profile.prohibited_words or "[]"),
            "sample_headlines": json.loads(profile.sample_headlines or "[]"),
            "sample_descriptions": json.loads(profile.sample_descriptions or "[]"),
            "meta_page_id": profile.meta_page_id,
            "meta_pixel_id": profile.meta_pixel_id,
            "logo_url": profile.logo_url,
            "brand_colors": json.loads(profile.brand_colors or "[]"),
            "image_style_preference": profile.image_style_preference,
            "is_complete": profile.is_complete
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching brand profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# Ad Generation Endpoints
# ==========================================

@router.post("/generate")
async def generate_ad_variations(
    request: AdGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered ad variations (text + images)
    This is Step 2 of the workflow
    """
    try:
        # Get brand profile
        profile = db.query(CustomerProfile).filter(
            CustomerProfile.customer_id == request.customer_id
        ).first()

        if not profile:
            raise HTTPException(
                status_code=404,
                detail="Brand profile not found. Please complete brand setup first."
            )

        # Initialize AI services
        text_generator = AITextGenerator()
        image_generator = AIImageGenerator() if request.generate_images else None

        # Parse JSON fields
        unique_selling_points = json.loads(profile.unique_selling_points or "[]")
        preferred_ctas = json.loads(profile.preferred_ctas or "[]")
        prohibited_words = json.loads(profile.prohibited_words or "[]")
        brand_colors = json.loads(profile.brand_colors or "[]")

        # Generate ad copy variations
        logger.info(f"Generating {request.num_variations} ad variations for {request.product_name}")

        ad_variations = text_generator.generate_meta_ad_copy(
            product_name=request.product_name,
            product_description=request.product_description,
            target_audience=profile.target_audience_description,
            brand_voice=profile.brand_voice,
            unique_selling_points=unique_selling_points,
            preferred_ctas=preferred_ctas,
            prohibited_words=prohibited_words,
            num_variations=request.num_variations
        )

        # Generate images for each variation (or use same image)
        if request.generate_images and image_generator:
            logger.info(f"Generating AI image for {request.product_name}")

            image_result = image_generator.generate_meta_ad_image(
                product_name=request.product_name,
                product_description=request.product_description,
                image_style=profile.image_style_preference,
                brand_colors=brand_colors if brand_colors else None,
                size="1024x1024"
            )

            # Use same image for all variations (can generate multiple later)
            image_url = image_result["image_url"]
        else:
            image_url = None

        # Format response
        variations_response = []
        for idx, ad in enumerate(ad_variations):
            variations_response.append({
                "variation_id": idx + 1,
                "primary_text": ad["primary_text"],
                "headline": ad["headline"],
                "description": ad["description"],
                "cta": ad["cta"],
                "image_url": image_url,
                "confidence_score": ad["confidence_score"],
                "focus_usp": ad["focus_usp"]
            })

        logger.info(f"Successfully generated {len(variations_response)} ad variations")

        return {
            "success": True,
            "variations": variations_response,
            "total_count": len(variations_response)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating ad variations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate ads: {str(e)}")


# ==========================================
# Ad Launch Endpoint
# ==========================================

@router.post("/launch")
async def launch_ad_to_meta(
    request: AdLaunchRequest,
    db: Session = Depends(get_db)
):
    """
    Launch selected ad variation to Meta Ads
    Creates campaign ’ ad set ’ creative ’ ad (all in PAUSED state)
    This is Step 4 of the workflow
    """
    try:
        # Get brand profile for page_id
        profile = db.query(CustomerProfile).filter(
            CustomerProfile.customer_id == request.customer_id
        ).first()

        if not profile or not profile.meta_page_id:
            raise HTTPException(
                status_code=400,
                detail="Meta Page ID not found in brand profile. Please update brand settings."
            )

        # Initialize Meta service
        meta_service = get_meta_ads_service(account_id=request.meta_account_id)

        logger.info(f"Launching ad to Meta account {request.meta_account_id}")

        # Convert budget to cents
        daily_budget_cents = int(request.daily_budget_usd * 100)

        # Step 1: Create Campaign
        campaign_result = meta_service.create_sales_campaign(
            account_id=request.meta_account_id,
            campaign_name=request.campaign_name,
            daily_budget_cents=daily_budget_cents,
            status="PAUSED"
        )
        campaign_id = campaign_result["campaign_id"]
        logger.info(f"Created campaign {campaign_id}")

        # Step 2: Create Ad Set with targeting
        targeting_spec = {
            "geo_locations": {
                "countries": request.target_countries
            },
            "age_min": request.target_age_min,
            "age_max": request.target_age_max,
            "genders": request.target_genders,
            "publisher_platforms": ["facebook", "instagram"]
        }

        ad_set_result = meta_service.create_ad_set(
            campaign_id=campaign_id,
            ad_set_name=f"{request.product_name} - Ad Set",
            daily_budget_cents=daily_budget_cents,
            targeting=targeting_spec,
            optimization_goal="OFFSITE_CONVERSIONS",
            billing_event="IMPRESSIONS",
            status="PAUSED"
        )
        ad_set_id = ad_set_result["ad_set_id"]
        logger.info(f"Created ad set {ad_set_id}")

        # Step 3: Upload image (if provided)
        image_hash = None
        if request.image_url:
            logger.info(f"Uploading image from URL: {request.image_url}")
            image_hash = meta_service.upload_image(
                account_id=request.meta_account_id,
                image_url=request.image_url,
                filename=f"{request.product_name.replace(' ', '_')}.jpg"
            )
            logger.info(f"Image uploaded with hash {image_hash}")

        # Step 4: Create Ad Creative
        creative_id = meta_service.create_ad_creative(
            account_id=request.meta_account_id,
            page_id=profile.meta_page_id,
            creative_name=f"{request.product_name} - Creative",
            primary_text=request.primary_text,
            headline=request.headline,
            description=request.description,
            landing_url=request.landing_url,
            image_hash=image_hash,
            call_to_action_type=request.cta.upper().replace(" ", "_")
        )
        logger.info(f"Created creative {creative_id}")

        # Step 5: Create Ad
        ad_result = meta_service.create_ad(
            account_id=request.meta_account_id,
            ad_set_id=ad_set_id,
            creative_id=creative_id,
            ad_name=f"{request.product_name} - Ad",
            status="PAUSED"
        )
        ad_id = ad_result["ad_id"]
        logger.info(f"Created ad {ad_id}")

        return {
            "success": True,
            "message": "Ad launched successfully to Meta Ads (PAUSED for review)",
            "campaign_id": campaign_id,
            "ad_set_id": ad_set_id,
            "creative_id": creative_id,
            "ad_id": ad_id,
            "meta_ads_url": f"https://business.facebook.com/adsmanager/manage/campaigns?act={request.meta_account_id.replace('act_', '')}&selected_campaign_ids={campaign_id}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error launching ad to Meta: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to launch ad: {str(e)}")
