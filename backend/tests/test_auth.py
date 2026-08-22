import pytest
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token, generate_totp_secret, verify_totp


def test_password_hashing():
    pwd = "MySecretPass2026!"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPass", hashed) is False


def test_jwt_token_generation():
    data = {"sub": "admin", "role": "Administrateur"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "admin"
    assert decoded["role"] == "Administrateur"


def test_totp_secret():
    secret = generate_totp_secret()
    assert len(secret) == 32
