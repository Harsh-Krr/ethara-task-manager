from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user, require_admin
import models

router = APIRouter(prefix="/users", tags=["users"])
templates = Jinja2Templates(directory="templates")

@router.get("", response_class=HTMLResponse)
async def users_list(request: Request, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    if user.role != models.UserRole.admin:
        # For members, they can't access user management, redirect them
        return RedirectResponse(url="/dashboard", status_code=302)
    
    users = db.query(models.User).all()
    return templates.TemplateResponse("users/list.html", {
        "request": request, "user": user, "users": users, "active": "users"
    })

@router.post("/{user_id}/role")
async def change_user_role(
    user_id: int, 
    role: str = Form(...), 
    user=Depends(require_admin), 
    db: Session = Depends(get_db)
):
    if user.id == user_id:
        # Cannot change own role
        return RedirectResponse(url="/users?error=Cannot+change+own+role", status_code=302)
    
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if target_user:
        target_user.role = models.UserRole.admin if role == "admin" else models.UserRole.member
        db.commit()
    return RedirectResponse(url="/users", status_code=302)

@router.post("/{user_id}/delete")
async def delete_user(
    user_id: int, 
    user=Depends(require_admin), 
    db: Session = Depends(get_db)
):
    if user.id == user_id:
        # Cannot delete self
        return RedirectResponse(url="/users?error=Cannot+delete+yourself", status_code=302)
        
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if target_user:
        db.delete(target_user)
        db.commit()
    return RedirectResponse(url="/users", status_code=302)
