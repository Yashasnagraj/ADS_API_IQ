# 🤖 AI Chatbot Setup Guide

## Overview

Your MarketingIQ platform now has a **floating AI chatbot** that appears on all pages! It's powered by:
- **Google Gemini 2.0 Flash** for natural language understanding
- **ADK Multi-Agent System** for data retrieval
- **Beautiful Material-UI** interface

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                 USER INTERFACE                      │
│          React App (Port 3000)                      │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │   Floating Chatbot Component               │   │
│  │   - Material-UI Design                     │   │
│  │   - Markdown Formatting                    │   │
│  │   - Real-time Messaging                    │   │
│  └────────────┬───────────────────────────────┘   │
└───────────────┼─────────────────────────────────────┘
                │ HTTP POST
                ▼
┌─────────────────────────────────────────────────────┐
│          CHATBOT API (Port 8002)                    │
│                                                     │
│  ┌────────────────────────────────────────────┐   │
│  │  Step 1: Intent Classification              │   │
│  │  Gemini analyzes: "Show top campaigns"     │   │
│  │  → Intent: campaign_query                  │   │
│  │  → Requires Data: true                     │   │
│  └────────────┬───────────────────────────────┘   │
│               │                                     │
│  ┌────────────▼───────────────────────────────┐   │
│  │  Step 2: Query ADK Orchestrator            │   │
│  │  POST /api/agent/execute                   │   │
│  │  {agent_type: "data", action: "get_..."}  │   │
│  └────────────┬───────────────────────────────┘   │
│               │                                     │
│  ┌────────────▼───────────────────────────────┐   │
│  │  Step 3: Format Response with Gemini       │   │
│  │  Creates natural, conversational reply     │   │
│  │  with markdown formatting                  │   │
│  └────────────────────────────────────────────┘   │
└────────────────┼───────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│       MULTI-AGENT SYSTEM (Port 8001)                │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │  Orchestrator Agent                          │  │
│  │  ┌────────┐ ┌─────────┐ ┌──────────┐       │  │
│  │  │ Data   │ │ Insight │ │Optimize │        │  │
│  │  │ Agent  │ │ Agent   │ │Agent    │        │  │
│  │  └────┬───┘ └─────────┘ └──────────┘       │  │
│  └───────┼──────────────────────────────────────┘  │
└──────────┼──────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│      DATA WAREHOUSE API (Port 8004)                 │
│      SQLite Database with Real Google Ads Data      │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd marketingiq-platform/web
npm install react-markdown
```

### Step 2: Start All Backend Services

Run the startup script:

```bash
cd C:\Users\yashr\Desktop\ADS_API
start_all_services.bat
```

This will start:
- **Port 8004:** Data Warehouse API (SQLite)
- **Port 8001:** Multi-Agent System
- **Port 8002:** AI Chatbot API

### Step 3: Start React Frontend

```bash
cd marketingiq-platform/web
npm start
```

The app will open at `http://localhost:3000` with the chatbot available!

---

## 🎯 Features

### Floating Chat Button
- **Location:** Bottom-right corner of every page
- **Icon:** Chat bubble icon with gradient background
- **Animation:** Hover effect with scale transform

### Chat Window
- **Design:** Modern Material-UI Paper component
- **Size:** 400px × 600px
- **Position:** Above the floating button
- **Effects:**
  - Slide-up animation
  - Shadow with primary color glow
  - Smooth transitions

### Message Types

#### User Messages
- **Alignment:** Right-aligned
- **Color:** Primary blue
- **Avatar:** Person icon

#### AI Messages
- **Alignment:** Left-aligned
- **Color:** White/gray background
- **Avatar:** Robot icon
- **Formatting:** Full markdown support
  - **Bold text**
  - Bullet lists
  - Paragraphs
  - Code blocks

### Quick Prompts

When chat opens, users see suggested prompts:
- "Show top performing campaigns"
- "What keywords are underperforming?"
- "Analyze my budget allocation"
- "Forecast next month's spend"

