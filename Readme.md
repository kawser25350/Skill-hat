# 🧢 Skill-Hat

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-4.0-%230092BF)](https://www.djangoproject.com/)

> A marketplace that connects semi-skilled workers in Bangladesh with customers for short-term and small-scale services — powered by verification, escrow payments, and simple, human-centered design.

---

## 📋 Table of Contents
- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Architecture & Repo Structure](#-architecture--repo-structure)
- [Tech Stack](#-tech-stack)
- [Quick Start (Local Development)](#-quick-start-local-development)
- [Configuration](#-configuration)
- [Data & Migrations](#-data--migrations)
- [Deployment](#-deployment)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [Security Notes](#-security-notes)
- [Roadmap](#-roadmap)
- [License & Contact](#-license--contact)

---

## 🔖 Project Overview
Skill-Hat enables customers to find and hire semi-skilled workers (electricians, painters, tutors, drivers, cleaners, etc.) for short-term jobs. The platform emphasizes:
- Verification (NID, phone, police clearance) to build trust
- Escrow-based payments to protect both parties
- Ratings and feedback to surface reliable workers
- Simple booking and payment flows focused on mobile-first users

This repository contains a Django backend, frontend templates, static assets, and an API app to support mobile or single-page frontends.

---

## ✨ Key Features
- Worker profiles with skills, location, and verification documents
- Customer booking flow with escrow deposit and completion confirmation
- Cancellation and penalty rules
- Ratings, reviews, and trust-score influencing search ranking
- Admin dashboard for managing users, transactions, and disputes
- REST API endpoints (basic serializers and views under `api/`) for integrations

---

## 🏗️ Architecture & Repo Structure
Relevant top-level folders and files (abridged):

- `skill_hat/` — Django project settings & wsgi/asgi
- `core/` — main app (models, payment logic, signals, admin)
- `api/` — DRF serializers & views for programmatic access
- `static/` — CSS, JS, images
- `templates/` — Django templates (components, layouts, pages)
- `db.sqlite3` — Lightweight local DB (for quick start)
- `requirements.txt`, `Procfile`, `runtime.txt` — deployment and dependency metadata

---

## 🛠️ Tech Stack
- Python 3.12+
- Django (latest stable)
- Django REST Framework (for `api/`)
- MySQL (recommended for production) or SQLite for local development
- Bootstrap 5, vanilla JS for the frontend

---

## 🚀 Quick Start (Local Development)
These steps will get the app running locally using SQLite.

1. Clone the repository

```bash
git clone https://github.com/kawser25350/Skill-hat.git
cd Skill-hat
```

2. Create & activate a virtual environment

```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
# macOS / Linux
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Copy the example env and set secrets

```bash
cp .env.example .env
# edit .env and set at minimum: SECRET_KEY, DEBUG, DATABASE_URL (optional)
```

5. Run migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

6. (Optional) Collect static files

```bash
python manage.py collectstatic --noinput
```

7. Start the development server

```bash
python manage.py runserver
```
Open http://127.0.0.1:8000/ in your browser.

> Tip: `db.sqlite3` is included for quick setups; for production, configure MySQL as shown below.

---

## ⚙️ Configuration
Configuration values live in `skill_hat/settings.py`. Use environment variables for production-sensitive settings.

Important environment variables:
- `SECRET_KEY` — Django secret key
- `DEBUG` — `True` for dev, `False` for prod
- `DATABASE_URL` or explicit DB settings for MySQL
- `ALLOWED_HOSTS` — domain(s) to allow in production
- Email/SMS provider credentials (for verification workflows)

Example MySQL snippet for production (set these values in env or `settings.py`):

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'skill_hat_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

---

## 🔁 Data & Migrations
- Make schema changes with `makemigrations` and `migrate`:

```bash
python manage.py makemigrations
python manage.py migrate
```

- To seed demo data, add fixtures or create via admin UI.

---

## 📦 Deployment
This project includes a `Procfile` and `runtime.txt` (suitable for platforms like Render or Heroku). A minimal production workflow:

1. Ensure `DEBUG=False` and `SECRET_KEY` is set to a secure value
2. Configure production DB (MySQL)
3. Run migrations: `python manage.py migrate`
4. Collect static files: `python manage.py collectstatic --noinput`
5. Use Gunicorn or platform default to serve the app (example):

```bash
gunicorn skill_hat.wsgi:application --bind 0.0.0.0:$PORT
```

Docker & CI: Add a `Dockerfile` and `docker-compose.yml` when you want reproducible build/runtime environments.

---

## ✅ Testing
- Run unit tests with:

```bash
pytest  # if pytest is configured
# or
python manage.py test
```

- Add tests for new API endpoints, payment logic, and model behaviors.

---

## 🧰 Contributing
Contributions are welcome! Please follow these steps:

1. Fork the repo and create a feature branch: `git checkout -b feat/your-change`
2. Write tests for your change
3. Run linters/formatters (Black, isort) and ensure tests pass
4. Create a Pull Request describing the change and linking any relevant issues

Code style: follow PEP8 and prefer clear, minimal commits. Use feature branches and small PRs for review.

---

## 🔒 Security Notes
- Never commit `.env` or secrets to git. Use platform secrets for deployment.
- The verification pipeline includes handling of sensitive documents — ensure uploaded files are scanned/validated and stored securely.
- Report security bugs via email: `mkshuvo25350@gmail.com`.

---

## 🛣️ Roadmap
Planned enhancements:
- Real-time chat with moderation
- AI-powered worker recommendations
- Payment gateway integrations (bKash, Nagad)
- Mobile-first improvements and PWA support

---

## 📄 License & Contact
- License: **MIT**. See `LICENSE` for full text.
- Maintainer / Contact: **Kawser Ahmmed** — `mkshuvo25350@gmail.com`

---

> If you'd like, I can: (1) add a short `ENV` example file, (2) add a `Dockerfile`/`docker-compose.yml`, or (3) generate a contributor PR template — tell me which to do next. ✅  



\`\`\`

### 2️⃣ Create & Activate Virtual Environment
\`\`\`bash
python -m venv venv
venv\\Scripts\\activate   # On Windows
source venv/bin/activate  # On Linux/Mac
\`\`\`

### 3️⃣ Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4️⃣ Configure MySQL Database
Open \`settings.py\` and set your credentials:
\`\`\`python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'skill_hat_db',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
\`\`\`

### 5️⃣ Apply Migrations
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

### 6️⃣ Create a Superuser
\`\`\`bash
python manage.py createsuperuser
\`\`\`

### 7️⃣ Run the Server
\`\`\`bash
python manage.py runserver
\`\`\`
Visit the app at **http://127.0.0.1:8000/**

---

## 🎨 UI Design
- Built with **HTML5**, **CSS3**, and **Bootstrap 5** for responsiveness.  
- Clean, minimal interface focused on usability and accessibility.  
- Ready for integration with custom Django templates.

---

## 🧮 Future Enhancements
- AI-based worker recommendation system.  
- Real-time chat with message moderation.  
- Mobile-first PWA (Progressive Web App) version.  
- Job completion image verification for escrow release.

---

## 👥 Contributors

| Name | Role |
|------|------|
| **Kawser Ahmmed** | Project Lead / Full-Stack Developer |
| **Marziya sultana** | developer  /  Frontent-Developer |
---

## 📄 License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute this project with proper attribution.

---

## 📬 Contact

For inquiries, suggestions, or collaborations:

**Email:** mkshuvo25350@gmail.com
**GitHub:** [kawser25350](https://github.com/kawser25350)

---

> **Skill-Hat — Empowering Bangladesh’s semi-skilled workforce with digital trust and opportunity.**

