"""
Shopify E-commerce Integration Endpoints
Provides access to Shopify orders, products, customers, and attribution data
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from app.db.database import get_db
from app.db.models import ShopifyStore, ShopifyOrder, ShopifyProduct, ShopifyCustomer, ShopifyCartEvent
from app.schemas.shopify import (
    ShopifyStoreList, ShopifyStoreResponse,
    ShopifyOrderList, ShopifyOrderResponse, ShopifyOrderFilter,
    ShopifyProductList, ShopifyProductResponse, ShopifyProductPerformance,
    ShopifyCustomerList, ShopifyCustomerResponse, ShopifyCustomerLTV, ShopifyCustomerLTVList,
    ShopifyCartEventList, ShopifyCartEventResponse,
    ShopifyRevenueAttribution, ShopifyRevenueAttributionList,
    ShopifyCartAbandonmentMetrics,
    ShopifyIntegrationStatus
)
from app.core.config import settings
from datetime import datetime, timedelta

router = APIRouter(prefix="/shopify", tags=["shopify"])


# ==============================================================================
# STORE MANAGEMENT ENDPOINTS
# ==============================================================================

@router.get("/stores", response_model=ShopifyStoreList)
def get_shopify_stores(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    db: Session = Depends(get_db)
):
    """
    List all connected Shopify stores

    Filter by customer_id to show only specific customer's stores
    """
    query = db.query(ShopifyStore).filter(ShopifyStore.is_active == True)

    if customer_id:
        query = query.filter(ShopifyStore.customer_id == customer_id)

    stores = query.all()

    return ShopifyStoreList(
        stores=stores,
        total=len(stores)
    )


@router.get("/stores/{store_id}", response_model=ShopifyStoreResponse)
def get_shopify_store(store_id: str, db: Session = Depends(get_db)):
    """Get details of a specific Shopify store"""
    store = db.query(ShopifyStore).filter(ShopifyStore.store_id == store_id).first()

    if not store:
        raise HTTPException(status_code=404, detail=f"Store {store_id} not found")

    return store


@router.get("/integration/status", response_model=ShopifyIntegrationStatus)
def get_integration_status(
    customer_id: int = Query(..., description="Customer ID"),
    db: Session = Depends(get_db)
):
    """Get Shopify integration status for a customer"""

    # Count stores
    stores = db.query(ShopifyStore).filter(ShopifyStore.customer_id == customer_id)
    stores_count = stores.count()
    active_stores = stores.filter(ShopifyStore.is_active == True).count()

    # Get last sync
    last_sync = stores.order_by(desc(ShopifyStore.last_sync_at)).first()
    last_sync_at = last_sync.last_sync_at if last_sync else None

    # Data summary
    total_orders = db.query(func.count(ShopifyOrder.order_id)).filter(
        ShopifyOrder.customer_id == customer_id
    ).scalar() or 0

    total_products = db.query(func.count(ShopifyProduct.product_id)).filter(
        ShopifyProduct.customer_id == customer_id
    ).scalar() or 0

    total_customers = db.query(func.count(ShopifyCustomer.shopify_customer_id)).filter(
        ShopifyCustomer.customer_id == customer_id
    ).scalar() or 0

    total_revenue = db.query(func.sum(ShopifyOrder.total_price)).filter(
        and_(
            ShopifyOrder.customer_id == customer_id,
            ShopifyOrder.financial_status == 'paid'
        )
    ).scalar() or 0

    # Attribution coverage
    orders_with_gclid = db.query(func.count(ShopifyOrder.order_id)).filter(
        and_(
            ShopifyOrder.customer_id == customer_id,
            ShopifyOrder.gclid.isnot(None)
        )
    ).scalar() or 0

    attribution_coverage = (orders_with_gclid / total_orders * 100) if total_orders > 0 else 0

    return ShopifyIntegrationStatus(
        customer_id=customer_id,
        is_connected=stores_count > 0,
        stores_count=stores_count,
        active_stores=active_stores,
        last_sync_at=last_sync_at,
        total_orders=total_orders,
        total_products=total_products,
        total_customers=total_customers,
        total_revenue=total_revenue,
        orders_with_gclid=orders_with_gclid,
        attribution_coverage=attribution_coverage
    )


# ==============================================================================
# ORDER ENDPOINTS
# ==============================================================================

@router.get("/orders", response_model=ShopifyOrderList)
def get_orders(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    financial_status: Optional[str] = Query(None, description="Filter by financial status"),
    fulfillment_status: Optional[str] = Query(None, description="Filter by fulfillment status"),
    has_gclid: Optional[bool] = Query(None, description="Filter orders with Google Click ID"),
    utm_source: Optional[str] = Query(None, description="Filter by UTM source"),
    utm_campaign: Optional[str] = Query(None, description="Filter by UTM campaign"),
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List Shopify orders with filtering options

    Supports filtering by:
    - customer_id: Your customer account
    - store_id: Specific Shopify store
    - Date range
    - Financial status (paid, pending, refunded, etc.)
    - Fulfillment status
    - Attribution (has_gclid, utm_source, utm_campaign)
    """
    query = db.query(ShopifyOrder)

    if customer_id:
        query = query.filter(ShopifyOrder.customer_id == customer_id)

    if store_id:
        query = query.filter(ShopifyOrder.store_id == store_id)

    if start_date:
        query = query.filter(ShopifyOrder.created_at_shopify >= start_date)

    if end_date:
        query = query.filter(ShopifyOrder.created_at_shopify <= end_date)

    if financial_status:
        query = query.filter(ShopifyOrder.financial_status == financial_status)

    if fulfillment_status:
        query = query.filter(ShopifyOrder.fulfillment_status == fulfillment_status)

    if has_gclid is not None:
        if has_gclid:
            query = query.filter(ShopifyOrder.gclid.isnot(None))
        else:
            query = query.filter(ShopifyOrder.gclid.is_(None))

    if utm_source:
        query = query.filter(ShopifyOrder.utm_source == utm_source)

    if utm_campaign:
        query = query.filter(ShopifyOrder.utm_campaign == utm_campaign)

    total = query.count()

    # Calculate total revenue
    total_revenue = query.with_entities(func.sum(ShopifyOrder.total_price)).scalar() or 0

    orders = query.order_by(desc(ShopifyOrder.created_at_shopify)).offset(offset).limit(limit).all()

    return ShopifyOrderList(
        orders=orders,
        total=total,
        total_revenue=total_revenue
    )


