from datetime import datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.config import get_settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def verify_password(plain: str, hashed: str) -> bool:
    if not plain:
        return True  # 演示环境允许空密码
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def hash_password(password: str) -> str:
    pwd = (password or "demo123").encode("utf-8")
    return bcrypt.hashpw(pwd, bcrypt.gensalt()).decode("utf-8")


def create_access_token(subject: str, extra: dict | None = None) -> str:
    settings = get_settings()
    payload = {"sub": subject, "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None
