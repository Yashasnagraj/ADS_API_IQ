#!/usr/bin/env python3
"""
Shopify E-commerce ETL Pipeline
Extracts order, product, customer, and cart data from Shopify stores
Links orders to Google Ads via GCLID and UTM parameters for true ROAS calculation
"""

import os
import sys
import sqlite3
import pandas as pd
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
from dotenv import load_dotenv
import requests
import warnings

warnings.filterwarnings('ignore')
load_dotenv()


class ShopifyETL:
    def __init__(self, db_path="google_ads_data.db"):
        """Initialize Shopify ETL pipeline"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)

        logger.info(f"Shopify ETL initialized - Database: {db_path}")
        self.create_shopify_tables()

    def create_shopify_tables(self):
        """Create Shopify tables in the warehouse"""
        logger.info("Creating Shopify tables...")

        cursor = self.conn.cursor()

        # shopify_stores table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopify_stores (
                store_id TEXT PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                shop_domain TEXT UNIQUE NOT NULL,
                shop_name TEXT,
                access_token TEXT NOT NULL,
                scope TEXT,
                email TEXT,
                currency TEXT DEFAULT 'USD',
                timezone TEXT,
                installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_sync_at TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)

        # shopify_orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopify_orders (
                order_id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                customer_id INTEGER NOT NULL,
                order_number TEXT,
                order_name TEXT,
                email TEXT,
                total_price REAL NOT NULL,
                subtotal_price REAL,
                total_tax REAL,
                total_discounts REAL,
                total_shipping REAL,
                currency TEXT DEFAULT 'USD',
                financial_status TEXT,
                fulfillment_status TEXT,
                gclid TEXT,
                utm_source TEXT,
                utm_medium TEXT,
                utm_campaign TEXT,
                utm_term TEXT,
                utm_content TEXT,
                landing_site TEXT,
                referring_site TEXT,
                shopify_customer_id TEXT,
                customer_first_name TEXT,
                customer_last_name TEXT,
                created_at_shopify TIMESTAMP,
                updated_at_shopify TIMESTAMP,
                processed_at TIMESTAMP,
                cancelled_at TIMESTAMP,
                closed_at TIMESTAMP,
                tags TEXT,
                note TEXT,
                line_items_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (store_id) REFERENCES shopify_stores(store_id)
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopify_orders_gclid ON shopify_orders(gclid)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopify_orders_utm ON shopify_orders(utm_source, utm_campaign)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopify_orders_customer ON shopify_orders(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopify_orders_store ON shopify_orders(store_id)")

        # shopify_products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopify_products (
                product_id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                customer_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                body_html TEXT,
                vendor TEXT,
                product_type TEXT,
                handle TEXT,
                variants_count INTEGER,
                inventory_quantity INTEGER,
                inventory_policy TEXT,
                price REAL,
                compare_at_price REAL,
                status TEXT,
                published_at TIMESTAMP,
                tags TEXT,
                meta_description TEXT,
                image_url TEXT,
                images_count INTEGER,
                created_at_shopify TIMESTAMP,
                updated_at_shopify TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (store_id) REFERENCES shopify_stores(store_id)
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopify_products_type ON shopify_products(product_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopify_products_status ON shopify_products(status)")

        # shopify_customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopify_customers (
                shopify_customer_id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                customer_id INTEGER NOT NULL,
                email TEXT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                accepts_marketing BOOLEAN,
                marketing_opt_in_level TEXT,
                total_spent REAL DEFAULT 0.0,
                orders_count INTEGER DEFAULT 0,
                average_order_value REAL,
                first_order_gclid TEXT,
                first_order_utm_source TEXT,
                first_order_utm_campaign TEXT,
                state TEXT,
                verified_email BOOLEAN,
                city TEXT,
                province TEXT,
                country TEXT,
                created_at_shopify TIMESTAMP,
                updated_at_shopify TIMESTAMP,
                last_order_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (store_id) REFERENCES shopify_stores(store_id)
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopify_customers_email ON shopify_customers(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopify_customers_gclid ON shopify_customers(first_order_gclid)")

        # shopify_cart_events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopify_cart_events (
                event_id TEXT PRIMARY KEY,
                store_id TEXT NOT NULL,
                customer_id INTEGER NOT NULL,
                cart_token TEXT,
                checkout_token TEXT,
                customer_email TEXT,
                event_type TEXT NOT NULL,
                total_price REAL,
                currency TEXT DEFAULT 'USD',
                line_items_count INTEGER,
                gclid TEXT,
                utm_source TEXT,
                utm_campaign TEXT,
                landing_site TEXT,
                products_json TEXT,
                abandoned_checkout_url TEXT,
                completed_order_id TEXT,
                event_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (store_id) REFERENCES shopify_stores(store_id)
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopify_cart_event_type ON shopify_cart_events(event_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopify_cart_email ON shopify_cart_events(customer_email)")

        self.conn.commit()
        logger.info("Shopify tables created successfully")

    def add_shopify_store(self, customer_id: int, shop_domain: str, access_token: str,
                          shop_name: str = None, email: str = None,
                          currency: str = "USD", timezone: str = None):
        """
        Add a new Shopify store connection

        Args:
            customer_id: Customer ID (links to customers table)
            shop_domain: Shopify domain (e.g., mystore.myshopify.com)
            access_token: Shopify Admin API access token
            shop_name: Store name
            email: Store owner email
            currency: Store currency
            timezone: Store timezone
        """
        try:
            # Generate store_id from shop_domain
            store_id = hashlib.md5(shop_domain.encode()).hexdigest()[:16]

            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO shopify_stores (
                    store_id, customer_id, shop_domain, shop_name, access_token,
                    email, currency, timezone, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (store_id, customer_id, shop_domain, shop_name, access_token,
                  email, currency, timezone))

            self.conn.commit()
            logger.info(f"Added Shopify store: {shop_domain} (ID: {store_id})")
            return store_id

        except Exception as e:
            logger.error(f"Failed to add Shopify store {shop_domain}: {e}")
            raise

    def get_shopify_stores(self, customer_id: Optional[int] = None) -> List[Dict]:
        """Get list of configured Shopify stores"""
        try:
            query = "SELECT * FROM shopify_stores WHERE is_active = 1"
            params = []

            if customer_id:
                query += " AND customer_id = ?"
                params.append(customer_id)

            cursor = self.conn.cursor()
            cursor.execute(query, params)

            stores = []
            for row in cursor.fetchall():
                stores.append({
                    'store_id': row[0],
                    'customer_id': row[1],
                    'shop_domain': row[2],
                    'shop_name': row[3],
                    'access_token': row[4],
                    'currency': row[7],
                    'timezone': row[8]
                })

            logger.info(f"Found {len(stores)} active Shopify stores")
            return stores

        except Exception as e:
            logger.error(f"Failed to get Shopify stores: {e}")
            return []

    def _make_shopify_api_request(self, shop_domain: str, access_token: str,
                                   endpoint: str, api_version: str = "2024-01") -> Optional[Dict]:
        """
        Make a request to Shopify Admin REST API

        Args:
            shop_domain: Shopify domain
            access_token: API access token
            endpoint: API endpoint (e.g., 'orders.json')
            api_version: Shopify API version
        """
        url = f"https://{shop_domain}/admin/api/{api_version}/{endpoint}"
        headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Shopify API request failed: {e}")
            return None

    def extract_orders(self, store_id: str, shop_domain: str, access_token: str,
                      customer_id: int, days_back: int = 90) -> pd.DataFrame:
        """
        Extract orders from Shopify for the last N days

        Args:
            store_id: Store ID
            shop_domain: Shopify domain
            access_token: API access token
            customer_id: Customer ID
            days_back: Number of days to look back (default: 90)
        """
        logger.info(f"Extracting orders from {shop_domain} (last {days_back} days)...")

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Shopify date format: 2024-01-01T00:00:00Z
        created_at_min = start_date.strftime("%Y-%m-%dT%H:%M:%S-00:00")

        # Make API request
        endpoint = f"orders.json?status=any&created_at_min={created_at_min}&limit=250"
        data = self._make_shopify_api_request(shop_domain, access_token, endpoint)

        if not data or 'orders' not in data:
            logger.warning(f"No orders found for {shop_domain}")
            return pd.DataFrame()

        orders_data = []

        for order in data['orders']:
            # Extract attribution data from order properties, tags, or notes
            gclid = None
            utm_source = None
            utm_medium = None
            utm_campaign = None
            utm_term = None
            utm_content = None
            landing_site = order.get('landing_site', '')
            referring_site = order.get('referring_site', '')

            # Try to extract gclid and UTM from landing_site URL
            if landing_site:
                # Parse URL parameters
                if '?' in landing_site:
                    params = landing_site.split('?')[1]
                    for param in params.split('&'):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            if key == 'gclid':
                                gclid = value
                            elif key == 'utm_source':
                                utm_source = value
                            elif key == 'utm_medium':
                                utm_medium = value
                            elif key == 'utm_campaign':
                                utm_campaign = value
                            elif key == 'utm_term':
                                utm_term = value
                            elif key == 'utm_content':
                                utm_content = value

            # Extract customer info
            customer = order.get('customer', {})

            orders_data.append({
                'order_id': str(order['id']),
                'store_id': store_id,
                'customer_id': customer_id,
                'order_number': str(order.get('order_number', '')),
                'order_name': order.get('name', ''),
                'email': order.get('email', order.get('contact_email', '')),
                'total_price': float(order.get('total_price', 0)),
                'subtotal_price': float(order.get('subtotal_price', 0)),
                'total_tax': float(order.get('total_tax', 0)),
                'total_discounts': float(order.get('total_discounts', 0)),
                'total_shipping': float(order.get('total_shipping_price_set', {}).get('shop_money', {}).get('amount', 0)),
                'currency': order.get('currency', 'USD'),
                'financial_status': order.get('financial_status', ''),
                'fulfillment_status': order.get('fulfillment_status', ''),
                'gclid': gclid,
                'utm_source': utm_source,
                'utm_medium': utm_medium,
                'utm_campaign': utm_campaign,
                'utm_term': utm_term,
                'utm_content': utm_content,
                'landing_site': landing_site,
                'referring_site': referring_site,
                'shopify_customer_id': str(customer.get('id', '')) if customer else None,
                'customer_first_name': customer.get('first_name', '') if customer else None,
                'customer_last_name': customer.get('last_name', '') if customer else None,
                'created_at_shopify': order.get('created_at', ''),
                'updated_at_shopify': order.get('updated_at', ''),
                'processed_at': order.get('processed_at', ''),
                'cancelled_at': order.get('cancelled_at', None),
                'closed_at': order.get('closed_at', None),
                'tags': order.get('tags', ''),
                'note': order.get('note', ''),
                'line_items_count': len(order.get('line_items', []))
            })

        df = pd.DataFrame(orders_data)
        logger.info(f"Extracted {len(df)} orders from {shop_domain}")

        # Log attribution coverage
        if not df.empty:
            with_gclid = df['gclid'].notna().sum()
            with_utm = df['utm_source'].notna().sum()
            logger.info(f"Attribution coverage: {with_gclid} orders with GCLID ({with_gclid/len(df)*100:.1f}%), "
                       f"{with_utm} with UTM source ({with_utm/len(df)*100:.1f}%)")

        return df

    def extract_products(self, store_id: str, shop_domain: str, access_token: str,
                        customer_id: int) -> pd.DataFrame:
        """Extract product catalog from Shopify"""
        logger.info(f"Extracting products from {shop_domain}...")

        endpoint = "products.json?limit=250"
        data = self._make_shopify_api_request(shop_domain, access_token, endpoint)

        if not data or 'products' not in data:
            logger.warning(f"No products found for {shop_domain}")
            return pd.DataFrame()

        products_data = []

        for product in data['products']:
            # Get primary image
            images = product.get('images', [])
            image_url = images[0].get('src', '') if images else None

            # Calculate total inventory
            variants = product.get('variants', [])
            inventory_quantity = sum(v.get('inventory_quantity', 0) for v in variants if v.get('inventory_quantity'))

            # Get price from first variant
            price = float(variants[0].get('price', 0)) if variants else 0
            compare_at_price = float(variants[0].get('compare_at_price', 0)) if variants and variants[0].get('compare_at_price') else None

            products_data.append({
                'product_id': str(product['id']),
                'store_id': store_id,
                'customer_id': customer_id,
                'title': product.get('title', ''),
                'body_html': product.get('body_html', ''),
                'vendor': product.get('vendor', ''),
                'product_type': product.get('product_type', ''),
                'handle': product.get('handle', ''),
                'variants_count': len(variants),
                'inventory_quantity': inventory_quantity,
                'inventory_policy': variants[0].get('inventory_policy', '') if variants else '',
                'price': price,
                'compare_at_price': compare_at_price,
                'status': product.get('status', ''),
                'published_at': product.get('published_at', None),
                'tags': product.get('tags', ''),
                'meta_description': product.get('meta_description', ''),
                'image_url': image_url,
                'images_count': len(images),
                'created_at_shopify': product.get('created_at', ''),
                'updated_at_shopify': product.get('updated_at', '')
            })

        df = pd.DataFrame(products_data)
        logger.info(f"Extracted {len(df)} products from {shop_domain}")
        return df

    def extract_customers(self, store_id: str, shop_domain: str, access_token: str,
                         customer_id: int) -> pd.DataFrame:
        """Extract customer data from Shopify"""
        logger.info(f"Extracting customers from {shop_domain}...")

        endpoint = "customers.json?limit=250"
        data = self._make_shopify_api_request(shop_domain, access_token, endpoint)

        if not data or 'customers' not in data:
            logger.warning(f"No customers found for {shop_domain}")
            return pd.DataFrame()

        customers_data = []

        for cust in data['customers']:
            # Get default address
            default_address = cust.get('default_address', {}) or {}

            # Calculate AOV
            orders_count = cust.get('orders_count', 0)
            total_spent = float(cust.get('total_spent', 0))
            aov = total_spent / orders_count if orders_count > 0 else 0

            customers_data.append({
                'shopify_customer_id': str(cust['id']),
                'store_id': store_id,
                'customer_id': customer_id,
                'email': cust.get('email', ''),
                'first_name': cust.get('first_name', ''),
                'last_name': cust.get('last_name', ''),
                'phone': cust.get('phone', ''),
                'accepts_marketing': cust.get('accepts_marketing', False),
                'marketing_opt_in_level': cust.get('marketing_opt_in_level', ''),
                'total_spent': total_spent,
                'orders_count': orders_count,
                'average_order_value': aov,
                'first_order_gclid': None,  # Will be filled by joining with orders
                'first_order_utm_source': None,
                'first_order_utm_campaign': None,
                'state': cust.get('state', ''),
                'verified_email': cust.get('verified_email', False),
                'city': default_address.get('city', ''),
                'province': default_address.get('province', ''),
                'country': default_address.get('country', ''),
                'created_at_shopify': cust.get('created_at', ''),
                'updated_at_shopify': cust.get('updated_at', ''),
                'last_order_at': cust.get('last_order_date', None)
            })

        df = pd.DataFrame(customers_data)
        logger.info(f"Extracted {len(df)} customers from {shop_domain}")
        return df

    def load_data(self, table_name: str, df: pd.DataFrame):
        """Load data into Shopify table"""
        if df.empty:
            logger.warning(f"No data to load into {table_name}")
            return

        try:
            # Use REPLACE to handle duplicates
            df.to_sql(table_name, self.conn, if_exists='append', index=False)
            logger.info(f"Loaded {len(df)} records into {table_name}")
        except Exception as e:
            logger.error(f"Error loading data into {table_name}: {e}")
            # Try to load row by row to identify problematic records
            logger.info("Attempting row-by-row load...")
            success_count = 0
            for idx, row in df.iterrows():
                try:
                    pd.DataFrame([row]).to_sql(table_name, self.conn, if_exists='append', index=False)
                    success_count += 1
                except Exception as row_error:
                    logger.error(f"Failed to load row {idx}: {row_error}")
            logger.info(f"Successfully loaded {success_count}/{len(df)} records")

    def update_customer_attribution(self, store_id: str):
        """
        Update customer attribution data (first order GCLID/UTM)
        Links customers to their first Google Ads click
        """
        logger.info(f"Updating customer attribution for store {store_id}...")

        cursor = self.conn.cursor()

        # Update customers with attribution from their first order
        cursor.execute("""
            UPDATE shopify_customers
            SET
                first_order_gclid = (
                    SELECT gclid FROM shopify_orders
                    WHERE shopify_orders.shopify_customer_id = shopify_customers.shopify_customer_id
                      AND shopify_orders.store_id = shopify_customers.store_id
                      AND gclid IS NOT NULL
                    ORDER BY created_at_shopify ASC
                    LIMIT 1
                ),
                first_order_utm_source = (
                    SELECT utm_source FROM shopify_orders
                    WHERE shopify_orders.shopify_customer_id = shopify_customers.shopify_customer_id
                      AND shopify_orders.store_id = shopify_customers.store_id
                      AND utm_source IS NOT NULL
                    ORDER BY created_at_shopify ASC
                    LIMIT 1
                ),
                first_order_utm_campaign = (
                    SELECT utm_campaign FROM shopify_orders
                    WHERE shopify_orders.shopify_customer_id = shopify_customers.shopify_customer_id
                      AND shopify_orders.store_id = shopify_customers.store_id
                      AND utm_campaign IS NOT NULL
                    ORDER BY created_at_shopify ASC
                    LIMIT 1
                )
            WHERE store_id = ?
        """, (store_id,))

        self.conn.commit()
        logger.info("Customer attribution updated successfully")

    def run_etl(self, customer_id: Optional[int] = None, days_back: int = 90):
        """
        Run the complete Shopify ETL pipeline

        Args:
            customer_id: Optional customer ID to process (processes all if None)
            days_back: Number of days to extract orders (default: 90)
        """
        logger.info("="*70)
        logger.info("STARTING SHOPIFY ETL PIPELINE")
        logger.info("="*70)

        try:
            # Get Shopify stores
            stores = self.get_shopify_stores(customer_id)

            if not stores:
                logger.warning("No Shopify stores configured")
                return

            # Process each store
            for store in stores:
                store_id = store['store_id']
                shop_domain = store['shop_domain']
                access_token = store['access_token']
                cust_id = store['customer_id']

                logger.info(f"\nProcessing store: {shop_domain} (ID: {store_id})")
                logger.info("-" * 70)

                # Extract data
                orders_df = self.extract_orders(store_id, shop_domain, access_token, cust_id, days_back)
                products_df = self.extract_products(store_id, shop_domain, access_token, cust_id)
                customers_df = self.extract_customers(store_id, shop_domain, access_token, cust_id)

                # Load data
                self.load_data('shopify_orders', orders_df)
                self.load_data('shopify_products', products_df)
                self.load_data('shopify_customers', customers_df)

                # Update customer attribution
                self.update_customer_attribution(store_id)

                # Update last_sync_at
                cursor = self.conn.cursor()
                cursor.execute("""
                    UPDATE shopify_stores
                    SET last_sync_at = CURRENT_TIMESTAMP
                    WHERE store_id = ?
                """, (store_id,))
                self.conn.commit()

                logger.info(f"Completed processing for {shop_domain}")

            # Print summary
            logger.info("\n" + "="*70)
            logger.info("SHOPIFY ETL PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*70)

            cursor = self.conn.cursor()
            summary = {
                'stores': cursor.execute("SELECT COUNT(*) FROM shopify_stores WHERE is_active = 1").fetchone()[0],
                'orders': cursor.execute("SELECT COUNT(*) FROM shopify_orders").fetchone()[0],
                'products': cursor.execute("SELECT COUNT(*) FROM shopify_products").fetchone()[0],
                'customers': cursor.execute("SELECT COUNT(*) FROM shopify_customers").fetchone()[0],
                'total_revenue': cursor.execute("SELECT SUM(total_price) FROM shopify_orders WHERE financial_status = 'paid'").fetchone()[0] or 0,
                'orders_with_gclid': cursor.execute("SELECT COUNT(*) FROM shopify_orders WHERE gclid IS NOT NULL").fetchone()[0],
                'attribution_rate': 0
            }

            if summary['orders'] > 0:
                summary['attribution_rate'] = (summary['orders_with_gclid'] / summary['orders']) * 100

            logger.info(f"\nData Summary:")
            logger.info(f"  Active Stores:      {summary['stores']}")
            logger.info(f"  Orders:             {summary['orders']}")
            logger.info(f"  Products:           {summary['products']}")
            logger.info(f"  Customers:          {summary['customers']}")
            logger.info(f"  Total Revenue:      ${summary['total_revenue']:.2f}")
            logger.info(f"  Orders with GCLID:  {summary['orders_with_gclid']} ({summary['attribution_rate']:.1f}%)")
            logger.info("="*70)

        except Exception as e:
            logger.error(f"Shopify ETL Pipeline failed: {e}")
            raise
        finally:
            self.conn.close()


if __name__ == "__main__":
    # Example usage
    etl = ShopifyETL()

    # To add a new store (run once per store):
    # store_id = etl.add_shopify_store(
    #     customer_id=1,
    #     shop_domain="your-store.myshopify.com",
    #     access_token="your_shopify_access_token",
    #     shop_name="Your Store Name",
    #     email="owner@example.com",
    #     currency="USD"
    # )

    # Run ETL for all stores
    etl.run_etl(days_back=90)
