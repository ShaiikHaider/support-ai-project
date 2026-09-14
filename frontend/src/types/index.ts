export type TicketStatus =
  | "open"
  | "in_progress"
  | "resolved"
  | "requires_more_information"
  | "escalated"
  | "closed";

export type Priority = "low" | "medium" | "high" | "critical";

export interface RetrievedChunk {
  id: string;
  title: string;
  category: string;
  content: string;
  relevance_score: number;
}

export interface PerformedAction {
  tool: string;
  status: string;
  [key: string]: unknown;
}

export interface AgentTraceEntry {
  agent_name: string;
  step_order: number;
  input_summary: string;
  output_summary: string;
  duration_ms: number;
}

export interface TicketMessage {
  role: "customer" | "assistant" | "system" | "agent_trace";
  content: string;
  created_at: string;
}

export interface Ticket {
  id: number;
  ticket_ref: string;
  subject: string;
  original_query: string;
  category: string;
  priority: Priority;
  status: TicketStatus;
  retrieved_knowledge: RetrievedChunk[];
  suggested_resolution: string;
  recommended_actions: string[];
  actions_performed: PerformedAction[];
  final_response: string;
  is_escalated: boolean;
  escalation_reason: string;
  reviewer_verdict: string;
  reviewer_notes: string;
  created_at: string;
  updated_at: string;
}

export interface TicketDetail extends Ticket {
  agent_trace: AgentTraceEntry[];
  messages: TicketMessage[];
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
}
