# Oracle Subscription Cancellation Protocol (GHL)

To fulfill the "One-Click Cancel" flow from the Oracle Dashboard without writing raw Stripe API logic in Python, build this simple funnel in GoHighLevel:

### 1. The GHL Page
*   **Path:** `https://oracle.moderncyph3r.com/cancel-access`
*   **Design:** Use the same dark aesthetic CSS (`oracle_checkout_styles.css`).
*   **Content:** A simple form asking for their Email Address.
*   **Button:** "Terminate Pro Tier Access"

### 2. Workflow A: The "Deferred Downgrade" Request
Create a new Workflow in GHL named "Oracle - 1 - Cancellation Requested".

*   **Trigger:** Form Submitted -> [Select the Cancellation Form]
*   **Action 1 (CRM Update):** 
    *   *Type:* Add Contact Tag.
    *   *Action:* `Pending Cancellation`.
*   **Action 2 (Stripe Termination):**
    *   *Type:* Cancel Subscription (Native GHL Premium Action).
    *   *CRITICAL SETTING:* Set to cancel **"At the end of the billing period"**. (Do NOT select "Immediately").

### 3. Workflow B: The "True" Killswitch (End of Billing Cycle)
Create a second Workflow in GHL named "Oracle - 2 - Subscription Officially Terminated".

*   **Trigger:** Subscription Cancelled (Native GHL Trigger listening to Stripe).
*   **Action 1 (CRM Update):** 
    *   *Type:* Move Opportunity.
    *   *Action:* Move to "Vault User: Free Tier" (or a specific "Churned" stage).
*   **Action 2 (The Oracle Downgrade Webhook):**
    *   *Type:* Webhook.
    *   *URL:* `https://oracle-backend-ca5k2evwwq-ue.a.run.app/api/admin/users/webhook-tier-downgrade` 
    *   *Payload:* Must pass the user's email.

*Note: We will build the `/webhook-tier-downgrade` endpoint in the Oracle backend on Thursday to catch this final signal and securely flip their `users` table record from `pro` to `free`.*