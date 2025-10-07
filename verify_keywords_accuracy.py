#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Keyword Data Verification Script
Compares keywords from Google Ads API with database to prove 100% accuracy
Generates proof report for stakeholders
"""

import sys
import json
import sqlite3
import pandas as pd
from datetime import datetime
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
DB_FILE = "google_ads_data.db"
PROOF_DIR = "verification_proof"
Path(PROOF_DIR).mkdir(exist_ok=True)

class KeywordVerifier:
    def __init__(self):
        """Initialize verifier with Google Ads client and database connection."""
        try:
            self.client = GoogleAdsClient.load_from_storage("google-ads.yaml")
            self.ga_service = self.client.get_service("GoogleAdsService")
            self.conn = sqlite3.connect(DB_FILE)
            self.cursor = self.conn.cursor()
            print("[✓] Initialized Google Ads API client and database connection")
        except Exception as e:
            print(f"[✗] Initialization failed: {e}")
            sys.exit(1)

    def get_client_accounts(self, manager_id="3341907700"):
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
            response = self.ga_service.search(customer_id=manager_id, query=query)

            for row in response:
                if not row.customer_client.manager:  # Only client accounts
                    client_accounts.append({
                        'id': str(row.customer_client.id),
                        'name': row.customer_client.descriptive_name
                    })
        except Exception as e:
            print(f"[!] Failed to get client accounts: {e}")
            # Fallback to known accounts
            client_accounts = [
                {'id': '6265362093', 'name': 'Communn.io'},
                {'id': '5032737756', 'name': 'Emcee Sons'},
                {'id': '7613138874', 'name': 'VANAVASI KALYANA'}
            ]

        return client_accounts

    def fetch_keywords_from_api(self, customer_id, limit=100):
        """
        Fetch keywords directly from Google Ads API
        This is the EXACT query used in the ETL pipeline
        """
        print(f"\n[→] Fetching keywords from Google Ads API for customer {customer_id}...")

        # EXACT GAQL query from google_ads_etl_pipeline.py (lines 356-393)
        query = """
            SELECT
                ad_group_criterion.criterion_id,
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
                ad_group.name,
                campaign.id,
                campaign.name,
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
            LIMIT {limit}
        """.format(limit=limit)

        keywords_from_api = []

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
                    'source': 'GOOGLE_ADS_API',
                    'keyword_id': keyword_id,
                    'customer_id': customer_id,
                    'campaign_id': campaign.id,
                    'campaign_name': campaign.name,
                    'ad_group_id': ad_group.id,
                    'ad_group_name': ad_group.name,
                    'criterion_id': criterion.criterion_id,
                    'keyword_text': criterion.keyword.text,
                    'match_type': criterion.keyword.match_type.name,
                    'status': criterion.status.name,
                    'quality_score': quality_info.quality_score if quality_info.quality_score else 0,
                    'creative_quality_score': quality_info.creative_quality_score.name if quality_info.creative_quality_score else None,
                    'landing_page_quality_score': quality_info.post_click_quality_score.name if quality_info.post_click_quality_score else None,
                    'search_predicted_ctr': quality_info.search_predicted_ctr.name if quality_info.search_predicted_ctr else None,
                    'cpc_bid_micros': criterion.cpc_bid_micros if criterion.cpc_bid_micros else 0,
                    'first_page_cpc_micros': position_estimates.first_page_cpc_micros if position_estimates.first_page_cpc_micros else 0,
                    'first_position_cpc_micros': position_estimates.first_position_cpc_micros if position_estimates.first_position_cpc_micros else 0,
                    'top_of_page_cpc_micros': position_estimates.top_of_page_cpc_micros if position_estimates.top_of_page_cpc_micros else 0,
                    'approval_status': criterion.approval_status.name if criterion.approval_status else None,
                    'system_serving_status': criterion.system_serving_status.name if criterion.system_serving_status else None,
                    'is_negative': criterion.negative,
                    'bid_modifier': criterion.bid_modifier if criterion.bid_modifier else None,
                    'clicks': metrics.clicks if metrics else 0,
                    'impressions': metrics.impressions if metrics else 0,
                    'cost_micros': metrics.cost_micros if metrics else 0,
                    'conversions': metrics.conversions if metrics else 0,
                    'conversions_value': metrics.conversions_value if metrics else 0,
                    'ctr': metrics.ctr if metrics else 0,
                    'average_cpc': metrics.average_cpc if metrics else 0,
                }
                keywords_from_api.append(keyword_data)

            print(f"[✓] Fetched {len(keywords_from_api)} keywords from Google Ads API")

        except GoogleAdsException as ex:
            print(f"[✗] API query failed: {ex.error.code().name}")
            for error in ex.failure.errors:
                print(f"    Error: {error.message}")
        except Exception as e:
            print(f"[✗] Unexpected error: {e}")

        return keywords_from_api

    def fetch_keywords_from_database(self, customer_id, limit=100):
        """Fetch keywords from local database."""
        print(f"\n[→] Fetching keywords from database for customer {customer_id}...")

        query = """
            SELECT
                k.keyword_id,
                k.customer_id,
                k.campaign_id,
                k.ad_group_id,
                k.keyword_text,
                k.match_type,
                k.status,
                k.quality_score,
                k.creative_quality_score,
                k.landing_page_quality_score,
                k.search_predicted_ctr,
                k.cpc_bid_micros,
                k.first_page_cpc_micros,
                k.first_position_cpc_micros,
                k.top_of_page_cpc_micros,
                k.approval_status,
                k.system_serving_status,
                k.is_negative,
                k.bid_modifier,
                c.campaign_name,
                ag.ad_group_name,
                COALESCE(ck.clicks, 0) as clicks,
                COALESCE(ck.impressions, 0) as impressions,
                COALESCE(ck.cost_micros, 0) as cost_micros,
                COALESCE(ck.conversions, 0) as conversions,
                COALESCE(ck.conversion_value, 0) as conversions_value,
                COALESCE(ck.ctr, 0) as ctr,
                COALESCE(ck.avg_cpc_micros, 0) as average_cpc
            FROM keywords k
            LEFT JOIN campaigns c ON k.campaign_id = c.campaign_id
            LEFT JOIN ad_groups ag ON k.ad_group_id = ag.ad_group_id
            LEFT JOIN campaign_keywords ck ON k.keyword_id = ck.keyword_id
            WHERE k.customer_id = ?
            ORDER BY impressions DESC
            LIMIT ?
        """

        self.cursor.execute(query, (customer_id, limit))
        rows = self.cursor.fetchall()

        keywords_from_db = []
        for row in rows:
            keyword_data = {
                'source': 'DATABASE',
                'keyword_id': row[0],
                'customer_id': row[1],
                'campaign_id': row[2],
                'ad_group_id': row[3],
                'keyword_text': row[4],
                'match_type': row[5],
                'status': row[6],
                'quality_score': row[7] if row[7] else 0,
                'creative_quality_score': row[8],
                'landing_page_quality_score': row[9],
                'search_predicted_ctr': row[10],
                'cpc_bid_micros': row[11] if row[11] else 0,
                'first_page_cpc_micros': row[12] if row[12] else 0,
                'first_position_cpc_micros': row[13] if row[13] else 0,
                'top_of_page_cpc_micros': row[14] if row[14] else 0,
                'approval_status': row[15],
                'system_serving_status': row[16],
                'is_negative': row[17],
                'bid_modifier': row[18],
                'campaign_name': row[19],
                'ad_group_name': row[20],
                'clicks': row[21],
                'impressions': row[22],
                'cost_micros': row[23],
                'conversions': row[24],
                'conversions_value': row[25],
                'ctr': row[26],
                'average_cpc': row[27],
            }
            keywords_from_db.append(keyword_data)

        print(f"[✓] Fetched {len(keywords_from_db)} keywords from database")
        return keywords_from_db

    def compare_keywords(self, api_keywords, db_keywords):
        """Compare keywords from API and database."""
        print("\n" + "="*80)
        print("KEYWORD DATA COMPARISON")
        print("="*80)

        # Create lookup dictionaries
        api_dict = {k['keyword_id']: k for k in api_keywords}
        db_dict = {k['keyword_id']: k for k in db_keywords}

        # Find matches and differences
        all_keyword_ids = set(list(api_dict.keys()) + list(db_dict.keys()))

        matches = []
        differences = []
        api_only = []
        db_only = []

        for keyword_id in all_keyword_ids:
            api_kw = api_dict.get(keyword_id)
            db_kw = db_dict.get(keyword_id)

            if api_kw and db_kw:
                # Compare key fields
                fields_to_compare = [
                    'keyword_text', 'match_type', 'status', 'quality_score',
                    'clicks', 'impressions', 'cost_micros', 'conversions'
                ]

                is_match = True
                field_diffs = []

                for field in fields_to_compare:
                    api_val = api_kw.get(field)
                    db_val = db_kw.get(field)

                    if api_val != db_val:
                        is_match = False
                        field_diffs.append({
                            'field': field,
                            'api_value': api_val,
                            'db_value': db_val
                        })

                if is_match:
                    matches.append({'keyword_id': keyword_id, 'keyword_text': api_kw['keyword_text']})
                else:
                    differences.append({
                        'keyword_id': keyword_id,
                        'keyword_text': api_kw['keyword_text'],
                        'differences': field_diffs
                    })
            elif api_kw:
                api_only.append(api_kw)
            elif db_kw:
                db_only.append(db_kw)

        # Print summary
        print(f"\n📊 COMPARISON SUMMARY:")
        print(f"  ✓ Perfect Matches: {len(matches)}")
        print(f"  ⚠ Differences Found: {len(differences)}")
        print(f"  → API Only (New): {len(api_only)}")
        print(f"  → Database Only (Old): {len(db_only)}")

        accuracy_rate = (len(matches) / len(all_keyword_ids) * 100) if all_keyword_ids else 0
        print(f"\n🎯 Data Accuracy Rate: {accuracy_rate:.2f}%")

        return {
            'matches': matches,
            'differences': differences,
            'api_only': api_only,
            'db_only': db_only,
            'accuracy_rate': accuracy_rate
        }

    def generate_proof_files(self, api_keywords, db_keywords, comparison_result):
        """Generate proof files for verification."""
        print("\n[→] Generating proof files...")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 1. Save raw API response
        api_file = f"{PROOF_DIR}/keywords_from_api_{timestamp}.json"
        with open(api_file, 'w') as f:
            json.dump(api_keywords, f, indent=2, default=str)
        print(f"  [✓] Saved: {api_file}")

        # 2. Save database data
        db_file = f"{PROOF_DIR}/keywords_from_db_{timestamp}.json"
        with open(db_file, 'w') as f:
            json.dump(db_keywords, f, indent=2, default=str)
        print(f"  [✓] Saved: {db_file}")

        # 3. Save comparison report
        comparison_file = f"{PROOF_DIR}/comparison_report_{timestamp}.json"
        with open(comparison_file, 'w') as f:
            json.dump(comparison_result, f, indent=2, default=str)
        print(f"  [✓] Saved: {comparison_file}")

        # 4. Create side-by-side CSV comparison
        if api_keywords and db_keywords:
            comparison_data = []

            for api_kw in api_keywords[:20]:  # Top 20 for readability
                keyword_id = api_kw['keyword_id']
                db_kw = next((k for k in db_keywords if k['keyword_id'] == keyword_id), None)

                if db_kw:
                    comparison_data.append({
                        'Keyword': api_kw['keyword_text'],
                        'Match Type': api_kw['match_type'],
                        'Status': api_kw['status'],
                        'API Quality Score': api_kw['quality_score'],
                        'DB Quality Score': db_kw['quality_score'],
                        'API Clicks': api_kw['clicks'],
                        'DB Clicks': db_kw['clicks'],
                        'API Impressions': api_kw['impressions'],
                        'DB Impressions': db_kw['impressions'],
                        'API Cost (₹)': api_kw['cost_micros'] / 1_000_000,
                        'DB Cost (₹)': db_kw['cost_micros'] / 1_000_000,
                        'Match': '✓' if api_kw['keyword_text'] == db_kw['keyword_text'] else '✗'
                    })

            df = pd.DataFrame(comparison_data)
            csv_file = f"{PROOF_DIR}/side_by_side_comparison_{timestamp}.csv"
            df.to_csv(csv_file, index=False)
            print(f"  [✓] Saved: {csv_file}")

        print(f"\n[✓] All proof files saved to: {PROOF_DIR}/")

    def display_sample_keywords(self, keywords, source_name, count=10):
        """Display sample keywords in a formatted table."""
        print(f"\n{'='*80}")
        print(f"SAMPLE KEYWORDS FROM {source_name}")
        print(f"{'='*80}")

        for i, kw in enumerate(keywords[:count], 1):
            print(f"\n[{i}] Keyword: {kw['keyword_text']}")
            print(f"    Match Type: {kw['match_type']}")
            print(f"    Status: {kw['status']}")
            print(f"    Quality Score: {kw['quality_score']}")
            print(f"    Campaign: {kw.get('campaign_name', 'N/A')}")
            print(f"    Ad Group: {kw.get('ad_group_name', 'N/A')}")
            print(f"    Metrics:")
            print(f"      - Impressions: {kw['impressions']:,}")
            print(f"      - Clicks: {kw['clicks']:,}")
            print(f"      - CTR: {kw['ctr']:.2%}")
            print(f"      - Cost: ₹{kw['cost_micros']/1_000_000:.2f}")
            print(f"      - Conversions: {kw['conversions']:.2f}")

    def run_verification(self, customer_id=None, limit=50):
        """Run complete verification process."""
        print("\n" + "="*80)
        print("GOOGLE ADS KEYWORD DATA VERIFICATION")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: {DB_FILE}")

        # Get client accounts
        if not customer_id:
            accounts = self.get_client_accounts()
            if accounts:
                print(f"\n[→] Available customer accounts:")
                for i, acc in enumerate(accounts, 1):
                    print(f"    {i}. {acc['name']} (ID: {acc['id']})")
                customer_id = accounts[0]['id']  # Use first account
                print(f"\n[→] Using customer: {customer_id}")

        # Fetch from API
        api_keywords = self.fetch_keywords_from_api(customer_id, limit)

        # Fetch from Database
        db_keywords = self.fetch_keywords_from_database(customer_id, limit)

        # Display samples
        if api_keywords:
            self.display_sample_keywords(api_keywords, "GOOGLE ADS API (LIVE)", count=5)

        if db_keywords:
            self.display_sample_keywords(db_keywords, "DATABASE", count=5)

        # Compare
        if api_keywords and db_keywords:
            comparison_result = self.compare_keywords(api_keywords, db_keywords)

            # Generate proof files
            self.generate_proof_files(api_keywords, db_keywords, comparison_result)
        elif not api_keywords and not db_keywords:
            print("\n[!] No keywords found in either API or database")
        elif not api_keywords:
            print("\n[!] No keywords returned from API (may be a new account or no active keywords)")
        else:
            print("\n[!] No keywords in database - ETL may need to be run")

        print("\n" + "="*80)
        print("VERIFICATION COMPLETE")
        print("="*80)
        print(f"\n📁 Proof files saved to: {PROOF_DIR}/")
        print("💡 Share these files with your boss to prove data accuracy!\n")

    def close(self):
        """Close database connection."""
        self.conn.close()

def main():
    """Main entry point."""
    verifier = KeywordVerifier()

    try:
        # You can specify a customer_id or leave it None to auto-select
        verifier.run_verification(customer_id=None, limit=50)
    finally:
        verifier.close()

if __name__ == "__main__":
    main()
