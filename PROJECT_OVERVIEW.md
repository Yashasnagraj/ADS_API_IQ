# MarketingIQ Google Ads Platform - Project Overview

## 🎯 Quick Start for Team Members

### For Dashboard Developers (Manya & Mayeera)

1. **API is running at**: `http://localhost:8000`
2. **API Documentation**: `http://localhost:8000/docs`
3. **Test the API**:
   ```bash
   curl http://localhost:8000/api/v1/campaigns
   ```

### Key Endpoints You'll Need:

```javascript
// Get all campaigns with metrics
GET /api/v1/campaigns

// Get specific campaign details
GET /api/v1/campaigns/{campaign_id}

// Get keywords with performance data
GET /api/v1/keywords?limit=100&offset=0

// Get aggregated metrics
GET /api/v1/metrics/summary?date_range=LAST_30_DAYS

// Get time series for charts
GET /api/v1/metrics/timeseries?campaign_id=123&interval=daily
```

## 📁 Repository Structure

```
MarketingIQ-Google-Ads/
│
├── 📊 ETL Pipeline (Main Directory)
│   ├── google_ads_etl_pipeline.py    # Main ETL script
│   ├── google_ads_data.db           # SQLite database
│   ├── extracted_data/              # CSV exports
│   └── requirements.txt             # Python dependencies
│
├── 🚀 API Service (/api)
│   ├── app/
│   │   ├── main.py                  # FastAPI application
│   │   ├── routes/                  # All endpoints
│   │   ├── schemas/                 # Response models
│   │   └── db/                      # Database models
│   └── requirements.txt             # API dependencies
│
├── 📚 Documentation
│   ├── README.md                    # Main documentation
│   ├── SETUP_GUIDE.md              # Detailed setup instructions
│   ├── GOOGLE_ADS_DATA_DOCUMENTATION.md  # Data schema docs
│   └── CONTRIBUTING.md            # Development guidelines
│
└── 🔧 Configuration
    ├── .gitignore                  # Git ignore rules
    ├── .env.example                # Environment template
    └── google-ads.yaml.template   # Google Ads config template
```

## 🔑 Important Files for Each Team

### Data Team
- `google_ads_etl_pipeline.py` - Main ETL logic
- `fix_campaigns_ml.py` - ML feature engineering
- `query_database.py` - Database queries

### API Team
- `api/app/main.py` - FastAPI application
- `api/app/routes/` - All endpoint implementations
- `api/app/schemas/` - Response schemas

### Frontend Team
- `api/README.md` - API documentation
- Access Swagger UI at `/docs` for interactive testing
- All endpoints return JSON with consistent structure

## 🚦 Current System Status

### ✅ What's Working
- ETL Pipeline extracting from Google Ads API
- 7 database tables with normalized data
- REST API with 20+ endpoints
- Pagination on all list endpoints
- Real-time metrics aggregation
- Time series data for charts
- API documentation (Swagger)

### 📊 Live Data
- **19** campaigns tracked
- **542** keywords monitored
- **199** search terms analyzed
- **$5,114** total spend
- **6** conversions recorded

## 🔒 Security Notes

### ⚠️ NEVER Commit These Files:
- `google-ads.yaml` (contains API keys)
- `.env` files (environment variables)
- Any `client_secret*.json` files
- `oauth_client.json`

### ✅ Safe to Share:
- All `.template` files
- `.example` files
- Documentation files
- Source code (without credentials)

## 🚀 Running the System

### 1. ETL Pipeline (Update Data)
```bash
python google_ads_etl_pipeline.py
```
Runs daily to fetch latest data from Google Ads

### 2. API Service (Serve Data)
```bash
cd api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Always running to serve data to dashboards

## 📞 Team Contacts & Responsibilities

| Component | Team Member | Responsibility |
|-----------|------------|----------------|
| ETL Pipeline | Data Team | Data extraction & transformation |
| API Development | Backend Team | REST service & endpoints |
| Dashboard Integration | Manya | Frontend development |
| Dashboard Integration | Mayeera | Frontend development |
| ML Features | ML Team | Feature engineering |
| DevOps | Infrastructure | Deployment & monitoring |

## 🎉 Ready for Sharing!

The repository is now:
- ✅ Clean of sensitive data
- ✅ Well documented
- ✅ Properly structured
- ✅ Ready for team collaboration

## Next Steps

1. **For New Team Members**:
   - Read `SETUP_GUIDE.md`
   - Copy `.env.example` to `.env`
   - Get credentials from team lead

2. **For Development**:
   - Create feature branch
   - Make changes
   - Test locally
   - Submit PR

3. **For Production**:
   - Deploy API to cloud
   - Set up scheduled ETL runs
   - Implement monitoring

---
**Repository Status**: Production-Ready ✅
**Last Updated**: September 2025
**Maintained By**: MarketingIQ Data Platform Team