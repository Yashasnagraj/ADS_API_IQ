# ADK Chatbot Integration - Summary

## What Was Created

### 1. Backend - ADK Chatbot API

**File:** `google-ads-multiagent/adk/chatbot_api.py`

A FastAPI server that:
- Connects the ADK multi-agent system to the React frontend
- Provides conversational interface to Data, Insight, Optimization, and Forecasting agents
- Uses keyword-based intent classification
- Formats responses in natural language with markdown
- Runs on port 8003

**Key Features:**
- Intent classification (campaign queries, keyword analysis, budget optimization, etc.)
- Agent routing to appropriate ADK sub-agent
- Natural language response formatting
- Customer-aware filtering
- CORS enabled for frontend access

### 2. Frontend Updates

**File:** `marketingiq-platform/web/src/config/api.ts`

Updated API configuration:
```typescript
CHATBOT_API_URL: 'http://localhost:8003/api'
```

**File:** `marketingiq-platform/web/src/components/chatbot/FloatingChatbot.tsx`

Updated chatbot component to:
- Connect to ADK chatbot API (port 8003)
- Pass selected customer_id from global filter
- Display "Powered by ADK Multi-Agent" instead of Gemini
- Handle ADK-specific error messages

### 3. Startup Scripts

**File:** `start_marketingiq_platform.bat`

All-in-one launcher that starts:
1. SQLite Data API (port 8004)
2. ADK Chatbot API (port 8003)
3. React Dashboard (port 3000)

**File:** `google-ads-multiagent/adk/start_chatbot.bat`

Individual launcher for just the chatbot API

### 4. Documentation

**File:** `CHATBOT_INTEGRATION.md`

Comprehensive documentation including:
- Architecture diagram
- Component descriptions
- Quick start guide
- Usage examples
- Agent routing logic
- Troubleshooting guide
- Development guide

**File:** `INTEGRATION_SUMMARY.md` (this file)

Quick reference for what was created

### 5. Testing

**File:** `google-ads-multiagent/adk/test_chatbot.py`

Test script that verifies:
- Health endpoint
- Agent listing
- Chat functionality with various queries

## How to Use

### Quick Start

```bash
# From project root
start_marketingiq_platform.bat
```

Then open http://localhost:3000 and click the chat icon in the bottom-right.

### Manual Start

**Terminal 1:**
```bash
python api_sqlite.py
```

**Terminal 2:**
```bash
cd google-ads-multiagent/adk
python chatbot_api.py
```

**Terminal 3:**
```bash
cd marketingiq-platform/web
npm start
```

### Test the API

```bash
cd google-ads-multiagent/adk
python test_chatbot.py
```

## Architecture Flow

```
User types message in React Dashboard
    ↓
FloatingChatbot component sends POST to /api/chat
    ↓
ADK Chatbot API classifies intent
    ↓
Routes to appropriate agent (Data/Insight/Optimization/Forecasting)
    ↓
Agent calls SQLite Data API (port 8004)
    ↓
Data returned and formatted in natural language
    ↓
Response sent back to React component
    ↓
Displayed in chat with markdown formatting
```

## Supported Query Types

1. **Campaign Queries** → Data Agent
   - "Show top campaigns"
   - "List my campaigns"

2. **Keyword Analysis** → Data Agent
   - "What keywords are underperforming?"
   - "Show keyword quality scores"

3. **Performance Insights** → Insight Agent
   - "Analyze my trends"
   - "Detect anomalies"

4. **Budget Optimization** → Optimization Agent
   - "How should I optimize my budget?"
   - "Reallocate budgets"

5. **Bid Optimization** → Optimization Agent
   - "Optimize my bids"
   - "What should my CPC be?"

6. **Forecasting** → Forecasting Agent
   - "Forecast next month"
   - "Predict my spend"

## Integration Points

### Backend → Backend
- ADK Chatbot API (8003) → SQLite Data API (8004)
- Uses `requests` library for HTTP calls
- Imports agent functions directly from `orchestration_agent.agent`

### Frontend → Backend
- React Dashboard → ADK Chatbot API
- Uses `fetch()` with `API_CONFIG.CHATBOT_API_URL`
- Passes `customer_id` from localStorage

### Customer Filtering
- Global filter in React sets `selected_customer_id` in localStorage
- FloatingChatbot reads this and sends with every query
- ADK agents pass to Data API for filtered results

## Files Modified

1. `marketingiq-platform/web/src/config/api.ts` - Added CHATBOT_API_URL
2. `marketingiq-platform/web/src/components/chatbot/FloatingChatbot.tsx` - Updated API endpoint

## Files Created

1. `google-ads-multiagent/adk/chatbot_api.py` - Main chatbot API
2. `google-ads-multiagent/adk/start_chatbot.bat` - Chatbot launcher
3. `google-ads-multiagent/adk/test_chatbot.py` - Test script
4. `start_marketingiq_platform.bat` - All-in-one launcher
5. `CHATBOT_INTEGRATION.md` - Full documentation
6. `INTEGRATION_SUMMARY.md` - This summary

## Next Steps

To use the chatbot:

1. **Start all services:**
   ```bash
   start_marketingiq_platform.bat
   ```

2. **Open dashboard:**
   - Navigate to http://localhost:3000

3. **Click chat icon:**
   - Bottom-right floating button

4. **Ask questions:**
   - Try the quick prompts or type your own

5. **Select customer (optional):**
   - Use global filter to scope queries to specific customer

## Testing Checklist

- [ ] Health check: `curl http://localhost:8003/health`
- [ ] List agents: `curl http://localhost:8003/api/agents`
- [ ] Test chat: `python google-ads-multiagent/adk/test_chatbot.py`
- [ ] Open dashboard and test UI chatbot
- [ ] Try each query type
- [ ] Verify customer filtering works
- [ ] Check markdown rendering in responses

## Troubleshooting

**Chatbot shows connection error:**
- Ensure chatbot API is running on port 8003
- Check browser console for CORS errors
- Verify `api.ts` has correct CHATBOT_API_URL

**"ADK agents not available" error:**
- Install google-adk: `pip install google-adk`
- Check imports in chatbot_api.py

**No data in responses:**
- Ensure SQLite Data API is running on port 8004
- Verify database has data: `python check_db_schema.py`

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| React Dashboard | 3000 | http://localhost:3000 |
| ADK Chatbot | 8003 | http://localhost:8003 |
| SQLite Data API | 8004 | http://localhost:8004 |

---

**Integration Status:** ✅ Complete
**Ready for Testing:** Yes
**Production Ready:** Yes (after testing)
