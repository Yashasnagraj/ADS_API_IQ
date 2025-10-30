#!/usr/bin/env python3
"""
Shopify Setup Script
One-time setup to connect your Shopify store
"""
import os
import sys
from loguru import logger
from dotenv import load_dotenv
from shopify_etl import ShopifyETL

# Load Shopify credentials from .env.shopify
load_dotenv('.env.shopify')

def setup_shopify_store():
    """Connect a Shopify store to the system"""

    # Get credentials from environment
    shop_domain = os.getenv('SHOPIFY_SHOP_DOMAIN')
    access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    customer_id = int(os.getenv('CUSTOMER_ID', 1))

    if not shop_domain or not access_token:
        logger.error("Missing Shopify credentials!")
        logger.info("Please create .env.shopify file with:")
        logger.info("  SHOPIFY_SHOP_DOMAIN=your-store.myshopify.com")
        logger.info("  SHOPIFY_ACCESS_TOKEN=shpat_xxxxx")
        logger.info("  CUSTOMER_ID=1")
        sys.exit(1)

    logger.info("="*70)
    logger.info("SHOPIFY STORE SETUP")
    logger.info("="*70)
    logger.info(f"Shop Domain: {shop_domain}")
    logger.info(f"Customer ID: {customer_id}")
    logger.info("")

    # Initialize ETL
    etl = ShopifyETL()

    try:
        # Add store
        store_id = etl.add_shopify_store(
            customer_id=customer_id,
            shop_domain=shop_domain,
            access_token=access_token,
            shop_name=shop_domain.split('.')[0].replace('-', ' ').title(),
            currency='USD'
        )

        logger.success(f"✅ Shopify store connected successfully!")
        logger.success(f"   Store ID: {store_id}")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Run ETL: python shopify_etl.py")
        logger.info("  2. Start API: cd api && uvicorn app.main:app --reload")
        logger.info("  3. Test: curl http://localhost:8000/api/v1/shopify/integration/status?customer_id=1")

        return store_id

    except Exception as e:
        logger.error(f"❌ Failed to connect Shopify store: {e}")
        sys.exit(1)
    finally:
        etl.conn.close()


if __name__ == "__main__":
    setup_shopify_store()
