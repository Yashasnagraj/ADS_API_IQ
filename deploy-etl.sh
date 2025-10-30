#!/bin/bash
# Deploy ETL Pipeline to Google Cloud Run
# Usage: ./deploy-etl.sh [PROJECT_ID]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${1:-your-project-id}"
REGION="us-central1"
SERVICE_NAME="ads-etl-pipeline"
REPOSITORY="ads-etl"
IMAGE_NAME="ads-etl"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Google Ads ETL Pipeline Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo -e "${YELLOW}Setting project: ${PROJECT_ID}${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    cloudscheduler.googleapis.com

# Create Artifact Registry repository
echo -e "${YELLOW}Creating Artifact Registry repository...${NC}"
gcloud artifacts repositories create ${REPOSITORY} \
    --repository-format=docker \
    --location=${REGION} \
    --description="Docker repository for Google Ads ETL pipeline" \
    || echo "Repository already exists"

# Upload google-ads.yaml to Secret Manager
echo -e "${YELLOW}Uploading google-ads.yaml to Secret Manager...${NC}"
if [ -f "google-ads.yaml" ]; then
    gcloud secrets create google-ads-yaml --data-file=google-ads.yaml \
        || gcloud secrets versions add google-ads-yaml --data-file=google-ads.yaml
    echo -e "${GREEN}✓ Secret uploaded${NC}"
else
    echo -e "${RED}Error: google-ads.yaml not found${NC}"
    exit 1
fi

# Build and deploy using Cloud Build
echo -e "${YELLOW}Building and deploying with Cloud Build...${NC}"
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_REGION=${REGION},_REPOSITORY=${REPOSITORY},_SERVICE_NAME=${SERVICE_NAME}

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --region=${REGION} \
    --format='value(status.url)')

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Completed Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Service URL: ${SERVICE_URL}"
echo ""

# Set up Cloud Scheduler
echo -e "${YELLOW}Setting up Cloud Scheduler for daily runs...${NC}"

# Create service accounts
SA_RUNNER="etl-runner"
SA_SCHEDULER="etl-scheduler"
SA_RUNNER_EMAIL="${SA_RUNNER}@${PROJECT_ID}.iam.gserviceaccount.com"
SA_SCHEDULER_EMAIL="${SA_SCHEDULER}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Creating service accounts..."
gcloud iam service-accounts create ${SA_RUNNER} \
    --display-name="ETL Runner Service Account" \
    || echo "Runner service account already exists"

gcloud iam service-accounts create ${SA_SCHEDULER} \
    --display-name="ETL Scheduler Service Account" \
    || echo "Scheduler service account already exists"

# Grant permissions to service accounts
echo "Granting permissions..."

# Runner service account needs Secret Manager access
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_RUNNER_EMAIL}" \
    --role="roles/secretmanager.secretAccessor" \
    || echo "Already has secret access"

# Scheduler service account needs Cloud Run Invoker
gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
    --region=${REGION} \
    --member="serviceAccount:${SA_SCHEDULER_EMAIL}" \
    --role="roles/run.invoker" \
    || echo "Already has invoker role"

# Create Cloud Scheduler job (runs daily at 2 AM UTC)
gcloud scheduler jobs create http etl-daily-run \
    --location=${REGION} \
    --schedule="0 2 * * *" \
    --uri="${SERVICE_URL}" \
    --http-method=POST \
    --oidc-service-account-email="${SA_SCHEDULER_EMAIL}" \
    --oidc-token-audience="${SERVICE_URL}" \
    --time-zone="UTC" \
    --description="Run Google Ads ETL pipeline daily at 2 AM UTC" \
    || gcloud scheduler jobs update http etl-daily-run \
        --location=${REGION} \
        --schedule="0 2 * * *" \
        --uri="${SERVICE_URL}" \
        --oidc-service-account-email="${SA_SCHEDULER_EMAIL}"

echo -e "${GREEN}✓ Cloud Scheduler configured (runs daily at 2 AM UTC)${NC}"
echo ""
echo -e "${YELLOW}Manual Trigger:${NC}"
echo "gcloud run jobs execute ${SERVICE_NAME} --region=${REGION}"
echo ""
echo -e "${YELLOW}View Logs:${NC}"
echo "gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}\" --limit 50"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
