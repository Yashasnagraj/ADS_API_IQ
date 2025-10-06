from flask import Flask, jsonify
from flask_cors import CORS
import random
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

def generate_mock_data():
    return {
        'campaigns': [
            {
                'campaign_id': f'C{i:03d}',
                'campaign_name': campaign,
                'status': random.choice(['ENABLED', 'PAUSED']),
                'impressions': random.randint(1000, 50000),
                'clicks': random.randint(50, 2000),
                'cost': round(random.uniform(100, 5000), 2),
                'conversions': random.randint(5, 200),
                'ctr': round(random.uniform(1, 5), 2),
                'cpc': round(random.uniform(0.5, 3), 2),
                'conversion_rate': round(random.uniform(1, 10), 2),
                'date': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
            }
            for i, campaign in enumerate([
                'Summer Sale 2024',
                'Black Friday Deals',
                'Brand Awareness Q4',
                'Product Launch - Pro Series',
                'Holiday Promotions 2024',
                'New Customer Acquisition',
                'Retargeting - Cart Abandoners',
                'Mobile App Install Campaign',
                'Local Services - Metro Area',
                'B2B Lead Generation'
            ], 1)
        ],
        'keywords': [
            {
                'keyword_id': f'K{i:03d}',
                'keyword_text': keyword,
                'match_type': random.choice(['EXACT', 'PHRASE', 'BROAD']),
                'impressions': random.randint(500, 20000),
                'clicks': random.randint(20, 1000),
                'cost': round(random.uniform(50, 2000), 2),
                'avg_position': round(random.uniform(1, 5), 1),
                'quality_score': random.randint(1, 10),
                'ctr': round(random.uniform(1, 8), 2),
                'cpc': round(random.uniform(0.3, 2.5), 2),
                'conversions': random.randint(2, 150),
                'conversion_rate': round(random.uniform(1, 15), 2)
            }
            for i, keyword in enumerate([
                'digital marketing services',
                'seo optimization',
                'ppc management',
                'social media marketing',
                'content marketing strategy',
                'email marketing campaigns',
                'marketing automation tools',
                'google ads management',
                'facebook advertising',
                'instagram marketing',
                'linkedin advertising',
                'youtube marketing',
                'influencer marketing',
                'affiliate marketing',
                'conversion rate optimization',
                'landing page design',
                'marketing analytics',
                'brand strategy',
                'customer acquisition',
                'lead generation services'
            ], 1)
        ]
    }

mock_data = generate_mock_data()

@app.route('/campaigns', methods=['GET'])
def get_campaigns():
    return jsonify(mock_data['campaigns'])

@app.route('/keywords', methods=['GET'])
def get_keywords():
    return jsonify(mock_data['keywords'])

@app.route('/metrics/campaigns', methods=['GET'])
def get_campaign_metrics():
    total_impressions = sum(c['impressions'] for c in mock_data['campaigns'])
    total_clicks = sum(c['clicks'] for c in mock_data['campaigns'])
    total_cost = sum(c['cost'] for c in mock_data['campaigns'])
    total_conversions = sum(c['conversions'] for c in mock_data['campaigns'])

    return jsonify({
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_cost': round(total_cost, 2),
        'total_conversions': total_conversions,
        'avg_ctr': round(total_clicks / total_impressions * 100 if total_impressions > 0 else 0, 2),
        'avg_cpc': round(total_cost / total_clicks if total_clicks > 0 else 0, 2),
        'conversion_rate': round(total_conversions / total_clicks * 100 if total_clicks > 0 else 0, 2),
        'cost_per_conversion': round(total_cost / total_conversions if total_conversions > 0 else 0, 2)
    })

@app.route('/insights/campaigns', methods=['GET'])
def get_campaign_insights():
    insights = []
    for campaign in mock_data['campaigns'][:5]:
        insights.append({
            'type': random.choice(['performance', 'trend', 'anomaly', 'opportunity']),
            'severity': random.choice(['low', 'medium', 'high']),
            'title': f"Insight for {campaign['campaign_name']}",
            'description': f"CTR is {'above' if campaign['ctr'] > 3 else 'below'} average. Consider {'expanding' if campaign['ctr'] > 3 else 'optimizing'} this campaign.",
            'campaign_id': campaign['campaign_id'],
            'metric': 'ctr',
            'value': campaign['ctr'],
            'timestamp': datetime.now().isoformat()
        })
    return jsonify(insights)

@app.route('/alerts', methods=['GET'])
def get_alerts():
    return jsonify([
        {
            'alert_id': f'A{i:03d}',
            'type': random.choice(['performance_drop', 'budget_exceeded', 'low_quality_score']),
            'severity': random.choice(['low', 'medium', 'high', 'critical']),
            'message': f'Alert {i}: Performance issue detected',
            'timestamp': datetime.now().isoformat()
        }
        for i in range(1, 6)
    ])

