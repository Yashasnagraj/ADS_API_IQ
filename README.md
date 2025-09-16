# MarketingIQ Google Ads Data Platform

A comprehensive ETL pipeline and REST API service for Google Ads data extraction, transformation, and analysis. This platform enables seamless integration with Google Ads API, provides structured data storage, and offers RESTful endpoints for dashboard integration and machine learning applications.

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌──────────────┐     ┌────────────┐
│  Google Ads API │────>│ ETL Pipeline │────>│  SQLite DB │
└─────────────────┘     └──────────────┘     └────────────┘
                                                    │
                                                    ▼
                        ┌────────────────────────────────┐
                        │      FastAPI REST Service      │
                        └────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐           ┌──────────┐
                    │Dashboard │           │ML Models │
                    └──────────┘           └──────────┘
```

## 🚀 Features

### ETL Pipeline
- **Automated Data Extraction**: Pulls comprehensive data from Google Ads API
- **Multi-Account Support**: Manages multiple client accounts via Manager Account
- **Data Normalization**: Structured storage in 7 normalized tables
- **Performance Metrics**: Tracks CTR, conversions, quality scores, and costs
- **ML-Ready Features**: Pre-processed features for machine learning models

### REST API Service
- **FastAPI Framework**: High-performance, async API with automatic documentation
- **Comprehensive Endpoints**: Access to campaigns, keywords, ad groups, search terms
- **Metrics Aggregation**: Real-time calculation of performance metrics
- **Time Series Data**: Historical performance data for trend analysis
- **Pagination & Filtering**: Efficient data retrieval for large datasets

## 📊 Data Schema

### Core Tables
- **campaigns**: Campaign configuration and settings
- **ad_groups**: Ad group structure and bidding strategies
- **keywords**: Keyword targeting with quality scores
- **search_terms**: Actual search queries and performance
- **campaign_keywords**: Performance metrics aggregation
- **ml_features**: Denormalized features for ML training

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Google Ads Manager Account
- Google Ads API Developer Token

### 1. Clone Repository
```bash
git clone https://github.com/your-org/marketingiq-google-ads.git
cd marketingiq-google-ads
```

### 2. Install Dependencies

#### ETL Pipeline
```bash
pip install -r requirements.txt
```

#### API Service
```bash
cd api
pip install -r requirements.txt
cd ..
```

### 3. Configure Google Ads Credentials

Copy the template and add your credentials:
```bash
cp google-ads.yaml.template google-ads.yaml
```

Edit `google-ads.yaml` with:
- Developer token
- Client ID & Secret
- Refresh token
- Manager Account ID

### 4. Generate Refresh Token
```bash
python generate_refresh_token.py
```

### 5. Run ETL Pipeline
```bash
python google_ads_etl_pipeline.py
```

This will:
- Connect to Google Ads API
- Extract data from all client accounts
- Transform and load into SQLite database
- Export CSV files to `extracted_data/`

### 6. Start API Service
```bash
cd api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access API documentation at: http://localhost:8000/docs

## 📡 API Endpoints

### Campaigns
- `GET /api/v1/campaigns` - List all campaigns with metrics
- `GET /api/v1/campaigns/{id}` - Campaign details
- `GET /api/v1/campaigns/{id}/adgroups` - Ad groups in campaign

### Keywords
- `GET /api/v1/keywords` - All keywords with performance
- `GET /api/v1/keywords/{id}` - Keyword details
- `GET /api/v1/keywords/{id}/search-terms` - Related search terms

### Metrics
- `GET /api/v1/metrics/summary` - Global aggregation
- `GET /api/v1/metrics/timeseries` - Historical performance

### ML Features
- `GET /api/v1/ml-features` - Pre-processed features for ML

## 📈 Usage Examples

### Query Campaign Performance
```python
import requests

response = requests.get("http://localhost:8000/api/v1/campaigns")
campaigns = response.json()["campaigns"]

for campaign in campaigns:
    print(f"{campaign['campaign_name']}: {campaign['metrics']['conversions']} conversions")
```

### Get Time Series Data
```python
params = {
    "campaign_id": 12345,
    "interval": "daily",
    "days": 30
}
response = requests.get("http://localhost:8000/api/v1/metrics/timeseries", params=params)
time_series = response.json()["data_points"]
```

## 🔧 Utility Scripts

- `list_accounts.py` - List all accessible Google Ads accounts
- `query_database.py` - Query SQLite database directly
- `query_keywords.py` - Analyze keyword performance
- `fix_campaigns_ml.py` - Fix and enhance ML features

## 📂 Project Structure

```
marketingiq-google-ads/
├── api/                          # REST API Service
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── core/                # Configuration
│   │   ├── db/                  # Database models
│   │   ├── routes/              # API endpoints
│   │   └── schemas/             # Response schemas
│   └── requirements.txt
├── extracted_data/               # CSV exports
├── google_ads_etl_pipeline.py   # Main ETL script
├── google_ads_data.db           # SQLite database
├── google-ads.yaml.template     # Config template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔐 Security Notes

- Never commit `google-ads.yaml` (contains API keys)
- Use `.env` files for environment-specific configs
- Rotate refresh tokens periodically
- Implement rate limiting in production
- Use HTTPS in production deployments

## 📊 Current Data Statistics

- **19** Active Campaigns
- **542** Keywords tracked
- **199** Search terms analyzed
- **511** ML features generated
- **$5,114** Total spend tracked
- **6** Conversions recorded

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is proprietary and confidential. All rights reserved.

## 👥 Team

- **Data Engineering**: ETL Pipeline Development
- **API Development**: REST Service Implementation
- **Dashboard Team**: Manya & Mayeera
- **ML Engineering**: Feature Engineering & Model Training

## 📞 Support

For issues or questions:
- Create an issue in the repository
- Contact the development team
- Check API documentation at `/docs`

---

Built with ❤️ for MarketingIQ by the Data Platform Team