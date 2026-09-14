"""
Persistent ticket history & account data live in PostgreSQL.
Short-term conversational memory lives in Redis (see app/db/redis_client.py).
"""
import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# --------------------------------------------------------------------------
# Enums
# --------------------------------------------------------------------------
class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REQUIRES_MORE_INFO = "requires_more_information"
    ESCALATED = "escalated"
    CLOSED = "closed"


class TicketCategory(str, enum.Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    SUBSCRIPTION = "subscription"
    ACCOUNT = "account"
    PRODUCT = "product"
    SERVICE_REQUEST = "service_request"
    OTHER = "other"


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MessageRole(str, enum.Enum):
    CUSTOMER = "customer"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    AGENT_TRACE = "agent_trace"


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------
class User(Base):
    """A customer (or support-agent) account able to log in."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="customer")  # customer | support_rep | admin
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    account: Mapped["CustomerAccount"] = relationship(back_populates="user", uselist=False)
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="user")


class CustomerAccount(Base):
    """Business/account context the Customer Context Agent retrieves:
    plan, billing history, subscription status etc."""

    __tablename__ = "customer_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    plan_name: Mapped[str] = mapped_column(String(100), default="Free")
    subscription_status: Mapped[str] = mapped_column(String(50), default="active")
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly")
    last_charge_amount: Mapped[float] = mapped_column(default=0.0)
    last_charge_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    account_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    extra_metadata: Mapped[dict] = mapped_column(JSON, default=dict)

    user: Mapped["User"] = relationship(back_populates="account")


class Ticket(Base):
    """A persistent support ticket. This is the primary record surfaced
    to the frontend dashboard."""

    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_ref: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    subject: Mapped[str] = mapped_column(String(255))
    original_query: Mapped[str] = mapped_column(Text)

    category: Mapped[TicketCategory] = mapped_column(Enum(TicketCategory), default=TicketCategory.OTHER)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), default=Priority.MEDIUM)
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus), default=TicketStatus.OPEN)

    retrieved_knowledge: Mapped[list] = mapped_column(JSON, default=list)
    suggested_resolution: Mapped[str] = mapped_column(Text, default="")
    actions_performed: Mapped[list] = mapped_column(JSON, default=list)   # tool calls actually executed
    recommended_actions: Mapped[list] = mapped_column(JSON, default=list)  # actions proposed but NOT executed
    final_response: Mapped[str] = mapped_column(Text, default="")

    is_escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    escalation_reason: Mapped[str] = mapped_column(Text, default="")

    reviewer_verdict: Mapped[str] = mapped_column(String(50), default="")  # approved | needs_revision | rejected
    reviewer_notes: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="tickets")
    messages: Mapped[list["TicketMessage"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")
    agent_logs: Mapped[list["AgentExecutionLog"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")
    escalation: Mapped["EscalationRecord"] = relationship(back_populates="ticket", uselist=False, cascade="all, delete-orphan")


class TicketMessage(Base):
    """Multi-turn conversation history for a ticket (persisted long-term;
    mirrored short-term in Redis for fast in-flight agent access)."""

    __tablename__ = "ticket_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped["Ticket"] = relationship(back_populates="messages")


class AgentExecutionLog(Base):
    """Full agent execution history — which agent ran, what it decided,
    and how long it took. Powers the 'Agent Execution History' UI panel."""

    __tablename__ = "agent_execution_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    agent_name: Mapped[str] = mapped_column(String(100))
    step_order: Mapped[int] = mapped_column(Integer)
    input_summary: Mapped[str] = mapped_column(Text)
    output_summary: Mapped[str] = mapped_column(Text)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped["Ticket"] = relationship(back_populates="agent_logs")


class EscalationRecord(Base):
    """Escalation summary created by the Escalation Agent when human
    intervention is required."""

    __tablename__ = "escalation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), unique=True)
    reason: Mapped[str] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String(20), default="medium")
    summary_for_human: Mapped[str] = mapped_column(Text)
    assigned_to: Mapped[str] = mapped_column(String(255), default="unassigned")
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ticket: Mapped["Ticket"] = relationship(back_populates="escalation")
