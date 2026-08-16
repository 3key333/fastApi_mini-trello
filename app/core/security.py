# хеш + AuthX

from datetime import timedelta

from authx import AuthX, AuthXConfig
from pwdlib import PasswordHash

from app.core.config import settings


# recommended() = Argon2. hash() и verify() — единственные две операции
password_hasher = PasswordHash.recommended()

auth = AuthX(
    config=AuthXConfig(
        JWT_SECRET_KEY=settings.jwt_secret_key,
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=settings.jwt_access_expires_minutes),
        JWT_TOKEN_LOCATION=["headers"]   # Authorization: Bearer ..., не cookie
    )
)

def hash_password(plain: str) -> str:
    return password_hasher.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return password_hasher.verify(plain, hashed)
