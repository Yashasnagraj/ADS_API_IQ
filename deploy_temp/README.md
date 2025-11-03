# MarketingIQ Google Ads REST API

Production-grade REST API service for accessing Google Ads ETL data.

## Features

- **FastAPI** framework with automatic OpenAPI documentation
- **SQLAlchemy ORM** for database operations
- **Pagination** support on all list endpoints
- **CORS** enabled for frontend access
- **Error handling** with consistent error responses
- **Health checks** for monitoring
- **Environment-based configuration**

## Installation

1. Install dependencies:
```bash
cd api
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Run the API:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access the interactive documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Campaigns
- `GET /api/v1/campaigns` - List all campaigns with metrics
- `GET /api/v1/campaigns/{campaign_id}` - Campaign details
- `GET /api/v1/campaigns/{campaign_id}/adgroups` - Ad groups in campaign

### Ad Groups
- `GET /api/v1/adgroups/{ad_group_id}` - Ad group details
- `GET /api/v1/adgroups/{ad_group_id}/keywords` - Keywords in ad group

### Keywords
- `GET /api/v1/keywords` - All keywords with metrics
- `GET /api/v1/keywords/{keyword_id}` - Keyword details
- `GET /api/v1/keywords/{keyword_id}/search-terms` - Related search terms

### Search Terms
- `GET /api/v1/search-terms` - All search terms with performance

### ML Features
- `GET /api/v1/ml-features` - ML-ready features for training

### Metrics
- `GET /api/v1/metrics/summary` - Global metrics aggregation
- `GET /api/v1/metrics/timeseries` - Time series data for charts

## Query Parameters

All list endpoints support:
- `limit`: Number of results (default: 100, max: 1000)
- `offset`: Pagination offset
- Additional filters per endpoint (status, campaign_id, etc.)

## Response Format

### Success Response
```json
{
  "data": [...],
  "total": 1000,
  "limit": 100,
  "offset": 0,
  "has_more": true
}
```

### Error Response
```json
{
  "error": "Not Found",
  "detail": "Campaign 123 not found",
  "status_code": 404
}
```

## Environment Variables

- `DATABASE_URL`: SQLite database path
- `API_VERSION`: API version string
- `DEBUG`: Enable debug mode
- `CORS_ORIGINS`: Allowed CORS origins
- `LOG_LEVEL`: Logging level
- `PAGINATION_DEFAULT_LIMIT`: Default page size
- `PAGINATION_MAX_LIMIT`: Maximum page size

## Development

Run with auto-reload:
```bash
uvicorn app.main:app --reload
```

## Production

For production deployment:
1. Set `DEBUG=False` in .env
2. Use a production ASGI server like Gunicorn
3. Enable HTTPS with a reverse proxy
4. Monitor with health endpoint: `/health`

## Testing

Test the API endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Get campaigns
curl http://localhost:8000/api/v1/campaigns

# Get campaign details
curl http://localhost:8000/api/v1/campaigns/123
```