import { useCallback, useEffect, useState } from "react";
import { getTicket, listTickets, sendChatMessage } from "../api/client";
import { ChatPanel } from "../components/ChatPanel";
import { TicketDetailPanel } from "../components/TicketDetailPanel";
import { TicketList } from "../components/TicketList";
import { useAuth } from "../context/AuthContext";
import type { Ticket, TicketDetail } from "../types";

export function DashboardPage() {
  const { user, signOut } = useAuth();
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [activeTicketId, setActiveTicketId] = useState<number | null>(null);
  const [activeTicket, setActiveTicket] = useState<TicketDetail | null>(null);
  const [sending, setSending] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  const refreshTickets = useCallback(async () => {
    const data = await listTickets();
    setTickets(data);
  }, []);

  useEffect(() => {
    refreshTickets();
  }, [refreshTickets]);

  useEffect(() => {
    if (activeTicketId == null) {
      setActiveTicket(null);
      return;
    }
    getTicket(activeTicketId).then(setActiveTicket);
  }, [activeTicketId]);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  async function handleSend(message: string) {
    setSending(true);
    // optimistic local echo so the chat feels responsive while agents run
    setActiveTicket((prev) => {
      const newMessage = { role: "customer" as const, content: message, created_at: new Date().toISOString() };
      if (prev) {
        return { ...prev, messages: [...prev.messages, newMessage] };
      }
      return {
        id: 0,
        ticket_ref: "",
        subject: message.slice(0, 80),
        original_query: message,
        category: "other",
        priority: "medium",
        status: "in_progress",
        retrieved_knowledge: [],
        suggested_resolution: "",
        recommended_actions: [],
        actions_performed: [],
        final_response: "",
        is_escalated: false,
        escalation_reason: "",
        reviewer_verdict: "",
        reviewer_notes: "",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        agent_trace: [],
        messages: [newMessage],
      };
    });
    try {
      const updated = await sendChatMessage(message, activeTicketId ?? undefined);
      setActiveTicket(updated);
      setActiveTicketId(updated.id);
      await refreshTickets();
    } finally {
      setSending(false);
    }
  }

  function handleNewTicket() {
    setActiveTicketId(null);
    setActiveTicket(null);
    setIsMobileMenuOpen(false);
  }

  return (
    <div className="flex h-[100dvh] w-full bg-slate-50 dark:bg-panel-900 text-slate-900 dark:text-slate-100 overflow-hidden relative">
      {/* Mobile Header (visible only on small screens) */}
      <div className="md:hidden absolute top-0 left-0 right-0 h-14 border-b border-slate-200 dark:border-panel-800 bg-white/90 dark:bg-panel-900/90 backdrop-blur-md z-20 flex items-center justify-between px-4 w-full">
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
        </button>
        <span className="font-semibold text-accent-500">Resolve</span>
        <button onClick={() => setIsDetailOpen(!isDetailOpen)} className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </button>
      </div>

      {/* Sidebar (Drawer on Mobile) */}
      <aside className={`fixed inset-y-0 left-0 z-30 w-72 max-w-[85vw] transform border-r border-slate-200 dark:border-panel-800 bg-white dark:bg-panel-900 transition-transform duration-300 ease-in-out md:relative md:translate-x-0 flex-shrink-0 ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <TicketList
          tickets={tickets}
          activeTicketId={activeTicketId}
          onSelect={(id) => {
            setActiveTicketId(id);
            setIsMobileMenuOpen(false);
          }}
          onNewTicket={handleNewTicket}
        />
      </aside>

      {/* Mobile Drawer Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-20 bg-slate-900/50 dark:bg-black/50 md:hidden" onClick={() => setIsMobileMenuOpen(false)} />
      )}

      {/* Main Chat Area */}
      <main className="flex min-w-0 flex-1 flex-col pt-14 md:pt-0 relative bg-slate-50 dark:bg-panel-900 h-full overflow-hidden w-full">
        <div className="hidden md:flex items-center justify-between border-b border-slate-200 dark:border-panel-800 px-6 py-3.5 bg-white dark:bg-panel-900 z-10 w-full">
          <span className="font-semibold text-accent-500 tracking-wide">Resolve</span>
          
          <div className="flex items-center gap-2">
            {/* Theme Toggle */}
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="flex items-center justify-center w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-200 dark:bg-panel-800 dark:hover:bg-panel-700 text-slate-600 dark:text-slate-300 transition-colors focus:outline-none focus:ring-2 focus:ring-accent-500/50"
              title="Toggle theme"
            >
              {isDarkMode ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
              )}
            </button>
            
            <div className="h-5 w-px bg-slate-200 dark:bg-panel-700 mx-2"></div>

            {/* User Menu / Sign Out */}
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{user?.full_name}</span>
              <button 
                onClick={signOut}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 hover:bg-slate-100 dark:hover:bg-panel-800 transition-colors focus:outline-none focus:ring-2 focus:ring-accent-500/50"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                Sign out
              </button>
            </div>
          </div>
        </div>
        <div className="min-h-0 flex-1 relative w-full">
          <ChatPanel activeTicket={activeTicket} onSend={handleSend} sending={sending} />
        </div>
      </main>

      {/* Detail Panel (Bottom Sheet on Mobile) */}
      <aside className={`fixed inset-x-0 bottom-0 z-30 h-[80dvh] overflow-y-auto transform border-t border-slate-200 dark:border-panel-800 bg-white dark:bg-panel-900 transition-transform duration-300 ease-in-out md:relative md:h-full md:w-96 md:border-l md:border-t-0 md:translate-y-0 md:overflow-y-auto flex-shrink-0 ${isDetailOpen ? 'translate-y-0' : 'translate-y-full md:translate-y-0'}`}>
        {/* Mobile Detail Panel Handle */}
        <div className="md:hidden flex items-center justify-center pt-3 pb-1 cursor-pointer" onClick={() => setIsDetailOpen(false)}>
          <div className="w-12 h-1.5 rounded-full bg-slate-200 dark:bg-panel-700"></div>
        </div>
        <TicketDetailPanel ticket={activeTicket} />
      </aside>
      
      {/* Mobile Detail Panel Overlay */}
      {isDetailOpen && (
        <div className="fixed inset-0 z-20 bg-slate-900/50 dark:bg-black/50 md:hidden" onClick={() => setIsDetailOpen(false)} />
      )}
    </div>
  );
}
