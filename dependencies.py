from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth import decode_token
import models


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    return db.query(models.User).filter(models.User.id == int(user_id)).first()


def require_login(request: Request, db: Session = Depends(get_db)) -> models.User:
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def require_admin(user: models.User = Depends(require_login)) -> models.User:
    if user.role != models.UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
