#!/usr/bin/env python3
"""
Enhanced MarketingIQ Dashboard with Complete Analytics
Descriptive, Diagnostic, Predictive, and Prescriptive Analytics
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import json
from typing import Dict, List, Any
import random
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Import our KPI calculation engine
from kpi_algorithms import KPICalculator

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('google_ads_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    return dict(zip(row.keys(), row))

# ==================== DESCRIPTIVE ANALYTICS ====================

@app.route('/')
def dashboard():
    """Serve the main analytics dashboard"""
    return render_template('analytics_dashboard.html')

@app.route('/api/customers')
def get_customers():
    """Get list of available customers for filtering"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT DISTINCT
            c.customer_id,
            COUNT(DISTINCT c.campaign_id) as campaign_count,
            SUM(ck.conversion_value) as total_revenue,
            MAX(ck.date) as last_activity
        FROM campaigns c
        LEFT JOIN campaign_keywords ck ON c.campaign_id = ck.campaign_id
        GROUP BY c.customer_id
        ORDER BY total_revenue DESC
    """

    cursor.execute(query)
    customers = [dict_from_row(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        'customers': customers,
        'total': len(customers)
    })

@app.route('/api/descriptive/kpis')
def get_descriptive_kpis():
    """Get current KPIs and performance metrics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get customer_id from query parameters
    customer_id = request.args.get('customer_id', type=int)

    # Build WHERE clause for customer filtering
    where_clause = "WHERE ck.date >= date('now', '-30 days')"
    if customer_id:
        where_clause += f" AND ck.customer_id = {customer_id}"

    # Get overall metrics
    metrics_query = f"""
        SELECT
            SUM(ck.conversion_value) as total_revenue,
            AVG(ck.conversion_rate) as avg_conversion_rate,
            AVG(ck.avg_cpc_micros) / 1000000.0 as avg_cpc,
            AVG(ck.ctr) as avg_ctr,
            SUM(ck.clicks) as total_clicks,
            SUM(ck.impressions) as total_impressions,
            SUM(ck.cost_micros) / 1000000.0 as total_cost,
            SUM(ck.conversions) as total_conversions
        FROM campaign_keywords ck
        {where_clause}
    """

    cursor.execute(metrics_query)
    current_metrics = dict_from_row(cursor.fetchone())

    # Get previous period metrics for comparison
    prev_where_clause = "WHERE ck.date >= date('now', '-60 days') AND ck.date < date('now', '-30 days')"
    if customer_id:
        prev_where_clause += f" AND ck.customer_id = {customer_id}"

    prev_query = f"""
        SELECT
            SUM(ck.conversion_value) as total_revenue,
            AVG(ck.conversion_rate) as avg_conversion_rate,
            AVG(ck.avg_cpc_micros) / 1000000.0 as avg_cpc,
            AVG(ck.ctr) as avg_ctr
        FROM campaign_keywords ck
        {prev_where_clause}
    """

    cursor.execute(prev_query)
    prev_metrics = dict_from_row(cursor.fetchone())

    # Calculate changes
    revenue_change = ((current_metrics['total_revenue'] - prev_metrics['total_revenue']) /
                     prev_metrics['total_revenue'] * 100) if prev_metrics['total_revenue'] else 0

    conversion_rate_change = (current_metrics['avg_conversion_rate'] - prev_metrics['avg_conversion_rate'])

    cpc_change = ((current_metrics['avg_cpc'] - prev_metrics['avg_cpc']) /
                 prev_metrics['avg_cpc'] * 100) if prev_metrics['avg_cpc'] else 0

    ctr_change = (current_metrics['avg_ctr'] - prev_metrics['avg_ctr'])

    # Get sparkline data (last 7 days)
    sparkline_where = "WHERE date >= date('now', '-7 days')"
    if customer_id:
        sparkline_where += f" AND customer_id = {customer_id}"

    sparkline_query = f"""
        SELECT
            date,
            SUM(conversion_value) as revenue,
            AVG(conversion_rate) as conversion_rate,
            AVG(avg_cpc_micros) / 1000000.0 as cpc,
            AVG(ctr) as ctr
        FROM campaign_keywords
        {sparkline_where}
        GROUP BY date
        ORDER BY date
    """

    cursor.execute(sparkline_query)
    sparkline_data = [dict_from_row(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        'kpis': {
            'revenue': {
                'value': f"${current_metrics['total_revenue']:,.0f}",
                'change': revenue_change,
                'change_type': 'positive' if revenue_change > 0 else 'negative',
                'sparkline': [row['revenue'] for row in sparkline_data]
            },
            'conversion_rate': {
                'value': f"{current_metrics['avg_conversion_rate']:.2f}%",
                'change': conversion_rate_change,
                'change_type': 'positive' if conversion_rate_change > 0 else 'negative',
                'sparkline': [row['conversion_rate'] for row in sparkline_data]
            },
            'cpc': {
                'value': f"${current_metrics['avg_cpc']:.2f}",
                'change': cpc_change,
                'change_type': 'negative' if cpc_change > 0 else 'positive',
                'sparkline': [row['cpc'] for row in sparkline_data]
            },
            'ctr': {
                'value': f"{current_metrics['avg_ctr']:.2f}%",
                'change': ctr_change,
                'change_type': 'positive' if ctr_change > 0 else 'negative',
                'sparkline': [row['ctr'] for row in sparkline_data]
            }
        },
        'summary': {
            'total_clicks': current_metrics['total_clicks'],
            'total_impressions': current_metrics['total_impressions'],
            'total_cost': current_metrics['total_cost'],
            'total_conversions': current_metrics['total_conversions']
        }
    })

