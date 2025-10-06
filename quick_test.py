#!/usr/bin/env python3
"""
Quick test to verify system readiness for multi-agent development
"""

print("\n" + "="*60)
print("MARKETINGIQ SYSTEM STATUS CHECK")
print("="*60)

# Check 1: Python Dependencies
print("\n1. CHECKING PYTHON DEPENDENCIES...")
try:
    import pyodbc
    import sqlalchemy
    import pandas
    import fastapi
    import uvicorn
    from google.ads.googleads.client import GoogleAdsClient
    from loguru import logger
    from dotenv import load_dotenv
    print("   [OK] All required packages installed")
    deps_ok = True
except ImportError as e:
    print(f"   [FAIL] Missing package: {e}")
    deps_ok = False

# Check 2: Configuration Files
print("\n2. CHECKING CONFIGURATION FILES...")
import os
from pathlib import Path

files_ok = True
required_files = [
    '.env',
    'google-ads.yaml',
    'docker-compose.yml',
    'db_connection.py',
    'etl_pipeline_sqlserver.py',
    'api_sqlserver.py'
]

for file in required_files:
    if Path(file).exists():
        print(f"   [OK] {file}")
    else:
        print(f"   [FAIL] {file} NOT FOUND")
        files_ok = False

# Check 3: Google Ads Config
print("\n3. CHECKING GOOGLE ADS CONFIGURATION...")
try:
    import yaml
    with open('google-ads.yaml', 'r') as f:
        config = yaml.safe_load(f)

    if config.get('developer_token') and config.get('client_id'):
        print("   [OK] Google Ads API configured")
        google_ok = True
    else:
        print("   [FAIL] Google Ads API missing configuration")
        google_ok = False
except Exception as e:
    print(f"   [FAIL] Error: {e}")
    google_ok = False

# Check 4: Docker Status
print("\n4. CHECKING DOCKER...")
import subprocess
try:
    result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   [OK] Docker installed: {result.stdout.strip()}")
        docker_installed = True
    else:
        print("   [FAIL] Docker not available")
        docker_installed = False
except Exception as e:
    print(f"   [FAIL] Docker check failed: {e}")
    docker_installed = False

# Check 5: Database Connection (if Docker is running)
print("\n5. CHECKING DATABASE CONNECTION...")
if docker_installed:
    try:
        from db_connection import db
        if db.test_connection():
            print("   [OK] Database connection successful")
            db_ok = True
        else:
            print("   [WARN]  Database not accessible (start Docker container)")
            db_ok = False
    except Exception as e:
        print(f"   [WARN]  Database check failed: {e}")
        db_ok = False
else:
    print("   [SKIP]  Skipped (Docker not running)")
    db_ok = False

# Final Report
print("\n" + "="*60)
print("SUMMARY")
print("="*60)

status = {
    "Python Dependencies": deps_ok,
    "Configuration Files": files_ok,
    "Google Ads API": google_ok,
    "Docker": docker_installed,
    "Database": db_ok
}

all_ready = all(status.values())

for component, ready in status.items():
    status_icon = "[OK]" if ready else "[FAIL]"
    print(f"  {status_icon} {component}")

print("\n" + "="*60)

if all_ready:
    print("[SUCCESS] SYSTEM FULLY READY FOR MULTI-AGENT DEVELOPMENT!")
    print("\nYou can now proceed with building your multi-agent system.")
    print("\nNext steps:")
    print("1. Run ETL: python etl_pipeline_sqlserver.py")
    print("2. Start API: python api_sqlserver.py")
    print("3. Access API: http://localhost:8000/docs")
elif deps_ok and files_ok and google_ok:
    print("[OK] SYSTEM PARTIALLY READY - Can proceed with development!")
    print("\n[WARN]  Note: Docker/Database not running but all code is ready.")
    print("\nTo complete setup:")
    print("1. Ensure Docker Desktop is running")
    print("2. Run: docker-compose up -d")
    print("3. Wait 30 seconds for SQL Server to start")
    print("4. Run: python test_connection.py")
    print("\nYou can still:")
    print("- Develop multi-agent logic")
    print("- Build ML models")
    print("- Design agent architectures")
    print("- Write unit tests")
else:
    print("[FAIL] SYSTEM NOT READY - Fixes needed before proceeding")
    print("\nRequired actions:")
    if not deps_ok:
        print("- Install packages: pip install -r requirements.txt")
    if not files_ok:
        print("- Ensure all configuration files are present")
    if not google_ok:
        print("- Configure Google Ads API credentials")

print("="*60)