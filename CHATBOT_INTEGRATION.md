# ADK Chatbot Integration with MarketingIQ Platform

## Overview

This integration connects the Google ADK Multi-Agent System with the MarketingIQ React dashboard through a chatbot API.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   MarketingIQ Platform                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React Dashboard (Port 3000)                         │  │
│  │  - FloatingChatbot Component                         │  │
│  │  - Customer Filters                                  │  │
│  │  - Data Visualizations                               │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│                 │ HTTP Requests                              │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ADK Chatbot API (Port 8003)                         │  │
│  │  - Intent Classification                             │  │
│  │  - Agent Routing                                     │  │
│  │  - Response Formatting                               │  │
│  └──────────────┬───────────────────────────────────────┘  │
│                 │                                            │
│                 │ Function Calls                             │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ADK Orchestration Agent                             │  │
│  │  ┌────────────┬────────────┬─────────────────────┐  │  │
│  │  │ Data Agent │Insight Agent│Optimization Agent  │  │  │
│  │  └────────────┴────────────┴─────────────────────┘  │  │
│  │  └──────────────────┬──────────────────────────────┘  │  │
│  │                     │                                   │  │
│  │                     │ API Calls                         │  │
│  │                     ▼                                   │  │
│  │  ┌──────────────────────────────────────────────────┐  │
│  │  │  SQLite Data API (Port 8004)                     │  │
│  │  │  - Campaigns, Keywords, Ad Groups               │  │
│  │  │  - Search Terms, ML Features                    │  │
│  │  │  - Performance Metrics                           │  │
│  │  └──────────────┬───────────────────────────────────┘  │
│  │                 │                                        │
│  │                 ▼                                        │
│  │  ┌──────────────────────────────┐                      │
│  │  │  google_ads_data.db          │                      │
│  │  │  (SQLite Database)           │                      │
│  │  └──────────────────────────────┘                      │
│  │                                                          │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. ADK Chatbot API (`google-ads-multiagent/adk/chatbot_api.py`)

**Port:** 8003

**Features:**
- Keyword-based intent classification
- Routes queries to appropriate ADK agents:
  - **Data Agent**: Campaign, keyword, ad group data
  - **Insight Agent**: Trend analysis, anomaly detection
  - **Optimization Agent**: Bid and budget recommendations
  - **Forecasting Agent**: Performance predictions
- Formats responses in natural language with markdown

**Endpoints:**
- `POST /api/chat` - Main chatbot endpoint
- `GET /api/agents` - List available agents
- `GET /health` - Health check

### 2. React Chatbot Component (`marketingiq-platform/web/src/components/chatbot/FloatingChatbot.tsx`)

**Features:**
- Floating chat widget (bottom-right corner)
- Real-time messaging with ADK agents
- Markdown response rendering
- Quick prompt suggestions
- Customer context awareness

### 3. Configuration (`marketingiq-platform/web/src/config/api.ts`)

Updated to include:
```typescript
CHATBOT_API_URL: 'http://localhost:8003/api'
```

## Quick Start

### Option 1: All-in-One Launcher (Recommended)

```bash
# From project root
start_marketingiq_platform.bat
```

This starts:
1. SQLite Data API (port 8004)
2. ADK Chatbot API (port 8003)
3. React Dashboard (port 3000)

### Option 2: Manual Start

**Terminal 1 - Data API:**
```bash
python api_sqlite.py
```

**Terminal 2 - Chatbot API:**
```bash
cd google-ads-multiagent/adk
python chatbot_api.py
```

**Terminal 3 - React Dashboard:**
```bash
cd marketingiq-platform/web
npm start
```

## Usage Examples

### Chat Interface

Open the dashboard at `http://localhost:3000` and click the chat icon in the bottom-right corner.

**Example Queries:**

1. **Campaign Performance**
   - "Show top performing campaigns"
   - "List my active campaigns"
   - "What campaigns are running?"

2. **Keyword Analysis**
   - "What keywords are underperforming?"
   - "Show keyword quality scores"
   - "Which keywords should I pause?"

3. **Budget Optimization**
   - "How should I optimize my budget?"
   - "Reallocate my campaign budgets"
   - "Where should I spend more?"

4. **Performance Insights**
   - "Analyze my performance trends"
   - "Are there any issues with my campaigns?"
   - "Detect anomalies in my data"

