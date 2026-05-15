from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from dependencies import get_current_user
import models

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="templates")


def get_stats(user: models.User, db: Session) -> dict:
    today = date.today()

    if user.role == models.UserRole.admin:
        all_tasks = db.query(models.Task).all()
        projects = db.query(models.Project).all()
    else:
        member_project_ids = [m.project_id for m in user.memberships]
        all_tasks = db.query(models.Task).filter(models.Task.project_id.in_(member_project_ids)).all()
        projects = db.query(models.Project).filter(models.Project.id.in_(member_project_ids)).all()

    todo = sum(1 for t in all_tasks if t.status == models.TaskStatus.todo)
    in_progress = sum(1 for t in all_tasks if t.status == models.TaskStatus.in_progress)
    done = sum(1 for t in all_tasks if t.status == models.TaskStatus.done)
    overdue = sum(
        1 for t in all_tasks
        if t.due_date and t.due_date < today and t.status != models.TaskStatus.done
    )

    recent_tasks = sorted(all_tasks, key=lambda t: t.created_at, reverse=True)[:8]

    return {
        "total_tasks": len(all_tasks),
        "todo": todo,
        "in_progress": in_progress,
        "done": done,
        "overdue": overdue,
        "total_projects": len(projects),
        "projects": projects,
        "recent_tasks": recent_tasks,
        "today": today,
    }


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    stats = get_stats(user, db)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, **stats})


@router.get("/api/dashboard")
async def api_dashboard(user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=401)
    stats = get_stats(user, db)
    return {k: v for k, v in stats.items() if k not in ("projects", "recent_tasks")}
