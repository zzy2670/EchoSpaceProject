# EchoSpace

Anonymous group chat + Native AI “Tree Hole” (emotional support chat). Django backend, Bootstrap 5 SPA frontend, SQLite locally / Postgres in prod.

## What’s in it

- Home, register / login / guest (via offcanvas drawer).
- Lobby: list active rooms, search filtering, create (if not guest), join.
- Room: group chat via polling, message withdrawal, dynamic UI updates.
- AI Tree Hole: native chat with Gemini 2.5 Flash API. Persistent history stored in DB.
- Dashboard for staff (metrics, room list, message logs, AI conversations).

## Run locally

Clone, venv, install deps:

```bash
git clone <your-repo-url>
cd EchoSpaceProject
python -m venv .venv
.venv\Scripts\activate   # Windows; on Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt

Copy env and edit:
cp .env.example .env

In .env, set the following:
SECRET_KEY=change-me-to-a-secure-random-string
DEBUG=True
AI_PROVIDER=gemini
GEMINI_API_KEY=<your-google-gemini-api-key>

Migrate and run:
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

Optional: python manage.py createsuperuser for admin/dashboard access. Then open http://127.0.0.1:8000/
python manage.py test
Covers main, accounts, chat (lobby/rooms/API), ai_chat, and dashboard components.