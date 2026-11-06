import argparse
import getpass
import sys
from pathlib import Path

from src.vault import Vault, InvalidPasswordError
from src.generator import generate_password


DEFAULT_VAULT_PATH = Path.home() / ".securevault" / "vault.json"


def create_parser():
    parser = argparse.ArgumentParser(
        prog="securevault",
        description="A secure command-line password manager.",
    )

    parser.add_argument(
        "--vault",
        type=Path,
        default=DEFAULT_VAULT_PATH,
        help="Path to the encrypted vault file.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser("init", help="Create a new vault.")

    add_parser = subparsers.add_parser("add", help="Add a credential.")
    add_parser.add_argument("name")

    list_parser = subparsers.add_parser("list", help="List saved accounts.")

    get_parser = subparsers.add_parser("get", help="View an account.")
    get_parser.add_argument("name")

    search_parser = subparsers.add_parser("search", help="Search accounts.")
    search_parser.add_argument("query")

    delete_parser = subparsers.add_parser("delete", help="Delete an account.")
    delete_parser.add_argument("name")

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate a secure password.",
    )
    generate_parser.add_argument(
        "--length",
        type=int,
        default=20,
        help="Password length (default: 20).",
    )

    return parser


def load_vault(path):
    password = getpass.getpass("Master password: ")
    return Vault(path, password).open()


def handle_init(path):
    if path.exists():
        raise FileExistsError("Vault already exists.")

    password = getpass.getpass("Create master password: ")
    confirmation = getpass.getpass("Confirm master password: ")

    if password != confirmation:
        raise ValueError("Master passwords do not match.")

    if not password:
        raise ValueError("Master password cannot be empty.")

    Vault(path, password).create()
    print("Vault created successfully.")


def handle_add(vault, name):
    username = input("Username: ")
    password = getpass.getpass("Account password: ")
    url = input("Website URL (optional): ")

    vault.add_entry(name, username, password, url)
    print(f"Account '{name}' added successfully.")


def handle_list(vault):
    entries = vault.list_entries()

    if not entries:
        print("No accounts found.")
        return

    print("Saved accounts:")
    for name in entries:
        print(f"- {name}")


def handle_get(vault, name):
    entry = vault.get_entry(name)

    print(f"Name: {name}")
    print(f"Username: {entry['username']}")
    print(f"Password: {entry['password']}")
    print(f"URL: {entry['url']}")


def handle_search(vault, query):
    results = vault.search_entries(query)

    if not results:
        print("No matching accounts found.")
        return

    print("Matching accounts:")
    for name in results:
        print(f"- {name}")


def handle_delete(vault, name):
    vault.delete_entry(name)
    print(f"Account '{name}' deleted successfully.")


def main(argv=None):
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "init":
            handle_init(args.vault)

        elif args.command == "generate":
            password = generate_password(args.length)
            print(password)

        else:
            vault = load_vault(args.vault)

            if args.command == "add":
                handle_add(vault, args.name)

            elif args.command == "list":
                handle_list(vault)

            elif args.command == "get":
                handle_get(vault, args.name)

            elif args.command == "search":
                handle_search(vault, args.query)

            elif args.command == "delete":
                handle_delete(vault, args.name)

        return 0

    except InvalidPasswordError:
        print("Error: Incorrect master password.", file=sys.stderr)

    except (FileNotFoundError, FileExistsError, ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)

    return 1


if __name__ == "__main__":
    sys.exit(main())