from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(String(16))  # admin | auditor
    status: Mapped[str] = mapped_column(String(16), default="active")
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UploadRecord(Base):
    __tablename__ = "upload_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(512))
    supplier: Mapped[str] = mapped_column(String(128), default="未知厂商")
    uploader: Mapped[str] = mapped_column(String(64))
    upload_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    ai_result: Mapped[str] = mapped_column(String(8))  # PASS | FAIL
    ai_detail: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    ai_reasons: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    model_name: Mapped[str] = mapped_column(String(64), default="mock")
    process_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)

    manual_result: Mapped[str | None] = mapped_column(String(8), nullable=True)
    admin_spot_check_result: Mapped[str | None] = mapped_column(String(8), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    action: Mapped[str] = mapped_column(String(32), index=True)
    record_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    operator: Mapped[str] = mapped_column(String(64))
    detail: Mapped[str] = mapped_column(Text)
    result: Mapped[str | None] = mapped_column(String(8), nullable=True)
