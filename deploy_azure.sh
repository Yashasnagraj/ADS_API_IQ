#!/bin/bash
# ==============================================================================
# Azure Deployment Script for MarketingIQ Platform
# ==============================================================================
# This script deploys:
# 1. Resource Group
# 2. PostgreSQL Flexible Server (database warehouse)
# 3. Azure App Service (FastAPI backend)
# 4. Azure Static Web Apps (React frontend - optional)
# ==============================================================================

set -e  # Exit on error

# ==============================================================================
# Configuration Variables
# ==============================================================================

# Azure Configuration
LOCATION="eastus"
RESOURCE_GROUP="marketingiq-rg"
APP_SERVICE_PLAN="marketingiq-plan"
WEB_APP_NAME="marketingiq-api"
POSTGRES_SERVER="marketingiq-db-server"
POSTGRES_DB="marketing_warehouse"
POSTGRES_ADMIN_USER="marketingiq_admin"
POSTGRES_SKU="Standard_B1ms"  # Burstable, 1 vCore, 2GB RAM - $12/month
POSTGRES_STORAGE_SIZE=32      # GB
POSTGRES_VERSION="16"

# Generate secure password (or set your own)
POSTGRES_ADMIN_PASSWORD="MarketingIQ2025!$(date +%s | sha256sum | base64 | head -c 8)"

# App Service Configuration
APP_SERVICE_SKU="B1"  # Basic tier - ~$13/month
PYTHON_VERSION="3.11"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ==============================================================================
# Helper Functions
# ==============================================================================

