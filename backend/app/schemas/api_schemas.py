from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ---------------- Auth ----------------
class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str

    model_config = {"from_attributes": True}


# ---------------- Chat / Ticket ----------------
class ChatMessageIn(BaseModel):
    message: str = Field(min_length=1)
    ticket_id: int | None = Field(default=None, description="Omit to start a new ticket")


class AgentTraceEntryOut(BaseModel):
    agent_name: str
    step_order: int
    input_summary: str
    output_summary: str
    duration_ms: int


class TicketOut(BaseModel):
    id: int
    ticket_ref: str
    subject: str
    original_query: str
    category: str
    priority: str
    status: str

    retrieved_knowledge: list[dict]
    suggested_resolution: str
    recommended_actions: list[str]
    actions_performed: list[dict]
    final_response: str

    is_escalated: bool
    escalation_reason: str

    reviewer_verdict: str
    reviewer_notes: str

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketDetailOut(TicketOut):
    agent_trace: list[AgentTraceEntryOut]
    messages: list[dict]


class ChatResponseOut(BaseModel):
    ticket: TicketDetailOut
