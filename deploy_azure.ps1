# ==============================================================================
# Azure Deployment Script for MarketingIQ Platform (PowerShell)
# ==============================================================================

$ErrorActionPreference = "Stop"

# ==============================================================================
# Configuration Variables
# ==============================================================================

$LOCATION = "eastus"
$RESOURCE_GROUP = "marketingiq-rg"
$APP_SERVICE_PLAN = "marketingiq-plan"
$WEB_APP_NAME = "marketingiq-api"
$POSTGRES_SERVER = "marketingiq-db-server"
$POSTGRES_DB = "marketing_warehouse"
$POSTGRES_ADMIN_USER = "marketingiq_admin"
$POSTGRES_SKU = "Standard_B1ms"
$POSTGRES_STORAGE_SIZE = 32
$POSTGRES_VERSION = "16"

# Generate secure password
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$POSTGRES_ADMIN_PASSWORD = "MarketingIQ2025!$($timestamp.Substring(8))"

$APP_SERVICE_SKU = "B1"
$PYTHON_VERSION = "3.11"

# ==============================================================================
# Helper Functions
# ==============================================================================

function Write-Step {
    param($Message)
    Write-Host "==> " -ForegroundColor Blue -NoNewline
    Write-Host $Message -ForegroundColor Green
}

function Write-Info {
    param($Message)
    Write-Host "INFO: " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-Error-Custom {
    param($Message)
    Write-Host "ERROR: " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Write-Success {
    param($Message)
    Write-Host "SUCCESS: " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

# ==============================================================================
# Pre-flight Checks
# ==============================================================================

Write-Step "Running pre-flight checks..."

# Check if Azure CLI is installed
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error-Custom "Azure CLI is not installed. Please install it first."
    exit 1
}

# Check if logged in
try {
    $account = az account show 2>&1 | ConvertFrom-Json
    $SUBSCRIPTION = $account.name
    Write-Info "Using Azure subscription: $SUBSCRIPTION"
} catch {
    Write-Error-Custom "Not logged in to Azure. Please run 'az login' first."
    exit 1
}

# Confirm deployment
Write-Host ""
Write-Host "This script will create the following resources:"
Write-Host "  - Resource Group: $RESOURCE_GROUP"
Write-Host "  - Location: $LOCATION"
Write-Host "  - PostgreSQL Server: $POSTGRES_SERVER"
Write-Host "  - Database: $POSTGRES_DB"
Write-Host "  - App Service: $WEB_APP_NAME"
Write-Host ""
$confirm = Read-Host "Continue with deployment? (y/n)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Info "Deployment cancelled."
    exit 0
}

# ==============================================================================
# Step 1: Create Resource Group
# ==============================================================================

Write-Step "Creating Resource Group: $RESOURCE_GROUP"

$groupExists = az group exists --name $RESOURCE_GROUP
if ($groupExists -eq 'true') {
    Write-Info "Resource group already exists. Skipping..."
} else {
    az group create `
        --name $RESOURCE_GROUP `
        --location $LOCATION `
        --output none
    Write-Success "Resource group created successfully"
}

# ==============================================================================
# Step 2: Create PostgreSQL Flexible Server
# ==============================================================================

Write-Step "Creating PostgreSQL Flexible Server: $POSTGRES_SERVER"

try {
    az postgres flexible-server show `
        --resource-group $RESOURCE_GROUP `
        --name $POSTGRES_SERVER `
        --output none 2>$null
    Write-Info "PostgreSQL server already exists. Skipping creation..."
} catch {
    Write-Info "This may take 5-10 minutes..."

    az postgres flexible-server create `
        --resource-group $RESOURCE_GROUP `
        --name $POSTGRES_SERVER `
        --location $LOCATION `
        --admin-user $POSTGRES_ADMIN_USER `
        --admin-password $POSTGRES_ADMIN_PASSWORD `
        --sku-name $POSTGRES_SKU `
        --storage-size $POSTGRES_STORAGE_SIZE `
        --version $POSTGRES_VERSION `
        --public-access "0.0.0.0-255.255.255.255" `
        --output none

    Write-Success "PostgreSQL server created successfully"
}

# Create database
Write-Step "Creating database: $POSTGRES_DB"

try {
    az postgres flexible-server db show `
        --resource-group $RESOURCE_GROUP `
        --server-name $POSTGRES_SERVER `
        --database-name $POSTGRES_DB `
        --output none 2>$null
    Write-Info "Database already exists. Skipping..."
} catch {
    az postgres flexible-server db create `
        --resource-group $RESOURCE_GROUP `
        --server-name $POSTGRES_SERVER `
        --database-name $POSTGRES_DB `
        --output none

    Write-Success "Database created successfully"
}

# Configure firewall
Write-Step "Configuring firewall rules..."

az postgres flexible-server firewall-rule create `
    --resource-group $RESOURCE_GROUP `
    --name $POSTGRES_SERVER `
    --rule-name AllowAzureServices `
    --start-ip-address "0.0.0.0" `
    --end-ip-address "0.0.0.0" `
    --output none 2>$null

Write-Success "Firewall configured"

# Build connection string
$POSTGRES_HOST = "$POSTGRES_SERVER.postgres.database.azure.com"
$DATABASE_URL = "postgresql://$POSTGRES_ADMIN_USER`:$POSTGRES_ADMIN_PASSWORD@$POSTGRES_HOST`:5432/$POSTGRES_DB`?sslmode=require"

Write-Info "PostgreSQL connection string configured"

# ==============================================================================
# Step 3: Create App Service Plan
# ==============================================================================

Write-Step "Creating App Service Plan: $APP_SERVICE_PLAN"

try {
    az appservice plan show `
        --resource-group $RESOURCE_GROUP `
        --name $APP_SERVICE_PLAN `
        --output none 2>$null
    Write-Info "App Service Plan already exists. Skipping..."
} catch {
    az appservice plan create `
        --resource-group $RESOURCE_GROUP `
        --name $APP_SERVICE_PLAN `
        --location $LOCATION `
        --sku $APP_SERVICE_SKU `
        --is-linux `
        --output none

    Write-Success "App Service Plan created successfully"
}

# ==============================================================================
# Step 4: Create Web App
# ==============================================================================

Write-Step "Creating Web App: $WEB_APP_NAME"

try {
    az webapp show `
        --resource-group $RESOURCE_GROUP `
        --name $WEB_APP_NAME `
        --output none 2>$null
    Write-Info "Web App already exists. Skipping creation..."
} catch {
    az webapp create `
        --resource-group $RESOURCE_GROUP `
        --plan $APP_SERVICE_PLAN `
        --name $WEB_APP_NAME `
        --runtime "PYTHON:$PYTHON_VERSION" `
        --output none

    Write-Success "Web App created successfully"
}

# ==============================================================================
# Step 5: Configure App Settings
# ==============================================================================

Write-Step "Configuring application settings..."

az webapp config appsettings set `
    --resource-group $RESOURCE_GROUP `
    --name $WEB_APP_NAME `
    --settings `
        "DATABASE_URL=$DATABASE_URL" `
        "API_VERSION=v1" `
        "DEBUG=false" `
        "LOG_LEVEL=INFO" `
        'CORS_ORIGINS=["*"]' `
        "PAGINATION_DEFAULT_LIMIT=100" `
        "PAGINATION_MAX_LIMIT=1000" `
        "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
        "WEBSITE_HTTPLOGGING_RETENTION_DAYS=7" `
    --output none

Write-Success "App settings configured"

# Configure startup command
Write-Step "Configuring startup command..."

az webapp config set `
    --resource-group $RESOURCE_GROUP `
    --name $WEB_APP_NAME `
    --startup-file "cd api && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" `
    --output none

Write-Success "Startup command configured"

# ==============================================================================
# Step 6: Deploy Application Code
# ==============================================================================

Write-Step "Deploying application code..."

Write-Info "Creating deployment package..."

# Create temporary directory
$DEPLOY_DIR = New-Item -ItemType Directory -Path "$env:TEMP\marketingiq_deploy_$(Get-Date -Format 'yyyyMMddHHmmss')" -Force

# Copy necessary files
Copy-Item -Path "api" -Destination $DEPLOY_DIR -Recurse -Force
Copy-Item -Path "requirements.txt" -Destination $DEPLOY_DIR -Force
if (Test-Path "marketing_warehouse.db") {
    Copy-Item -Path "marketing_warehouse.db" -Destination $DEPLOY_DIR -Force
}

# Create deployment zip
$zipPath = "$DEPLOY_DIR\deploy.zip"
Compress-Archive -Path "$DEPLOY_DIR\*" -DestinationPath $zipPath -Force

Write-Info "Uploading to Azure (this may take a few minutes)..."

az webapp deployment source config-zip `
    --resource-group $RESOURCE_GROUP `
    --name $WEB_APP_NAME `
    --src $zipPath `
    --output none

# Cleanup
Remove-Item -Path $DEPLOY_DIR -Recurse -Force

Write-Success "Application deployed successfully"

# ==============================================================================
# Step 7: Restart Web App
# ==============================================================================

Write-Step "Restarting web app..."

az webapp restart `
    --resource-group $RESOURCE_GROUP `
    --name $WEB_APP_NAME `
    --output none

Write-Success "Web app restarted"

Write-Info "Waiting for app to start (30 seconds)..."
Start-Sleep -Seconds 30

# ==============================================================================
# Deployment Complete
# ==============================================================================

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Resource Information:"
Write-Host "  Resource Group: $RESOURCE_GROUP"
Write-Host "  Location: $LOCATION"
Write-Host ""
Write-Host "Database:"
Write-Host "  Server: $POSTGRES_HOST"
Write-Host "  Database: $POSTGRES_DB"
Write-Host "  Username: $POSTGRES_ADMIN_USER"
Write-Host "  Password: $POSTGRES_ADMIN_PASSWORD"
Write-Host ""
Write-Host "Web Application:"
Write-Host "  URL: https://$WEB_APP_NAME.azurewebsites.net"
Write-Host "  API Docs: https://$WEB_APP_NAME.azurewebsites.net/docs"
Write-Host "  Health Check: https://$WEB_APP_NAME.azurewebsites.net/health"
Write-Host ""
Write-Host "Next Steps:"
Write-Host "  1. Test the health endpoint:"
Write-Host "     curl https://$WEB_APP_NAME.azurewebsites.net/health"
Write-Host ""
Write-Host "  2. View API documentation:"
Write-Host "     start https://$WEB_APP_NAME.azurewebsites.net/docs"
Write-Host ""
Write-Host "  3. View application logs:"
Write-Host "     az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
Write-Host ""
Write-Host "Cost Estimate: ~`$25/month"
Write-Host ""

# Save credentials
$CREDS_FILE = "azure_credentials.txt"
@"
Azure MarketingIQ Deployment Credentials
Generated: $(Get-Date)

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

Cost: ~`$25/month
"@ | Out-File -FilePath $CREDS_FILE -Encoding UTF8

Write-Success "Credentials saved to: $CREDS_FILE"
Write-Info "Keep this file secure and do not commit to git!"

Write-Host ""
Write-Info "Testing health endpoint..."
Start-Sleep -Seconds 10

try {
    $response = Invoke-WebRequest -Uri "https://$WEB_APP_NAME.azurewebsites.net/health" -UseBasicParsing -TimeoutSec 10
    Write-Success "Health check passed! Application is running."
} catch {
    Write-Info "Health check failed. The app may still be starting. Check logs with:"
    Write-Host "    az webapp log tail --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME"
}

Write-Host ""
Write-Success "Deployment script completed!"
