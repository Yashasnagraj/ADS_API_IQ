#!/usr/bin/env python3
"""
End-to-End System Check for MarketingIQ
Verifies all components are ready for multi-agent system development
"""

import sys
import os
import subprocess
from pathlib import Path
import importlib.util
from datetime import datetime

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def check_status(condition, success_msg, fail_msg):
    if condition:
        print(f"{GREEN}[OK] {success_msg}{RESET}")
        return True
    else:
        print(f"{RED}[FAIL] {fail_msg}{RESET}")
        return False

def check_python_dependencies():
    """Check if all required Python packages are installed"""
    print_header("1. PYTHON DEPENDENCIES CHECK")

    required_packages = [
        'pyodbc',
        'sqlalchemy',
        'pandas',
        'fastapi',
        'uvicorn',
        'google.ads.googleads',
        'dotenv',
        'loguru'
    ]

    all_installed = True
    for package in required_packages:
        try:
            if '.' in package:
                parts = package.split('.')
                importlib.import_module(parts[0])
            else:
                importlib.import_module(package)
            check_status(True, f"{package} installed", "")
        except ImportError:
            check_status(False, "", f"{package} NOT installed")
            all_installed = False

    return all_installed

def check_configuration_files():
    """Check if all configuration files exist"""
    print_header("2. CONFIGURATION FILES CHECK")

    files_to_check = [
        ('.env', 'Environment variables'),
        ('google-ads.yaml', 'Google Ads credentials'),
        ('docker-compose.yml', 'Docker Compose configuration'),
        ('db_connection.py', 'Database connection module'),
        ('etl_pipeline_sqlserver.py', 'ETL pipeline'),
        ('api_sqlserver.py', 'REST API')
    ]

    all_exist = True
    for file, description in files_to_check:
        exists = Path(file).exists()
        check_status(exists, f"{description} ({file})", f"{description} ({file}) NOT FOUND")
        if not exists:
            all_exist = False

    return all_exist

def check_docker_status():
    """Check Docker status"""
    print_header("3. DOCKER STATUS CHECK")

    try:
        # Check if Docker is running
        result = subprocess.run(['docker', 'version'], capture_output=True, text=True)
        docker_running = result.returncode == 0
        check_status(docker_running, "Docker is installed and running", "Docker is not running")

        if docker_running:
            # Check for SQL Server container
            result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=marketing_sqlserver', '--format', '{{.Status}}'],
                                  capture_output=True, text=True)
            container_status = result.stdout.strip()

            if 'Up' in container_status:
                check_status(True, f"SQL Server container is running ({container_status})", "")
                return True
            elif container_status:
                check_status(False, "", f"SQL Server container exists but not running ({container_status})")
                print(f"{YELLOW}  → Run: docker-compose up -d{RESET}")
                return False
            else:
                check_status(False, "", "SQL Server container not found")
                print(f"{YELLOW}  → Run: docker-compose up -d{RESET}")
                return False
    except Exception as e:
        check_status(False, "", f"Docker check failed: {e}")
        return False

def check_database_connection():
    """Check database connection and schema"""
    print_header("4. DATABASE CONNECTION CHECK")

    try:
        from db_connection import db

        # Test connection
        connected = db.test_connection()
        check_status(connected, "Database connection successful", "Database connection failed")

        if connected:
            # Check schema
            result = db.execute_query("SELECT COUNT(*) FROM sys.schemas WHERE name = 'dw'")
            schema_exists = result and result[0][0] > 0
            check_status(schema_exists, "Schema 'dw' exists", "Schema 'dw' not found")

            # Check tables
            tables = db.execute_query("""
                SELECT COUNT(*) as table_count
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'dw'
            """)
            table_count = tables[0][0] if tables else 0
            check_status(table_count > 0, f"Found {table_count} tables in schema", "No tables found")

            # Check Date dimension
            dates = db.execute_query("SELECT COUNT(*) FROM dw.DimDate")
            date_count = dates[0][0] if dates else 0
            check_status(date_count > 0, f"Date dimension populated ({date_count} rows)", "Date dimension empty")

            return connected and schema_exists and table_count > 0
    except ImportError:
        check_status(False, "", "Cannot import db_connection module")
        return False
    except Exception as e:
        check_status(False, "", f"Database check failed: {e}")
        return False

