import type { Ticket } from "../types";
import { PriorityPill } from "./PriorityPill";
import { StatusBadge } from "./StatusBadge";

interface Props {
  tickets: Ticket[];
  activeTicketId: number | null;
  onSelect: (id: number) => void;
  onNewTicket: () => void;
}

export function TicketList({ tickets, activeTicketId, onSelect, onNewTicket }: Props) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between px-6 py-5">
        <h2 className="font-semibold text-lg text-slate-900 dark:text-slate-100 tracking-tight">Tickets</h2>
        <button
          onClick={onNewTicket}
          className="rounded-lg bg-accent-500/10 px-3 py-1.5 text-xs font-semibold text-accent-500 ring-1 ring-accent-500/30 transition-colors hover:bg-accent-500/20"
        >
          + New
        </button>
      </div>
      <div className="flex-1 overflow-y-auto px-4 pb-4">
        {tickets.length === 0 && (
          <p className="px-2 py-8 text-center text-sm text-slate-500 dark:text-slate-500">
            No tickets yet - start a conversation to create one.
          </p>
        )}
        {tickets.map((t) => (
          <button
            key={t.id}
            onClick={() => onSelect(t.id)}
            className={`mb-2 w-full rounded-xl px-4 py-3 text-left transition-all duration-200 border-l-4 shadow-sm ${
              activeTicketId === t.id 
                ? "bg-white dark:bg-panel-800 border-accent-500 ring-1 ring-slate-200 dark:ring-panel-700 shadow-surface" 
                : "bg-slate-50 dark:bg-panel-900 border-transparent hover:bg-panel-800 hover:border-panel-700"
            }`}
          >
            <div className="flex items-center justify-between gap-2 mb-2">
              <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500 dark:text-slate-500 font-semibold">{t.ticket_ref}</span>
              <PriorityPill priority={t.priority} />
            </div>
            <p className="line-clamp-1 text-sm font-medium text-slate-800 dark:text-slate-200 leading-snug">{t.subject}</p>
            <div className="mt-3 flex items-center justify-between">
              <StatusBadge status={t.status} />
              <span className="text-[11px] font-medium capitalize text-slate-500 dark:text-slate-500 bg-white dark:bg-panel-800 px-2 py-0.5 rounded-full ring-1 ring-slate-200 dark:ring-panel-700">{t.category}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
