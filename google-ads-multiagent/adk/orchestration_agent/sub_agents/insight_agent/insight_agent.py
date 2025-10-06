"""
Insight Agent for ADK - Google Ads Performance Analysis
"""
from typing import Dict, Any, List, Optional
from google.adk.agents import Agent
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Add parent directory to path for database client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_agent.db_client import DatabaseClient


class InsightAgent(Agent):
    """Agent responsible for analyzing campaign data and generating insights"""

    def __init__(self):
        super().__init__(
            name="InsightAgent",
            description="Analyzes Google Ads performance data and generates insights"
        )
        self.db_client = DatabaseClient()

        # Performance thresholds
        self.thresholds = {
            'good_ctr': 2.0,  # 2% CTR
            'good_conversion_rate': 3.0,  # 3% conversion rate
            'good_roas': 4.0,  # 4x ROAS
            'high_cpc': 5.0,  # $5 CPC
            'low_quality_score': 5  # Quality score < 5
        }

    def analyze_campaign_performance(self) -> Dict[str, Any]:
        """
        Analyze campaign performance and generate report

        Returns:
            Campaign performance analysis
        """
        try:
            # Fetch campaign data from database
            campaigns_data = self.db_client.fetch_campaigns()

            if "error" in campaigns_data:
                return {
                    'status': 'error',
                    'message': campaigns_data['error']
                }

            campaigns = campaigns_data.get('campaigns', [])

            if not campaigns:
                return {
                    'status': 'success',
                    'message': 'No campaigns found',
                    'report': {}
                }

            # Convert to DataFrame for analysis
            df = pd.DataFrame(campaigns)

            # Calculate overall metrics
            total_spend = df['cost'].sum() if 'cost' in df else 0
            total_conversions = df['conversions'].sum() if 'conversions' in df else 0
            total_clicks = df['clicks'].sum() if 'clicks' in df else 0
            total_impressions = df['impressions'].sum() if 'impressions' in df else 0

            overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            overall_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            overall_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0

            # Identify top performers
            top_campaigns = []
            if not df.empty and 'conversions' in df:
                top_df = df.nlargest(5, 'conversions')[['name', 'conversions', 'ctr', 'cpc', 'roas']]
                top_campaigns = top_df.to_dict('records')

            # Identify underperformers
            underperformers = []
            if not df.empty:
                low_performers = df[
                    (df.get('ctr', 0) < self.thresholds['good_ctr']) |
                    (df.get('cpc', 0) > self.thresholds['high_cpc'])
                ]
                if not low_performers.empty:
                    underperformers = low_performers[['name', 'ctr', 'cpc', 'cost']].head(5).to_dict('records')

            # Generate recommendations
            recommendations = []

            # Low CTR campaigns
            if not df.empty and 'ctr' in df:
                low_ctr = df[df['ctr'] < self.thresholds['good_ctr']]
                for _, campaign in low_ctr.iterrows():
                    recommendations.append({
                        'campaign': campaign['name'],
                        'issue': 'Low CTR',
                        'current_value': f"{campaign['ctr']:.2f}%",
                        'recommendation': 'Review ad copy and keywords'
                    })

            report = {
                'summary': {
                    'total_campaigns': len(campaigns),
                    'total_spend': round(total_spend, 2),
                    'total_conversions': int(total_conversions),
                    'overall_ctr': round(overall_ctr, 2),
                    'overall_conversion_rate': round(overall_conversion_rate, 2),
                    'overall_cpc': round(overall_cpc, 2)
                },
                'top_performers': top_campaigns[:5],
                'underperformers': underperformers[:5],
                'recommendations': recommendations[:10],
                'generated_at': datetime.now().isoformat()
            }

            return {
                'status': 'success',
                'report': report
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def analyze_keyword_performance(self) -> Dict[str, Any]:
        """
        Analyze keyword performance

        Returns:
            Keyword performance analysis
        """
        try:
            # Fetch keyword data
            keywords_data = self.db_client.fetch_keywords()

            if "error" in keywords_data:
                return {
                    'status': 'error',
                    'message': keywords_data['error']
                }

            keywords = keywords_data.get('keywords', [])

            if not keywords:
                return {
                    'status': 'success',
                    'message': 'No keywords found',
                    'report': {}
                }

            # Convert to DataFrame
            df = pd.DataFrame(keywords)

            # Filter by minimum impressions
            if 'impressions' in df:
                df = df[df['impressions'] >= 100]

            if df.empty:
                return {
                    'status': 'success',
                    'message': 'No keywords with sufficient data',
                    'report': {}
                }

            # Categorize keywords
            high_performers = []
            low_quality_keywords = []
            wasted_spend_keywords = []

            if not df.empty:
                # High performers
                if all(col in df for col in ['quality_score', 'ctr', 'conversion_rate']):
                    high_perf = df[
                        (df['quality_score'] >= 7) &
                        (df['ctr'] >= self.thresholds['good_ctr']) &
                        (df['conversion_rate'] >= self.thresholds['good_conversion_rate'])
                    ]
                    if not high_perf.empty:
                        high_performers = high_perf.head(10).to_dict('records')

                # Low quality score
                if 'quality_score' in df:
                    low_qs = df[df['quality_score'] < self.thresholds['low_quality_score']]
                    if not low_qs.empty:
                        low_quality_keywords = low_qs.head(10).to_dict('records')

                # Wasted spend
                if all(col in df for col in ['cost', 'conversions']):
                    wasted = df[(df['cost'] > 50) & (df['conversions'] == 0)]
                    if not wasted.empty:
                        wasted_spend_keywords = wasted.head(10).to_dict('records')

            # Calculate summary metrics
            avg_quality_score = df['quality_score'].mean() if 'quality_score' in df else 0
            total_wasted_spend = df[(df.get('cost', 0) > 50) & (df.get('conversions', 0) == 0)]['cost'].sum() if 'cost' in df else 0

            report = {
                'summary': {
                    'total_keywords': len(df),
                    'avg_quality_score': round(avg_quality_score, 1),
                    'high_performers_count': len(high_performers),
                    'low_quality_count': len(low_quality_keywords),
                    'total_wasted_spend': round(total_wasted_spend, 2)
                },
                'high_performers': high_performers,
                'low_quality_keywords': low_quality_keywords,
                'wasted_spend_keywords': wasted_spend_keywords,
                'generated_at': datetime.now().isoformat()
            }

            return {
                'status': 'success',
                'report': report
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def detect_anomalies(self) -> Dict[str, Any]:
        """
        Detect anomalies in campaign performance

        Returns:
            Detected anomalies
        """
        try:
            # Fetch campaign data
            campaigns_data = self.db_client.fetch_campaigns()

            if "error" in campaigns_data:
                return {
                    'status': 'error',
                    'message': campaigns_data['error']
                }

            campaigns = campaigns_data.get('campaigns', [])

            if not campaigns:
                return {
                    'status': 'success',
                    'anomalies': [],
                    'message': 'No campaigns found'
                }

            df = pd.DataFrame(campaigns)
            anomalies = []

            # Detect spend anomalies
            if 'cost' in df:
                mean_spend = df['cost'].mean()
                std_spend = df['cost'].std()
                spend_threshold = mean_spend + (std_spend * 2)  # 2 standard deviations

                high_spend = df[df['cost'] > spend_threshold]
                for _, campaign in high_spend.iterrows():
                    anomalies.append({
                        'type': 'high_spend',
                        'entity': campaign['name'],
                        'value': round(campaign['cost'], 2),
                        'expected_max': round(spend_threshold, 2),
                        'severity': 'high',
                        'recommendation': 'Review campaign budget'
                    })

            # Detect CTR anomalies
            if 'ctr' in df:
                low_ctr = df[df['ctr'] < df['ctr'].quantile(0.1)]
                for _, campaign in low_ctr.iterrows():
                    anomalies.append({
                        'type': 'low_ctr',
                        'entity': campaign['name'],
                        'value': round(campaign['ctr'], 2),
                        'expected_min': round(df['ctr'].quantile(0.25), 2),
                        'severity': 'medium',
                        'recommendation': 'Review ad relevance'
                    })

            # Detect conversion anomalies
            if all(col in df for col in ['conversions', 'cost', 'clicks']):
                zero_conv = df[(df['conversions'] == 0) & (df['cost'] > df['cost'].quantile(0.5))]
                for _, campaign in zero_conv.iterrows():
                    anomalies.append({
                        'type': 'zero_conversions',
                        'entity': campaign['name'],
                        'spend': round(campaign['cost'], 2),
                        'clicks': int(campaign['clicks']),
                        'severity': 'high',
                        'recommendation': 'Urgent review needed'
                    })

            return {
                'status': 'success',
                'anomalies': anomalies,
                'total_anomalies': len(anomalies),
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def calculate_roi(self) -> Dict[str, Any]:
        """
        Calculate ROI across campaigns

        Returns:
            ROI analysis
        """
        try:
            campaigns_data = self.db_client.fetch_campaigns()

            if "error" in campaigns_data:
                return {
                    'status': 'error',
                    'message': campaigns_data['error']
                }

            campaigns = campaigns_data.get('campaigns', [])

            if not campaigns:
                return {
                    'status': 'success',
                    'roi_analysis': {},
                    'message': 'No campaigns found'
                }

            df = pd.DataFrame(campaigns)

            # Calculate ROI metrics
            total_spend = df['cost'].sum() if 'cost' in df else 0
            total_conversions = df['conversions'].sum() if 'conversions' in df else 0

            # Assume $50 per conversion if no conversion value
            total_revenue = df.get('conversion_value', df.get('conversions', 0) * 50).sum()

            overall_roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
            overall_roas = (total_revenue / total_spend) if total_spend > 0 else 0

            # Campaign-level ROI
            campaign_roi = []
            for _, campaign in df.iterrows():
                spend = campaign.get('cost', 0)
                revenue = campaign.get('conversion_value', campaign.get('conversions', 0) * 50)
                roi = ((revenue - spend) / spend * 100) if spend > 0 else 0
                roas = (revenue / spend) if spend > 0 else 0

                campaign_roi.append({
                    'campaign': campaign['name'],
                    'spend': round(spend, 2),
                    'revenue': round(revenue, 2),
                    'roi_percentage': round(roi, 2),
                    'roas': round(roas, 2),
                    'profitability': 'profitable' if roi > 0 else 'unprofitable'
                })

            # Sort by ROI
            campaign_roi = sorted(campaign_roi, key=lambda x: x['roi_percentage'], reverse=True)

            roi_analysis = {
                'overall': {
                    'total_spend': round(total_spend, 2),
                    'total_revenue': round(total_revenue, 2),
                    'total_conversions': int(total_conversions),
                    'roi_percentage': round(overall_roi, 2),
                    'roas': round(overall_roas, 2)
                },
                'campaign_roi': campaign_roi[:10],
                'profitable_campaigns': len([c for c in campaign_roi if c['profitability'] == 'profitable']),
                'unprofitable_campaigns': len([c for c in campaign_roi if c['profitability'] == 'unprofitable'])
            }

            return {
                'status': 'success',
                'roi_analysis': roi_analysis,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }