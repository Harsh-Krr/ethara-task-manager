from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from database import engine, Base
import models  # noqa: F401 – needed so models register with Base

from routers import auth_router, projects_router, tasks_router, dashboard_router, users_router

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Team Task Manager", version="1.0.0", docs_url="/api/docs")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router.router)
app.include_router(dashboard_router.router)
app.include_router(projects_router.router)
app.include_router(tasks_router.router)
app.include_router(users_router.router)


@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard", status_code=302)
