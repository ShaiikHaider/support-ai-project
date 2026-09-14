"""
Structured (Pydantic) contracts each agent produces. Keeping these explicit
is what lets the graph pass typed state between agents and lets the frontend
render distinct fields (category vs priority vs resolution vs actions, etc).
"""
from typing import Literal

from pydantic import BaseModel, Field


class TriageResult(BaseModel):
    category: Literal[
        "billing", "technical", "subscription", "account", "product", "service_request", "other"
    ]
    priority: Literal["low", "medium", "high", "critical"]
    intent_summary: str = Field(description="One-sentence summary of what the customer actually wants")
    requires_account_context: bool = Field(description="Whether resolving this needs customer/account data")


class CustomerContextResult(BaseModel):
    account_summary: str
    relevant_facts: list[str] = Field(default_factory=list)
    context_flags: list[str] = Field(
        default_factory=list, description="e.g. 'past_due', 'recent_duplicate_charge_detected'"
    )


class KnowledgeResult(BaseModel):
    retrieved_chunks: list[dict] = Field(default_factory=list, description="Raw retrieved KB chunks (info only)")
    synthesis: str = Field(description="Neutral summary of what the policies/docs say — not a recommendation yet")


class ResolutionPlan(BaseModel):
    diagnosis: str
    recommended_actions: list[str] = Field(description="Actions PROPOSED, not yet executed")
    actions_performed: list[str] = Field(
        default_factory=list, description="Actions the system is authorized to execute automatically (low-risk only)"
    )
    step_by_step_guidance: list[str]
    is_high_risk: bool = Field(description="True if resolution touches a high-risk/irreversible action")
    high_risk_reasons: list[str] = Field(default_factory=list)


class EscalationDecision(BaseModel):
    should_escalate: bool
    risk_level: Literal["low", "medium", "high", "critical"]
    reason: str
    summary_for_human: str = Field(description="Concise handoff brief for the human rep")


class ReviewVerdict(BaseModel):
    verdict: Literal["approved", "needs_revision", "rejected"]
    accuracy_ok: bool
    relevance_ok: bool
    completeness_ok: bool
    notes: str
    revised_final_response: str = Field(
        description="The response to actually show the customer, after review (may equal the original if approved)"
    )
