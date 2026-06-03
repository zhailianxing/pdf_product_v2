from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import ApiResponse, DashboardResponse, KpiData, PendingQueueItem
from app.services.record_service import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("", response_model=ApiResponse[DashboardResponse])
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = get_dashboard_data(db)
    return ApiResponse(
        data=DashboardResponse(
            kpi=KpiData(**data["kpi"]),
            pendingQueue=[PendingQueueItem(**item) for item in data["pendingQueue"]],
        )
    )
