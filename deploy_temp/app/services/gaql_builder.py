"""
GAQL (Google Ads Query Language) Query Builder Utilities
Helps construct type-safe GAQL queries with proper formatting
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class DateRange(str, Enum):
    """Common date range presets"""
    TODAY = "TODAY"
    YESTERDAY = "YESTERDAY"
    LAST_7_DAYS = "LAST_7_DAYS"
    LAST_14_DAYS = "LAST_14_DAYS"
    LAST_30_DAYS = "LAST_30_DAYS"
    LAST_90_DAYS = "LAST_90_DAYS"
    THIS_MONTH = "THIS_MONTH"
    LAST_MONTH = "LAST_MONTH"
    THIS_YEAR = "THIS_YEAR"
    LAST_YEAR = "LAST_YEAR"


class CampaignStatus(str, Enum):
    """Campaign status values"""
    ENABLED = "ENABLED"
    PAUSED = "PAUSED"
    REMOVED = "REMOVED"


class MatchType(str, Enum):
    """Keyword match types"""
    EXACT = "EXACT"
    PHRASE = "PHRASE"
    BROAD = "BROAD"


class GAQLBuilder:
    """Builder class for constructing GAQL queries"""

    def __init__(self):
        self.select_fields: List[str] = []
        self.from_table: str = ""
        self.where_conditions: List[str] = []
        self.order_by_fields: List[str] = []
        self.limit_value: Optional[int] = None
        self.parameters: Dict[str, Any] = {}

    def select(self, *fields: str) -> 'GAQLBuilder':
        """Add fields to SELECT clause"""
        self.select_fields.extend(fields)
        return self

    def from_(self, table: str) -> 'GAQLBuilder':
        """Set FROM clause"""
        self.from_table = table
        return self

    def where(self, condition: str) -> 'GAQLBuilder':
        """Add WHERE condition"""
        self.where_conditions.append(condition)
        return self

    def order_by(self, *fields: str) -> 'GAQLBuilder':
        """Add ORDER BY fields"""
        self.order_by_fields.extend(fields)
        return self

    def limit(self, value: int) -> 'GAQLBuilder':
        """Set LIMIT"""
        self.limit_value = value
        return self

    def date_range(self, range_type: DateRange) -> 'GAQLBuilder':
        """Add date range filter"""
        self.where(f"segments.date DURING {range_type.value}")
        return self

    def campaign_status(self, status: CampaignStatus) -> 'GAQLBuilder':
        """Filter by campaign status"""
        self.where(f"campaign.status = '{status.value}'")
        return self

    def exclude_removed(self, entity: str = "campaign") -> 'GAQLBuilder':
        """Exclude REMOVED entities"""
        self.where(f"{entity}.status != 'REMOVED'")
        return self

    def build(self) -> str:
        """Build the final GAQL query string"""
        if not self.select_fields:
            raise ValueError("SELECT fields are required")
        if not self.from_table:
            raise ValueError("FROM table is required")

        query_parts = []

        # SELECT
        select_clause = "SELECT " + ", ".join(self.select_fields)
        query_parts.append(select_clause)

        # FROM
        from_clause = f"FROM {self.from_table}"
        query_parts.append(from_clause)

        # WHERE
        if self.where_conditions:
            where_clause = "WHERE " + " AND ".join(self.where_conditions)
            query_parts.append(where_clause)

        # ORDER BY
        if self.order_by_fields:
            order_clause = "ORDER BY " + ", ".join(self.order_by_fields)
            query_parts.append(order_clause)

        # LIMIT
        if self.limit_value:
            limit_clause = f"LIMIT {self.limit_value}"
            query_parts.append(limit_clause)

        return " ".join(query_parts)


# Pre-built query templates
class QueryTemplates:
    """Common GAQL query templates"""

    @staticmethod
    def campaigns_overview(
        date_range: DateRange = DateRange.LAST_30_DAYS,
        status: Optional[CampaignStatus] = None
    ) -> str:
        """Campaign overview with key metrics"""
        builder = (
            GAQLBuilder()
            .select(
                "campaign.id",
                "campaign.name",
                "campaign.status",
                "campaign.advertising_channel_type",
                "campaign.bidding_strategy_type",
                "campaign_budget.amount_micros",
                "campaign.optimization_score",
                "metrics.clicks",
                "metrics.impressions",
                "metrics.cost_micros",
                "metrics.conversions",
                "metrics.conversions_value",
                "metrics.ctr",
                "metrics.average_cpc"
            )
            .from_("campaign")
            .date_range(date_range)
        )

        if status:
            builder.campaign_status(status)
        else:
            builder.exclude_removed()

        return builder.build()

    @staticmethod
    def keywords_performance(
        date_range: DateRange = DateRange.LAST_30_DAYS,
        campaign_id: Optional[int] = None,
        min_quality_score: Optional[int] = None
    ) -> str:
        """Keywords with quality scores and performance"""
        builder = (
            GAQLBuilder()
            .select(
                "ad_group_criterion.criterion_id",
                "ad_group_criterion.keyword.text",
                "ad_group_criterion.keyword.match_type",
                "ad_group_criterion.status",
                "ad_group_criterion.quality_info.quality_score",
                "ad_group_criterion.quality_info.creative_quality_score",
                "ad_group_criterion.quality_info.post_click_quality_score",
                "ad_group_criterion.quality_info.search_predicted_ctr",
                "ad_group_criterion.cpc_bid_micros",
                "ad_group.id",
                "ad_group.name",
                "campaign.id",
                "campaign.name",
                "metrics.clicks",
                "metrics.impressions",
                "metrics.cost_micros",
                "metrics.conversions",
                "metrics.ctr",
                "metrics.average_cpc"
            )
            .from_("keyword_view")
            .date_range(date_range)
            .exclude_removed("ad_group_criterion")
        )

        if campaign_id:
            builder.where(f"campaign.id = {campaign_id}")

        if min_quality_score:
            builder.where(
                f"ad_group_criterion.quality_info.quality_score >= {min_quality_score}"
            )

        return builder.build()

    @staticmethod
    def search_terms(
        date_range: DateRange = DateRange.LAST_30_DAYS,
        campaign_id: Optional[int] = None,
        min_clicks: Optional[int] = None
    ) -> str:
        """Search terms (actual user queries)"""
        builder = (
            GAQLBuilder()
            .select(
                "search_term_view.search_term",
                "search_term_view.status",
                "segments.keyword.info.text",
                "segments.keyword.info.match_type",
                "search_term_view.search_term_match_type",
                "ad_group.id",
                "ad_group.name",
                "campaign.id",
                "campaign.name",
                "segments.date",
                "metrics.clicks",
                "metrics.impressions",
                "metrics.cost_micros",
                "metrics.conversions",
                "metrics.ctr",
                "metrics.average_cpc"
            )
            .from_("search_term_view")
            .date_range(date_range)
        )

        if campaign_id:
            builder.where(f"campaign.id = {campaign_id}")

        if min_clicks:
            builder.where(f"metrics.clicks >= {min_clicks}")

        return builder.build()

    @staticmethod
    def ad_groups_performance(
        date_range: DateRange = DateRange.LAST_30_DAYS,
        campaign_id: Optional[int] = None
    ) -> str:
        """Ad groups with performance metrics"""
        builder = (
            GAQLBuilder()
            .select(
                "ad_group.id",
                "ad_group.name",
                "ad_group.status",
                "ad_group.type",
                "ad_group.cpc_bid_micros",
                "campaign.id",
                "campaign.name",
                "metrics.clicks",
                "metrics.impressions",
                "metrics.cost_micros",
                "metrics.conversions",
                "metrics.ctr",
                "metrics.average_cpc"
            )
            .from_("ad_group")
            .date_range(date_range)
            .exclude_removed("ad_group")
        )

        if campaign_id:
            builder.where(f"campaign.id = {campaign_id}")

        return builder.build()

    @staticmethod
    def customer_summary() -> str:
        """Customer account information"""
        return (
            GAQLBuilder()
            .select(
                "customer.id",
                "customer.descriptive_name",
                "customer.currency_code",
                "customer.time_zone",
                "customer.status",
                "customer.manager"
            )
            .from_("customer")
            .build()
        )

    @staticmethod
    def campaign_metrics_timeseries(
        campaign_id: int,
        date_range: DateRange = DateRange.LAST_30_DAYS
    ) -> str:
        """Daily metrics for a campaign"""
        return (
            GAQLBuilder()
            .select(
                "segments.date",
                "campaign.id",
                "campaign.name",
                "metrics.clicks",
                "metrics.impressions",
                "metrics.cost_micros",
                "metrics.conversions",
                "metrics.conversions_value",
                "metrics.ctr",
                "metrics.average_cpc"
            )
            .from_("campaign")
            .date_range(date_range)
            .where(f"campaign.id = {campaign_id}")
            .order_by("segments.date")
            .build()
        )

    @staticmethod
    def top_keywords_by_conversions(
        date_range: DateRange = DateRange.LAST_30_DAYS,
        limit: int = 50
    ) -> str:
        """Top converting keywords"""
        return (
            GAQLBuilder()
            .select(
                "ad_group_criterion.keyword.text",
                "ad_group_criterion.keyword.match_type",
                "ad_group_criterion.quality_info.quality_score",
                "campaign.name",
                "ad_group.name",
                "metrics.conversions",
                "metrics.cost_micros",
                "metrics.clicks",
                "metrics.ctr"
            )
            .from_("keyword_view")
            .date_range(date_range)
            .where("metrics.conversions > 0")
            .exclude_removed("ad_group_criterion")
            .order_by("metrics.conversions DESC")
            .limit(limit)
            .build()
        )

    @staticmethod
    def low_quality_keywords(
        max_quality_score: int = 5,
        date_range: DateRange = DateRange.LAST_30_DAYS
    ) -> str:
        """Keywords with low quality scores"""
        return (
            GAQLBuilder()
            .select(
                "ad_group_criterion.keyword.text",
                "ad_group_criterion.quality_info.quality_score",
                "ad_group_criterion.quality_info.creative_quality_score",
                "ad_group_criterion.quality_info.post_click_quality_score",
                "ad_group_criterion.quality_info.search_predicted_ctr",
                "campaign.name",
                "metrics.clicks",
                "metrics.cost_micros",
                "metrics.ctr"
            )
            .from_("keyword_view")
            .date_range(date_range)
            .where(
                f"ad_group_criterion.quality_info.quality_score <= {max_quality_score}"
            )
            .exclude_removed("ad_group_criterion")
            .order_by("ad_group_criterion.quality_info.quality_score ASC")
            .build()
        )


# Utility functions
def format_date_range(start_date: str, end_date: str) -> str:
    """Format custom date range for GAQL"""
    return f"BETWEEN '{start_date}' AND '{end_date}'"


def micros_to_currency(micros: int) -> float:
    """Convert micros to standard currency (e.g., 77,000,000 → 77.00)"""
    return micros / 1_000_000 if micros else 0.0


def currency_to_micros(amount: float) -> int:
    """Convert currency to micros (e.g., 77.00 → 77,000,000)"""
    return int(amount * 1_000_000)
