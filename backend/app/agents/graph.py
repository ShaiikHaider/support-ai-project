"""
LangGraph orchestration: wires the six agents into a directed graph.

Flow:
  Triage -> Customer Context -> Knowledge Retrieval -> Resolution
         -> Escalation -> Reviewer -> END

The Customer Context Agent needs a DB session + user id, which aren't part
of the plain graph state machinery, so we bind them via a closure when
building the graph for a given request (see build_graph()).
"""
from functools import partial

from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

from app.agents.customer_context_agent import run_customer_context_agent
from app.agents.escalation_agent import run_escalation_agent
from app.agents.knowledge_agent import run_knowledge_agent
from app.agents.resolution_agent import run_resolution_agent
from app.agents.reviewer_agent import run_reviewer_agent
from app.agents.state import SupportGraphState
from app.agents.triage_agent import run_triage_agent


def build_graph(db: AsyncSession, user_id: int):
    graph = StateGraph(SupportGraphState)

    graph.add_node("triage", run_triage_agent)
    graph.add_node("customer_context", partial(run_customer_context_agent, db=db, user_id=user_id))
    graph.add_node("knowledge_retrieval", run_knowledge_agent)
    graph.add_node("resolution", run_resolution_agent)
    graph.add_node("escalation", run_escalation_agent)
    graph.add_node("review", run_reviewer_agent)

    graph.set_entry_point("triage")
    graph.add_edge("triage", "customer_context")
    graph.add_edge("customer_context", "knowledge_retrieval")
    graph.add_edge("knowledge_retrieval", "resolution")
    graph.add_edge("resolution", "escalation")
    graph.add_edge("escalation", "review")
    graph.add_edge("review", END)

    return graph.compile()


async def run_support_pipeline(
    db: AsyncSession,
    user_id: int,
    ticket_id: int,
    customer_query: str,
    conversation_history: list[dict[str, str]],
) -> SupportGraphState:
    app_graph = build_graph(db, user_id)

    initial_state: SupportGraphState = {
        "ticket_id": ticket_id,
        "customer_query": customer_query,
        "conversation_history": conversation_history,
        "agent_trace": [],
    }

    final_state: SupportGraphState = await app_graph.ainvoke(
        initial_state,
        config={"recursion_limit": settings.MAX_LLM_CALLS_PER_TICKET}
    )
    
    if len(final_state.get("agent_trace", [])) >= settings.MAX_LLM_CALLS_PER_TICKET:
        raise ValueError(f"Exceeded MAX_LLM_CALLS_PER_TICKET limit of {settings.MAX_LLM_CALLS_PER_TICKET}")
        
    return final_state
