"""
Shared state object threaded through the LangGraph pipeline. Each agent node
reads what it needs and writes its own contribution; nothing is overwritten
implicitly, which is what lets the API return a clean per-agent execution
trace to the frontend.
"""
from typing import Any, TypedDict


class AgentTraceEntry(TypedDict):
    agent_name: str
    step_order: int
    input_summary: str
    output_summary: str
    duration_ms: int


class SupportGraphState(TypedDict, total=False):
    # --- input ---
    ticket_id: int
    customer_query: str
    conversation_history: list[dict[str, str]]  # short-term memory from Redis

    # --- triage agent output ---
    category: str
    priority: str
    intent_summary: str
    requires_account_context: bool

    # --- customer context agent output ---
    account_summary: str
    relevant_facts: list[str]
    context_flags: list[str]

    # --- knowledge retrieval agent output (INFORMATION ONLY) ---
    retrieved_chunks: list[dict]
    knowledge_synthesis: str

    # --- resolution agent output ---
    diagnosis: str
    recommended_actions: list[str]   # proposed, NOT executed
    actions_performed: list[str]     # actually executed via tools
    step_by_step_guidance: list[str]
    is_high_risk: bool
    high_risk_reasons: list[str]

    # --- escalation agent output ---
    should_escalate: bool
    escalation_risk_level: str
    escalation_reason: str
    escalation_summary: str

    # --- reviewer agent output ---
    reviewer_verdict: str
    reviewer_notes: str
    final_response: str

    # --- bookkeeping ---
    agent_trace: list[AgentTraceEntry]
    ticket_status: str
