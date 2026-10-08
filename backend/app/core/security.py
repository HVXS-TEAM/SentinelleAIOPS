from datetime import timedelta
from app.core.time_utils import utcnow_naive
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import pyotp
from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash password using bcrypt with 72-byte truncation safety."""
    pwd_bytes = password.encode('utf-8')
    if len(pwd_bytes) > 72:
        pwd_bytes = pwd_bytes[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password."""
    try:
        pwd_bytes = plain_password.encode('utf-8')
        if len(pwd_bytes) > 72:
            pwd_bytes = pwd_bytes[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = utcnow_naive() + expires_delta
    else:
        expire = utcnow_naive() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_totp_secret() -> str:
    """Generate TOTP secret key for MFA."""
    return pyotp.random_base32()


def verify_totp(secret: str, code: str) -> bool:
    """Verify TOTP code against secret key."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)   # tolère ±30 s de dérive d'horloge
