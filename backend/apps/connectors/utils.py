import json
from django.conf import settings
from cryptography.fernet import Fernet
import base64
import hashlib


def _derive_key() -> bytes:
    """Derive a Fernet-compatible key from DJANGO_SECRET_KEY."""
    raw = settings.SECRET_KEY.encode()
    key = base64.urlsafe_b64encode(hashlib.sha256(raw).digest())
    return key


def encrypt_credentials(data: dict) -> str:
    """Encrypt a credential dict to a Fernet token string."""
    fernet = Fernet(_derive_key())
    return fernet.encrypt(json.dumps(data, ensure_ascii=False).encode()).decode()


def decrypt_credentials(token: str) -> dict:
    """Decrypt a Fernet token string back to a credential dict."""
    fernet = Fernet(_derive_key())
    return json.loads(fernet.decrypt(token.encode()).decode())