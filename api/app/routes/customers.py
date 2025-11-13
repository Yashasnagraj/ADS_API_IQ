"""
Customer endpoints for filtering
Uses real-time Google Ads API queries
"""
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.google_ads_service import get_google_ads_service
from app.services.gaql_builder import QueryTemplates, DateRange
from loguru import logger

router = APIRouter(prefix="/customers", tags=["customers"])

class CustomerInfo(BaseModel):
    """Customer information"""
    customer_id: int
    customer_name: str
    campaigns_count: int

    class Config:
        from_attributes = True

class CustomerListResponse(BaseModel):
    """Response for customer list"""
    customers: List[CustomerInfo]
    total: int

@router.get("", response_model=CustomerListResponse)
def get_customers():
    """
    Get list of all client customers (not manager accounts)
    Real-time query from Google Ads API - optimized for speed
    """
    try:
        ads_service = get_google_ads_service()

        # Get manager account ID from env
        import os
        manager_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "3341907700")

        # Get list of client accounts under the manager
        client_accounts = ads_service.list_client_accounts(manager_customer_id)

        customers = []
        for client_data in client_accounts:
            customer_id = int(client_data["customer_id"])

            # Skip campaign count for faster loading - just return customer list
            # The campaign count can be fetched separately if needed
            customers.append(CustomerInfo(
                customer_id=customer_id,
                customer_name=client_data.get("descriptive_name", f"Customer {customer_id}"),
                campaigns_count=0  # Set to 0 for fast loading
            ))

        return CustomerListResponse(
            customers=customers,
            total=len(customers)
        )

    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers: {str(e)}")

@router.get("/{customer_id}/summary")
def get_customer_summary(customer_id: int):
    """
    Get summary metrics for a specific customer
    Real-time aggregated metrics from Google Ads API
    """
    try:
        ads_service = get_google_ads_service()
        customer_id_str = str(customer_id)

        # Get customer info
        customer_info = ads_service.get_customer_info(customer_id_str)
        customer_name = "Unknown Customer"
        if customer_info and "customer" in customer_info:
            customer_name = customer_info["customer"].get("descriptive_name", f"Customer {customer_id}")

        # Get campaigns and aggregate metrics
        campaigns = ads_service.get_campaigns(customer_id_str, date_range="LAST_30_DAYS")

        # Aggregate metrics across all campaigns
        total_clicks = 0
        total_impressions = 0
        total_cost_micros = 0
        total_conversions = 0.0

        for campaign in campaigns:
            metrics = campaign.get("metrics", {})
            total_clicks += int(metrics.get("clicks", 0) or 0)
            total_impressions += int(metrics.get("impressions", 0) or 0)
            total_cost_micros += int(metrics.get("cost_micros", 0) or 0)
            total_conversions += float(metrics.get("conversions", 0) or 0)

        return {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "campaigns_count": len(campaigns),
            "metrics": {
                "clicks": total_clicks,
                "impressions": total_impressions,
                "cost": total_cost_micros / 1_000_000 if total_cost_micros else 0,
                "conversions": total_conversions,
                "ctr": (total_clicks / total_impressions * 100) if total_impressions > 0 else 0,
                "conversion_rate": (total_conversions / total_clicks * 100) if total_clicks > 0 else 0,
                "avg_cpc": (total_cost_micros / total_clicks / 1_000_000) if total_clicks > 0 else 0
            }
        }

    except Exception as e:
        logger.error(f"Error fetching customer summary for {customer_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch customer summary: {str(e)}")
