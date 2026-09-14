from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.graph import run_support_pipeline
from app.core.security import get_current_user
from app.db import models
from app.db.database import get_db
from app.schemas.api_schemas import ChatMessageIn, ChatResponseOut, TicketDetailOut
from app.services.ticket_service import (
    get_or_create_ticket,
    load_conversation_memory,
    persist_pipeline_result,
    record_customer_turn,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponseOut)
async def send_message(
    payload: ChatMessageIn,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        ticket = await get_or_create_ticket(db, current_user.id, payload.ticket_id, payload.message)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")

    history = await load_conversation_memory(ticket.id)
    await record_customer_turn(ticket.id, payload.message)

    final_state = await run_support_pipeline(
        db=db,
        user_id=current_user.id,
        ticket_id=ticket.id,
        customer_query=payload.message,
        conversation_history=history,
    )

    ticket = await persist_pipeline_result(db, ticket, final_state)

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(models.Ticket)
        .options(selectinload(models.Ticket.agent_logs), selectinload(models.Ticket.messages))
        .where(models.Ticket.id == ticket.id)
    )
    ticket = result.scalar_one()

    detail = TicketDetailOut(
        id=ticket.id,
        ticket_ref=ticket.ticket_ref,
        subject=ticket.subject,
        original_query=ticket.original_query,
        category=ticket.category.value,
        priority=ticket.priority.value,
        status=ticket.status.value,
        retrieved_knowledge=ticket.retrieved_knowledge,
        suggested_resolution=ticket.suggested_resolution,
        recommended_actions=ticket.recommended_actions,
        actions_performed=ticket.actions_performed,
        final_response=ticket.final_response,
        is_escalated=ticket.is_escalated,
        escalation_reason=ticket.escalation_reason,
        reviewer_verdict=ticket.reviewer_verdict,
        reviewer_notes=ticket.reviewer_notes,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        agent_trace=[
            {
                "agent_name": log.agent_name,
                "step_order": log.step_order,
                "input_summary": log.input_summary,
                "output_summary": log.output_summary,
                "duration_ms": log.duration_ms,
            }
            for log in sorted(ticket.agent_logs, key=lambda entry: entry.step_order)
        ],
        messages=[{"role": m.role.value, "content": m.content, "created_at": m.created_at.isoformat()} for m in ticket.messages],
    )

    return ChatResponseOut(ticket=detail)

