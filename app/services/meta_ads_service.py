"""
Meta (Facebook) Ads Real-time Service
Uses Facebook Marketing API for live data querying
"""
from typing import List, Dict, Any, Optional
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.customconversion import CustomConversion
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.advideo import AdVideo
from facebook_business.exceptions import FacebookRequestError
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta
from loguru import logger


# Load .env.meta file explicitly
env_path = Path(__file__).parent.parent.parent.parent / '.env.meta'
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"✅ Loaded .env.meta from: {env_path}")
else:
    # Fallback to main .env file
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"✅ Loaded .env from: {env_path} (fallback)")
    else:
        logger.warning(f"⚠️  No .env.meta or .env file found")


class MetaAdsService:
    """Service for real-time Meta (Facebook) Ads API queries"""

    def __init__(self, account_id: Optional[str] = None):
        """
        Initialize Meta Ads API client from environment credentials

        Args:
            account_id: Optional Meta ad account ID (format: act_123456789)
                       If not provided, uses META_AD_ACCOUNT_ID from env
        """
        # Load credentials from environment
        app_id = os.getenv("META_APP_ID")
        app_secret = os.getenv("META_APP_SECRET")
        access_token = os.getenv("META_ACCESS_TOKEN")
        self.default_account_id = account_id or os.getenv("META_AD_ACCOUNT_ID")
        api_version = os.getenv("META_API_VERSION", "v19.0")

        # Validate required credentials
        missing_creds = []
        if not app_id:
            missing_creds.append("META_APP_ID")
        if not app_secret:
            missing_creds.append("META_APP_SECRET")
        if not access_token:
            missing_creds.append("META_ACCESS_TOKEN")

        if missing_creds:
            error_msg = f"Missing required environment variables: {', '.join(missing_creds)}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)

        # Initialize Facebook Ads API
        try:
            logger.info("🔧 Initializing Meta (Facebook) Ads API client...")
            logger.debug(f"Using app_id: {app_id}")
            logger.debug(f"Using API version: {api_version}")
            logger.debug(f"Default account: {self.default_account_id}")

            FacebookAdsApi.init(
                app_id=app_id,
                app_secret=app_secret,
                access_token=access_token,
                api_version=api_version
            )

            self.api = FacebookAdsApi.get_default_api()
            logger.info("✅ Meta Ads API client initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Meta Ads API: {e}")
            raise

    def _convert_budget(self, budget_cents: Optional[int]) -> float:
        """Convert budget from cents to currency units"""
        if budget_cents is None:
            return 0.0
        return float(budget_cents) / 100

    def _parse_actions(self, actions: Optional[List[Dict]], action_type: str) -> float:
        """
        Parse Facebook's actions array to extract specific metrics

        Args:
            actions: List of action dictionaries from Facebook API
            action_type: Type of action (e.g., 'purchase', 'lead', 'add_to_cart')

        Returns:
            Sum of values for the specified action type
        """
        if not actions:
            return 0.0

        total = 0.0
        for action in actions:
            if action.get('action_type') == action_type:
                total += float(action.get('value', 0))

        return total

    def _get_date_range(self, range_str: str) -> Dict[str, str]:
        """
        Convert date range string to Facebook API format

        Args:
            range_str: Date range (e.g., 'last_7d', 'last_30d', 'last_90d')

        Returns:
            Dict with 'since' and 'until' dates
        """
        days_map = {
            'last_7d': 7,
            'last_14d': 14,
            'last_30d': 30,
            'last_60d': 60,
            'last_90d': 90,
            'today': 1,
            'yesterday': 1
        }

        days = days_map.get(range_str, 30)

        if range_str == 'yesterday':
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date
        elif range_str == 'today':
            end_date = datetime.now()
            start_date = end_date
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

        return {
            'since': start_date.strftime('%Y-%m-%d'),
            'until': end_date.strftime('%Y-%m-%d')
        }

    def get_account_info(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Meta ad account information

        Args:
            account_id: Meta ad account ID (format: act_123456789)

        Returns:
            Dictionary with account details
        """
        account_id = account_id or self.default_account_id

        try:
            logger.info(f"🔍 Fetching account info for {account_id}")

            ad_account = AdAccount(account_id)
            account_data = ad_account.api_get(fields=[
                'id',
                'account_id',
                'name',
                'account_status',
                'currency',
                'timezone_name',
                'business',
                'business_name',
                'spend_cap',
                'amount_spent',
                'balance',
            ])

            logger.info(f"✅ Retrieved account info for {account_data.get('name', account_id)}")
            return dict(account_data)

        except FacebookRequestError as e:
            logger.error(f"❌ Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching account info: {e}")
            raise

    def get_campaigns(
        self,
        account_id: Optional[str] = None,
        status: Optional[str] = None,
        date_range: str = 'last_30d',
        include_insights: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get campaigns with optional performance metrics

        Args:
            account_id: Meta ad account ID
            status: Filter by status (ACTIVE, PAUSED, ARCHIVED, DELETED)
            date_range: Date range for insights (last_7d, last_30d, etc.)
            include_insights: Whether to include performance insights

        Returns:
            List of campaign dictionaries
        """
        account_id = account_id or self.default_account_id

        try:
            logger.info(f"🔍 Fetching campaigns for account {account_id}")

            ad_account = AdAccount(account_id)

            # Build fields list
            fields = [
                Campaign.Field.id,
                Campaign.Field.name,
                Campaign.Field.status,
                Campaign.Field.effective_status,
                Campaign.Field.objective,
                Campaign.Field.daily_budget,
                Campaign.Field.lifetime_budget,
                Campaign.Field.budget_remaining,
                Campaign.Field.bid_strategy,
                Campaign.Field.buying_type,
                Campaign.Field.created_time,
                Campaign.Field.updated_time,
                Campaign.Field.start_time,
                Campaign.Field.stop_time,
                Campaign.Field.special_ad_categories,
            ]

            # Build params
            params = {}
            if status:
                params['effective_status'] = [status]

            # Get campaigns
            campaigns = ad_account.get_campaigns(fields=fields, params=params)

            results = []
            for campaign in campaigns:
                campaign_dict = dict(campaign)

                # Convert budgets from cents to currency
                if 'daily_budget' in campaign_dict:
                    campaign_dict['daily_budget_converted'] = self._convert_budget(
                        campaign_dict.get('daily_budget')
                    )
                if 'lifetime_budget' in campaign_dict:
                    campaign_dict['lifetime_budget_converted'] = self._convert_budget(
                        campaign_dict.get('lifetime_budget')
                    )
                if 'budget_remaining' in campaign_dict:
                    campaign_dict['budget_remaining_converted'] = self._convert_budget(
                        campaign_dict.get('budget_remaining')
                    )

                # Get insights if requested
                if include_insights:
                    insights = self._get_entity_insights(
                        campaign['id'],
                        'campaign',
                        date_range
                    )
                    campaign_dict['insights'] = insights

                results.append(campaign_dict)

            logger.info(f"✅ Retrieved {len(results)} campaigns")
            return results

        except FacebookRequestError as e:
            logger.error(f"❌ Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching campaigns: {e}")
            raise

    def get_ad_sets(
        self,
        account_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        status: Optional[str] = None,
        date_range: str = 'last_30d',
        include_insights: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get ad sets with optional performance metrics

        Args:
            account_id: Meta ad account ID
            campaign_id: Filter by campaign ID
            status: Filter by status
            date_range: Date range for insights
            include_insights: Whether to include performance insights

        Returns:
            List of ad set dictionaries
        """
        account_id = account_id or self.default_account_id

        try:
            logger.info(f"🔍 Fetching ad sets for account {account_id}")

            # Build fields list
            fields = [
                AdSet.Field.id,
                AdSet.Field.name,
                AdSet.Field.campaign_id,
                AdSet.Field.status,
                AdSet.Field.effective_status,
                AdSet.Field.daily_budget,
                AdSet.Field.lifetime_budget,
                AdSet.Field.bid_amount,
                AdSet.Field.bid_strategy,
                AdSet.Field.billing_event,
                AdSet.Field.optimization_goal,
                AdSet.Field.targeting,
                AdSet.Field.created_time,
                AdSet.Field.updated_time,
                AdSet.Field.start_time,
                AdSet.Field.end_time,
            ]

            # Build params
            params = {}
            if status:
                params['effective_status'] = [status]
            if campaign_id:
                params['campaign_id'] = campaign_id

            # Get ad sets
            if campaign_id:
                # Get from specific campaign
                campaign = Campaign(campaign_id)
                adsets = campaign.get_ad_sets(fields=fields, params=params)
            else:
                # Get from account
                ad_account = AdAccount(account_id)
                adsets = ad_account.get_ad_sets(fields=fields, params=params)

            results = []
            for adset in adsets:
                adset_dict = dict(adset)

                # Convert budgets
                if 'daily_budget' in adset_dict:
                    adset_dict['daily_budget_converted'] = self._convert_budget(
                        adset_dict.get('daily_budget')
                    )
                if 'lifetime_budget' in adset_dict:
                    adset_dict['lifetime_budget_converted'] = self._convert_budget(
                        adset_dict.get('lifetime_budget')
                    )
                if 'bid_amount' in adset_dict:
                    adset_dict['bid_amount_converted'] = self._convert_budget(
                        adset_dict.get('bid_amount')
                    )

                # Get insights if requested
                if include_insights:
                    insights = self._get_entity_insights(
                        adset['id'],
                        'adset',
                        date_range
                    )
                    adset_dict['insights'] = insights

                results.append(adset_dict)

            logger.info(f"✅ Retrieved {len(results)} ad sets")
            return results

        except FacebookRequestError as e:
            logger.error(f"❌ Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching ad sets: {e}")
            raise

    def get_ads(
        self,
        account_id: Optional[str] = None,
        adset_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        status: Optional[str] = None,
        date_range: str = 'last_30d',
        include_insights: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get ads with optional performance metrics

        Args:
            account_id: Meta ad account ID
            adset_id: Filter by ad set ID
            campaign_id: Filter by campaign ID
            status: Filter by status
            date_range: Date range for insights
            include_insights: Whether to include performance insights

        Returns:
            List of ad dictionaries
        """
        account_id = account_id or self.default_account_id

        try:
            logger.info(f"🔍 Fetching ads for account {account_id}")

            # Build fields list
            fields = [
                Ad.Field.id,
                Ad.Field.name,
                Ad.Field.adset_id,
                Ad.Field.campaign_id,
                Ad.Field.status,
                Ad.Field.effective_status,
                Ad.Field.creative,
                Ad.Field.created_time,
                Ad.Field.updated_time,
            ]

            # Build params
            params = {}
            if status:
                params['effective_status'] = [status]
            if adset_id:
                params['adset_id'] = adset_id
            if campaign_id:
                params['campaign_id'] = campaign_id

            # Get ads
            if adset_id:
                # Get from specific ad set
                adset = AdSet(adset_id)
                ads = adset.get_ads(fields=fields, params=params)
            elif campaign_id:
                # Get from specific campaign
                campaign = Campaign(campaign_id)
                ads = campaign.get_ads(fields=fields, params=params)
            else:
                # Get from account
                ad_account = AdAccount(account_id)
                ads = ad_account.get_ads(fields=fields, params=params)

            results = []
            for ad in ads:
                ad_dict = dict(ad)

                # Get insights if requested
                if include_insights:
                    insights = self._get_entity_insights(
                        ad['id'],
                        'ad',
                        date_range
                    )
                    ad_dict['insights'] = insights

                results.append(ad_dict)

            logger.info(f"✅ Retrieved {len(results)} ads")
            return results

        except FacebookRequestError as e:
            logger.error(f"❌ Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching ads: {e}")
            raise

    def _get_entity_insights(
        self,
        entity_id: str,
        level: str,
        date_range: str = 'last_30d',
        breakdowns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get insights for a specific entity (campaign, adset, or ad)

        Args:
            entity_id: ID of the entity
            level: Level (campaign, adset, ad)
            date_range: Date range
            breakdowns: Optional list of breakdowns (age, gender, country, etc.)

        Returns:
            Dictionary with aggregated insights
        """
        try:
            # Determine entity object
            if level == 'campaign':
                entity = Campaign(entity_id)
            elif level == 'adset':
                entity = AdSet(entity_id)
            elif level == 'ad':
                entity = Ad(entity_id)
            else:
                raise ValueError(f"Invalid level: {level}")

            # Build insights params
            params = {
                'time_range': self._get_date_range(date_range),
                'level': level,
            }

            if breakdowns:
                params['breakdowns'] = breakdowns

            # Build fields
            fields = [
                AdsInsights.Field.impressions,
                AdsInsights.Field.clicks,
                AdsInsights.Field.spend,
                AdsInsights.Field.reach,
                AdsInsights.Field.frequency,
                AdsInsights.Field.ctr,
                AdsInsights.Field.cpc,
                AdsInsights.Field.cpm,
                AdsInsights.Field.cpp,
                AdsInsights.Field.actions,
                AdsInsights.Field.action_values,
                AdsInsights.Field.conversions,
                AdsInsights.Field.conversion_values,
            ]

            # Get insights
            insights_data = entity.get_insights(fields=fields, params=params)

            # Aggregate insights (sum across date range)
            aggregated = {
                'impressions': 0,
                'clicks': 0,
                'spend': 0.0,
                'reach': 0,
                'frequency': 0.0,
                'conversions': 0.0,
                'conversion_value': 0.0,
                'purchases': 0.0,
                'purchase_value': 0.0,
                'leads': 0.0,
                'adds_to_cart': 0.0,
                # Post Engagement
                'post_reactions': 0.0,
                'post_likes': 0.0,
                'post_loves': 0.0,
                'post_comments': 0.0,
                'post_shares': 0.0,
                'post_engagement': 0.0,
                # Video Metrics
                'video_views': 0.0,
                'video_30s_views': 0.0,
                'video_p50_watched': 0.0,
                'video_p100_watched': 0.0,
                # Instagram Engagement
                'instagram_profile_visits': 0.0,
                'instagram_follows': 0.0,
                'instagram_saves': 0.0,
                # Other Engagement
                'photo_views': 0.0,
                'link_clicks': 0.0,
                'page_likes': 0.0,
            }

            count = 0
            for insight in insights_data:
                count += 1
                insight_dict = dict(insight)

                aggregated['impressions'] += int(insight_dict.get('impressions', 0))
                aggregated['clicks'] += int(insight_dict.get('clicks', 0))
                aggregated['spend'] += float(insight_dict.get('spend', 0))
                aggregated['reach'] += int(insight_dict.get('reach', 0))
                aggregated['frequency'] += float(insight_dict.get('frequency', 0))

                # Parse actions
                actions = insight_dict.get('actions', [])

                # Conversions
                aggregated['conversions'] += self._parse_actions(actions, 'offsite_conversion.fb_pixel_purchase')
                aggregated['purchases'] += self._parse_actions(actions, 'purchase')
                aggregated['leads'] += self._parse_actions(actions, 'lead')
                aggregated['adds_to_cart'] += self._parse_actions(actions, 'add_to_cart')

                # Post Engagement
                aggregated['post_reactions'] += self._parse_actions(actions, 'post_reaction')
                aggregated['post_likes'] += self._parse_actions(actions, 'action_reaction_like')
                aggregated['post_loves'] += self._parse_actions(actions, 'action_reaction_love')
                aggregated['post_comments'] += self._parse_actions(actions, 'post_comment')
                aggregated['post_shares'] += self._parse_actions(actions, 'post_share')
                aggregated['post_engagement'] += self._parse_actions(actions, 'post_engagement')

                # Video Metrics
                aggregated['video_views'] += self._parse_actions(actions, 'video_view')
                aggregated['video_30s_views'] += self._parse_actions(actions, 'video_30_sec_watched_actions')
                aggregated['video_p50_watched'] += self._parse_actions(actions, 'video_p50_watched_actions')
                aggregated['video_p100_watched'] += self._parse_actions(actions, 'video_p100_watched_actions')

                # Instagram Engagement
                aggregated['instagram_profile_visits'] += self._parse_actions(actions, 'instagram_profile_visit')
                aggregated['instagram_follows'] += self._parse_actions(actions, 'instagram_follow')
                aggregated['instagram_saves'] += self._parse_actions(actions, 'instagram_save')

                # Other Engagement
                aggregated['photo_views'] += self._parse_actions(actions, 'photo_view')
                aggregated['link_clicks'] += self._parse_actions(actions, 'link_click')
                aggregated['page_likes'] += self._parse_actions(actions, 'page_like')

                # Parse action values
                action_values = insight_dict.get('action_values', [])
                aggregated['purchase_value'] += self._parse_actions(action_values, 'purchase')
                aggregated['conversion_value'] += self._parse_actions(action_values, 'offsite_conversion.fb_pixel_purchase')

            # Calculate averages
            if count > 0:
                aggregated['frequency'] = aggregated['frequency'] / count

            # Calculate derived metrics
            if aggregated['clicks'] > 0:
                aggregated['ctr'] = (aggregated['clicks'] / aggregated['impressions'] * 100) if aggregated['impressions'] > 0 else 0
                aggregated['cpc'] = aggregated['spend'] / aggregated['clicks']
            else:
                aggregated['ctr'] = 0
                aggregated['cpc'] = 0

            if aggregated['impressions'] > 0:
                aggregated['cpm'] = (aggregated['spend'] / aggregated['impressions']) * 1000
            else:
                aggregated['cpm'] = 0

            if aggregated['spend'] > 0:
                aggregated['roas'] = aggregated['purchase_value'] / aggregated['spend']
            else:
                aggregated['roas'] = 0

            return aggregated

        except FacebookRequestError as e:
            logger.warning(f"⚠️  Could not fetch insights for {entity_id}: {e.api_error_message()}")
            return {}
        except Exception as e:
            logger.warning(f"⚠️  Error fetching insights for {entity_id}: {e}")
            return {}

    def get_insights(
        self,
        account_id: Optional[str] = None,
        level: str = 'campaign',
        date_range: str = 'last_30d',
        breakdowns: Optional[List[str]] = None,
        campaign_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated insights at account level

        Args:
            account_id: Meta ad account ID
            level: Aggregation level (account, campaign, adset, ad)
            date_range: Date range
            breakdowns: Optional breakdowns (age, gender, country, etc.)
            campaign_id: Optional campaign filter

        Returns:
            List of insight dictionaries
        """
        account_id = account_id or self.default_account_id

        try:
            logger.info(f"🔍 Fetching insights for account {account_id} at {level} level")

            ad_account = AdAccount(account_id)

            # Build params
            params = {
                'time_range': self._get_date_range(date_range),
                'level': level,
            }

            if breakdowns:
                params['breakdowns'] = breakdowns

            if campaign_id:
                params['filtering'] = [{'field': 'campaign.id', 'operator': 'EQUAL', 'value': campaign_id}]

            # Build fields
            fields = [
                AdsInsights.Field.campaign_id,
                AdsInsights.Field.campaign_name,
                AdsInsights.Field.adset_id,
                AdsInsights.Field.adset_name,
                AdsInsights.Field.ad_id,
                AdsInsights.Field.ad_name,
                AdsInsights.Field.date_start,
                AdsInsights.Field.date_stop,
                AdsInsights.Field.impressions,
                AdsInsights.Field.clicks,
                AdsInsights.Field.spend,
                AdsInsights.Field.reach,
                AdsInsights.Field.frequency,
                AdsInsights.Field.ctr,
                AdsInsights.Field.cpc,
                AdsInsights.Field.cpm,
                AdsInsights.Field.actions,
                AdsInsights.Field.action_values,
            ]

            # Add breakdown fields if specified
            if breakdowns:
                if 'age' in breakdowns or 'gender' in breakdowns:
                    fields.extend(['age', 'gender'])
                if 'country' in breakdowns:
                    fields.append('country')
                if 'publisher_platform' in breakdowns:
                    fields.append('publisher_platform')
                if 'platform_position' in breakdowns:
                    fields.append('platform_position')

            # Get insights
            insights_data = ad_account.get_insights(fields=fields, params=params)

            results = []
            for insight in insights_data:
                insight_dict = dict(insight)

                # Parse actions
                actions = insight_dict.get('actions', [])

                # Conversions
                insight_dict['conversions'] = self._parse_actions(actions, 'offsite_conversion.fb_pixel_purchase')
                insight_dict['purchases'] = self._parse_actions(actions, 'purchase')
                insight_dict['leads'] = self._parse_actions(actions, 'lead')
                insight_dict['adds_to_cart'] = self._parse_actions(actions, 'add_to_cart')

                # Post Engagement
                insight_dict['post_reactions'] = self._parse_actions(actions, 'post_reaction')
                insight_dict['post_likes'] = self._parse_actions(actions, 'action_reaction_like')
                insight_dict['post_loves'] = self._parse_actions(actions, 'action_reaction_love')
                insight_dict['post_comments'] = self._parse_actions(actions, 'post_comment')
                insight_dict['post_shares'] = self._parse_actions(actions, 'post_share')
                insight_dict['post_engagement'] = self._parse_actions(actions, 'post_engagement')

                # Video Metrics
                insight_dict['video_views'] = self._parse_actions(actions, 'video_view')
                insight_dict['video_30s_views'] = self._parse_actions(actions, 'video_30_sec_watched_actions')
                insight_dict['video_p50_watched'] = self._parse_actions(actions, 'video_p50_watched_actions')
                insight_dict['video_p100_watched'] = self._parse_actions(actions, 'video_p100_watched_actions')

                # Instagram Engagement
                insight_dict['instagram_profile_visits'] = self._parse_actions(actions, 'instagram_profile_visit')
                insight_dict['instagram_follows'] = self._parse_actions(actions, 'instagram_follow')
                insight_dict['instagram_saves'] = self._parse_actions(actions, 'instagram_save')

                # Other Engagement
                insight_dict['photo_views'] = self._parse_actions(actions, 'photo_view')
                insight_dict['link_clicks'] = self._parse_actions(actions, 'link_click')
                insight_dict['page_likes'] = self._parse_actions(actions, 'page_like')

                # Parse action values
                action_values = insight_dict.get('action_values', [])
                insight_dict['purchase_value'] = self._parse_actions(action_values, 'purchase')
                insight_dict['conversion_value'] = self._parse_actions(action_values, 'offsite_conversion.fb_pixel_purchase')

                # Calculate ROAS
                spend = float(insight_dict.get('spend', 0))
                if spend > 0:
                    insight_dict['roas'] = insight_dict['purchase_value'] / spend
                else:
                    insight_dict['roas'] = 0

                # Calculate engagement rate
                total_engagement = (
                    insight_dict['post_reactions'] +
                    insight_dict['post_comments'] +
                    insight_dict['post_shares'] +
                    insight_dict['link_clicks']
                )
                impressions = float(insight_dict.get('impressions', 0))
                insight_dict['engagement_rate'] = (total_engagement / impressions * 100) if impressions > 0 else 0

                results.append(insight_dict)

            logger.info(f"✅ Retrieved {len(results)} insight records")
            return results

        except FacebookRequestError as e:
            logger.error(f"❌ Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching insights: {e}")
            raise


    def get_custom_conversions(
        self,
        account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get custom conversion tracking events

        Args:
            account_id: Meta ad account ID

        Returns:
            List of custom conversion dictionaries
        """
        account_id = account_id or self.default_account_id

        try:
            logger.info(f"🔍 Fetching custom conversions for account {account_id}")

            ad_account = AdAccount(account_id)

            # Build fields list
            fields = [
                CustomConversion.Field.id,
                CustomConversion.Field.name,
                CustomConversion.Field.description,
                CustomConversion.Field.event_source_type,
                CustomConversion.Field.rule,
                CustomConversion.Field.custom_event_type,
                CustomConversion.Field.default_conversion_value,
                CustomConversion.Field.creation_time,
                CustomConversion.Field.last_fired_time,
            ]

            # Get custom conversions
            conversions = ad_account.get_custom_conversions(fields=fields)

            results = []
            for conversion in conversions:
                conversion_dict = dict(conversion)
                results.append(conversion_dict)

            logger.info(f"✅ Retrieved {len(results)} custom conversions")
            return results

        except FacebookRequestError as e:
            logger.error(f"❌ Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching custom conversions: {e}")
            raise

    def get_custom_audiences(
        self,
        account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get custom audience segments

        Args:
            account_id: Meta ad account ID

        Returns:
            List of custom audience dictionaries
        """
        account_id = account_id or self.default_account_id

        try:
            logger.info(f"🔍 Fetching custom audiences for account {account_id}")

            ad_account = AdAccount(account_id)

            # Build fields list
            fields = [
                CustomAudience.Field.id,
                CustomAudience.Field.name,
                CustomAudience.Field.description,
                CustomAudience.Field.subtype,
                CustomAudience.Field.approximate_count,
                CustomAudience.Field.customer_file_source,
                CustomAudience.Field.delivery_status,
                CustomAudience.Field.operation_status,
                CustomAudience.Field.opt_out_link,
                CustomAudience.Field.permission_for_actions,
                CustomAudience.Field.pixel_id,
                CustomAudience.Field.retention_days,
                CustomAudience.Field.rule,
                CustomAudience.Field.time_created,
                CustomAudience.Field.time_updated,
            ]

            # Get custom audiences
            audiences = ad_account.get_custom_audiences(fields=fields)

            results = []
            for audience in audiences:
                audience_dict = dict(audience)
                results.append(audience_dict)

            logger.info(f"✅ Retrieved {len(results)} custom audiences")
            return results

        except FacebookRequestError as e:
            logger.error(f"❌ Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching custom audiences: {e}")
            raise

    def get_ad_creatives(
        self,
        account_id: Optional[str] = None,
        ad_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get ad creative assets

        Args:
            account_id: Meta ad account ID
            ad_id: Optional filter by specific ad ID

        Returns:
            List of ad creative dictionaries
        """
        account_id = account_id or self.default_account_id

        try:
            logger.info(f"🔍 Fetching ad creatives for account {account_id}")

            # Build fields list
            fields = [
                AdCreative.Field.id,
                AdCreative.Field.name,
                AdCreative.Field.title,
                AdCreative.Field.body,
                AdCreative.Field.image_url,
                AdCreative.Field.video_id,
                AdCreative.Field.thumbnail_url,
                AdCreative.Field.object_story_spec,
                AdCreative.Field.object_url,
                AdCreative.Field.url_tags,
                AdCreative.Field.call_to_action_type,
                AdCreative.Field.effective_object_story_id,
                AdCreative.Field.status,
            ]

            if ad_id:
                # Get creative for specific ad
                ad = Ad(ad_id)
                creative_id = ad.api_get(fields=['creative'])['creative']['id']
                creative = AdCreative(creative_id).api_get(fields=fields)
                results = [dict(creative)]
            else:
                # Get all creatives from account
                ad_account = AdAccount(account_id)
                creatives = ad_account.get_ad_creatives(fields=fields)

                results = []
                for creative in creatives:
                    creative_dict = dict(creative)
                    results.append(creative_dict)

            logger.info(f"✅ Retrieved {len(results)} ad creatives")
            return results

        except FacebookRequestError as e:
            logger.error(f"❌ Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching ad creatives: {e}")
            raise

    def get_images(
        self,
        account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get image assets from ad account

        Args:
            account_id: Meta ad account ID

        Returns:
            List of image asset dictionaries
        """
        account_id = account_id or self.default_account_id

        try:
            logger.info(f"🔍 Fetching image assets for account {account_id}")

            ad_account = AdAccount(account_id)

            # Build fields list
            fields = [
                'id',
                'hash',
                'name',
                'url',
                'url_128',
                'width',
                'height',
                'created_time',
                'updated_time',
            ]

            # Get images
            images = ad_account.get_ad_images(fields=fields)

            results = []
            for image in images:
                image_dict = dict(image)
                results.append(image_dict)

            logger.info(f"✅ Retrieved {len(results)} image assets")
            return results

        except FacebookRequestError as e:
            logger.error(f"❌ Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching images: {e}")
            raise

    def get_videos(
        self,
        account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get video assets from ad account

        Args:
            account_id: Meta ad account ID

        Returns:
            List of video asset dictionaries
        """
        account_id = account_id or self.default_account_id

        try:
            logger.info(f"🔍 Fetching video assets for account {account_id}")

            ad_account = AdAccount(account_id)

            # Build fields list
            fields = [
                'id',
                'title',
                'description',
                'length',
                'source',
                'thumbnails',
                'embed_html',
                'format',
                'created_time',
                'updated_time',
            ]

            # Get videos
            videos = ad_account.get_ad_videos(fields=fields)

            results = []
            for video in videos:
                video_dict = dict(video)
                results.append(video_dict)

            logger.info(f"✅ Retrieved {len(results)} video assets")
            return results

        except FacebookRequestError as e:
            logger.error(f"❌ Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching videos: {e}")
            raise

    def get_leads(
        self,
        account_id: Optional[str] = None,
        form_id: Optional[str] = None,
        date_range: str = 'last_30d'
    ) -> List[Dict[str, Any]]:
        """
        Get leads from lead generation campaigns

        Args:
            account_id: Meta ad account ID
            form_id: Optional specific lead form ID
            date_range: Date range for leads

        Returns:
            List of lead dictionaries
        """
        account_id = account_id or self.default_account_id

        try:
            logger.info(f"🔍 Fetching leads for account {account_id}")

            ad_account = AdAccount(account_id)

            # Build date range
            date_filter = self._get_date_range(date_range)

            # Build fields list
            fields = [
                'id',
                'created_time',
                'ad_id',
                'ad_name',
                'form_id',
                'field_data',
                'is_organic',
            ]

            # Build params
            params = {}
            if form_id:
                params['filtering'] = [{'field': 'form_id', 'operator': 'EQUAL', 'value': form_id}]

            # Get leads
            leads = ad_account.get_leads(fields=fields, params=params)

            results = []
            for lead in leads:
                lead_dict = dict(lead)

                # Parse field_data (form responses)
                if 'field_data' in lead_dict:
                    field_data = lead_dict['field_data']
                    parsed_fields = {}
                    for field in field_data:
                        field_name = field.get('name', 'unknown')
                        field_values = field.get('values', [])
                        parsed_fields[field_name] = field_values[0] if field_values else None
                    lead_dict['parsed_fields'] = parsed_fields

                results.append(lead_dict)

            logger.info(f"✅ Retrieved {len(results)} leads")
            return results

        except FacebookRequestError as e:
            logger.error(f"❌ Facebook API error: {e.api_error_message()}")
            raise
        except Exception as e:
            logger.error(f"❌ Error fetching leads: {e}")
            raise

    # Demographic and geographic insight methods

    def get_insights_by_age_gender(
        self,
        account_id: Optional[str] = None,
        date_range: str = 'last_30d',
        level: str = 'campaign'
    ) -> List[Dict[str, Any]]:
        """
        Get insights broken down by age and gender

        Args:
            account_id: Meta ad account ID
            date_range: Date range
            level: Aggregation level (campaign, adset, ad)

        Returns:
            List of insights with age/gender breakdowns
        """
        return self.get_insights(
            account_id=account_id,
            level=level,
            date_range=date_range,
            breakdowns=['age', 'gender']
        )

    def get_insights_by_country(
        self,
        account_id: Optional[str] = None,
        date_range: str = 'last_30d',
        level: str = 'campaign'
    ) -> List[Dict[str, Any]]:
        """
        Get insights broken down by country

        Args:
            account_id: Meta ad account ID
            date_range: Date range
            level: Aggregation level (campaign, adset, ad)

        Returns:
            List of insights with country breakdowns
        """
        return self.get_insights(
            account_id=account_id,
            level=level,
            date_range=date_range,
            breakdowns=['country']
        )

    def get_insights_by_device(
        self,
        account_id: Optional[str] = None,
        date_range: str = 'last_30d',
        level: str = 'campaign'
    ) -> List[Dict[str, Any]]:
        """
        Get insights broken down by device platform

        Args:
            account_id: Meta ad account ID
            date_range: Date range
            level: Aggregation level (campaign, adset, ad)

        Returns:
            List of insights with device/platform breakdowns
        """
        return self.get_insights(
            account_id=account_id,
            level=level,
            date_range=date_range,
            breakdowns=['device_platform']
        )

    def get_insights_by_platform(
        self,
        account_id: Optional[str] = None,
        date_range: str = 'last_30d',
        level: str = 'campaign'
    ) -> List[Dict[str, Any]]:
        """
        Get insights broken down by publisher platform and position

        Args:
            account_id: Meta ad account ID
            date_range: Date range
            level: Aggregation level (campaign, adset, ad)

        Returns:
            List of insights with platform/position breakdowns
        """
        return self.get_insights(
            account_id=account_id,
            level=level,
            date_range=date_range,
            breakdowns=['publisher_platform', 'platform_position']
        )


    # =====================================
    # CAMPAIGN CREATION METHODS (NEW)
    # =====================================

    def create_sales_campaign(
        self,
        account_id: Optional[str] = None,
        campaign_name: str = "New Campaign",
        daily_budget_cents: int = 1000,  # $10.00
        status: str = "PAUSED"
    ) -> Dict[str, Any]:
        """
        Create a new Sales campaign in Meta Ads

        Args:
            account_id: Meta ad account ID (uses default if not provided)
            campaign_name: Name for the campaign
            daily_budget_cents: Daily budget in cents (1000 = $10.00)
            status: Campaign status (PAUSED or ACTIVE - recommend PAUSED for safety)

        Returns:
            Dict with campaign_id, name, and status
        """
        from facebook_business.adobjects.campaign import Campaign

        account_id = account_id or self.account_id
        if not account_id:
            raise ValueError("account_id must be provided")

        try:
            campaign = Campaign(parent_id=account_id)
            campaign.update({
                Campaign.Field.name: campaign_name,
                Campaign.Field.objective: 'OUTCOME_SALES',  # Sales objective
                Campaign.Field.status: status.upper(),
                Campaign.Field.daily_budget: daily_budget_cents,
                Campaign.Field.special_ad_categories: [],  # Empty for most campaigns
            })

            campaign.remote_create()

            logger.info(f"Created campaign {campaign_name} with ID {campaign[Campaign.Field.id]}")

            return {
                "campaign_id": campaign[Campaign.Field.id],
                "name": campaign_name,
                "status": status.upper(),
                "daily_budget_cents": daily_budget_cents
            }

        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            raise

    def create_ad_set(
        self,
        campaign_id: str,
        ad_set_name: str,
        daily_budget_cents: int,
        targeting: Dict[str, Any],
        optimization_goal: str = "OFFSITE_CONVERSIONS",
        billing_event: str = "IMPRESSIONS",
        bid_amount_cents: Optional[int] = None,
        status: str = "PAUSED"
    ) -> Dict[str, Any]:
        """
        Create an ad set within a campaign

        Args:
            campaign_id: Parent campaign ID
            ad_set_name: Name for the ad set
            daily_budget_cents: Daily budget in cents
            targeting: Targeting spec (geo, age, gender, interests)
            optimization_goal: What to optimize for (OFFSITE_CONVERSIONS, LINK_CLICKS, etc.)
            billing_event: What to bill for (IMPRESSIONS, LINK_CLICKS)
            bid_amount_cents: Optional bid cap in cents
            status: Ad set status (PAUSED or ACTIVE)

        Returns:
            Dict with ad_set_id, name, and status
        """
        from facebook_business.adobjects.adset import AdSet

        try:
            ad_set = AdSet(parent_id=self.account_id)

            ad_set_params = {
                AdSet.Field.name: ad_set_name,
                AdSet.Field.campaign_id: campaign_id,
                AdSet.Field.daily_budget: daily_budget_cents,
                AdSet.Field.billing_event: billing_event,
                AdSet.Field.optimization_goal: optimization_goal,
                AdSet.Field.targeting: targeting,
                AdSet.Field.status: status.upper(),
            }

            if bid_amount_cents:
                ad_set_params[AdSet.Field.bid_amount] = bid_amount_cents

            ad_set.update(ad_set_params)
            ad_set.remote_create()

            logger.info(f"Created ad set {ad_set_name} with ID {ad_set[AdSet.Field.id]}")

            return {
                "ad_set_id": ad_set[AdSet.Field.id],
                "name": ad_set_name,
                "status": status.upper(),
                "daily_budget_cents": daily_budget_cents
            }

        except Exception as e:
            logger.error(f"Error creating ad set: {e}")
            raise

    def upload_image(
        self,
        account_id: Optional[str] = None,
        image_bytes: bytes = None,
        image_url: Optional[str] = None,
        filename: str = "ad_image.jpg"
    ) -> str:
        """
        Upload an image to Meta and get the image hash

        Args:
            account_id: Meta ad account ID
            image_bytes: Image file bytes (OR image_url)
            image_url: URL of image to upload (OR image_bytes)
            filename: Filename for the image

        Returns:
            Image hash string (needed for ad creative)
        """
        from facebook_business.adobjects.adimage import AdImage

        account_id = account_id or self.account_id
        if not account_id:
            raise ValueError("account_id must be provided")

        try:
            image = AdImage(parent_id=account_id)

            if image_bytes:
                image[AdImage.Field.bytes] = image_bytes
                image[AdImage.Field.filename] = filename
            elif image_url:
                image[AdImage.Field.url] = image_url
            else:
                raise ValueError("Either image_bytes or image_url must be provided")

            image.remote_create()

            image_hash = image[AdImage.Field.hash]
            logger.info(f"Uploaded image with hash {image_hash}")

            return image_hash

        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            raise

    def create_ad_creative(
        self,
        account_id: Optional[str] = None,
        page_id: str = None,
        creative_name: str = "Ad Creative",
        primary_text: str = "",
        headline: str = "",
        description: str = "",
        landing_url: str = "",
        image_hash: str = None,
        call_to_action_type: str = "SHOP_NOW"
    ) -> str:
        """
        Create an ad creative (the actual ad content)

        Args:
            account_id: Meta ad account ID
            page_id: Facebook Page ID
            creative_name: Name for the creative
            primary_text: Main ad copy (max 125 chars)
            headline: Ad headline (max 27 chars)
            description: Ad description (max 27 chars)
            landing_url: Destination URL
            image_hash: Image hash from upload_image()
            call_to_action_type: CTA button type (SHOP_NOW, LEARN_MORE, etc.)

        Returns:
            Creative ID string
        """
        from facebook_business.adobjects.adcreative import AdCreative

        account_id = account_id or self.account_id
        if not account_id:
            raise ValueError("account_id must be provided")

        if not page_id:
            raise ValueError("page_id must be provided")

        try:
            creative = AdCreative(parent_id=account_id)

            creative.update({
                AdCreative.Field.name: creative_name,
                AdCreative.Field.object_story_spec: {
                    'page_id': page_id,
                    'link_data': {
                        'message': primary_text[:125],  # Enforce limit
                        'link': landing_url,
                        'name': headline[:27],  # Enforce limit
                        'description': description[:27],  # Enforce limit
                        'image_hash': image_hash,
                        'call_to_action': {
                            'type': call_to_action_type
                        }
                    }
                }
            })

            creative.remote_create()

            creative_id = creative[AdCreative.Field.id]
            logger.info(f"Created ad creative {creative_name} with ID {creative_id}")

            return creative_id

        except Exception as e:
            logger.error(f"Error creating ad creative: {e}")
            raise

    def create_ad(
        self,
        account_id: Optional[str] = None,
        ad_set_id: str = None,
        creative_id: str = None,
        ad_name: str = "New Ad",
        status: str = "PAUSED"
    ) -> Dict[str, Any]:
        """
        Create an ad (links creative to ad set)

        Args:
            account_id: Meta ad account ID
            ad_set_id: Parent ad set ID
            creative_id: Creative ID to use
            ad_name: Name for the ad
            status: Ad status (PAUSED or ACTIVE)

        Returns:
            Dict with ad_id, name, and status
        """
        from facebook_business.adobjects.ad import Ad

        account_id = account_id or self.account_id
        if not account_id:
            raise ValueError("account_id must be provided")

        if not ad_set_id or not creative_id:
            raise ValueError("ad_set_id and creative_id must be provided")

        try:
            ad = Ad(parent_id=account_id)

            ad.update({
                Ad.Field.name: ad_name,
                Ad.Field.adset_id: ad_set_id,
                Ad.Field.creative: {'creative_id': creative_id},
                Ad.Field.status: status.upper(),
            })

            ad.remote_create()

            ad_id = ad[Ad.Field.id]
            logger.info(f"Created ad {ad_name} with ID {ad_id}")

            return {
                "ad_id": ad_id,
                "name": ad_name,
                "status": status.upper(),
                "ad_set_id": ad_set_id,
                "creative_id": creative_id
            }

        except Exception as e:
            logger.error(f"Error creating ad: {e}")
            raise


def get_meta_ads_service(account_id: Optional[str] = None) -> MetaAdsService:
    """
    Create a new MetaAdsService instance

    Args:
        account_id: Optional Meta ad account ID (format: act_123456789)

    Returns:
        MetaAdsService instance
    """
    # Reload .env.meta file to get latest credentials
    env_path = Path(__file__).parent.parent.parent.parent / '.env.meta'
    if env_path.exists():
        load_dotenv(env_path, override=True)
    return MetaAdsService(account_id=account_id)
