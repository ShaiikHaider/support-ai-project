import os

path = r'd:\downloads\support-ai-project\support-ai\frontend\src\components\TicketList.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace button content
new_button = '''          <button
            key={t.id}
            onClick={() => onSelect(t.id)}
            className={mb-2 w-full rounded-xl px-4 py-3 text-left transition-all duration-200 border-l-4 shadow-sm \}
          >
            <div className="flex items-center justify-between gap-2 mb-2">
              <span className="font-mono text-[10px] uppercase tracking-wider text-slate-500 font-semibold">{t.ticket_ref}</span>
              <PriorityPill priority={t.priority} />
            </div>
            <p className="line-clamp-1 text-sm font-medium text-slate-200 leading-snug">{t.subject}</p>
            <div className="mt-3 flex items-center justify-between">
              <StatusBadge status={t.status} />
              <span className="text-[11px] font-medium capitalize text-slate-500 bg-panel-800 px-2 py-0.5 rounded-full ring-1 ring-panel-700">{t.category}</span>
            </div>
          </button>'''

import re
content = re.sub(r'          <button.*?</button>', new_button, content, flags=re.DOTALL)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
