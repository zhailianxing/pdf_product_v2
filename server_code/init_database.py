"""初始化 MySQL 数据库：建表 + 写入 mock 数据。

用法:
    python init_database.py          # 建表，仅在空库时写入 mock
    python init_database.py --reset  # 清空表后重新写入 mock
"""

import argparse
import sys

from sqlalchemy import text

from app.database import SessionLocal, engine
from app.models import AuditLog, Base, UploadRecord, User
from app.seed import seed_records, seed_users


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    print("[OK] Tables ready: users, upload_records, audit_logs")


def reset_tables() -> None:
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for table in ("audit_logs", "upload_records", "users"):
            conn.execute(text(f"TRUNCATE TABLE `{table}`"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
        conn.commit()
    print("[OK] Tables truncated")


def seed_all() -> None:
    db = SessionLocal()
    try:
        seed_users(db)
        seed_records(db)
        db.commit()
        user_count = db.query(User).count()
        record_count = db.query(UploadRecord).count()
        log_count = db.query(AuditLog).count()
        print(f"[OK] Mock data: users={user_count}, upload_records={record_count}, audit_logs={log_count}")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="初始化 pdf_vl 数据库")
    parser.add_argument("--reset", action="store_true", help="清空表后重新导入 mock 数据")
    args = parser.parse_args()

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[OK] MySQL connected (pdf_vl)")
    except Exception as exc:
        print(f"[ERROR] Database connection failed: {exc}", file=sys.stderr)
        sys.exit(1)

    create_tables()
    if args.reset:
        reset_tables()
    seed_all()


if __name__ == "__main__":
    main()
