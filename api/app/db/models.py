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