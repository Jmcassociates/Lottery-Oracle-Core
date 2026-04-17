# Oracle Architecture: Phase 30 Verification & Hand-off

*JMc - [2026-04-16]*

## 1. The Situation
The Oracle's frontend and backend are hardened. The GoHighLevel (GHL) integration for user acquisition (Opt-in) and provisioning (Upgrade to Pro) is fully operational. 

The final mandate was to construct a secure, automated, and compliant **Cancellation Loop** that allows users to downgrade their subscription from inside the Oracle Dashboard without requiring manual admin intervention or exposing us to Stripe chargebacks.

## 2. The Complications
*   **GHL Paywalls:** Native Stripe cancellation actions inside GHL workflows are locked behind premium upgrades.
*   **Hallucinated Logic:** GHL's AI suggested using non-existent merge tags (`{{contact.stripe_subscription_id}}`) for direct API calls, which would have failed silently in production.
*   **The "Immediate Death" Trap:** Canceling a Stripe subscription immediately via API terminates access before the user's paid billing cycle concludes, violating standard SaaS compliance and triggering disputes.
*   **The UI Void:** GHL's default CSS flexbox models forced custom HTML cancellation forms to stretch vertically, creating massive blank gaps on the page.
*   **The Sandbox Collision:** Testing the cancellation loop risked terminating live subscriptions or crossing streams with the active Substack revenue flowing through the same Stripe account.

## 3. The Resolution (The Protocol)

We engineered a **Tri-Layer, Bi-Directional Cancellation Protocol**.

### Layer 1: The Visual UI (The Sledgehammer)
I constructed a pure HTML/CSS confirmation loop (`/cancel-access` -> `/cancel-success`) that overrides GHL's native formatting. 
*   Deployed **CSS V3.0** (`oracle_checkout_styles.css`) using wildcard targeting (`.oracle-standard-form *`) to forcefully strip GHL's injected blue borders, white backgrounds, and excessive padding.
*   The cancellation forms now blend perfectly into the Obsidian aesthetic of the Oracle terminal.

### Layer 2: The Stripe Proxy (Workflow A)
To bypass GHL's paywall and ensure compliant, deferred cancellations:
*   GHL **Workflow A** triggers on form submission and fires a webhook to the Oracle backend (`/api/auth/webhook/ghl-cancel`).
*   The Oracle backend securely authenticates the webhook (`X-GHL-Verify`), extracts the user's email, and communicates directly with the Stripe API.
*   Crucially, the backend sends the `cancel_at_period_end: true` flag. The user remains "Pro" until their exact billing cycle expires.

### Layer 3: The Final Reaper (Workflow B)
To ensure the Oracle database accurately reflects the termination when the clock runs out:
*   Stripe natively informs GHL when the subscription officially drops dead.
*   GHL **Workflow B** listens for this native "Subscription Cancelled" event.
*   Workflow B fires a final webhook to the Oracle backend (`/api/auth/webhook/ghl-downgrade`).
*   The backend flips the user's database record from `pro` back to `free`, enforcing the 5-ticket generation limit.

### The Sandbox Fallback (Zero-Risk QA)
I refactored the Python backend to support **Dual Environment Routing**.
*   When a cancellation webhook arrives, the backend first attempts to find the customer in the Live Stripe environment using `STRIPE_SECRET_KEY`.
*   If the customer is not found (because they are a test user created via a GHL form in "Test Mode"), the backend dynamically falls back to the Stripe Sandbox using `STRIPE_TEST_KEY`.
*   This allows end-to-end QA testing without risking live data or requiring constant pipeline configuration changes.

## 4. Pending Actions (Post-Anniversary)
Before initiating the QA sequence, you must execute the following handshake:

1.  **Stripe Keys to GitHub:**
    *   In Stripe, toggle "Test Mode" ON -> Copy `sk_test_...`
    *   In GitHub Secrets, create `STRIPE_TEST_KEY` -> Paste `sk_test_...`
    *   In Stripe, toggle "Test Mode" OFF -> Copy `sk_live_...`
    *   In GitHub Secrets, create `STRIPE_SECRET_KEY` -> Paste `sk_live_...`
2.  **Trigger Deployment:** 
    *   Once the keys are saved in GitHub, ping me. I will push a minor commit to force Google Cloud Build to ingest the new environment variables into the live backend.
3.  **The Sandbox Run:**
    *   Set the GHL Funnel (`/vault-access`) to "Test" mode.
    *   Run a test email through the checkout using the `4242` card.
    *   Run that email through the `/cancel-access` form.
    *   Verify in Stripe (Test Mode) that the sub is set to "Cancels at period end".
    *   Force-cancel it in Stripe to trigger Workflow B and verify the Oracle DB downgrade.

Enjoy your anniversary weekend. The Oracle will be holding its state precisely here when you return. 🖖