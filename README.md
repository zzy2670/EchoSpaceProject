# EchoSpace

EchoSpace is an anonymous group chat and AI "Tree Hole" website. It provides instant emotional release, real resonance, and AI-guided support while minimizing social exposure.

## Features

- **Home / Product intro** — Landing page with feature overview
- **Register / Login / Guest mode** — Full auth with optional anonymous guest access
- **Lobby** — Browse rooms, see member counts, create rooms (registered users only)
- **Group Chat** — Join rooms, send/receive messages via AJAX polling
- **AI Tree Hole** — Chat with an AI for emotional support (mock or OpenAI)
- **Admin Dashboard** — Staff-only overview (user count, rooms, messages, AI sessions)

## Tech Stack

- **Backend:** Python 3.11, Django 4.2 LTS
- **Frontend:** HTML, CSS, Bootstrap 5, vanilla JavaScript + fetch
- **Database:** SQLite (local), PostgreSQL (production via `DATABASE_URL`)
- **Deployment:** Gunicorn, WhiteNoise, Render.com

## Local Development

### 1. Clone and setup

```bash
git clone <Add your GitHub URL here>
cd EchoSpaceProject
python -m venv .venv
.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate   # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment variables

Copy `.env.example` to `.env` and adjust:

```bash
cp .env.example .env
```

- `SECRET_KEY` — Use a random string for local dev
- `DEBUG=True` for local
- `AI_PROVIDER=mock` — No API key needed; set to `openai` and add `OPENAI_API_KEY` for real AI

### 4. Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 6. Run server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Running Tests

```bash
python manage.py test
```

Tests cover: main pages, accounts (register/login/guest), chat (rooms, messages, API), AI chat (mock provider), dashboard (staff-only).

## Deployment (Render.com)

1. Create a new Web Service and connect your repo.
2. Add a PostgreSQL database and link it (Render sets `DATABASE_URL`).
3. Set environment variables in Render dashboard (or use `render.yaml`).
4. Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
5. Start command: `gunicorn EchoSpace.wsgi:application`

Deployed URL: _Add your Render URL here_

## Project Structure

```
EchoSpaceProject/
├── manage.py
├── EchoSpace/          # Project settings, urls, wsgi
├── main/               # Home, health
├── accounts/           # User model, register, login, guest
├── chat/               # Lobby, rooms, messages, API
├── ai_chat/            # AI Tree Hole, conversations, API
├── dashboard/          # Staff dashboard
├── templates/
├── static/
└── requirements.txt, render.yaml, .env.example
```

## Team

- Member A: Backend, database, deployment
- _Add other members and roles here_

## License

Course project — use as specified by your course requirements.
