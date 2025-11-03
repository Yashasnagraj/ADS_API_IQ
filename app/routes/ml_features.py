"""
ML Features endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import MLFeature
from app.schemas.ml_feature import MLFeatureListResponse, MLFeatureBase
from app.core.config import settings

router = APIRouter(prefix="/ml-features", tags=["ml_features"])

@router.get("", response_model=MLFeatureListResponse)
def get_ml_features(
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    campaign_id: Optional[int] = None,
    min_quality_score: Optional[int] = Query(None, ge=1, le=10),
    channel_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all ML-ready features for model training (normalized)
    """
    query = db.query(MLFeature)

    if campaign_id:
        query = query.filter(MLFeature.campaign_id == campaign_id)
    if min_quality_score:
        query = query.filter(MLFeature.quality_score >= min_quality_score)
    if channel_type:
        query = query.filter(MLFeature.channel_type == channel_type)

    # Order by impressions for relevance
    query = query.order_by(MLFeature.impressions.desc())

    total = query.count()
    features = query.offset(offset).limit(limit).all()

    feature_list = [
        MLFeatureBase(
            id=f.id,
            customer_id=f.customer_id,
            campaign_id=f.campaign_id,
            campaign_name=f.campaign_name,
            channel_type=f.channel_type,
            bidding_strategy=f.bidding_strategy,
            budget_amount=f.budget_amount,
            keyword_id=f.keyword_id,
            keyword_text=f.keyword_text,
            match_type=f.match_type,
            quality_score=f.quality_score,
            avg_cpc=f.avg_cpc,
            ctr=f.ctr,
            conversion_rate=f.conversion_rate,
            conversions=f.conversions,
            cost=f.cost,
            impressions=f.impressions,
            clicks=f.clicks,
            competition_index=f.competition_index,
            search_volume_trend=f.search_volume_trend,
            created_at=f.created_at
        ) for f in features
    ]

    return MLFeatureListResponse(
        features=feature_list,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total
    )