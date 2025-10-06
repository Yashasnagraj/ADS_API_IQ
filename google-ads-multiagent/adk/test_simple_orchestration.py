"""
Simple test to verify ADK orchestration works
"""

from google.adk.agents import Agent

# Create simple test agents
def get_test_data() -> str:
    """Simple function to test data retrieval"""
    return "Sample campaign data: 3 campaigns, 150 keywords, $5000 spend"

def analyze_test_data() -> str:
    """Simple function to test analysis"""
    return "Analysis: CTR is 2.5%, conversions are trending up 15%"

def optimize_test() -> str:
    """Simple function to test optimization"""
    return "Recommendations: Increase bids by 20% on top performers, pause 5 underperforming keywords"

# Create test agents
test_data_agent = Agent(
    name="TestDataAgent",
    model="gemini-2.0-flash",
    description="Test agent for data retrieval",
    instruction="You retrieve test data. Always respond quickly with sample data.",
    tools=[get_test_data]
)

test_insight_agent = Agent(
    name="TestInsightAgent",
    model="gemini-2.0-flash",
    description="Test agent for analysis",
    instruction="You analyze test data. Provide simple insights.",
    tools=[analyze_test_data]
)

test_optimization_agent = Agent(
    name="TestOptimizationAgent",
    model="gemini-2.0-flash",
    description="Test agent for optimization",
    instruction="You provide optimization recommendations.",
    tools=[optimize_test]
)

# Create test orchestrator
test_orchestrator = Agent(
    name="TestOrchestrator",
    model="gemini-2.0-flash",
    description="Simple test orchestrator for verifying multi-agent setup",
    instruction="""You coordinate test agents to verify the multi-agent system works.

    You have three test agents:
    1. TestDataAgent - Gets sample data
    2. TestInsightAgent - Analyzes data
    3. TestOptimizationAgent - Provides recommendations

    Based on user requests, delegate to the appropriate agent.
    For data requests -> TestDataAgent
    For analysis -> TestInsightAgent
    For optimization -> TestOptimizationAgent

    This is a test setup to verify orchestration works correctly.""",
    sub_agents=[test_data_agent, test_insight_agent, test_optimization_agent]
)

if __name__ == "__main__":
    print("Test orchestrator created successfully!")
    print("\nTo run this test orchestrator:")
    print("python -m adk run test_simple_orchestration:test_orchestrator --port 8000")
    print("\nThen test with queries like:")
    print("  - 'Get campaign data'")
    print("  - 'Analyze my performance'")
    print("  - 'How can I optimize?'")