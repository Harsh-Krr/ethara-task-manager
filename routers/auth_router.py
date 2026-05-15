from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user
from auth import hash_password, verify_password, create_access_token
import models

router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="templates")


# ── Pages ──────────────────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user=Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("auth/login.html", {"request": request, "error": None})


@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request, user=Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("auth/signup.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == email.lower().strip()).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Invalid email or password"},
            status_code=400,
        )
    token = create_access_token(user.id, user.role.value)
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie("access_token", token, httponly=True, max_age=60 * 60 * 24 * 7, samesite="lax")
    return response


@router.post("/signup", response_class=HTMLResponse)
async def signup_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("member"),
    db: Session = Depends(get_db),
):
    email = email.lower().strip()
    if db.query(models.User).filter(models.User.email == email).first():
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": "Email already registered"},
            status_code=400,
        )
    if len(password) < 6:
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": "Password must be at least 6 characters"},
            status_code=400,
        )
    if len(name.strip()) < 2:
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": "Name must be at least 2 characters"},
            status_code=400,
        )
    role_val = models.UserRole.admin if role == "admin" else models.UserRole.member
    user = models.User(name=name.strip(), email=email, password_hash=hash_password(password), role=role_val)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.role.value)
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie("access_token", token, httponly=True, max_age=60 * 60 * 24 * 7, samesite="lax")
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


# ── REST API ───────────────────────────────────────────────────────────────

@router.get("/api/auth/me")
async def me(user=Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


@router.get("/api/users")
async def list_users(user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Members can only see themselves — not other users' data
    if user.role == models.UserRole.member:
        return [{"id": user.id, "name": user.name, "email": user.email, "role": user.role}]
    # Admins see everyone
    users = db.query(models.User).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]
