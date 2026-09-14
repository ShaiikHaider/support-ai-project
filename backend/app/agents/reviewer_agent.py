"""
Decision / Reviewer Agent
---------------------------
Reviews the proposed resolution before it reaches the customer. Checks
accuracy (grounded in retrieved knowledge), relevance (answers the actual
question), and completeness (nothing important left out). Produces the
final_response actually shown to the customer, and can send the ticket
back for revision.
"""
from app.agents.schemas import ReviewVerdict
from app.agents.state import SupportGraphState
from app.agents.tracing import trace_step
from app.core.llm_client import structured_completion

SYSTEM_PROMPT = """You are the Decision/Reviewer Agent, the final quality
gate before a response reaches the customer. Review the proposed resolution
against the retrieved knowledge and the customer's actual question.
Check:
- accuracy_ok: does it match the retrieved policy/knowledge, with no invented facts?
- relevance_ok: does it directly address what the customer asked?
- completeness_ok: does it cover next steps, and clearly state escalation
  status if applicable?
Then write revised_final_response: the actual customer-facing message —
warm, clear, and precise. If escalated, this should explain that the case
was routed to a specialist and what happens next, without promising a fixed
resolution time you don't know. If not escalated, include the concrete
guidance/resolution and confirm which actions (if any) were already taken
automatically vs. which are recommended next steps."""


async def run_reviewer_agent(state: SupportGraphState) -> SupportGraphState:
    with trace_step(state, "Decision/Reviewer Agent", input_summary=state["diagnosis"]) as trace:
        prompt = (
            f"Customer issue: {state['customer_query']}\n"
            f"Diagnosis: {state['diagnosis']}\n"
            f"Knowledge synthesis: {state.get('knowledge_synthesis', 'n/a')}\n"
            f"Recommended actions: {state['recommended_actions']}\n"
            f"Actions already performed automatically: {state.get('actions_performed', [])}\n"
            f"Step-by-step guidance: {state['step_by_step_guidance']}\n"
            f"Escalated: {state.get('should_escalate')} — reason: {state.get('escalation_reason', '')}\n"
        )
        verdict: ReviewVerdict = await structured_completion(
            system_prompt=SYSTEM_PROMPT, user_prompt=prompt, schema=ReviewVerdict
        )

        state["reviewer_verdict"] = verdict.verdict
        state["reviewer_notes"] = verdict.notes
        state["final_response"] = verdict.revised_final_response

        if state.get("should_escalate"):
            state["ticket_status"] = "escalated"
        elif verdict.verdict == "needs_revision" and not state.get("should_escalate"):
            # A reviewer flag that isn't auto-fixable by revision alone is
            # routed to a human rather than looping indefinitely.
            state["ticket_status"] = "requires_more_information"
        else:
            state["ticket_status"] = "resolved"

        trace["output_summary"] = f"verdict={verdict.verdict}, status={state['ticket_status']}"

    return state
