"""
Resolution Agent
-----------------
Determines the recommended solution and generates step-by-step guidance.

Distinguishes three categories, per the assignment's core requirement:
  1. Information retrieval  -> already captured upstream (knowledge_synthesis)
  2. Recommended actions    -> proposed to the customer/human, NOT executed
  3. Actions actually performed -> only low-risk tool calls the system is
     explicitly authorized to run automatically (see app.agents.tools)

Anything flagged high-risk is left for the Escalation Agent to route to a
human rather than executed here.
"""
from app.agents.schemas import ResolutionPlan
from app.agents.state import SupportGraphState
from app.agents.tools import LOW_RISK_TOOLS, TOOL_DISPATCH
from app.agents.tracing import trace_step
from app.core.config import settings
from app.core.llm_client import structured_completion

SYSTEM_PROMPT = """You are the Resolution Agent in a customer support system.
You are given the customer's issue, retrieved knowledge-base policy/FAQ
content, and account context. Produce:
- diagnosis: what's actually going on
- recommended_actions: a list of concrete actions that WOULD resolve this
  (phrase each as a short imperative, e.g. "Issue refund for duplicate charge")
- actions_performed: leave this EMPTY — a downstream system decides what can
  be auto-executed; you only propose.
- step_by_step_guidance: numbered, customer-facing steps in plain language
- is_high_risk: true if ANY recommended action involves money movement,
  cancellation, account deletion, identity/ownership change, or data export
- high_risk_reasons: why, if is_high_risk is true

Ground every claim in the provided knowledge synthesis and account context —
do not invent policy details that weren't retrieved."""


async def run_resolution_agent(state: SupportGraphState) -> SupportGraphState:
    with trace_step(state, "Resolution Agent", input_summary=state["intent_summary"]) as trace:
        prompt = (
            f"Customer issue: {state['customer_query']}\n"
            f"Intent: {state['intent_summary']}\n"
            f"Category: {state['category']} | Priority: {state['priority']}\n\n"
            f"Account context: {state.get('account_summary', 'n/a')}\n"
            f"Relevant facts: {state.get('relevant_facts', [])}\n"
            f"Context flags: {state.get('context_flags', [])}\n\n"
            f"Knowledge base synthesis: {state.get('knowledge_synthesis', 'n/a')}"
        )
        plan: ResolutionPlan = await structured_completion(
            system_prompt=SYSTEM_PROMPT, user_prompt=prompt, schema=ResolutionPlan
        )

        # Cross-check high-risk flag against the configured policy list as a
        # deterministic safety net (don't rely on the LLM's judgment alone).
        is_high_risk = plan.is_high_risk or _matches_high_risk_keyword(plan.recommended_actions)

        state["diagnosis"] = plan.diagnosis
        state["recommended_actions"] = plan.recommended_actions
        state["step_by_step_guidance"] = plan.step_by_step_guidance
        state["is_high_risk"] = is_high_risk
        state["high_risk_reasons"] = plan.high_risk_reasons

        # Execute ONLY low-risk, whitelisted tool actions automatically.
        performed = await _execute_low_risk_actions(state, plan.recommended_actions)
        state["actions_performed"] = performed

        trace["output_summary"] = (
            f"high_risk={is_high_risk}, recommended={len(plan.recommended_actions)}, "
            f"auto_performed={len(performed)}"
        )

    return state


def _matches_high_risk_keyword(actions: list[str]) -> bool:
    joined = " ".join(actions).lower()
    return any(keyword.replace("_", " ") in joined for keyword in settings.HIGH_RISK_ACTIONS)


async def _execute_low_risk_actions(state: SupportGraphState, recommended_actions: list[str]) -> list[dict]:
    """Maps recommended-action phrases to whitelisted tool calls. Very
    conservative: only fires a tool when there's a clear keyword match to a
    known low-risk tool, and never for high-risk categories."""
    if state.get("is_high_risk"):
        return []

    performed = []
    joined = " ".join(recommended_actions).lower()

    keyword_map = {
        "resend_confirmation_email": ["resend", "confirmation email"],
        "retry_failed_payment": ["retry", "payment"],
        "reset_password_link": ["reset password", "password reset"],
        "unlock_account_after_cooldown": ["unlock account"],
        "reconnect_integration_token": ["reconnect", "integration", "oauth token"],
        "send_plan_comparison": ["plan comparison", "compare plans", "upgrade path"],
    }

    for tool_name, keywords in keyword_map.items():
        if tool_name not in LOW_RISK_TOOLS:
            continue
        if any(kw in joined for kw in keywords):
            tool_fn = TOOL_DISPATCH[tool_name]
            # Mock args — a production system would pull real identifiers from state.
            if tool_name in ("resend_confirmation_email", "reset_password_link", "send_plan_comparison"):
                result = await tool_fn(user_email="customer@example.com")
            elif tool_name == "reconnect_integration_token":
                result = await tool_fn(account_id=state["ticket_id"], integration="crm")
            else:
                result = await tool_fn(account_id=state["ticket_id"])
            performed.append(result)

    return performed