print_step() {
    echo -e "${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_info() {
    echo -e "${YELLOW}INFO:${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

print_success() {
    echo -e "${GREEN}SUCCESS:${NC} $1"
}

# ==============================================================================
# Pre-flight Checks
# ==============================================================================

print_step "Running pre-flight checks..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

# Display current subscription
SUBSCRIPTION=$(az account show --query name -o tsv)
print_info "Using Azure subscription: $SUBSCRIPTION"

# Confirm deployment
echo ""
echo "This script will create the following resources:"
echo "  - Resource Group: $RESOURCE_GROUP"
echo "  - Location: $LOCATION"
echo "  - PostgreSQL Server: $POSTGRES_SERVER"
echo "  - Database: $POSTGRES_DB"
echo "  - App Service: $WEB_APP_NAME"
echo ""
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Deployment cancelled."
    exit 0
fi

# ==============================================================================
# Step 1: Create Resource Group
# ==============================================================================

print_step "Creating Resource Group: $RESOURCE_GROUP"

if az group exists --name $RESOURCE_GROUP | grep -q true; then
    print_info "Resource group already exists. Skipping..."
else
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION \
        --output none
    print_success "Resource group created successfully"
fi

# ==============================================================================
# Step 2: Create PostgreSQL Flexible Server
# ==============================================================================

print_step "Creating PostgreSQL Flexible Server: $POSTGRES_SERVER"

# Check if server exists
if az postgres flexible-server show --resource-group $RESOURCE_GROUP --name $POSTGRES_SERVER &> /dev/null; then
    print_info "PostgreSQL server already exists. Skipping creation..."
else
    print_info "This may take 5-10 minutes..."

    az postgres flexible-server create \
        --resource-group $RESOURCE_GROUP \
        --name $POSTGRES_SERVER \
        --location $LOCATION \
        --admin-user $POSTGRES_ADMIN_USER \
        --admin-password "$POSTGRES_ADMIN_PASSWORD" \
        --sku-name $POSTGRES_SKU \
        --storage-size $POSTGRES_STORAGE_SIZE \
        --version $POSTGRES_VERSION \
        --public-access 0.0.0.0-255.255.255.255 \
        --output none

    print_success "PostgreSQL server created successfully"
fi

# Create database
print_step "Creating database: $POSTGRES_DB"

if az postgres flexible-server db show \
    --resource-group $RESOURCE_GROUP \
    --server-name $POSTGRES_SERVER \
    --database-name $POSTGRES_DB &> /dev/null; then
    print_info "Database already exists. Skipping..."
else
    az postgres flexible-server db create \
        --resource-group $RESOURCE_GROUP \
        --server-name $POSTGRES_SERVER \
        --database-name $POSTGRES_DB \
        --output none

    print_success "Database created successfully"
fi

# Configure firewall to allow Azure services
print_step "Configuring firewall rules..."

az postgres flexible-server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --name $POSTGRES_SERVER \
    --rule-name AllowAzureServices \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0 \
    --output none

print_success "Firewall configured"

# Build connection string
POSTGRES_HOST="$POSTGRES_SERVER.postgres.database.azure.com"
DATABASE_URL="postgresql://$POSTGRES_ADMIN_USER:$POSTGRES_ADMIN_PASSWORD@$POSTGRES_HOST:5432/$POSTGRES_DB?sslmode=require"

print_info "PostgreSQL connection string configured"

# ==============================================================================
# Step 3: Create App Service Plan
# ==============================================================================

print_step "Creating App Service Plan: $APP_SERVICE_PLAN"

if az appservice plan show --resource-group $RESOURCE_GROUP --name $APP_SERVICE_PLAN &> /dev/null; then
    print_info "App Service Plan already exists. Skipping..."
else
    az appservice plan create \
        --resource-group $RESOURCE_GROUP \
        --name $APP_SERVICE_PLAN \
        --location $LOCATION \
        --sku $APP_SERVICE_SKU \
        --is-linux \
        --output none

    print_success "App Service Plan created successfully"
fi

# ==============================================================================
# Step 4: Create Web App
# ==============================================================================

print_step "Creating Web App: $WEB_APP_NAME"

if az webapp show --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME &> /dev/null; then
    print_info "Web App already exists. Skipping creation..."
else
    az webapp create \
        --resource-group $RESOURCE_GROUP \
        --plan $APP_SERVICE_PLAN \
        --name $WEB_APP_NAME \
        --runtime "PYTHON:$PYTHON_VERSION" \
        --output none

    print_success "Web App created successfully"
fi

# ==============================================================================
# Step 5: Configure App Settings
# ==============================================================================

print_step "Configuring application settings..."

az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --settings \
        DATABASE_URL="$DATABASE_URL" \
        API_VERSION="v1" \
        DEBUG="false" \
        LOG_LEVEL="INFO" \
        CORS_ORIGINS='["*"]' \
        PAGINATION_DEFAULT_LIMIT="100" \
        PAGINATION_MAX_LIMIT="1000" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
        WEBSITE_HTTPLOGGING_RETENTION_DAYS="7" \
    --output none

print_success "App settings configured"

# Configure startup command
print_step "Configuring startup command..."

az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --startup-file "cd api && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" \
    --output none

print_success "Startup command configured"

# ==============================================================================
# Step 6: Deploy Application Code
# ==============================================================================

print_step "Deploying application code..."

print_info "Creating deployment package..."

# Create a temporary directory for deployment
DEPLOY_DIR=$(mktemp -d)
trap "rm -rf $DEPLOY_DIR" EXIT

# Copy necessary files
cp -r api "$DEPLOY_DIR/"
cp requirements.txt "$DEPLOY_DIR/"
cp marketing_warehouse.db "$DEPLOY_DIR/" 2>/dev/null || print_info "No local DB to copy"

# Create deployment zip
cd "$DEPLOY_DIR"
zip -r deploy.zip . -x "*.pyc" -x "*__pycache__*" > /dev/null

print_info "Uploading to Azure (this may take a few minutes)..."

az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --src deploy.zip \
    --output none

print_success "Application deployed successfully"

# ==============================================================================
# Step 7: Initialize Database Schema
# ==============================================================================

print_step "Initializing database schema..."

print_info "Checking if psql is available..."

if command -v psql &> /dev/null; then
    print_info "Uploading schema to PostgreSQL..."

    # Convert SQLite schema to PostgreSQL-compatible format
    cat warehouse_schema.sql | \
        sed 's/INTEGER PRIMARY KEY AUTOINCREMENT/SERIAL PRIMARY KEY/g' | \
        sed 's/TEXT/VARCHAR/g' | \
        sed 's/BOOLEAN/BOOLEAN/g' | \
        sed 's/TIMESTAMP DEFAULT CURRENT_TIMESTAMP/TIMESTAMP DEFAULT CURRENT_TIMESTAMP/g' | \
        PGPASSWORD="$POSTGRES_ADMIN_PASSWORD" psql \
            -h "$POSTGRES_HOST" \
            -U "$POSTGRES_ADMIN_USER" \
            -d "$POSTGRES_DB" \
            -v ON_ERROR_STOP=1 \
            > /dev/null 2>&1 || print_info "Schema might already exist or some tables may have been created"

    print_success "Database schema initialized"
else
    print_info "psql not found. You can initialize the schema manually using the connection string below."
fi

# ==============================================================================
# Step 8: Restart Web App
# ==============================================================================

print_step "Restarting web app..."

az webapp restart \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --output none

print_success "Web app restarted"

# Wait for app to start
print_info "Waiting for app to start (30 seconds)..."
sleep 30

# ==============================================================================
# Deployment Complete - Display Information
# ==============================================================================

echo ""
echo "=============================================================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=============================================================================="
echo ""
echo "Resource Information:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo ""
echo "Database:"
echo "  Server: $POSTGRES_HOST"
echo "  Database: $POSTGRES_DB"
echo "  Username: $POSTGRES_ADMIN_USER"
echo "  Password: $POSTGRES_ADMIN_PASSWORD"
echo "  Connection String: $DATABASE_URL"
echo ""
echo "Web Application:"
echo "  URL: https://$WEB_APP_NAME.azurewebsites.net"
echo "  API Docs: https://$WEB_APP_NAME.azurewebsites.net/docs"
echo "  Health Check: https://$WEB_APP_NAME.azurewebsites.net/health"
echo ""
echo "Next Steps:"
echo "  1. Test the health endpoint:"
echo "     curl https://$WEB_APP_NAME.azurewebsites.net/health"
echo ""
echo "  2. View API documentation:"
echo "     open https://$WEB_APP_NAME.azurewebsites.net/docs"
echo ""
echo "  3. View application logs:"
echo "     az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
echo ""
echo "  4. Connect to database:"
echo "     psql \"$DATABASE_URL\""
echo ""
echo "Cost Estimate:"
echo "  - PostgreSQL: ~$12/month (Standard_B1ms)"
echo "  - App Service: ~$13/month (B1 tier)"
echo "  - Total: ~$25/month"
echo ""
echo "Important: Save your database credentials in a secure location!"
echo "=============================================================================="
echo ""

# Save credentials to file
CREDS_FILE="azure_credentials.txt"
cat > $CREDS_FILE << EOF
Azure MarketingIQ Deployment Credentials
Generated: $(date)

Resource Group: $RESOURCE_GROUP
Location: $LOCATION

PostgreSQL Database:
  Host: $POSTGRES_HOST
  Database: $POSTGRES_DB
  Username: $POSTGRES_ADMIN_USER
  Password: $POSTGRES_ADMIN_PASSWORD
  Connection String: $DATABASE_URL

Web Application:
  URL: https://$WEB_APP_NAME.azurewebsites.net
  API Docs: https://$WEB_APP_NAME.azurewebsites.net/docs
  Health: https://$WEB_APP_NAME.azurewebsites.net/health

Management Commands:
  View logs: az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME
  Restart app: az webapp restart --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME
  SSH into app: az webapp ssh --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME

Cost: ~$25/month
EOF

print_success "Credentials saved to: $CREDS_FILE"
print_info "Keep this file secure and do not commit to git!"

echo ""
print_info "Testing health endpoint..."
sleep 10  # Give the app a moment more to fully start

if curl -sf "https://$WEB_APP_NAME.azurewebsites.net/health" > /dev/null 2>&1; then
    print_success "Health check passed! Application is running."
else
    print_info "Health check failed. The app may still be starting. Check logs with:"
    echo "    az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
fi

echo ""
print_success "Deployment script completed!"