---

## 🧠 Supported Intents

### 1. Campaign Query
**Examples:**
- "Show my campaigns"
- "Which campaigns are performing best?"
- "List active campaigns"

**Agent:** Data Agent
**Action:** `get_campaign_performance`

### 2. Keyword Analysis
**Examples:**
- "What keywords are underperforming?"
- "Show keyword quality scores"
- "Analyze my keywords"

**Agent:** Insight Agent
**Action:** `analyze_performance`

### 3. Budget Optimization
**Examples:**
- "How should I optimize my budget?"
- "Reallocate campaign budgets"
- "Where should I spend more?"

**Agent:** Optimization Agent
**Action:** `optimize_budgets`

### 4. Performance Forecast
**Examples:**
- "Predict next month's spend"
- "Forecast my CTR"
- "What's my expected ROAS?"

**Agent:** Forecasting Agent
**Action:** `forecast_performance`

### 5. Anomaly Detection
**Examples:**
- "Are there any issues?"
- "Detect anomalies"
- "What's wrong with my campaigns?"

**Agent:** Insight Agent
**Action:** `detect_anomalies`

### 6. General Questions
**Examples:**
- "What is ROAS?"
- "How does Quality Score work?"
- "Explain CTR"

**Response:** Direct answer from Gemini (no agent call)

---

## 🔧 Configuration

### Environment Variables

Create `.env` in root directory:

```bash
# Gemini API Key (for chatbot)
GEMINI_API_KEY=your_gemini_api_key_here

# ADK Orchestrator URL
ADK_URL=http://localhost:8001

# Data Warehouse API
DATA_API_URL=http://localhost:8004
```

### Customer ID

The chatbot uses `customer_id` from localStorage to filter data:

```javascript
// In your app, set customer ID when user logs in
localStorage.setItem('customer_id', '6265362093');
```

---

## 📝 API Endpoints

### Chatbot API (Port 8002)

#### POST /api/chat
**Request:**
```json
{
  "message": "Show top campaigns",
  "customer_id": "6265362093"
}
```

**Response:**
```json
{
  "response": "Here are your top campaigns...",
  "metadata": {
    "intent": "campaign_query",
    "adk_called": true
  },
  "timestamp": "2025-10-01T12:00:00"
}
```

#### GET /health
Check chatbot API health and ADK connection

#### GET /api/intents
List all supported intents with examples

---

## 🎨 Customization

### Change Chat Window Size

Edit `FloatingChatbot.tsx`:

```typescript
<Paper
  sx={{
    width: 500,  // Change from 400
    height: 700, // Change from 600
    // ...
  }}
>
```

### Change Position

```typescript
sx={{
  bottom: 90,  // Distance from bottom
  right: 24,   // Distance from right
}}
```

### Modify Colors

```typescript
// Header gradient
background: `linear-gradient(135deg,
  ${theme.palette.primary.main} 0%,
  ${theme.palette.secondary.main} 100%)`

// Button colors
sx={{
  bgcolor: theme.palette.primary.main,
  '&:hover': {
    bgcolor: theme.palette.primary.dark,
  },
}}
```

### Add New Intents

1. Update `classify_intent()` in `chatbot_api.py`:
```python
"intent": "one of: ..., your_new_intent"
```

2. Add handler in `query_adk_orchestrator()`:
```python
elif intent == "your_new_intent":
    response = requests.post(
        f"{ADK_ORCHESTRATOR_URL}/api/agent/execute",
        json={
            "agent_type": "your_agent",
            "action": "your_action",
            ...
        }
    )
```

---

## 🧪 Testing

### Test Chatbot API

```bash
# Check health
curl http://localhost:8002/health

# Send test message
curl -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show top campaigns"}'

# List intents
curl http://localhost:8002/api/intents
```

### Test in Browser

