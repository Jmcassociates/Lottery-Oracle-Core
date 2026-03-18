# Oracle GCP Deployment & GitHub Actions Guide

We have fully automated the GCP infrastructure build using `gcloud` locally, except for the final Service Account key generation which was blocked by your organization policy. 

Here are the precise, step-by-step instructions to clear the blocker, get the JSON key, and connect your repository to Google Cloud Platform.

### Step 1: Temporarily Lift the Key Creation Block
Because your Google Workspace/Cloud Identity admin has secured your organization, you cannot create long-lived JSON keys. You must temporarily disable this policy.

1. Open your web browser and go to the **[Google Cloud Console](https://console.cloud.google.com/)**.
2. Ensure you have the `law-of-large-numbers` project selected in the top drop-down menu.
3. In the search bar at the top, type **Organization Policies** and click it.
4. Filter or search the list for `constraints/iam.disableServiceAccountKeyCreation` (or "Disable Service Account Key Creation").
5. Click on the policy to view its details.
6. Click **Edit** at the top. 
7. Change the enforcement from `Enforce` to **Not Enforced** (or "Customize" and select "Off").
8. Click **Save**. *Wait about 60 seconds for the policy change to propagate across GCP's global network.*

### Step 2: Generate the JSON Key
Once the policy is lifted, open your Mac terminal and run this exact command. It will download the JSON key to your home directory.

```bash
gcloud iam service-accounts keys create ~/gcp-github-key.json \
    --iam-account=github-actions-deployer@law-of-large-numbers.iam.gserviceaccount.com \
    --project=law-of-large-numbers
```

*(Crucial: Once you have the file, go back to the Google Cloud Console and re-enable the `Disable Service Account Key Creation` policy to lock your organization back down!)*

### Step 3: Connect GitHub to Google Cloud
You now have all four secrets required to make the `.github/workflows/deploy.yml` pipeline work. 

1. Open your web browser and go to your GitHub repository for this project.
2. Click on **Settings** (the gear icon at the top).
3. On the left sidebar, scroll down to **Secrets and variables** and click **Actions**.
4. Click the green **New repository secret** button and add these four exact secrets:

*   **Name:** `GCP_PROJECT_ID`
    *   **Value:** `law-of-large-numbers`
*   **Name:** `GCP_SA_KEY`
    *   **Value:** *(Open `~/gcp-github-key.json` in a text editor, copy the ENTIRE contents of the file, and paste it here).*
*   **Name:** `JWT_SECRET`
    *   **Value:** `067d1613e2ec7612425fc230a9f0efa447a028f26451f6c57ea0a2e6f968f72b`
*   **Name:** `PROD_DATABASE_URL`
    *   **Value:** `postgresql+pg8000://postgres:MondernCYPH3r08125!@/lottery_oracle?unix_sock=/cloudsql/law-of-large-numbers:us-east1:oracle-db-instance/.s.PGSQL.5432`

### Step 4: Fire the Pipeline
Once those four secrets are saved in GitHub, your pipeline is armed.

1. In your local Mac terminal, stage all the files we created:
   ```bash
   git add .
   ```
2. Commit the new architecture:
   ```bash
   git commit -m "feat: The Stage C Expansion (New York) and GCP CI/CD Pipeline"
   ```
3. Push to GitHub:
   ```bash
   git push origin main
   ```

The moment you push, go to the **Actions** tab in your GitHub repository. You will see the "Oracle CI/CD Pipeline" spin up. It will run the mathematical unit tests, build the Docker images, push them to Artifact Registry, and deploy them to Cloud Run.
