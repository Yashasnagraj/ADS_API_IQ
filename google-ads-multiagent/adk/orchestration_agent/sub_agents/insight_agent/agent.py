"""
Insight Agent for Google Ads Multi-Agent System
"""
from typing import Dict, Any, List, Optional
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from data_agent.db_client import DatabaseClient
from data_agent.warehouse_client import WarehouseClient


class InsightAgent:
    """
    Agent responsible for analyzing data and generating insights
    """

    def __init__(self, data_agent=None, use_warehouse=True):
        """
        Initialize Insight Agent

        Args:
            data_agent: DataAgent instance for fetching data
            use_warehouse: Use new warehouse (default True)
        """
        self.data_agent = data_agent
        self.name = "InsightAgent"
        self.db_client = DatabaseClient()

        # Initialize warehouse client (new)
        self.use_warehouse = use_warehouse
        if use_warehouse:
            try:
                self.warehouse_client = WarehouseClient()
                logger.info("Insight Agent initialized with warehouse client")
            except Exception as e:
                logger.warning(f"Could not initialize warehouse client: {e}. Falling back to old DB.")
                self.use_warehouse = False
                self.warehouse_client = None
        else:
            self.warehouse_client = None

        # Performance thresholds
        self.thresholds = {
            'good_ctr': 2.0,  # 2% CTR
            'good_conversion_rate': 3.0,  # 3% conversion rate
            'good_roas': 4.0,  # 4x ROAS
            'high_cpc': 5.0,  # $5 CPC
            'low_quality_score': 5  # Quality score < 5
        }

    def analyze_campaign_performance(
        self,
        customer_id: str = None,
        date_range: str = "LAST_30_DAYS"
    ) -> Dict[str, Any]:
        """
        Analyze campaign performance and generate detailed report

        Args:
            customer_id: Customer ID (optional for API)
            date_range: Date range for analysis

        Returns:
            Campaign performance analysis report
        """
        try:
            # Fetch campaign data - use warehouse if available
            if self.use_warehouse and self.warehouse_client:
                # Convert customer_id to int if string
                cust_id = int(customer_id) if customer_id and customer_id.isdigit() else None
                campaigns_data = self.warehouse_client.fetch_campaigns(customer_id=cust_id)
                logger.info("Using warehouse for campaign analysis")
            else:
                campaigns_data = self.db_client.fetch_campaigns()
                logger.info("Using old DB for campaign analysis")

            if "error" in campaigns_data:
                return {
                    'error': campaigns_data['error'],
                    'report': None
                }

            campaigns = campaigns_data.get('campaigns', [])

            if not campaigns:
                return {
                    'report': {
                        'summary': 'No campaigns found',
                        'details': []
                    }
                }

            # Convert to DataFrame for analysis
            df = pd.DataFrame(campaigns)

            # Calculate overall metrics
            total_spend = df['cost'].sum()
            total_conversions = df['conversions'].sum()
            total_clicks = df['clicks'].sum()
            total_impressions = df['impressions'].sum()

            overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            overall_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            overall_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0

            # Identify top performers
            df['performance_score'] = (
                df['conversions'] * 0.4 +
                df['ctr'] * 0.3 +
                (1 / (df['cpc'] + 0.01)) * 0.3
            )

            top_campaigns = df.nlargest(5, 'performance_score')[
                ['name', 'conversions', 'ctr', 'cpc', 'roas']
            ].to_dict('records')

            # Identify underperformers
            underperformers = df[
                (df['ctr'] < self.thresholds['good_ctr']) |
                (df['conversion_rate'] < self.thresholds['good_conversion_rate']) |
                (df['cpc'] > self.thresholds['high_cpc'])
            ][['name', 'ctr', 'conversion_rate', 'cpc', 'cost']].to_dict('records')

            # Generate recommendations
            recommendations = []

            # CTR recommendations
            low_ctr_campaigns = df[df['ctr'] < self.thresholds['good_ctr']]
            if not low_ctr_campaigns.empty:
                for _, campaign in low_ctr_campaigns.iterrows():
                    recommendations.append({
                        'campaign': campaign['name'],
                        'issue': 'Low CTR',
                        'current_value': f"{campaign['ctr']:.2f}%",
                        'recommendation': 'Review ad copy and keywords for relevance',
                        'priority': 'high'
                    })

            # CPC recommendations
            high_cpc_campaigns = df[df['cpc'] > self.thresholds['high_cpc']]
            if not high_cpc_campaigns.empty:
                for _, campaign in high_cpc_campaigns.iterrows():
                    recommendations.append({
                        'campaign': campaign['name'],
                        'issue': 'High CPC',
                        'current_value': f"${campaign['cpc']:.2f}",
                        'recommendation': 'Consider lowering bids or improving quality score',
                        'priority': 'medium'
                    })

            # Conversion rate recommendations
            low_conv_campaigns = df[
                (df['clicks'] > 100) &
                (df['conversion_rate'] < self.thresholds['good_conversion_rate'])
            ]
            if not low_conv_campaigns.empty:
                for _, campaign in low_conv_campaigns.iterrows():
                    recommendations.append({
                        'campaign': campaign['name'],
                        'issue': 'Low conversion rate',
                        'current_value': f"{campaign['conversion_rate']:.2f}%",
                        'recommendation': 'Review landing page and targeting',
                        'priority': 'high'
                    })

            report = {
                'summary': {
                    'total_campaigns': len(campaigns),
                    'total_spend': round(total_spend, 2),
                    'total_conversions': int(total_conversions),
                    'overall_ctr': round(overall_ctr, 2),
                    'overall_conversion_rate': round(overall_conversion_rate, 2),
                    'overall_cpc': round(overall_cpc, 2),
                    'date_range': date_range
                },
                'top_performers': top_campaigns,
                'underperformers': underperformers,
                'recommendations': recommendations,
                'generated_at': datetime.now().isoformat()
            }

            logger.info(f"Generated campaign performance report with {len(recommendations)} recommendations")

            return {
                'report': report,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Error analyzing campaign performance: {str(e)}")
            return {
                'error': str(e),
                'report': None
            }

    def analyze_keyword_performance(
        self,
        customer_id: str = None,
        min_impressions: int = 100
    ) -> Dict[str, Any]:
        """
        Analyze keyword performance and generate report

        Args:
            customer_id: Customer ID (optional for API)
            min_impressions: Minimum impressions for analysis

        Returns:
            Keyword performance analysis report
        """
        try:
            # Fetch keyword data
            keywords_data = self.db_client.fetch_keywords()

            if "error" in keywords_data:
                return {
                    'error': keywords_data['error'],
                    'report': None
                }

            keywords = keywords_data.get('keywords', [])

            if not keywords:
                return {
                    'report': {
                        'summary': 'No keywords found',
                        'details': []
                    }
                }

            # Convert to DataFrame
            df = pd.DataFrame(keywords)

            # Filter by minimum impressions
            df = df[df.get('impressions', 0) >= min_impressions]

            if df.empty:
                return {
                    'report': {
                        'summary': f'No keywords with at least {min_impressions} impressions',
                        'details': []
                    }
                }

            # Categorize keywords
            high_performers = df[
                (df.get('quality_score', 0) >= 7) &
                (df.get('ctr', 0) >= self.thresholds['good_ctr']) &
                (df.get('conversion_rate', 0) >= self.thresholds['good_conversion_rate'])
            ]

            low_quality_keywords = df[
                df.get('quality_score', 0) < self.thresholds['low_quality_score']
            ]

            wasted_spend_keywords = df[
                (df.get('cost', 0) > 50) &
                (df.get('conversions', 0) == 0)
            ]

            # Generate optimization opportunities
            opportunities = []

            # Quality score improvements
            if not low_quality_keywords.empty:
                for _, keyword in low_quality_keywords.iterrows():
                    opportunities.append({
                        'keyword': keyword.get('text', 'Unknown'),
                        'opportunity': 'Improve quality score',
                        'current_qs': keyword.get('quality_score', 0),
                        'potential_savings': round(keyword.get('cost', 0) * 0.2, 2),  # 20% potential savings
                        'action': 'Review ad relevance and landing page'
                    })

            # Negative keyword candidates
            if not wasted_spend_keywords.empty:
                for _, keyword in wasted_spend_keywords.iterrows():
                    opportunities.append({
                        'keyword': keyword.get('text', 'Unknown'),
                        'opportunity': 'Add as negative',
                        'wasted_spend': round(keyword.get('cost', 0), 2),
                        'impressions': int(keyword.get('impressions', 0)),
                        'action': 'Consider adding as negative keyword'
                    })

            # Calculate summary metrics
            avg_quality_score = df.get('quality_score', pd.Series([0])).mean()
            total_wasted_spend = wasted_spend_keywords.get('cost', pd.Series([0])).sum()

            report = {
                'summary': {
                    'total_keywords': len(df),
                    'avg_quality_score': round(avg_quality_score, 1),
                    'high_performers_count': len(high_performers),
                    'low_quality_count': len(low_quality_keywords),
                    'total_wasted_spend': round(total_wasted_spend, 2)
                },
                'high_performers': high_performers.head(10).to_dict('records') if not high_performers.empty else [],
                'low_quality_keywords': low_quality_keywords.head(10).to_dict('records') if not low_quality_keywords.empty else [],
                'optimization_opportunities': opportunities[:20],  # Top 20 opportunities
                'generated_at': datetime.now().isoformat()
            }

            logger.info(f"Generated keyword performance report with {len(opportunities)} optimization opportunities")

            return {
                'report': report,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Error analyzing keyword performance: {str(e)}")
            return {
                'error': str(e),
                'report': None
            }

    def analyze_performance_trends(
        self,
        customer_id: str = None,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze performance trends over time

        Args:
            customer_id: Customer ID (required)
            lookback_days: Number of days to analyze

        Returns:
            Trend analysis report
        """
        try:
            # Validate customer_id
            if not customer_id:
                return {
                    'status': 'error',
                    'message': 'customer_id is required for trend analysis',
                    'trends': None
                }

            # Use warehouse if available
            if self.use_warehouse and self.warehouse_client:
                cust_id = int(customer_id) if customer_id and customer_id.isdigit() else None
                campaigns_data = self.warehouse_client.fetch_campaigns(customer_id=cust_id)
                logger.info(f"Using warehouse for trend analysis (customer {customer_id})")
            else:
                campaigns_data = self.db_client.fetch_campaigns()
                logger.info("Using old DB for trend analysis")

            if "error" in campaigns_data:
                return {
                    'error': campaigns_data['error'],
                    'trends': None
                }

            campaigns = campaigns_data.get('campaigns', [])

            if not campaigns:
                return {
                    'trends': {
                        'summary': 'No data available for trend analysis'
                    }
                }

            df = pd.DataFrame(campaigns)

            # Calculate trend indicators (simplified)
            current_performance = {
                'spend': df['cost'].sum(),
                'conversions': df['conversions'].sum(),
                'ctr': df['ctr'].mean(),
                'cpc': df['cpc'].mean()
            }

            # Simulate trend (in real implementation, would compare with historical data)
            trends = {
                'spend_trend': 'increasing' if current_performance['spend'] > 1000 else 'stable',
                'conversion_trend': 'improving' if current_performance['conversions'] > 100 else 'stable',
                'ctr_trend': 'improving' if current_performance['ctr'] > 2.0 else 'declining',
                'cpc_trend': 'increasing' if current_performance['cpc'] > 3.0 else 'stable'
            }

            # Generate insights
            insights = []

            if trends['spend_trend'] == 'increasing' and trends['conversion_trend'] != 'improving':
                insights.append({
                    'type': 'warning',
                    'message': 'Spend is increasing but conversions are not improving proportionally',
                    'recommendation': 'Review campaign targeting and optimization'
                })

            if trends['ctr_trend'] == 'declining':
                insights.append({
                    'type': 'alert',
                    'message': 'CTR is declining over time',
                    'recommendation': 'Refresh ad creatives and review keyword relevance'
                })

            if trends['cpc_trend'] == 'increasing':
                insights.append({
                    'type': 'info',
                    'message': 'CPC is trending upward',
                    'recommendation': 'Consider bid adjustments and quality score improvements'
                })

            report = {
                'period': f'Last {lookback_days} days',
                'current_metrics': current_performance,
                'trends': trends,
                'insights': insights,
                'generated_at': datetime.now().isoformat()
            }

            logger.info(f"Generated trend analysis with {len(insights)} insights")

            return {
                'trends': report,
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {
                'error': str(e),
                'trends': None
            }

    def detect_anomalies(
        self,
        customer_id: str = None,
        sensitivity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Detect anomalies in performance data

        Args:
            customer_id: Customer ID (required)
            sensitivity: Anomaly detection sensitivity (low/medium/high)

        Returns:
            Detected anomalies
        """
        try:
            # Validate customer_id
            if not customer_id:
                return {
                    'status': 'error',
                    'message': 'customer_id is required for anomaly detection',
                    'anomalies': []
                }

            # Use warehouse if available
            if self.use_warehouse and self.warehouse_client:
                cust_id = int(customer_id) if customer_id and customer_id.isdigit() else None
                campaigns_data = self.warehouse_client.fetch_campaigns(customer_id=cust_id)
                logger.info(f"Using warehouse for anomaly detection (customer {customer_id})")
            else:
                campaigns_data = self.db_client.fetch_campaigns()
                logger.info("Using old DB for anomaly detection")

            if "error" in campaigns_data:
                return {
                    'error': campaigns_data['error'],
                    'anomalies': []
                }

            campaigns = campaigns_data.get('campaigns', [])

            if not campaigns:
                return {
                    'anomalies': [],
                    'summary': 'No data available for anomaly detection'
                }

            df = pd.DataFrame(campaigns)

            # Define anomaly thresholds based on sensitivity
            thresholds = {
                'low': {'std_multiplier': 3, 'percentile': 95},
                'medium': {'std_multiplier': 2, 'percentile': 90},
                'high': {'std_multiplier': 1.5, 'percentile': 85}
            }[sensitivity]

            anomalies = []

            # Detect spend anomalies
            if 'cost' in df.columns:
                mean_spend = df['cost'].mean()
                std_spend = df['cost'].std()
                spend_threshold = mean_spend + (std_spend * thresholds['std_multiplier'])

                high_spend_campaigns = df[df['cost'] > spend_threshold]
                for _, campaign in high_spend_campaigns.iterrows():
                    anomalies.append({
                        'type': 'high_spend',
                        'entity': campaign['name'],
                        'value': round(campaign['cost'], 2),
                        'expected_max': round(spend_threshold, 2),
                        'severity': 'high' if campaign['cost'] > spend_threshold * 1.5 else 'medium',
                        'recommendation': 'Review campaign budget and performance'
                    })

            # Detect CTR anomalies
            if 'ctr' in df.columns:
                percentile_ctr = df['ctr'].quantile(thresholds['percentile'] / 100)
                low_ctr_campaigns = df[df['ctr'] < df['ctr'].quantile(0.1)]

                for _, campaign in low_ctr_campaigns.iterrows():
                    anomalies.append({
                        'type': 'low_ctr',
                        'entity': campaign['name'],
                        'value': round(campaign['ctr'], 2),
                        'expected_min': round(df['ctr'].quantile(0.25), 2),
                        'severity': 'low',
                        'recommendation': 'Review ad relevance and targeting'
                    })

            # Detect conversion anomalies
            if 'conversion_rate' in df.columns:
                zero_conv_high_spend = df[
                    (df['conversions'] == 0) &
                    (df['cost'] > df['cost'].quantile(0.5))
                ]

                for _, campaign in zero_conv_high_spend.iterrows():
                    anomalies.append({
                        'type': 'zero_conversions',
                        'entity': campaign['name'],
                        'spend': round(campaign['cost'], 2),
                        'clicks': int(campaign.get('clicks', 0)),
                        'severity': 'high',
                        'recommendation': 'Urgent review needed - high spend with no conversions'
                    })

            summary = {
                'total_anomalies': len(anomalies),
                'high_severity': len([a for a in anomalies if a.get('severity') == 'high']),
                'medium_severity': len([a for a in anomalies if a.get('severity') == 'medium']),
                'low_severity': len([a for a in anomalies if a.get('severity') == 'low']),
                'sensitivity': sensitivity
            }

            logger.info(f"Detected {len(anomalies)} anomalies with {sensitivity} sensitivity")

            return {
                'anomalies': anomalies,
                'summary': summary,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error detecting anomalies: {str(e)}")
            return {
                'error': str(e),
                'anomalies': []
            }

    def calculate_roi(
        self,
        customer_id: str = None,
        include_lifetime_value: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate ROI metrics across campaigns

        Args:
            customer_id: Customer ID (required)
            include_lifetime_value: Whether to include LTV in calculations

        Returns:
            ROI analysis
        """
        try:
            # Validate customer_id
            if not customer_id:
                return {
                    'status': 'error',
                    'message': 'customer_id is required for ROI calculation',
                    'roi_analysis': None
                }

            # Use warehouse if available
            if self.use_warehouse and self.warehouse_client:
                cust_id = int(customer_id) if customer_id and customer_id.isdigit() else None
                campaigns_data = self.warehouse_client.fetch_campaigns(customer_id=cust_id)
                logger.info(f"Using warehouse for ROI calculation (customer {customer_id})")
            else:
                campaigns_data = self.db_client.fetch_campaigns()
                logger.info("Using old DB for ROI calculation")

            if "error" in campaigns_data:
                return {
                    'error': campaigns_data['error'],
                    'roi_analysis': None
                }

            campaigns = campaigns_data.get('campaigns', [])

            if not campaigns:
                return {
                    'roi_analysis': {
                        'summary': 'No campaigns found for ROI calculation'
                    }
                }

            df = pd.DataFrame(campaigns)

            # Calculate ROI metrics
            total_spend = df['cost'].sum()
            total_revenue = df.get('conversion_value', df['conversions'] * 50).sum()  # Default $50 per conversion
            total_conversions = df['conversions'].sum()

            overall_roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
            overall_roas = (total_revenue / total_spend) if total_spend > 0 else 0

            # Campaign-level ROI
            campaign_roi = []
            for _, campaign in df.iterrows():
                spend = campaign['cost']
                revenue = campaign.get('conversion_value', campaign['conversions'] * 50)
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

            # Identify best and worst performers
            profitable_campaigns = [c for c in campaign_roi if c['profitability'] == 'profitable']
            unprofitable_campaigns = [c for c in campaign_roi if c['profitability'] == 'unprofitable']

            roi_analysis = {
                'overall': {
                    'total_spend': round(total_spend, 2),
                    'total_revenue': round(total_revenue, 2),
                    'total_conversions': int(total_conversions),
                    'roi_percentage': round(overall_roi, 2),
                    'roas': round(overall_roas, 2)
                },
                'campaign_roi': campaign_roi[:10],  # Top 10 campaigns
                'profitable_campaigns': len(profitable_campaigns),
                'unprofitable_campaigns': len(unprofitable_campaigns),
                'recommendations': []
            }

            # Generate recommendations
            if overall_roi < 0:
                roi_analysis['recommendations'].append({
                    'priority': 'critical',
                    'message': 'Overall campaigns are unprofitable',
                    'action': 'Review and pause underperforming campaigns immediately'
                })

            if len(unprofitable_campaigns) > len(profitable_campaigns):
                roi_analysis['recommendations'].append({
                    'priority': 'high',
                    'message': 'More unprofitable campaigns than profitable ones',
                    'action': 'Focus budget on top performing campaigns'
                })

            logger.info(f"Calculated ROI for {len(campaigns)} campaigns")

            return {
                'roi_analysis': roi_analysis,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            return {
                'error': str(e),
                'roi_analysis': None
            }