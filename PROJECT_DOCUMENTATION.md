# Ethara.AI Team Task Manager - Comprehensive Project Blueprint & Documentation

## 1. Executive Summary

The **Ethara.AI Team Task Manager** is a full-stack, production-ready web application designed to streamline team collaboration, project tracking, and task management. Built with a focus on high performance and a premium user experience, the application provides secure authentication, strict role-based access control (RBAC), and an intuitive, modern "Glassmorphism" interface.

This document serves as an exhaustive blueprint. Whether you are a reviewer auditing the architecture, or a developer looking for a step-by-step roadmap on what you need to learn to build a project exactly like this from scratch, every major and minor detail is documented here.

---

## 2. Prerequisites & Learning Blueprint

To create this project from scratch, a developer needs a solid understanding of several core concepts across the frontend, backend, and database layers. Here is the exact learning roadmap:

### 2.1. Backend Prerequisites (Python)
*   **Core Python:** Classes, functions, decorators, and asynchronous programming (`async`/`await`).
*   **FastAPI Framework:** 
    *   Understanding how to create API endpoints (`@app.get`, `@app.post`).
    *   Handling form data and query parameters.
    *   Dependency Injection (e.g., using `Depends()` to extract the current user).
*   **Authentication Fundamentals:** 
    *   Understanding how JWTs (JSON Web Tokens) work.
    *   Password hashing concepts using `bcrypt`.
    *   Understanding HTTP-only cookies to prevent XSS attacks.

### 2.2. Database Prerequisites (SQL & ORM)
*   **Relational Databases:** Basic understanding of tables, rows, Primary Keys, and Foreign Keys (One-to-Many relationships).
*   **SQLAlchemy ORM:** 
    *   How to define models (classes mapping to database tables).
    *   Executing CRUD operations (Create, Read, Update, Delete) using SQLAlchemy sessions.
    *   Query filtering (e.g., fetching only tasks belonging to a specific user).

### 2.3. Frontend Prerequisites (UI/UX)
*   **HTML5:** Semantic structure, form handling, and accessibility.
*   **CSS3 (Advanced):**
    *   Flexbox and CSS Grid for layout management.
    *   CSS Variables (`--primary-color`) for theming.
    *   Modern UI techniques like `backdrop-filter: blur()` for glassmorphism.
    *   Keyframe animations and transitions.
*   **JavaScript (ES6):**
    *   DOM manipulation (selecting elements, adding event listeners).
    *   The Fetch API for making asynchronous AJAX calls (updating task statuses without reloading the page).
*   **Jinja2 Templating:** Using loops (`{% for task in tasks %}`) and conditionals (`{% if user.role == 'admin' %}`) to render dynamic HTML on the server.

---

## 3. Detailed Directory & File Structure

Understanding the file structure is critical to grasping how the application is separated into logical, maintainable components (Separation of Concerns).

```text
ethara-task-manager/
│
├── main.py                 # The entry point of the app. Initializes FastAPI, sets up static/template folders, and includes all routers.
├── database.py             # Handles the SQLAlchemy engine, session maker, and database URL configurations.
├── models.py               # Defines the database schema (User, Project, Task classes).
├── auth.py                 # Core security logic: Password hashing, JWT creation, and the get_current_user dependency.
├── dependencies.py         # Reusable dependencies (like getting a database session).
│
├── routers/                # Modularized route handlers (Controllers)
│   ├── auth_router.py      # Handles /login, /signup, and /logout.
│   ├── dashboard_router.py # Aggregates user stats and renders the main dashboard.
│   ├── projects_router.py  # Handles creating, viewing, and deleting projects.
│   ├── tasks_router.py     # Handles creating tasks and updating their statuses via AJAX.
│   └── users_router.py     # Admin panel logic (viewing directory, deleting users).
│
├── static/                 # Static assets served directly to the browser
│   ├── css/
│   │   ├── style.css       # Global styling, components, and layout.
│   │   └── auth-doodle.css # Specific animations and SVG layouts for the auth pages.
│   └── js/
│       └── app.js          # Client-side logic for task status dropdowns and dynamic UI updates.
│
├── templates/              # Jinja2 HTML Templates
│   ├── base.html           # The master layout (sidebar, header, content area).
│   ├── auth/               # Login and signup pages.
│   ├── dashboard.html      # The main overview screen.
│   ├── projects/           # Project creation and detail views.
│   ├── tasks/              # Task creation forms.
│   └── users/              # Admin team directory view.
│
├── requirements.txt        # Python dependencies required to run the project.
└── railway.toml            # Deployment configuration for Railway.app.
```

---

## 4. Database Schema Deep-Dive

The database is fully normalized to ensure data integrity. Here is the precise schema implemented in `models.py`:

### 4.1. Users Table
*   `id`: Integer, Primary Key, Auto-increment.
*   `name`: String, Not Null.
*   `email`: String, Unique, Indexed for fast logins.
*   `hashed_password`: String (Bcrypt hash).
*   `role`: String (Restricted to either 'admin' or 'member').
*   `created_at`: DateTime, defaults to the current UTC time.

### 4.2. Projects Table
*   `id`: Integer, Primary Key.
*   `title`: String, Not Null (e.g., "Q3 Marketing Campaign").
*   `description`: Text (Optional detailed context).
*   `owner_id`: Integer, Foreign Key linking to `Users.id` (Who created the project).
*   `created_at`: DateTime.

