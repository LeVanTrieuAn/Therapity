import sys
sys.path.append('d:/thapsang/backend')
import cms_helper
import json

user_chats = cms_helper.get_chat_sessions('trieuan3499@gmail.com')
valid_sessions = [c.get('custom_title') for c in user_chats.values() if c.get('custom_title')]
for c in user_chats.values():
    for m in c.get('chat_history', []):
        if m.get('title'):
            valid_sessions.append(m['title'])
        if m.get('reasoning'):
            valid_sessions.append(m['reasoning'])

valid_sessions.extend(['T?o th? công', 'Ðu?c phân tích t? lu?ng suy nghi Socratic', 'Coach Session'])

tasks = cms_helper.get_tasks('trieuan3499@gmail.com')
deleted = 0
for t in tasks:
    link = t.get('contextLink')
    if link and link not in valid_sessions and not link.startswith('L? trình cá nhân'):
        cms_helper.delete_task(t['id'])
        deleted += 1

print(f'Deleted {deleted} polluted tasks.')
