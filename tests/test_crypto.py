
import pytest
from cryptography.fernet import InvalidToken

from src.crypto import (
    generate_salt,
    derive_key,
    encrypt_data,
    decrypt_data,
)


def test_generate_salt():
    salt = generate_salt()

    assert isinstance(salt, bytes)
    assert len(salt) == 16


def test_generate_unique_salts():
    assert generate_salt() != generate_salt()


def test_derive_key():
    salt = generate_salt()
    key = derive_key("StrongPassword123!", salt)

    assert isinstance(key, bytes)
    assert len(key) == 44


def test_same_password_and_salt_produce_same_key():
    salt = generate_salt()

    key1 = derive_key("Password123!", salt)
    key2 = derive_key("Password123!", salt)

    assert key1 == key2


def test_different_salts_produce_different_keys():
    key1 = derive_key("Password123!", generate_salt())
    key2 = derive_key("Password123!", generate_salt())

    assert key1 != key2


def test_empty_password():
    with pytest.raises(ValueError):
        derive_key("", generate_salt())


def test_invalid_salt():
    with pytest.raises(ValueError):
        derive_key("Password123!", b"short")


def test_encrypt_and_decrypt():
    salt = generate_salt()
    key = derive_key("Password123!", salt)

    original = b"Sensitive account information"

    encrypted = encrypt_data(original, key)
    decrypted = decrypt_data(encrypted, key)

    assert encrypted != original
    assert decrypted == original


def test_wrong_key_cannot_decrypt():
    salt1 = generate_salt()
    salt2 = generate_salt()

    key1 = derive_key("Password123!", salt1)
    key2 = derive_key("DifferentPassword123!", salt2)

    encrypted = encrypt_data(b"Secret data", key1)

    with pytest.raises(InvalidToken):
        decrypt_data(encrypted, key2)


def test_encrypt_requires_bytes():
    key = derive_key("Password123!", generate_salt())

    with pytest.raises(TypeError):
        encrypt_data("Secret data", key)
