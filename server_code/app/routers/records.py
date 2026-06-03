from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import User
from app.schemas import (
    ApiResponse,
    CommentRequest,
    ManualReviewRequest,
    RecordDetail,
    RecordListItem,
    SpotCheckRequest,
    WorkspaceResponse,
)
from app.services.record_service import (
    add_comment,
    get_record_detail,
    get_record_file_path,
    list_records,
    manual_review,
    spot_check,
    upload_and_audit,
)

router = APIRouter(prefix="/records", tags=["上传记录"])


@router.post("/upload", response_model=ApiResponse[RecordDetail])
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record = await upload_and_audit(db, file, user)
    return ApiResponse(data=record)


@router.get("", response_model=ApiResponse[list[RecordListItem]])
def get_records(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ApiResponse(data=list_records(db))


@router.get("/{record_id}", response_model=ApiResponse[RecordDetail])
def get_record(record_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ApiResponse(data=get_record_detail(db, record_id))


@router.get("/{record_id}/workspace", response_model=ApiResponse[WorkspaceResponse])
def get_workspace(record_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    detail = get_record_detail(db, record_id)
    ai_status = "pass" if detail.aiResult == "PASS" else "fail"
    return ApiResponse(data=WorkspaceResponse(record=detail, aiStatus=ai_status))


@router.get("/{record_id}/file")
def download_file(record_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    path = get_record_file_path(db, record_id)
    return FileResponse(path, media_type="application/pdf", filename=path.name)


@router.post("/{record_id}/manual-review", response_model=ApiResponse[RecordDetail])
def post_manual_review(
    record_id: str,
    body: ManualReviewRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    operator = user.name or user.username
    record = manual_review(db, record_id, body.action, operator, body.comment)
    return ApiResponse(data=record)


@router.post("/{record_id}/comment", response_model=ApiResponse[RecordDetail])
def post_comment(
    record_id: str,
    body: CommentRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    operator = user.name or user.username
    record = add_comment(db, record_id, operator, body.comment)
    return ApiResponse(data=record)


@router.post("/{record_id}/spot-check", response_model=ApiResponse[RecordDetail])
def post_spot_check(
    record_id: str,
    body: SpotCheckRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    operator = user.name or user.username
    record = spot_check(db, record_id, operator, body.result, body.comment)
    return ApiResponse(data=record)
