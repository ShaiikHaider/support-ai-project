import os

path = r'd:\downloads\support-ai-project\support-ai\frontend\src\components\ChatPanel.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("Welcome back, {user?.full_name?.split(' ')[0]} ??", "Welcome back, {user?.full_name?.split(' ')[0]} ??")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
