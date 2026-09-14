import os
import glob

# Mapping from existing dark-mode class to (light-mode-class dark:existing-class)
replacements = {
    "bg-panel-900": "bg-slate-50 dark:bg-panel-900",
    "bg-panel-800": "bg-white dark:bg-panel-800",
    "bg-panel-700": "bg-slate-200 dark:bg-panel-700",
    "border-panel-800": "border-slate-200 dark:border-panel-800",
    "border-panel-700": "border-slate-200 dark:border-panel-700",
    "ring-panel-700": "ring-slate-200 dark:ring-panel-700",
    "text-slate-100": "text-slate-900 dark:text-slate-100",
    "text-slate-200": "text-slate-800 dark:text-slate-200",
    "text-slate-300": "text-slate-700 dark:text-slate-300",
    "text-slate-400": "text-slate-500 dark:text-slate-400",
    "text-slate-500": "text-slate-500 dark:text-slate-500",
    # Some special cases for the chat and layout
    "bg-black/50": "bg-slate-900/50 dark:bg-black/50",
}

directory = r'd:\downloads\support-ai-project\support-ai\frontend\src'

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith(('.tsx', '.ts', '.css')):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            for old, new in replacements.items():
                # Avoid double-replacing if the script is run multiple times
                if new not in content:
                    # Simple string replace, might need word boundaries but tailwind classes are space-separated
                    import re
                    # Replace only if surrounded by spaces/quotes/backticks
                    content = re.sub(rf'(?<!\w|\:){re.escape(old)}(?!\w|-)', new, content)
            
            if content != original:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)

print("Patch complete.")
