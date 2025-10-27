"""
Shopify Integration Schemas
Pydantic models for Shopify e-commerce data
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ==============================================================================
# SHOPIFY STORE SCHEMAS
# ==============================================================================

class ShopifyStoreBase(BaseModel):
    """Base Shopify store schema"""
    shop_domain: str = Field(..., description="Shopify domain (e.g., mystore.myshopify.com)")
    shop_name: Optional[str] = Field(None, description="Store name")
    email: Optional[str] = Field(None, description="Store owner email")
    currency: str = Field(default="USD", description="Store currency")
    timezone: Optional[str] = Field(None, description="Store timezone")


class ShopifyStoreCreate(ShopifyStoreBase):
    """Create Shopify store connection"""
    customer_id: int = Field(..., description="Customer ID")
    access_token: str = Field(..., description="Shopify API access token")
    scope: Optional[str] = Field(None, description="OAuth scopes")


class ShopifyStoreResponse(ShopifyStoreBase):
    """Shopify store response"""
    store_id: str
    customer_id: int
    is_active: bool
    installed_at: datetime
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShopifyStoreList(BaseModel):
    """List of Shopify stores"""
    stores: List[ShopifyStoreResponse]
    total: int


# ==============================================================================
# SHOPIFY ORDER SCHEMAS
# ==============================================================================

class ShopifyOrderBase(BaseModel):
    """Base Shopify order schema"""
    order_number: str = Field(..., description="Human-readable order number")
    order_name: Optional[str] = Field(None, description="Order name (e.g., #1001)")
    email: Optional[str] = Field(None, description="Customer email")

    # Financial
    total_price: float = Field(..., description="Total order price")
    subtotal_price: Optional[float] = Field(None, description="Subtotal")
    total_tax: Optional[float] = Field(None, description="Total tax")
    total_discounts: Optional[float] = Field(None, description="Total discounts")
    total_shipping: Optional[float] = Field(None, description="Shipping cost")
    currency: str = Field(default="USD", description="Order currency")
    financial_status: Optional[str] = Field(None, description="Payment status")
    fulfillment_status: Optional[str] = Field(None, description="Fulfillment status")

    # Attribution
    gclid: Optional[str] = Field(None, description="Google Click ID for attribution")
    utm_source: Optional[str] = Field(None, description="UTM source")
    utm_medium: Optional[str] = Field(None, description="UTM medium")
    utm_campaign: Optional[str] = Field(None, description="UTM campaign")
    utm_term: Optional[str] = Field(None, description="UTM term")
    utm_content: Optional[str] = Field(None, description="UTM content")
    landing_site: Optional[str] = Field(None, description="Landing page URL")
    referring_site: Optional[str] = Field(None, description="Referring site URL")

    # Customer
    shopify_customer_id: Optional[str] = Field(None, description="Shopify customer ID")
    customer_first_name: Optional[str] = Field(None, description="Customer first name")
    customer_last_name: Optional[str] = Field(None, description="Customer last name")


class ShopifyOrderCreate(ShopifyOrderBase):
    """Create Shopify order"""
    order_id: str = Field(..., description="Shopify order ID")
    store_id: str = Field(..., description="Store ID")
    customer_id: int = Field(..., description="Customer ID")
    created_at_shopify: Optional[datetime] = None
    updated_at_shopify: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    line_items_count: Optional[int] = None
    tags: Optional[str] = None
    note: Optional[str] = None


class ShopifyOrderResponse(ShopifyOrderBase):
    """Shopify order response"""
    order_id: str
    store_id: str
    customer_id: int
    line_items_count: Optional[int] = None
    created_at_shopify: Optional[datetime] = None
    updated_at_shopify: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShopifyOrderList(BaseModel):
    """List of Shopify orders"""
    orders: List[ShopifyOrderResponse]
    total: int
    total_revenue: float = Field(..., description="Sum of all order totals")


class ShopifyOrderFilter(BaseModel):
    """Filters for Shopify orders"""
    customer_id: Optional[int] = None
    store_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    financial_status: Optional[str] = None
    fulfillment_status: Optional[str] = None
    has_gclid: Optional[bool] = Field(None, description="Filter orders with Google Click ID")
    utm_source: Optional[str] = None
    utm_campaign: Optional[str] = None
    limit: int = Field(default=50, le=1000)
    offset: int = Field(default=0, ge=0)


# ==============================================================================
# SHOPIFY PRODUCT SCHEMAS
# ==============================================================================

class ShopifyProductBase(BaseModel):
    """Base Shopify product schema"""
    title: str = Field(..., description="Product title")
    body_html: Optional[str] = Field(None, description="Product description HTML")
    vendor: Optional[str] = Field(None, description="Product vendor")
    product_type: Optional[str] = Field(None, description="Product type/category")
    handle: Optional[str] = Field(None, description="URL handle")
    variants_count: Optional[int] = Field(None, description="Number of variants")
    inventory_quantity: Optional[int] = Field(None, description="Total inventory")
    price: Optional[float] = Field(None, description="Product price")
    compare_at_price: Optional[float] = Field(None, description="Compare at price")
    status: Optional[str] = Field(None, description="Product status (active, archived, draft)")
    tags: Optional[str] = Field(None, description="Product tags")
    image_url: Optional[str] = Field(None, description="Primary image URL")


class ShopifyProductCreate(ShopifyProductBase):
    """Create Shopify product"""
    product_id: str = Field(..., description="Shopify product ID")
    store_id: str = Field(..., description="Store ID")
    customer_id: int = Field(..., description="Customer ID")
    created_at_shopify: Optional[datetime] = None
    updated_at_shopify: Optional[datetime] = None
    published_at: Optional[datetime] = None


class ShopifyProductResponse(ShopifyProductBase):
    """Shopify product response"""
    product_id: str
    store_id: str
    customer_id: int
    created_at_shopify: Optional[datetime] = None
    updated_at_shopify: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShopifyProductList(BaseModel):
    """List of Shopify products"""
    products: List[ShopifyProductResponse]
    total: int


class ShopifyProductPerformance(BaseModel):
    """Product performance with sales data"""
    product_id: str
    title: str
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None

    # Performance metrics
    orders_count: int = Field(..., description="Number of orders containing this product")
    total_revenue: float = Field(..., description="Total revenue from this product")
    avg_order_value: float = Field(..., description="Average order value for orders with this product")
    inventory_quantity: Optional[int] = None

    # Ranking
    performance_rank: int = Field(..., description="Performance rank (1=best)")


# ==============================================================================
# SHOPIFY CUSTOMER SCHEMAS
# ==============================================================================

class ShopifyCustomerBase(BaseModel):
    """Base Shopify customer schema"""
    email: Optional[str] = Field(None, description="Customer email")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    phone: Optional[str] = Field(None, description="Phone number")
    accepts_marketing: Optional[bool] = Field(None, description="Accepts marketing emails")
    total_spent: float = Field(default=0.0, description="Total amount spent")
    orders_count: int = Field(default=0, description="Total orders count")
    average_order_value: Optional[float] = Field(None, description="Average order value")

    # Attribution
    first_order_gclid: Optional[str] = Field(None, description="Google Click ID from first order")
    first_order_utm_source: Optional[str] = Field(None, description="UTM source from first order")
    first_order_utm_campaign: Optional[str] = Field(None, description="UTM campaign from first order")

    # Location
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None


class ShopifyCustomerCreate(ShopifyCustomerBase):
    """Create Shopify customer"""
    shopify_customer_id: str = Field(..., description="Shopify customer ID")
    store_id: str = Field(..., description="Store ID")
    customer_id: int = Field(..., description="Customer ID")
    created_at_shopify: Optional[datetime] = None
    updated_at_shopify: Optional[datetime] = None
    last_order_at: Optional[datetime] = None


class ShopifyCustomerResponse(ShopifyCustomerBase):
    """Shopify customer response"""
    shopify_customer_id: str
    store_id: str
    customer_id: int
    state: Optional[str] = None
    verified_email: Optional[bool] = None
    created_at_shopify: Optional[datetime] = None
    updated_at_shopify: Optional[datetime] = None
    last_order_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShopifyCustomerList(BaseModel):
    """List of Shopify customers"""
    customers: List[ShopifyCustomerResponse]
    total: int
    total_ltv: float = Field(..., description="Total lifetime value of all customers")
    avg_ltv: float = Field(..., description="Average lifetime value per customer")


# ==============================================================================
# SHOPIFY CART EVENT SCHEMAS
# ==============================================================================

class ShopifyCartEventBase(BaseModel):
    """Base Shopify cart event schema"""
    cart_token: Optional[str] = Field(None, description="Cart token")
    checkout_token: Optional[str] = Field(None, description="Checkout token")
    customer_email: Optional[str] = Field(None, description="Customer email")
    event_type: str = Field(..., description="Event type (cart_created, checkout_started, checkout_abandoned)")
    total_price: Optional[float] = Field(None, description="Cart total")
    currency: str = Field(default="USD", description="Currency")
    line_items_count: Optional[int] = Field(None, description="Number of items in cart")

    # Attribution
    gclid: Optional[str] = Field(None, description="Google Click ID")
    utm_source: Optional[str] = Field(None, description="UTM source")
    utm_campaign: Optional[str] = Field(None, description="UTM campaign")
    landing_site: Optional[str] = Field(None, description="Landing site")

    # Products
    products_json: Optional[str] = Field(None, description="JSON array of products")

    # Recovery
    abandoned_checkout_url: Optional[str] = Field(None, description="Recovery URL")
    completed_order_id: Optional[str] = Field(None, description="Order ID if converted")

    event_at: datetime = Field(..., description="Event timestamp")


class ShopifyCartEventCreate(ShopifyCartEventBase):
    """Create Shopify cart event"""
    event_id: str = Field(..., description="Event ID (UUID)")
    store_id: str = Field(..., description="Store ID")
    customer_id: int = Field(..., description="Customer ID")


class ShopifyCartEventResponse(ShopifyCartEventBase):
    """Shopify cart event response"""
    event_id: str
    store_id: str
    customer_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ShopifyCartEventList(BaseModel):
    """List of Shopify cart events"""
    events: List[ShopifyCartEventResponse]
    total: int
    abandonment_rate: Optional[float] = Field(None, description="Cart abandonment rate %")


# ==============================================================================
# SHOPIFY ATTRIBUTION & ANALYTICS SCHEMAS
# ==============================================================================

class ShopifyRevenueAttribution(BaseModel):
    """Revenue attribution by Google Ads campaign"""
    campaign_id: Optional[int] = None
    campaign_name: Optional[str] = None
    utm_source: Optional[str] = None
    utm_campaign: Optional[str] = None

    # Orders
    orders_count: int = Field(..., description="Number of orders attributed")
    total_revenue: float = Field(..., description="Total revenue attributed")
    avg_order_value: float = Field(..., description="Average order value")

    # Customers
    unique_customers: int = Field(..., description="Number of unique customers")
    new_customers: int = Field(..., description="Number of new customers")
    returning_customers: int = Field(..., description="Number of returning customers")

    # Attribution quality
    has_gclid: bool = Field(..., description="Has Google Click ID for precise attribution")


class ShopifyRevenueAttributionList(BaseModel):
    """List of revenue attributions"""
    attributions: List[ShopifyRevenueAttribution]
    total_attributed_revenue: float
    total_attributed_orders: int
    attribution_coverage: float = Field(..., description="% of orders with attribution data")


class ShopifyCartAbandonmentMetrics(BaseModel):
    """Cart abandonment analytics"""
    total_carts: int = Field(..., description="Total carts created")
    total_checkouts: int = Field(..., description="Total checkouts started")
    abandoned_checkouts: int = Field(..., description="Abandoned checkouts")
    completed_orders: int = Field(..., description="Completed orders")

    # Rates
    cart_to_checkout_rate: float = Field(..., description="% of carts that reach checkout")
    checkout_to_order_rate: float = Field(..., description="% of checkouts that complete")
    overall_conversion_rate: float = Field(..., description="% of carts that convert to orders")
    abandonment_rate: float = Field(..., description="Cart abandonment rate %")

    # Financial
    abandoned_revenue: float = Field(..., description="Potential revenue in abandoned carts")
    recovered_revenue: float = Field(..., description="Revenue from recovered carts")
    recovery_rate: float = Field(..., description="% of abandoned carts recovered")


class ShopifyCustomerLTV(BaseModel):
    """Customer lifetime value analysis"""
    customer_id_shopify: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    # LTV metrics
    total_spent: float
    orders_count: int
    average_order_value: float
    lifetime_value: float

    # Acquisition
    acquisition_source: Optional[str] = Field(None, description="First touch attribution source")
    acquisition_campaign: Optional[str] = Field(None, description="First touch campaign")
    first_order_date: Optional[datetime] = None
    last_order_date: Optional[datetime] = None
    days_as_customer: Optional[int] = None

    # Segmentation
    customer_segment: str = Field(..., description="HIGH_VALUE, MEDIUM_VALUE, LOW_VALUE")
    repeat_customer: bool = Field(..., description="Has more than 1 order")


class ShopifyCustomerLTVList(BaseModel):
    """List of customer LTV data"""
    customers: List[ShopifyCustomerLTV]
    total: int
    avg_ltv: float
    total_ltv: float


# ==============================================================================
# SHOPIFY INTEGRATION STATUS SCHEMAS
# ==============================================================================

class ShopifyIntegrationStatus(BaseModel):
    """Shopify integration status"""
    customer_id: int
    is_connected: bool
    stores_count: int
    active_stores: int
    last_sync_at: Optional[datetime] = None

    # Data summary
    total_orders: int
    total_products: int
    total_customers: int
    total_revenue: float

    # Attribution coverage
    orders_with_gclid: int
    attribution_coverage: float = Field(..., description="% of orders with Google Click ID")


class ShopifyOAuthInitiate(BaseModel):
    """Initiate Shopify OAuth flow"""
    customer_id: int = Field(..., description="Customer ID")
    shop_domain: str = Field(..., description="Shopify domain (e.g., mystore.myshopify.com)")
    redirect_uri: str = Field(..., description="OAuth redirect URI")


class ShopifyOAuthCallback(BaseModel):
    """Shopify OAuth callback"""
    customer_id: int
    shop: str = Field(..., description="Shopify shop domain")
    code: str = Field(..., description="OAuth authorization code")
    state: Optional[str] = Field(None, description="OAuth state for security")


class ShopifyOAuthResponse(BaseModel):
    """Shopify OAuth response"""
    success: bool
    store_id: Optional[str] = None
    shop_domain: Optional[str] = None
    message: str