### 4.3. Tasks Table
*   `id`: Integer, Primary Key.
*   `title`: String, Not Null.
*   `description`: Text.
*   `status`: String (Enum: 'todo', 'in_progress', 'done'). Defaults to 'todo'.
*   `priority`: String (Enum: 'low', 'medium', 'high'). Defaults to 'medium'.
*   `due_date`: Date.
*   `project_id`: Integer, Foreign Key linking to `Projects.id`.
*   `assignee_id`: Integer, Foreign Key linking to `Users.id` (Who the task is assigned to).

---

## 5. Core Features & Functional Details

### 5.1. Authentication & Security (Deep Dive)
Security is a foundational pillar. It is implemented in `auth.py`:
1.  **Registration:** When a user submits the signup form, `bcrypt` generates a complex salt and hashes the password. The plaintext password is immediately discarded.
2.  **Login:** The user submits their email and password. The system fetches the user by email, uses `bcrypt.checkpw()` to verify the hash, and generates a JSON Web Token (JWT).
3.  **Session Management:** Instead of LocalStorage (which is vulnerable to XSS), the JWT is placed inside a cookie configured with `httponly=True` and `samesite='lax'`.
4.  **Route Protection:** The `get_current_user` function runs before every protected page load. It reads the cookie, decodes the JWT using the `SECRET_KEY`, and verifies the user exists in the database.

### 5.2. Strict Role-Based Access Control (RBAC)
Data privacy is enforced at the database query level:
*   **Members:** In `dashboard_router.py`, when a Member logs in, the query is specifically scoped: `db.query(Task).filter(Task.assignee_id == current_user.id).all()`. They physically cannot query data belonging to other members.
*   **Admins:** Admins bypass these filters (`db.query(Task).all()`) and have access to the Admin Portal (`/users`), where they can change roles or securely delete accounts.

### 5.3. Dynamic AJAX Task Updates
To make the application feel like a modern Single Page Application without the complexity of React, Vanilla JavaScript (`app.js`) is used to intercept task status changes:
1.  User clicks the dropdown on a task and selects "Done".
2.  JavaScript intercepts this event, prevents a page reload, and fires a `fetch()` POST request to `/tasks/{id}/status`.
3.  FastAPI updates the database.
4.  JavaScript visually updates the task badge color instantly.

### 5.4. Premium "Glassmorphism" UI/UX Design
The user interface was meticulously designed from scratch to provide a "WOW" factor:
*   **Aesthetic:** Deep, dark theme with vibrant purple (`#a78bfa`) and blue glowing gradients.
*   **Glass Panels:** Cards and sidebars use `backdrop-filter: blur(16px)` combined with a semi-transparent white background (`rgba(255,255,255,0.04)`) to create a frosted glass effect.
*   **Custom SVG Backgrounds:** The authentication pages feature animated, immersive SVG doodles (floating dots, dashed arcs, and twinkling sparkles) covering the entire screen.
*   **Micro-interactions:** Buttons and cards feature subtle hover states (translating up by 2px) and glow effects to make the interface feel highly responsive.

---

## 6. Development Challenges & Engineering Solutions

During development, several complex technical challenges were addressed:

1.  **Bcrypt Python 3.14+ Compatibility:** Newer versions of Python have strict compatibility issues with older `bcrypt` hashing methods. 
    *   *Solution:* Actively solved by implementing a custom hashing utility wrapper, ensuring cross-platform compatibility across local Windows environments and the Linux-based Railway production servers.
2.  **Date Parsing & HTML5 Variations:** Different browsers send HTML5 `<input type="date">` data in slightly varying formats. 
    *   *Solution:* A robust `try/except` wrapper was implemented using `date.fromisoformat` to safely parse dates, guaranteeing the application never crashes from user-malformed date inputs.
3.  **Form Validation with SSR:** Handling form errors gracefully without resetting user input.
    *   *Solution:* Utilized Jinja2 context variables to pass error messages and previous form data back to the template if validation fails, providing a smooth user experience.

---

## 7. How to Run and Test Locally

For developers or reviewers wishing to test the codebase on their local machines:

1.  **Clone the repository:** 
    `git clone https://github.com/Harsh-Krr/ethara-task-manager.git`
2.  **Navigate to the project:**
    `cd ethara-task-manager`
3.  **Create a virtual environment:** 
    `python -m venv venv`
4.  **Activate the environment:**
    *   Windows: `.\venv\Scripts\activate`
    *   Mac/Linux: `source venv/bin/activate`
5.  **Install all required dependencies:** 
    `pip install -r requirements.txt`
6.  **Run the local development server:** 
    `uvicorn main:app --reload`
7.  **Access the application:** Open any modern web browser and navigate to `http://localhost:8000`.

*Note: The local version automatically utilizes a lightweight SQLite database (`taskmanager.db`), requiring zero manual database configuration to get started.*

---

## 8. Future Enhancements & Scalability Roadmap

While the application is fully functional and production-ready today, the highly modular architecture allows for seamless integration of future features:
*   **WebSockets Integration:** Upgrading the current AJAX polling to real-time WebSockets so team members can see task status changes instantly on their screen without any delay.
*   **Email Notifications:** Integrating an SMTP service (like SendGrid or AWS SES) to automatically alert users via email when a new high-priority task is assigned to them, utilizing background tasks in FastAPI.
*   **Drag-and-Drop Kanban Board:** Enhancing the current UI to allow users to drag tasks between "Todo", "In Progress", and "Done" columns natively via the HTML5 Drag and Drop API.
*   **File Attachments:** Adding cloud storage integration (AWS S3) to allow users to attach documents and images directly to task descriptions.

---
*Comprehensive Documentation meticulously prepared for Ethara.AI Project Review.*
