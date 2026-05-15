# Ethara Task Manager

A full-stack collaborative task management platform built for **Ethara.AI** using **FastAPI**, **PostgreSQL**, and modern glassmorphism design.

🔗 **Live Website**: *https://web-production-0e627.up.railway.app/*  
📦 **GitHub**: *https://github.com/Harsh-Krr/ethara-task-manager*

🎥 **Demo Video**: *https://drive.google.com/file/d/1a4TsiZCdjCHi4pmBEUEpxrsV-xnaWwPH/view?usp=drive_link*

---

## ✨ Features

- 🔐 **Auth** — Signup/Login with JWT (HTTP-only cookies, 7-day session)
- 👥 **Two-Interface Portal** — Separate Admin & Member UI with strict Role-Based Access Control (RBAC)
- 📁 **Project Management** — Create projects, manage team membership
- ✅ **Task Tracking** — Assign tasks, set priority & due dates, track status
- 📊 **Dashboard** — Live stats, overdue alerts, project progress bars
- 🎨 **Modern UI** — Center-focused scrollable auth pages, animated doodles, and a dark glassmorphism theme
- 🔌 **REST API** — Full JSON API at `/api/...` (Swagger docs at `/api/docs`)
- 🛡️ **Admin Portal** — Manage users, change roles, remove accounts

---

## 🔒 Role Matrix

| Action | Admin | Member |
|--------|-------|--------|
| View ALL projects | ✅ | ❌ (own projects only) |
| Create / Edit / Delete projects | ✅ | ❌ |
| Manage team members | ✅ | ❌ |
| Create / Edit / Delete tasks | ✅ | ❌ |
| Update task status | ✅ | ✅ (own projects only) |
| View Team Directory (`/users`) | ✅ | ❌ |
| Promote / Demote users | ✅ | ❌ |
| Delete users | ✅ | ❌ |

---

## 🛠️ Tech Stack

| Layer       | Technology                         |
|-------------|------------------------------------|
| Backend     | FastAPI + Uvicorn                  |
| Database    | PostgreSQL (Railway) / SQLite (dev)|
| ORM         | SQLAlchemy 2.0                     |
| Auth        | JWT (python-jose) + bcrypt         |
| Frontend    | Jinja2 SSR + Vanilla CSS/JS        |
| Deployment  | Railway                            |

---

## 💻 Local Development

### 1. Clone & install
```bash
git clone https://github.com/Harsh-Krr/ethara-task-manager.git
cd ethara-task-manager

python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run
```bash
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000  
> Uses **SQLite** locally (auto-created as `taskmanager.db`). No setup needed.

---

## 🚀 Deployment on Railway

1. Push repo to GitHub.
2. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub**.
3. Add **PostgreSQL plugin** (Railway will provide a `DATABASE_URL` for you).
4. Go to your App Service → Variables and add:
   - `DATABASE_URL` (paste the URL from the PostgreSQL service).
   - `SECRET_KEY` (a long random string like `1a2b3c4d5e...`).
5. Deploy — your app goes live! 🚀

---

## 📖 API Reference

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/signup` | Register new user | Public |
| POST | `/login` | Login (sets cookie) | Public |
| POST | `/logout` | Logout | Auth |
| GET | `/api/auth/me` | Current user info | Auth |
| GET | `/api/users` | List users (self only for members) | Auth |
| GET | `/api/dashboard` | Dashboard stats JSON | Auth |
| GET | `/api/projects` | Projects list JSON | Auth |
| POST | `/projects/create` | Create project | Admin |
| POST | `/projects/{id}/edit` | Edit project | Admin |
| POST | `/projects/{id}/delete` | Delete project | Admin |
| POST | `/projects/{id}/members/add` | Add member | Admin |
| POST | `/projects/{id}/members/{uid}/remove` | Remove member | Admin |
| GET | `/tasks` | All tasks page | Auth |
| POST | `/tasks/create` | Create task | Admin |
| POST | `/tasks/{id}/edit` | Edit task | Admin |
| POST | `/tasks/{id}/delete` | Delete task | Admin |
| PATCH | `/tasks/{id}/status` | Update status (AJAX) | Auth |
| GET | `/users` | Team Directory | Admin |
| POST | `/users/{id}/role` | Change user role | Admin |
| POST | `/users/{id}/delete` | Delete user | Admin |

Full interactive docs available at: `/api/docs`
