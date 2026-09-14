"""
Triage Agent
------------
Understands the customer issue, classifies the ticket into a support
category, and determines urgency/priority. This is the entry point of
the graph.
"""
from app.agents.schemas import TriageResult
from app.agents.state import SupportGraphState
from app.agents.tracing import trace_step
from app.core.llm_client import structured_completion

SYSTEM_PROMPT = """You are the Triage Agent in a customer support system.
Read the customer's message (and any prior conversation) and:
1. Classify it into exactly one category: billing, technical, subscription,
   account, product, service_request, or other.
2. Determine urgency/priority: low, medium, high, or critical.
   - critical: account security, service completely down, money at risk (e.g. double charge)
   - high: blocking issue for the customer's core use case
   - medium: inconvenient but has a workaround
   - low: general question, no urgency
3. Write a one-sentence intent_summary of what the customer actually wants.
4. Decide requires_account_context: true if resolving this needs the
   customer's account/billing/subscription data, false for generic
   how-to questions.
Be decisive — always pick the single best-fit category, never 'other' unless
truly nothing else fits."""


async def run_triage_agent(state: SupportGraphState) -> SupportGraphState:
    query = state["customer_query"]
    history_text = _format_history(state.get("conversation_history", []))

    with trace_step(state, "Triage Agent", input_summary=query) as trace:
        result: TriageResult = await structured_completion(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=f"Conversation so far:\n{history_text}\n\nLatest customer message:\n{query}",
            schema=TriageResult,
        )
        state["category"] = result.category
        state["priority"] = result.priority
        state["intent_summary"] = result.intent_summary
        state["requires_account_context"] = result.requires_account_context

        trace["output_summary"] = (
            f"category={result.category}, priority={result.priority}, "
            f"needs_context={result.requires_account_context}"
        )

    return state


def _format_history(history: list[dict[str, str]]) -> str:
    if not history:
        return "(no prior turns)"
    return "\n".join(f"{turn['role']}: {turn['content']}" for turn in history[-8:])
