from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_current_user
from app.db import models
from app.db.database import get_db
from app.schemas.api_schemas import TicketDetailOut, TicketOut

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketOut])
async def list_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result = await db.execute(
        select(models.Ticket)
        .where(models.Ticket.user_id == current_user.id)
        .order_by(models.Ticket.updated_at.desc())
    )
    tickets = result.scalars().all()
    return [_to_ticket_out(t) for t in tickets]


@router.get("/{ticket_id}", response_model=TicketDetailOut)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    result = await db.execute(
        select(models.Ticket)
        .options(selectinload(models.Ticket.agent_logs), selectinload(models.Ticket.messages))
        .where(models.Ticket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    if ticket is None or ticket.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Ticket not found")

    base = _to_ticket_out(ticket)
    return TicketDetailOut(
        **base.model_dump(),
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


def _to_ticket_out(t: models.Ticket) -> TicketOut:
    return TicketOut(
        id=t.id,
        ticket_ref=t.ticket_ref,
        subject=t.subject,
        original_query=t.original_query,
        category=t.category.value,
        priority=t.priority.value,
        status=t.status.value,
        retrieved_knowledge=t.retrieved_knowledge,
        suggested_resolution=t.suggested_resolution,
        recommended_actions=t.recommended_actions,
        actions_performed=t.actions_performed,
        final_response=t.final_response,
        is_escalated=t.is_escalated,
        escalation_reason=t.escalation_reason,
        reviewer_verdict=t.reviewer_verdict,
        reviewer_notes=t.reviewer_notes,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )
