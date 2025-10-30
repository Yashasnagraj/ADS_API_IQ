"""
Meta (Facebook) Ads ETL Pipeline

Extracts data from Meta Marketing API and loads into local database:
- Campaigns (objectives, budgets, status)
- Ad Sets (targeting, bidding, optimization)
- Ads (creatives, CTAs)
- Insights (performance metrics: impressions, clicks, conversions, ROAS)

Usage:
    python meta_ads_etl.py [--days=30] [--customer-id=1]

    --days: Number of days to extract insights (default: 30)
    --customer-id: Customer ID to extract for (default: from .env.meta)
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adsinsights import AdsInsights

# Add project root and api directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'api'))

from api.app.db.database import SessionLocal, engine
from api.app.db import models

# Create all tables
models.Base.metadata.create_all(bind=engine)


def load_config():
    """Load configuration from .env.meta"""
    env_path = Path(__file__).parent / '.env.meta'

    if not env_path.exists():
        print("❌ ERROR: .env.meta file not found!")
        print("   Please run setup_meta_ads.py first")
        sys.exit(1)

    load_dotenv(env_path)

    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')
    access_token = os.getenv('META_ACCESS_TOKEN')
    ad_account_id = os.getenv('META_AD_ACCOUNT_ID')
    customer_id = os.getenv('CUSTOMER_ID')
    api_version = os.getenv('META_API_VERSION', 'v19.0')

    if not all([app_id, app_secret, access_token, ad_account_id, customer_id]):
        print("❌ ERROR: Missing configuration in .env.meta")
        sys.exit(1)

    return {
        'app_id': app_id,
        'app_secret': app_secret,
        'access_token': access_token,
        'ad_account_id': ad_account_id,
        'customer_id': int(customer_id),
        'api_version': api_version
    }


def init_meta_api(config):
    """Initialize Meta Marketing API"""
    FacebookAdsApi.init(
        app_id=config['app_id'],
        app_secret=config['app_secret'],
        access_token=config['access_token'],
        api_version=config['api_version']
    )


def extract_campaigns(ad_account_id, customer_id):
    """
    Extract campaigns from Meta Ads

    Fields:
    - Name, status, objective
    - Budget (daily/lifetime)
    - Bid strategy
    - Start/stop times
    """
    print(f"\n📊 Extracting campaigns...")

    try:
        ad_account = AdAccount(ad_account_id)

        campaigns = ad_account.get_campaigns(fields=[
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
            Campaign.Field.special_ad_categories,
            Campaign.Field.created_time,
            Campaign.Field.updated_time,
            Campaign.Field.start_time,
            Campaign.Field.stop_time,
        ])

        db = SessionLocal()
        count = 0

        for campaign in campaigns:
            campaign_id = campaign.get('id')

            # Check if campaign exists
            existing = db.query(models.MetaCampaign).filter(
                models.MetaCampaign.campaign_id == campaign_id
            ).first()

            # Parse budgets (Meta returns in cents, convert to currency units)
            daily_budget = float(campaign.get('daily_budget', 0)) / 100 if campaign.get('daily_budget') else None
            lifetime_budget = float(campaign.get('lifetime_budget', 0)) / 100 if campaign.get('lifetime_budget') else None
            budget_remaining = float(campaign.get('budget_remaining', 0)) / 100 if campaign.get('budget_remaining') else None

            # Parse timestamps
            created_time = datetime.strptime(campaign.get('created_time'), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) if campaign.get('created_time') else None
            updated_time = datetime.strptime(campaign.get('updated_time'), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) if campaign.get('updated_time') else None
            start_time = datetime.strptime(campaign.get('start_time'), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) if campaign.get('start_time') else None
            stop_time = datetime.strptime(campaign.get('stop_time'), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) if campaign.get('stop_time') else None

            if existing:
                # Update existing
                existing.name = campaign.get('name')
                existing.status = campaign.get('status')
                existing.effective_status = campaign.get('effective_status')
                existing.objective = campaign.get('objective')
                existing.daily_budget = daily_budget
                existing.lifetime_budget = lifetime_budget
                existing.budget_remaining = budget_remaining
                existing.bid_strategy = campaign.get('bid_strategy')
                existing.buying_type = campaign.get('buying_type')
                existing.special_ad_categories = str(campaign.get('special_ad_categories', []))
                existing.updated_time = updated_time
                existing.start_time = start_time
                existing.stop_time = stop_time
            else:
                # Create new
                meta_campaign = models.MetaCampaign(
                    campaign_id=campaign_id,
                    account_id=ad_account_id,
                    customer_id=customer_id,
                    name=campaign.get('name'),
                    status=campaign.get('status'),
                    effective_status=campaign.get('effective_status'),
                    objective=campaign.get('objective'),
                    daily_budget=daily_budget,
                    lifetime_budget=lifetime_budget,
                    budget_remaining=budget_remaining,
                    bid_strategy=campaign.get('bid_strategy'),
                    buying_type=campaign.get('buying_type'),
                    special_ad_categories=str(campaign.get('special_ad_categories', [])),
                    created_time=created_time,
                    updated_time=updated_time,
                    start_time=start_time,
                    stop_time=stop_time
                )
                db.add(meta_campaign)
                count += 1

        db.commit()
        db.close()

        print(f"   ✅ Extracted {count} campaigns")
        return count

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return 0


def extract_adsets(ad_account_id, customer_id):
    """
    Extract ad sets from Meta Ads

    Fields:
    - Name, status
    - Budget, bid amount
    - Targeting (stored as JSON)
    - Optimization goal
    """
    print(f"\n📊 Extracting ad sets...")

    try:
        ad_account = AdAccount(ad_account_id)

        adsets = ad_account.get_ad_sets(fields=[
            AdSet.Field.id,
            AdSet.Field.name,
            AdSet.Field.campaign_id,
            AdSet.Field.status,
            AdSet.Field.effective_status,
            AdSet.Field.daily_budget,
            AdSet.Field.lifetime_budget,
            AdSet.Field.bid_amount,
            AdSet.Field.bid_strategy,
            AdSet.Field.targeting,
            AdSet.Field.optimization_goal,
            AdSet.Field.billing_event,
            AdSet.Field.created_time,
            AdSet.Field.updated_time,
            AdSet.Field.start_time,
            AdSet.Field.end_time,
        ])

        db = SessionLocal()
        count = 0

        for adset in adsets:
            adset_id = adset.get('id')

            # Check if adset exists
            existing = db.query(models.MetaAdSet).filter(
                models.MetaAdSet.adset_id == adset_id
            ).first()

            # Parse budgets
            daily_budget = float(adset.get('daily_budget', 0)) / 100 if adset.get('daily_budget') else None
            lifetime_budget = float(adset.get('lifetime_budget', 0)) / 100 if adset.get('lifetime_budget') else None
            bid_amount = float(adset.get('bid_amount', 0)) / 100 if adset.get('bid_amount') else None

            # Parse timestamps
            created_time = datetime.strptime(adset.get('created_time'), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) if adset.get('created_time') else None
            updated_time = datetime.strptime(adset.get('updated_time'), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) if adset.get('updated_time') else None
            start_time = datetime.strptime(adset.get('start_time'), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) if adset.get('start_time') else None
            end_time = datetime.strptime(adset.get('end_time'), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) if adset.get('end_time') else None

            # Targeting as JSON string
            targeting = str(adset.get('targeting', {}))

            if existing:
                # Update existing
                existing.name = adset.get('name')
                existing.campaign_id = adset.get('campaign_id')
                existing.status = adset.get('status')
                existing.effective_status = adset.get('effective_status')
                existing.daily_budget = daily_budget
                existing.lifetime_budget = lifetime_budget
                existing.bid_amount = bid_amount
                existing.bid_strategy = adset.get('bid_strategy')
                existing.targeting = targeting
                existing.optimization_goal = adset.get('optimization_goal')
                existing.billing_event = adset.get('billing_event')
                existing.updated_time = updated_time
                existing.start_time = start_time
                existing.end_time = end_time
            else:
                # Create new
                meta_adset = models.MetaAdSet(
                    adset_id=adset_id,
                    campaign_id=adset.get('campaign_id'),
                    account_id=ad_account_id,
                    customer_id=customer_id,
                    name=adset.get('name'),
                    status=adset.get('status'),
                    effective_status=adset.get('effective_status'),
                    daily_budget=daily_budget,
                    lifetime_budget=lifetime_budget,
                    bid_amount=bid_amount,
                    bid_strategy=adset.get('bid_strategy'),
                    targeting=targeting,
                    optimization_goal=adset.get('optimization_goal'),
                    billing_event=adset.get('billing_event'),
                    created_time=created_time,
                    updated_time=updated_time,
                    start_time=start_time,
                    end_time=end_time
                )
                db.add(meta_adset)
                count += 1

        db.commit()
        db.close()

        print(f"   ✅ Extracted {count} ad sets")
        return count

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return 0


def extract_ads(ad_account_id, customer_id):
    """
    Extract ads (creatives) from Meta Ads

    Fields:
    - Name, status
    - Creative details (title, body, image, video)
    - Call to action
    """
    print(f"\n📊 Extracting ads...")

    try:
        ad_account = AdAccount(ad_account_id)

        ads = ad_account.get_ads(fields=[
            Ad.Field.id,
            Ad.Field.name,
            Ad.Field.adset_id,
            Ad.Field.campaign_id,
            Ad.Field.status,
            Ad.Field.effective_status,
            Ad.Field.creative,
            Ad.Field.tracking_specs,
            Ad.Field.created_time,
            Ad.Field.updated_time,
        ])

        db = SessionLocal()
        count = 0

        for ad in ads:
            ad_id = ad.get('id')

            # Check if ad exists
            existing = db.query(models.MetaAd).filter(
                models.MetaAd.ad_id == ad_id
            ).first()

            # Parse creative
            creative = ad.get('creative', {})
            creative_id = creative.get('id') if isinstance(creative, dict) else None

            # Parse timestamps
            created_time = datetime.strptime(ad.get('created_time'), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) if ad.get('created_time') else None
            updated_time = datetime.strptime(ad.get('updated_time'), '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) if ad.get('updated_time') else None

            if existing:
                # Update existing
                existing.name = ad.get('name')
                existing.adset_id = ad.get('adset_id')
                existing.campaign_id = ad.get('campaign_id')
                existing.status = ad.get('status')
                existing.effective_status = ad.get('effective_status')
                existing.creative_id = creative_id
                existing.tracking_specs = str(ad.get('tracking_specs', []))
                existing.updated_time = updated_time
            else:
                # Create new
                meta_ad = models.MetaAd(
                    ad_id=ad_id,
                    adset_id=ad.get('adset_id'),
                    campaign_id=ad.get('campaign_id'),
                    account_id=ad_account_id,
                    customer_id=customer_id,
                    name=ad.get('name'),
                    status=ad.get('status'),
                    effective_status=ad.get('effective_status'),
                    creative_id=creative_id,
                    tracking_specs=str(ad.get('tracking_specs', [])),
                    created_time=created_time,
                    updated_time=updated_time
                )
                db.add(meta_ad)
                count += 1

        db.commit()
        db.close()

        print(f"   ✅ Extracted {count} ads")
        return count

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return 0


def extract_insights(ad_account_id, customer_id, days=30):
    """
    Extract performance insights (daily metrics)

    Metrics:
    - Impressions, clicks, spend
    - Reach, frequency
    - Conversions, purchase value
    - CTR, CPC, CPM, ROAS
    """
    print(f"\n📊 Extracting insights (last {days} days)...")

    try:
        ad_account = AdAccount(ad_account_id)

        # Date range
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        # Get insights at campaign level
        insights = ad_account.get_insights(
            fields=[
                AdsInsights.Field.campaign_id,
                AdsInsights.Field.date_start,
                AdsInsights.Field.date_stop,
                AdsInsights.Field.impressions,
                AdsInsights.Field.clicks,
                AdsInsights.Field.spend,
                AdsInsights.Field.reach,
                AdsInsights.Field.frequency,
                AdsInsights.Field.inline_link_clicks,
                AdsInsights.Field.inline_post_engagement,
                AdsInsights.Field.actions,
                AdsInsights.Field.action_values,
                AdsInsights.Field.ctr,
                AdsInsights.Field.cpc,
                AdsInsights.Field.cpm,
                AdsInsights.Field.cpp,
            ],
            params={
                'time_range': {'since': start_date, 'until': end_date},
                'level': 'campaign',
                'time_increment': 1,  # Daily breakdown
            }
        )

        db = SessionLocal()
        count = 0

        for insight in insights:
            campaign_id = insight.get('campaign_id')
            date_start = insight.get('date_start')
            date_stop = insight.get('date_stop')

            # Create unique insight ID
            insight_id = f"campaign_{campaign_id}_{date_start}"

            # Check if insight exists
            existing = db.query(models.MetaInsights).filter(
                models.MetaInsights.insight_id == insight_id
            ).first()

            # Parse metrics
            impressions = int(insight.get('impressions', 0))
            clicks = int(insight.get('clicks', 0))
            spend = float(insight.get('spend', 0))
            reach = int(insight.get('reach', 0))
            frequency = float(insight.get('frequency', 0))
            inline_link_clicks = int(insight.get('inline_link_clicks', 0))
            inline_post_engagement = int(insight.get('inline_post_engagement', 0))

            # Parse CTR, CPC, CPM
            ctr = float(insight.get('ctr', 0))
            cpc = float(insight.get('cpc', 0))
            cpm = float(insight.get('cpm', 0))
            cpp = float(insight.get('cpp', 0))

            # Parse conversions from actions array
            conversions = 0
            purchases = 0
            purchase_value = 0.0
            adds_to_cart = 0
            checkouts = 0
            leads = 0

            actions = insight.get('actions', [])
            action_values = insight.get('action_values', [])

            for action in actions:
                action_type = action.get('action_type')
                value = float(action.get('value', 0))

                if action_type == 'omni_purchase' or action_type == 'purchase':
                    purchases = int(value)
                    conversions += value
                elif action_type == 'add_to_cart':
                    adds_to_cart = int(value)
                elif action_type == 'initiate_checkout':
                    checkouts = int(value)
                elif action_type == 'lead':
                    leads = int(value)
                    conversions += value

            for action_value in action_values:
                action_type = action_value.get('action_type')
                value = float(action_value.get('value', 0))

                if action_type == 'omni_purchase' or action_type == 'purchase':
                    purchase_value = value

            # Calculate ROAS
            roas = round(purchase_value / spend, 2) if spend > 0 else 0

            if existing:
                # Update existing
                existing.impressions = impressions
                existing.clicks = clicks
                existing.spend = spend
                existing.reach = reach
                existing.frequency = frequency
                existing.inline_link_clicks = inline_link_clicks
                existing.inline_post_engagement = inline_post_engagement
                existing.conversions = conversions
                existing.purchases = purchases
                existing.purchase_value = purchase_value
                existing.adds_to_cart = adds_to_cart
                existing.checkouts_initiated = checkouts
                existing.leads = leads
                existing.ctr = ctr
                existing.cpc = cpc
                existing.cpm = cpm
                existing.cpp = cpp
                existing.roas = roas
            else:
                # Create new
                meta_insight = models.MetaInsights(
                    insight_id=insight_id,
                    entity_type='campaign',
                    entity_id=campaign_id,
                    campaign_id=campaign_id,
                    account_id=ad_account_id,
                    customer_id=customer_id,
                    date_start=date_start,
                    date_stop=date_stop,
                    impressions=impressions,
                    clicks=clicks,
                    spend=spend,
                    reach=reach,
                    frequency=frequency,
                    inline_link_clicks=inline_link_clicks,
                    inline_post_engagement=inline_post_engagement,
                    conversions=conversions,
                    purchases=purchases,
                    purchase_value=purchase_value,
                    adds_to_cart=adds_to_cart,
                    checkouts_initiated=checkouts,
                    leads=leads,
                    ctr=ctr,
                    cpc=cpc,
                    cpm=cpm,
                    cpp=cpp,
                    roas=roas
                )
                db.add(meta_insight)
                count += 1

        db.commit()
        db.close()

        print(f"   ✅ Extracted {count} insight records")
        return count

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return 0


def update_account_sync_time(ad_account_id):
    """Update last_sync_at timestamp for ad account"""
    db = SessionLocal()
    try:
        account = db.query(models.MetaAdAccount).filter(
            models.MetaAdAccount.account_id == ad_account_id
        ).first()

        if account:
            account.last_sync_at = datetime.now()
            db.commit()
    finally:
        db.close()


def main():
    """Main ETL flow"""
    parser = argparse.ArgumentParser(description='Meta Ads ETL Pipeline')
    parser.add_argument('--days', type=int, default=30, help='Number of days to extract insights')
    parser.add_argument('--customer-id', type=int, help='Customer ID override')
    args = parser.parse_args()

    print("=" * 70)
    print("META ADS ETL PIPELINE")
    print("=" * 70)

    # Load configuration
    config = load_config()

    # Override customer ID if provided
    if args.customer_id:
        config['customer_id'] = args.customer_id

    print(f"\n📋 Configuration:")
    print(f"   Ad Account ID: {config['ad_account_id']}")
    print(f"   Customer ID: {config['customer_id']}")
    print(f"   Days to extract: {args.days}")

    # Initialize API
    print(f"\n🔐 Initializing Meta Marketing API...")
    init_meta_api(config)
    print(f"   ✅ Initialized")

    # Run ETL tasks
    total_campaigns = extract_campaigns(config['ad_account_id'], config['customer_id'])
    total_adsets = extract_adsets(config['ad_account_id'], config['customer_id'])
    total_ads = extract_ads(config['ad_account_id'], config['customer_id'])
    total_insights = extract_insights(config['ad_account_id'], config['customer_id'], args.days)

    # Update sync timestamp
    update_account_sync_time(config['ad_account_id'])

    # Summary
    print("\n" + "=" * 70)
    print("✅ META ADS ETL PIPELINE COMPLETED")
    print("=" * 70)
    print(f"\n📊 Data Summary:")
    print(f"   Campaigns:  {total_campaigns}")
    print(f"   Ad Sets:    {total_adsets}")
    print(f"   Ads:        {total_ads}")
    print(f"   Insights:   {total_insights}")
    print(f"\n📝 Next Steps:")
    print(f"   1. Start API server: cd api && uvicorn app.main:app --reload")
    print(f"   2. View docs: http://localhost:8000/docs")
    print(f"   3. Test endpoint: http://localhost:8000/api/v1/meta/campaigns?customer_id={config['customer_id']}")
    print()


if __name__ == "__main__":
    main()
