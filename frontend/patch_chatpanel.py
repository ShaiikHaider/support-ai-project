import os
import re

# --- 1. Patch tailwind.config.js for shimmer ---
tw_path = r'd:\downloads\support-ai-project\support-ai\frontend\tailwind.config.js'
with open(tw_path, 'r', encoding='utf-8') as f:
    tw_content = f.read()

if 'shimmer:' not in tw_content:
    tw_content = tw_content.replace(
        "'fade-in': 'fadeIn 0.2s ease-out forwards',",
        "'fade-in': 'fadeIn 0.2s ease-out forwards',\n        'shimmer': 'shimmer 2s infinite linear',"
    )
    tw_content = tw_content.replace(
        "'100%': { opacity: '1', transform: 'translateY(0)' },\n        }",
        "'100%': { opacity: '1', transform: 'translateY(0)' },\n        },\n        shimmer: {\n          '100%': { transform: 'translateX(100%)' }\n        }"
    )
    with open(tw_path, 'w', encoding='utf-8') as f:
        f.write(tw_content)

# --- 2. Patch ChatPanel.tsx ---
cp_path = r'd:\downloads\support-ai-project\support-ai\frontend\src\components\ChatPanel.tsx'
with open(cp_path, 'r', encoding='utf-8') as f:
    cp_content = f.read()

# Replace header
cp_content = cp_content.replace(
    'className="font-display text-lg text-slate-100"',
    'className="font-semibold text-lg text-slate-100 tracking-tight"'
)
cp_content = cp_content.replace(
    'className="border-b border-panel-700 px-6 py-4"',
    'className="border-b border-panel-800 px-6 py-4 bg-panel-900/50"'
)

# Replace message mapping
old_map = '''        {messages.map((m, idx) => (
          <div key={idx} className={lex \}>
            <div
              className={max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed \}
            >
              {m.content}
            </div>
          </div>
        ))}'''

new_map = '''        {messages.map((m, idx) => (
          <div key={idx} className={lex w-full animate-fade-in \}>
            {m.role !== "customer" && (
              <div className="mr-3 mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent-500/10 text-accent-500 ring-1 ring-accent-500/20">
                <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              </div>
            )}
            <div className="flex flex-col gap-1.5 max-w-[75%]">
              <div
                className={ounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm \}
              >
                {m.content}
              </div>
              {m.created_at && (
                <span className={	ext-[10px] text-slate-500 font-medium \}>
                  {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              )}
            </div>
          </div>
        ))}'''
cp_content = cp_content.replace(old_map, new_map)

# Replace sending state
old_sending = '''        {sending && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-panel-800 px-4 py-2.5 text-sm text-slate-400 ring-1 ring-panel-700">
              <span className="inline-flex gap-1">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-signal-teal" />
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-signal-teal [animation-delay:150ms]" />
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-signal-teal [animation-delay:300ms]" />
              </span>
              <span className="ml-2">Agents working?</span>
            </div>
          </div>
        )}'''

new_sending = '''        {sending && (
          <div className="flex justify-start animate-fade-in">
            <div className="mr-3 mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent-500/10 text-accent-500 ring-1 ring-accent-500/20">
                <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
            </div>
            <div className="rounded-2xl bg-panel-800 border border-panel-700 px-5 py-3 text-sm text-slate-400 shadow-sm flex items-center gap-3 relative overflow-hidden rounded-bl-sm">
              <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/5 to-transparent"></div>
              <span className="relative z-10 flex items-center gap-2.5 font-medium">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-500"></span>
                </span>
                Agents working...
              </span>
            </div>
          </div>
        )}'''
cp_content = cp_content.replace(old_sending, new_sending)

# Replace textarea and button
old_form = '''      <form onSubmit={handleSubmit} className="border-t border-panel-700 px-4 py-3">
        <div className="flex items-end gap-2">
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            rows={1}
            placeholder="Describe your issue?"
            className="flex-1 resize-none rounded-lg bg-panel-800 px-3.5 py-2.5 text-sm text-slate-100 placeholder-slate-500 outline-none ring-1 ring-panel-700 focus:ring-signal-teal/50"
          />
          <button
            type="submit"
            disabled={sending || !draft.trim()}
            className="rounded-lg bg-signal-teal px-4 py-2.5 text-sm font-medium text-panel-900 transition disabled:cursor-not-allowed disabled:opacity-40"
          >
            Send
          </button>
        </div>
      </form>'''

new_form = '''      <form onSubmit={handleSubmit} className="border-t border-panel-800 px-6 py-4 bg-panel-900/50">
        <div className="flex items-end gap-3">
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            rows={1}
            placeholder="Describe your issue..."
            className="flex-1 resize-none rounded-xl bg-panel-800 px-4 py-3 text-sm text-slate-100 placeholder-slate-500 outline-none border border-panel-700 focus:border-accent-500 focus:ring-1 focus:ring-accent-500 transition-all shadow-inner"
          />
          <button
            type="submit"
            disabled={sending || !draft.trim()}
            className="rounded-xl bg-accent-600 hover:bg-accent-500 px-5 py-3 text-sm font-medium text-white shadow-sm transition-all disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-accent-600"
          >
            Send
          </button>
        </div>
      </form>'''
cp_content = cp_content.replace(old_form, new_form)

with open(cp_path, 'w', encoding='utf-8') as f:
    f.write(cp_content)
