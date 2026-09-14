import type { AgentTraceEntry } from "../types";

const agentIcons: Record<string, React.ReactNode> = {
  Router: <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" /></svg>,
  Retriever: <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>,
  Diagnosis: <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>,
  Action: <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>,
  Reviewer: <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>,
  Escalator: <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>,
  Responder: <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>,
};

export function AgentTimeline({ trace }: { trace: AgentTraceEntry[] }) {
  if (trace.length === 0) {
    return <p className="text-sm text-slate-500 dark:text-slate-500">No agent runs recorded yet.</p>;
  }

  return (
    <ol className="relative space-y-0">
      {trace.map((entry, idx) => {
        const icon = agentIcons[entry.agent_name] || <div className="w-1.5 h-1.5 bg-current rounded-full" />;
        return (
          <li key={`${entry.agent_name}-${entry.step_order}`} className="relative flex gap-4 pb-6 last:pb-0 group">
            <div className="flex flex-col items-center">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-50 dark:bg-panel-900 text-slate-500 dark:text-slate-500 dark:text-slate-400 ring-1 ring-slate-200 dark:ring-panel-700 shadow-sm group-hover:text-accent-500 group-hover:ring-accent-500/50 transition-colors">
                {icon}
              </span>
              {idx < trace.length - 1 && <span className="mt-2 w-px flex-1 bg-slate-200 dark:bg-panel-700" />}
            </div>
            <div className="flex-1 pb-1 pt-1">
              <div className="flex items-baseline justify-between gap-3">
                <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">{entry.agent_name}</h4>
                <span className="font-mono text-[10px] text-slate-500 dark:text-slate-500">{entry.duration_ms}ms</span>
              </div>
              <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-500 dark:text-slate-400 leading-relaxed">
                <span className="font-medium text-slate-500 dark:text-slate-500">in:</span> {entry.input_summary}
              </p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-500 dark:text-slate-400 leading-relaxed">
                <span className="font-medium text-slate-500 dark:text-slate-500">out:</span> {entry.output_summary}
              </p>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
