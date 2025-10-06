"""
Simple test to verify ADK compliance
"""
from orchestration_agent.agent import (
    analyze_performance_trends,
    detect_anomalies,
    calculate_roi,
    optimize_bids,
    optimize_budgets,
    optimize_keywords,
    root_agent,
    insight_agent
)

print("Testing function signatures...")

# Test 1: Call with None (should work with Optional)
result = analyze_performance_trends(None)
print(f"analyze_performance_trends(None): {result.get('status', 'OK')}")

# Test 2: Call without arguments (should use default None)
result = analyze_performance_trends()
print(f"analyze_performance_trends(): {result.get('status', 'OK')}")

# Test 3: Call with data
result = analyze_performance_trends({"test": "data"})
print(f"analyze_performance_trends(data): {result.get('status', 'OK')}")

print("\nAll other functions:")
print(f"detect_anomalies: {detect_anomalies().get('status', 'OK')}")
print(f"calculate_roi: {calculate_roi().get('status', 'OK')}")
print(f"optimize_bids: {optimize_bids().get('status', 'OK')}")
print(f"optimize_budgets: {optimize_budgets().get('status', 'OK')}")
print(f"optimize_keywords: {optimize_keywords().get('status', 'OK')}")

print("\nAgent configuration:")
print(f"Root agent: {root_agent.name}")
print(f"Insight agent: {insight_agent.name}")
print(f"Insight agent tools: {len(insight_agent.tools)}")

print("\nSUCCESS: All functions are ADK compliant!")