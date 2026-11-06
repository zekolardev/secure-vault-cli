import pytest

from src.cli import main
from src.vault import Vault


@pytest.fixture
def vault_path(tmp_path):
    return tmp_path / "vault.json"


@pytest.fixture
def initialized_vault(vault_path):
    Vault(vault_path, "MasterPassword123!").create()
    return vault_path


def test_init_vault(vault_path, monkeypatch, capsys):
    monkeypatch.setattr(
        "src.cli.getpass.getpass",
        lambda _: "MasterPassword123!",
    )

    result = main(["--vault", str(vault_path), "init"])

    assert result == 0
    assert vault_path.exists()
    assert "created successfully" in capsys.readouterr().out


def test_init_password_mismatch(vault_path, monkeypatch):
    passwords = iter(["Password123!", "Different123!"])

    monkeypatch.setattr(
        "src.cli.getpass.getpass",
        lambda _: next(passwords),
    )

    result = main(["--vault", str(vault_path), "init"])

    assert result == 1
    assert not vault_path.exists()


def test_init_existing_vault(initialized_vault, monkeypatch):
    monkeypatch.setattr(
        "src.cli.getpass.getpass",
        lambda _: "Password123!",
    )

    result = main(["--vault", str(initialized_vault), "init"])

    assert result == 1


def test_add_account(initialized_vault, monkeypatch):
    passwords = iter(["MasterPassword123!", "GitHubSecret123!"])

    monkeypatch.setattr(
        "src.cli.getpass.getpass",
        lambda _: next(passwords),
    )

    inputs = iter(["zekolar", "https://github.com"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = main([
        "--vault", str(initialized_vault),
        "add", "GitHub",
    ])

    assert result == 0

    vault = Vault(initialized_vault, "MasterPassword123!").open()
    assert vault.get_entry("GitHub")["username"] == "zekolar"


def test_list_accounts(initialized_vault, monkeypatch, capsys):
    vault = Vault(initialized_vault, "MasterPassword123!").open()
    vault.add_entry("GitHub", "zekolar", "Secret123!")

    monkeypatch.setattr(
        "src.cli.getpass.getpass",
        lambda _: "MasterPassword123!",
    )

    result = main(["--vault", str(initialized_vault), "list"])

    assert result == 0
    assert "GitHub" in capsys.readouterr().out


def test_list_empty_vault(initialized_vault, monkeypatch, capsys):
    monkeypatch.setattr(
        "src.cli.getpass.getpass",
        lambda _: "MasterPassword123!",
    )

    result = main(["--vault", str(initialized_vault), "list"])

    assert result == 0
    assert "No accounts found" in capsys.readouterr().out


def test_get_account(initialized_vault, monkeypatch, capsys):
    vault = Vault(initialized_vault, "MasterPassword123!").open()
    vault.add_entry("GitHub", "zekolar", "Secret123!")

    monkeypatch.setattr(
        "src.cli.getpass.getpass",
        lambda _: "MasterPassword123!",
    )

    result = main([
        "--vault", str(initialized_vault),
        "get", "GitHub",
    ])

    output = capsys.readouterr().out

    assert result == 0
    assert "zekolar" in output
    assert "Secret123!" in output


def test_search_accounts(initialized_vault, monkeypatch, capsys):
    vault = Vault(initialized_vault, "MasterPassword123!").open()
    vault.add_entry("GitHub", "user1", "pass1")
    vault.add_entry("Google", "user2", "pass2")

    monkeypatch.setattr(
        "src.cli.getpass.getpass",
        lambda _: "MasterPassword123!",
    )

    result = main([
        "--vault", str(initialized_vault),
        "search", "git",
    ])

    output = capsys.readouterr().out

    assert result == 0
    assert "GitHub" in output
    assert "Google" not in output


def test_delete_account(initialized_vault, monkeypatch):
    vault = Vault(initialized_vault, "MasterPassword123!").open()
    vault.add_entry("GitHub", "user1", "pass1")

    monkeypatch.setattr(
        "src.cli.getpass.getpass",
        lambda _: "MasterPassword123!",
    )

    result = main([
        "--vault", str(initialized_vault),
        "delete", "GitHub",
    ])

    assert result == 0

    reopened = Vault(initialized_vault, "MasterPassword123!").open()
    assert reopened.list_entries() == []


def test_wrong_master_password(initialized_vault, monkeypatch, capsys):
    monkeypatch.setattr(
        "src.cli.getpass.getpass",
        lambda _: "WrongPassword123!",
    )

    result = main(["--vault", str(initialized_vault), "list"])

    assert result == 1
    assert "Incorrect master password" in capsys.readouterr().err


def test_missing_vault(monkeypatch, tmp_path):
    missing_path = tmp_path / "missing.json"

    monkeypatch.setattr(
        "src.cli.getpass.getpass",
        lambda _: "MasterPassword123!",
    )

    result = main(["--vault", str(missing_path), "list"])

    assert result == 1


def test_generate_password(capsys):
    result = main(["generate"])

    password = capsys.readouterr().out.strip()

    assert result == 0
    assert len(password) == 20


def test_generate_custom_length(capsys):
    result = main(["generate", "--length", "32"])

    password = capsys.readouterr().out.strip()

    assert result == 0
    assert len(password) == 32


def test_generate_invalid_length():
    result = main(["generate", "--length", "3"])

    assert result == 1