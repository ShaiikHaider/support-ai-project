"""
Customer Context Agent
-----------------------
Retrieves relevant customer/account information (from PostgreSQL, cached in
Redis) and folds in short-term conversation memory so downstream agents have
full context. This is pure information retrieval — it never proposes or
performs actions.
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import SupportGraphState
from app.agents.tracing import trace_step
from app.db import models
from app.db.redis_client import cache_customer_context, get_cached_customer_context


async def run_customer_context_agent(state: SupportGraphState, db: AsyncSession, user_id: int) -> SupportGraphState:
    with trace_step(state, "Customer Context Agent", input_summary=f"user_id={user_id}") as trace:
        if not state.get("requires_account_context", True):
            state["account_summary"] = "Not required for this request."
            state["relevant_facts"] = []
            state["context_flags"] = []
            trace["output_summary"] = "Skipped — query does not require account context."
            return state

        cached = await get_cached_customer_context(state["ticket_id"])
        if cached:
            state["account_summary"] = cached["account_summary"]
            state["relevant_facts"] = cached["relevant_facts"]
            state["context_flags"] = cached["context_flags"]
            trace["output_summary"] = "Loaded from Redis cache."
            return state

        account = await db.get(models.CustomerAccount, user_id)
        # NOTE: in this schema account.id == user_id via 1:1 relationship;
        # in a real system this would be a lookup by user_id FK.
        result = await db.execute(
            models.CustomerAccount.__table__.select().where(models.CustomerAccount.user_id == user_id)
        )
        row = result.first()

        if row is None:
            summary = "No account record found — likely a new or trial user."
            facts: list[str] = []
            flags: list[str] = ["no_account_record"]
        else:
            acct = row._mapping
            facts = [
                f"Plan: {acct['plan_name']}",
                f"Subscription status: {acct['subscription_status']}",
                f"Billing cycle: {acct['billing_cycle']}",
                f"Last charge: ${acct['last_charge_amount']} on {acct['last_charge_date']}",
            ]
            summary = f"{acct['plan_name']} plan, subscription {acct['subscription_status']}."
            flags = []
            if acct["subscription_status"] in ("past_due", "suspended"):
                flags.append(acct["subscription_status"])

        state["account_summary"] = summary
        state["relevant_facts"] = facts
        state["context_flags"] = flags

        await cache_customer_context(
            state["ticket_id"],
            {"account_summary": summary, "relevant_facts": facts, "context_flags": flags},
        )

        trace["output_summary"] = summary

    return state