@app.route('/ad_groups', methods=['GET'])
@app.route('/adgroups', methods=['GET'])
def get_ad_groups():
    ad_group_names = [
        'Brand Keywords - Exact',
        'Competitor Terms',
        'Product Categories',
        'Long-tail Keywords',
        'Location-based Terms',
        'Seasonal Offers',
        'Mobile Users',
        'Desktop Users',
        'Remarketing List',
        'Similar Audiences',
        'Custom Intent',
        'In-Market Audiences',
        'Shopping Ads',
        'Dynamic Search Ads',
        'Video Campaign'
    ]
    return jsonify([
        {
            'ad_group_id': f'AG{i:03d}',
            'ad_group_name': ad_group_names[i-1],
            'campaign_id': f'C{(i % 10) + 1:03d}',
            'status': random.choice(['ENABLED', 'PAUSED']),
            'impressions': random.randint(500, 15000),
            'clicks': random.randint(20, 800),
            'cost': round(random.uniform(50, 1500), 2),
            'conversions': random.randint(2, 100)
        }
        for i in range(1, 16)
    ])

@app.route('/search_terms', methods=['GET'])
@app.route('/search-terms', methods=['GET'])
def get_search_terms():
    search_terms = [
        'buy digital marketing services online',
        'best seo company near me',
        'how to improve google ads performance',
        'social media marketing tips',
        'email marketing software comparison',
        'marketing automation for small business',
        'ppc management services pricing',
        'facebook ads vs google ads',
        'instagram marketing strategy 2024',
        'content marketing examples',
        'lead generation techniques',
        'conversion rate optimization tools',
        'landing page best practices',
        'marketing analytics dashboard',
        'brand awareness campaign ideas',
        'customer acquisition cost calculator',
        'influencer marketing platform',
        'affiliate marketing for beginners',
        'youtube advertising costs',
        'linkedin ads targeting options',
        'marketing budget template',
        'digital marketing trends 2024',
        'seo keyword research tools',
        'google ads quality score',
        'marketing roi calculator'
    ]
    return jsonify([
        {
            'search_term': search_terms[i-1],
            'impressions': random.randint(100, 5000),
            'clicks': random.randint(5, 200),
            'cost': round(random.uniform(10, 500), 2),
            'conversions': random.randint(0, 20)
        }
        for i in range(1, 26)
    ])

