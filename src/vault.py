import json
import os
import tempfile
from pathlib import Path

from cryptography.fernet import InvalidToken

from src.crypto import (
    generate_salt,
    derive_key,
    encrypt_data,
    decrypt_data,
)


class InvalidPasswordError(Exception):
    """Raised when the master password is incorrect."""


class Vault:
    VERSION = 1

    def __init__(self, file_path, password):
        self.file_path = Path(file_path)
        self.password = password
        self.entries = {}
        self.salt = None
        self.key = None

    def create(self):
        """Create a new encrypted vault."""

        if self.file_path.exists():
            raise FileExistsError("Vault already exists.")

        self.salt = generate_salt()
        self.key = derive_key(self.password, self.salt)
        self.password = None

        self.save()
        return self

    def open(self):
        """Open and decrypt an existing vault."""

        if not self.file_path.exists():
            raise FileNotFoundError("Vault file not found.")

        try:
            data = json.loads(
                self.file_path.read_text(encoding="utf-8")
            )

            if data.get("version") != self.VERSION:
                raise ValueError("Unsupported vault version.")

            self.salt = bytes.fromhex(data["salt"])
            self.key = derive_key(self.password, self.salt)
            self.password = None

            encrypted_data = bytes.fromhex(data["data"])
            decrypted_data = decrypt_data(encrypted_data, self.key)

            self.entries = json.loads(
                decrypted_data.decode("utf-8")
            )

        except InvalidToken as exc:
            raise InvalidPasswordError(
                "Incorrect master password."
            ) from exc

        return self

    def save(self):
        """Save vault contents using encrypted atomic file writing."""

        if self.key is None or self.salt is None:
            raise RuntimeError("Vault is not initialized.")

        plaintext = json.dumps(
            self.entries,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")

        encrypted_data = encrypt_data(plaintext, self.key)

        payload = {
            "version": self.VERSION,
            "salt": self.salt.hex(),
            "data": encrypted_data.hex(),
        }

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.file_path.parent,
                delete=False,
            ) as temp_file:
                temp_path = Path(temp_file.name)

                json.dump(
                    payload,
                    temp_file,
                    ensure_ascii=False,
                )

            os.replace(temp_path, self.file_path)

        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink()

    def add_entry(self, name, username, password, url=""):
        """Add a credential entry."""

        if not name or not name.strip():
            raise ValueError("Entry name cannot be empty.")

        if name in self.entries:
            raise ValueError(
                "An entry with this name already exists."
            )

        self.entries[name] = {
            "username": username,
            "password": password,
            "url": url,
        }

        self.save()

    def get_entry(self, name):
        """Retrieve a credential entry."""

        if name not in self.entries:
            raise KeyError(f"Entry '{name}' not found.")

        return self.entries[name]

    def list_entries(self):
        """Return all entry names."""

        return sorted(
            self.entries.keys(),
            key=str.casefold,
        )

    def search_entries(self, query):
        """Search entries by name."""

        query = query.casefold()

        return [
            name
            for name in self.list_entries()
            if query in name.casefold()
        ]

    def delete_entry(self, name):
        """Delete an entry."""

        if name not in self.entries:
            raise KeyError(f"Entry '{name}' not found.")

        del self.entries[name]
        self.save()