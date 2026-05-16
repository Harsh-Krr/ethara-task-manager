# Ethara.AI Team Task Manager - Project Documentation

## 1. Executive Summary

The **Ethara.AI Team Task Manager** is a full-stack, production-ready web application designed to streamline team collaboration, project tracking, and task management. Built with a focus on high performance and a premium user experience, the application provides secure authentication, role-based access control (RBAC), and an intuitive, modern "Glassmorphism" interface.

This document serves as a comprehensive guide for reviewers and team members to understand the architecture, technology stack, design decisions, and implementation details of the project.

---

## 2. Technology Stack & Languages Used

The project was built using a modern, lightweight, yet powerful stack. Instead of relying on heavy frontend frameworks, the application utilizes Server-Side Rendering (SSR) combined with vanilla web technologies to maximize performance and maintain full control over the UI/UX.

### Backend & Core Logic
*   **Language:** Python 3.10+
*   **Framework:** FastAPI
    *   *Why?* Chosen for its asynchronous capabilities, extreme speed (comparable to NodeJS and Go), and automatic data validation using Pydantic.
*   **Templating Engine:** Jinja2 
    *   *Why?* Used for Server-Side Rendering to inject dynamic data directly into HTML, reducing initial browser load times and removing the need for a complex frontend build step.
*   **Authentication:** JWT (JSON Web Tokens) with `python-jose`, utilizing HTTP-only cookies for enhanced security against Cross-Site Scripting (XSS) attacks. Password hashing is handled securely via `bcrypt`.

### Frontend & UI/UX
*   **Structure:** HTML5 (Semantic and accessible markup).
*   **Styling:** Vanilla CSS3 
    *   *Why?* Tailored specifically for a custom "Glassmorphism" aesthetic, utilizing CSS variables, flexbox/grid layouts, backdrop filters, and smooth CSS animations. No external CSS libraries like Tailwind or Bootstrap were used, allowing for a completely bespoke, highly-optimized design.
*   **Interactivity:** Vanilla JavaScript (ES6+)
    *   *Why?* Handles asynchronous form submissions, dynamic status updates via the Fetch API, and lightweight DOM manipulation without the heavy bundle size overhead of React or Angular.

### Database & ORM
*   **ORM:** SQLAlchemy 
    *   *Why?* Handles database interactions, schema creation, and relationship mapping securely, automatically preventing SQL injection attacks.
*   **Local Database:** SQLite (Used for rapid local development, testing, and debugging).
*   **Production Database:** PostgreSQL (Robust, scalable relational database deployed via Railway).

### Deployment & DevOps
*   **Hosting platform:** Railway.app
*   **Build System:** Nixpacks (Automatically detects the Python environment and installs required dependencies without needing a manual Dockerfile).
*   **Version Control:** Git & GitHub.

---

## 3. Core Features & Functionality

### 3.1. Authentication & Security
Security is a foundational pillar of this application:
*   **Secure Registration & Login:** Users can create accounts and log in securely. Passwords are never stored in plaintext; they are salted and hashed using `bcrypt` before reaching the database.
*   **JWT Session Management:** Upon successful login, a JWT is generated and stored securely in an `HttpOnly` browser cookie. This prevents malicious JavaScript scripts from accessing the session token.
*   **Route Protection:** Every endpoint (except login/signup) is strictly protected by a dependency injection function (`get_current_user`) that verifies the JWT signature and expiration before allowing access to the page.

### 3.2. Role-Based Access Control (RBAC)
The application implements a strict two-tier user hierarchy to ensure data privacy and administrative control:
*   **Members:** Standard users. They can view projects they are assigned to, create tasks within those projects, and update the status of their specific tasks. They are completely sandboxed and cannot see other users' private data or projects.
*   **Admins:** Have elevated, full-platform access. They can create, edit, and delete projects, view all tasks globally, and access the dedicated **Admin Portal** (Team Directory) to manage users—including promoting members to admins, demoting them, or securely removing accounts from the system.

### 3.3. Project & Task Management (CRUD Operations)
*   **Projects:** Groupings of related tasks. Projects have titles, descriptions, and a visual progress bar that calculates dynamically based on the completion status of associated tasks (e.g., 2 out of 4 tasks done = 50% progress).
*   **Tasks:** Individual actionable items. Tasks include titles, descriptions, due dates, priority levels (Low, Medium, High), status (Todo, In Progress, Done), and are assigned directly to specific team members.
*   **Dynamic AJAX Updates:** Task statuses can be updated directly from the dashboard or project view without reloading the entire page, utilizing asynchronous JavaScript `fetch` requests for a seamless, SPA-like experience.

