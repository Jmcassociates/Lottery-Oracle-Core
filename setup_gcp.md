# JMc - [2026-03-18] - GCP Architecture & Infrastructure Mapping

The Oracle is moving from a localized Docker environment to a scalable, serverless Google Cloud Platform (GCP) architecture. This document maps out the specific GCP services and the steps required to provision the infrastructure before the GitHub Actions CI/CD pipeline can be executed.

## 1. Core GCP Infrastructure

The application will be deployed across the following Google Cloud services:

*   **Google Cloud Run:** Serverless container execution. We will deploy two separate services: `oracle-backend` (FastAPI) and `oracle-frontend` (React/Nginx). Cloud Run scales to zero to save costs and scales up automatically during traffic spikes.
*   **Google Cloud SQL (PostgreSQL):** The managed relational database. We are migrating away from the fragile local SQLite volume (`lottery.db`) to a hardened PostgreSQL instance. Cloud Run connects to Cloud SQL via a secure, private proxy.
*   **Google Artifact Registry (GAR):** The private container image repository where GitHub Actions will push the compiled Docker images before deploying them to Cloud Run.
*   **Google Cloud Scheduler:** The serverless cron job execution service. It will replace the internal `APScheduler` to trigger the nightly `sync_to_db` processes via authenticated HTTP endpoints.

## 2. Infrastructure Setup & Provisioning Checklist

Before pushing code to trigger the `.github/workflows/deploy.yml` pipeline, the following steps must be executed manually or via Terraform to prepare the GCP environment.

### A. Project & APIs
1.  Create a new GCP Project (e.g., `moderncyph3r-oracle`).
2.  Enable the required APIs:
    *   Cloud Run API (`run.googleapis.com`)
    *   Artifact Registry API (`artifactregistry.googleapis.com`)
    *   Cloud SQL Admin API (`sqladmin.googleapis.com`)
    *   Cloud Scheduler API (`cloudscheduler.googleapis.com`)

### B. Database (Cloud SQL)
1.  Provision a Cloud SQL instance (PostgreSQL 15+).
    *   Tier: `db-f1-micro` (for development/pilot) or `db-custom-1-3840` (for production).
2.  Create a database named `lottery_oracle`.
3.  Create a database user and generate a secure password.
4.  Construct the SQLAlchemy connection string: 
    `postgresql+pg8000://<USER>:<PASSWORD>@/<DATABASE>?unix_sock=/cloudsql/<PROJECT_ID>:<REGION>:<INSTANCE_NAME>/.s.PGSQL.5432`

### C. Artifact Registry
1.  Create a new Docker repository in Artifact Registry.
    *   Name: `lottery-oracle`
    *   Format: `Docker`
    *   Region: `us-east1` (or your preferred region).

### D. Service Account & Security (GitHub Actions Integration)
1.  Create a new GCP Service Account (e.g., `github-actions-deployer`).
2.  Grant the Service Account the following IAM roles:
    *   `Cloud Run Admin` (to deploy the containers)
    *   `Artifact Registry Writer` (to push images)
    *   `Service Account User` (required to act as the compute service account)
3.  Generate a JSON key for this Service Account.

## 3. GitHub Secrets Configuration

The GitHub Actions pipeline (`deploy.yml`) relies on the following secrets being securely injected into the repository:

*   `GCP_PROJECT_ID`: The exact ID of the Google Cloud Project.
*   `GCP_SA_KEY`: The raw JSON string of the Service Account key generated in Step 2.D.
*   `PROD_DATABASE_URL`: The fully constructed PostgreSQL connection string for Cloud SQL.
*   `JWT_SECRET`: A secure, randomly generated string for FastAPI authentication token signing.

Once this infrastructure is provisioned and the secrets are loaded into GitHub, pushing to the `main` branch will autonomously test, build, and deploy the entire Oracle platform to the cloud.