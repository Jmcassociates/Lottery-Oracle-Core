# Oracle Subscription Cancellation Protocol (GHL)

To fulfill the "One-Click Cancel" flow from the Oracle Dashboard without writing raw Stripe API logic in Python, build this simple funnel in GoHighLevel:

### 1a. The Cancellation Request Page
*   **Path:** `https://oracle.moderncyph3r.com/cancel-access`
*   **Design:** Use the same dark aesthetic CSS (`oracle_checkout_styles.css`).
*   **Content:** A simple form asking for their Email Address. Set the "On Submit" action of this form to redirect to the Confirmation Page (1b).
*   **Button:** "Terminate Pro Tier Access"

### 1b. The Cancellation Confirmation Page
*   **Path:** `https://oracle.moderncyph3r.com/cancel-success`
*   **Design:** Use the dark aesthetic CSS (`oracle_checkout_styles.css`).
*   **Content:** A 1-Column Row with a Custom HTML block. Paste the contents of `oracle_cancel_confirmation.html` into this block. It provides immediate reassurance and a button to route them back to the Oracle Dashboard.

### 2. Workflow A: The "Deferred Downgrade" Request
Create a new Workflow in GHL named "Oracle - 1 - Cancellation Requested".

*   **Trigger:** Form Submitted -> [Select the Cancellation Form]
*   **Action 1 (CRM Update):** 
    *   *Type:* Add Contact Tag.
    *   *Action:* `Pending Cancellation`.
*   **Action 2 (The Stripe Proxy Webhook):**
    *   *Type:* Webhook.
    *   *URL:* `https://oracle-backend-ca5k2evwwq-ue.a.run.app/api/auth/webhook/ghl-cancel`
    *   *Headers:* Add a Custom Header named `X-GHL-Verify` and set the value to your `GHL_WEBHOOK_SECRET` (the same one used in the provision workflow).
    *   *Payload:* Ensure it sends the standard contact data (which includes the email).
*   **Action 3 (Email Confirmation):**
    *   *Type:* Send Email.
    *   *Subject:* `Oracle Protocol: Deactivation Notice`
    *   *Body Template:* 
        > "Your request to terminate your Oracle Pro Tier subscription has been successfully processed. 
        > 
        > As per our protocol, your terminal will remain fully operational until the end of your current billing cycle. After that date, your account will automatically revert to the Free Tier. Your historical artifacts in The Vault will be preserved.
        > 
        > Return to Terminal: https://oracleapp.moderncyph3r.com/dashboard"

### 3. Workflow B: The "True" Killswitch (End of Billing Cycle)
Create a second Workflow in GHL named "Oracle - 2 - Subscription Officially Terminated".

*   **Trigger:** Subscription -> Filter: **Status is Canceled**.
*   **Action 1 (CRM Update):** 
    *   *Type:* Remove Tag: `Pending Cancellation`.
    *   *Type:* Add Tag: `Churned`.
    *   *Action:* Move Opportunity to "Vault User: Free Tier" (or a specific "Churned" stage).
*   **Action 2 (The Oracle Downgrade Webhook):**
    *   *Type:* Webhook.
    *   *Method:* **POST**
    *   *URL:* `https://oracle-backend-ca5k2evwwq-ue.a.run.app/api/auth/webhook/ghl-downgrade` 
    *   *Headers:* Add a Custom Header named `X-GHL-Verify` and set the value to your `GHL_WEBHOOK_SECRET` (the same one used in the provision workflow).
    *   *Payload:* Leave empty (default contact data).

*Note: The `/webhook/ghl-downgrade` endpoint is live on the Oracle backend to catch this final signal and securely flip the user record from `pro` to `free`.*
