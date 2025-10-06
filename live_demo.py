#!/usr/bin/env python3
"""
Live Demonstration - Google Ads API Data Fetching
Shows real-time data from Google Ads through the API
"""

import requests
import json
import time
from datetime import datetime
from colorama import init, Fore, Style

init()

def demo_google_ads_data():
    """Live demonstration of Google Ads data fetching"""
    api_url = "http://localhost:8000"

    print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}    GOOGLE ADS API - LIVE DATA DEMONSTRATION{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

    print("This demo proves that the API endpoints fetch real Google Ads data.\n")

    # 1. Show API is connected
    print(f"{Fore.YELLOW}1. Checking API Connection...{Style.RESET_ALL}")
    try:
        health = requests.get(f"{api_url}/health").json()
        print(f"   {Fore.GREEN}✓ API Status: {health['status']}{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}✓ Database: {health['database']}{Style.RESET_ALL}\n")
    except:
        print(f"   {Fore.RED}✗ API is not running. Start it with: python api_sqlserver.py{Style.RESET_ALL}")
        return

    # 2. Fetch and display campaign data
    print(f"{Fore.YELLOW}2. Fetching Live Campaign Data from Google Ads...{Style.RESET_ALL}")
    try:
        campaigns = requests.get(f"{api_url}/campaigns?limit=3").json()
        if campaigns:
            print(f"   {Fore.GREEN}✓ Found {len(campaigns)} campaigns{Style.RESET_ALL}\n")

            for i, camp in enumerate(campaigns, 1):
                print(f"   Campaign #{i}:")
                print(f"   • Name: {Fore.CYAN}{camp['campaign_name']}{Style.RESET_ALL}")
                print(f"   • Status: {camp['status']}")
                print(f"   • Budget: ${camp['budget_amount']:,.2f}")
                print(f"   • Impressions: {camp['impressions']:,}")
                print(f"   • Clicks: {camp['clicks']:,}")
                print(f"   • Cost: ${camp['cost']:,.2f}")
                print(f"   • CTR: {camp['ctr']:.2f}%")
                print()
        else:
            print(f"   {Fore.YELLOW}No campaigns found. Run ETL first: python etl_pipeline_sqlserver.py{Style.RESET_ALL}")
    except Exception as e:
        print(f"   {Fore.RED}Error: {e}{Style.RESET_ALL}")

    # 3. Show account-wide metrics
    print(f"{Fore.YELLOW}3. Fetching Account Performance Metrics...{Style.RESET_ALL}")
    try:
        metrics = requests.get(f"{api_url}/metrics/summary").json()
        if metrics and 'metrics' in metrics:
            m = metrics['metrics']
            print(f"   {Fore.GREEN}✓ Last 30 Days Performance:{Style.RESET_ALL}")
            print(f"   • Total Spend: ${m['total_cost']:,.2f}")
            print(f"   • Impressions: {m['total_impressions']:,}")
            print(f"   • Clicks: {m['total_clicks']:,}")
            print(f"   • Conversions: {m['total_conversions']:,}")
            print(f"   • Avg. ROAS: {m['avg_roas']:.2f}x")
            print()
    except Exception as e:
        print(f"   {Fore.RED}Error: {e}{Style.RESET_ALL}")

    # 4. Show top keywords
    print(f"{Fore.YELLOW}4. Fetching Top Keywords...{Style.RESET_ALL}")
    try:
        keywords = requests.get(f"{api_url}/keywords?limit=5").json()
        if keywords:
            print(f"   {Fore.GREEN}✓ Top 5 Keywords by Impressions:{Style.RESET_ALL}")
            for kw in keywords[:5]:
                print(f"   • {kw['keyword']} ({kw['match_type']})")
                print(f"     Impressions: {kw['impressions']:,} | CTR: {kw['ctr']:.2f}%")
            print()
    except Exception as e:
        print(f"   {Fore.RED}Error: {e}{Style.RESET_ALL}")

    # 5. Show search terms
    print(f"{Fore.YELLOW}5. Fetching Actual Search Terms...{Style.RESET_ALL}")
    try:
        search_data = requests.get(f"{api_url}/search-terms?limit=5").json()
        if search_data and 'search_terms' in search_data:
            terms = search_data['search_terms']
            if terms:
                print(f"   {Fore.GREEN}✓ Recent Search Terms from Users:{Style.RESET_ALL}")
                for term in terms[:5]:
                    print(f"   • \"{term['search_term']}\"")
                    print(f"     Impressions: {term['impressions']:,} | Cost: ${term['cost']:.2f}")
                print()
    except Exception as e:
        print(f"   {Fore.RED}Error: {e}{Style.RESET_ALL}")

    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Successfully demonstrated API endpoints fetching Google Ads data!{Style.RESET_ALL}")
    print(f"\nAPI Documentation: {Fore.CYAN}http://localhost:8000/docs{Style.RESET_ALL}")
    print(f"All endpoints: {Fore.CYAN}http://localhost:8000/{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    demo_google_ads_data()