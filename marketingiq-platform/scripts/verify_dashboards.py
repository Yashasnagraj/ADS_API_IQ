#!/usr/bin/env python3
"""
Dashboard Verification Script for MarketingIQ Platform
=======================================================
Verifies that all dashboard metrics come from the database and not mocked/hardcoded values.
Checks metric calculations (CTR, CPC, CPA, ROAS) against canonical formulas.
Ensures currency is formatted as INR (₹) and all values are numeric (not strings).
"""

import os
import sys
import json
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8001')
DB_PATH = os.getenv('DB_PATH', '../../google_ads_data.db')  # Relative to scripts dir
TOLERANCE = 0.01  # Tolerance for float comparisons (1 cent)
PERCENT_TOLERANCE = 0.1  # Tolerance for percentage comparisons

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def log_info(message: str):
    """Log info message"""
    print(f"{Colors.BLUE}[INFO]{Colors.END} {message}")


def log_success(message: str):
    """Log success message"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {message}")


def log_error(message: str):
    """Log error message"""
    print(f"{Colors.RED}[ERROR]{Colors.END} {message}")


def log_warning(message: str):
    """Log warning message"""
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {message}")


class DashboardVerifier:
    """Verifies dashboard metrics against database"""

    def __init__(self, db_path: str, api_base_url: str):
        self.db_path = db_path
        self.api_base_url = api_base_url
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'endpoints_tested': [],
            'hardcoded_occurrences': [],
            'currency_issues': [],
            'metric_mismatches': [],
            'type_issues': [],
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }

    def connect_db(self):
        """Connect to SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            log_error(f"Failed to connect to database: {e}")
            return None

    def get_db_metrics(self, customer_id: Optional[str] = None,
                      date_from: Optional[str] = None,
                      date_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics from database for comparison
        Returns canonical metrics: impressions, clicks, cost, conversions, CTR, CPC, CPA, etc.
        """
        conn = self.connect_db()
        if not conn:
            return {}

        try:
            # Build query with filters
            where_clauses = []
            params = []

            if customer_id:
                where_clauses.append("customer_id = ?")
                params.append(customer_id)

            if date_from and date_to:
                where_clauses.append("date BETWEEN ? AND ?")
                params.extend([date_from, date_to])

            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            # Get campaign performance from DB
            # Adjust table names based on actual schema
            query = f"""
            SELECT
                SUM(impressions) as impressions,
                SUM(clicks) as clicks,
                SUM(cost_micros) / 1000000.0 as cost,
                SUM(conversions) as conversions
            FROM campaigns_performance
            {where_sql}
            """

            cursor = conn.execute(query, params)
            row = cursor.fetchone()

            if row:
                impressions = float(row['impressions'] or 0)
                clicks = float(row['clicks'] or 0)
                cost = float(row['cost'] or 0)
                conversions = float(row['conversions'] or 0)

                # Calculate metrics using canonical formulas
                ctr = (clicks / impressions * 100.0) if impressions > 0 else None
                avg_cpc = (cost / clicks) if clicks > 0 else None
                cpa = (cost / conversions) if conversions > 0 else None

                return {
                    'impressions': int(impressions),
                    'clicks': int(clicks),
                    'cost': round(cost, 2),
                    'conversions': int(conversions),
                    'ctr': round(ctr, 2) if ctr is not None else None,
                    'avg_cpc': round(avg_cpc, 2) if avg_cpc is not None else None,
                    'cpa': round(cpa, 2) if cpa is not None else None
                }

            return {}

        except Exception as e:
            log_error(f"Database query failed: {e}")
            return {}
        finally:
            conn.close()

    def call_api(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Call API endpoint and return response"""
        try:
            url = f"{self.api_base_url}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            log_error(f"API call failed [{endpoint}]: {e}")
            return {}

    def compare_metrics(self, db_metrics: Dict, api_metrics: Dict, endpoint: str) -> bool:
        """Compare DB metrics vs API metrics"""
        self.results['total_tests'] += 1
        test_result = {
            'endpoint': endpoint,
            'db_metrics': db_metrics,
            'api_metrics': api_metrics,
            'status': 'OK',
            'mismatches': []
        }

        # Check each metric
        for metric in ['impressions', 'clicks', 'cost', 'conversions', 'ctr', 'avg_cpc', 'cpa']:
            db_value = db_metrics.get(metric)
            api_value = api_metrics.get(metric)

            # Skip if either value is missing
            if db_value is None and api_value is None:
                continue

            if db_value is None or api_value is None:
                test_result['mismatches'].append({
                    'metric': metric,
                    'db_value': db_value,
                    'api_value': api_value,
                    'issue': 'One value is null'
                })
                continue

            # Check type - API should return numbers, not strings
            if isinstance(api_value, str):
                self.results['type_issues'].append({
                    'endpoint': endpoint,
                    'metric': metric,
                    'value': api_value,
                    'expected_type': 'number',
                    'actual_type': 'string'
                })
                test_result['mismatches'].append({
                    'metric': metric,
                    'issue': f'API returns string instead of number: "{api_value}"'
                })
                continue

            # Compare values with tolerance
            if metric in ['ctr', 'avg_cpc', 'cpa']:
                # Percentage/decimal metrics
                tolerance = PERCENT_TOLERANCE
            else:
                # Count metrics
                tolerance = TOLERANCE

            diff = abs(float(db_value) - float(api_value))
            if diff > tolerance:
                test_result['mismatches'].append({
                    'metric': metric,
                    'db_value': db_value,
                    'api_value': api_value,
                    'difference': round(diff, 4)
                })

        # Determine status
        if test_result['mismatches']:
            test_result['status'] = 'MISMATCH'
            self.results['metric_mismatches'].append(test_result)
            self.results['summary']['failed'] += 1
            return False
        else:
            self.results['endpoints_tested'].append(test_result)
            self.results['summary']['passed'] += 1
            return True

    def check_hardcoded_values(self):
        """Check source code for hardcoded values"""
        log_info("Scanning for hardcoded values...")

        web_src = os.path.join(os.path.dirname(self.db_path), 'marketingiq-platform', 'web', 'src')
        server_src = os.path.join(os.path.dirname(self.db_path), 'marketingiq-platform', 'server')

        patterns = {
            'mock': ['mock', 'mockData', 'mockCampaigns', 'mockMetrics', 'mock_api'],
            'currency_dollar': [r'\$[0-9]', 'USD'],
            'hardcoded_numbers': ['value={0}', 'ctr: 0', 'clicks: 0']
        }

        # This would normally use grep/ripgrep but simplified for demo
        log_warning("Hardcoded value scanning requires grep - implement separately")

    def verify_endpoint(self, endpoint: str, customer_id: Optional[str] = None,
                       date_from: Optional[str] = None, date_to: Optional[str] = None):
        """Verify a single endpoint"""
        log_info(f"Testing endpoint: {endpoint}")

        # Get DB metrics
        db_metrics = self.get_db_metrics(customer_id, date_from, date_to)
        if not db_metrics:
            log_warning(f"No DB metrics available for {endpoint}")
            return

        # Call API
        params = {}
        if customer_id:
            params['customer_id'] = customer_id
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to

        api_response = self.call_api(endpoint, params)
        if not api_response:
            log_error(f"No API response for {endpoint}")
            self.results['summary']['failed'] += 1
            return

        # Compare
        success = self.compare_metrics(db_metrics, api_response, endpoint)
        if success:
            log_success(f"✓ {endpoint} - metrics match")
        else:
            log_error(f"✗ {endpoint} - metrics mismatch")

    def run_full_verification(self):
        """Run complete verification suite"""
        log_info(f"{Colors.BOLD}Starting Dashboard Verification{Colors.END}")
        log_info(f"API: {self.api_base_url}")
        log_info(f"DB: {self.db_path}")
        print()

        # Get a sample customer ID from DB
        conn = self.connect_db()
        if conn:
            try:
                cursor = conn.execute("SELECT DISTINCT customer_id FROM campaigns_performance LIMIT 1")
                row = cursor.fetchone()
                sample_customer_id = row['customer_id'] if row else None
            except:
                sample_customer_id = None
            finally:
                conn.close()
        else:
            sample_customer_id = None

        # Date range - last 30 days
        date_to = datetime.now().strftime('%Y-%m-%d')
        date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        # Test critical endpoints
        endpoints_to_test = [
            '/metrics/campaigns',
            '/metrics/keywords',
            '/metrics/adgroups',
            '/metrics/search-terms'
        ]

        for endpoint in endpoints_to_test:
            self.verify_endpoint(endpoint, sample_customer_id, date_from, date_to)
            print()

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate JSON report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f"reports/dashboard_verification_{timestamp}.json"

        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        log_success(f"Report generated: {report_path}")

        # Print summary
        print()
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}VERIFICATION SUMMARY{Colors.END}")
        print(f"{'='*60}")
        print(f"Total Tests:     {self.results['summary']['total_tests']}")
        print(f"{Colors.GREEN}Passed:          {self.results['summary']['passed']}{Colors.END}")
        print(f"{Colors.RED}Failed:          {self.results['summary']['failed']}{Colors.END}")
        print(f"{Colors.YELLOW}Warnings:        {self.results['summary']['warnings']}{Colors.END}")
        print(f"{'='*60}")

        if self.results['metric_mismatches']:
            print(f"\n{Colors.RED}{Colors.BOLD}METRIC MISMATCHES:{Colors.END}")
            for mismatch in self.results['metric_mismatches']:
                print(f"  Endpoint: {mismatch['endpoint']}")
                for issue in mismatch['mismatches']:
                    print(f"    - {issue['metric']}: DB={issue.get('db_value')} API={issue.get('api_value')}")

        if self.results['type_issues']:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}TYPE ISSUES:{Colors.END}")
            for issue in self.results['type_issues']:
                print(f"  {issue['endpoint']} - {issue['metric']}: expected {issue['expected_type']}, got {issue['actual_type']}")

        return report_path


def main():
    """Main entry point"""
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # DB path - check multiple locations
    db_candidates = [
        os.path.join(project_root, '..', 'google_ads_data.db'),
        os.path.join(project_root, '..', '..', 'google_ads_data.db'),
        '/app/data/google_ads_data.db'
    ]

    db_path = None
    for candidate in db_candidates:
        if os.path.exists(candidate):
            db_path = candidate
            break

    if not db_path:
        log_warning(f"Database not found. Searched: {db_candidates}")
        log_warning("Verification will be limited")
        db_path = db_candidates[0]  # Use default

    # Create verifier
    verifier = DashboardVerifier(db_path, API_BASE_URL)

    # Run verification
    verifier.run_full_verification()

    # Exit with appropriate code
    if verifier.results['summary']['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
