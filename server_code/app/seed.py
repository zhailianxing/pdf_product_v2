import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import BASE_DIR, get_settings
from app.database import SessionLocal, engine
from app.models import AuditLog, Base, UploadRecord, User
from app.security import hash_password
from app.services.audit_service import add_audit_log, format_time


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_users(db: Session) -> None:
    if db.query(User).count() > 0:
        return
    users = [
        User(username="admin", password_hash=hash_password("admin123"), name="系统管理员", role="admin"),
        User(username="auditor01", password_hash=hash_password("123456"), name="张审核", role="auditor"),
        User(username="auditor02", password_hash=hash_password("123456"), name="李质检", role="auditor"),
        User(username="auditor03", password_hash=hash_password("123456"), name="王审核", role="auditor", status="inactive"),
    ]
    db.add_all(users)


def _copy_mock_pdf(file_name: str, record_id: str) -> str:
    settings = get_settings()
    mock_dir = BASE_DIR.parent / "mock_data"
    src = mock_dir / file_name
    if not src.exists():
        return ""
    dest_dir = settings.upload_path / record_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / file_name
    shutil.copy2(src, dest)
    return str(dest)


def _build_seed_ai_detail(ai_result: str, supplier: str, reasons: list[str]) -> str:
    if ai_result == "PASS":
        detail = {
            "materialGrade": "ASTM A182 F316L",
            "heatNumber": "A123456",
            "supplier": supplier,
            "certificateNumber": "MC-2026-004521",
            "standard": "EN 10204 3.1",
            "batchNumber": "LOT-20260528",
            "date": "2026-05-28",
            "chemicalComposition": "OK",
            "mechanicalProperties": "OK",
            "reasons": [],
            "fields": [
                {"label": "Supplier", "value": supplier, "highlight": False},
                {"label": "Heat Number", "value": "A123456", "highlight": False},
            ],
            "chemical": [{"element": "S", "actual": "0.008", "requirement": "≤0.030", "status": "ok"}],
            "mechanical": [{"property": "Tensile Strength", "actual": "520 MPa", "requirement": "≥485 MPa", "status": "ok"}],
        }
    else:
        detail = {
            "materialGrade": "ASTM A182 F316L",
            "heatNumber": "—",
            "supplier": supplier,
            "certificateNumber": "BT-2026-00891",
            "standard": "EN 10204 3.1",
            "batchNumber": "LOT-20260530",
            "date": "2026-05-30",
            "chemicalComposition": "FAIL",
            "mechanicalProperties": "OK",
            "reasons": reasons,
            "fields": [
                {"label": "Supplier", "value": supplier, "highlight": False},
                {"label": "Heat Number", "value": "—", "highlight": True},
            ],
            "chemical": [{"element": "S", "actual": "0.042", "requirement": "≤0.030", "status": "fail"}],
            "mechanical": [{"property": "Tensile Strength", "actual": "495 MPa", "requirement": "≥485 MPa", "status": "ok"}],
        }
    return json.dumps(detail, ensure_ascii=False)


