from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import User
from app.schemas import ApiResponse, UserInfo

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("", response_model=ApiResponse[list[UserInfo]])
def list_users(db: Session = Depends(get_db), user: User = Depends(require_admin)):
    users = db.query(User).order_by(User.id).all()
    return ApiResponse(data=[UserInfo.model_validate(u) for u in users])
