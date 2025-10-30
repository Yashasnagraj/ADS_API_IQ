"""
SQLAlchemy models for the Google Ads database
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    descriptive_name = Column(String)
    currency_code = Column(String, default='INR')
    time_zone = Column(String, default='Asia/Kolkata')
    status = Column(String, default='ENABLED')
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class Campaign(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, nullable=False)
    campaign_name = Column(String, nullable=False)
    status = Column(String)
    serving_status = Column(String)
    channel_type = Column(String)
    channel_subtype = Column(String)
    bidding_strategy_type = Column(String)
    budget_id = Column(String)
    budget_amount_micros = Column(Integer)
    start_date = Column(String)
    end_date = Column(String)
    optimization_score = Column(Float)
    target_cpa_micros = Column(Integer)
    target_roas = Column(Float)
    network_target_search = Column(Boolean)
    network_target_content = Column(Boolean)
    network_target_partner = Column(Boolean)
    geo_target_type_positive = Column(String)
    geo_target_type_negative = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    ad_groups = relationship("AdGroup", back_populates="campaign")
    keywords = relationship("Keyword", back_populates="campaign")
    search_terms = relationship("SearchTerm", back_populates="campaign")
    campaign_keywords = relationship("CampaignKeyword", back_populates="campaign")


class AdGroup(Base):
    __tablename__ = "ad_groups"

    ad_group_id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"))
    customer_id = Column(Integer, nullable=False)
    ad_group_name = Column(String, nullable=False)
    status = Column(String)
    type = Column(String)
    cpc_bid_micros = Column(Integer)
    cpm_bid_micros = Column(Integer)
    target_cpa_micros = Column(Integer)
    target_roas = Column(Float)
    ad_rotation_mode = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    campaign = relationship("Campaign", back_populates="ad_groups")
    keywords = relationship("Keyword", back_populates="ad_group")
    search_terms = relationship("SearchTerm", back_populates="ad_group")


class Keyword(Base):
    __tablename__ = "keywords"

    keyword_id = Column(String, primary_key=True, index=True)
    ad_group_id = Column(Integer, ForeignKey("ad_groups.ad_group_id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"))
    customer_id = Column(Integer, nullable=False)
    keyword_text = Column(String, nullable=False, index=True)
    match_type = Column(String)
    status = Column(String)
    quality_score = Column(Integer)
    creative_quality_score = Column(String)
    landing_page_quality_score = Column(String)
    search_predicted_ctr = Column(String)
    cpc_bid_micros = Column(Integer)
    first_page_cpc_micros = Column(Integer)
    first_position_cpc_micros = Column(Integer)
    top_of_page_cpc_micros = Column(Integer)
    approval_status = Column(String)
    system_serving_status = Column(String)
    is_negative = Column(Boolean)
    bid_modifier = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    ad_group = relationship("AdGroup", back_populates="keywords")
    campaign = relationship("Campaign", back_populates="keywords")
    search_terms = relationship("SearchTerm", back_populates="keyword")
    campaign_keywords = relationship("CampaignKeyword", back_populates="keyword")


class SearchTerm(Base):
    __tablename__ = "search_terms"

    search_term_id = Column(Integer, primary_key=True, autoincrement=True)
    keyword_id = Column(String, ForeignKey("keywords.keyword_id"))
    ad_group_id = Column(Integer, ForeignKey("ad_groups.ad_group_id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"))
    customer_id = Column(Integer, nullable=False)
    search_term = Column(String, nullable=False, index=True)
    keyword_text = Column(String)
    match_type = Column(String)
    search_term_match_type = Column(String)
    date = Column(String)
    clicks = Column(Integer)
    impressions = Column(Integer)
    cost_micros = Column(Integer)
    conversions = Column(Float)
    conversion_value = Column(Float)
    ctr = Column(Float)
    avg_cpc_micros = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    keyword = relationship("Keyword", back_populates="search_terms")
    ad_group = relationship("AdGroup", back_populates="search_terms")
    campaign = relationship("Campaign", back_populates="search_terms")


class CampaignKeyword(Base):
    __tablename__ = "campaign_keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"))
    keyword_id = Column(String, ForeignKey("keywords.keyword_id"))
    customer_id = Column(Integer, nullable=False)
    date = Column(String)
    clicks = Column(Integer)
    impressions = Column(Integer)
    cost_micros = Column(Integer)
    conversions = Column(Float)
    conversion_value = Column(Float)
    ctr = Column(Float)
    conversion_rate = Column(Float)
    avg_cpc_micros = Column(Integer)
    avg_position = Column(Float)
    absolute_top_impression_percentage = Column(Float)
    top_impression_percentage = Column(Float)
    search_impression_share = Column(Float)
    search_rank_lost_impression_share = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_keywords")
    keyword = relationship("Keyword", back_populates="campaign_keywords")


class MLFeature(Base):
    __tablename__ = "ml_features"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False)
    campaign_id = Column(Integer)
    campaign_name = Column(String)
    channel_type = Column(String)
    bidding_strategy = Column(String)
    budget_amount = Column(Float)
    keyword_id = Column(String)
    keyword_text = Column(String)
    match_type = Column(String)
    quality_score = Column(Integer)
    avg_cpc = Column(Float)
    ctr = Column(Float)
    conversion_rate = Column(Float)
    conversions = Column(Float)
    cost = Column(Float)
    impressions = Column(Integer)
    clicks = Column(Integer)
    competition_index = Column(Float)
    search_volume_trend = Column(Float)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


# ==============================================================================
# SHOPIFY E-COMMERCE MODELS
# ==============================================================================

class ShopifyStore(Base):
    """Shopify store connection and credentials"""
    __tablename__ = "shopify_stores"

    store_id = Column(String, primary_key=True, index=True)  # Shopify shop domain
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    shop_domain = Column(String, nullable=False, unique=True)  # mystore.myshopify.com
    shop_name = Column(String)
    access_token = Column(String, nullable=False)  # OAuth access token (encrypted)
    scope = Column(String)  # OAuth scopes granted
    email = Column(String)
    currency = Column(String, default='USD')
    timezone = Column(String)
    installed_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    last_sync_at = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    orders = relationship("ShopifyOrder", back_populates="store")
    products = relationship("ShopifyProduct", back_populates="store")
    customers = relationship("ShopifyCustomer", back_populates="store")
    cart_events = relationship("ShopifyCartEvent", back_populates="store")


class ShopifyOrder(Base):
    """Shopify order data with Google Ads attribution"""
    __tablename__ = "shopify_orders"

    order_id = Column(String, primary_key=True, index=True)  # Shopify order ID
    store_id = Column(String, ForeignKey("shopify_stores.store_id"), nullable=False)
    customer_id = Column(Integer, nullable=False)  # Our customer ID

    # Order details
    order_number = Column(String, index=True)  # Human-readable order number
    order_name = Column(String)  # e.g., "#1001"
    email = Column(String, index=True)

    # Financial
    total_price = Column(Float, nullable=False)
    subtotal_price = Column(Float)
    total_tax = Column(Float)
    total_discounts = Column(Float)
    total_shipping = Column(Float)
    currency = Column(String, default='USD')
    financial_status = Column(String)  # paid, pending, refunded, etc.
    fulfillment_status = Column(String)  # fulfilled, partial, unfulfilled

    # Attribution - CRITICAL for Google Ads ROAS
    gclid = Column(String, index=True)  # Google Click ID
    utm_source = Column(String, index=True)
    utm_medium = Column(String)
    utm_campaign = Column(String, index=True)
    utm_term = Column(String)
    utm_content = Column(String)
    landing_site = Column(String)
    referring_site = Column(String)

    # Customer info
    shopify_customer_id = Column(String, index=True)
    customer_first_name = Column(String)
    customer_last_name = Column(String)

    # Timestamps
    created_at_shopify = Column(TIMESTAMP)  # When order was created in Shopify
    updated_at_shopify = Column(TIMESTAMP)  # Last updated in Shopify
    processed_at = Column(TIMESTAMP)  # When order was processed
    cancelled_at = Column(TIMESTAMP)  # If cancelled
    closed_at = Column(TIMESTAMP)  # If closed

    # Metadata
    tags = Column(Text)  # Comma-separated tags
    note = Column(Text)
    line_items_count = Column(Integer)

    # System
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    store = relationship("ShopifyStore", back_populates="orders")


class ShopifyProduct(Base):
    """Shopify product catalog"""
    __tablename__ = "shopify_products"

    product_id = Column(String, primary_key=True, index=True)  # Shopify product ID
    store_id = Column(String, ForeignKey("shopify_stores.store_id"), nullable=False)
    customer_id = Column(Integer, nullable=False)

    # Product details
    title = Column(String, nullable=False)
    body_html = Column(Text)  # Product description
    vendor = Column(String)
    product_type = Column(String, index=True)
    handle = Column(String)  # URL handle

    # Inventory
    variants_count = Column(Integer)
    inventory_quantity = Column(Integer)
    inventory_policy = Column(String)  # deny or continue

    # Pricing
    price = Column(Float)
    compare_at_price = Column(Float)

    # Status
    status = Column(String, index=True)  # active, archived, draft
    published_at = Column(TIMESTAMP)

    # SEO
    tags = Column(Text)
    meta_description = Column(Text)

    # Images
    image_url = Column(String)
    images_count = Column(Integer)

    # Timestamps
    created_at_shopify = Column(TIMESTAMP)
    updated_at_shopify = Column(TIMESTAMP)

    # System
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    store = relationship("ShopifyStore", back_populates="products")


class ShopifyCustomer(Base):
    """Shopify customer data for LTV analysis"""
    __tablename__ = "shopify_customers"

    shopify_customer_id = Column(String, primary_key=True, index=True)  # Shopify customer ID
    store_id = Column(String, ForeignKey("shopify_stores.store_id"), nullable=False)
    customer_id = Column(Integer, nullable=False)

    # Customer details
    email = Column(String, index=True)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)

    # Marketing
    accepts_marketing = Column(Boolean)
    marketing_opt_in_level = Column(String)

    # Financial - LTV metrics
    total_spent = Column(Float, default=0.0)
    orders_count = Column(Integer, default=0)
    average_order_value = Column(Float)

    # Attribution - First touch
    first_order_gclid = Column(String, index=True)  # Google Click ID from first order
    first_order_utm_source = Column(String, index=True)
    first_order_utm_campaign = Column(String)

    # Status
    state = Column(String)  # enabled, disabled, invited, declined
    verified_email = Column(Boolean)

    # Location
    city = Column(String)
    province = Column(String)
    country = Column(String)

    # Timestamps
    created_at_shopify = Column(TIMESTAMP)
    updated_at_shopify = Column(TIMESTAMP)
    last_order_at = Column(TIMESTAMP)

    # System
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    store = relationship("ShopifyStore", back_populates="customers")


class ShopifyCartEvent(Base):
    """Shopify cart abandonment events"""
    __tablename__ = "shopify_cart_events"

    event_id = Column(String, primary_key=True, index=True)  # Generated UUID
    store_id = Column(String, ForeignKey("shopify_stores.store_id"), nullable=False)
    customer_id = Column(Integer, nullable=False)

    # Cart details
    cart_token = Column(String, index=True)
    checkout_token = Column(String, index=True)
    customer_email = Column(String, index=True)

    # Event type
    event_type = Column(String, index=True)  # cart_created, cart_updated, checkout_started, checkout_abandoned

    # Financial
    total_price = Column(Float)
    currency = Column(String, default='USD')
    line_items_count = Column(Integer)

    # Attribution
    gclid = Column(String, index=True)
    utm_source = Column(String)
    utm_campaign = Column(String)
    landing_site = Column(String)

    # Products JSON
    products_json = Column(Text)  # JSON array of products in cart

    # Recovery
    abandoned_checkout_url = Column(String)
    completed_order_id = Column(String)  # If cart was converted to order

    # Timestamps
    event_at = Column(TIMESTAMP, index=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    store = relationship("ShopifyStore", back_populates="cart_events")


# ==============================================================================
# META (FACEBOOK) ADS MODELS
# ==============================================================================

class MetaAdAccount(Base):
    """Meta (Facebook) Ad Account connection"""
    __tablename__ = "meta_ad_accounts"

    account_id = Column(String, primary_key=True, index=True)  # act_123456789
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)

    # Account details
    account_name = Column(String)
    business_id = Column(String)
    currency = Column(String, default='USD')
    timezone_name = Column(String)

    # Access
    access_token = Column(String, nullable=False)  # Long-lived access token
    token_expires_at = Column(TIMESTAMP)

    # Status
    account_status = Column(String)  # ACTIVE, DISABLED, UNSETTLED, etc.
    is_active = Column(Boolean, default=True)

    # Timestamps
    installed_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    last_sync_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    campaigns = relationship("MetaCampaign", back_populates="account")


class MetaCampaign(Base):
    """Meta Ads Campaign"""
    __tablename__ = "meta_campaigns"

    campaign_id = Column(String, primary_key=True, index=True)  # Meta campaign ID
    account_id = Column(String, ForeignKey("meta_ad_accounts.account_id"), nullable=False)
    customer_id = Column(Integer, nullable=False)

    # Campaign details
    name = Column(String, nullable=False, index=True)
    status = Column(String, index=True)  # ACTIVE, PAUSED, DELETED, ARCHIVED
    effective_status = Column(String)  # ACTIVE, PAUSED, CAMPAIGN_PAUSED, etc.
    objective = Column(String, index=True)  # OUTCOME_TRAFFIC, OUTCOME_SALES, OUTCOME_LEADS, etc.

    # Budget
    daily_budget = Column(Float)  # Daily budget in account currency
    lifetime_budget = Column(Float)  # Lifetime budget
    budget_remaining = Column(Float)

    # Settings
    bid_strategy = Column(String)  # LOWEST_COST_WITHOUT_CAP, COST_CAP, etc.
    buying_type = Column(String)  # AUCTION, RESERVED
    special_ad_categories = Column(String)  # JSON array

    # Timestamps
    created_time = Column(TIMESTAMP)
    updated_time = Column(TIMESTAMP)
    start_time = Column(TIMESTAMP)
    stop_time = Column(TIMESTAMP)

    # System
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    account = relationship("MetaAdAccount", back_populates="campaigns")
    adsets = relationship("MetaAdSet", back_populates="campaign")
    ads = relationship("MetaAd", back_populates="campaign")


class MetaAdSet(Base):
    """Meta Ads Ad Set"""
    __tablename__ = "meta_adsets"

    adset_id = Column(String, primary_key=True, index=True)  # Meta ad set ID
    campaign_id = Column(String, ForeignKey("meta_campaigns.campaign_id"), nullable=False)
    account_id = Column(String, nullable=False)
    customer_id = Column(Integer, nullable=False)

    # Ad Set details
    name = Column(String, nullable=False, index=True)
    status = Column(String, index=True)  # ACTIVE, PAUSED, DELETED, ARCHIVED
    effective_status = Column(String)

    # Budget & Bidding
    daily_budget = Column(Float)
    lifetime_budget = Column(Float)
    bid_amount = Column(Float)
    bid_strategy = Column(String)

    # Targeting (stored as JSON for flexibility)
    targeting = Column(Text)  # JSON: age, gender, locations, interests, behaviors
    optimization_goal = Column(String)  # REACH, LINK_CLICKS, IMPRESSIONS, etc.
    billing_event = Column(String)  # IMPRESSIONS, LINK_CLICKS, etc.

    # Timestamps
    created_time = Column(TIMESTAMP)
    updated_time = Column(TIMESTAMP)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)

    # System
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    campaign = relationship("MetaCampaign", back_populates="adsets")
    ads = relationship("MetaAd", back_populates="adset")


class MetaAd(Base):
    """Meta Ads Creative/Ad"""
    __tablename__ = "meta_ads"

    ad_id = Column(String, primary_key=True, index=True)  # Meta ad ID
    adset_id = Column(String, ForeignKey("meta_adsets.adset_id"), nullable=False)
    campaign_id = Column(String, ForeignKey("meta_campaigns.campaign_id"), nullable=False)
    account_id = Column(String, nullable=False)
    customer_id = Column(Integer, nullable=False)

    # Ad details
    name = Column(String, nullable=False, index=True)
    status = Column(String, index=True)  # ACTIVE, PAUSED, DELETED, ARCHIVED
    effective_status = Column(String)

    # Creative
    creative_id = Column(String, index=True)
    creative_name = Column(String)
    creative_title = Column(String)
    creative_body = Column(Text)
    creative_image_url = Column(String)
    creative_video_url = Column(String)
    call_to_action_type = Column(String)  # LEARN_MORE, SHOP_NOW, SIGN_UP, etc.

    # Tracking
    tracking_specs = Column(Text)  # JSON array

    # Timestamps
    created_time = Column(TIMESTAMP)
    updated_time = Column(TIMESTAMP)

    # System
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    campaign = relationship("MetaCampaign", back_populates="ads")
    adset = relationship("MetaAdSet", back_populates="ads")


class MetaInsights(Base):
    """Meta Ads Performance Insights (time-series metrics)"""
    __tablename__ = "meta_insights"

    insight_id = Column(String, primary_key=True, index=True)  # Generated: {entity_type}_{entity_id}_{date}

    # Entity reference (campaign, adset, or ad level)
    entity_type = Column(String, index=True)  # campaign, adset, ad
    entity_id = Column(String, index=True)  # The campaign_id, adset_id, or ad_id
    campaign_id = Column(String, index=True)
    account_id = Column(String, index=True)
    customer_id = Column(Integer, nullable=False, index=True)

    # Date
    date_start = Column(String, index=True)  # YYYY-MM-DD
    date_stop = Column(String, index=True)  # YYYY-MM-DD

    # Core Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)  # In account currency
    reach = Column(Integer, default=0)
    frequency = Column(Float, default=0.0)

    # Engagement Metrics
    inline_link_clicks = Column(Integer, default=0)
    inline_post_engagement = Column(Integer, default=0)
    post_reactions = Column(Integer, default=0)
    post_comments = Column(Integer, default=0)
    post_shares = Column(Integer, default=0)
    video_views = Column(Integer, default=0)
    video_avg_time_watched = Column(Float, default=0.0)

    # Conversion Metrics
    conversions = Column(Float, default=0.0)
    conversion_values = Column(Float, default=0.0)  # Total conversion value
    purchases = Column(Integer, default=0)
    purchase_value = Column(Float, default=0.0)
    adds_to_cart = Column(Integer, default=0)
    checkouts_initiated = Column(Integer, default=0)
    leads = Column(Integer, default=0)

    # Calculated Metrics
    ctr = Column(Float, default=0.0)  # Click-through rate %
    cpc = Column(Float, default=0.0)  # Cost per click
    cpm = Column(Float, default=0.0)  # Cost per 1000 impressions
    cpp = Column(Float, default=0.0)  # Cost per purchase
    roas = Column(Float, default=0.0)  # Return on ad spend

    # System
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


# ==============================================================================
# GOOGLE ANALYTICS 4 (GA4) MODELS
# ==============================================================================

class GA4Property(Base):
    """Google Analytics 4 Property connection"""
    __tablename__ = "ga4_properties"

    property_id = Column(String, primary_key=True, index=True)  # GA4 Property ID (e.g., "123456789")
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)

    # Property details
    property_name = Column(String, nullable=False)
    display_name = Column(String)
    website_url = Column(String)
    industry_category = Column(String)
    time_zone = Column(String)
    currency_code = Column(String, default='USD')

    # Authentication
    service_account_email = Column(String)  # Service account used for API access
    credentials_path = Column(String)  # Path to service account JSON key

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    connected_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    last_sync_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    sessions = relationship("GA4Session", back_populates="property")
    events = relationship("GA4Event", back_populates="property")
    conversion_paths = relationship("GA4ConversionPath", back_populates="property")


class GA4Session(Base):
    """GA4 Session aggregated data"""
    __tablename__ = "ga4_sessions"

    session_id = Column(String, primary_key=True, index=True)  # Generated: property_id_date_source_campaign
    property_id = Column(String, ForeignKey("ga4_properties.property_id"), nullable=False)
    customer_id = Column(Integer, nullable=False, index=True)

    # Date
    date = Column(String, index=True)  # YYYY-MM-DD

    # Attribution (campaign tracking)
    utm_source = Column(String, index=True)
    utm_medium = Column(String, index=True)
    utm_campaign = Column(String, index=True)
    utm_term = Column(String)
    utm_content = Column(String)
    source = Column(String, index=True)  # Fallback if UTM not available
    medium = Column(String, index=True)

    # Session Metrics
    sessions = Column(Integer, default=0)
    engaged_sessions = Column(Integer, default=0)
    bounced_sessions = Column(Integer, default=0)
    session_duration = Column(Float, default=0.0)  # Total seconds
    avg_session_duration = Column(Float, default=0.0)  # Seconds per session

    # User Metrics
    users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)

    # Engagement Metrics
    page_views = Column(Integer, default=0)
    screen_views = Column(Integer, default=0)
    events_count = Column(Integer, default=0)
    pages_per_session = Column(Float, default=0.0)

    # Rates
    bounce_rate = Column(Float, default=0.0)  # %
    engagement_rate = Column(Float, default=0.0)  # %

    # Conversion Metrics
    conversions = Column(Integer, default=0)
    conversion_value = Column(Float, default=0.0)

    # Device Category
    device_category = Column(String, index=True)  # desktop, mobile, tablet

    # System
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    property = relationship("GA4Property", back_populates="sessions")


class GA4Event(Base):
    """GA4 Event tracking"""
    __tablename__ = "ga4_events"

    event_id = Column(String, primary_key=True, index=True)  # Generated: property_id_event_name_date
    property_id = Column(String, ForeignKey("ga4_properties.property_id"), nullable=False)
    customer_id = Column(Integer, nullable=False, index=True)

    # Event details
    event_name = Column(String, nullable=False, index=True)  # e.g., page_view, purchase, add_to_cart
    event_category = Column(String, index=True)  # Custom grouping
    date = Column(String, index=True)  # YYYY-MM-DD

    # Attribution
    utm_source = Column(String, index=True)
    utm_campaign = Column(String, index=True)

    # Event metrics
    event_count = Column(Integer, default=0)
    event_value = Column(Float, default=0.0)

    # E-commerce specific (for purchase, add_to_cart, etc.)
    ecommerce_revenue = Column(Float, default=0.0)
    ecommerce_quantity = Column(Integer, default=0)
    ecommerce_items = Column(Integer, default=0)

    # User context
    users = Column(Integer, default=0)

    # System
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    property = relationship("GA4Property", back_populates="events")


class GA4ConversionPath(Base):
    """GA4 Multi-touch attribution - conversion paths"""
    __tablename__ = "ga4_conversion_paths"

    path_id = Column(String, primary_key=True, index=True)  # Generated UUID
    property_id = Column(String, ForeignKey("ga4_properties.property_id"), nullable=False)
    customer_id = Column(Integer, nullable=False, index=True)

    # User identifier
    user_pseudo_id = Column(String, index=True)  # GA4 anonymous user ID

    # Conversion details
    conversion_event = Column(String, index=True)  # e.g., purchase, sign_up
    conversion_date = Column(String, index=True)  # YYYY-MM-DD
    conversion_timestamp = Column(TIMESTAMP)
    conversion_value = Column(Float, default=0.0)

    # Path details (stored as JSON for flexibility)
    touchpoints_json = Column(Text)  # JSON array of touchpoints
    # Example: [
    #   {"source": "google", "medium": "cpc", "campaign": "summer_sale", "timestamp": "2024-01-01", "order": 1},
    #   {"source": "facebook", "medium": "social", "campaign": "retargeting", "timestamp": "2024-01-03", "order": 2},
    #   {"source": "direct", "medium": "none", "timestamp": "2024-01-05", "order": 3}
    # ]

    # Path metrics
    touchpoints_count = Column(Integer, default=0)  # Number of touchpoints
    days_to_conversion = Column(Integer, default=0)  # Days from first touch to conversion

    # Attribution
    first_touch_source = Column(String, index=True)
    first_touch_campaign = Column(String, index=True)
    last_touch_source = Column(String, index=True)
    last_touch_campaign = Column(String, index=True)

    # System
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Relationships
    property = relationship("GA4Property", back_populates="conversion_paths")


class GA4Audience(Base):
    """GA4 Audience insights"""
    __tablename__ = "ga4_audiences"

    audience_id = Column(String, primary_key=True, index=True)  # Generated: property_id_segment_date
    property_id = Column(String, ForeignKey("ga4_properties.property_id"), nullable=False)
    customer_id = Column(Integer, nullable=False, index=True)

    # Audience segment
    segment_name = Column(String, nullable=False, index=True)  # e.g., "All Users", "Purchasers", "High Value"
    segment_type = Column(String, index=True)  # demographic, behavior, technology
    date = Column(String, index=True)  # YYYY-MM-DD

    # Demographics
    age_range = Column(String)  # 18-24, 25-34, etc.
    gender = Column(String)  # male, female, unknown
    country = Column(String, index=True)
    city = Column(String)
    language = Column(String)

    # Technology
    device_category = Column(String, index=True)  # desktop, mobile, tablet
    operating_system = Column(String)
    browser = Column(String)

    # Interests (stored as JSON)
    interests_json = Column(Text)  # JSON array of interest categories

    # Metrics
    users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    sessions = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    avg_session_duration = Column(Float, default=0.0)
    pages_per_session = Column(Float, default=0.0)

    # Conversion
    conversions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    avg_revenue_per_user = Column(Float, default=0.0)

    # System
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())