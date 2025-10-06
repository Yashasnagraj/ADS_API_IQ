# ADK Multi-Agent System - Setup Guide

## ✅ All Issues Have Been Fixed!

### Fixed Issues:
1. **Parameter Annotations**: All `Dict[str, Any] = None` changed to `Optional[Dict[str, Any]] = None`
2. **Context Variable Error**: Resolved by proper function signatures
3. **API Endpoints**: Updated to use port 8001 to avoid conflict with ADK server

## 🚀 How to Run the System

### Step 1: Start the API Server (Port 8001)
Open a terminal in the main directory and run:
```bash
cd C:\Users\yashr\Desktop\ADS_API
python start_api_8001.py
```

This will start the MarketingIQ API on port 8001 with all endpoints:
- `/campaigns` - Campaign data
- `/metrics/trends` - Performance trends
- `/keywords` - Keyword data
- `/search-terms` - Search terms
- And many more...

### Step 2: Start the ADK Server (Port 8000)
Open a second terminal and run:
```bash
cd C:\Users\yashr\Desktop\ADS_API\google-ads-multiagent\adk
google-adk run
```

This starts the ADK web interface on http://localhost:8000

### Step 3: Access the Web Interface
1. Open your browser to http://localhost:8000
2. You'll see the ADK interface
3. Start chatting with the orchestration agent!

## 📊 Available Commands

You can ask the agent things like:
- "Show me campaign performance"
- "Analyze trends in conversions"
- "Calculate ROI for all campaigns"
- "Detect any anomalies"
- "Optimize my bid strategy"
- "Forecast next month's performance"
- "Give me insights on my campaigns"

## 🔧 Architecture

```
ADK Web Interface (Port 8000)
    ↓
OrchestrationAgent (Coordinator)
    ├── DataAgent → API Server (Port 8001)
    ├── InsightAgent → Analyzes data
    ├── OptimizationAgent → Provides recommendations
    └── ForecastingAgent → Predicts future performance
```

## ✅ What Was Fixed

### 1. Parameter Type Annotations
All functions now use proper Optional types:
```python
# Before (ERROR):
def analyze_performance_trends(data: Dict[str, Any] = None)

# After (FIXED):
def analyze_performance_trends(data: Optional[Dict[str, Any]] = None)
```

### 2. API Port Separation
- ADK Server: Port 8000
- API Server: Port 8001
- No more conflicts!

### 3. All Tools Working
- ✅ DataAgent: 6 tools
- ✅ InsightAgent: 4 tools
- ✅ OptimizationAgent: 3 tools
- ✅ ForecastingAgent: 2 tools

## 🎯 Testing

To test if everything is working:

1. **Test API endpoints**:
```bash
curl http://localhost:8001/campaigns
curl http://localhost:8001/metrics/summary
```

2. **Test through ADK**:
Visit http://localhost:8000 and type:
- "give insights"
- "show campaign performance"
- "optimize my campaigns"

## 📝 Notes

- The context variable error was a red herring - it was caused by the parameter type issue
- All 15 tool functions are now properly typed and working
- The system is fully ADK compliant and ready for production use

## 🚦 Status: READY FOR USE!

All errors have been resolved. The system is fully functional and ready for your billion-dollar company demo!