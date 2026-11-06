
import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


SALT_LENGTH = 16
KEY_LENGTH = 32

SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1


def generate_salt() -> bytes:
    """Generate a cryptographically secure random salt."""
    return os.urandom(SALT_LENGTH)


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible encryption key from a password."""

    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string.")

    if not isinstance(salt, bytes) or len(salt) != SALT_LENGTH:
        raise ValueError("Salt must be exactly 16 bytes.")

    kdf = Scrypt(
        salt=salt,
        length=KEY_LENGTH,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
    )

    key = kdf.derive(password.encode("utf-8"))

    return base64.urlsafe_b64encode(key)


def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Encrypt data using Fernet symmetric encryption."""

    if not isinstance(data, bytes):
        raise TypeError("Data must be bytes.")

    return Fernet(key).encrypt(data)


def decrypt_data(token: bytes, key: bytes) -> bytes:
    """Decrypt Fernet-encrypted data."""

    return Fernet(key).decrypt(token)
