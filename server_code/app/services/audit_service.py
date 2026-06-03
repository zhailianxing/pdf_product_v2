import json
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import AuditLog, UploadRecord

ACTION_LABELS = {
    "UPLOAD": "上传报告",
    "AI_AUDIT": "AI 自动审核",
    "MANUAL_CONFIRM_FAIL": "审核员确认不合格",
    "MANUAL_OVERRIDE_PASS": "审核员强转合格",
    "MANUAL_COMMENT": "添加审核备注",
    "ADMIN_SPOT_CHECK": "管理员抽检",
}


def format_time(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def add_audit_log(
    db: Session,
    *,
    action: str,
    operator: str,
    detail: str,
    record_id: str | None = None,
    file_name: str | None = None,
    result: str | None = None,
) -> AuditLog:
    log = AuditLog(
        id=f"log{uuid.uuid4().hex[:12]}",
        time=datetime.utcnow(),
        action=action,
        record_id=record_id,
        file_name=file_name,
        operator=operator,
        detail=detail,
        result=result,
    )
    db.add(log)
    return log


def log_upload(db: Session, record: UploadRecord, operator: str) -> None:
    add_audit_log(
        db,
        action="UPLOAD",
        record_id=record.id,
        file_name=record.file_name,
        operator=operator,
        detail="上传材质报告 PDF",
    )


def log_ai_audit(
    db: Session,
    record: UploadRecord,
    reasons: list[str],
    model_name: str,
) -> None:
    reason_text = "；".join(reasons) if reasons else "化学成分、力学性能均符合要求"
    add_audit_log(
        db,
        action="AI_AUDIT",
        record_id=record.id,
        file_name=record.file_name,
        operator=f"系统 ({model_name})",
        detail=f"AI 判定：{record.ai_result} — {reason_text}",
        result=record.ai_result,
    )


def get_audit_stats(db: Session) -> dict:
    logs = db.query(AuditLog).all()
    manual_actions = {"MANUAL_CONFIRM_FAIL", "MANUAL_OVERRIDE_PASS", "MANUAL_COMMENT"}
    return {
        "total": len(logs),
        "upload": sum(1 for l in logs if l.action == "UPLOAD"),
        "aiAudit": sum(1 for l in logs if l.action == "AI_AUDIT"),
        "manual": sum(1 for l in logs if l.action in manual_actions),
        "spotCheck": sum(1 for l in logs if l.action == "ADMIN_SPOT_CHECK"),
    }


def serialize_log(log: AuditLog) -> dict:
    return {
        "id": log.id,
        "time": format_time(log.time),
        "action": log.action,
        "recordId": log.record_id,
        "fileName": log.file_name,
        "operator": log.operator,
        "detail": log.detail,
        "result": log.result,
    }


def parse_ai_detail(record: UploadRecord):
    if not record.ai_detail:
        return None
    try:
        from app.schemas import AiExtractionResult

        return AiExtractionResult(**json.loads(record.ai_detail))
    except Exception:
        return None


def parse_ai_reasons(record: UploadRecord) -> list[str]:
    if not record.ai_reasons:
        return []
    try:
        return json.loads(record.ai_reasons)
    except Exception:
        return []
