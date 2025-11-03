# ==============================================================================
# Azure Free Tier Deployment - Backend with SQLite
# ==============================================================================

$ErrorActionPreference = "Continue"  # Continue on errors to see all messages

# Configuration
$RESOURCE_GROUP = "marketingiq-rg"
$APP_NAME = "marketingiq-api-$(Get-Random -Minimum 10000 -Maximum 99999)"
$LOCATION = "eastasia"  # Allowed region for your Azure subscription

Write-Host "==> Starting deployment..." -ForegroundColor Green
Write-Host "Resource Group: $RESOURCE_GROUP" -ForegroundColor Cyan
Write-Host "App Name: $APP_NAME" -ForegroundColor Cyan
Write-Host "Location: $LOCATION" -ForegroundColor Cyan
Write-Host ""

# Step 1: Ensure resource group exists
Write-Host "==> Checking resource group..." -ForegroundColor Yellow
az group create --name $RESOURCE_GROUP --location $LOCATION --output none 2>&1 | Out-Null
Write-Host "Resource group ready" -ForegroundColor Green

# Step 2: Create App Service with Free tier directly (up command)
Write-Host "==> Creating web app with FREE tier..." -ForegroundColor Yellow
Write-Host "This may take 2-3 minutes..." -ForegroundColor Gray

$result = az webapp up `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --runtime "PYTHON:3.11" `
    --sku FREE `
    --location $LOCATION `
    --os-type Linux `
    2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create web app" -ForegroundColor Red
    Write-Host $result

    # Try different location
    Write-Host ""
    Write-Host "Trying Southeast Asia location..." -ForegroundColor Yellow
    $LOCATION = "southeastasia"

    $result = az webapp up `
        --resource-group $RESOURCE_GROUP `
        --name $APP_NAME `
        --runtime "PYTHON:3.11" `
        --sku FREE `
        --location $LOCATION `
        --os-type Linux `
        2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed with Southeast Asia too" -ForegroundColor Red
        Write-Host $result
        exit 1
    }
}

Write-Host "Web app created!" -ForegroundColor Green

# Step 3: Deploy code
Write-Host "==> Preparing code for deployment..." -ForegroundColor Yellow

# Create deployment directory
$deployDir = "$env:TEMP\miq_deploy_$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -ItemType Directory -Path $deployDir -Force | Out-Null

# Copy api directory
Copy-Item -Path "api\*" -Destination $deployDir -Recurse -Force -Exclude "nul","NUL","__pycache__"

# Copy database
Copy-Item -Path "marketing_warehouse.db" -Destination $deployDir -Force

# Copy requirements
Copy-Item -Path "requirements.txt" -Destination $deployDir -Force

# Create startup command file
$startupCmd = "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
Set-Content -Path "$deployDir\startup.txt" -Value $startupCmd

Write-Host "Creating deployment package..." -ForegroundColor Gray
$zipFile = "$env:TEMP\deploy_$(Get-Date -Format 'yyyyMMddHHmmss').zip"
Compress-Archive -Path "$deployDir\*" -DestinationPath $zipFile -Force

Write-Host "==> Deploying code to Azure..." -ForegroundColor Yellow
az webapp deploy `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --src-path $zipFile `
    --type zip `
    2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "Code deployed!" -ForegroundColor Green
} else {
    Write-Host "WARNING: Deploy may have issues, continuing..." -ForegroundColor Yellow
}

# Step 4: Configure app settings
Write-Host "==> Configuring app settings..." -ForegroundColor Yellow

az webapp config appsettings set `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --settings `
        "DATABASE_URL=sqlite:///./marketing_warehouse.db" `
        "API_VERSION=v1" `
        "DEBUG=false" `
        "LOG_LEVEL=INFO" `
        'CORS_ORIGINS=["*"]' `
        "SCM_DO_BUILD_DURING_DEPLOYMENT=true" `
    --output none 2>&1 | Out-Null

Write-Host "Settings configured!" -ForegroundColor Green

# Step 5: Set startup command
Write-Host "==> Setting startup command..." -ForegroundColor Yellow

az webapp config set `
    --resource-group $RESOURCE_GROUP `
    --name $APP_NAME `
    --startup-file "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" `
    --output none 2>&1 | Out-Null

Write-Host "Startup command set!" -ForegroundColor Green

# Step 6: Restart app
Write-Host "==> Restarting app..." -ForegroundColor Yellow
az webapp restart --resource-group $RESOURCE_GROUP --name $APP_NAME --output none 2>&1 | Out-Null

Write-Host "Waiting for app to start (60 seconds)..." -ForegroundColor Gray
Start-Sleep -Seconds 60

# Cleanup
Remove-Item -Path $deployDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path $zipFile -Force -ErrorAction SilentlyContinue

# Final output
$APP_URL = "https://$APP_NAME.azurewebsites.net"

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your Backend API:" -ForegroundColor Cyan
Write-Host "  URL: $APP_URL" -ForegroundColor White
Write-Host "  Health: $APP_URL/health" -ForegroundColor White
Write-Host "  Docs: $APP_URL/docs" -ForegroundColor White
Write-Host "  API: $APP_URL/api/v1" -ForegroundColor White
Write-Host ""
Write-Host "Resource Details:" -ForegroundColor Cyan
Write-Host "  Resource Group: $RESOURCE_GROUP"
Write-Host "  App Name: $APP_NAME"
Write-Host "  Location: $LOCATION"
Write-Host "  Tier: FREE (no cost!)"
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "  Logs: az webapp log tail -g $RESOURCE_GROUP -n $APP_NAME"
Write-Host "  Restart: az webapp restart -g $RESOURCE_GROUP -n $APP_NAME"
Write-Host ""

# Save info
$info = @"
MarketingIQ Backend Deployment
Deployed: $(Get-Date)

Backend URL: $APP_URL
Health: $APP_URL/health
API Docs: $APP_URL/docs
API Base: $APP_URL/api/v1

Azure Resources:
Resource Group: $RESOURCE_GROUP
App Name: $APP_NAME
Location: $LOCATION
Tier: FREE

Management:
az webapp log tail -g $RESOURCE_GROUP -n $APP_NAME
az webapp restart -g $RESOURCE_GROUP -n $APP_NAME
"@

Set-Content -Path "azure_deployment.txt" -Value $info
Write-Host "Deployment info saved to: azure_deployment.txt" -ForegroundColor Green

# Test health
Write-Host ""
Write-Host "==> Testing health endpoint..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

try {
    $health = Invoke-RestMethod -Uri "$APP_URL/health" -TimeoutSec 30
    Write-Host ""
    Write-Host "SUCCESS! Backend is healthy!" -ForegroundColor Green
    Write-Host "  Status: $($health.status)" -ForegroundColor White
    Write-Host "  Database: $($health.database)" -ForegroundColor White
    Write-Host ""
    Write-Host "Open $APP_URL/docs to see your API!" -ForegroundColor Yellow
} catch {
    Write-Host ""
    Write-Host "App is still starting... wait 1-2 minutes then visit:" -ForegroundColor Yellow
    Write-Host "  $APP_URL/health" -ForegroundColor White
    Write-Host ""
    Write-Host "Check logs: az webapp log tail -g $RESOURCE_GROUP -n $APP_NAME" -ForegroundColor Gray
}

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
