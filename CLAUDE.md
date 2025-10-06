- ultra think about the plan i give now and start implemening carefully, When CEO/team selects a customer, every dashboard (Data, Insights,     
  Optimization, Forecasting, Alerts) should update and show only that customer’s data.

  🗂 Plan
  1. Database Layer

  Make sure every record in your warehouse has a customer_id (a.k.a. Google Ads customerId).
  Tables:

  campaigns_performance → has customer_id + campaign_id

  adgroups_performance → has customer_id + adgroup_id

  keywords_performance → has customer_id + keyword_id

  search_terms → has customer_id

  ml_features → has customer_id

  ✅ This ensures we can filter everything downstream.

  2. Backend API

  Expose routes that accept customer_id as query param:

  /api/campaigns?customer_id=123

  /api/adgroups?customer_id=123

  /api/keywords/performance?customer_id=123

  Each agent’s tools will forward customer_id to DB queries.

  3. Frontend (React Dashboard)

  Global Customer Selector (dropdown at top → all dashboards react).

  Options → list of customer_id + customer_name pairs.

  Default → first customer in DB.

  Pass customer_id to all API calls.

  4. Filters Per Dashboard

  Data Agent → campaign/adgroup/keyword list filtered by customer.

  Insight Agent → anomalies only from that customer’s campaigns.

  Optimization Agent → budget recommendations just for that customer.

  Forecasting Agent → spend/CTR projections on customer’s past data.

  Alert Agent → alerts (threshold breaches) scoped to selected customer.

  5. UI/UX

  Place filter bar fixed at top (dark theme, minimal).

  Add:

  Customer selector

  Date range picker

  Campaign type filter (Search/Ecommerce/B2B)

  Smooth transition → when filters change, dashboards reload without heavy animations.

  ⚡ Why this works

  Scales for multi-customer setups.

  CEO can pick a client and instantly see only their story.

  Matches expectation: Google Ads UI parity.