import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import UploadRecord, User
from app.schemas import AiExtractionResult, RecordDetail, RecordListItem
from app.services.ai_service import get_ai_client
from app.services.audit_service import (
    add_audit_log,
    format_time,
    log_ai_audit,
    log_upload,
    parse_ai_detail,
    parse_ai_reasons,
)
from app.services.pdf_utils import guess_supplier


def _record_to_list_item(record: UploadRecord) -> RecordListItem:
    return RecordListItem(
        id=record.id,
        fileName=record.file_name,
        supplier=record.supplier,
        uploader=record.uploader,
        uploadTime=format_time(record.upload_time),
        aiResult=record.ai_result,
        manualResult=record.manual_result,
        adminSpotCheckResult=record.admin_spot_check_result,
    )


def _record_to_detail(record: UploadRecord) -> RecordDetail:
    return RecordDetail(
        **_record_to_list_item(record).model_dump(),
        aiDetail=parse_ai_detail(record),
        aiReasons=parse_ai_reasons(record),
        comment=record.comment,
        modelName=record.model_name,
        processTimeMs=record.process_time_ms,
        pdfUrl=f"/api/v1/records/{record.id}/file",
    )


def get_record_or_404(db: Session, record_id: str) -> UploadRecord:
    record = db.query(UploadRecord).filter(UploadRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    return record


async def upload_and_audit(db: Session, file: UploadFile, user: User) -> RecordDetail:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="仅支持 PDF 格式")

    record_id = str(uuid.uuid4())
    settings = get_settings()
    save_dir = settings.upload_path / record_id
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / file.filename

    with save_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    ai_client = get_ai_client()
    ai_result, extraction, reasons, model_name, process_ms = await ai_client.audit_pdf(
        save_path, file.filename
    )

    record = UploadRecord(
        id=record_id,
        file_name=file.filename,
        file_path=str(save_path),
        supplier=extraction.supplier or guess_supplier(file.filename),
        uploader=user.name or user.username,
        upload_time=datetime.utcnow(),
        ai_result=ai_result,
        ai_detail=extraction.model_dump_json(),
        ai_reasons=json.dumps(reasons, ensure_ascii=False),
        model_name=model_name,
        process_time_ms=process_ms,
    )
    db.add(record)
    log_upload(db, record, record.uploader)
    log_ai_audit(db, record, reasons, model_name)
    db.commit()
    db.refresh(record)
    return _record_to_detail(record)


def list_records(db: Session) -> list[RecordListItem]:
    records = db.query(UploadRecord).order_by(UploadRecord.upload_time.desc()).all()
    return [_record_to_list_item(r) for r in records]


def get_record_detail(db: Session, record_id: str) -> RecordDetail:
    return _record_to_detail(get_record_or_404(db, record_id))


def get_record_file_path(db: Session, record_id: str) -> Path:
    record = get_record_or_404(db, record_id)
    path = Path(record.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF 文件不存在")
    return path


def manual_review(
    db: Session,
    record_id: str,
    action: str,
    operator: str,
    comment: str | None = None,
) -> RecordDetail:
    record = get_record_or_404(db, record_id)

    if action == "confirm_fail":
        record.manual_result = "FAIL"
        log_action = "MANUAL_CONFIRM_FAIL"
        detail = "人工审核：确认 AI FAIL 判定，维持不合格"
        result = "FAIL"
    elif action == "override_pass":
        record.manual_result = "PASS"
        log_action = "MANUAL_OVERRIDE_PASS"
        detail = "人工审核：AI FAIL → 人工 PASS（强转合格）"
        result = "PASS"
    else:
        raise HTTPException(status_code=400, detail="无效操作")

    if comment:
        record.comment = comment

    add_audit_log(
        db,
        action=log_action,
        record_id=record.id,
        file_name=record.file_name,
        operator=operator,
        detail=detail + (f"；备注：{comment}" if comment else ""),
        result=result,
    )
    db.commit()
    db.refresh(record)
    return _record_to_detail(record)


def add_comment(db: Session, record_id: str, operator: str, comment: str) -> RecordDetail:
    record = get_record_or_404(db, record_id)
    record.comment = comment
    add_audit_log(
        db,
        action="MANUAL_COMMENT",
        record_id=record.id,
        file_name=record.file_name,
        operator=operator,
        detail=f"审核备注：{comment}" if comment else "添加审核备注（无内容）",
    )
    db.commit()
    db.refresh(record)
    return _record_to_detail(record)


def spot_check(
    db: Session,
    record_id: str,
    operator: str,
    result: str,
    comment: str | None = None,
) -> RecordDetail:
    record = get_record_or_404(db, record_id)
    if record.ai_result != "PASS":
        raise HTTPException(status_code=400, detail="仅 PASS 自动通过件可进行管理员抽检")

    record.admin_spot_check_result = result
    detail = f"PASS 件抽检：{'确认 AI 判定正确' if result == 'PASS' else '发现 AI 漏判问题'}"
    if comment:
        detail += f"；备注：{comment}"

    add_audit_log(
        db,
        action="ADMIN_SPOT_CHECK",
        record_id=record.id,
        file_name=record.file_name,
        operator=operator,
        detail=detail,
        result=result,
    )
    db.commit()
    db.refresh(record)
    return _record_to_detail(record)


def get_dashboard_data(db: Session) -> dict:
    records = db.query(UploadRecord).all()
    total = len(records)
    pass_count = sum(1 for r in records if r.ai_result == "PASS")
    fail_count = total - pass_count
    pass_rate = round(pass_count / total * 100, 1) if total else 0.0
    fail_rate = round(fail_count / total * 100, 1) if total else 0.0

    times = [r.process_time_ms for r in records if r.process_time_ms]
    avg_time = round(sum(times) / len(times) / 1000, 1) if times else 0.0

    pending = [
        {
            "id": r.id,
            "fileName": r.file_name,
            "supplier": r.supplier,
            "reason": "；".join(parse_ai_reasons(r)) or "AI 判定 FAIL",
            "uploadTime": format_time(r.upload_time),
        }
        for r in records
        if r.ai_result == "FAIL" and not r.manual_result
    ]
    pending.sort(key=lambda x: x["uploadTime"], reverse=True)

    return {
        "kpi": {
            "totalReports": total,
            "passRate": pass_rate,
            "failRate": fail_rate,
            "avgProcessTime": avg_time,
            "trends": {
                "totalReports": f"+{total}" if total else "0",
                "passRate": f"{pass_rate}%",
                "failRate": f"{fail_rate}%",
                "avgProcessTime": f"{avg_time}s",
            },
        },
        "pendingQueue": pending,
    }
