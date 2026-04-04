# JMc - [2026-03-18] - GCP Architecture & Infrastructure Mapping

The Oracle is moving from a localized Docker environment to a scalable, serverless Google Cloud Platform (GCP) architecture. This document maps out the specific GCP services and the steps required to provision the infrastructure before the GitHub Actions CI/CD pipeline can be executed.

## 1. Core GCP Infrastructure

The application will be deployed across the following Google Cloud services:

*   **Google Cloud Run (Services):** Serverless container execution for the web interfaces. We deploy two services: `oracle-backend` (FastAPI) and `oracle-frontend` (React/Nginx). These are configured to scale to zero and use CPU throttling when idle to minimize costs.
*   **Google Cloud Run (Jobs):** Standalone execution for the high-intensity synchronization protocol (`oracle-sync-job`). Unlike services, Jobs run to completion and then stop billing immediately. This prevents the "Always-On CPU" tax.
*   **Google Cloud SQL (PostgreSQL):** The managed relational database. We are migrating away from the fragile local SQLite volume (`lottery.db`) to a hardened PostgreSQL instance.
*   **Google Artifact Registry (GAR):** The private container image repository.
*   **Google Cloud Scheduler:** Triggers the `oracle-sync-job` nightly at 3:00 AM via the Cloud Run Jobs API.

## 2. Infrastructure Setup & Provisioning Checklist

### A. Project & APIs
1.  Enable the required APIs:
    *   Cloud Run API (`run.googleapis.com`)
    *   Artifact Registry API (`artifactregistry.googleapis.com`)
    *   Cloud SQL Admin API (`sqladmin.googleapis.com`)
    *   Cloud Scheduler API (`cloudscheduler.googleapis.com`)

### B. Database (Cloud SQL)
1.  Provision a Cloud SQL instance (PostgreSQL 15+).
    *   Tier: `db-f1-micro` (Cost optimized).

### C. Service Account & IAM (Crucial for Jobs)
1.  Ensure the `github-actions-deployer` has the following roles:
    *   `Cloud Run Admin`
    *   `Artifact Registry Writer`
    *   `Service Account User`
2.  The `oracle-backend` service account needs the `Cloud Run Invoker` and `Cloud Run Developer` roles (or specifically `run.jobs.run`) to trigger the Job manually from the War Room.

## 3. GitHub Secrets Configuration

*   `GCP_PROJECT_ID`: The exact ID of the Google Cloud Project.
*   `GCP_SA_KEY`: The raw JSON string of the Service Account key.
*   `PROD_DATABASE_URL`: PostgreSQL connection string.
*   `JWT_SECRET`: Secret for auth tokens.
*   `GHL_WEBHOOK_SECRET`: Secret for GHL verification.
*   `SMTP_*`: Mail server credentials.