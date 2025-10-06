"""
MarketingIQ Dashboard API
Comprehensive API endpoints for all sub-agents and tools
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
import sys
from datetime import datetime, timedelta
import json
import pandas as pd
from typing import Dict, List, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'google-ads-multiagent'))

from google_ads_multiagent.adk.orchestration_agent.agent import OrchestrationAgent
from google_ads_multiagent.adk.orchestration_agent.sub_agents.data_agent.agent import DataAgent
from google_ads_multiagent.adk.orchestration_agent.sub_agents.insight_agent.agent import InsightAgent
from google_ads_multiagent.adk.orchestration_agent.sub_agents.forecasting_agent.agent import ForecastingAgent
from google_ads_multiagent.adk.orchestration_agent.sub_agents.optimization_agent.agent import OptimizationAgent

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize agents
orchestration_agent = OrchestrationAgent()
data_agent = DataAgent()
insight_agent = InsightAgent()
forecasting_agent = ForecastingAgent()
optimization_agent = OptimizationAgent()

# ==================== Main Dashboard Routes ====================

@app.route('/')
def index():
    """Main MarketingIQ Dashboard"""
    return render_template('index.html')

@app.route('/api/dashboard/overview')
def dashboard_overview():
    """Get overview metrics for main dashboard"""
    try:
        metrics = {
            'total_campaigns': 12,
            'active_campaigns': 8,
            'total_spend': 45000.00,
            'total_conversions': 3450,
            'avg_ctr': 3.45,
            'avg_cpc': 1.23,
            'roi': 245.5,
            'performance_trend': [
                {'date': '2024-01-01', 'impressions': 10000, 'clicks': 350, 'conversions': 45},
                {'date': '2024-01-02', 'impressions': 12000, 'clicks': 420, 'conversions': 52},
                {'date': '2024-01-03', 'impressions': 11500, 'clicks': 380, 'conversions': 48},
            ],
            'top_campaigns': [
                {'name': 'Brand Awareness Q1', 'spend': 5000, 'conversions': 450, 'roi': 320},
                {'name': 'Product Launch 2024', 'spend': 8000, 'conversions': 680, 'roi': 285},
                {'name': 'Holiday Special', 'spend': 3500, 'conversions': 290, 'roi': 265},
            ]
        }
        return jsonify({'status': 'success', 'data': metrics})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== Data Agent API Endpoints ====================

@app.route('/api/data-agent/campaigns')
def get_campaigns():
    """Get all campaigns data"""
    try:
        campaigns = data_agent.get_campaigns()
        return jsonify({'status': 'success', 'data': campaigns})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/data-agent/adgroups/<campaign_id>')
def get_adgroups(campaign_id):
    """Get ad groups for a specific campaign"""
    try:
        adgroups = data_agent.get_adgroups(campaign_id)
        return jsonify({'status': 'success', 'data': adgroups})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/data-agent/keywords/<adgroup_id>')
def get_keywords(adgroup_id):
    """Get keywords for a specific ad group"""
    try:
        keywords = data_agent.get_keywords(adgroup_id)
        return jsonify({'status': 'success', 'data': keywords})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/data-agent/search-terms')
def get_search_terms():
    """Get search terms report"""
    try:
        date_range = request.args.get('date_range', '7')
        search_terms = data_agent.get_search_terms(date_range)
        return jsonify({'status': 'success', 'data': search_terms})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== Insight Agent API Endpoints ====================

@app.route('/api/insight-agent/performance-analysis')
def get_performance_analysis():
    """Get performance analysis"""
    try:
        campaign_id = request.args.get('campaign_id')
        date_range = request.args.get('date_range', '30')
        analysis = insight_agent.analyze_performance(campaign_id, date_range)
        return jsonify({'status': 'success', 'data': analysis})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/insight-agent/anomalies')
def detect_anomalies():
    """Detect anomalies in campaign performance"""
    try:
        anomalies = insight_agent.detect_anomalies()
        return jsonify({'status': 'success', 'data': anomalies})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/insight-agent/competitor-analysis')
def get_competitor_analysis():
    """Get competitor analysis"""
    try:
        analysis = insight_agent.analyze_competitors()
        return jsonify({'status': 'success', 'data': analysis})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/insight-agent/trends')
def get_trends():
    """Get trend analysis"""
    try:
        metric = request.args.get('metric', 'clicks')
        period = request.args.get('period', '30')
        trends = insight_agent.analyze_trends(metric, period)
        return jsonify({'status': 'success', 'data': trends})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/insight-agent/roi-calculator')
def calculate_roi():
    """Calculate ROI for campaigns"""
    try:
        campaign_id = request.args.get('campaign_id')
        roi_data = insight_agent.calculate_roi(campaign_id)
        return jsonify({'status': 'success', 'data': roi_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== Forecasting Agent API Endpoints ====================

@app.route('/api/forecasting-agent/performance-forecast')
def get_performance_forecast():
    """Get performance forecast"""
    try:
        campaign_id = request.args.get('campaign_id')
        days_ahead = int(request.args.get('days', 30))
        forecast = forecasting_agent.forecast_performance(campaign_id, days_ahead)
        return jsonify({'status': 'success', 'data': forecast})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/forecasting-agent/scenario-planning', methods=['POST'])
def plan_scenarios():
    """Plan different scenarios"""
    try:
        scenarios = request.json
        results = forecasting_agent.plan_scenarios(scenarios)
        return jsonify({'status': 'success', 'data': results})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== Optimization Agent API Endpoints ====================

@app.route('/api/optimization-agent/recommendations')
def get_recommendations():
    """Get optimization recommendations"""
    try:
        campaign_id = request.args.get('campaign_id')
        recommendations = optimization_agent.get_recommendations(campaign_id)
        return jsonify({'status': 'success', 'data': recommendations})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/optimization-agent/bid-adjustments')
def get_bid_adjustments():
    """Get bid adjustment recommendations"""
    try:
        campaign_id = request.args.get('campaign_id')
        adjustments = optimization_agent.calculate_bid_adjustments(campaign_id)
        return jsonify({'status': 'success', 'data': adjustments})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/optimization-agent/budget-allocation')
def get_budget_allocation():
    """Get budget allocation recommendations"""
    try:
        total_budget = float(request.args.get('budget', 10000))
        allocation = optimization_agent.allocate_budget(total_budget)
        return jsonify({'status': 'success', 'data': allocation})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== Tool-Specific Dashboard Routes ====================

@app.route('/dashboard/data-agent')
def data_agent_dashboard():
    """Data Agent Dashboard"""
    return render_template('dashboards/data_agent.html')

@app.route('/dashboard/insight-agent')
def insight_agent_dashboard():
    """Insight Agent Dashboard"""
    return render_template('dashboards/insight_agent.html')

@app.route('/dashboard/forecasting-agent')
def forecasting_agent_dashboard():
    """Forecasting Agent Dashboard"""
    return render_template('dashboards/forecasting_agent.html')

@app.route('/dashboard/optimization-agent')
def optimization_agent_dashboard():
    """Optimization Agent Dashboard"""
    return render_template('dashboards/optimization_agent.html')

# Tool-specific dashboards
@app.route('/dashboard/tools/<tool_name>')
def tool_dashboard(tool_name):
    """Individual tool dashboards"""
    return render_template(f'dashboards/tools/{tool_name}.html')

# ==================== WebSocket Events ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to MarketingIQ Dashboard'})

@socketio.on('subscribe_metrics')
def handle_subscribe(data):
    """Subscribe to real-time metrics"""
    campaign_id = data.get('campaign_id')
    emit('metrics_update', get_real_time_metrics(campaign_id))

def get_real_time_metrics(campaign_id=None):
    """Get real-time metrics for WebSocket"""
    return {
        'timestamp': datetime.now().isoformat(),
        'impressions': 12500,
        'clicks': 425,
        'conversions': 52,
        'spend': 520.50,
        'ctr': 3.4,
        'cpc': 1.22
    }

# ==================== Health Check ====================

@app.route('/health')
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'agents': {
            'orchestration': 'active',
            'data': 'active',
            'insight': 'active',
            'forecasting': 'active',
            'optimization': 'active'
        }
    })

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8002, debug=True)