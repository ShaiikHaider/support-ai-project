"""
Bridges the LangGraph agent pipeline (in-memory state) with persistent
storage: creates/updates the Ticket row, appends TicketMessage history,
writes AgentExecutionLog rows, and creates an EscalationRecord when needed.
Also mirrors the turn into Redis short-term memory.
"""
import secrets
import string

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import SupportGraphState
from app.db import models
from app.db.redis_client import append_turn, get_recent_turns


def _generate_ticket_ref() -> str:
    return "TKT-" + "".join(secrets.choice(string.digits) for _ in range(6))


async def get_or_create_ticket(db: AsyncSession, user_id: int, ticket_id: int | None, query: str) -> models.Ticket:
    if ticket_id is not None:
        ticket = await db.get(models.Ticket, ticket_id)
        if ticket is None or ticket.user_id != user_id:
            raise ValueError("Ticket not found")
        return ticket

    ticket = models.Ticket(
        ticket_ref=_generate_ticket_ref(),
        user_id=user_id,
        subject=query[:80],
        original_query=query,
        status=models.TicketStatus.IN_PROGRESS,
    )
    db.add(ticket)
    await db.flush()
    return ticket


async def load_conversation_memory(ticket_id: int) -> list[dict[str, str]]:
    return await get_recent_turns(ticket_id)


async def record_customer_turn(ticket_id: int, message: str) -> None:
    await append_turn(ticket_id, role="customer", content=message)


async def persist_pipeline_result(db: AsyncSession, ticket: models.Ticket, state: SupportGraphState) -> models.Ticket:
    ticket.category = models.TicketCategory(state["category"])
    ticket.priority = models.Priority(state["priority"])
    ticket.retrieved_knowledge = state.get("retrieved_chunks", [])
    ticket.suggested_resolution = state.get("diagnosis", "")
    ticket.recommended_actions = state.get("recommended_actions", [])
    ticket.actions_performed = state.get("actions_performed", [])
    ticket.final_response = state.get("final_response", "")
    ticket.is_escalated = state.get("should_escalate", False)
    ticket.escalation_reason = state.get("escalation_reason", "")
    ticket.reviewer_verdict = state.get("reviewer_verdict", "")
    ticket.reviewer_notes = state.get("reviewer_notes", "")

    status_map = {
        "resolved": models.TicketStatus.RESOLVED,
        "requires_more_information": models.TicketStatus.REQUIRES_MORE_INFO,
        "escalated": models.TicketStatus.ESCALATED,
    }
    ticket.status = status_map.get(state.get("ticket_status", ""), models.TicketStatus.IN_PROGRESS)

    # Persist conversation messages
    db.add(models.TicketMessage(ticket_id=ticket.id, role=models.MessageRole.CUSTOMER, content=state["customer_query"]))
    db.add(models.TicketMessage(ticket_id=ticket.id, role=models.MessageRole.ASSISTANT, content=state.get("final_response", "")))

    # Persist agent execution trace
    for entry in state.get("agent_trace", []):
        db.add(
            models.AgentExecutionLog(
                ticket_id=ticket.id,
                agent_name=entry["agent_name"],
                step_order=entry["step_order"],
                input_summary=entry["input_summary"],
                output_summary=entry["output_summary"],
                duration_ms=entry["duration_ms"],
            )
        )

    # Escalation record
    if state.get("should_escalate"):
        from sqlalchemy import select
        existing_result = await db.execute(select(models.EscalationRecord).where(models.EscalationRecord.ticket_id == ticket.id))
        existing = existing_result.scalar_one_or_none()
        if existing is None:
            db.add(
                models.EscalationRecord(
                    ticket_id=ticket.id,
                    reason=state.get("escalation_reason", ""),
                    risk_level=state.get("escalation_risk_level", "medium"),
                    summary_for_human=state.get("escalation_summary", ""),
                )
            )
        else:
            existing.reason = state.get("escalation_reason", "")
            existing.risk_level = state.get("escalation_risk_level", "medium")
            existing.summary_for_human = state.get("escalation_summary", "")

    await db.commit()
    await db.refresh(ticket)

    # mirror assistant reply into short-term memory
    await append_turn(ticket.id, role="assistant", content=state.get("final_response", ""))

    return ticket