@app.route('/api/descriptive/performance-trends')
def get_performance_trends():
    """Get historical performance trends"""
    conn = get_db_connection()

    # Get customer_id from query parameters
    customer_id = request.args.get('customer_id', type=int)

    where_clause = "WHERE date >= date('now', '-180 days')"
    if customer_id:
        where_clause += f" AND customer_id = {customer_id}"

    query = f"""
        SELECT
            date,
            SUM(conversion_value) as revenue,
            SUM(cost_micros) / 1000000.0 as cost,
            SUM(conversions) as conversions,
            SUM(clicks) as clicks,
            SUM(impressions) as impressions
        FROM campaign_keywords
        {where_clause}
        GROUP BY date
        ORDER BY date
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return jsonify({
        'dates': df['date'].tolist(),
        'revenue': df['revenue'].tolist(),
        'cost': df['cost'].tolist(),
        'conversions': df['conversions'].tolist(),
        'clicks': df['clicks'].tolist(),
        'impressions': df['impressions'].tolist()
    })

@app.route('/api/descriptive/channel-distribution')
def get_channel_distribution():
    """Get channel performance distribution"""
    conn = get_db_connection()

    # Get customer_id from query parameters
    customer_id = request.args.get('customer_id', type=int)

    where_clause = ""
    if customer_id:
        where_clause = f"WHERE c.customer_id = {customer_id}"

    query = f"""
        SELECT
            c.channel_type,
            COUNT(DISTINCT c.campaign_id) as campaign_count,
            SUM(ck.conversion_value) as revenue,
            SUM(ck.cost_micros) / 1000000.0 as cost,
            SUM(ck.conversions) as conversions
        FROM campaigns c
        LEFT JOIN campaign_keywords ck ON c.campaign_id = ck.campaign_id
        {where_clause}
        GROUP BY c.channel_type
    """

    cursor = conn.cursor()
    cursor.execute(query)
    data = [dict_from_row(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify(data)

# ==================== DIAGNOSTIC ANALYTICS ====================

@app.route('/api/diagnostic/insights')
def get_diagnostic_insights():
    """Get diagnostic insights about performance issues"""
    conn = get_db_connection()
    cursor = conn.cursor()

    insights = []

    # Analyze high CPC causes
    high_cpc_query = """
        SELECT
            k.keyword_text,
            k.quality_score,
            AVG(ck.avg_cpc_micros) / 1000000.0 as avg_cpc,
            AVG(ck.search_rank_lost_impression_share) as competition
        FROM keywords k
        JOIN campaign_keywords ck ON k.keyword_id = ck.keyword_id
        WHERE ck.avg_cpc_micros / 1000000.0 > 3
        GROUP BY k.keyword_text, k.quality_score
        ORDER BY avg_cpc DESC
        LIMIT 10
    """

    cursor.execute(high_cpc_query)
    high_cpc_keywords = cursor.fetchall()

    if high_cpc_keywords:
        insights.append({
            'type': 'diagnostic',
            'title': 'High CPC Root Cause Analysis',
            'icon': 'search',
            'severity': 'warning',
            'description': f"""Your Cost-Per-Click has increased due to {len(high_cpc_keywords)} keywords
                           with high competition. Top keyword "{high_cpc_keywords[0]['keyword_text']}"
                           has CPC of ${high_cpc_keywords[0]['avg_cpc']:.2f}. Average Quality Score
                           is {high_cpc_keywords[0]['quality_score'] or 'N/A'}, indicating room for improvement.""",
            'action': 'View Detailed Analysis',
            'data': [dict_from_row(row) for row in high_cpc_keywords]
        })

    # Analyze conversion drop patterns
    conversion_pattern_query = """
        SELECT
            strftime('%w', date) as day_of_week,
            AVG(conversion_rate) as avg_conversion_rate,
            COUNT(*) as sample_size
        FROM campaign_keywords
        GROUP BY day_of_week
        ORDER BY avg_conversion_rate
    """

    cursor.execute(conversion_pattern_query)
    conversion_patterns = cursor.fetchall()

    if conversion_patterns:
        worst_day = conversion_patterns[0]
        best_day = conversion_patterns[-1]

        insights.append({
            'type': 'diagnostic',
            'title': 'Conversion Rate Pattern Analysis',
            'icon': 'bug',
            'severity': 'info',
            'description': f"""Conversion rates vary significantly by day of week.
                           Worst performing day (weekday {worst_day['day_of_week']}) has
                           {worst_day['avg_conversion_rate']:.2f}% conversion rate, while
                           best day has {best_day['avg_conversion_rate']:.2f}%.""",
            'action': 'Optimize Schedule',
            'data': [dict_from_row(row) for row in conversion_patterns]
        })

    # Budget efficiency analysis
    budget_waste_query = """
        SELECT
            k.keyword_text,
            k.quality_score,
            SUM(ck.cost_micros) / 1000000.0 as total_cost,
            SUM(ck.conversions) as total_conversions,
            SUM(ck.cost_micros) / NULLIF(SUM(ck.conversions), 0) / 1000000.0 as cost_per_conversion
        FROM keywords k
        JOIN campaign_keywords ck ON k.keyword_id = ck.keyword_id
        WHERE k.quality_score < 5 OR ck.conversions = 0
        GROUP BY k.keyword_text, k.quality_score
        HAVING total_cost > 100
        ORDER BY total_cost DESC
        LIMIT 20
    """

    cursor.execute(budget_waste_query)
    wasteful_keywords = cursor.fetchall()

    if wasteful_keywords:
        total_waste = sum(row['total_cost'] for row in wasteful_keywords)

        insights.append({
            'type': 'diagnostic',
            'title': 'Budget Efficiency Analysis',
            'icon': 'alert',
            'severity': 'high',
            'description': f"""${total_waste:,.2f} is being spent on {len(wasteful_keywords)}
                           underperforming keywords with Quality Scores below 5 or zero conversions.
                           This represents a significant optimization opportunity.""",
            'action': 'Optimize Budget',
            'data': [dict_from_row(row) for row in wasteful_keywords]
        })

    conn.close()

    return jsonify({'insights': insights})

@app.route('/api/diagnostic/correlation-matrix')
def get_correlation_matrix():
    """Get correlation matrix for key metrics"""
    conn = get_db_connection()

    query = """
        SELECT
            ctr,
            avg_cpc_micros / 1000000.0 as cpc,
            conversion_rate,
            search_impression_share as impression_share,
            absolute_top_impression_percentage as position
        FROM campaign_keywords
        WHERE ctr IS NOT NULL
        AND avg_cpc_micros IS NOT NULL
        AND conversion_rate IS NOT NULL
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        correlation_matrix = df.corr().round(2)

        return jsonify({
            'matrix': correlation_matrix.to_dict(),
            'metrics': correlation_matrix.columns.tolist()
        })

    return jsonify({'matrix': {}, 'metrics': []})