### 3.4. Premium "Glassmorphism" UI/UX Design
The user interface was meticulously designed from scratch to provide a "WOW" factor and premium feel:
*   **Aesthetic:** The design utilizes a deep, dark theme with vibrant purple and blue glowing gradients.
*   **Glass Panels:** Cards, tables, and sidebars use `backdrop-filter: blur(16px)` combined with semi-transparent white backgrounds (`rgba(255,255,255,0.04)`) to create a frosted glass effect.
*   **Custom SVG Doodles:** The authentication pages (Login/Signup) feature a unique centered layout with animated, productivity-themed SVG doodles (floating dots, dashed arcs, and twinkling sparkles) that act as an immersive background.
*   **Micro-interactions:** Buttons, inputs, and project cards feature subtle hover states, glow effects, and transition animations (`0.2s ease`) to make the interface feel highly responsive and alive.

---

## 4. Architectural Design & Implementation Details

### 4.1. Server-Side Rendering (SSR) Workflow
Unlike a Single Page Application (SPA) where the browser must download a heavy JavaScript bundle to render the page, this application uses highly optimized SSR:
1.  The browser requests a page URL (e.g., `/dashboard`).
2.  FastAPI securely queries the database via SQLAlchemy for the necessary data (the user's specific projects and tasks).
3.  The data is securely passed to a Jinja2 template (`dashboard.html`).
4.  Jinja2 constructs the final HTML document on the server and sends it to the browser.
5.  **Benefit:** Faster initial load times, better Search Engine Optimization (SEO), and significantly less CPU/memory strain on the client's device.

### 4.2. Database Schema Overview
The relational database is carefully structured around three primary tables to ensure data normalization:

1.  **Users Table:**
    *   `id` (Primary Key)
    *   `name`, `email`, `hashed_password`
    *   `role` (Enum: Admin / Member)
    *   `created_at`
2.  **Projects Table:**
    *   `id` (Primary Key)
    *   `title`, `description`, `created_at`
    *   `owner_id` (Foreign Key -> Users.id)
3.  **Tasks Table:**
    *   `id` (Primary Key)
    *   `title`, `description`, `status`, `priority`, `due_date`
    *   `project_id` (Foreign Key -> Projects.id)
    *   `assignee_id` (Foreign Key -> Users.id)

*Relationships:* A Project can contain many Tasks. A User can own many Projects and be assigned to many Tasks.

### 4.3. API Routing Structure
The backend logic is strictly modularized using FastAPI's `APIRouter` to keep the codebase clean, organized, and highly maintainable for future developers:
*   `routers/auth_router.py`: Handles `/login`, `/signup`, `/logout`, and JWT generation/validation.
*   `routers/dashboard_router.py`: Aggregates data across all projects and tasks to render the main overview screen.
*   `routers/projects_router.py`: Handles creation, viewing, and deletion of projects.
*   `routers/tasks_router.py`: Manages adding tasks to projects and updating task states.
*   `routers/users_router.py`: Contains the Admin Portal logic for viewing and modifying the team directory and user roles.

---

## 5. Development Challenges & Solutions

During development, several complex technical challenges were addressed to ensure enterprise-grade stability:

1.  **Bcrypt Python 3.14+ Compatibility:** Newer versions of Python have strict compatibility issues with older `bcrypt` hashing methods. This was actively solved by implementing a custom hashing utility wrapper, ensuring cross-platform compatibility across local Windows environments and the Linux-based Railway production servers.
2.  **Date Parsing & HTML5:** Different browsers send HTML5 `<input type="date">` data in slightly varying formats. A robust `try/except` wrapper was implemented using `date.fromisoformat` to safely parse dates, guaranteeing the application never crashes from user-malformed date inputs.
3.  **Strict Data Privacy (RBAC):** To ensure members absolutely cannot see other users' data or projects, SQLAlchemy queries were heavily scoped. For example, instead of querying `Session.query(Task).all()`, the application filters dynamically at the ORM level: `Session.query(Task).filter(Task.assignee_id == current_user.id)`.

---

## 6. How to Run and Test Locally

For reviewers wishing to test the codebase on their local machines:

1.  **Clone the repository:** 
    `git clone https://github.com/Harsh-Krr/ethara-task-manager.git`
2.  **Create a virtual environment:** 
    `python -m venv venv`
3.  **Activate the environment:**
    *   Windows: `.\venv\Scripts\activate`
    *   Mac/Linux: `source venv/bin/activate`
4.  **Install all required dependencies:** 
    `pip install -r requirements.txt`
5.  **Run the local development server:** 
    `uvicorn main:app --reload`
6.  **Access the application:** Open any modern web browser and navigate to `http://localhost:8000`.

*Note: The local version automatically utilizes a lightweight SQLite database (`taskmanager.db`), requiring zero manual database configuration to get started.*

---

## 7. Future Enhancements & Scalability

While the application is fully functional and production-ready today, the modular architecture allows for easy integration of future features:
*   **WebSockets:** Implementing real-time updates so team members can see task status changes instantly on their screen without needing to refresh the page.
*   **Email Notifications:** Integrating an SMTP service (like SendGrid or AWS SES) to automatically alert users via email when a new high-priority task is assigned to them.
*   **Drag-and-Drop Kanban Board:** Enhancing the current UI to allow users to drag tasks between "Todo", "In Progress", and "Done" columns natively, providing an even more tactile user experience.

---
*Documentation officially prepared for Ethara.AI Project Review.*
