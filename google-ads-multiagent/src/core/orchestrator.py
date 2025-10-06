"""
ADK-compatible Orchestrator Agent
Coordinates all sub-agents for comprehensive Google Ads management
"""

from google.adk import Agent
from typing import Dict, Any, List

# Define the orchestrator agent for ADK
orchestrator_agent = Agent(
    name="orchestrator",
    description="Master agent that coordinates Data, Insight, Optimization, and Forecasting agents",
    instructions="""You are the master orchestrator agent for Google Ads management.

    Your role is to:
    1. Coordinate data retrieval from the Data Agent
    2. Generate insights using the Insight Agent
    3. Provide optimizations through the Optimization Agent
    4. Create forecasts via the Forecasting Agent

    When a user makes a request, determine which agents to activate and in what sequence.

    Available analysis types:
    - Comprehensive: Use all agents for full analysis
    - Performance: Focus on data and insights
    - Optimization: Focus on improvement recommendations
    - Forecasting: Focus on predictions and scenarios

    Always provide structured, actionable recommendations based on the coordinated agent outputs.
    """,
    agents=[
        Agent(
            name="data_agent",
            description="Retrieves Google Ads campaign, ad group, keyword, and search term data",
            instructions="""You retrieve and process Google Ads data including:
            - Campaign performance metrics
            - Ad group statistics
            - Keyword performance
            - Search term reports
            - ML features for analysis

            Return structured data for other agents to analyze."""
        ),
        Agent(
            name="insight_agent",
            description="Analyzes performance data to generate insights and detect patterns",
            instructions="""You analyze Google Ads data to:
            - Identify performance trends
            - Detect anomalies and issues
            - Provide competitive analysis
            - Calculate ROI metrics
            - Generate actionable insights

            Focus on finding patterns and opportunities in the data."""
        ),
        Agent(
            name="optimization_agent",
            description="Provides optimization recommendations for campaigns",
            instructions="""You provide optimization recommendations for:
            - Bid strategies and adjustments
            - Budget allocation across campaigns
            - Campaign settings and structure
            - Keyword optimizations
            - Ad copy improvements

            All recommendations should be data-driven and actionable."""
        ),
        Agent(
            name="forecasting_agent",
            description="Predicts future performance and analyzes scenarios",
            instructions="""You forecast and predict:
            - Future campaign performance
            - Impact of budget changes
            - Scenario analysis (what-if)
            - Conversion predictions
            - Seasonal trends

            Use historical data to provide accurate predictions."""
        )
    ]
)