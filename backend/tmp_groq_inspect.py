import os
from pathlib import Path

from groq import Groq

# Load API key from backend/.env if present
env_path = Path(__file__).resolve().parent / '.env'
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            if k == 'GROQ_API_KEY':
                os.environ[k] = v.strip()

api_key = os.environ.get('GROQ_API_KEY')
print('API_KEY_PRESENT', bool(api_key))
print('API_KEY_PREFIX', api_key[:4] if api_key else None)

client = Groq(api_key=api_key)
message = client.chat.completions.create(
    model='openai/gpt-oss-120b',
    messages=[{'role': 'user', 'content': 'Write one short sentence saying OK.'}],
    max_tokens=50,
)

print('MESSAGE_TYPE', type(message))
print('MESSAGE_REPR', repr(message)[:2000])
print('HAS_CHOICES', hasattr(message, 'choices'))
print('CHOICES_OBJ', message.choices)
print('CHOICES_TYPE', type(message.choices))
print('CHOICES_LEN', len(message.choices))
choice = message.choices[0]
print('CHOICE_TYPE', type(choice))
print('CHOICE_REPR', repr(choice)[:2000])
print('CHOICE_DICT', getattr(choice, '__dict__', None))
print('CHOICE_CONTENT', getattr(choice, 'content', None))
print('CHOICE_TEXT', getattr(choice, 'text', None))
print('CHOICE_MESSAGE', getattr(choice, 'message', None))
msg = getattr(choice, 'message', None)
print('MSG_TYPE', type(msg) if msg is not None else None)
print('MSG_REPR', repr(msg)[:2000] if msg is not None else None)
print('MSG_DICT', getattr(msg, '__dict__', None))
if isinstance(msg, dict):
    print('MSG_KEYS', list(msg.keys()))
    print('MSG_CONTENT', msg.get('content'), msg.get('text'))
else:
    print('MSG_CONTENT', getattr(msg, 'content', None), getattr(msg, 'text', None))
