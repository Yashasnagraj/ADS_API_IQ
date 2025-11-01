# 🤖 AI Chatbot Setup Guide

## Overview

Your Marketing IQ platform now has an **AI-powered chatbot** connected to the Google ADK multi-agent system!

The chatbot provides:
- **Campaign Performance Analysis**: Ask about top-performing campaigns
- **Keyword Insights**: Get keyword performance and recommendations
- **Budget Optimization**: Get AI-powered budget allocation suggestions
- **Anomaly Detection**: Find issues in your campaigns
- **Performance Forecasting**: Predict future campaign performance

---

## ✅ What's New

### 1. **Floating Chat Button**
- Appears on all dashboard pages (bottom-right corner)
- Purple gradient button with chat icon
- Click to open AI assistant

### 2. **ADK Multi-Agent System**
- **Data Agent**: Fetches campaign, keyword, and ad group data
- **Insight Agent**: Analyzes trends and detects anomalies
- **Optimization Agent**: Recommends budget and bid optimizations
- **Forecasting Agent**: Predicts future performance

### 3. **Natural Language Interface**
- Ask questions in plain English
- AI understands context from your current filters (customer, date range)
- Responses formatted with markdown

---

## 🚀 Quick Start

### **Option 1: One-Click Start (Easiest)**

Double-click this file:
```
D:\ADS_API\START_ALL_SERVERS.bat
```

This will start:
1. Backend API (port 8000)
2. ADK Chatbot API (port 8003)

### **Option 2: Manual Start**

**Terminal 1 - Backend API:**
```bash
cd D:\ADS_API\api
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Chatbot API:**
```bash
cd D:\ADS_API\google-ads-multiagent\adk
python chatbot_api.py
```

**Terminal 3 - Frontend:**
```bash
cd D:\ADS_API\marketingiq-platform\web
npm run dev
```

---

## 🧪 Testing the Chatbot

### **1. Test Chatbot API Connection**
```bash
cd D:\ADS_API
python test_chatbot_connection.py
```

You should see:
```
✅ Chatbot API is healthy!
✅ Available ADK Agents: Data Agent, Insight Agent, Optimization Agent...
✅ Chat response received!
```

### **2. Test in Browser**
1. Open http://localhost:5173
2. Navigate to any dashboard (e.g., Unified Dashboard)
3. Click the **purple chat button** in bottom-right
4. Try these example questions:

**Campaign Questions:**
- "Show me my top performing campaigns"
- "Which campaigns are spending the most?"
- "How are my campaigns doing?"

**Keyword Questions:**
- "Show me underperforming keywords"
- "Which keywords have low quality scores?"
- "Analyze my keyword performance"

**Optimization Questions:**
- "How should I optimize my budget?"
- "Which bids should I adjust?"
- "Give me campaign optimization recommendations"

**Forecasting Questions:**
- "Predict next month's performance"
- "Forecast my campaign spend"
- "What are my projections?"

**Anomaly Detection:**
- "Are there any issues in my campaigns?"
- "Detect anomalies in my performance"
- "Show me alerts"

---

## 📊 How It Works

### **Request Flow:**
```
User Question
    ↓
FloatingChatButton Component (Frontend)
    ↓
POST http://localhost:8003/api/chat
    ↓
ADK Chatbot API (chatbot_api.py)
    ↓
Intent Classification (keyword matching)
    ↓
Agent Routing (Data/Insight/Optimization/Forecasting)
    ↓
Warehouse Query (marketing_warehouse.db)
    ↓
Format Response (markdown)
    ↓
[Optional] Gemini Enhancement (friendly tone)
    ↓
Return to Frontend
    ↓
Display in Chat Window
```

### **Data Source:**
The chatbot queries the same **marketing_warehouse.db** that powers your dashboards:
- `dim_google_ads_campaign` - Campaign metadata
- `fact_campaign_performance_daily` - Performance metrics
- `dim_keyword` - Keyword data
- `meta_insights` - Meta Ads data
- `dim_customer` - Customer information

---

## 🔧 Configuration

### **Chatbot API Configuration**

Located in: `D:\ADS_API\google-ads-multiagent\adk\chatbot_api.py`

**Key Settings:**
- **Port**: 8003 (can be changed in `chatbot_api.py` line 550)
- **Gemini API**: Optional - enhances responses with friendly tone
- **Database**: Uses `marketing_warehouse.db` at project root

### **Frontend Configuration**

Located in: `D:\ADS_API\marketingiq-platform\web\src\components\chat\FloatingChatButton.tsx`

**Key Settings:**
- **API URL**: Line 30 - `http://localhost:8003/api/chat`
- **Chat Position**: Bottom-right (fixed position)
- **Auto-scroll**: Enabled
- **Context**: Automatically sends customer_id and date_range from filters

---

## 🎯 Advanced Features