# ==================== PREDICTIVE ANALYTICS ====================

@app.route('/api/predictive/forecasts')
def get_forecasts():
    """Get predictive forecasts using ML models"""
    conn = get_db_connection()

    # Get historical data for forecasting
    query = """
        SELECT
            date,
            SUM(conversion_value) as revenue,
            SUM(cost_micros) / 1000000.0 as cost,
            AVG(conversion_rate) as conversion_rate,
            AVG(avg_cpc_micros) / 1000000.0 as cpc,
            SUM(conversions) as conversions
        FROM campaign_keywords
        WHERE date >= date('now', '-90 days')
        GROUP BY date
        ORDER BY date
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        # Simple linear regression for forecasting
        df['day_num'] = range(len(df))

        # Revenue forecast
        X = df[['day_num']].values
        y_revenue = df['revenue'].values

        model_revenue = LinearRegression()
        model_revenue.fit(X, y_revenue)

        # Forecast next 30 days
        future_days = np.array([[i] for i in range(len(df), len(df) + 30)])
        revenue_forecast = model_revenue.predict(future_days)

        # Add some randomness for upper/lower bounds
        revenue_upper = revenue_forecast * 1.15
        revenue_lower = revenue_forecast * 0.85

        # CPC forecast
        y_cpc = df['cpc'].values
        model_cpc = LinearRegression()
        model_cpc.fit(X, y_cpc)
        cpc_forecast = model_cpc.predict([[len(df) + 7]])[0]  # Next week

        # Conversion rate forecast
        y_conv = df['conversion_rate'].values
        model_conv = LinearRegression()
        model_conv.fit(X, y_conv)
        conv_forecast = model_conv.predict([[len(df) + 30]])[0]  # Next month

        # Calculate churn risk (simulated)
        recent_conversions = df.tail(7)['conversions'].mean()
        historical_avg = df['conversions'].mean()
        churn_risk = max(0, min(100, (1 - recent_conversions / historical_avg) * 100)) if historical_avg > 0 else 0

        return jsonify({
            'revenue_30day': {
                'value': f"${revenue_forecast.sum():,.0f}",
                'confidence_interval': f"${revenue_lower.sum():,.0f}-${revenue_upper.sum():,.0f}",
                'trend': 'positive' if revenue_forecast[-1] > revenue_forecast[0] else 'negative'
            },
            'conversion_rate': {
                'value': f"{conv_forecast:.2f}%",
                'current': f"{df['conversion_rate'].iloc[-1]:.2f}%",
                'change': conv_forecast - df['conversion_rate'].iloc[-1]
            },
            'cpc_next_week': {
                'value': f"${cpc_forecast:.2f}",
                'current': f"${df['cpc'].iloc[-1]:.2f}",
                'change_percent': ((cpc_forecast - df['cpc'].iloc[-1]) / df['cpc'].iloc[-1] * 100)
            },
            'churn_risk': {
                'score': f"{churn_risk:.0f}%",
                'customers_at_risk': int(churn_risk * 7.78),  # Simulated
                'severity': 'high' if churn_risk > 30 else 'medium' if churn_risk > 15 else 'low'
            },
            'forecast_series': {
                'dates': pd.date_range(start=pd.to_datetime(df['date'].iloc[-1]) + timedelta(days=1),
                                      periods=30).strftime('%Y-%m-%d').tolist(),
                'revenue': revenue_forecast.tolist(),
                'revenue_upper': revenue_upper.tolist(),
                'revenue_lower': revenue_lower.tolist()
            }
        })

    return jsonify({'error': 'Insufficient data for forecasting'})

@app.route('/api/predictive/alerts')
def get_predictive_alerts():
    """Get predictive alerts based on trend analysis"""
    conn = get_db_connection()
    cursor = conn.cursor()

    alerts = []

    # Budget depletion prediction
    budget_query = """
        SELECT
            c.campaign_name,
            c.budget_amount_micros / 1000000.0 as budget,
            AVG(ck.cost_micros) / 1000000.0 as daily_spend
        FROM campaigns c
        JOIN campaign_keywords ck ON c.campaign_id = ck.campaign_id
        WHERE ck.date >= date('now', '-7 days')
        GROUP BY c.campaign_name, c.budget_amount_micros
        HAVING daily_spend > 0
    """

    cursor.execute(budget_query)
    campaigns = cursor.fetchall()

    for campaign in campaigns:
        if campaign['budget'] and campaign['daily_spend']:
            days_remaining = campaign['budget'] / campaign['daily_spend']
            if days_remaining < 5:
                alerts.append({
                    'type': 'budget_depletion',
                    'severity': 'high' if days_remaining < 2 else 'medium',
                    'title': f"Budget Depletion Warning: {campaign['campaign_name']}",
                    'description': f"Campaign will exhaust budget in {days_remaining:.1f} days at current spending rate",
                    'impact': f"Potential loss of ${campaign['daily_spend'] * 5:.0f} in revenue"
                })

    # Seasonal pattern detection
    seasonal_query = """
        SELECT
            strftime('%m', date) as month,
            AVG(conversion_value) as avg_revenue,
            AVG(ctr) as avg_ctr
        FROM campaign_keywords
        GROUP BY month
        ORDER BY month
    """

    cursor.execute(seasonal_query)
    seasonal_data = cursor.fetchall()

    current_month = datetime.now().month
    next_month = (current_month % 12) + 1

    for month_data in seasonal_data:
        if int(month_data['month']) == next_month:
            alerts.append({
                'type': 'seasonal_pattern',
                'severity': 'info',
                'title': 'Seasonal Pattern Alert',
                'description': f"Based on historical data, expect {month_data['avg_ctr']:.1f}% CTR next month",
                'impact': f"Estimated revenue: ${month_data['avg_revenue']:,.0f}"
            })

    conn.close()

    return jsonify({'alerts': alerts})

# ==================== PRESCRIPTIVE ANALYTICS ====================

@app.route('/api/prescriptive/recommendations')
def get_recommendations():
    """Get actionable recommendations based on analysis"""
    conn = get_db_connection()
    cursor = conn.cursor()

    recommendations = []

    # 1. Identify keywords to pause
    pause_keywords_query = """
        SELECT
            k.keyword_text,
            k.keyword_id,
            k.quality_score,
            SUM(ck.cost_micros) / 1000000.0 as total_cost,
            SUM(ck.conversions) as total_conversions
        FROM keywords k
        JOIN campaign_keywords ck ON k.keyword_id = ck.keyword_id
        WHERE ck.date >= date('now', '-30 days')
        GROUP BY k.keyword_id, k.keyword_text, k.quality_score
        HAVING (k.quality_score < 3 OR k.quality_score IS NULL)
        AND total_conversions = 0
        AND total_cost > 50
    """

    cursor.execute(pause_keywords_query)
    keywords_to_pause = cursor.fetchall()

    if keywords_to_pause:
        total_savings = sum(kw['total_cost'] for kw in keywords_to_pause)

        recommendations.append({
            'priority': 'high',
            'title': 'Pause Underperforming Keywords',
            'description': f"Immediately pause {len(keywords_to_pause)} keywords with Quality Score below 3 and zero conversions. These keywords have consumed ${total_savings:,.0f} without generating any conversions.",
            'impact': {
                'cost_savings': f"${total_savings:,.0f}/mo",
                'roi_impact': '+15%',
                'effort': 'Low'
            },
            'action_items': [kw['keyword_text'] for kw in keywords_to_pause[:5]],
            'implementation': 'immediate'
        })

    # 2. Smart bidding recommendation
    manual_bidding_query = """
        SELECT
            c.campaign_name,
            c.campaign_id,
            c.bidding_strategy_type,
            AVG(ck.conversion_rate) as avg_conv_rate,
            SUM(ck.cost_micros) / NULLIF(SUM(ck.conversions), 0) / 1000000.0 as cpa
        FROM campaigns c
        JOIN campaign_keywords ck ON c.campaign_id = ck.campaign_id
        WHERE c.bidding_strategy_type = 'MANUAL_CPC'
        AND ck.date >= date('now', '-30 days')
        GROUP BY c.campaign_id, c.campaign_name, c.bidding_strategy_type
        HAVING SUM(ck.conversions) > 50
    """

    cursor.execute(manual_bidding_query)
    manual_campaigns = cursor.fetchall()

    if manual_campaigns:
        avg_cpa = np.mean([c['cpa'] for c in manual_campaigns if c['cpa']])
        potential_cpa_reduction = avg_cpa * 0.22  # 22% reduction estimate

        recommendations.append({
            'priority': 'high',
            'title': 'Implement Smart Bidding',
            'description': f"Switch {len(manual_campaigns)} campaigns from Manual CPC to Target CPA bidding. Based on conversion data, this could reduce CPA by 22% while maintaining conversion volume.",
            'impact': {
                'cpa_reduction': '-22%',
                'time_saved': '5hrs/week',
                'effort': 'Medium'
            },
            'action_items': [c['campaign_name'] for c in manual_campaigns[:3]],
            'implementation': '1-2 days'
        })

    # 3. Negative keywords recommendation
    search_terms_query = """
        SELECT
            st.search_term,
            SUM(st.clicks) as total_clicks,
            SUM(st.cost_micros) / 1000000.0 as total_cost,
            SUM(st.conversions) as total_conversions
        FROM search_terms st
        WHERE st.date >= date('now', '-30 days')
        GROUP BY st.search_term
        HAVING total_conversions = 0
        AND total_clicks > 10
        ORDER BY total_cost DESC
        LIMIT 50
    """

    cursor.execute(search_terms_query)
    negative_keywords = cursor.fetchall()

    if negative_keywords:
        wasted_budget = sum(kw['total_cost'] for kw in negative_keywords)
        wasted_clicks = sum(kw['total_clicks'] for kw in negative_keywords)

        recommendations.append({
            'priority': 'medium',
            'title': 'Add Negative Keywords',
            'description': f"Add {len(negative_keywords)} identified negative keywords to prevent irrelevant clicks. These terms generated {wasted_clicks} clicks and ${wasted_budget:,.0f} in costs with zero conversions.",
            'impact': {
                'budget_saved': f"{(wasted_budget/sum(kw['total_cost'] for kw in negative_keywords)*100):.0f}%",
                'ctr_impact': '+2.3%',
                'effort': 'Low'
            },
            'action_items': [kw['search_term'] for kw in negative_keywords[:5]],
            'implementation': 'immediate'
        })

    # 4. Ad schedule optimization
    hourly_performance_query = """
        SELECT
            strftime('%H', date) as hour,
            AVG(conversion_rate) as avg_conv_rate,
            AVG(avg_cpc_micros) / 1000000.0 as avg_cpc,
            COUNT(*) as sample_size
        FROM campaign_keywords
        GROUP BY hour
        ORDER BY avg_conv_rate DESC
    """

    cursor.execute(hourly_performance_query)
    hourly_data = cursor.fetchall()

    if hourly_data:
        best_hours = hourly_data[:4]  # Top 4 hours
        worst_hours = hourly_data[-4:]  # Bottom 4 hours

        recommendations.append({
            'priority': 'medium',
            'title': 'Optimize Ad Schedule',
            'description': f"Increase bids by 25% during peak hours ({', '.join([h['hour'] + ':00' for h in best_hours])}) and decrease by 50% during low-performing hours. Peak hours show {best_hours[0]['avg_conv_rate']:.1f}% conversion rate.",
            'impact': {
                'conv_increase': '+12%',
                'cost_change': '-5%',
                'effort': 'Low'
            },
            'action_items': [
                f"Increase bids at {h['hour']}:00 (Conv Rate: {h['avg_conv_rate']:.1f}%)" for h in best_hours[:2]
            ],
            'implementation': 'immediate'
        })

    # 5. Responsive Search Ads recommendation
    text_ad_query = """
        SELECT COUNT(DISTINCT ag.ad_group_id) as ad_group_count
        FROM ad_groups ag
        WHERE ag.status = 'ENABLED'
    """

    cursor.execute(text_ad_query)
    ad_group_count = cursor.fetchone()['ad_group_count']

    if ad_group_count:
        recommendations.append({
            'priority': 'low',
            'title': 'Test Responsive Search Ads',
            'description': f"Create responsive search ads for top {min(10, ad_group_count)} ad groups. Machine learning will test different combinations to improve CTR by 15-20%.",
            'impact': {
                'ctr_increase': '+15%',
                'setup_time': '2hrs',
                'effort': 'Medium'
            },
            'action_items': [
                'Create 3-5 headlines per ad group',
                'Add 2-3 descriptions',
                'Enable auto-optimization'
            ],
            'implementation': '2-3 days'
        })

    conn.close()

    return jsonify({'recommendations': recommendations})

@app.route('/api/prescriptive/action-timeline')
def get_action_timeline():
    """Get recommended implementation timeline"""

    timeline = [
        {
            'task': 'Pause Keywords',
            'start_day': 0,
            'duration': 1,
            'priority': 'high',
            'responsible': 'PPC Manager'
        },
        {
            'task': 'Smart Bidding',
            'start_day': 1,
            'duration': 3,
            'priority': 'high',
            'responsible': 'Campaign Manager'
        },
        {
            'task': 'Negative Keywords',
            'start_day': 2,
            'duration': 1,
            'priority': 'medium',
            'responsible': 'PPC Analyst'
        },
        {
            'task': 'Ad Schedule',
            'start_day': 4,
            'duration': 1,
            'priority': 'medium',
            'responsible': 'PPC Manager'
        },
        {
            'task': 'Test RSAs',
            'start_day': 6,
            'duration': 3,
            'priority': 'low',
            'responsible': 'Creative Team'
        },
        {
            'task': 'Expand Match Types',
            'start_day': 9,
            'duration': 2,
            'priority': 'low',
            'responsible': 'PPC Analyst'
        }
    ]

    return jsonify({'timeline': timeline})

# ==================== ADVANCED KPI ENDPOINTS ====================

@app.route('/api/kpi/roas')
def get_roas():
    """Get Return on Ad Spend (ROAS) metrics"""
    customer_id = request.args.get('customer_id', type=int)
    period_days = request.args.get('period_days', 30, type=int)

    calculator = KPICalculator()
    roas_data = calculator.calculate_roas(customer_id, period_days)
    calculator.close()

    return jsonify(roas_data)

@app.route('/api/kpi/clv')
def get_customer_lifetime_value():
    """Get Customer Lifetime Value (CLV) metrics"""
    customer_id = request.args.get('customer_id', type=int)

    calculator = KPICalculator()
    clv_data = calculator.calculate_customer_lifetime_value(customer_id)
    calculator.close()

    return jsonify(clv_data)

@app.route('/api/kpi/cac')
def get_customer_acquisition_cost():
    """Get Customer Acquisition Cost (CAC) metrics"""
    customer_id = request.args.get('customer_id', type=int)
    period_days = request.args.get('period_days', 30, type=int)

    calculator = KPICalculator()
    cac_data = calculator.calculate_customer_acquisition_cost(customer_id, period_days)
    calculator.close()

    return jsonify(cac_data)

@app.route('/api/kpi/quality-score')
def get_quality_score_impact():
    """Get Quality Score impact analysis"""
    customer_id = request.args.get('customer_id', type=int)

    calculator = KPICalculator()
    qs_data = calculator.calculate_quality_score_impact(customer_id)
    calculator.close()

    return jsonify(qs_data)

@app.route('/api/kpi/attribution')
def get_attribution_analysis():
    """Get attribution-weighted conversion analysis"""
    customer_id = request.args.get('customer_id', type=int)

    calculator = KPICalculator()
    attribution_data = calculator.calculate_attribution_weighted_conversions(customer_id)
    calculator.close()

    return jsonify(attribution_data)

@app.route('/api/kpi/anomalies')
def get_anomaly_detection():
    """Get anomaly detection for KPIs"""
    customer_id = request.args.get('customer_id', type=int)
    sensitivity = request.args.get('sensitivity', 2.0, type=float)

    calculator = KPICalculator()
    anomaly_data = calculator.calculate_anomaly_scores(customer_id, sensitivity)
    calculator.close()

    return jsonify(anomaly_data)

@app.route('/api/kpi/trends')
def get_trend_analysis():
    """Get comprehensive trend analysis"""
    customer_id = request.args.get('customer_id', type=int)
    period_days = request.args.get('period_days', 90, type=int)

    calculator = KPICalculator()
    trend_data = calculator.calculate_trend_analysis(customer_id, period_days)
    calculator.close()

    return jsonify(trend_data)

# ==================== REAL-TIME DATA ENDPOINTS ====================

@app.route('/api/realtime/metrics')
def get_realtime_metrics():
    """Get real-time performance metrics from actual database data"""

    # Get customer_id from query parameters
    customer_id = request.args.get('customer_id', type=int)

    # Use KPI calculator for real data
    calculator = KPICalculator()
    realtime_data = calculator.calculate_realtime_metrics(customer_id)
    calculator.close()

    return jsonify(realtime_data)

@app.route('/api/export/<report_type>')
def export_report(report_type):
    """Export analytics reports"""
    conn = get_db_connection()

    if report_type == 'performance':
        query = """
            SELECT * FROM campaign_keywords
            WHERE date >= date('now', '-30 days')
        """
    elif report_type == 'keywords':
        query = """
            SELECT * FROM keywords
            WHERE status = 'ENABLED'
        """
    elif report_type == 'recommendations':
        # Return prescriptive recommendations as CSV
        return get_recommendations()
    else:
        return jsonify({'error': 'Invalid report type'}), 400

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Convert to CSV
    csv_data = df.to_csv(index=False)

    return csv_data, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename={report_type}_report_{datetime.now().strftime("%Y%m%d")}.csv'
    }

if __name__ == '__main__':
    print("=" * 80)
    print("MARKETINGIQ ENHANCED ANALYTICS DASHBOARD")
    print("=" * 80)
    print("\nStarting server...")
    print("\nFeatures:")
    print("  + Descriptive Analytics - What happened?")
    print("  + Diagnostic Analytics - Why did it happen?")
    print("  + Predictive Analytics - What will happen?")
    print("  + Prescriptive Analytics - What should you do?")
    print("\nAccess the dashboard at: http://localhost:5000")
    print("=" * 80)

    app.run(host='0.0.0.0', port=5000, debug=True)