@app.route('/ml_features', methods=['GET'])
def get_ml_features_data():
    return jsonify({
        'features': ['clicks', 'impressions', 'cost', 'position', 'quality_score'],
        'importance': [0.25, 0.20, 0.18, 0.22, 0.15],
        'correlation_matrix': [
            [1.0, 0.8, 0.6, -0.3, 0.4],
            [0.8, 1.0, 0.7, -0.2, 0.3],
            [0.6, 0.7, 1.0, -0.1, 0.2],
            [-0.3, -0.2, -0.1, 1.0, -0.5],
            [0.4, 0.3, 0.2, -0.5, 1.0]
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/metrics/adgroups', methods=['GET'])
def get_adgroup_metrics():
    adgroups = get_ad_groups().get_json()
    total_impressions = sum(ag['impressions'] for ag in adgroups)
    total_clicks = sum(ag['clicks'] for ag in adgroups)
    total_cost = sum(ag['cost'] for ag in adgroups)
    return jsonify({
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_cost': round(total_cost, 2),
        'avg_ctr': round(total_clicks / total_impressions * 100 if total_impressions > 0 else 0, 2)
    })

@app.route('/metrics/keywords', methods=['GET'])
def get_keyword_metrics():
    keywords = mock_data['keywords']
    total_impressions = sum(k['impressions'] for k in keywords)
    total_clicks = sum(k['clicks'] for k in keywords)
    total_cost = sum(k['cost'] for k in keywords)
    avg_quality_score = sum(k['quality_score'] for k in keywords) / len(keywords) if keywords else 0
    return jsonify({
        'total_keywords': len(keywords),
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_cost': round(total_cost, 2),
        'avg_quality_score': round(avg_quality_score, 1),
        'avg_cpc': round(total_cost / total_clicks if total_clicks > 0 else 0, 2)
    })

@app.route('/metrics/search_terms', methods=['GET'])
@app.route('/metrics/search-terms', methods=['GET'])
def get_search_term_metrics():
    search_terms = get_search_terms().get_json()
    total_impressions = sum(st['impressions'] for st in search_terms)
    total_clicks = sum(st['clicks'] for st in search_terms)
    total_cost = sum(st['cost'] for st in search_terms)
    return jsonify({
        'total_search_terms': len(search_terms),
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_cost': round(total_cost, 2),
        'avg_ctr': round(total_clicks / total_impressions * 100 if total_impressions > 0 else 0, 2)
    })

@app.route('/insights/keywords', methods=['GET'])
def get_keyword_insights():
    insights = []
    for keyword in mock_data['keywords'][:5]:
        insights.append({
            'type': random.choice(['performance', 'opportunity', 'warning']),
            'severity': random.choice(['low', 'medium', 'high']),
            'title': f"Insight for {keyword['keyword_text']}",
            'description': f"Quality score is {keyword['quality_score']}/10. {'Good performance' if keyword['quality_score'] > 7 else 'Consider optimization'}.",
            'keyword_id': keyword['keyword_id'],
            'metric': 'quality_score',
            'value': keyword['quality_score'],
            'timestamp': datetime.now().isoformat()
        })
    return jsonify(insights)

@app.route('/insights/anomalies', methods=['GET'])
def get_anomalies():
    anomalies = []
    for i in range(1, 6):
        anomalies.append({
            'anomaly_id': f'AN{i:03d}',
            'entity_type': random.choice(['campaign', 'keyword', 'ad_group']),
            'entity_id': f'E{i:03d}',
            'metric': random.choice(['ctr', 'cpc', 'conversions', 'impressions']),
            'expected_value': round(random.uniform(100, 1000), 2),
            'actual_value': round(random.uniform(50, 1500), 2),
            'deviation_percentage': round(random.uniform(-50, 100), 2),
            'severity': random.choice(['low', 'medium', 'high']),
            'detected_at': datetime.now().isoformat()
        })
    return jsonify(anomalies)

@app.route('/insights/summary', methods=['GET'])
def get_insights_summary():
    return jsonify({
        'total_insights': random.randint(20, 50),
        'high_priority': random.randint(3, 10),
        'medium_priority': random.randint(5, 15),
        'low_priority': random.randint(10, 25),
        'top_opportunities': [
            {'description': 'Increase budget for high-performing campaigns', 'impact': 'high'},
            {'description': 'Optimize keywords with low quality scores', 'impact': 'medium'},
            {'description': 'Add negative keywords to reduce waste', 'impact': 'medium'}
        ],
        'key_metrics': {
            'overall_health_score': random.randint(60, 95),
            'optimization_potential': random.randint(20, 60),
            'risk_score': random.randint(10, 40)
        }
    })

@app.route('/optimization/budget', methods=['GET'])
def get_budget_optimization():
    recommendations = []
    for campaign in mock_data['campaigns'][:5]:
        recommendations.append({
            'campaign_id': campaign['campaign_id'],
            'campaign_name': campaign['campaign_name'],
            'current_budget': round(random.uniform(500, 5000), 2),
            'recommended_budget': round(random.uniform(600, 6000), 2),
            'expected_impact': {
                'impressions_change': round(random.uniform(-20, 50), 1),
                'clicks_change': round(random.uniform(-10, 40), 1),
                'conversions_change': round(random.uniform(-5, 30), 1)
            },
            'reason': random.choice([
                'High performing campaign with budget constraint',
                'Opportunity to scale successful campaign',
                'Reduce budget for underperforming campaign'
            ])
        })
    return jsonify(recommendations)

@app.route('/optimization/keywords', methods=['GET'])
def get_keyword_optimization():
    recommendations = []
    actions = ['pause', 'increase_bid', 'decrease_bid', 'change_match_type', 'add_negative']
    for keyword in mock_data['keywords'][:8]:
        recommendations.append({
            'keyword_id': keyword['keyword_id'],
            'keyword_text': keyword['keyword_text'],
            'action': random.choice(actions),
            'current_bid': round(random.uniform(0.5, 3), 2),
            'recommended_bid': round(random.uniform(0.4, 3.5), 2),
            'expected_impact': round(random.uniform(-10, 30), 1),
            'confidence': round(random.uniform(60, 95), 1),
            'reason': f"Based on quality score of {keyword['quality_score']} and CTR of {keyword['ctr']}%"
        })
    return jsonify(recommendations)

@app.route('/optimization/simulate', methods=['POST'])
def run_simulation():
    # Mock simulation results
    return jsonify({
        'simulation_id': f'SIM{random.randint(1000, 9999)}',
        'status': 'completed',
        'results': {
            'baseline': {
                'impressions': random.randint(10000, 50000),
                'clicks': random.randint(500, 2500),
                'cost': round(random.uniform(1000, 10000), 2),
                'conversions': random.randint(50, 500)
            },
            'optimized': {
                'impressions': random.randint(12000, 60000),
                'clicks': random.randint(600, 3000),
                'cost': round(random.uniform(900, 9500), 2),
                'conversions': random.randint(60, 600)
            },
            'improvement_percentage': round(random.uniform(5, 35), 1)
        },
        'recommendations': [
            'Apply recommended budget allocations',
            'Implement keyword bid adjustments',
            'Add suggested negative keywords'
        ]
    })

@app.route('/forecast/ctr', methods=['GET'])
def get_ctr_forecast():
    days = int(request.args.get('days', 30))
    forecast_data = []
    base_ctr = 2.5
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        ctr = base_ctr + random.uniform(-0.5, 0.8) + (i * 0.01)
        forecast_data.append({
            'date': date,
            'predicted_ctr': round(ctr, 2),
            'lower_bound': round(ctr - 0.3, 2),
            'upper_bound': round(ctr + 0.3, 2)
        })
    return jsonify({
        'forecast_period': days,
        'data': forecast_data,
        'avg_predicted_ctr': round(sum(d['predicted_ctr'] for d in forecast_data) / len(forecast_data), 2),
        'confidence': 85
    })

@app.route('/forecast/spend', methods=['GET'])
def get_spend_forecast():
    days = int(request.args.get('days', 30))
    forecast_data = []
    base_spend = 1000
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        spend = base_spend + random.uniform(-200, 300) + (i * 10)
        forecast_data.append({
            'date': date,
            'predicted_spend': round(spend, 2),
            'lower_bound': round(spend * 0.9, 2),
            'upper_bound': round(spend * 1.1, 2)
        })
    return jsonify({
        'forecast_period': days,
        'data': forecast_data,
        'total_predicted_spend': round(sum(d['predicted_spend'] for d in forecast_data), 2),
        'confidence': 82
    })

@app.route('/forecast/scenario', methods=['POST'])
def run_scenario():
    return jsonify({
        'scenario_id': f'SC{random.randint(1000, 9999)}',
        'status': 'completed',
        'scenarios': [
            {
                'name': 'Conservative',
                'total_spend': round(random.uniform(20000, 30000), 2),
                'expected_conversions': random.randint(200, 400),
                'expected_roi': round(random.uniform(1.5, 2.5), 2)
            },
            {
                'name': 'Moderate',
                'total_spend': round(random.uniform(30000, 45000), 2),
                'expected_conversions': random.randint(400, 700),
                'expected_roi': round(random.uniform(2.0, 3.5), 2)
            },
            {
                'name': 'Aggressive',
                'total_spend': round(random.uniform(45000, 60000), 2),
                'expected_conversions': random.randint(700, 1200),
                'expected_roi': round(random.uniform(2.5, 4.0), 2)
            }
        ],
        'recommended': 'Moderate'
    })

@app.route('/alerts/thresholds', methods=['GET'])
def get_thresholds():
    return jsonify([
        {
            'threshold_id': f'TH{i:03d}',
            'metric': random.choice(['ctr', 'cpc', 'spend', 'conversions']),
            'condition': random.choice(['above', 'below']),
            'value': round(random.uniform(0.5, 100), 2),
            'enabled': random.choice([True, False]),
            'alert_count': random.randint(0, 10),
            'last_triggered': (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat()
        }
        for i in range(1, 11)
    ])

@app.route('/alerts/thresholds/<threshold_id>', methods=['PUT'])
def update_threshold(threshold_id):
    return jsonify({
        'threshold_id': threshold_id,
        'status': 'updated',
        'message': 'Threshold updated successfully'
    })

@app.route('/ml/features', methods=['GET'])
def get_ml_features():
    return jsonify({
        'feature_importance': [
            {'feature': 'quality_score', 'importance': 0.28},
            {'feature': 'bid_amount', 'importance': 0.22},
            {'feature': 'ad_relevance', 'importance': 0.18},
            {'feature': 'landing_page_experience', 'importance': 0.15},
            {'feature': 'historical_ctr', 'importance': 0.12},
            {'feature': 'keyword_competition', 'importance': 0.05}
        ],
        'model_accuracy': 0.87,
        'last_trained': (datetime.now() - timedelta(days=2)).isoformat()
    })

@app.route('/ml/predictions', methods=['GET'])
def get_ml_predictions():
    predictions = []
    for i in range(1, 11):
        predictions.append({
            'entity_id': f'E{i:03d}',
            'entity_type': random.choice(['campaign', 'keyword', 'ad_group']),
            'prediction_type': random.choice(['conversion_rate', 'ctr', 'quality_score']),
            'current_value': round(random.uniform(1, 10), 2),
            'predicted_value': round(random.uniform(1.5, 12), 2),
            'confidence': round(random.uniform(70, 95), 1),
            'timeframe': '7_days'
        })
    return jsonify(predictions)

if __name__ == '__main__':
    from flask import request
    print("Starting MarketingIQ API Server on port 8001...")
    app.run(host='0.0.0.0', port=8001, debug=True)