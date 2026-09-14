import { useState, type FormEvent } from "react";
import type { TicketDetail } from "../types";
import { useAuth } from "../context/AuthContext";

interface Props {
  activeTicket: TicketDetail | null;
  onSend: (message: string) => Promise<void>;
  sending: boolean;
}

export function ChatPanel({ activeTicket, onSend, sending }: Props) {
  const [draft, setDraft] = useState("");
  const { user } = useAuth();

  const suggestedPrompts = [
    "I was charged twice this month",
    "I can't log into my account",
    "How do I upgrade my plan?"
  ];

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!draft.trim() || sending) return;
    const message = draft;
    
    setDraft("");
    
    try {
      await onSend(message);
    } catch (err) {
      alert("Failed to send message. Please try again.");
      setDraft(message);
    }
  }

  async function handlePromptClick(prompt: string) {
    if (sending) return;
    try {
      await onSend(prompt);
    } catch (err) {
      alert("Failed to send message. Please try again.");
      setDraft(prompt);
    }
  }

  const messages = activeTicket?.messages ?? [];

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-slate-200 dark:border-panel-800 px-6 py-4 bg-slate-50/50 dark:bg-panel-900/50">
        <h2 className="font-semibold text-lg text-slate-900 dark:text-slate-100 tracking-tight">
          {activeTicket ? activeTicket.subject : "New conversation"}
        </h2>
        {activeTicket && (
          <p className="mt-0.5 font-mono text-xs text-slate-500 dark:text-slate-500">{activeTicket.ticket_ref}</p>
        )}
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto px-6 py-5 relative">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="mb-4 h-16 w-16 rounded-full bg-accent-500/10 flex items-center justify-center">
               <svg className="h-8 w-8 text-accent-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" /></svg>
            </div>
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
              Welcome back, {user?.full_name?.split(' ')[0]} ??
            </h3>
            <p className="max-w-sm text-sm text-slate-500 dark:text-slate-400">
              How can we help today? Describe your issue - billing, technical, subscription, or account - and our agentic resolution system will assist you.
            </p>

            <div className="mt-10 grid gap-3 w-full max-w-md">
              {suggestedPrompts.map((prompt) => (
                <button 
                  key={prompt}
                  onClick={() => handlePromptClick(prompt)}
                  disabled={sending}
                  className="flex items-center gap-4 w-full text-left p-4 rounded-xl border border-slate-200 dark:border-panel-700 bg-white dark:bg-panel-800 hover:border-accent-500 dark:hover:border-accent-500 hover:shadow-sm transition-all group disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-50 dark:bg-panel-700 text-slate-400 group-hover:text-accent-500 group-hover:bg-accent-50 dark:group-hover:bg-accent-500/10 transition-colors">
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  </div>
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-200 group-hover:text-accent-600 dark:group-hover:text-accent-400">{prompt}</span>
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, idx) => (
          <div key={idx} className={`flex w-full animate-fade-in ${m.role === "customer" ? "justify-end" : "justify-start"}`}>
            {m.role !== "customer" && (
              <div className="mr-3 mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent-500/10 text-accent-500 ring-1 ring-accent-500/20">
                <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              </div>
            )}
            <div className="flex flex-col gap-1.5 max-w-[75%]">
              <div
                className={`rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
                  m.role === "customer"
                    ? "bg-accent-600 text-white rounded-br-sm"
                    : "bg-white dark:bg-panel-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-panel-700 rounded-bl-sm"
                }`}
              >
                {m.content}
              </div>
              {m.created_at && (
                <span className={`text-[10px] text-slate-500 dark:text-slate-500 font-medium ${m.role === "customer" ? "text-right mr-1" : "ml-1"}`}>
                  {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              )}
            </div>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start animate-fade-in pb-4">
            <div className="mr-3 mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent-500/10 text-accent-500 ring-1 ring-accent-500/20">
                <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            </div>
            <div className="rounded-2xl bg-white dark:bg-panel-800 border border-slate-200 dark:border-panel-700 px-5 py-3 text-sm text-slate-500 dark:text-slate-400 shadow-sm flex items-center gap-3 relative overflow-hidden rounded-bl-sm">
              <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-slate-900/5 dark:via-white/5 to-transparent"></div>
              <span className="relative z-10 flex items-center gap-2.5 font-medium">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-500"></span>
                </span>
                Agents working...
              </span>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-slate-200 dark:border-panel-800 px-6 py-4 bg-slate-50/50 dark:bg-panel-900/50">
        <div className="flex items-end gap-3">
          <textarea
            value={draft}
            disabled={sending}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            rows={1}
            placeholder={sending ? "Please wait..." : "Describe your issue..."}
            className="flex-1 resize-none rounded-xl bg-white dark:bg-panel-800 px-4 py-3 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 outline-none border border-slate-200 dark:border-panel-700 focus:border-accent-500 focus:ring-1 focus:ring-accent-500 transition-all shadow-inner disabled:opacity-50 disabled:bg-slate-50 dark:disabled:bg-panel-900"
          />
          <button
            type="submit"
            disabled={sending || !draft.trim()}
            className="rounded-xl bg-accent-600 hover:bg-accent-500 px-5 py-3 text-sm font-medium text-white shadow-sm transition-all disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-accent-600"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
