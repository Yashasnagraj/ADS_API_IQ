#!/usr/bin/env python3
"""
Google Ads ETL Pipeline
Extracts comprehensive data, transforms it, and loads into SQLite database
with proper schema for multi-agent ML training
"""

import sys
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import json
import os

# Configuration
DB_FILE = "google_ads_data.db"
OUTPUT_DIR = "extracted_data"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

class GoogleAdsETL:
    def __init__(self):
        """Initialize ETL pipeline."""
        try:
            self.client = GoogleAdsClient.load_from_storage("google-ads.yaml")
            self.ga_service = self.client.get_service("GoogleAdsService")
            self.conn = sqlite3.connect(DB_FILE)
            self.cursor = self.conn.cursor()
            self.manager_id = "3341907700"
            print(f"[INFO] ETL Pipeline initialized. Database: {DB_FILE}")
        except Exception as e:
            print(f"[ERROR] Failed to initialize: {e}")
            sys.exit(1)

    def create_database_schema(self):
        """Create SQLite database schema."""
        print("[INFO] Creating database schema...")

        # Drop existing tables
        tables = ['campaigns', 'ad_groups', 'keywords', 'search_terms', 'campaign_keywords', 'ml_features']
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table}")

        # Campaigns table
        self.cursor.execute("""
            CREATE TABLE campaigns (
                campaign_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                campaign_name TEXT,
                status TEXT,
                serving_status TEXT,
                channel_type TEXT,
                channel_subtype TEXT,
                bidding_strategy_type TEXT,
                budget_id TEXT,
                budget_amount_micros INTEGER,
                start_date TEXT,
                end_date TEXT,
                optimization_score REAL,
                target_cpa_micros INTEGER,
                target_roas REAL,
                network_target_search BOOLEAN,
                network_target_content BOOLEAN,
                network_target_partner BOOLEAN,
                geo_target_type_positive TEXT,
                geo_target_type_negative TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Ad Groups table
        self.cursor.execute("""
            CREATE TABLE ad_groups (
                ad_group_id INTEGER PRIMARY KEY,
                campaign_id INTEGER,
                customer_id INTEGER,
                ad_group_name TEXT,
                status TEXT,
                type TEXT,
                cpc_bid_micros INTEGER,
                cpm_bid_micros INTEGER,
                target_cpa_micros INTEGER,
                target_roas REAL,
                ad_rotation_mode TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
            )
        """)

        # Keywords table with comprehensive fields
        self.cursor.execute("""
            CREATE TABLE keywords (
                keyword_id TEXT PRIMARY KEY,
                ad_group_id INTEGER,
                campaign_id INTEGER,
                customer_id INTEGER,
                keyword_text TEXT,
                match_type TEXT,
                status TEXT,
                quality_score INTEGER,
                creative_quality_score TEXT,
                landing_page_quality_score TEXT,
                search_predicted_ctr TEXT,
                cpc_bid_micros INTEGER,
                first_page_cpc_micros INTEGER,
                first_position_cpc_micros INTEGER,
                top_of_page_cpc_micros INTEGER,
                approval_status TEXT,
                system_serving_status TEXT,
                is_negative BOOLEAN,
                bid_modifier REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ad_group_id) REFERENCES ad_groups(ad_group_id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
            )
        """)

        # Search Terms table
        self.cursor.execute("""
            CREATE TABLE search_terms (
                search_term_id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword_id TEXT,
                ad_group_id INTEGER,
                campaign_id INTEGER,
                customer_id INTEGER,
                search_term TEXT,
                keyword_text TEXT,
                match_type TEXT,
                search_term_match_type TEXT,
                date TEXT,
                clicks INTEGER,
                impressions INTEGER,
                cost_micros INTEGER,
                conversions REAL,
                conversion_value REAL,
                ctr REAL,
                avg_cpc_micros INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id),
                FOREIGN KEY (ad_group_id) REFERENCES ad_groups(ad_group_id),
                FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
            )
        """)

        # Campaign-Keywords performance aggregation table
        self.cursor.execute("""
            CREATE TABLE campaign_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                keyword_id TEXT,
                customer_id INTEGER,
                date TEXT,
                clicks INTEGER,
                impressions INTEGER,
                cost_micros INTEGER,
                conversions REAL,
                conversion_value REAL,
                ctr REAL,
                conversion_rate REAL,
                avg_cpc_micros INTEGER,
                avg_position REAL,
                absolute_top_impression_percentage REAL,
                top_impression_percentage REAL,
                search_impression_share REAL,
                search_rank_lost_impression_share REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
                FOREIGN KEY (keyword_id) REFERENCES keywords(keyword_id)
            )
        """)

        # ML Features table (denormalized for training)
        self.cursor.execute("""
            CREATE TABLE ml_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                campaign_id INTEGER,
                campaign_name TEXT,
                channel_type TEXT,
                bidding_strategy TEXT,
                budget_amount REAL,
                keyword_id TEXT,
                keyword_text TEXT,
                match_type TEXT,
                quality_score INTEGER,
                avg_cpc REAL,
                ctr REAL,
                conversion_rate REAL,
                conversions REAL,
                cost REAL,
                impressions INTEGER,
                clicks INTEGER,
                competition_index REAL,
                search_volume_trend REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()
        print("[INFO] Database schema created successfully")

    def extract_campaigns(self, customer_id):
        """Extract comprehensive campaign data."""
        print(f"[INFO] Extracting campaigns for customer {customer_id}...")

        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.serving_status,
                campaign.advertising_channel_type,
                campaign.advertising_channel_sub_type,
                campaign.bidding_strategy_type,
                campaign.campaign_budget,
                campaign.start_date,
                campaign.end_date,
                campaign.optimization_score,
                campaign.target_cpa.target_cpa_micros,
                campaign.target_roas.target_roas,
                campaign.network_settings.target_google_search,
                campaign.network_settings.target_content_network,
                campaign.network_settings.target_partner_search_network,
                campaign.geo_target_type_setting.positive_geo_target_type,
                campaign.geo_target_type_setting.negative_geo_target_type,
                campaign_budget.amount_micros,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.average_cpc,
                metrics.ctr,
                metrics.cost_per_conversion,
                metrics.search_impression_share,
                metrics.search_rank_lost_impression_share,
                metrics.absolute_top_impression_percentage,
                metrics.top_impression_percentage
            FROM campaign
            LEFT JOIN campaign_budget ON campaign.campaign_budget = campaign_budget.resource_name
            WHERE campaign.status != 'REMOVED'
            ORDER BY campaign.id
        """

        campaigns = []
        try:
            response = self.ga_service.search(customer_id=customer_id, query=query)

            for row in response:
                campaign = row.campaign
                metrics = row.metrics if hasattr(row, 'metrics') else None
                budget = row.campaign_budget if hasattr(row, 'campaign_budget') else None

                campaign_data = {
                    'campaign_id': campaign.id,
                    'customer_id': customer_id,
                    'campaign_name': campaign.name,
                    'status': campaign.status.name,
                    'serving_status': campaign.serving_status.name if campaign.serving_status else None,
                    'channel_type': campaign.advertising_channel_type.name,
                    'channel_subtype': campaign.advertising_channel_sub_type.name if campaign.advertising_channel_sub_type else None,
                    'bidding_strategy_type': campaign.bidding_strategy_type.name,
                    'budget_id': campaign.campaign_budget,
                    'budget_amount_micros': budget.amount_micros if budget and budget.amount_micros else 0,
                    'start_date': campaign.start_date,
                    'end_date': campaign.end_date,
                    'optimization_score': campaign.optimization_score,
                    'target_cpa_micros': campaign.target_cpa.target_cpa_micros if campaign.target_cpa.target_cpa_micros else None,
                    'target_roas': campaign.target_roas.target_roas if campaign.target_roas.target_roas else None,
                    'network_target_search': campaign.network_settings.target_google_search,
                    'network_target_content': campaign.network_settings.target_content_network,
                    'network_target_partner': campaign.network_settings.target_partner_search_network,
                    'geo_target_type_positive': campaign.geo_target_type_setting.positive_geo_target_type.name if campaign.geo_target_type_setting.positive_geo_target_type else None,
                    'geo_target_type_negative': campaign.geo_target_type_setting.negative_geo_target_type.name if campaign.geo_target_type_setting.negative_geo_target_type else None
                }
                campaigns.append(campaign_data)

                # Insert into database
                self.cursor.execute("""
                    INSERT OR REPLACE INTO campaigns VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                    )
                """, tuple(campaign_data.values()))

        except GoogleAdsException as ex:
            print(f"[ERROR] Campaign extraction failed: {ex.error.code().name}")

        self.conn.commit()
        return campaigns

    def extract_ad_groups(self, customer_id):
        """Extract comprehensive ad group data."""
        print(f"[INFO] Extracting ad groups for customer {customer_id}...")

        query = """
            SELECT
                ad_group.id,
                ad_group.campaign,
                ad_group.name,
                ad_group.status,
                ad_group.type,
                ad_group.cpc_bid_micros,
                ad_group.cpm_bid_micros,
                ad_group.target_cpa_micros,
                ad_group.target_roas,
                ad_group.ad_rotation_mode,
                campaign.id
            FROM ad_group
            WHERE ad_group.status != 'REMOVED'
            ORDER BY ad_group.id
        """

        ad_groups = []
        try:
            response = self.ga_service.search(customer_id=customer_id, query=query)

            for row in response:
                ad_group = row.ad_group
                campaign = row.campaign

                ad_group_data = {
                    'ad_group_id': ad_group.id,
                    'campaign_id': campaign.id,
                    'customer_id': customer_id,
                    'ad_group_name': ad_group.name,
                    'status': ad_group.status.name,
                    'type': ad_group.type.name,
                    'cpc_bid_micros': ad_group.cpc_bid_micros if ad_group.cpc_bid_micros else None,
                    'cpm_bid_micros': ad_group.cpm_bid_micros if ad_group.cpm_bid_micros else None,
                    'target_cpa_micros': ad_group.target_cpa_micros if ad_group.target_cpa_micros else None,
                    'target_roas': ad_group.target_roas if ad_group.target_roas else None,
                    'ad_rotation_mode': ad_group.ad_rotation_mode.name if ad_group.ad_rotation_mode else None
                }
                ad_groups.append(ad_group_data)

                # Insert into database
                self.cursor.execute("""
                    INSERT OR REPLACE INTO ad_groups VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                    )
                """, tuple(ad_group_data.values()))

        except GoogleAdsException as ex:
            print(f"[ERROR] Ad group extraction failed: {ex.error.code().name}")

        self.conn.commit()
        return ad_groups

    def extract_keywords(self, customer_id):
        """Extract comprehensive keyword data."""
        print(f"[INFO] Extracting keywords for customer {customer_id}...")

        query = """
            SELECT
                ad_group_criterion.criterion_id,
                ad_group_criterion.ad_group,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.status,
                ad_group_criterion.quality_info.quality_score,
                ad_group_criterion.quality_info.creative_quality_score,
                ad_group_criterion.quality_info.post_click_quality_score,
                ad_group_criterion.quality_info.search_predicted_ctr,
                ad_group_criterion.cpc_bid_micros,
                ad_group_criterion.position_estimates.first_page_cpc_micros,
                ad_group_criterion.position_estimates.first_position_cpc_micros,
                ad_group_criterion.position_estimates.top_of_page_cpc_micros,
                ad_group_criterion.approval_status,
                ad_group_criterion.system_serving_status,
                ad_group_criterion.negative,
                ad_group_criterion.bid_modifier,
                ad_group.id,
                campaign.id,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.absolute_top_impression_percentage,
                metrics.top_impression_percentage,
                metrics.search_impression_share,
                metrics.search_rank_lost_impression_share
            FROM keyword_view
            WHERE ad_group_criterion.type = 'KEYWORD'
                AND segments.date DURING LAST_30_DAYS
            ORDER BY metrics.impressions DESC
            LIMIT 5000
        """

        keywords = []
        try:
            response = self.ga_service.search(customer_id=customer_id, query=query)

            for row in response:
                criterion = row.ad_group_criterion
                ad_group = row.ad_group
                campaign = row.campaign
                metrics = row.metrics if hasattr(row, 'metrics') else None
                quality_info = criterion.quality_info
                position_estimates = criterion.position_estimates

                keyword_id = f"{customer_id}_{ad_group.id}_{criterion.criterion_id}"

                keyword_data = {
                    'keyword_id': keyword_id,
                    'ad_group_id': ad_group.id,
                    'campaign_id': campaign.id,
                    'customer_id': customer_id,
                    'keyword_text': criterion.keyword.text,
                    'match_type': criterion.keyword.match_type.name,
                    'status': criterion.status.name,
                    'quality_score': quality_info.quality_score if quality_info.quality_score else None,
                    'creative_quality_score': quality_info.creative_quality_score.name if quality_info.creative_quality_score else None,
                    'landing_page_quality_score': quality_info.post_click_quality_score.name if quality_info.post_click_quality_score else None,
                    'search_predicted_ctr': quality_info.search_predicted_ctr.name if quality_info.search_predicted_ctr else None,
                    'cpc_bid_micros': criterion.cpc_bid_micros if criterion.cpc_bid_micros else None,
                    'first_page_cpc_micros': position_estimates.first_page_cpc_micros if position_estimates.first_page_cpc_micros else None,
                    'first_position_cpc_micros': position_estimates.first_position_cpc_micros if position_estimates.first_position_cpc_micros else None,
                    'top_of_page_cpc_micros': position_estimates.top_of_page_cpc_micros if position_estimates.top_of_page_cpc_micros else None,
                    'approval_status': criterion.approval_status.name if criterion.approval_status else None,
                    'system_serving_status': criterion.system_serving_status.name if criterion.system_serving_status else None,
                    'is_negative': criterion.negative,
                    'bid_modifier': criterion.bid_modifier if criterion.bid_modifier else None
                }
                keywords.append(keyword_data)

                # Insert into database
                self.cursor.execute("""
                    INSERT OR REPLACE INTO keywords VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                    )
                """, tuple(keyword_data.values()))

                # Add performance data to campaign_keywords table
                if metrics:
                    perf_data = {
                        'campaign_id': campaign.id,
                        'keyword_id': keyword_id,
                        'customer_id': customer_id,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'clicks': metrics.clicks,
                        'impressions': metrics.impressions,
                        'cost_micros': metrics.cost_micros,
                        'conversions': metrics.conversions,
                        'conversion_value': metrics.conversions_value,
                        'ctr': metrics.ctr,
                        'conversion_rate': metrics.conversions / metrics.clicks if metrics.clicks > 0 else 0,
                        'avg_cpc_micros': metrics.average_cpc,
                        'avg_position': None,  # Not available in v21
                        'absolute_top_impression_percentage': metrics.absolute_top_impression_percentage,
                        'top_impression_percentage': metrics.top_impression_percentage,
                        'search_impression_share': metrics.search_impression_share if hasattr(metrics, 'search_impression_share') else None,
                        'search_rank_lost_impression_share': metrics.search_rank_lost_impression_share if hasattr(metrics, 'search_rank_lost_impression_share') else None
                    }

                    self.cursor.execute("""
                        INSERT INTO campaign_keywords VALUES (
                            NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                        )
                    """, tuple(perf_data.values()))

        except GoogleAdsException as ex:
            print(f"[ERROR] Keyword extraction failed: {ex.error.code().name}")

        self.conn.commit()
        return keywords

    def extract_search_terms(self, customer_id):
        """Extract search term data."""
        print(f"[INFO] Extracting search terms for customer {customer_id}...")

        query = """
            SELECT
                segments.keyword.info.text,
                segments.keyword.info.match_type,
                search_term_view.search_term,
                segments.search_term_match_type,
                ad_group.id,
                campaign.id,
                segments.date,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc
            FROM search_term_view
            WHERE segments.date DURING LAST_30_DAYS
            ORDER BY metrics.impressions DESC
            LIMIT 5000
        """

        search_terms = []
        try:
            response = self.ga_service.search(customer_id=customer_id, query=query)

            for row in response:
                search_term_view = row.search_term_view
                ad_group = row.ad_group
                campaign = row.campaign
                segments = row.segments
                metrics = row.metrics

                keyword_text = segments.keyword.info.text if hasattr(segments.keyword.info, 'text') else ''
                keyword_match = segments.keyword.info.match_type.name if hasattr(segments.keyword.info, 'match_type') else 'UNKNOWN'
                search_match = segments.search_term_match_type.name if hasattr(segments, 'search_term_match_type') else 'UNKNOWN'

                # Generate keyword_id to match keywords table
                keyword_id = f"{customer_id}_{ad_group.id}_*"  # Wildcard since we don't have criterion_id

                search_term_data = {
                    'keyword_id': keyword_id,
                    'ad_group_id': ad_group.id,
                    'campaign_id': campaign.id,
                    'customer_id': customer_id,
                    'search_term': search_term_view.search_term,
                    'keyword_text': keyword_text,
                    'match_type': keyword_match,
                    'search_term_match_type': search_match,
                    'date': segments.date,
                    'clicks': metrics.clicks,
                    'impressions': metrics.impressions,
                    'cost_micros': metrics.cost_micros,
                    'conversions': metrics.conversions,
                    'conversion_value': metrics.conversions_value,
                    'ctr': metrics.ctr,
                    'avg_cpc_micros': metrics.average_cpc
                }
                search_terms.append(search_term_data)

                # Insert into database
                self.cursor.execute("""
                    INSERT INTO search_terms VALUES (
                        NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
                    )
                """, tuple(search_term_data.values()))

        except GoogleAdsException as ex:
            print(f"[ERROR] Search term extraction failed: {ex.error.code().name}")

        self.conn.commit()
        return search_terms

    def create_ml_features(self):
        """Create denormalized ML features table."""
        print("[INFO] Creating ML features...")

        # Join campaigns and keywords data for ML training
        query = """
            INSERT INTO ml_features (
                customer_id,
                campaign_id,
                campaign_name,
                channel_type,
                bidding_strategy,
                budget_amount,
                keyword_id,
                keyword_text,
                match_type,
                quality_score,
                avg_cpc,
                ctr,
                conversion_rate,
                conversions,
                cost,
                impressions,
                clicks,
                competition_index,
                search_volume_trend
            )
            SELECT
                c.customer_id,
                c.campaign_id,
                c.campaign_name,
                c.channel_type,
                c.bidding_strategy_type,
                c.budget_amount_micros / 1000000.0 as budget_amount,
                k.keyword_id,
                k.keyword_text,
                k.match_type,
                k.quality_score,
                COALESCE(ck.avg_cpc_micros / 1000000.0, 0) as avg_cpc,
                COALESCE(ck.ctr, 0) as ctr,
                COALESCE(ck.conversion_rate, 0) as conversion_rate,
                COALESCE(ck.conversions, 0) as conversions,
                COALESCE(ck.cost_micros / 1000000.0, 0) as cost,
                COALESCE(ck.impressions, 0) as impressions,
                COALESCE(ck.clicks, 0) as clicks,
                COALESCE(ck.search_rank_lost_impression_share * 100, 50) as competition_index,
                RANDOM() * 100 as search_volume_trend  -- Placeholder for actual trend data
            FROM campaigns c
            INNER JOIN keywords k ON c.campaign_id = k.campaign_id
            LEFT JOIN campaign_keywords ck ON c.campaign_id = ck.campaign_id AND k.keyword_id = ck.keyword_id
            WHERE c.status = 'ENABLED'
        """

        self.cursor.execute(query)
        self.conn.commit()

        # Get count of ML features
        self.cursor.execute("SELECT COUNT(*) FROM ml_features")
        count = self.cursor.fetchone()[0]
        print(f"[INFO] Created {count} ML feature records")

    def export_to_csv(self):
        """Export all tables to CSV files."""
        print("[INFO] Exporting data to CSV files...")

        tables = ['campaigns', 'ad_groups', 'keywords', 'search_terms', 'campaign_keywords', 'ml_features']

        for table in tables:
            df = pd.read_sql_query(f"SELECT * FROM {table}", self.conn)
            csv_file = os.path.join(OUTPUT_DIR, f"{table}.csv")
            df.to_csv(csv_file, index=False)
            print(f"  - Exported {table} to {csv_file} ({len(df)} rows)")

    def get_client_accounts(self):
        """Get all client accounts under the manager."""
        query = """
            SELECT
                customer_client.id,
                customer_client.descriptive_name,
                customer_client.manager
            FROM customer_client
            WHERE customer_client.level <= 1
                AND customer_client.status = 'ENABLED'
        """

        client_accounts = []
        try:
            response = self.ga_service.search(customer_id=self.manager_id, query=query)

            for row in response:
                if not row.customer_client.manager:  # Only client accounts
                    client_accounts.append({
                        'id': str(row.customer_client.id),
                        'name': row.customer_client.descriptive_name
                    })
        except Exception as e:
            print(f"[ERROR] Failed to get client accounts: {e}")

        return client_accounts

    def run_etl_pipeline(self):
        """Run the complete ETL pipeline."""
        print("=" * 80)
        print("GOOGLE ADS ETL PIPELINE")
        print("=" * 80)

        # Create database schema
        self.create_database_schema()

        # Get all client accounts
        client_accounts = self.get_client_accounts()
        print(f"[INFO] Found {len(client_accounts)} client accounts")

        # Process each client account
        for account in client_accounts:
            print(f"\n[INFO] Processing: {account['name']} (ID: {account['id']})")
            print("-" * 60)

            # Extract data
            self.extract_campaigns(account['id'])
            self.extract_ad_groups(account['id'])
            self.extract_keywords(account['id'])
            self.extract_search_terms(account['id'])

        # Create ML features
        self.create_ml_features()

        # Export to CSV
        self.export_to_csv()

        # Create useful views
        self.create_analytical_views()

        print("\n" + "=" * 80)
        print("[SUCCESS] ETL Pipeline completed successfully!")
        print(f"Database: {DB_FILE}")
        print(f"CSV Files: {OUTPUT_DIR}/")
        print("=" * 80)

    def create_analytical_views(self):
        """Create analytical views for easy querying."""
        print("[INFO] Creating analytical views...")

        # Campaign Performance View
        self.cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_campaign_performance AS
            SELECT
                c.customer_id,
                c.campaign_id,
                c.campaign_name,
                c.channel_type,
                c.bidding_strategy_type,
                c.budget_amount_micros / 1000000.0 as budget,
                COUNT(DISTINCT k.keyword_id) as keyword_count,
                SUM(ck.clicks) as total_clicks,
                SUM(ck.impressions) as total_impressions,
                SUM(ck.cost_micros) / 1000000.0 as total_cost,
                SUM(ck.conversions) as total_conversions,
                AVG(ck.ctr) as avg_ctr,
                AVG(ck.conversion_rate) as avg_conversion_rate,
                SUM(ck.cost_micros) / NULLIF(SUM(ck.clicks), 0) / 1000000.0 as avg_cpc,
                SUM(ck.cost_micros) / NULLIF(SUM(ck.conversions), 0) / 1000000.0 as cost_per_conversion
            FROM campaigns c
            LEFT JOIN keywords k ON c.campaign_id = k.campaign_id
            LEFT JOIN campaign_keywords ck ON c.campaign_id = ck.campaign_id
            GROUP BY c.customer_id, c.campaign_id, c.campaign_name, c.channel_type, c.bidding_strategy_type, c.budget_amount_micros
        """)

        # Keyword Performance View
        self.cursor.execute("""
            CREATE VIEW IF NOT EXISTS v_keyword_performance AS
            SELECT
                k.keyword_id,
                k.keyword_text,
                k.match_type,
                k.quality_score,
                c.campaign_name,
                c.channel_type,
                c.bidding_strategy_type,
                ck.clicks,
                ck.impressions,
                ck.cost_micros / 1000000.0 as cost,
                ck.conversions,
                ck.ctr,
                ck.conversion_rate,
                ck.avg_cpc_micros / 1000000.0 as avg_cpc,
                k.first_page_cpc_micros / 1000000.0 as first_page_cpc,
                k.top_of_page_cpc_micros / 1000000.0 as top_page_cpc
            FROM keywords k
            JOIN campaigns c ON k.campaign_id = c.campaign_id
            LEFT JOIN campaign_keywords ck ON k.keyword_id = ck.keyword_id
            WHERE k.status = 'ENABLED'
        """)

        self.conn.commit()
        print("[INFO] Analytical views created")

    def close(self):
        """Close database connection."""
        self.conn.close()

def main():
    """Main function."""
    etl = GoogleAdsETL()
    try:
        etl.run_etl_pipeline()
    finally:
        etl.close()

if __name__ == "__main__":
    main()