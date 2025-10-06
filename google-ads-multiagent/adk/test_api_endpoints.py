"""
Test API endpoints to ensure they're accessible
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

def test_endpoints():
    """Test all API endpoints used by the agents"""

    endpoints = [
        # Working endpoints from api_sqlserver.py
        ("/", "GET", "Root endpoint"),
        ("/health", "GET", "Health check"),
        ("/campaigns", "GET", "Get campaigns"),
        ("/metrics/summary", "GET", "Metrics summary"),
        ("/metrics/trends", "GET", "Metrics trends"),
        ("/metrics/by-day-of-week", "GET", "Metrics by day"),
        ("/campaigns/top-performers", "GET", "Top performers"),
        ("/keywords/underperformers", "GET", "Underperforming keywords"),
        ("/search-terms", "GET", "Search terms"),
        ("/search-terms/negative", "GET", "Negative keywords"),
        ("/ad-groups", "GET", "Ad groups"),
        ("/keywords", "GET", "Keywords"),
    ]

    print("Testing API Endpoints")
    print("=" * 60)
    print(f"API Base: {API_BASE}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []
    for endpoint, method, description in endpoints:
        url = f"{API_BASE}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json={}, timeout=5)

            status = response.status_code
            if status == 200:
                result = "OK OK"
                # Try to get data length
                try:
                    data = response.json()
                    if isinstance(data, list):
                        result += f" ({len(data)} items)"
                    elif isinstance(data, dict):
                        if 'campaigns' in data:
                            result += f" ({len(data['campaigns'])} campaigns)"
                        elif 'error' not in data:
                            result += " (data returned)"
                except:
                    pass
            elif status == 404:
                result = "FAIL NOT FOUND"
            else:
                result = f"WARN Status: {status}"

            results.append((endpoint, result))
            print(f"{method:4} {endpoint:30} {result:20} {description}")

        except requests.exceptions.RequestException as e:
            result = f"FAIL ERROR: {str(e)[:30]}"
            results.append((endpoint, result))
            print(f"{method:4} {endpoint:30} {result:20} {description}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("-" * 60)

    working = sum(1 for _, r in results if "OK" in r)
    not_found = sum(1 for _, r in results if "NOT FOUND" in r)
    errors = sum(1 for _, r in results if "ERROR" in r)

    print(f"Working endpoints: {working}/{len(endpoints)}")
    print(f"Not found: {not_found}")
    print(f"Errors: {errors}")

    if not_found > 0:
        print("\nEndpoints not found:")
        for endpoint, result in results:
            if "NOT FOUND" in result:
                print(f"  - {endpoint}")

    return working > 0

if __name__ == "__main__":
    import sys

    # First check if API is running
    try:
        response = requests.get(f"{API_BASE}/health", timeout=2)
        if response.status_code == 200:
            print("API server is running\n")
        else:
            print(f"API server returned status {response.status_code}")
    except:
        print("ERROR: API server is not running on port 8000")
        print("Please start the API server first:")
        print("  cd ../..")
        print("  python api_sqlserver.py")
        sys.exit(1)

    # Test endpoints
    success = test_endpoints()

    if success:
        print("\nAPI is ready for ADK agents!")
    else:
        print("\nWARNING: Some endpoints are not working")
        print("The agents may not function correctly")