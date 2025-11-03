# ==============================================================================
# Azure Simple Deployment - Backend with SQLite Database
# ==============================================================================

$ErrorActionPreference = "Stop"

# ==============================================================================
# Configuration
# ==============================================================================

$LOCATION = "centralus"
$RESOURCE_GROUP = "marketingiq-rg"
$APP_SERVICE_PLAN = "marketingiq-plan"
$WEB_APP_NAME = "marketingiq-api-$(Get-Random -Minimum 1000 -Maximum 9999)"
$APP_SERVICE_SKU = "B1"  # Basic tier - ~$13/month
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

function Write-Success {
    param($Message)
    Write-Host "SUCCESS: " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

# ==============================================================================
# Pre-flight Checks
# ==============================================================================

Write-Step "Running pre-flight checks..."

if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Azure CLI is not installed" -ForegroundColor Red
    exit 1
}

try {
    $account = az account show 2>&1 | ConvertFrom-Json
    Write-Info "Using Azure subscription: $($account.name)"
} catch {
    Write-Host "ERROR: Not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

# Check if database exists
if (!(Test-Path "marketing_warehouse.db")) {
    Write-Host "ERROR: marketing_warehouse.db not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Deploying:"
Write-Host "  - Resource Group: $RESOURCE_GROUP"
Write-Host "  - App Service: $WEB_APP_NAME"
Write-Host "  - Database: SQLite (marketing_warehouse.db)"
Write-Host "  - Location: $LOCATION"
Write-Host "  - Cost: ~`$13/month"
Write-Host ""

# ==============================================================================
# Step 1: Create Resource Group
# ==============================================================================

Write-Step "Creating Resource Group..."

$groupExists = az group exists --name $RESOURCE_GROUP
if ($groupExists -eq 'true') {
    Write-Info "Resource group exists"
} else {
    az group create --name $RESOURCE_GROUP --location $LOCATION --output none
    Write-Success "Resource group created"
}

# ==============================================================================
# Step 2: Create App Service Plan
# ==============================================================================

Write-Step "Creating App Service Plan..."

try {
    az appservice plan show --resource-group $RESOURCE_GROUP --name $APP_SERVICE_PLAN --output none 2>$null
    Write-Info "App Service Plan exists"
} catch {
    az appservice plan create `
        --resource-group $RESOURCE_GROUP `
        --name $APP_SERVICE_PLAN `
        --location $LOCATION `
        --sku $APP_SERVICE_SKU `
        --is-linux `
        --output none
    Write-Success "App Service Plan created"
}

# ==============================================================================
# Step 3: Create Web App
# ==============================================================================

Write-Step "Creating Web App: $WEB_APP_NAME"

az webapp create `
    --resource-group $RESOURCE_GROUP `
    --plan $APP_SERVICE_PLAN `
    --name $WEB_APP_NAME `
    --runtime "PYTHON:$PYTHON_VERSION" `
    --output none

Write-Success "Web App created"

# ==============================================================================
# Step 4: Configure App Settings
# ==============================================================================

Write-Step "Configuring app settings..."

az webapp config appsettings set `
    --resource-group $RESOURCE_GROUP `
    --name $WEB_APP_NAME `
    --settings `
        "DATABASE_URL=sqlite:///./marketing_warehouse.db" `
        "API_VERSION=v1" `
        "DEBUG=false" `
        "LOG_LEVEL=INFO" `
        'CORS_ORIGINS=["*"]' `
        "PAGINATION_DEFAULT_LIMIT=100" `
        "PAGINATION_MAX_LIMIT=1000" `
        "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
    --output none

Write-Success "App settings configured"

# ==============================================================================
# Step 5: Prepare Deployment Package
# ==============================================================================

Write-Step "Preparing deployment package..."

# Create temp directory
$timestamp = Get-Date -Format 'yyyyMMddHHmmss'
$DEPLOY_DIR = New-Item -ItemType Directory -Path "$env:TEMP\marketingiq_$timestamp" -Force

Write-Info "Copying files..."

# Copy API directory
Copy-Item -Path "api" -Destination $DEPLOY_DIR -Recurse -Force

# Copy database to api directory (so it's accessible)
Copy-Item -Path "marketing_warehouse.db" -Destination "$DEPLOY_DIR\api\" -Force

# Copy requirements.txt to api directory
Copy-Item -Path "requirements.txt" -Destination "$DEPLOY_DIR\api\" -Force

# Create startup script in api directory
$startupScript = @"
#!/bin/bash
cd /home/site/wwwroot/api
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
"@

Set-Content -Path "$DEPLOY_DIR\api\startup.sh" -Value $startupScript

# Create .deployment file to tell Azure where to find files
$deploymentConfig = @"
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
"@

Set-Content -Path "$DEPLOY_DIR\.deployment" -Value $deploymentConfig

Write-Info "Creating zip file..."

# Change to api directory and zip its contents
$zipPath = "$env:TEMP\deploy_$timestamp.zip"
Compress-Archive -Path "$DEPLOY_DIR\api\*" -DestinationPath $zipPath -Force

Write-Success "Package ready"

# ==============================================================================
# Step 6: Deploy Code
# ==============================================================================

Write-Step "Deploying to Azure (this may take 3-5 minutes)..."

az webapp deployment source config-zip `
    --resource-group $RESOURCE_GROUP `
    --name $WEB_APP_NAME `
    --src $zipPath `
    --output none

Write-Success "Code deployed"

# ==============================================================================
# Step 7: Configure Startup Command
# ==============================================================================

Write-Step "Configuring startup command..."

az webapp config set `
    --resource-group $RESOURCE_GROUP `
    --name $WEB_APP_NAME `
    --startup-file "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" `
    --output none

Write-Success "Startup configured"

# ==============================================================================
# Step 8: Restart and Wait
# ==============================================================================

Write-Step "Restarting app..."

az webapp restart --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --output none

Write-Info "Waiting 45 seconds for app to start..."
Start-Sleep -Seconds 45

# Clean up temp files
Remove-Item -Path $DEPLOY_DIR -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path $zipPath -Force -ErrorAction SilentlyContinue

# ==============================================================================
# Deployment Complete
# ==============================================================================

$APP_URL = "https://$WEB_APP_NAME.azurewebsites.net"

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API:"
Write-Host "  URL: $APP_URL" -ForegroundColor Cyan
Write-Host "  Health: $APP_URL/health" -ForegroundColor Cyan
Write-Host "  API Docs: $APP_URL/docs" -ForegroundColor Cyan
Write-Host "  API Base: $APP_URL/api/v1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Resource Details:"
Write-Host "  Resource Group: $RESOURCE_GROUP"
Write-Host "  App Service: $WEB_APP_NAME"
Write-Host "  Location: $LOCATION"
Write-Host "  Database: SQLite (marketing_warehouse.db)"
Write-Host ""
Write-Host "Management Commands:"
Write-Host "  View logs: az webapp log tail -g $RESOURCE_GROUP -n $WEB_APP_NAME"
Write-Host "  Restart: az webapp restart -g $RESOURCE_GROUP -n $WEB_APP_NAME"
Write-Host "  SSH: az webapp ssh -g $RESOURCE_GROUP -n $WEB_APP_NAME"
Write-Host ""
Write-Host "Cost: ~`$13/month (Basic tier)"
Write-Host ""

# Save deployment info
$deploymentInfo = @"
MarketingIQ Backend Deployment
Generated: $(Get-Date)

Backend API:
  URL: $APP_URL
  Health: $APP_URL/health
  API Docs: $APP_URL/docs
  API Base: $APP_URL/api/v1

Azure Resources:
  Resource Group: $RESOURCE_GROUP
  App Service: $WEB_APP_NAME
  Location: $LOCATION
  Database: SQLite (marketing_warehouse.db)

Management:
  View logs: az webapp log tail -g $RESOURCE_GROUP -n $WEB_APP_NAME
  Restart: az webapp restart -g $RESOURCE_GROUP -n $WEB_APP_NAME
  SSH: az webapp ssh -g $RESOURCE_GROUP -n $WEB_APP_NAME

Cost: ~`$13/month
"@

Set-Content -Path "azure_deployment.txt" -Value $deploymentInfo
Write-Success "Deployment info saved to: azure_deployment.txt"

# ==============================================================================
# Test Health Endpoint
# ==============================================================================

Write-Host ""
Write-Step "Testing health endpoint..."

Start-Sleep -Seconds 10

try {
    $response = Invoke-RestMethod -Uri "$APP_URL/health" -TimeoutSec 30
    Write-Host ""
    Write-Success "Backend is healthy!"
    Write-Host "  Status: $($response.status)"
    Write-Host "  Database: $($response.database)"
    Write-Host "  Version: $($response.version)"
    Write-Host ""
    Write-Host "Next: Open $APP_URL/docs to see the API documentation" -ForegroundColor Yellow
} catch {
    Write-Host ""
    Write-Host "Health check couldn't connect yet. The app may still be starting." -ForegroundColor Yellow
    Write-Host "Wait 1-2 minutes, then try: curl $APP_URL/health" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "View logs: az webapp log tail -g $RESOURCE_GROUP -n $WEB_APP_NAME" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "Ready! Use the URL above to connect your frontend." -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
