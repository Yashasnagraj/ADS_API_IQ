"""
Customer endpoints for filtering
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.db.database import get_db
from app.db.models import Campaign, Customer
from pydantic import BaseModel

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
def get_customers(db: Session = Depends(get_db)):
    """
    Get list of all customers with their campaign counts
    """
    # Query distinct customers with campaign counts
    customers_data = db.query(
        Campaign.customer_id,
        func.count(Campaign.campaign_id).label("campaigns_count")
    ).group_by(Campaign.customer_id).all()

    # Build customer list with actual customer names
    customers = []
    for customer_id, campaigns_count in customers_data:
        # Try to get customer name from customers table
        customer_record = db.query(Customer).filter(Customer.customer_id == customer_id).first()

        customer_name = customer_record.customer_name if customer_record else f"Customer {customer_id}"

        customer = CustomerInfo(
            customer_id=customer_id,
            customer_name=customer_name,
            campaigns_count=campaigns_count
        )
        customers.append(customer)

    return CustomerListResponse(
        customers=customers,
        total=len(customers)
    )

@router.get("/{customer_id}/summary")
def get_customer_summary(customer_id: int, db: Session = Depends(get_db)):
    """
    Get summary metrics for a specific customer
    """
    from app.db.models import CampaignKeyword

    # Get customer name
    customer_record = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    customer_name = customer_record.customer_name if customer_record else f"Customer {customer_id}"

    # Get campaign count
    campaigns_count = db.query(func.count(distinct(Campaign.campaign_id)))\
        .filter(Campaign.customer_id == customer_id)\
        .scalar() or 0

    # Get aggregate metrics
    metrics = db.query(
        func.coalesce(func.sum(CampaignKeyword.clicks), 0).label("total_clicks"),
        func.coalesce(func.sum(CampaignKeyword.impressions), 0).label("total_impressions"),
        func.coalesce(func.sum(CampaignKeyword.cost_micros), 0).label("total_cost_micros"),
        func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("total_conversions"),
    ).filter(CampaignKeyword.customer_id == customer_id).first()

    total_clicks = metrics.total_clicks or 0
    total_impressions = metrics.total_impressions or 0
    total_cost_micros = metrics.total_cost_micros or 0
    total_conversions = metrics.total_conversions or 0

    return {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "campaigns_count": campaigns_count,
        "metrics": {
            "clicks": total_clicks,
            "impressions": total_impressions,
            "cost": total_cost_micros / 1_000_000 if total_cost_micros else 0,
            "conversions": total_conversions,
            "ctr": total_clicks / total_impressions if total_impressions > 0 else 0,
            "conversion_rate": total_conversions / total_clicks if total_clicks > 0 else 0,
            "avg_cpc": total_cost_micros / total_clicks / 1_000_000 if total_clicks > 0 else 0
        }
    }