### **1. Gemini AI Enhancement**

For even better responses, add Gemini API key:

1. Create `.env` file in `D:\ADS_API\google-ads-multiagent\adk\`
2. Add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
3. Restart chatbot server

**With Gemini:**
- Friendlier, more conversational tone
- Better formatting
- Contextual explanations

**Without Gemini:**
- Still works! Uses default formatting
- All features available
- Slightly more technical responses

### **2. Multi-Customer Support**

The chatbot automatically uses the customer selected in your filters:
- Select customer in filter bar → chatbot uses that customer_id
- Responses are scoped to selected customer's data
- Works seamlessly across all dashboards

### **3. Agent Metadata**

Each response includes metadata showing which agent handled the request:
- Look for small chip below message: "Agent: data"
- Helps understand which part of the system answered

---

## 🐛 Troubleshooting

### **Chat button not appearing?**
1. Check that `FloatingChatButton` is imported in Layout.tsx ✅
2. Refresh browser (Ctrl+Shift+R)
3. Check browser console for errors

### **"Cannot connect" error in chat?**
1. Verify chatbot API is running:
   ```bash
   curl http://localhost:8003/health
   ```
2. Check terminal for chatbot errors
3. Restart chatbot:
   ```bash
   cd D:\ADS_API\google-ads-multiagent\adk
   python chatbot_api.py
   ```

### **"ADK agents not available"?**
1. Check that ADK imports are working:
   ```bash
   cd D:\ADS_API\google-ads-multiagent\adk
   python -c "from adk.orchestration_agent.agent import root_agent; print('OK')"
   ```
2. If import errors, check Python path and dependencies

### **Slow responses?**
1. First request may be slower (warming up)
2. Subsequent requests use cache (5-minute TTL)
3. Complex forecasting queries take longer (~5-10 seconds)

### **Empty or "No data" responses?**
1. Make sure you've selected a customer with data (e.g., "Emcee Sons")
2. Check that warehouse has data:
   ```bash
   python test_chatbot_connection.py
   ```
3. Verify backend API is returning data

---

## 📁 Files Created/Modified

### **New Files:**
- `marketingiq-platform/web/src/components/chat/FloatingChatButton.tsx` - Chat UI component
- `START_ALL_SERVERS.bat` - Launch all services
- `test_chatbot_connection.py` - Test chatbot connectivity
- `CHATBOT_SETUP.md` - This file

### **Modified Files:**
- `marketingiq-platform/web/src/components/common/Layout.tsx` - Added FloatingChatButton

### **Existing Files (Already There):**
- `google-ads-multiagent/adk/chatbot_api.py` - Chatbot backend API
- `google-ads-multiagent/adk/orchestration_agent/sub_agents/data_agent/warehouse_client.py` - Warehouse connection
- `marketing_warehouse.db` - Data source

---

## 🎉 Success Criteria

Your chatbot is working if:

✅ Chat button appears in bottom-right of dashboards
✅ Clicking opens chat window
✅ Welcome message displays
✅ You can type and send messages
✅ AI responds with relevant campaign data
✅ No "cannot connect" errors
✅ Agent metadata chip shows (e.g., "Agent: data")

---

## 💡 Example Conversations

### **Example 1: Campaign Performance**
```
You: Show me my top performing campaigns
AI:  📊 Top 5 Performing Campaigns (out of 15 total):

     1. Demo Campaign - Search (ENABLED)
        - Clicks: 249 | Cost: ₹0.00
        - CTR: 0.00% | Conversions: 0.0

     [... more campaigns ...]
```

### **Example 2: Budget Optimization**
```
You: How should I optimize my budget?
AI:  💰 Budget Optimization:

     Campaign A
     Action: Increase budget (+20%)
     Why: High ROAS (3.5x), room to scale

     Campaign B
     Action: Reduce budget (-15%)
     Why: Low ROAS (0.8x), reallocate to better performers
```

### **Example 3: Forecasting**
```
You: Predict next month's performance
AI:  🔮 Performance Forecast (30 days):

     Projected Metrics:
     • Impressions: 45,000
     • Clicks: 1,200
     • Conversions: 36
     • Cost: ₹15,000
     • CTR: 2.67%

     Daily Averages:
     • ~40 clicks/day
     • ~₹500 spend/day
```

---

## 🔗 Useful Links

- **Chatbot API Docs**: http://localhost:8003/docs
- **Backend API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- **Health Check**: http://localhost:8003/health

---

## 🚀 Next Steps

1. **Start all servers**: Double-click `START_ALL_SERVERS.bat`
2. **Open frontend**: http://localhost:5173
3. **Click chat button**: Purple button in bottom-right
4. **Ask a question**: Try "Show me my top campaigns"
5. **Explore**: Try different questions and see what the agents can do!

Enjoy your AI-powered marketing assistant! 🎉