def seed_records(db: Session) -> None:
    if db.query(UploadRecord).count() > 0:
        return

    samples = [
        {
            "id": "u001",
            "file_name": "F1 博坦.pdf",
            "supplier": "博坦",
            "uploader": "张审核",
            "upload_time": datetime(2026, 6, 2, 9, 15),
            "ai_result": "FAIL",
            "ai_reasons": ["炉号缺失", "S元素超出标准范围"],
            "model_name": "mock",
            "process_time_ms": 1800,
        },
        {
            "id": "u002",
            "file_name": "F1 轩诺.pdf",
            "supplier": "轩诺",
            "uploader": "李质检",
            "upload_time": datetime(2026, 6, 2, 8, 42),
            "ai_result": "FAIL",
            "manual_result": "PASS",
            "ai_reasons": ["S元素不合格未判断"],
            "model_name": "mock",
            "process_time_ms": 1650,
        },
        {
            "id": "u003",
            "file_name": "C3 威地威.pdf",
            "supplier": "VDV",
            "uploader": "张审核",
            "upload_time": datetime(2026, 6, 1, 14, 20),
            "ai_result": "PASS",
            "admin_spot_check_result": "PASS",
            "ai_reasons": [],
            "model_name": "mock",
            "process_time_ms": 1500,
        },
        {
            "id": "u004",
            "file_name": "F3 迪宝.pdf",
            "supplier": "迪宝",
            "uploader": "王审核",
            "upload_time": datetime(2026, 6, 1, 10, 30),
            "ai_result": "PASS",
            "ai_reasons": [],
            "model_name": "mock",
            "process_time_ms": 1400,
        },
        {
            "id": "u005",
            "file_name": "C3 巨力.pdf",
            "supplier": "巨力",
            "uploader": "李质检",
            "upload_time": datetime(2026, 5, 31, 16, 0),
            "ai_result": "FAIL",
            "manual_result": "FAIL",
            "ai_reasons": ["化学成分范围识别单边"],
            "model_name": "mock",
            "process_time_ms": 2100,
        },
    ]

    for item in samples:
        reasons = item.pop("ai_reasons")
        file_path = _copy_mock_pdf(item["file_name"], item["id"])
        record = UploadRecord(
            file_path=file_path or "",
            ai_detail=_build_seed_ai_detail(item["ai_result"], item["supplier"], reasons),
            ai_reasons=json.dumps(reasons, ensure_ascii=False),
            **item,
        )
        db.add(record)

    db.flush()

    if db.query(AuditLog).count() == 0:
        logs = [
            ("UPLOAD", "u001", "F1 博坦.pdf", "张审核", "上传材质报告 PDF", None),
            ("AI_AUDIT", "u001", "F1 博坦.pdf", "系统 (mock)", "AI 判定：FAIL — 炉号缺失、S元素超出标准范围", "FAIL"),
            ("UPLOAD", "u002", "F1 轩诺.pdf", "李质检", "上传材质报告 PDF", None),
            ("AI_AUDIT", "u002", "F1 轩诺.pdf", "系统 (mock)", "AI 判定：FAIL — S元素不合格未判断", "FAIL"),
            ("MANUAL_OVERRIDE_PASS", "u002", "F1 轩诺.pdf", "李质检", "人工审核：AI FAIL → 人工 PASS（强转合格）", "PASS"),
            ("UPLOAD", "u003", "C3 威地威.pdf", "张审核", "上传材质报告 PDF", None),
            ("AI_AUDIT", "u003", "C3 威地威.pdf", "系统 (mock)", "AI 判定：PASS — 化学成分、力学性能均符合要求", "PASS"),
            ("ADMIN_SPOT_CHECK", "u003", "C3 威地威.pdf", "系统管理员", "PASS 件抽检：确认 AI 判定正确", "PASS"),
            ("UPLOAD", "u004", "F3 迪宝.pdf", "王审核", "上传材质报告 PDF", None),
            ("AI_AUDIT", "u004", "F3 迪宝.pdf", "系统 (mock)", "AI 判定：PASS", "PASS"),
            ("UPLOAD", "u005", "C3 巨力.pdf", "李质检", "上传材质报告 PDF", None),
            ("AI_AUDIT", "u005", "C3 巨力.pdf", "系统 (mock)", "AI 判定：FAIL — 化学成分范围识别单边", "FAIL"),
            ("MANUAL_CONFIRM_FAIL", "u005", "C3 巨力.pdf", "李质检", "人工审核：确认 AI FAIL 判定，维持不合格", "FAIL"),
        ]
        for action, record_id, file_name, operator, detail, result in logs:
            add_audit_log(
                db,
                action=action,
                record_id=record_id,
                file_name=file_name,
                operator=operator,
                detail=detail,
                result=result,
            )


def run_seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_users(db)
        seed_records(db)
        db.commit()
    finally:
        db.close()
