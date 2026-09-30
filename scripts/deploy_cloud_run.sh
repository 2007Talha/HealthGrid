#!/usr/bin/env bash
# ==============================================================================
# SwasthyaGrid AI — Google Cloud Run Deployment Script
# GCP Project: arcadeaiagent | Region: asia-south1
# Track 3: Smart Health & Supply Chain Resilience
# ==============================================================================

set -e

PROJECT_ID="arcadeaiagent"
REGION="asia-south1"
SERVICE_NAME="swasthyagrid"
SA_NAME="swasthyagrid-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "================================================================="
echo "Deploying SwasthyaGrid AI to Google Cloud Run"
echo "Project: ${PROJECT_ID} | Region: ${REGION}"
echo "================================================================="

# 1. Ensure GCP Project is selected
gcloud config set project "${PROJECT_ID}"

# 2. Enable required Google Cloud APIs
echo "--> Enabling required GCP APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    bigquery.googleapis.com \
    aiplatform.googleapis.com \
    secretmanager.googleapis.com \
    logging.googleapis.com

# 3. Create Least-Privilege Service Account (if not existing)
echo "--> Verifying Service Account with least-privilege IAM..."
if ! gcloud iam service-accounts describe "${SA_EMAIL}" >/dev/null 2>&1; then
    gcloud iam service-accounts create "${SA_NAME}" \
        --description="Least-privilege execution service account for SwasthyaGrid AI" \
        --display-name="SwasthyaGrid Service Account"
fi

# 4. Bind Least-Privilege IAM Roles (No Owner or Editor privileges)
echo "--> Granting least-privilege roles to ${SA_EMAIL}..."
ROLES=(
    "roles/bigquery.dataViewer"
    "roles/bigquery.jobUser"
    "roles/aiplatform.user"
    "roles/logging.logWriter"
    "roles/secretmanager.secretAccessor"
)

for ROLE in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="${ROLE}" --quiet >/dev/null
done

# 5. Build and Deploy Backend to Cloud Run
echo "--> Building container and deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}-api" \
    --source . \
    --region "${REGION}" \
    --service-account "${SA_EMAIL}" \
    --allow-unauthenticated \
    --min-instances 1 \
    --max-instances 10 \
    --memory 1Gi \
    --cpu 1 \
    --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},BIGQUERY_DATASET=swasthyagrid,BIGQUERY_LOCATION=${REGION},ENVIRONMENT=production"

BACKEND_URL=$(gcloud run services describe "${SERVICE_NAME}-api" --platform managed --region "${REGION}" --format 'value(status.url)')
echo "--> Backend successfully deployed: ${BACKEND_URL}"

# 6. Verify Health Check
echo "--> Probing backend health..."
curl -s "${BACKEND_URL}/health" || true

echo "================================================================="
echo "SwasthyaGrid AI Deployment Complete!"
echo "Production API Gateway: ${BACKEND_URL}"
echo "Interactive Swagger Docs: ${BACKEND_URL}/docs"
echo "================================================================="