@router.get("/orders/{order_id}", response_model=ShopifyOrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get details of a specific Shopify order"""
    order = db.query(ShopifyOrder).filter(ShopifyOrder.order_id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    return order


# ==============================================================================
# PRODUCT ENDPOINTS
# ==============================================================================

@router.get("/products", response_model=ShopifyProductList)
def get_products(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    product_type: Optional[str] = Query(None, description="Filter by product type"),
    status: Optional[str] = Query(None, description="Filter by status (active, archived, draft)"),
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List Shopify products from catalog

    Filter by customer_id, store_id, product_type, or status
    """
    query = db.query(ShopifyProduct)

    if customer_id:
        query = query.filter(ShopifyProduct.customer_id == customer_id)

    if store_id:
        query = query.filter(ShopifyProduct.store_id == store_id)

    if product_type:
        query = query.filter(ShopifyProduct.product_type == product_type)

    if status:
        query = query.filter(ShopifyProduct.status == status)

    total = query.count()
    products = query.offset(offset).limit(limit).all()

    return ShopifyProductList(
        products=products,
        total=total
    )


@router.get("/products/{product_id}", response_model=ShopifyProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get details of a specific Shopify product"""
    product = db.query(ShopifyProduct).filter(ShopifyProduct.product_id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    return product


@router.get("/products/performance/ranking", response_model=list[ShopifyProductPerformance])
def get_product_performance(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get product performance ranking

    Returns products sorted by total revenue with order counts
    Note: This is a simplified version. For accurate product-level attribution,
    you would need to parse line_items from orders.
    """
    # This is a placeholder that shows products with store info
    # In production, you'd need to:
    # 1. Parse line_items JSON from orders
    # 2. Join with products
    # 3. Calculate revenue per product

    query = db.query(ShopifyProduct)

    if customer_id:
        query = query.filter(ShopifyProduct.customer_id == customer_id)

    if store_id:
        query = query.filter(ShopifyProduct.store_id == store_id)

    products = query.filter(ShopifyProduct.status == 'active').order_by(
        desc(ShopifyProduct.price)
    ).limit(limit).all()

    # Format as performance data
    performance_list = []
    for idx, product in enumerate(products, start=1):
        performance_list.append(ShopifyProductPerformance(
            product_id=product.product_id,
            title=product.title,
            vendor=product.vendor,
            product_type=product.product_type,
            price=product.price,
            image_url=product.image_url,
            orders_count=0,  # Would need line_items parsing
            total_revenue=0,  # Would need line_items parsing
            avg_order_value=0,
            inventory_quantity=product.inventory_quantity,
            performance_rank=idx
        ))

    return performance_list


# ==============================================================================
# CUSTOMER ENDPOINTS
# ==============================================================================

@router.get("/customers", response_model=ShopifyCustomerList)
def get_customers(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List Shopify customers

    Filter by customer_id or store_id
    """
    query = db.query(ShopifyCustomer)

    if customer_id:
        query = query.filter(ShopifyCustomer.customer_id == customer_id)

    if store_id:
        query = query.filter(ShopifyCustomer.store_id == store_id)

    total = query.count()

    # Calculate aggregates
    total_ltv = query.with_entities(func.sum(ShopifyCustomer.total_spent)).scalar() or 0
    avg_ltv = (total_ltv / total) if total > 0 else 0

    customers = query.order_by(desc(ShopifyCustomer.total_spent)).offset(offset).limit(limit).all()

    return ShopifyCustomerList(
        customers=customers,
        total=total,
        total_ltv=total_ltv,
        avg_ltv=avg_ltv
    )


@router.get("/customers/ltv", response_model=ShopifyCustomerLTVList)
def get_customer_ltv(
    customer_id: int = Query(..., description="Customer ID"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    min_ltv: Optional[float] = Query(None, description="Minimum LTV filter"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get customer lifetime value analysis

    Returns customers sorted by LTV with acquisition attribution
    """
    query = db.query(ShopifyCustomer).filter(ShopifyCustomer.customer_id == customer_id)

    if store_id:
        query = query.filter(ShopifyCustomer.store_id == store_id)

    if min_ltv:
        query = query.filter(ShopifyCustomer.total_spent >= min_ltv)

    total = query.count()

    # Get total and average LTV
    total_ltv = query.with_entities(func.sum(ShopifyCustomer.total_spent)).scalar() or 0
    avg_ltv = (total_ltv / total) if total > 0 else 0

    customers = query.order_by(desc(ShopifyCustomer.total_spent)).offset(offset).limit(limit).all()

    # Format as LTV data
    ltv_list = []
    for cust in customers:
        # Calculate customer segment
        if cust.total_spent >= 1000:
            segment = "HIGH_VALUE"
        elif cust.total_spent >= 300:
            segment = "MEDIUM_VALUE"
        else:
            segment = "LOW_VALUE"

        # Calculate days as customer
        days_as_customer = None
        if cust.created_at_shopify and cust.last_order_at:
            delta = cust.last_order_at - cust.created_at_shopify
            days_as_customer = delta.days

        ltv_list.append(ShopifyCustomerLTV(
            customer_id_shopify=cust.shopify_customer_id,
            email=cust.email,
            first_name=cust.first_name,
            last_name=cust.last_name,
            total_spent=cust.total_spent,
            orders_count=cust.orders_count,
            average_order_value=cust.average_order_value or 0,
            lifetime_value=cust.total_spent,
            acquisition_source=cust.first_order_utm_source,
            acquisition_campaign=cust.first_order_utm_campaign,
            first_order_date=cust.created_at_shopify,
            last_order_date=cust.last_order_at,
            days_as_customer=days_as_customer,
            customer_segment=segment,
            repeat_customer=cust.orders_count > 1
        ))

    return ShopifyCustomerLTVList(
        customers=ltv_list,
        total=total,
        avg_ltv=avg_ltv,
        total_ltv=total_ltv
    )


# ==============================================================================
# REVENUE ATTRIBUTION ENDPOINTS (CRITICAL FOR GOOGLE ADS ROAS)
# ==============================================================================

@router.get("/attribution/revenue", response_model=ShopifyRevenueAttributionList)
def get_revenue_attribution(
    customer_id: int = Query(..., description="Customer ID"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get revenue attribution by Google Ads campaigns

    Links Shopify orders to Google Ads via GCLID and UTM parameters
    Returns revenue grouped by campaign for TRUE ROAS calculation

    This is CRITICAL for calculating true ROAS:
    - Google Ads API gives you Ad Spend
    - This endpoint gives you Actual Revenue
    - True ROAS = Revenue / Ad Spend
    """
    query = db.query(
        ShopifyOrder.utm_source,
        ShopifyOrder.utm_campaign,
        func.count(ShopifyOrder.order_id).label('orders_count'),
        func.sum(ShopifyOrder.total_price).label('total_revenue'),
        func.avg(ShopifyOrder.total_price).label('avg_order_value'),
        func.count(func.distinct(ShopifyOrder.shopify_customer_id)).label('unique_customers')
    ).filter(
        ShopifyOrder.customer_id == customer_id,
        ShopifyOrder.financial_status == 'paid'
    ).filter(
        ShopifyOrder.utm_source.isnot(None)  # Only orders with attribution
    )

    if store_id:
        query = query.filter(ShopifyOrder.store_id == store_id)

    if start_date:
        query = query.filter(ShopifyOrder.created_at_shopify >= start_date)

    if end_date:
        query = query.filter(ShopifyOrder.created_at_shopify <= end_date)

    query = query.group_by(ShopifyOrder.utm_source, ShopifyOrder.utm_campaign)
    results = query.all()

    # Format results
    attributions = []
    total_revenue = 0
    total_orders = 0

    for row in results:
        # Count new vs returning customers
        # (Simplified - would need more complex query for accurate count)
        new_customers = row.unique_customers  # Approximate
        returning_customers = row.orders_count - new_customers if row.orders_count > new_customers else 0

        has_gclid = True  # Would need to check in actual implementation

        attributions.append(ShopifyRevenueAttribution(
            campaign_id=None,  # Could be joined from campaigns table
            campaign_name=row.utm_campaign,
            utm_source=row.utm_source,
            utm_campaign=row.utm_campaign,
            orders_count=row.orders_count,
            total_revenue=row.total_revenue,
            avg_order_value=row.avg_order_value,
            unique_customers=row.unique_customers,
            new_customers=max(new_customers, 0),
            returning_customers=max(returning_customers, 0),
            has_gclid=has_gclid
        ))

        total_revenue += row.total_revenue
        total_orders += row.orders_count

    # Calculate attribution coverage
    all_orders = db.query(func.count(ShopifyOrder.order_id)).filter(
        ShopifyOrder.customer_id == customer_id,
        ShopifyOrder.financial_status == 'paid'
    ).scalar() or 1

    attribution_coverage = (total_orders / all_orders * 100)

    return ShopifyRevenueAttributionList(
        attributions=attributions,
        total_attributed_revenue=total_revenue,
        total_attributed_orders=total_orders,
        attribution_coverage=attribution_coverage
    )


# ==============================================================================
# CART ABANDONMENT ENDPOINTS
# ==============================================================================

@router.get("/cart-events", response_model=ShopifyCartEventList)
def get_cart_events(
    customer_id: int = Query(..., description="Customer ID"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """List cart events (for cart abandonment tracking)"""
    query = db.query(ShopifyCartEvent).filter(ShopifyCartEvent.customer_id == customer_id)

    if store_id:
        query = query.filter(ShopifyCartEvent.store_id == store_id)

    if event_type:
        query = query.filter(ShopifyCartEvent.event_type == event_type)

    total = query.count()

    # Calculate abandonment rate
    abandoned = query.filter(ShopifyCartEvent.event_type == 'checkout_abandoned').count()
    abandonment_rate = (abandoned / total * 100) if total > 0 else 0

    events = query.order_by(desc(ShopifyCartEvent.event_at)).offset(offset).limit(limit).all()

    return ShopifyCartEventList(
        events=events,
        total=total,
        abandonment_rate=abandonment_rate
    )


@router.get("/cart-abandonment/metrics", response_model=ShopifyCartAbandonmentMetrics)
def get_cart_abandonment_metrics(
    customer_id: int = Query(..., description="Customer ID"),
    store_id: Optional[str] = Query(None, description="Filter by store ID"),
    days_back: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get cart abandonment analytics

    Returns funnel metrics:
    - Carts created
    - Checkouts started
    - Checkouts abandoned
    - Orders completed
    - Conversion rates at each stage
    """
    # Get events from last N days
    since_date = datetime.now() - timedelta(days=days_back)

    query = db.query(ShopifyCartEvent).filter(
        ShopifyCartEvent.customer_id == customer_id,
        ShopifyCartEvent.event_at >= since_date
    )

    if store_id:
        query = query.filter(ShopifyCartEvent.store_id == store_id)

    # Count events by type
    total_carts = query.filter(ShopifyCartEvent.event_type.in_(['cart_created', 'cart_updated'])).count()
    total_checkouts = query.filter(ShopifyCartEvent.event_type == 'checkout_started').count()
    abandoned_checkouts = query.filter(ShopifyCartEvent.event_type == 'checkout_abandoned').count()

    # Count completed orders
    completed_orders = query.filter(
        ShopifyCartEvent.completed_order_id.isnot(None)
    ).count()

    # Calculate rates
    cart_to_checkout_rate = (total_checkouts / total_carts * 100) if total_carts > 0 else 0
    checkout_to_order_rate = (completed_orders / total_checkouts * 100) if total_checkouts > 0 else 0
    overall_conversion_rate = (completed_orders / total_carts * 100) if total_carts > 0 else 0
    abandonment_rate = (abandoned_checkouts / total_checkouts * 100) if total_checkouts > 0 else 0

    # Calculate financial metrics
    abandoned_revenue = query.filter(
        ShopifyCartEvent.event_type == 'checkout_abandoned'
    ).with_entities(func.sum(ShopifyCartEvent.total_price)).scalar() or 0

    recovered_revenue = query.filter(
        ShopifyCartEvent.completed_order_id.isnot(None)
    ).with_entities(func.sum(ShopifyCartEvent.total_price)).scalar() or 0

    recovery_rate = (recovered_revenue / abandoned_revenue * 100) if abandoned_revenue > 0 else 0

    return ShopifyCartAbandonmentMetrics(
        total_carts=total_carts,
        total_checkouts=total_checkouts,
        abandoned_checkouts=abandoned_checkouts,
        completed_orders=completed_orders,
        cart_to_checkout_rate=cart_to_checkout_rate,
        checkout_to_order_rate=checkout_to_order_rate,
        overall_conversion_rate=overall_conversion_rate,
        abandonment_rate=abandonment_rate,
        abandoned_revenue=abandoned_revenue,
        recovered_revenue=recovered_revenue,
        recovery_rate=recovery_rate
    )
