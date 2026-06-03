from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import AuditLog, User
from app.schemas import ApiResponse, AuditLogItem, AuditLogListResponse, AuditLogStats
from app.services.audit_service import ACTION_LABELS, get_audit_stats, serialize_log

router = APIRouter(prefix="/audit-logs", tags=["审核日志"])


@router.get("", response_model=ApiResponse[AuditLogListResponse])
def list_audit_logs(
    action: str | None = Query(None, description="操作类型筛选"),
    keyword: str | None = Query(None, description="关键词搜索"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(AuditLog).order_by(AuditLog.time.desc())
    logs = query.all()

    if action:
        logs = [l for l in logs if l.action == action]
    if keyword:
        kw = keyword.lower()
        logs = [
            l
            for l in logs
            if kw in (l.file_name or "").lower()
            or kw in l.operator.lower()
            or kw in l.detail.lower()
        ]

    stats = get_audit_stats(db)
    return ApiResponse(
        data=AuditLogListResponse(
            items=[AuditLogItem(**serialize_log(l)) for l in logs],
            stats=AuditLogStats(**stats),
        )
    )


@router.get("/action-labels", response_model=ApiResponse[dict])
def get_action_labels(user: User = Depends(get_current_user)):
    return ApiResponse(data=ACTION_LABELS)
