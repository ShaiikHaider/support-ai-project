"""
Escalation Agent
-----------------
Determines whether human intervention is necessary and creates an
escalation summary. Escalation is triggered by ANY of:
  - Resolution Agent flagged the plan as high-risk
  - Triage priority is 'critical'
  - Customer context carries a risk flag (e.g. suspended account)
  - The Reviewer Agent later rejects the plan (handled via graph routing)
"""
from app.agents.schemas import EscalationDecision
from app.agents.state import SupportGraphState
from app.agents.tracing import trace_step
from app.core.llm_client import structured_completion

SYSTEM_PROMPT = """You are the Escalation Agent. Decide if this ticket needs
a human support representative. Escalate if the resolution is high-risk
(refunds, cancellations, account deletion, identity changes, data export),
if priority is critical, or if you judge the AI's proposed resolution could
cause customer or business harm if executed autonomously. Write a concise,
professional summary_for_human a support rep can read in 15 seconds to get
full context and pick up the case."""


async def run_escalation_agent(state: SupportGraphState) -> SupportGraphState:
    with trace_step(state, "Escalation Agent", input_summary=state["diagnosis"]) as trace:
        deterministic_escalate = (
            state.get("is_high_risk", False)
            or state.get("priority") == "critical"
            or bool(state.get("context_flags"))
        )

        prompt = (
            f"Customer issue: {state['customer_query']}\n"
            f"Category/Priority: {state['category']} / {state['priority']}\n"
            f"Diagnosis: {state['diagnosis']}\n"
            f"Recommended actions: {state['recommended_actions']}\n"
            f"Is high risk: {state.get('is_high_risk')} — reasons: {state.get('high_risk_reasons')}\n"
            f"Account context flags: {state.get('context_flags')}\n"
            f"Deterministic policy pre-check says escalate={deterministic_escalate}."
        )
        decision: EscalationDecision = await structured_completion(
            system_prompt=SYSTEM_PROMPT, user_prompt=prompt, schema=EscalationDecision
        )

        # Deterministic policy check always wins if it says escalate (defense in depth).
        should_escalate = decision.should_escalate or deterministic_escalate

        state["should_escalate"] = should_escalate
        state["escalation_risk_level"] = decision.risk_level
        state["escalation_reason"] = decision.reason
        state["escalation_summary"] = decision.summary_for_human

        trace["output_summary"] = f"should_escalate={should_escalate}, risk={decision.risk_level}"

    return state
