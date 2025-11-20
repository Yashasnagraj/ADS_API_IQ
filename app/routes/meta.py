

"""
Meta (Facebook) Ads API Routes

Endpoints:
- Integration status
- Ad accounts
- Campaigns
- Ad sets
- Ads
- Performance insights
- Cross-platform comparison (Google Ads vs Meta Ads)

NOW USING REAL-TIME META ADS API (not database)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from typing import List, Optional
from datetime import datetime, timedelta
from loguru import logger

from app.db.database import get_db
from app.db import models
from app.schemas import meta as schemas
from app.services.meta_ads_service import get_meta_ads_service


router = APIRouter(prefix="/meta", tags=["meta"])


# ==============================================================================
# INTEGRATION STATUS
# ==============================================================================

@router.get("/integration/status", response_model=schemas.MetaIntegrationStatusResponse)
def get_integration_status(
    customer_id: int = Query(..., description="Customer ID"),
    db: Session = Depends(get_db)
):
    """
    Check Meta Ads integration status for a customer

    Returns:
    - Connection status
    - Number of ad accounts
    - Total campaigns, ad sets, ads
    - Total spend, clicks, conversions
    """

    # Check if customer has Meta ad accounts
    accounts = db.query(models.MetaAdAccount).filter(
        models.MetaAdAccount.customer_id == customer_id,
        models.MetaAdAccount.is_active == True
    ).all()

    is_connected = len(accounts) > 0

    if not is_connected:
        return schemas.MetaIntegrationStatusResponse(
            customer_id=customer_id,
            is_connected=False,
            accounts_count=0,
            active_accounts=0,
            total_campaigns=0,
            total_adsets=0,
            total_ads=0,
            total_spend=0.0,
            total_clicks=0,
            total_conversions=0.0,
            last_sync_at=None
        )

    # Get account IDs
    account_ids = [acc.account_id for acc in accounts]

    # Count campaigns
    total_campaigns = db.query(func.count(models.MetaCampaign.campaign_id)).filter(
        models.MetaCampaign.customer_id == customer_id
    ).scalar() or 0

    # Count ad sets
    total_adsets = db.query(func.count(models.MetaAdSet.adset_id)).filter(
        models.MetaAdSet.customer_id == customer_id
    ).scalar() or 0

    # Count ads
    total_ads = db.query(func.count(models.MetaAd.ad_id)).filter(
        models.MetaAd.customer_id == customer_id
    ).scalar() or 0

    # Aggregate insights
    insights_agg = db.query(
        func.sum(models.MetaInsights.spend).label('total_spend'),
        func.sum(models.MetaInsights.clicks).label('total_clicks'),
        func.sum(models.MetaInsights.conversions).label('total_conversions')
    ).filter(
        models.MetaInsights.customer_id == customer_id
    ).first()

    total_spend = float(insights_agg.total_spend or 0)
    total_clicks = int(insights_agg.total_clicks or 0)
    total_conversions = float(insights_agg.total_conversions or 0)

    # Get last sync time
    last_sync = max([acc.last_sync_at for acc in accounts if acc.last_sync_at], default=None)

    return schemas.MetaIntegrationStatusResponse(
        customer_id=customer_id,
        is_connected=True,
        accounts_count=len(accounts),
        active_accounts=len(accounts),
        total_campaigns=total_campaigns,
        total_adsets=total_adsets,
        total_ads=total_ads,
        total_spend=total_spend,
        total_clicks=total_clicks,
        total_conversions=total_conversions,
        last_sync_at=last_sync
    )


# ==============================================================================
# AD ACCOUNTS
# ==============================================================================

@router.get("/accounts", response_model=schemas.MetaAdAccountsListResponse)
def get_ad_accounts(
    customer_id: int = Query(..., description="Customer ID"),
    db: Session = Depends(get_db)
):
    """Get all Meta ad accounts for a customer"""

    accounts = db.query(models.MetaAdAccount).filter(
        models.MetaAdAccount.customer_id == customer_id
    ).all()

    return schemas.MetaAdAccountsListResponse(
        accounts=accounts,
        total_count=len(accounts)
    )


# ==============================================================================
# CAMPAIGNS
# ==============================================================================

@router.get("/campaigns", response_model=schemas.MetaCampaignsListResponse)
def get_campaigns(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID (format: act_123456789)"),
    status: Optional[str] = Query(None, description="Filter by status (ACTIVE, PAUSED, etc.)"),
    objective: Optional[str] = Query(None, description="Filter by objective"),
    date_range: str = Query('last_30d', description="Date range for insights (last_7d, last_30d, etc.)"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Get Meta Ads campaigns (REAL-TIME from Facebook Marketing API)

    Filters:
    - customer_id (required)
    - account_id (optional): If not provided, uses first account for customer
    - status (optional): ACTIVE, PAUSED, DELETED, ARCHIVED
    - objective (optional): OUTCOME_SALES, OUTCOME_LEADS, etc.
    - date_range: last_7d, last_30d, last_60d, last_90d
    """

    try:
        # Get Meta ad account for customer if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(
                    status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}"
                )

            account_id = meta_account.account_id
            logger.info(f"Using Meta account {account_id} for customer {customer_id}")

        # Get real-time campaigns from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)

        campaigns_data = meta_service.get_campaigns(
            account_id=account_id,
            status=status,
            date_range=date_range,
            include_insights=True
        )

        # Filter by objective if provided
        if objective:
            campaigns_data = [
                c for c in campaigns_data
                if c.get('objective') == objective
            ]

        # Build response objects
        campaigns_list = []
        for campaign_data in campaigns_data:
            insights = campaign_data.get('insights', {})

            # Build campaign response
            campaign = schemas.MetaCampaignResponse(
                campaign_id=campaign_data.get('id', ''),
                account_id=account_id,
                customer_id=customer_id,
                name=campaign_data.get('name', ''),
                status=campaign_data.get('status'),
                effective_status=campaign_data.get('effective_status'),
                objective=campaign_data.get('objective'),
                daily_budget=campaign_data.get('daily_budget_converted'),
                lifetime_budget=campaign_data.get('lifetime_budget_converted'),
                budget_remaining=campaign_data.get('budget_remaining_converted'),
                bid_strategy=campaign_data.get('bid_strategy'),
                buying_type=campaign_data.get('buying_type'),
                created_time=campaign_data.get('created_time'),
                updated_time=campaign_data.get('updated_time'),
                start_time=campaign_data.get('start_time'),
                stop_time=campaign_data.get('stop_time')
            )

            campaigns_list.append(campaign)

        # Apply pagination
        total_count = len(campaigns_list)
        paginated_campaigns = campaigns_list[offset:offset + limit]

        logger.info(f"✅ Retrieved {total_count} campaigns (showing {len(paginated_campaigns)})")

        return schemas.MetaCampaignsListResponse(
            campaigns=paginated_campaigns,
            total_count=total_count
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching Meta campaigns: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch campaigns: {str(e)}")


@router.get("/campaigns/{campaign_id}", response_model=schemas.MetaCampaignResponse)
def get_campaign_details(
    campaign_id: str,
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    date_range: str = Query('last_30d', description="Date range for insights"),
    db: Session = Depends(get_db)
):
    """Get details for a specific Meta campaign (REAL-TIME from Facebook Marketing API)"""

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time campaign data from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)

        campaigns_data = meta_service.get_campaigns(
            account_id=account_id,
            status=None,
            date_range=date_range,
            include_insights=True
        )

        # Find the specific campaign
        campaign_data = next((c for c in campaigns_data if c.get('id') == campaign_id), None)

        if not campaign_data:
            raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

        # Build response
        return schemas.MetaCampaignResponse(
            campaign_id=campaign_data.get('id', ''),
            account_id=account_id,
            customer_id=customer_id,
            name=campaign_data.get('name', ''),
            status=campaign_data.get('status'),
            effective_status=campaign_data.get('effective_status'),
            objective=campaign_data.get('objective'),
            daily_budget=campaign_data.get('daily_budget_converted'),
            lifetime_budget=campaign_data.get('lifetime_budget_converted'),
            budget_remaining=campaign_data.get('budget_remaining_converted'),
            bid_strategy=campaign_data.get('bid_strategy'),
            buying_type=campaign_data.get('buying_type'),
            created_time=campaign_data.get('created_time'),
            updated_time=campaign_data.get('updated_time'),
            start_time=campaign_data.get('start_time'),
            stop_time=campaign_data.get('stop_time')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch campaign: {str(e)}")


# ==============================================================================
# AD SETS
# ==============================================================================

@router.get("/adsets", response_model=schemas.MetaAdSetsListResponse)
def get_adsets(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date_range: str = Query('last_30d', description="Date range for insights"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get Meta Ads ad sets (REAL-TIME from Facebook Marketing API)

    Filters:
    - customer_id (required)
    - account_id (optional)
    - campaign_id (optional)
    - status (optional): ACTIVE, PAUSED, DELETED, ARCHIVED
    - date_range: last_7d, last_30d, last_60d, last_90d
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time ad sets from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)

        adsets_data = meta_service.get_ad_sets(
            account_id=account_id,
            campaign_id=campaign_id,
            status=status,
            date_range=date_range,
            include_insights=True
        )

        # Build response objects
        adsets_list = []
        for adset_data in adsets_data:
            adset = schemas.MetaAdSetResponse(
                adset_id=adset_data.get('id', ''),
                campaign_id=adset_data.get('campaign_id', ''),
                account_id=account_id,
                customer_id=customer_id,
                name=adset_data.get('name', ''),
                status=adset_data.get('status'),
                effective_status=adset_data.get('effective_status'),
                daily_budget=adset_data.get('daily_budget_converted'),
                lifetime_budget=adset_data.get('lifetime_budget_converted'),
                budget_remaining=adset_data.get('budget_remaining_converted'),
                bid_strategy=adset_data.get('bid_strategy'),
                billing_event=adset_data.get('billing_event'),
                optimization_goal=adset_data.get('optimization_goal'),
                created_time=adset_data.get('created_time'),
                updated_time=adset_data.get('updated_time'),
                start_time=adset_data.get('start_time'),
                end_time=adset_data.get('end_time')
            )
            adsets_list.append(adset)

        # Apply pagination
        total_count = len(adsets_list)
        paginated_adsets = adsets_list[offset:offset + limit]

        logger.info(f"✅ Retrieved {total_count} ad sets (showing {len(paginated_adsets)})")

        return schemas.MetaAdSetsListResponse(
            adsets=paginated_adsets,
            total_count=total_count
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching Meta ad sets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ad sets: {str(e)}")


@router.get("/adsets/{adset_id}", response_model=schemas.MetaAdSetResponse)
def get_adset_details(
    adset_id: str,
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    date_range: str = Query('last_30d', description="Date range for insights"),
    db: Session = Depends(get_db)
):
    """Get details for a specific Meta ad set (REAL-TIME from Facebook Marketing API)"""

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time ad sets from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)

        adsets_data = meta_service.get_ad_sets(
            account_id=account_id,
            campaign_id=None,
            status=None,
            date_range=date_range,
            include_insights=True
        )

        # Find the specific ad set
        adset_data = next((a for a in adsets_data if a.get('id') == adset_id), None)

        if not adset_data:
            raise HTTPException(status_code=404, detail=f"Ad set {adset_id} not found")

        # Build response
        return schemas.MetaAdSetResponse(
            adset_id=adset_data.get('id', ''),
            campaign_id=adset_data.get('campaign_id', ''),
            account_id=account_id,
            customer_id=customer_id,
            name=adset_data.get('name', ''),
            status=adset_data.get('status'),
            effective_status=adset_data.get('effective_status'),
            daily_budget=adset_data.get('daily_budget_converted'),
            lifetime_budget=adset_data.get('lifetime_budget_converted'),
            budget_remaining=adset_data.get('budget_remaining_converted'),
            bid_strategy=adset_data.get('bid_strategy'),
            billing_event=adset_data.get('billing_event'),
            optimization_goal=adset_data.get('optimization_goal'),
            created_time=adset_data.get('created_time'),
            updated_time=adset_data.get('updated_time'),
            start_time=adset_data.get('start_time'),
            end_time=adset_data.get('end_time')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching ad set {adset_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ad set: {str(e)}")


# ==============================================================================
# ADS
# ==============================================================================

@router.get("/ads", response_model=schemas.MetaAdsListResponse)
def get_ads(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign"),
    adset_id: Optional[str] = Query(None, description="Filter by ad set"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date_range: str = Query('last_30d', description="Date range for insights"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get Meta Ads (creatives) (REAL-TIME from Facebook Marketing API)

    Filters:
    - customer_id (required)
    - account_id (optional)
    - campaign_id (optional)
    - adset_id (optional)
    - status (optional): ACTIVE, PAUSED, DELETED, ARCHIVED
    - date_range: last_7d, last_30d, last_60d, last_90d
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time ads from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)

        ads_data = meta_service.get_ads(
            account_id=account_id,
            adset_id=adset_id,
            campaign_id=campaign_id,
            status=status,
            date_range=date_range,
            include_insights=True
        )

        # Build response objects
        ads_list = []
        for ad_data in ads_data:
            ad = schemas.MetaAdResponse(
                ad_id=ad_data.get('id', ''),
                adset_id=ad_data.get('adset_id', ''),
                campaign_id=ad_data.get('campaign_id', ''),
                account_id=account_id,
                customer_id=customer_id,
                name=ad_data.get('name', ''),
                status=ad_data.get('status'),
                effective_status=ad_data.get('effective_status'),
                created_time=ad_data.get('created_time'),
                updated_time=ad_data.get('updated_time')
            )
            ads_list.append(ad)

        # Apply pagination
        total_count = len(ads_list)
        paginated_ads = ads_list[offset:offset + limit]

        logger.info(f"✅ Retrieved {total_count} ads (showing {len(paginated_ads)})")

        return schemas.MetaAdsListResponse(
            ads=paginated_ads,
            total_count=total_count
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching Meta ads: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ads: {str(e)}")


@router.get("/ads/{ad_id}", response_model=schemas.MetaAdResponse)
def get_ad_details(
    ad_id: str,
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    date_range: str = Query('last_30d', description="Date range for insights"),
    db: Session = Depends(get_db)
):
    """Get details for a specific Meta ad (REAL-TIME from Facebook Marketing API)"""

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time ads from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)

        ads_data = meta_service.get_ads(
            account_id=account_id,
            adset_id=None,
            campaign_id=None,
            status=None,
            date_range=date_range,
            include_insights=True
        )

        # Find the specific ad
        ad_data = next((a for a in ads_data if a.get('id') == ad_id), None)

        if not ad_data:
            raise HTTPException(status_code=404, detail=f"Ad {ad_id} not found")

        # Build response
        return schemas.MetaAdResponse(
            ad_id=ad_data.get('id', ''),
            adset_id=ad_data.get('adset_id', ''),
            campaign_id=ad_data.get('campaign_id', ''),
            account_id=account_id,
            customer_id=customer_id,
            name=ad_data.get('name', ''),
            status=ad_data.get('status'),
            effective_status=ad_data.get('effective_status'),
            created_time=ad_data.get('created_time'),
            updated_time=ad_data.get('updated_time')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching ad {ad_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ad: {str(e)}")


# ==============================================================================
# INSIGHTS (PERFORMANCE METRICS)
# ==============================================================================

@router.get("/insights")  # response_model=schemas.MetaInsightsResponse
def get_insights(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    level: str = Query('account', description="Level: account, campaign, adset, or ad"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign"),
    date_range: str = Query('last_30d', description="Date range: last_7d, last_30d, etc."),
    breakdowns: Optional[str] = Query(None, description="Breakdowns: age,gender or country"),
    db: Session = Depends(get_db)
):
    """
    Get Meta Ads performance insights (REAL-TIME from Facebook Marketing API)

    Returns metrics:
    - Impressions, clicks, spend
    - Reach, frequency
    - Conversions, ROAS
    - CTR, CPC, CPM
    - Engagement metrics (reactions, comments, shares, video views)

    Levels:
    - account: Account-level aggregated metrics
    - campaign: Per-campaign metrics
    - adset: Per-adset metrics
    - ad: Per-ad metrics

    Breakdowns (optional):
    - age,gender: Demographics
    - country: Geographic
    - device_platform: Device type
    - publisher_platform: Platform/placement
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time insights from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)

        # Parse breakdowns into list if provided
        breakdowns_list = breakdowns.split(',') if breakdowns else None

        insights_data = meta_service.get_insights(
            account_id=account_id,
            level=level,
            date_range=date_range,
            breakdowns=breakdowns_list,
            campaign_id=campaign_id
        )

        logger.info(f"✅ Retrieved insights for {level} level")

        return schemas.MetaInsightsResponse(
            customer_id=customer_id,
            account_id=account_id,
            level=level,
            date_range=date_range,
            insights=insights_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching Meta insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch insights: {str(e)}")


@router.get("/insights/summary", response_model=schemas.MetaInsightsSummaryResponse)
def get_insights_summary(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    date_range: str = Query('last_30d', description="Date range: last_7d, last_30d, etc."),
    db: Session = Depends(get_db)
):
    """
    Get aggregated insights summary (REAL-TIME from Facebook Marketing API)

    Returns totals across all campaigns:
    - Total spend, clicks, impressions
    - Total conversions, purchase value
    - Average CTR, CPC, CPM
    - Overall ROAS
    - Engagement metrics (reactions, comments, shares, video views)
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time account-level insights from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)

        insights_data = meta_service.get_insights(
            account_id=account_id,
            level='account',
            date_range=date_range,
            breakdowns=None,
            campaign_id=None
        )

        # Extract aggregated metrics (account level returns single result)
        if not insights_data:
            # Return empty summary if no data
            return schemas.MetaInsightsSummaryResponse(
                customer_id=customer_id,
                date_start=date_range,
                date_stop=date_range,
                total_impressions=0,
                total_clicks=0,
                total_spend=0.0,
                total_reach=0,
                avg_frequency=0.0,
                total_conversions=0.0,
                total_purchase_value=0.0,
                avg_ctr=0.0,
                avg_cpc=0.0,
                avg_cpm=0.0,
                overall_roas=0.0
            )

        summary = insights_data[0]  # Account level returns single aggregated result

        total_impressions = int(summary.get('impressions', 0))
        total_clicks = int(summary.get('clicks', 0))
        total_spend = float(summary.get('spend', 0))
        total_reach = int(summary.get('reach', 0))
        avg_frequency = float(summary.get('frequency', 0))
        total_conversions = float(summary.get('conversions', 0))
        total_purchase_value = float(summary.get('purchase_value', 0))

        # Calculate metrics
        avg_ctr = round((total_clicks / total_impressions) * 100, 2) if total_impressions > 0 else 0
        avg_cpc = round(total_spend / total_clicks, 2) if total_clicks > 0 else 0
        avg_cpm = round((total_spend / total_impressions) * 1000, 2) if total_impressions > 0 else 0
        overall_roas = round(total_purchase_value / total_spend, 2) if total_spend > 0 else 0

        logger.info(f"✅ Retrieved insights summary for account {account_id}")

        return schemas.MetaInsightsSummaryResponse(
            customer_id=customer_id,
            date_start=date_range,
            date_stop=date_range,
            total_impressions=total_impressions,
            total_clicks=total_clicks,
            total_spend=total_spend,
            total_reach=total_reach,
            avg_frequency=avg_frequency,
            total_conversions=total_conversions,
            total_purchase_value=total_purchase_value,
            avg_ctr=avg_ctr,
            avg_cpc=avg_cpc,
            avg_cpm=avg_cpm,
            overall_roas=overall_roas
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching Meta insights summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch insights summary: {str(e)}")


# ==============================================================================
# CROSS-PLATFORM COMPARISON
# ==============================================================================

@router.get("/cross-platform/comparison", response_model=schemas.CrossPlatformComparisonResponse)
def get_cross_platform_comparison(
    customer_id: int = Query(..., description="Customer ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Compare Google Ads vs Meta Ads performance

    Returns:
    - Side-by-side metrics comparison
    - CPC, CTR, ROAS comparison
    - Budget allocation recommendation
    """

    date_start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    date_stop = datetime.now().strftime('%Y-%m-%d')

    # Get Meta Ads metrics
    meta_agg = db.query(
        func.sum(models.MetaInsights.spend).label('total_spend'),
        func.sum(models.MetaInsights.clicks).label('total_clicks'),
        func.sum(models.MetaInsights.impressions).label('total_impressions'),
        func.sum(models.MetaInsights.conversions).label('total_conversions'),
        func.sum(models.MetaInsights.purchase_value).label('total_revenue')
    ).filter(
        models.MetaInsights.customer_id == customer_id,
        models.MetaInsights.date_start >= date_start
    ).first()

    meta_spend = float(meta_agg.total_spend or 0)
    meta_clicks = int(meta_agg.total_clicks or 0)
    meta_impressions = int(meta_agg.total_impressions or 0)
    meta_conversions = float(meta_agg.total_conversions or 0)
    meta_revenue = float(meta_agg.total_revenue or 0)

    meta_cpc = round(meta_spend / meta_clicks, 2) if meta_clicks > 0 else 0
    meta_ctr = round((meta_clicks / meta_impressions) * 100, 2) if meta_impressions > 0 else 0
    meta_roas = round(meta_revenue / meta_spend, 2) if meta_spend > 0 else 0
    meta_conv_rate = round((meta_conversions / meta_clicks) * 100, 2) if meta_clicks > 0 else 0

    # Get Google Ads metrics (from campaign_keywords table)
    google_agg = db.query(
        func.sum(models.CampaignKeyword.cost_micros).label('total_cost'),
        func.sum(models.CampaignKeyword.clicks).label('total_clicks'),
        func.sum(models.CampaignKeyword.impressions).label('total_impressions'),
        func.sum(models.CampaignKeyword.conversions).label('total_conversions'),
        func.sum(models.CampaignKeyword.conversion_value).label('total_revenue')
    ).filter(
        models.CampaignKeyword.customer_id == customer_id,
        models.CampaignKeyword.date >= date_start
    ).first()

    google_spend = float(google_agg.total_cost or 0) / 1_000_000  # Convert micros to currency
    google_clicks = int(google_agg.total_clicks or 0)
    google_impressions = int(google_agg.total_impressions or 0)
    google_conversions = float(google_agg.total_conversions or 0)
    google_revenue = float(google_agg.total_revenue or 0)

    google_cpc = round(google_spend / google_clicks, 2) if google_clicks > 0 else 0
    google_ctr = round((google_clicks / google_impressions) * 100, 2) if google_impressions > 0 else 0
    google_roas = round(google_revenue / google_spend, 2) if google_spend > 0 else 0
    google_conv_rate = round((google_conversions / google_clicks) * 100, 2) if google_clicks > 0 else 0

    # Calculate comparisons
    spend_ratio = round(meta_spend / google_spend, 2) if google_spend > 0 else 0
    cpc_diff = round(meta_cpc - google_cpc, 2)
    roas_diff = round(meta_roas - google_roas, 2)

    # Generate recommendation
    if meta_roas > google_roas and meta_cpc < google_cpc:
        recommendation = f"Meta Ads is outperforming Google Ads with {abs(cpc_diff):.2f} lower CPC and {roas_diff:.2f} higher ROAS. Consider increasing Meta budget by 15-20%."
    elif google_roas > meta_roas and google_cpc < meta_cpc:
        recommendation = f"Google Ads is outperforming Meta Ads with {abs(cpc_diff):.2f} lower CPC and {abs(roas_diff):.2f} higher ROAS. Consider increasing Google Ads budget by 15-20%."
    elif meta_cpc < google_cpc:
        recommendation = f"Meta Ads has {abs(cpc_diff):.2f} lower CPC. Consider testing budget reallocation to Meta for cost efficiency."
    else:
        recommendation = "Both platforms performing similarly. Maintain current budget allocation and continue monitoring."

    return schemas.CrossPlatformComparisonResponse(
        customer_id=customer_id,
        date_range=f"Last {days} days",
        google_ads=schemas.PlatformMetrics(
            total_spend=google_spend,
            total_clicks=google_clicks,
            total_impressions=google_impressions,
            total_conversions=google_conversions,
            avg_cpc=google_cpc,
            ctr=google_ctr,
            roas=google_roas,
            conversion_rate=google_conv_rate
        ),
        meta_ads=schemas.PlatformMetrics(
            total_spend=meta_spend,
            total_clicks=meta_clicks,
            total_impressions=meta_impressions,
            total_conversions=meta_conversions,
            avg_cpc=meta_cpc,
            ctr=meta_ctr,
            roas=meta_roas,
            conversion_rate=meta_conv_rate
        ),
        meta_vs_google_spend_ratio=spend_ratio,
        meta_vs_google_cpc_diff=cpc_diff,
        meta_vs_google_roas_diff=roas_diff,
        recommendation=recommendation
    )


@router.get("/cross-platform/unified-metrics", response_model=schemas.UnifiedMetricsResponse)
def get_unified_metrics(
    customer_id: int = Query(..., description="Customer ID"),
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    db: Session = Depends(get_db)
):
    """
    Get unified metrics across all platforms

    Combines:
    - Google Ads spend & conversions
    - Meta Ads spend & conversions
    - GA4 sessions
    - Shopify orders & revenue
    """

    date_start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    # Meta Ads
    meta_agg = db.query(
        func.sum(models.MetaInsights.spend).label('spend'),
        func.sum(models.MetaInsights.clicks).label('clicks'),
        func.sum(models.MetaInsights.impressions).label('impressions'),
        func.sum(models.MetaInsights.conversions).label('conversions'),
        func.sum(models.MetaInsights.purchase_value).label('revenue')
    ).filter(
        models.MetaInsights.customer_id == customer_id,
        models.MetaInsights.date_start >= date_start
    ).first()

    # Google Ads
    google_agg = db.query(
        func.sum(models.CampaignKeyword.cost_micros).label('spend'),
        func.sum(models.CampaignKeyword.clicks).label('clicks'),
        func.sum(models.CampaignKeyword.impressions).label('impressions'),
        func.sum(models.CampaignKeyword.conversions).label('conversions'),
        func.sum(models.CampaignKeyword.conversion_value).label('revenue')
    ).filter(
        models.CampaignKeyword.customer_id == customer_id,
        models.CampaignKeyword.date >= date_start
    ).first()

    # GA4 Sessions
    ga4_sessions = db.query(func.sum(models.GA4Session.sessions)).filter(
        models.GA4Session.customer_id == customer_id,
        models.GA4Session.date >= date_start
    ).scalar() or 0

    # Shopify Orders
    shopify_agg = db.query(
        func.count(models.ShopifyOrder.order_id).label('orders'),
        func.sum(models.ShopifyOrder.total_price).label('revenue')
    ).filter(
        models.ShopifyOrder.customer_id == customer_id
    ).first()

    # Calculate totals
    meta_spend = float(meta_agg.spend or 0)
    google_spend = float(google_agg.spend or 0) / 1_000_000

    total_spend = meta_spend + google_spend
    total_clicks = int(meta_agg.clicks or 0) + int(google_agg.clicks or 0)
    total_impressions = int(meta_agg.impressions or 0) + int(google_agg.impressions or 0)
    total_conversions = float(meta_agg.conversions or 0) + float(google_agg.conversions or 0)
    total_revenue = float(shopify_agg.revenue or 0)

    # Calculate KPIs
    overall_roas = round(total_revenue / total_spend, 2) if total_spend > 0 else 0
    blended_cpc = round(total_spend / total_clicks, 2) if total_clicks > 0 else 0
    blended_conv_rate = round((total_conversions / total_clicks) * 100, 2) if total_clicks > 0 else 0

    return schemas.UnifiedMetricsResponse(
        customer_id=customer_id,
        date_range=f"Last {days} days",
        total_spend=total_spend,
        total_clicks=total_clicks,
        total_impressions=total_impressions,
        total_conversions=total_conversions,
        total_revenue=total_revenue,
        google_ads_spend=google_spend,
        meta_ads_spend=meta_spend,
        ga4_sessions=int(ga4_sessions),
        shopify_orders=int(shopify_agg.orders or 0),
        overall_roas=overall_roas,
        blended_cpc=blended_cpc,
        blended_conversion_rate=blended_conv_rate
    )


# ==============================================================================
# CUSTOM CONVERSIONS
# ==============================================================================

@router.get("/custom-conversions")
def get_custom_conversions(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    db: Session = Depends(get_db)
):
    """
    Get custom conversion events and tracking pixels (REAL-TIME from Facebook Marketing API)

    Returns:
    - Custom conversion tracking events
    - Pixel-based conversions
    - Custom event definitions
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time custom conversions from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)
        conversions_data = meta_service.get_custom_conversions(account_id=account_id)

        logger.info(f"✅ Retrieved {len(conversions_data)} custom conversions")

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "custom_conversions": conversions_data,
            "total_count": len(conversions_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching custom conversions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch custom conversions: {str(e)}")


@router.get("/custom-conversions/{conversion_id}")
def get_custom_conversion_details(
    conversion_id: str,
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    db: Session = Depends(get_db)
):
    """Get details for a specific custom conversion (REAL-TIME from Facebook Marketing API)"""

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time custom conversions
        meta_service = get_meta_ads_service(account_id=account_id)
        conversions_data = meta_service.get_custom_conversions(account_id=account_id)

        # Find specific conversion
        conversion = next((c for c in conversions_data if c.get('id') == conversion_id), None)

        if not conversion:
            raise HTTPException(status_code=404, detail=f"Custom conversion {conversion_id} not found")

        return conversion

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching custom conversion {conversion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch custom conversion: {str(e)}")


# ==============================================================================
# CUSTOM AUDIENCES
# ==============================================================================

@router.get("/custom-audiences")
def get_custom_audiences(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    db: Session = Depends(get_db)
):
    """
    Get custom audiences and lookalike audiences (REAL-TIME from Facebook Marketing API)

    Returns:
    - Custom audience segments
    - Lookalike audiences
    - Audience sizes and reach
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time custom audiences from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)
        audiences_data = meta_service.get_custom_audiences(account_id=account_id)

        logger.info(f"✅ Retrieved {len(audiences_data)} custom audiences")

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "custom_audiences": audiences_data,
            "total_count": len(audiences_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching custom audiences: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch custom audiences: {str(e)}")


@router.get("/custom-audiences/{audience_id}")
def get_custom_audience_details(
    audience_id: str,
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    db: Session = Depends(get_db)
):
    """Get details for a specific custom audience (REAL-TIME from Facebook Marketing API)"""

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time custom audiences
        meta_service = get_meta_ads_service(account_id=account_id)
        audiences_data = meta_service.get_custom_audiences(account_id=account_id)

        # Find specific audience
        audience = next((a for a in audiences_data if a.get('id') == audience_id), None)

        if not audience:
            raise HTTPException(status_code=404, detail=f"Custom audience {audience_id} not found")

        return audience

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching custom audience {audience_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch custom audience: {str(e)}")


# ==============================================================================
# AD CREATIVES
# ==============================================================================

@router.get("/ad-creatives")
def get_ad_creatives(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    ad_id: Optional[str] = Query(None, description="Filter by ad ID"),
    db: Session = Depends(get_db)
):
    """
    Get ad creative assets and templates (REAL-TIME from Facebook Marketing API)

    Returns:
    - Creative assets used in ads
    - Creative templates
    - Image/video URLs
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time ad creatives from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)
        creatives_data = meta_service.get_ad_creatives(account_id=account_id, ad_id=ad_id)

        logger.info(f"✅ Retrieved {len(creatives_data)} ad creatives")

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "ad_creatives": creatives_data,
            "total_count": len(creatives_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching ad creatives: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ad creatives: {str(e)}")


@router.get("/ad-creatives/{creative_id}")
def get_ad_creative_details(
    creative_id: str,
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    db: Session = Depends(get_db)
):
    """Get details for a specific ad creative (REAL-TIME from Facebook Marketing API)"""

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time ad creatives
        meta_service = get_meta_ads_service(account_id=account_id)
        creatives_data = meta_service.get_ad_creatives(account_id=account_id, ad_id=None)

        # Find specific creative
        creative = next((c for c in creatives_data if c.get('id') == creative_id), None)

        if not creative:
            raise HTTPException(status_code=404, detail=f"Ad creative {creative_id} not found")

        return creative

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching ad creative {creative_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ad creative: {str(e)}")


# ==============================================================================
# IMAGE & VIDEO ASSETS
# ==============================================================================

@router.get("/images")
def get_images(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    db: Session = Depends(get_db)
):
    """
    Get image assets from ad account library (REAL-TIME from Facebook Marketing API)

    Returns:
    - Image hashes
    - Image URLs
    - Image dimensions
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time images from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)
        images_data = meta_service.get_images(account_id=account_id)

        logger.info(f"✅ Retrieved {len(images_data)} images")

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "images": images_data,
            "total_count": len(images_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching images: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch images: {str(e)}")


@router.get("/videos")
def get_videos(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    db: Session = Depends(get_db)
):
    """
    Get video assets from ad account library (REAL-TIME from Facebook Marketing API)

    Returns:
    - Video IDs
    - Video URLs
    - Video thumbnails
    - Video durations
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time videos from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)
        videos_data = meta_service.get_videos(account_id=account_id)

        logger.info(f"✅ Retrieved {len(videos_data)} videos")

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "videos": videos_data,
            "total_count": len(videos_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching videos: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch videos: {str(e)}")


# ==============================================================================
# LEAD GENERATION
# ==============================================================================

@router.get("/leads")
def get_leads(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    form_id: Optional[str] = Query(None, description="Filter by lead form ID"),
    db: Session = Depends(get_db)
):
    """
    Get lead form submissions from lead generation campaigns (REAL-TIME from Facebook Marketing API)

    Returns:
    - Lead contact information
    - Form responses
    - Lead creation time
    - Associated campaigns/ads
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time leads from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)
        leads_data = meta_service.get_leads(account_id=account_id, form_id=form_id)

        logger.info(f"✅ Retrieved {len(leads_data)} leads")

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "leads": leads_data,
            "total_count": len(leads_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching leads: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch leads: {str(e)}")


@router.get("/lead-forms/{form_id}/leads")
def get_lead_form_submissions(
    form_id: str,
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    db: Session = Depends(get_db)
):
    """Get all lead submissions for a specific lead form (REAL-TIME from Facebook Marketing API)"""

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time leads for specific form
        meta_service = get_meta_ads_service(account_id=account_id)
        leads_data = meta_service.get_leads(account_id=account_id, form_id=form_id)

        logger.info(f"✅ Retrieved {len(leads_data)} leads for form {form_id}")

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "form_id": form_id,
            "leads": leads_data,
            "total_count": len(leads_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching leads for form {form_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch leads: {str(e)}")


# ==============================================================================
# DEMOGRAPHIC & GEOGRAPHIC INSIGHTS
# ==============================================================================

@router.get("/insights/age-gender")
def get_insights_by_age_gender(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    date_range: str = Query('last_30d', description="Date range: last_7d, last_30d, etc."),
    level: str = Query('account', description="Level: account, campaign, adset, or ad"),
    db: Session = Depends(get_db)
):
    """
    Get performance breakdown by age and gender (REAL-TIME from Facebook Marketing API)

    Returns:
    - Performance metrics segmented by age groups (18-24, 25-34, 35-44, etc.)
    - Gender breakdown (male, female, unknown)
    - Combined age-gender segments
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time age/gender breakdown from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)
        insights_data = meta_service.get_insights_by_age_gender(
            account_id=account_id,
            date_range=date_range,
            level=level
        )

        logger.info(f"✅ Retrieved age/gender insights")

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "level": level,
            "date_range": date_range,
            "breakdown_type": "age_gender",
            "insights": insights_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching age/gender insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch age/gender insights: {str(e)}")


@router.get("/insights/country")
def get_insights_by_country(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    date_range: str = Query('last_30d', description="Date range: last_7d, last_30d, etc."),
    level: str = Query('account', description="Level: account, campaign, adset, or ad"),
    db: Session = Depends(get_db)
):
    """
    Get performance breakdown by country/region (REAL-TIME from Facebook Marketing API)

    Returns:
    - Performance metrics by country
    - Geographic targeting effectiveness
    - Regional conversion rates
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time country breakdown from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)
        insights_data = meta_service.get_insights_by_country(
            account_id=account_id,
            date_range=date_range,
            level=level
        )

        logger.info(f"✅ Retrieved country insights")

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "level": level,
            "date_range": date_range,
            "breakdown_type": "country",
            "insights": insights_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching country insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch country insights: {str(e)}")


@router.get("/insights/device")
def get_insights_by_device(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    date_range: str = Query('last_30d', description="Date range: last_7d, last_30d, etc."),
    level: str = Query('account', description="Level: account, campaign, adset, or ad"),
    db: Session = Depends(get_db)
):
    """
    Get performance breakdown by device platform (REAL-TIME from Facebook Marketing API)

    Returns:
    - Performance by device (mobile, desktop, tablet)
    - Device-specific conversion rates
    - Mobile vs desktop effectiveness
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time device breakdown from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)
        insights_data = meta_service.get_insights_by_device(
            account_id=account_id,
            date_range=date_range,
            level=level
        )

        logger.info(f"✅ Retrieved device insights")

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "level": level,
            "date_range": date_range,
            "breakdown_type": "device_platform",
            "insights": insights_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching device insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch device insights: {str(e)}")


@router.get("/insights/platform")
def get_insights_by_platform(
    customer_id: int = Query(..., description="Customer ID"),
    account_id: Optional[str] = Query(None, description="Meta Ad Account ID"),
    date_range: str = Query('last_30d', description="Date range: last_7d, last_30d, etc."),
    level: str = Query('account', description="Level: account, campaign, adset, or ad"),
    db: Session = Depends(get_db)
):
    """
    Get performance breakdown by publisher platform (REAL-TIME from Facebook Marketing API)

    Returns:
    - Performance by platform (Facebook, Instagram, Messenger, Audience Network)
    - Placement performance (feed, stories, reels, etc.)
    - Platform-specific ROAS
    """

    try:
        # Get account_id if not provided
        if not account_id:
            meta_account = db.query(models.MetaAdAccount).filter(
                models.MetaAdAccount.customer_id == customer_id,
                models.MetaAdAccount.is_active == True
            ).first()

            if not meta_account:
                raise HTTPException(status_code=404,
                    detail=f"No active Meta ad account found for customer {customer_id}")

            account_id = meta_account.account_id

        # Get real-time platform breakdown from Meta Ads API
        meta_service = get_meta_ads_service(account_id=account_id)
        insights_data = meta_service.get_insights_by_platform(
            account_id=account_id,
            date_range=date_range,
            level=level
        )

        logger.info(f"✅ Retrieved platform insights")

        return {
            "customer_id": customer_id,
            "account_id": account_id,
            "level": level,
            "date_range": date_range,
            "breakdown_type": "publisher_platform",
            "insights": insights_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching platform insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch platform insights: {str(e)}")