1. Open React app: `http://localhost:3000`
2. Click chat button (bottom-right)
3. Try quick prompts or type your own
4. Check for:
   - Smooth animations
   - Markdown formatting
   - Loading states
   - Error handling

---

## 🐛 Troubleshooting

### Chatbot Not Appearing

**Check:**
1. FloatingChatbot imported in Layout.tsx ✓
2. React app compiled without errors
3. Browser console for errors

### API Connection Failed

**Check:**
1. Port 8002 not in use
2. Chatbot API running: `http://localhost:8002/health`
3. CORS configured correctly
4. Browser console network tab

### No Response from AI

**Check:**
1. Gemini API key valid
2. ADK orchestrator running (port 8001)
3. Data API running (port 8004)
4. Check `chatbot_api.py` logs

### Markdown Not Rendering

**Check:**
1. `react-markdown` installed: `npm list react-markdown`
2. Import statement correct in FloatingChatbot.tsx
3. ReactMarkdown component used for assistant messages

---

## 📊 Port Summary

| Service | Port | Purpose |
|---------|------|---------|
| **React Frontend** | 3000 | Web UI |
| **Multi-Agent API** | 8001 | ADK Orchestrator |
| **Chatbot API** | 8002 | AI Chat Engine |
| **Data Warehouse** | 8004 | SQLite API |

---

## 🎯 Example Conversations

### Example 1: Campaign Performance

**User:** "Show my top campaigns"

**AI Response:**
> 📊 Here are your top-performing campaigns:
>
> **Top 3 Campaigns:**
> 1. **Whatsappapicommunn** - 583 impressions, 68 clicks (11.3% CTR)
> 2. Campaign B - ...
>
> **Recommendations:**
> - Increase budget for Campaign 1 (highest CTR)
> - Optimize keywords for Campaign 2
>
> Would you like detailed analysis?

### Example 2: Keyword Issues

**User:** "What keywords are underperforming?"

**AI Response:**
> 🔍 **Underperforming Keywords Detected:**
>
> - **wati** - Quality Score: 3, needs improvement
> - Keyword X - Low CTR, consider pausing
>
> **Actions:**
> - Review ad copy for these keywords
> - Improve landing page quality
> - Consider bid adjustments

### Example 3: General Question

**User:** "What is ROAS?"

**AI Response:**
> 📚 **ROAS (Return on Ad Spend)** measures the revenue generated for every dollar spent on advertising.
>
> Formula: `Revenue / Ad Spend`
>
> Example: If you spend $100 and make $400 in sales, your ROAS is 4:1 or 400%.

---

## 🚀 Next Steps

### Phase 2 Enhancements

1. **Conversation Memory**
   - Store chat history in Redis/DB
   - Context-aware responses

2. **Voice Input**
   - Web Speech API integration
   - Voice commands

3. **Suggested Actions**
   - Clickable buttons for common tasks
   - "Apply recommendation" buttons

4. **Multi-language Support**
   - Detect user language
   - Translate responses

5. **Analytics**
   - Track popular questions
   - Improve intent classification
   - A/B test responses

---

## 📚 Tech Stack

- **Frontend:** React 19 + TypeScript + Material-UI
- **Backend:** FastAPI + Python 3.10+
- **AI:** Google Gemini 2.0 Flash
- **Agents:** Google ADK Framework
- **Database:** SQLite
- **Styling:** Emotion CSS-in-JS

---

## ✅ Checklist

- [x] Floating chatbot UI component
- [x] Backend chatbot API
- [x] ADK orchestrator integration
- [x] Gemini AI formatting
- [x] Markdown support
- [x] Intent classification
- [x] Multi-agent routing
- [x] Error handling
- [x] Loading states
- [x] Quick prompts
- [x] Startup script
- [ ] Conversation history (future)
- [ ] Voice input (future)
- [ ] Analytics tracking (future)

---

**Created:** October 1, 2025
**Version:** 1.0.0
**Status:** ✅ Ready for Testing
