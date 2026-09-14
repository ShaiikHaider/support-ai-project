"""
Tool/API-calling layer.

These represent the "External/customer API integration" the tech stack
calls for. In this reference implementation they are safe, deterministic
mocks so the project runs end-to-end without live billing/CRM credentials —
swap the bodies for real API calls (Stripe, Zendesk, internal account
service, etc.) in production.

CRITICAL DESIGN RULE: only LOW-RISK, reversible, well-understood actions are
ever invoked automatically by the Resolution Agent. Anything touching money,
identity, or irreversible account state must go through the Escalation
Agent instead — see app.core.config.settings.HIGH_RISK_ACTIONS and
resolution_agent.py's risk check.
"""
from datetime import datetime, timezone

LOW_RISK_TOOLS = {
    "resend_confirmation_email",
    "retry_failed_payment",
    "reset_password_link",
    "unlock_account_after_cooldown",
    "reconnect_integration_token",
    "send_plan_comparison",
}


async def resend_confirmation_email(user_email: str) -> dict:
    return {"tool": "resend_confirmation_email", "status": "sent", "to": user_email, "at": _now()}


async def retry_failed_payment(account_id: int) -> dict:
    return {"tool": "retry_failed_payment", "status": "retry_queued", "account_id": account_id, "at": _now()}


async def reset_password_link(user_email: str) -> dict:
    return {"tool": "reset_password_link", "status": "link_sent", "to": user_email, "at": _now()}


async def unlock_account_after_cooldown(account_id: int) -> dict:
    return {"tool": "unlock_account_after_cooldown", "status": "unlocked", "account_id": account_id, "at": _now()}


async def reconnect_integration_token(account_id: int, integration: str) -> dict:
    return {
        "tool": "reconnect_integration_token",
        "status": "reconnect_link_sent",
        "account_id": account_id,
        "integration": integration,
        "at": _now(),
    }


async def send_plan_comparison(user_email: str) -> dict:
    return {"tool": "send_plan_comparison", "status": "sent", "to": user_email, "at": _now()}


TOOL_DISPATCH = {
    "resend_confirmation_email": resend_confirmation_email,
    "retry_failed_payment": retry_failed_payment,
    "reset_password_link": reset_password_link,
    "unlock_account_after_cooldown": unlock_account_after_cooldown,
    "reconnect_integration_token": reconnect_integration_token,
    "send_plan_comparison": send_plan_comparison,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
