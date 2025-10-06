"""
Tool Registry for InsightAgent - Enterprise-Grade Integration
Handles tool registration, query parsing, and data flow orchestration
"""
from typing import Dict, Any, List, Optional, Callable
from langchain.tools import Tool, tool
from loguru import logger
import pandas as pd
from datetime import datetime, timedelta
import json

from .performance_analyzer import PerformanceAnalyzer
from .trend_analyzer import TrendAnalyzer
from .roi_calculator import ROICalculator
from .competitor_analysis import CompetitorAnalysis
from .anomaly_detector import AnomalyDetector


class InsightToolRegistry:
    """
    Enterprise-grade tool registry for InsightAgent
    Manages all analysis tools with proper data validation and error handling
    """

    def __init__(self, data_agent=None):
        """
        Initialize tool registry with all analysis components

        Args:
            data_agent: DataAgent instance for fetching data
        """
        self.data_agent = data_agent

        # Initialize all tool components
        self.performance_analyzer = PerformanceAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.roi_calculator = ROICalculator()
        self.competitor_analysis = CompetitorAnalysis()
        self.anomaly_detector = AnomalyDetector()

        # Tool metadata for intelligent routing
        self.tool_metadata = {
            'performance': {
                'keywords': ['performance', 'campaign', 'metrics', 'kpi', 'results'],
                'data_requirements': ['campaigns', 'ad_groups', 'keywords']
            },
            'trends': {
                'keywords': ['trend', 'pattern', 'forecast', 'prediction', 'seasonality'],
                'data_requirements': ['time_series', 'historical_data']
            },
            'roi': {
                'keywords': ['roi', 'roas', 'profit', 'revenue', 'cost', 'investment'],
                'data_requirements': ['conversions', 'costs', 'revenue']
            },
            'competitor': {
                'keywords': ['competitor', 'auction', 'share', 'benchmark', 'market'],
                'data_requirements': ['auction_insights', 'impression_share']
            },
            'anomaly': {
                'keywords': ['anomaly', 'unusual', 'outlier', 'spike', 'drop', 'alert'],
                'data_requirements': ['metrics', 'thresholds']
            }
        }

        logger.info("InsightToolRegistry initialized with all analysis components")

    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse user query to determine intent and required tools

        Args:
            query: User query string

        Returns:
            Parsed query with intent and parameters
        """
        query_lower = query.lower()

        # Determine primary intent
        intents = []
        for tool_name, metadata in self.tool_metadata.items():
            if any(keyword in query_lower for keyword in metadata['keywords']):
                intents.append(tool_name)

        # Extract parameters
        parameters = {
            'date_range': self._extract_date_range(query),
            'metrics': self._extract_metrics(query),
            'entities': self._extract_entities(query),
            'thresholds': self._extract_thresholds(query),
            'comparison_type': self._extract_comparison_type(query)
        }

        return {
            'original_query': query,
            'intents': intents or ['performance'],  # Default to performance
            'parameters': parameters,
            'timestamp': datetime.now().isoformat()
        }

    def _extract_date_range(self, query: str) -> str:
        """Extract date range from query"""
        query_lower = query.lower()

        if 'today' in query_lower:
            return 'TODAY'
        elif 'yesterday' in query_lower:
            return 'YESTERDAY'
        elif 'last week' in query_lower or 'past week' in query_lower:
            return 'LAST_7_DAYS'
        elif 'last month' in query_lower or 'past month' in query_lower:
            return 'LAST_30_DAYS'
        elif 'last quarter' in query_lower:
            return 'LAST_90_DAYS'
        elif 'last year' in query_lower:
            return 'LAST_365_DAYS'
        else:
            return 'LAST_30_DAYS'  # Default

    def _extract_metrics(self, query: str) -> List[str]:
        """Extract specific metrics from query"""
        query_lower = query.lower()
        metrics = []

        metric_keywords = {
            'impressions': ['impression', 'views', 'reach'],
            'clicks': ['click', 'traffic'],
            'conversions': ['conversion', 'sales', 'leads'],
            'cost': ['cost', 'spend', 'budget'],
            'ctr': ['ctr', 'click rate', 'click-through'],
            'cpc': ['cpc', 'cost per click'],
            'conversion_rate': ['conversion rate', 'cvr'],
            'roas': ['roas', 'return on ad'],
            'roi': ['roi', 'return on investment']
        }

        for metric, keywords in metric_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                metrics.append(metric)

        return metrics or ['impressions', 'clicks', 'conversions', 'cost', 'ctr', 'cpc']

    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entity names (campaigns, ad groups, keywords) from query"""
        entities = {
            'campaigns': [],
            'ad_groups': [],
            'keywords': []
        }

        # Look for quoted strings as potential entity names
        import re
        quoted = re.findall(r'"([^"]*)"', query)
        if quoted:
            # Heuristic: assume these are campaign names unless specified otherwise
            entities['campaigns'] = quoted

        return entities

    def _extract_thresholds(self, query: str) -> Dict[str, float]:
        """Extract performance thresholds from query"""
        thresholds = {}

        # Extract numeric values with context
        import re

        # Look for patterns like "CTR above 2%" or "CPC below $5"
        ctr_pattern = r'ctr\s*(?:above|over|>\s*)(\d+(?:\.\d+)?)\s*%'
        cpc_pattern = r'cpc\s*(?:below|under|<\s*)\$?(\d+(?:\.\d+)?)'
        roas_pattern = r'roas\s*(?:above|over|>\s*)(\d+(?:\.\d+)?)'

        query_lower = query.lower()

        ctr_match = re.search(ctr_pattern, query_lower)
        if ctr_match:
            thresholds['min_ctr'] = float(ctr_match.group(1))

        cpc_match = re.search(cpc_pattern, query_lower)
        if cpc_match:
            thresholds['max_cpc'] = float(cpc_match.group(1))

        roas_match = re.search(roas_pattern, query_lower)
        if roas_match:
            thresholds['min_roas'] = float(roas_match.group(1))

        return thresholds

    def _extract_comparison_type(self, query: str) -> str:
        """Extract comparison type from query"""
        query_lower = query.lower()

        if 'compare' in query_lower or 'vs' in query_lower:
            if 'last' in query_lower:
                return 'period_over_period'
            elif 'competitor' in query_lower:
                return 'competitive'
            else:
                return 'baseline'

        return 'none'

    def fetch_required_data(
        self,
        data_requirements: List[str],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fetch all required data for analysis

        Args:
            data_requirements: List of required data types
            parameters: Query parameters

        Returns:
            Dictionary containing all required data
        """
        if not self.data_agent:
            logger.warning("No data agent available, using mock data")
            return self._get_mock_data(data_requirements)

        data = {}
        date_range = parameters.get('date_range', 'LAST_30_DAYS')

        try:
            # Fetch data based on requirements
            if 'campaigns' in data_requirements:
                data['campaigns'] = self.data_agent.fetch_campaign_data(
                    date_range=date_range
                )

            if 'ad_groups' in data_requirements:
                data['ad_groups'] = self.data_agent.fetch_ad_group_data(
                    date_range=date_range
                )

            if 'keywords' in data_requirements:
                data['keywords'] = self.data_agent.fetch_keyword_data(
                    date_range=date_range
                )

            if 'time_series' in data_requirements or 'historical_data' in data_requirements:
                data['time_series'] = self.data_agent.fetch_time_series_data(
                    date_range=date_range,
                    metrics=parameters.get('metrics', [])
                )

            if 'auction_insights' in data_requirements:
                data['auction_insights'] = self.data_agent.fetch_auction_insights(
                    date_range=date_range
                )

            if 'impression_share' in data_requirements:
                data['impression_share'] = self.data_agent.fetch_impression_share(
                    date_range=date_range
                )

            if 'conversions' in data_requirements or 'revenue' in data_requirements:
                data['conversion_data'] = self.data_agent.fetch_conversion_data(
                    date_range=date_range
                )

            logger.info(f"Successfully fetched {len(data)} data types")

        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            # Return mock data on error for demo purposes
            return self._get_mock_data(data_requirements)

        return data

    def _get_mock_data(self, data_requirements: List[str]) -> Dict[str, Any]:
        """
        Generate mock data for testing and demos

        Args:
            data_requirements: List of required data types

        Returns:
            Mock data dictionary
        """
        import random
        from datetime import datetime, timedelta

        mock_data = {}

        # Generate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        dates = pd.date_range(start_date, end_date, freq='D')

        if 'campaigns' in data_requirements:
            mock_data['campaigns'] = [
                {
                    'id': f'campaign_{i}',
                    'name': f'Campaign {i}',
                    'status': 'ENABLED',
                    'impressions': random.randint(10000, 100000),
                    'clicks': random.randint(100, 5000),
                    'conversions': random.randint(10, 500),
                    'cost': round(random.uniform(100, 5000), 2),
                    'ctr': round(random.uniform(0.5, 5.0), 2),
                    'cpc': round(random.uniform(0.5, 10.0), 2),
                    'conversion_rate': round(random.uniform(1.0, 10.0), 2),
                    'roas': round(random.uniform(1.0, 10.0), 2)
                }
                for i in range(1, 11)
            ]

        if 'time_series' in data_requirements or 'historical_data' in data_requirements:
            time_series_data = []
            for date in dates:
                time_series_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'impressions': random.randint(5000, 50000),
                    'clicks': random.randint(50, 2000),
                    'conversions': random.randint(5, 200),
                    'cost': round(random.uniform(50, 2000), 2),
                    'ctr': round(random.uniform(0.5, 5.0), 2),
                    'conversion_rate': round(random.uniform(1.0, 10.0), 2)
                })
            mock_data['time_series'] = time_series_data

        if 'keywords' in data_requirements:
            mock_data['keywords'] = [
                {
                    'id': f'keyword_{i}',
                    'text': f'keyword {i}',
                    'match_type': random.choice(['EXACT', 'PHRASE', 'BROAD']),
                    'quality_score': random.randint(1, 10),
                    'impressions': random.randint(1000, 50000),
                    'clicks': random.randint(10, 1000),
                    'conversions': random.randint(0, 100),
                    'cost': round(random.uniform(10, 1000), 2),
                    'ctr': round(random.uniform(0.1, 10.0), 2),
                    'cpc': round(random.uniform(0.1, 20.0), 2),
                    'conversion_rate': round(random.uniform(0, 15.0), 2)
                }
                for i in range(1, 51)
            ]

        if 'auction_insights' in data_requirements:
            mock_data['auction_insights'] = [
                {
                    'domain': f'competitor{i}.com',
                    'impression_share': round(random.uniform(5, 30), 2),
                    'overlap_rate': round(random.uniform(10, 70), 2),
                    'outranking_share': round(random.uniform(20, 80), 2),
                    'top_of_page_rate': round(random.uniform(30, 90), 2),
                    'absolute_top_of_page_rate': round(random.uniform(10, 60), 2)
                }
                for i in range(1, 6)
            ]

        logger.info(f"Generated mock data for {len(mock_data)} data types")
        return mock_data

    @tool
    def analyze_performance(
        self,
        query: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main performance analysis tool

        Args:
            query: User query
            data: Optional pre-fetched data

        Returns:
            Performance analysis results
        """
        try:
            # Parse query
            parsed = self.parse_query(query)

            # Fetch data if not provided
            if not data:
                data = self.fetch_required_data(
                    self.tool_metadata['performance']['data_requirements'],
                    parsed['parameters']
                )

            # Validate data
            if not data or 'error' in data:
                return {
                    'status': 'error',
                    'message': 'Failed to fetch required data',
                    'query': query
                }

            # Perform analysis
            campaign_data = data.get('campaigns', [])
            if not campaign_data:
                return {
                    'status': 'no_data',
                    'message': 'No campaign data available',
                    'query': query
                }

            # Use performance analyzer
            result = self.performance_analyzer.analyze_campaign_performance(
                campaign_data=campaign_data[0] if len(campaign_data) == 1 else {'campaigns': campaign_data},
                performance_threshold=parsed['parameters'].get('thresholds')
            )

            result['query_context'] = parsed
            return result

        except Exception as e:
            logger.error(f"Error in performance analysis: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'query': query
            }

    @tool
    def analyze_trends(
        self,
        query: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trend analysis tool

        Args:
            query: User query
            data: Optional pre-fetched data

        Returns:
            Trend analysis results
        """
        try:
            # Parse query
            parsed = self.parse_query(query)

            # Fetch data if not provided
            if not data:
                data = self.fetch_required_data(
                    self.tool_metadata['trends']['data_requirements'],
                    parsed['parameters']
                )

            # Validate data
            if not data or 'error' in data:
                return {
                    'status': 'error',
                    'message': 'Failed to fetch required data',
                    'query': query
                }

            # Perform trend analysis
            time_series_data = data.get('time_series', [])
            if not time_series_data:
                return {
                    'status': 'no_data',
                    'message': 'No time series data available',
                    'query': query
                }

            # Use trend analyzer
            result = self.trend_analyzer.analyze_performance_trends(
                performance_data=time_series_data,
                metrics=parsed['parameters'].get('metrics'),
                period='daily'
            )

            result['query_context'] = parsed
            return result

        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'query': query
            }

    @tool
    def calculate_roi(
        self,
        query: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        ROI calculation tool

        Args:
            query: User query
            data: Optional pre-fetched data

        Returns:
            ROI analysis results
        """
        try:
            # Parse query
            parsed = self.parse_query(query)

            # Fetch data if not provided
            if not data:
                data = self.fetch_required_data(
                    self.tool_metadata['roi']['data_requirements'],
                    parsed['parameters']
                )

            # Validate data
            if not data or 'error' in data:
                return {
                    'status': 'error',
                    'message': 'Failed to fetch required data',
                    'query': query
                }

            # Perform ROI calculation
            campaign_data = data.get('campaigns', [])
            conversion_data = data.get('conversion_data', [])

            if not campaign_data:
                return {
                    'status': 'no_data',
                    'message': 'No campaign data available for ROI calculation',
                    'query': query
                }

            # Use ROI calculator
            result = self.roi_calculator.calculate_campaign_roi(
                campaign_data=campaign_data,
                conversion_value=50.0  # Default conversion value
            )

            result['query_context'] = parsed
            return result

        except Exception as e:
            logger.error(f"Error in ROI calculation: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'query': query
            }

    @tool
    def analyze_competitors(
        self,
        query: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Competitor analysis tool

        Args:
            query: User query
            data: Optional pre-fetched data

        Returns:
            Competitor analysis results
        """
        try:
            # Parse query
            parsed = self.parse_query(query)

            # Fetch data if not provided
            if not data:
                data = self.fetch_required_data(
                    self.tool_metadata['competitor']['data_requirements'],
                    parsed['parameters']
                )

            # Validate data
            if not data or 'error' in data:
                return {
                    'status': 'error',
                    'message': 'Failed to fetch required data',
                    'query': query
                }

            # Perform competitor analysis
            auction_data = data.get('auction_insights', [])

            if not auction_data:
                return {
                    'status': 'no_data',
                    'message': 'No auction insights data available',
                    'query': query
                }

            # Use competitor analysis
            result = self.competitor_analysis.analyze_auction_insights(
                auction_data=auction_data,
                competitor_domains=None  # Will analyze all competitors
            )

            result['query_context'] = parsed
            return result

        except Exception as e:
            logger.error(f"Error in competitor analysis: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'query': query
            }

    @tool
    def detect_anomalies(
        self,
        query: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Anomaly detection tool

        Args:
            query: User query
            data: Optional pre-fetched data

        Returns:
            Detected anomalies
        """
        try:
            # Parse query
            parsed = self.parse_query(query)

            # Fetch data if not provided
            if not data:
                data = self.fetch_required_data(
                    self.tool_metadata['anomaly']['data_requirements'],
                    parsed['parameters']
                )

            # Validate data
            if not data or 'error' in data:
                return {
                    'status': 'error',
                    'message': 'Failed to fetch required data',
                    'query': query
                }

            # Perform anomaly detection
            time_series_data = data.get('time_series', [])

            if not time_series_data:
                campaign_data = data.get('campaigns', [])
                if campaign_data:
                    # Convert campaign data to time series format
                    time_series_data = [
                        {
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            **campaign
                        }
                        for campaign in campaign_data
                    ]

            if not time_series_data:
                return {
                    'status': 'no_data',
                    'message': 'No data available for anomaly detection',
                    'query': query
                }

            # Use anomaly detector
            result = self.anomaly_detector.detect_performance_anomalies(
                performance_data=time_series_data,
                sensitivity='medium'
            )

            result['query_context'] = parsed
            return result

        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'query': query
            }

    def get_all_tools(self) -> List[Tool]:
        """
        Get all registered tools for LangChain

        Returns:
            List of LangChain Tool objects
        """
        tools = [
            Tool(
                name="analyze_performance",
                func=lambda q: self.analyze_performance(q),
                description="Analyze campaign performance metrics and KPIs. Use for performance reviews, campaign analysis, and metric evaluation."
            ),
            Tool(
                name="analyze_trends",
                func=lambda q: self.analyze_trends(q),
                description="Analyze trends, patterns, and seasonality in data. Use for forecasting, trend detection, and pattern recognition."
            ),
            Tool(
                name="calculate_roi",
                func=lambda q: self.calculate_roi(q),
                description="Calculate ROI, ROAS, and profitability metrics. Use for investment analysis and financial performance."
            ),
            Tool(
                name="analyze_competitors",
                func=lambda q: self.analyze_competitors(q),
                description="Analyze competitor performance and market position. Use for auction insights and competitive intelligence."
            ),
            Tool(
                name="detect_anomalies",
                func=lambda q: self.detect_anomalies(q),
                description="Detect anomalies and unusual patterns. Use for alerts, outlier detection, and performance monitoring."
            )
        ]

        # Add specialized tools from each component
        tools.extend(self.performance_analyzer.get_tools())
        tools.extend(self.trend_analyzer.get_tools())
        tools.extend(self.roi_calculator.get_tools())
        tools.extend(self.competitor_analysis.get_tools())
        tools.extend(self.anomaly_detector.get_tools())

        logger.info(f"Registered {len(tools)} tools for InsightAgent")
        return tools

    def validate_tool_response(self, response: Dict[str, Any]) -> bool:
        """
        Validate tool response for quality assurance

        Args:
            response: Tool response

        Returns:
            True if valid, False otherwise
        """
        # Check for required fields
        if not response:
            return False

        if 'error' in response and response['error']:
            logger.error(f"Tool returned error: {response['error']}")
            return False

        # Check for data integrity
        if 'status' in response and response['status'] == 'error':
            return False

        # Validate data types
        if 'report' in response and not isinstance(response['report'], dict):
            return False

        return True

    def format_response_for_presentation(
        self,
        response: Dict[str, Any],
        format_type: str = 'detailed'
    ) -> str:
        """
        Format tool response for presentation

        Args:
            response: Tool response
            format_type: Format type (detailed, summary, executive)

        Returns:
            Formatted response string
        """
        if not self.validate_tool_response(response):
            return "Invalid response received from analysis tool."

        if format_type == 'executive':
            return self._format_executive_summary(response)
        elif format_type == 'summary':
            return self._format_summary(response)
        else:
            return self._format_detailed(response)

    def _format_executive_summary(self, response: Dict[str, Any]) -> str:
        """Format response as executive summary"""
        lines = []
        lines.append("=== EXECUTIVE SUMMARY ===\n")

        if 'summary' in response:
            for key, value in response['summary'].items():
                lines.append(f"  {key.replace('_', ' ').title()}: {value}")

        if 'recommendations' in response:
            lines.append("\nKey Recommendations:")
            for i, rec in enumerate(response['recommendations'][:3], 1):
                if isinstance(rec, dict):
                    lines.append(f"  {i}. {rec.get('recommendation', rec.get('message', str(rec)))}")
                else:
                    lines.append(f"  {i}. {rec}")

        return "\n".join(lines)

    def _format_summary(self, response: Dict[str, Any]) -> str:
        """Format response as summary"""
        lines = []
        lines.append("=== ANALYSIS SUMMARY ===\n")

        # Add main metrics
        if 'metrics' in response:
            lines.append("Key Metrics:")
            for metric, data in list(response['metrics'].items())[:5]:
                if isinstance(data, dict) and 'current_value' in data:
                    lines.append(f"  {metric}: {data['current_value']}")

        # Add insights
        if 'insights' in response:
            lines.append("\nInsights:")
            for insight in response['insights'][:5]:
                if isinstance(insight, str):
                    lines.append(f"  - {insight}")
                elif isinstance(insight, dict):
                    lines.append(f"  - {insight.get('message', str(insight))}")

        return "\n".join(lines)

    def _format_detailed(self, response: Dict[str, Any]) -> str:
        """Format response as detailed report"""
        import json
        return json.dumps(response, indent=2, default=str)


# Singleton instance for easy access
_tool_registry = None

def get_tool_registry(data_agent=None) -> InsightToolRegistry:
    """
    Get or create tool registry singleton

    Args:
        data_agent: Optional DataAgent instance

    Returns:
        InsightToolRegistry instance
    """
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = InsightToolRegistry(data_agent)
    return _tool_registry