5. **Forecasting**
   - "Forecast next month's spend"
   - "Predict my CTR for next 30 days"
   - "What will my conversions be?"

## Agent Routing Logic

The chatbot uses keyword-based intent classification:

| Keywords | Agent | Action |
|----------|-------|--------|
| campaign, campaigns, top performer | Data Agent | Get campaign performance |
| keyword, keywords, quality score | Data Agent | Get keyword performance |
| ad group, adgroup | Data Agent | Get ad group performance |
| trend, performance, analyze | Insight Agent | Analyze trends |
| anomaly, issue, problem, alert | Insight Agent | Detect anomalies |
| budget, spend, allocate | Optimization Agent | Optimize budgets |
| bid, bids, cpc | Optimization Agent | Optimize bids |
| forecast, predict, future | Forecasting Agent | Forecast performance |

## Customer Filtering

The chatbot respects the selected customer from the global filter:

```javascript
customer_id: localStorage.getItem('selected_customer_id')
```

When a customer is selected in the dashboard, all chatbot queries are scoped to that customer's data.

## Response Format

Responses are formatted in markdown with:
- **Bold headers** for sections
- Bullet points for lists
- Emojis for visual appeal
- INR currency formatting (₹)
- Numbered lists for top performers

Example response:
```
📊 **Top Performing Campaigns:**

1. **Summer Sale Campaign**
   - Clicks: 1,234 | Cost: ₹12,345.67 | Conversions: 45

2. **Brand Awareness**
   - Clicks: 987 | Cost: ₹8,765.43 | Conversions: 32

**Recommendations:**
• Increase budget for Summer Sale by 20%
• Optimize ad copy for Brand Awareness
```

## Troubleshooting

### Chatbot not responding

1. **Check API is running:**
   ```bash
   curl http://localhost:8003/health
   ```

2. **Verify ADK agents loaded:**
   - Look for "ADK Agents Available: True" in console

3. **Check Data API connection:**
   ```bash
   curl http://localhost:8004/campaigns
   ```

### "ADK agents not available" error

This means the ADK orchestration agent couldn't be imported. Ensure:

1. Google ADK SDK is installed:
   ```bash
   pip install google-adk
   ```

2. Agent files exist in `adk/orchestration_agent/`

3. No import errors in the agent files

### CORS errors in browser

The chatbot API has CORS enabled for all origins. If you still see errors:

1. Check browser console for specific error
2. Verify API is running on correct port
3. Clear browser cache and reload

## Development

### Adding New Intents

Edit `chatbot_api.py`:

```python
def classify_user_intent(message: str) -> Dict[str, Any]:
    # Add new keyword patterns
    if any(word in message_lower for word in ['new', 'keywords']):
        return {
            "agent": "your_agent",
            "action": "your_action",
            "keywords": ["new"]
        }
```

### Adding New Response Formats

Edit the `format_response()` function:

```python
if agent == "your_agent":
    response = "🎯 **Your Response:**\n\n"
    # Add formatting logic
    return response
```

### Testing the API

Use curl or Postman:

```bash
curl -X POST http://localhost:8003/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show top campaigns",
    "customer_id": "123"
  }'
```

## Future Enhancements

- [ ] Session-based conversation history
- [ ] Multi-turn conversations with context
- [ ] Voice input/output
- [ ] Suggested follow-up questions
- [ ] Export chat history
- [ ] Share insights from chat
- [ ] Integration with Google Gemini for more natural responses
- [ ] Agent selection by user
- [ ] Streaming responses

## API Ports Reference

| Service | Port | URL |
|---------|------|-----|
| React Dashboard | 3000 | http://localhost:3000 |
| ADK Chatbot API | 8003 | http://localhost:8003 |
| SQLite Data API | 8004 | http://localhost:8004 |

## Dependencies

**Python (Chatbot API):**
- fastapi
- uvicorn
- pydantic
- requests
- google-adk

**React (Dashboard):**
- @mui/material
- react-markdown
- axios

## Support

For issues or questions:
1. Check console logs in browser (F12)
2. Check API logs in terminal
3. Verify all services are running
4. Review this documentation

---

**Status:** ✅ Production Ready
**Last Updated:** 2025-10-04
**Version:** 1.0.0
