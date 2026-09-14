import type { Priority } from "../types";

const PRIORITY_STYLES: Record<Priority, string> = {
  low: "border-slate-700 text-slate-500 dark:text-slate-500 dark:text-slate-400 bg-white dark:bg-panel-800",
  medium: "border-yellow-500/30 text-yellow-500 bg-yellow-500/10",
  high: "border-orange-500/30 text-orange-500 bg-orange-500/10",
  critical: "border-red-500/30 text-red-500 bg-red-500/10 shadow-sm",
};

export function PriorityPill({ priority }: { priority: Priority }) {
  return (
    <span className={`rounded-full border px-2.5 py-0.5 text-[10px] font-semibold tracking-wide uppercase ${PRIORITY_STYLES[priority]}`}>
      {priority}
    </span>
  );
}
