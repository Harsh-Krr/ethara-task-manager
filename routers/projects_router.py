from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
import models

router = APIRouter(prefix="/projects", tags=["projects"])
templates = Jinja2Templates(directory="templates")


def user_can_access_project(user: models.User, project: models.Project) -> bool:
    if user.role == models.UserRole.admin:
        return True
    return any(m.user_id == user.id for m in project.members)


# ── Pages ──────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def projects_list(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    if user.role == models.UserRole.admin:
        projects = db.query(models.Project).order_by(models.Project.created_at.desc()).all()
    else:
        ids = [m.project_id for m in user.memberships]
        projects = db.query(models.Project).filter(models.Project.id.in_(ids)).all()
    return templates.TemplateResponse("projects/list.html", {"request": request, "user": user, "projects": projects})


@router.get("/create", response_class=HTMLResponse)
async def create_project_page(request: Request, user=Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    if user.role != models.UserRole.admin:
        return RedirectResponse(url="/projects", status_code=302)
    return templates.TemplateResponse("projects/create.html", {"request": request, "user": user, "project": None, "error": None})


@router.post("/create", response_class=HTMLResponse)
async def create_project_submit(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not user or user.role != models.UserRole.admin:
        return RedirectResponse(url="/login", status_code=302)
    project = models.Project(name=name.strip(), description=description.strip() or None, created_by_id=user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    # Add creator as a member
    member = models.ProjectMember(project_id=project.id, user_id=user.id)
    db.add(member)
    db.commit()
    return RedirectResponse(url=f"/projects/{project.id}", status_code=302)


@router.get("/{project_id}", response_class=HTMLResponse)
async def project_detail(request: Request, project_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project or not user_can_access_project(user, project):
        return RedirectResponse(url="/projects", status_code=302)
    all_users = db.query(models.User).all()
    member_ids = {m.user_id for m in project.members}
    non_members = [u for u in all_users if u.id not in member_ids]
    from datetime import date
    today = date.today()
    return templates.TemplateResponse(
        "projects/detail.html",
        {"request": request, "user": user, "project": project, "non_members": non_members, "today": today},
    )


@router.get("/{project_id}/edit", response_class=HTMLResponse)
async def edit_project_page(request: Request, project_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user or user.role != models.UserRole.admin:
        return RedirectResponse(url="/login", status_code=302)
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        return RedirectResponse(url="/projects", status_code=302)
    return templates.TemplateResponse("projects/create.html", {"request": request, "user": user, "project": project, "error": None})


@router.post("/{project_id}/edit", response_class=HTMLResponse)
async def edit_project_submit(
    request: Request, project_id: int,
    name: str = Form(...), description: str = Form(""),
    user=Depends(get_current_user), db: Session = Depends(get_db),
):
    if not user or user.role != models.UserRole.admin:
        return RedirectResponse(url="/login", status_code=302)
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project:
        project.name = name.strip()
        project.description = description.strip() or None
        db.commit()
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


@router.post("/{project_id}/delete")
async def delete_project(project_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user or user.role != models.UserRole.admin:
        return RedirectResponse(url="/login", status_code=302)
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project:
        db.delete(project)
        db.commit()
    return RedirectResponse(url="/projects", status_code=302)


@router.post("/{project_id}/members/add")
async def add_member(
    project_id: int, user_id: int = Form(...),
    user=Depends(get_current_user), db: Session = Depends(get_db),
):
    if not user or user.role != models.UserRole.admin:
        raise HTTPException(status_code=403)
    exists = db.query(models.ProjectMember).filter_by(project_id=project_id, user_id=user_id).first()
    if not exists:
        db.add(models.ProjectMember(project_id=project_id, user_id=user_id))
        db.commit()
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


@router.post("/{project_id}/members/{uid}/remove")
async def remove_member(
    project_id: int, uid: int,
    user=Depends(get_current_user), db: Session = Depends(get_db),
):
    if not user or user.role != models.UserRole.admin:
        raise HTTPException(status_code=403)
    m = db.query(models.ProjectMember).filter_by(project_id=project_id, user_id=uid).first()
    if m:
        db.delete(m)
        db.commit()
    return RedirectResponse(url=f"/projects/{project_id}", status_code=302)


# ── REST API ───────────────────────────────────────────────────────────────

@router.get("/api/projects")
async def api_projects(user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401)
    if user.role == models.UserRole.admin:
        projects = db.query(models.Project).all()
    else:
        ids = [m.project_id for m in user.memberships]
        projects = db.query(models.Project).filter(models.Project.id.in_(ids)).all()
    return [{"id": p.id, "name": p.name, "description": p.description} for p in projects]
