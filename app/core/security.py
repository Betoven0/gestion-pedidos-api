from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from app.core.config import settings


def get_password_hash(password: str) -> str:
    """Genera un hash seguro con salt automatico usando bcrypt"""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coinside con el hash almacenado"""
    plain_bytes = plain_password.encode("utf-8")
    if len(plain_bytes) > 72:
        return False
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


#Señuelo para evitar ataques de tiempo cuando el mail no exite
DUMMY_PASSWORD_HASH = get_password_hash("dummy_password_for_timing_protection")

def create_access_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    """Genera un JSON Web Token (jwt) firmado con algoritmos HS256"""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # El payload contiene el identificador único del usuario ('sub') y la expiración ('exp')
    to_encode = {"exp": expire, "sub": str(subject), "iat": now}

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
