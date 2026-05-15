from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from dependencies import get_current_user
import models

router = APIRouter(prefix="/tasks", tags=["tasks"])
templates = Jinja2Templates(directory="templates")


def get_visible_tasks(user: models.User, db: Session):
    if user.role == models.UserRole.admin:
        return db.query(models.Task).order_by(models.Task.created_at.desc()).all()
    ids = [m.project_id for m in user.memberships]
    return db.query(models.Task).filter(models.Task.project_id.in_(ids)).order_by(models.Task.created_at.desc()).all()


# ── Pages ──────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def tasks_list(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    tasks = get_visible_tasks(user, db)
    today = date.today()
    return templates.TemplateResponse("tasks/list.html", {"request": request, "user": user, "tasks": tasks, "today": today})


@router.get("/create", response_class=HTMLResponse)
async def create_task_page(
    request: Request, project_id: int = None,
    user=Depends(get_current_user), db: Session = Depends(get_db),
):
    if not user or user.role != models.UserRole.admin:
        return RedirectResponse(url="/tasks", status_code=302)
    if user.role == models.UserRole.admin:
        projects = db.query(models.Project).all()
    else:
        ids = [m.project_id for m in user.memberships]
        projects = db.query(models.Project).filter(models.Project.id.in_(ids)).all()
    all_users = db.query(models.User).all()
    return templates.TemplateResponse(
        "tasks/create.html",
        {"request": request, "user": user, "projects": projects,
         "all_users": all_users, "task": None, "selected_project_id": project_id, "error": None},
    )


@router.post("/create", response_class=HTMLResponse)
async def create_task_submit(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    project_id: int = Form(...),
    assigned_to_id: str = Form(""),
    priority: str = Form("medium"),
    due_date: str = Form(""),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user or user.role != models.UserRole.admin:
        return RedirectResponse(url="/login", status_code=302)
    try:
        due = date.fromisoformat(due_date) if due_date else None
    except ValueError:
        due = None
    assigned = int(assigned_to_id) if assigned_to_id else None
    task = models.Task(
        title=title.strip(),
        description=description.strip() or None,
        project_id=project_id,
        assigned_to_id=assigned,
        priority=models.TaskPriority(priority),
        due_date=due,
        created_by_id=user.id,
    )
    db.add(task)
    db.commit()
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


@router.get("/{task_id}/edit", response_class=HTMLResponse)
async def edit_task_page(request: Request, task_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user or user.role != models.UserRole.admin:
        return RedirectResponse(url="/tasks", status_code=302)
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        return RedirectResponse(url="/tasks", status_code=302)
    projects = db.query(models.Project).all()
    all_users = db.query(models.User).all()
    return templates.TemplateResponse(
        "tasks/create.html",
        {"request": request, "user": user, "projects": projects,
         "all_users": all_users, "task": task, "selected_project_id": task.project_id, "error": None},
    )


@router.post("/{task_id}/edit", response_class=HTMLResponse)
async def edit_task_submit(
    request: Request, task_id: int,
    title: str = Form(...), description: str = Form(""),
    project_id: int = Form(...), assigned_to_id: str = Form(""),
    priority: str = Form("medium"), due_date: str = Form(""),
    status: str = Form("todo"),
    user=Depends(get_current_user), db: Session = Depends(get_db),
):
    if not user or user.role != models.UserRole.admin:
        return RedirectResponse(url="/login", status_code=302)
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task:
        task.title = title.strip()
        task.description = description.strip() or None
        task.project_id = project_id
        task.assigned_to_id = int(assigned_to_id) if assigned_to_id else None
        task.priority = models.TaskPriority(priority)
        task.status = models.TaskStatus(status)
        try:
            task.due_date = date.fromisoformat(due_date) if due_date else None
        except ValueError:
            task.due_date = None
        db.commit()
    return RedirectResponse(url=f"/projects/{task.project_id}", status_code=302)


@router.post("/{task_id}/delete")
async def delete_task(task_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user or user.role != models.UserRole.admin:
        return RedirectResponse(url="/login", status_code=302)
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    pid = task.project_id if task else None
    if task:
        db.delete(task)
        db.commit()
    return RedirectResponse(url=f"/projects/{pid}" if pid else "/tasks", status_code=302)


# ── REST API (AJAX) ─────────────────────────────────────────────────────────

@router.patch("/{task_id}/status")
async def update_status(
    task_id: int, request: Request,
    user=Depends(get_current_user), db: Session = Depends(get_db),
):
    if not user:
        raise HTTPException(status_code=401)
    body = await request.json()
    new_status = body.get("status")
    if new_status not in [s.value for s in models.TaskStatus]:
        raise HTTPException(status_code=400, detail="Invalid status")
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404)
    # Members can only update tasks in their projects
    if user.role == models.UserRole.member:
        ids = [m.project_id for m in user.memberships]
        if task.project_id not in ids:
            raise HTTPException(status_code=403)
    task.status = models.TaskStatus(new_status)
    db.commit()
    return {"id": task.id, "status": task.status.value}
