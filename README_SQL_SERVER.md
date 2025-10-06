# MarketingIQ - Google Ads Data Warehouse with SQL Server

## Overview
Complete ETL pipeline and REST API for Google Ads data using Dockerized SQL Server with dimensional modeling.

## Architecture
- **Database**: SQL Server 2022 (Dockerized)
- **ETL**: Python pipeline extracting from Google Ads API
- **API**: FastAPI REST endpoints
- **Data Model**: Star schema with dimensions and facts

## Quick Start

### 1. Prerequisites
- Docker Desktop installed and running
- Python 3.8+
- ODBC Driver 18 for SQL Server

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start SQL Server
```bash
# Start Docker container
docker-compose up -d

# Wait for SQL Server to initialize (about 10-15 seconds)
```

### 4. Initialize Database Schema
```bash
# Option 1: Use the batch script (Windows)
start_services.bat

# Option 2: Manual initialization
docker exec -it marketing_sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "Yashas#@123" -d master -Q "CREATE DATABASE MarketingIQ"

# Then run SQL scripts manually using sqlcmd or SQL Server Management Studio
```

### 5. Test Connection
```bash
python test_connection.py
```

### 6. Run ETL Pipeline
```bash
python etl_pipeline_sqlserver.py
```

### 7. Start API Server
```bash
python api_sqlserver.py
```

Access API documentation at: http://localhost:8000/docs

## Database Schema

### Dimensions
- **DimDate**: Date dimension with calendar attributes
- **DimCampaign**: Campaign master data
- **DimAdGroup**: Ad group details
- **DimKeyword**: Keyword information
- **DimAd**: Ad creative details
- **DimDevice**: Device categories
- **DimGeography**: Location data

### Facts
- **FactCampaignPerformance**: Campaign-level metrics
- **FactAdGroupPerformance**: Ad group metrics
- **FactKeywordPerformance**: Keyword performance
- **FactAdPerformance**: Ad-level metrics with device and geo

## API Endpoints

### Campaigns
- `GET /campaigns` - List all campaigns
- `GET /campaigns/{id}` - Get campaign details
- `GET /campaigns/{id}/performance` - Campaign performance over time

### Ad Groups
- `GET /ad-groups` - List ad groups
- `GET /ad-groups/{id}` - Get ad group details

### Keywords
- `GET /keywords` - List keywords with performance

### Metrics
- `GET /metrics/summary` - Overall performance summary
- `GET /metrics/trends` - Trending metrics over time

## Configuration

### Environment Variables (.env)
```
DB_TYPE=sqlserver
DB_HOST=localhost
DB_PORT=1433
DB_NAME=MarketingIQ
DB_USER=sa
DB_PASSWORD=Yashas#@123
```

### Google Ads Configuration (google-ads.yaml)
Already configured with your credentials.

## Docker Management

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f sqlserver
```

### Connect to SQL Server
```bash
# Using sqlcmd
docker exec -it marketing_sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "Yashas#@123"

# Or use SQL Server Management Studio (SSMS)
Server: localhost,1433
Authentication: SQL Server Authentication
Username: sa
Password: Yashas#@123
```

## Troubleshooting

### Connection Issues
1. Ensure Docker is running
2. Check if port 1433 is available
3. Verify ODBC Driver 18 is installed
4. Test with: `python test_connection.py`

### ETL Issues
- Check Google Ads API credentials in google-ads.yaml
- Verify customer IDs have proper access
- Review logs: ETL includes detailed logging

### API Issues
- Ensure database is populated (run ETL first)
- Check API logs for errors
- Verify port 8000 is available

## Data Flow
1. **Extract**: Google Ads API → Python ETL
2. **Transform**: Business rules and calculations
3. **Load**: SQL Server dimensional model
4. **Serve**: FastAPI REST endpoints

## Performance Optimization
- Indexed foreign keys for fast joins
- Computed columns for common metrics (CTR, CPC, ROAS)
- Bulk insert operations
- Connection pooling

## Next Steps
1. Add incremental data loading
2. Implement data quality checks
3. Add authentication to API
4. Create Power BI dashboards
5. Set up automated ETL scheduling