def check_google_ads_config():
    """Check Google Ads configuration"""
    print_header("5. GOOGLE ADS API CHECK")

    try:
        import yaml

        if Path('google-ads.yaml').exists():
            with open('google-ads.yaml', 'r') as f:
                config = yaml.safe_load(f)

            has_token = bool(config.get('developer_token'))
            has_client = bool(config.get('client_id'))
            has_refresh = bool(config.get('refresh_token'))
            has_customer = bool(config.get('login_customer_id'))

            check_status(has_token, "Developer token configured", "Developer token missing")
            check_status(has_client, "Client ID configured", "Client ID missing")
            check_status(has_refresh, "Refresh token configured", "Refresh token missing")
            check_status(has_customer, "Customer ID configured", "Customer ID missing")

            return all([has_token, has_client, has_refresh, has_customer])
        else:
            check_status(False, "", "google-ads.yaml not found")
            return False
    except Exception as e:
        check_status(False, "", f"Google Ads config check failed: {e}")
        return False

def check_api_readiness():
    """Check if API can be started"""
    print_header("6. API READINESS CHECK")

    try:
        # Check if FastAPI can be imported
        import fastapi
        import uvicorn
        check_status(True, "FastAPI and Uvicorn available", "")

        # Check if API file exists
        api_exists = Path('api_sqlserver.py').exists()
        check_status(api_exists, "API file exists (api_sqlserver.py)", "API file not found")

        return api_exists
    except ImportError as e:
        check_status(False, "", f"FastAPI dependencies missing: {e}")
        return False

def generate_report(results):
    """Generate final report"""
    print_header("SYSTEM READINESS REPORT")

    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)

    print(f"\nChecks passed: {passed_checks}/{total_checks}")

    if passed_checks == total_checks:
        print(f"\n{GREEN}[SUCCESS] SYSTEM READY FOR MULTI-AGENT DEVELOPMENT!{RESET}")
        print("\nNext steps:")
        print("1. Start Docker: docker-compose up -d")
        print("2. Initialize schema: python test_connection.py")
        print("3. Run ETL: python etl_pipeline_sqlserver.py")
        print("4. Start API: python api_sqlserver.py")
        print("5. Access API docs: http://localhost:8000/docs")
        return True
    else:
        print(f"\n{RED}[ERROR] SYSTEM NOT READY - FIXES NEEDED{RESET}")
        print("\nFailed checks:")
        for check, passed in results.items():
            if not passed:
                print(f"  - {check}")

        print("\nRecommended actions:")
        if not results.get('dependencies'):
            print("  1. Install missing packages: pip install -r requirements.txt")
        if not results.get('docker'):
            print("  2. Start Docker Desktop and run: docker-compose up -d")
        if not results.get('database'):
            print("  3. Initialize database: docker exec -it marketing_sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'Yashas#@123' -i /docker-entrypoint-initdb.d/01-create-database.sql")

        return False

def main():
    """Run all system checks"""
    print(f"\n{BLUE}MarketingIQ System Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")

    results = {
        'dependencies': check_python_dependencies(),
        'configuration': check_configuration_files(),
        'docker': check_docker_status(),
        'database': False,  # Will be updated if Docker is running
        'google_ads': check_google_ads_config(),
        'api': check_api_readiness()
    }

    # Only check database if Docker is running
    if results['docker']:
        results['database'] = check_database_connection()
    else:
        print_header("4. DATABASE CONNECTION CHECK")
        print(f"{YELLOW}[WARNING] Skipped - Docker not running{RESET}")

    # Generate final report
    system_ready = generate_report(results)

    # Return exit code
    sys.exit(0 if system_ready else 1)

if __name__ == "__main__":
    main()