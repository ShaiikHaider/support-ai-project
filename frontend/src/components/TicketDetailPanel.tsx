import type { TicketDetail } from "../types";
import { AgentTimeline } from "./AgentTimeline";
import { PriorityPill } from "./PriorityPill";
import { StatusBadge } from "./StatusBadge";

export function TicketDetailPanel({ ticket }: { ticket: TicketDetail | null }) {
  if (!ticket) {
    return (
      <div className="flex h-full items-center justify-center px-6">
        <p className="text-center text-sm text-slate-500 dark:text-slate-500">
          Ticket details, retrieved knowledge, and agent trace will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto px-5 py-5 space-y-4">
      {/* Status header */}
      <div className="rounded-xl bg-white dark:bg-panel-800 p-5 shadow-surface ring-1 ring-slate-200 dark:ring-panel-700">
        <div className="flex items-center justify-between">
          <StatusBadge status={ticket.status} />
          <PriorityPill priority={ticket.priority} />
        </div>
        <p className="mt-4 text-[10px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-500">Issue category</p>
        <p className="text-sm font-medium capitalize text-slate-800 dark:text-slate-200 mt-1">{ticket.category.replace("_", " ")}</p>
      </div>

      {/* Customer query */}
      <Section title="Customer query">
        <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{ticket.original_query}</p>
      </Section>

      {/* Retrieved knowledge */}
      <Section title="Retrieved knowledge">
        {ticket.retrieved_knowledge.length === 0 ? (
          <EmptyNote text="No knowledge-base sources retrieved for this turn." />
        ) : (
          <ul className="space-y-2">
            {ticket.retrieved_knowledge.map((chunk) => (
              <li key={chunk.id} className="rounded-lg bg-slate-50 dark:bg-panel-900 p-3 ring-1 ring-slate-200 dark:ring-panel-700 shadow-inner">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">{chunk.title}</span>
                  <span className="font-mono text-[10px] text-accent-500 bg-accent-500/10 px-1.5 py-0.5 rounded">
                    {(chunk.relevance_score * 100).toFixed(0)}% match
                  </span>
                </div>
                <p className="text-xs leading-relaxed text-slate-500 dark:text-slate-500 dark:text-slate-400">{chunk.content}</p>
              </li>
            ))}
          </ul>
        )}
      </Section>

      {/* Suggested resolution */}
      <Section title="Suggested resolution">
        <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{ticket.suggested_resolution || "-"}</p>
      </Section>

      {/* Recommended vs performed actions */}
      <Section title="Recommended actions (proposed)">
        {ticket.recommended_actions.length === 0 ? (
          <EmptyNote text="No actions recommended." />
        ) : (
          <ul className="space-y-2">
            {ticket.recommended_actions.map((a, i) => (
              <li key={i} className="rounded-lg border-2 border-dashed border-slate-200 dark:border-panel-700 bg-white dark:bg-panel-800/50 px-3 py-2 text-sm text-slate-700 dark:text-slate-300">
                {a}
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Actions performed">
        {ticket.actions_performed.length === 0 ? (
          <EmptyNote text="No automated actions were executed." />
        ) : (
          <ul className="space-y-2">
            {ticket.actions_performed.map((a, i) => (
              <li
                key={i}
                className="flex items-center justify-between rounded-lg bg-emerald-500/10 px-3 py-2.5 text-xs ring-1 ring-emerald-500/30"
              >
                <div className="flex items-center gap-2 text-emerald-500">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                  <span className="font-mono font-medium">{a.tool as string}</span>
                </div>
                <span className="text-emerald-600 font-medium capitalize">{a.status as string}</span>
              </li>
            ))}
          </ul>
        )}
      </Section>

      {/* Escalation status */}
      <Section title="Escalation status">
        {ticket.is_escalated ? (
          <div className="rounded-lg bg-red-500/10 p-3 ring-1 ring-red-500/30">
            <p className="text-xs font-bold text-red-500 flex items-center gap-1.5">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
              Escalated to human support
            </p>
            <p className="mt-1.5 text-xs text-slate-700 dark:text-slate-300 leading-relaxed">{ticket.escalation_reason}</p>
          </div>
        ) : (
          <EmptyNote text="Not escalated - handled autonomously." />
        )}
      </Section>

      {/* Reviewer verdict */}
      <Section title="Reviewer verdict">
        <p className="text-sm capitalize text-slate-700 dark:text-slate-300 font-medium">{ticket.reviewer_verdict || "-"}</p>
        {ticket.reviewer_notes && <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-500 leading-relaxed">{ticket.reviewer_notes}</p>}
      </Section>

      {/* Final response */}
      <Section title="Final response to customer">
        <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-800 dark:text-slate-200">{ticket.final_response || "-"}</p>
      </Section>

      {/* Agent execution history */}
      <Section title="Agent execution history">
        <AgentTimeline trace={ticket.agent_trace} />
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl bg-white dark:bg-panel-800 p-5 shadow-surface ring-1 ring-slate-200 dark:ring-panel-700">
      <h3 className="mb-3 text-[10px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-500">{title}</h3>
      {children}
    </div>
  );
}

function EmptyNote({ text }: { text: string }) {
  return <p className="text-xs text-slate-500 dark:text-slate-500">{text}</p>;
}
