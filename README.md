# EchoSpace

Anonymous group chat + AI “Tree Hole” (emotional support chat). Django backend, Bootstrap front, SQLite locally / Postgres in prod.

## What’s in it

- Home, register / login / guest.
- Lobby: list rooms, create (if not guest), join. Group chat via polling.
- AI Tree Hole: chat with AI (mock or openai/dashscope). Can embed AppFlow iframe if you set the env vars.
- Dashboard for staff (counts, rooms, messages, AI).

## Run locally

Clone, venv, install deps:

```bash
git clone <your-repo-url>
cd EchoSpaceProject
python -m venv .venv
.venv\Scripts\activate   # Windows; on Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Copy env and edit:

```bash
cp .env.example .env
```

In `.env`: `SECRET_KEY`, `DEBUG=True`, `AI_PROVIDER=mock` (or `openai`/`dashscope` with keys). For AppFlow embed: `APPFLOW_AI_CHAT_ENABLED=True`, `APPFLOW_AI_CHAT_URL=<your AppFlow page url>`.

Migrate and run:

```bash
python manage.py migrate
python manage.py runserver
```

Optional: `createsuperuser` for admin/dashboard. Then open http://127.0.0.1:8000/

## Tests

```bash
python manage.py test
```

Covers main, accounts, chat (lobby/rooms/API), ai_chat (mock + appflow config), dashboard.

## Deploy (e.g. Render)

New Web Service, connect repo, add Postgres (`DATABASE_URL`). Set env vars from `.env.example`. Build: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`. Start: `gunicorn EchoSpace.wsgi:application`. Put your deployed URL in docs if needed.

## Repo layout

- `EchoSpace/` — settings, urls, wsgi
- `main/`, `accounts/`, `chat/`, `ai_chat/`, `dashboard/` — apps
- `templates/`, `static/`
- `requirements.txt`, `render.yaml`, `.env.example`
