from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import ApiResponse, LoginRequest, LoginResponse, UserInfo
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=ApiResponse[LoginResponse])
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()
    if not user:
        return ApiResponse(code=401, message="用户名或密码错误", data=None)
    if user.role != body.role:
        return ApiResponse(code=403, message="角色不匹配", data=None)
    if not verify_password(body.password, user.password_hash):
        return ApiResponse(code=401, message="用户名或密码错误", data=None)

    user.last_login = datetime.utcnow()
    db.commit()

    token = create_access_token(user.username, {"role": user.role, "name": user.name})
    return ApiResponse(
        data=LoginResponse(
            token=token,
            user=UserInfo.model_validate(user),
        )
    )


@router.get("/me", response_model=ApiResponse[UserInfo])
def me(user: User = Depends(get_current_user)):
    return ApiResponse(data=UserInfo.model_validate(user))
