"""
Seed knowledge-base content used to populate the vector store on first run.
In production this would be replaced/augmented by a real CMS, Confluence
export, or support-doc pipeline — the RAG pipeline itself is agnostic to
where the source documents come from.
"""

KB_DOCUMENTS = [
    # ---------------- Billing ----------------
    {
        "id": "billing-001",
        "category": "billing",
        "title": "Duplicate Subscription Charge Policy",
        "content": (
            "If a customer is charged more than once for the same billing cycle, this is "
            "classified as a duplicate/double charge. Support should: 1) verify the two charges "
            "share the same billing period and amount, 2) check whether a plan change or retry "
            "from a failed payment caused a second authorization, 3) if confirmed duplicate, issue "
            "a refund for the extra charge within 5-7 business days, 4) if the charges are for "
            "different periods or add-ons, this is not a duplicate and should be explained to the "
            "customer. Refunds above $500 or disputed by the customer as fraud must be escalated "
            "to a human billing specialist."
        ),
    },
    {
        "id": "billing-002",
        "category": "billing",
        "title": "Refund Eligibility Policy",
        "content": (
            "Standard refunds are available within 14 days of a charge for monthly plans and 30 "
            "days for annual plans, provided the customer has not consumed more than 20% of usage "
            "quota in that cycle. Refunds for duplicate charges, billing errors, or failed service "
            "are not subject to the 14/30-day window and can be processed immediately after "
            "verification. All refunds are a high-risk action and require either automatic policy "
            "match (duplicate charge, verified billing error) or human approval otherwise."
        ),
    },
    {
        "id": "billing-003",
        "category": "billing",
        "title": "Failed Payment & Dunning Process",
        "content": (
            "When a payment fails, the system retries automatically on day 1, day 3, and day 7. "
            "The account is marked 'past_due' during this window and moves to 'suspended' after "
            "the third failed retry. Customers can update their payment method any time to trigger "
            "an immediate retry. Support can manually retry a charge once per day."
        ),
    },
    # ---------------- Subscription ----------------
    {
        "id": "sub-001",
        "category": "subscription",
        "title": "Plan Cancellation Policy",
        "content": (
            "Customers can cancel anytime; cancellation takes effect at the end of the current "
            "billing period and access continues until then. No partial-period refund is issued "
            "for cancellation alone (see refund policy for exceptions). Cancellation is a "
            "high-risk/irreversible-adjacent action: support may explain the process and retention "
            "offers but should escalate to a human rep before actually executing an immediate "
            "(non-standard) cancellation or any request bundled with a refund demand."
        ),
    },
    {
        "id": "sub-002",
        "category": "subscription",
        "title": "Upgrading or Downgrading a Plan",
        "content": (
            "Upgrades take effect immediately with prorated billing for the remainder of the "
            "cycle. Downgrades take effect at the start of the next billing cycle to avoid mid-cycle "
            "feature loss. This is a low-risk, self-service action the Resolution Agent can guide "
            "the customer through directly."
        ),
    },
    # ---------------- Technical ----------------
    {
        "id": "tech-001",
        "category": "technical",
        "title": "Login / Authentication Issues",
        "content": (
            "Common causes of login failure: expired session token, incorrect password after a "
            "recent reset, SSO provider outage, or account lock after 5 failed attempts (auto-"
            "unlocks after 30 minutes). Steps: confirm the exact error message, check account "
            "status is 'active' not 'suspended', have the customer try password reset, and if SSO, "
            "check provider status page. Escalate only if account shows signs of unauthorized "
            "access or security compromise."
        ),
    },
    {
        "id": "tech-002",
        "category": "technical",
        "title": "API Rate Limit Errors (HTTP 429)",
        "content": (
            "Free tier: 60 requests/min. Pro tier: 600 requests/min. Enterprise: custom limits. "
            "A 429 response includes a Retry-After header. Recommend exponential backoff and "
            "batching requests. Sustained rate-limit issues on Pro/Enterprise plans may indicate "
            "the customer needs a plan upgrade or custom limit — this is a sales-adjacent "
            "recommendation, not an action support can execute directly."
        ),
    },
    {
        "id": "tech-003",
        "category": "technical",
        "title": "Data Sync / Integration Failures",
        "content": (
            "If a third-party integration (e.g. CRM sync) stops working, first check the "
            "integration status page in account settings for a disconnected/expired-token state. "
            "Most syncs fail due to expired OAuth tokens (reconnect resolves ~80% of cases) or the "
            "third-party API changing scopes. If reconnecting does not resolve it within one sync "
            "cycle, escalate to the integrations engineering on-call."
        ),
    },
    # ---------------- Account ----------------
    {
        "id": "acct-001",
        "category": "account",
        "title": "Account Deletion & Data Export",
        "content": (
            "Account deletion is permanent after a 30-day grace period during which the account "
            "is deactivated but recoverable. Data export must be offered before deletion is "
            "confirmed. Both data export requests and account deletion are classified as high-risk "
            "actions under data-protection policy and must always be escalated to a human "
            "representative for identity verification before execution — the AI system may not "
            "perform them directly."
        ),
    },
    {
        "id": "acct-002",
        "category": "account",
        "title": "Updating Account Email or Ownership",
        "content": (
            "Changing the primary account email or transferring account ownership requires "
            "identity verification (matching the request against two account signals, e.g. last "
            "payment method + account creation date). This is a high-risk identity_change action "
            "and must be escalated; support may confirm receipt of the request but not execute it."
        ),
    },
    # ---------------- Product ----------------
    {
        "id": "prod-001",
        "category": "product",
        "title": "Feature Availability by Plan",
        "content": (
            "Advanced analytics, custom roles, and SSO are available on Pro and Enterprise plans "
            "only. Free and Basic plans include core features with usage caps. If a customer asks "
            "about a feature not on their plan, explain the upgrade path; do not imply the feature "
            "is broken."
        ),
    },
    # ---------------- Service Request ----------------
    {
        "id": "svc-001",
        "category": "service_request",
        "title": "Custom Enterprise Requests",
        "content": (
            "Requests for custom contracts, SLAs, dedicated infrastructure, or bespoke integrations "
            "fall outside standard support scope. These should always be escalated to the "
            "Enterprise Success team with a summary of the customer's ask and current plan."
        ),
    },
]
