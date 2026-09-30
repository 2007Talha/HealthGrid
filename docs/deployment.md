# Swasthya Records — Production Deployment Guide

**Target Platform**: Google Cloud Run  
**Region**: `asia-south1` (Mumbai)  
**GCP Project**: `arcadeaiagent`  

---

## 1. Prerequisites

1. **Google Cloud SDK (`gcloud`)** installed and authenticated:
   ```bash
   gcloud auth login
   gcloud config set project arcadeaiagent
   ```
2. **Required GCP APIs Enabled**:
   ```bash
   gcloud services enable \
     run.googleapis.com \
     artifactregistry.googleapis.com \
     bigquery.googleapis.com \
     aiplatform.googleapis.com
   ```
3. **Docker** installed for local container building and testing.

---

## 2. Environment Variables Configuration

Copy `.env.example` to `.env` and populate:

| Variable | Recommended Value | Description |
| :--- | :--- | :--- |
| `GCP_PROJECT_ID` | `arcadeaiagent` | Google Cloud Project ID |
| `GCP_REGION` | `asia-south1` | Deployment region (Mumbai) |
| `BIGQUERY_DATASET` | `arcadeaiagent.swasthyagrid` | Analytical BigQuery dataset |
| `ALLOWED_ORIGINS` | `http://localhost:5173,https://swasthya-frontend-*.run.app` | Allowed CORS origins |
| `RATE_LIMIT_PER_MINUTE`| `60` | Sliding-window requests/min per IP |
| `ENVIRONMENT` | `production` | Environment mode (`development`, `demo`, `production`) |

---

## 3. Automated Cloud Run Deployment Script

Execute the production deployment script located in `scripts/deploy_cloud_run.sh`:

```bash
chmod +x scripts/deploy_cloud_run.sh
./scripts/deploy_cloud_run.sh
```

### Script Execution Steps:
1. **Creates Artifact Registry Repository**:
   ```bash
   gcloud artifacts repositories create swasthya-repo \
     --repository-format=docker \
     --location=asia-south1
   ```
2. **Builds & Pushes Backend Container**:
   ```bash
   docker build -t asia-south1-docker.pkg.dev/arcadeaiagent/swasthya-repo/swasthya-backend:latest -f backend/Dockerfile .
   docker push asia-south1-docker.pkg.dev/arcadeaiagent/swasthya-repo/swasthya-backend:latest
   ```
3. **Deploys Backend to Cloud Run**:
   ```bash
   gcloud run deploy swasthya-backend \
     --image asia-south1-docker.pkg.dev/arcadeaiagent/swasthya-repo/swasthya-backend:latest \
     --region asia-south1 \
     --platform managed \
     --allow-unauthenticated \
     --memory 1Gi \
     --cpu 1 \
     --min-instances 1 \
     --max-instances 10
   ```
4. **Builds & Pushes Frontend Container**:
   ```bash
   docker build --build-arg VITE_API_URL=https://swasthya-backend-<hash>.run.app -t asia-south1-docker.pkg.dev/arcadeaiagent/swasthya-repo/swasthya-frontend:latest -f frontend/Dockerfile .
   docker push asia-south1-docker.pkg.dev/arcadeaiagent/swasthya-repo/swasthya-frontend:latest
   ```
5. **Deploys Frontend to Cloud Run**:
   ```bash
   gcloud run deploy swasthya-frontend \
     --image asia-south1-docker.pkg.dev/arcadeaiagent/swasthya-repo/swasthya-frontend:latest \
     --region asia-south1 \
     --platform managed \
     --allow-unauthenticated
   ```

---

## 4. Local Container Testing via Docker Compose

Test the full production stack locally before cloud deployment:

```bash
docker-compose up --build
```

Access services:
* **Frontend**: `http://localhost:3000`
* **Backend**: `http://localhost:8000`
* **Swagger API Docs**: `http://localhost:8000/docs`

---

## 5. Health & Liveness Verification

After deployment, verify that all probes report healthy:

```bash
# Liveness Probe (Fast HTTP 200)
curl https://<backend-url>/health

# Dependency Readiness Probe (Checks DB, BigQuery, Gemini, Simulator)
curl https://<backend-url>/health/dependencies
```

Expected output:
```json
{
  "status": "ok",
  "health": "HEALTHY",
  "code": 200
}
```
