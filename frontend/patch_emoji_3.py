import os

path = r'd:\downloads\support-ai-project\support-ai\frontend\src\components\ChatPanel.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("??", "??")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
