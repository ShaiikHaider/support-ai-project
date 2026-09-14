import os
import re

path = r'd:\downloads\support-ai-project\support-ai\frontend\src\pages\DashboardPage.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add states
content = content.replace(
    'const [sending, setSending] = useState(false);',
    'const [sending, setSending] = useState(false);\n  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);\n  const [isDetailOpen, setIsDetailOpen] = useState(false);'
)

# Update handleNewTicket
content = content.replace(
    'setActiveTicket(null);\n  }',
    'setActiveTicket(null);\n    setIsMobileMenuOpen(false);\n  }'
)

# Replace the entire return statement
return_replacement = '''  return (
    <div className="flex h-screen bg-panel-900 text-slate-100 overflow-hidden relative">
      {/* Mobile Header (visible only on small screens) */}
      <div className="md:hidden absolute top-0 left-0 right-0 h-14 border-b border-panel-800 bg-panel-900/90 backdrop-blur-md z-20 flex items-center justify-between px-4">
        <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="p-2 text-slate-400 hover:text-slate-200">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
        </button>
        <span className="font-semibold text-accent-500">Resolve</span>
        <button onClick={() => setIsDetailOpen(!isDetailOpen)} className="p-2 text-slate-400 hover:text-slate-200">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </button>
      </div>

      {/* Sidebar (Drawer on Mobile) */}
      <aside className={ixed inset-y-0 left-0 z-30 w-72 transform border-r border-panel-800 bg-panel-900 transition-transform duration-300 ease-in-out md:relative md:translate-x-0 }>
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
        <div className="fixed inset-0 z-20 bg-black/50 md:hidden" onClick={() => setIsMobileMenuOpen(false)} />
      )}

      {/* Main Chat Area */}
      <main className="flex min-w-0 flex-1 flex-col pt-14 md:pt-0 relative bg-panel-900">
        <div className="hidden md:flex items-center justify-between border-b border-panel-800 px-6 py-4 bg-panel-900 z-10">
          <span className="font-semibold text-accent-500 tracking-wide">Resolve</span>
          <div className="flex items-center gap-4 text-sm text-slate-400">
            <span>{user?.full_name}</span>
            <button onClick={signOut} className="text-slate-500 hover:text-accent-500 transition-colors">
              Sign out
            </button>
          </div>
        </div>
        <div className="min-h-0 flex-1">
          <ChatPanel activeTicket={activeTicket} onSend={handleSend} sending={sending} />
        </div>
      </main>

      {/* Detail Panel (Bottom Sheet on Mobile) */}
      <aside className={ixed inset-x-0 bottom-0 z-30 h-[80vh] overflow-y-auto transform border-t border-panel-800 bg-panel-900 transition-transform duration-300 ease-in-out md:relative md:h-auto md:w-96 md:border-l md:border-t-0 md:translate-y-0 md:overflow-visible }>
        {/* Mobile Detail Panel Handle */}
        <div className="md:hidden flex items-center justify-center pt-3 pb-1 cursor-pointer" onClick={() => setIsDetailOpen(false)}>
          <div className="w-12 h-1.5 rounded-full bg-panel-700"></div>
        </div>
        <TicketDetailPanel ticket={activeTicket} />
      </aside>
      
      {/* Mobile Detail Panel Overlay */}
      {isDetailOpen && (
        <div className="fixed inset-0 z-20 bg-black/50 md:hidden" onClick={() => setIsDetailOpen(false)} />
      )}
    </div>
  );
}'''

content = re.sub(r'  return \(\s*<div.*?</div>\s*\);\s*\}', return_replacement, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
