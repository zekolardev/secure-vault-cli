import json

import pytest

from src.vault import Vault, InvalidPasswordError


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.json"


@pytest.fixture
def vault(vault_path):
    instance = Vault(vault_path, "MasterPassword123!")
    instance.create()
    return instance


def test_create_vault(vault_path):
    vault = Vault(vault_path, "MasterPassword123!")
    vault.create()

    assert vault_path.exists()
    assert vault.entries == {}


def test_create_existing_vault(vault):
    with pytest.raises(FileExistsError):
        Vault(vault.file_path, "AnotherPassword123!").create()


def test_open_vault(vault_path):
    original = Vault(vault_path, "MasterPassword123!")
    original.create()
    original.add_entry("GitHub", "zekolar", "Secret123!")

    opened = Vault(vault_path, "MasterPassword123!")
    opened.open()

    assert opened.get_entry("GitHub")["username"] == "zekolar"
    assert opened.get_entry("GitHub")["password"] == "Secret123!"


def test_wrong_master_password(vault_path):
    Vault(vault_path, "MasterPassword123!").create()

    wrong_vault = Vault(vault_path, "WrongPassword123!")

    with pytest.raises(InvalidPasswordError):
        wrong_vault.open()


def test_add_entry(vault):
    vault.add_entry("GitHub", "zekolar", "Secret123!")

    entry = vault.get_entry("GitHub")

    assert entry["username"] == "zekolar"
    assert entry["password"] == "Secret123!"
    assert entry["url"] == ""


def test_duplicate_entry(vault):
    vault.add_entry("GitHub", "zekolar", "Secret123!")

    with pytest.raises(ValueError):
        vault.add_entry("GitHub", "another_user", "Another123!")


def test_empty_entry_name(vault):
    with pytest.raises(ValueError):
        vault.add_entry("", "zekolar", "Secret123!")


def test_get_missing_entry(vault):
    with pytest.raises(KeyError):
        vault.get_entry("Unknown")


def test_list_entries(vault):
    vault.add_entry("GitHub", "user1", "pass1")
    vault.add_entry("Google", "user2", "pass2")

    assert vault.list_entries() == ["GitHub", "Google"]


def test_search_entries(vault):
    vault.add_entry("GitHub", "user1", "pass1")
    vault.add_entry("Google", "user2", "pass2")

    assert vault.search_entries("git") == ["GitHub"]
    assert vault.search_entries("GOO") == ["Google"]


def test_delete_entry(vault):
    vault.add_entry("GitHub", "user1", "pass1")
    vault.delete_entry("GitHub")

    assert vault.list_entries() == []


def test_delete_missing_entry(vault):
    with pytest.raises(KeyError):
        vault.delete_entry("Unknown")


def test_data_is_encrypted(vault):
    vault.add_entry("GitHub", "zekolar", "Secret123!")

    raw_data = vault.file_path.read_text(encoding="utf-8")

    assert "Secret123!" not in raw_data
    assert "zekolar" not in raw_data


def test_persistence_after_reopening(vault):
    vault.add_entry("GitHub", "zekolar", "Secret123!")

    reopened = Vault(vault.file_path, "MasterPassword123!")
    reopened.open()

    assert "GitHub" in reopened.list_entries()


def test_save_creates_parent_directories(tmp_path):
    path = tmp_path / "nested" / "folder" / "vault.json"

    vault = Vault(path, "MasterPassword123!")
    vault.create()

    assert path.exists()