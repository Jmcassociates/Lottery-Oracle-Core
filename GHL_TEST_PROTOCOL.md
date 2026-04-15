# JMc - [2026-04-09] - The "Cold Start" Telemetry Protocol

This document outlines the precise 5-step testing sequence required to validate the end-to-end integration between the Oracle (GCP) and GoHighLevel (GHL).

**Prerequisite:** Ensure your GHL Inbound Webhook workflow is configured to catch and route based on the `status` and `tier` variables we transmit.

---

### 🧪 Step 1: The Lure (GHL Opt-in)
*   **Action**: Open an **Incognito/Private** browser window. Go to your GHL landing page and fill out the "Oracle Opt-in" form using a burner email (e.g., `james+test_apr9@moderncyph3r.com`).
*   **Expected Result**: GHL creates the contact, assigns them to the **"New Lead"** pipeline stage, and fires the automated email containing the PDF manifesto link.

### 🧪 Step 2: The Handshake (Identity Bridge)
*   **Action**: Open the automated email and click the Manifesto link. (Ensure the link format in GHL is set to: `https://oracleapp.moderncyph3r.com/manifesto?email={{contact.email}}`).
*   **Expected Result**:
    1.  The Oracle app opens and displays the "Initializing Handshake..." screen for ~2 seconds.
    2.  The PDF (`ORACLE_DEAD_ZONE_REPORT.pdf`) automatically downloads to your machine.
    3.  **IN GHL**: The backend fires an inbound webhook (`status: technical_prospect`). Your GHL workflow should immediately jump the contact card to the **"Technical Prospect"** stage.

### 🧪 Step 3: The Acquisition (Account Registration)
*   **Action**: The Identity Bridge will have automatically redirected you to the `/register` page with your email pre-filled. Enter a secure password and click "Start Playing Smarter."
*   **Expected Result**:
    1.  You are provisioned into the database and redirected to the Oracle Dashboard.
    2.  **IN GHL**: The backend fires an inbound webhook (`tier: free`). Your GHL workflow should jump the contact card to the **"Vault User: Free Tier"** stage.

### 🧪 Step 4: The Revenue (Stripe Purchase)
*   **Action**: Go to your GHL 2-step order form funnel. Purchase the Pro Tier using the *exact same test email*.
*   **Expected Result**:
    1.  GHL fires the `ghl-provision` outbound webhook to our backend (`/api/auth/webhook/ghl-provision`).
    2.  **IN THE ORACLE**: The backend upgrades your database record to `pro` and dispatches the Magic Link via SMTP.
    3.  Refresh your Oracle Dashboard—you should see **"PRO TIER ACTIVE"** in the top right.

### 🧪 Step 5: The Killswitch (Admin Compliance)
*   **Action**: Log in to the Oracle using your master architect credentials (`james@moderncyph3r.com`). Navigate to the **Admin Dashboard**, locate the burner email account, and toggle their status to **Inactive**.
*   **Expected Result**:
    1.  **IN GHL**: The backend fires an inbound webhook (`status: inactive`). Your GHL workflow should jump the contact card to the **"Inactive / Banned"** stage.
    2.  Attempting to log in as the test user should return an "ACCOUNT DEACTIVATED" error.

---

**Method of the Madness (The Strategy)**
This protocol tests the full bi-directional circuit. If Step 2 or 3 fails to move the stage in GHL, the "Inbound" webhook routing in GHL needs mapping adjustments. If Step 4 fails, the GHL "Outbound" webhook isn't firing correctly on purchase.
