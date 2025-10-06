from typing import Dict, List, Any

ORCHESTRATOR_SYSTEM_PROMPT = """
You are the Orchestrator Agent for Google Ads Multi-Agent System.

Your role is to:
1. Coordinate between different specialized agents (Data, Insight, Optimization, Forecasting)
2. Manage workflow execution (sequential and parallel)
3. Aggregate and synthesize results from multiple agents
4. Ensure efficient task distribution and execution
5. Handle error recovery and fallback strategies

You have access to the following sub-agents:
- Data Agent: Retrieves campaign, ad group, keyword, and search term data
- Insight Agent: Analyzes performance, detects anomalies, identifies trends
- Optimization Agent: Provides bid, budget, and campaign optimization recommendations
- Forecasting Agent: Generates performance forecasts and scenario analyses

Analysis Types:
- Comprehensive: Full analysis using all agents
- Performance: Focus on current performance metrics and insights
- Optimization: Focus on optimization recommendations
- Forecasting: Focus on future predictions and scenarios

Workflow Execution:
- Sequential: Execute steps one after another, passing context
- Parallel: Execute multiple steps simultaneously for efficiency
"""

ANALYSIS_PROMPTS = {
    "comprehensive": """
    Perform a comprehensive analysis that includes:
    1. Current campaign and ad group performance data
    2. Deep insights including anomalies and trends
    3. Optimization recommendations for bids, budgets, and campaigns
    4. Future performance forecasts and scenario planning

    Synthesize all results into actionable recommendations.
    """,

    "performance": """
    Analyze current performance focusing on:
    1. Campaign and ad group metrics
    2. Performance insights and anomaly detection
    3. Trend analysis and patterns

    Highlight key performance indicators and areas of concern.
    """,

    "optimization": """
    Generate optimization recommendations based on:
    1. Current campaign performance data
    2. Bid optimization opportunities
    3. Budget reallocation suggestions
    4. Campaign structure improvements

    Prioritize recommendations by potential impact.
    """,

    "forecasting": """
    Create performance forecasts including:
    1. Performance projections for next periods
    2. Scenario analysis for different strategies
    3. Risk assessment and confidence intervals

    Provide clear recommendations for future planning.
    """
}

WORKFLOW_TEMPLATES = {
    "daily_analysis": {
        "type": "parallel",
        "steps": [
            {"agent": "data", "action": "get_campaign_performance"},
            {"agent": "insight", "action": "analyze_performance"},
            {"agent": "optimization", "action": "optimize_bids"}
        ]
    },

    "weekly_review": {
        "type": "sequential",
        "steps": [
            {"agent": "data", "action": "get_campaign_performance"},
            {"agent": "insight", "action": "analyze_trends"},
            {"agent": "optimization", "action": "optimize_budgets"},
            {"agent": "forecasting", "action": "forecast_performance"}
        ]
    },

    "emergency_response": {
        "type": "sequential",
        "steps": [
            {"agent": "insight", "action": "detect_anomalies"},
            {"agent": "data", "action": "get_detailed_metrics"},
            {"agent": "optimization", "action": "emergency_adjustments"}
        ]
    }
}

ERROR_RECOVERY_STRATEGIES = {
    "data_fetch_failed": "Use cached data if available, otherwise skip dependent analyses",
    "agent_timeout": "Retry with reduced scope or use fallback agent",
    "api_limit_exceeded": "Queue requests and implement exponential backoff",
    "invalid_response": "Validate and sanitize response, use default values if necessary"
}

def get_orchestration_prompt(task_type: str, context: Dict[str, Any]) -> str:
    base_prompt = ORCHESTRATOR_SYSTEM_PROMPT

    if task_type in ANALYSIS_PROMPTS:
        base_prompt += f"\n\nTask: {ANALYSIS_PROMPTS[task_type]}"

    if context.get("customer_id"):
        base_prompt += f"\n\nCustomer ID: {context['customer_id']}"

    if context.get("date_range"):
        base_prompt += f"\nDate Range: {context['date_range']}"

    if context.get("specific_campaigns"):
        base_prompt += f"\nFocus Campaigns: {', '.join(context['specific_campaigns'])}"

    return base_prompt

def get_workflow_template(workflow_name: str) -> Dict[str, Any]:
    return WORKFLOW_TEMPLATES.get(workflow_name, {
        "type": "sequential",
        "steps": []
    })

def get_error_strategy(error_type: str) -> str:
    return ERROR_RECOVERY_STRATEGIES.get(error_type, "Log error and continue with available data")