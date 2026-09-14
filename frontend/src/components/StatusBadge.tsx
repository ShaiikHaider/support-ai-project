import type { TicketStatus } from "../types";

const STATUS_STYLES: Record<TicketStatus, { label: string; dot: string; text: string }> = {
  open: { label: "Open", dot: "bg-slate-400", text: "text-slate-700 dark:text-slate-300" },
  in_progress: { label: "In progress", dot: "bg-accent-500 animate-pulse", text: "text-accent-500" },
  resolved: { label: "Resolved", dot: "bg-emerald-500", text: "text-emerald-500" },
  requires_more_information: { label: "Needs more info", dot: "bg-yellow-500", text: "text-yellow-500" },
  escalated: { label: "Escalated", dot: "bg-red-500", text: "text-red-500" },
  closed: { label: "Closed", dot: "bg-slate-600", text: "text-slate-500 dark:text-slate-500" },
};

export function StatusBadge({ status }: { status: TicketStatus }) {
  const style = STATUS_STYLES[status] ?? STATUS_STYLES.open;
  return (
    <span className={`inline-flex items-center gap-2 text-xs font-semibold tracking-wide ${style.text}`}>
      <span className={`h-2 w-2 rounded-full shadow-sm ${style.dot}`} />
      {style.label}
    </span>
  );
}
