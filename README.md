# SecureVault CLI

A secure Python CLI password manager with encrypted credential storage.

SecureVault CLI helps you store, manage, search, and generate passwords directly from your terminal.

## Features

- Master password authentication
- Password-based key derivation using Scrypt
- Symmetric encryption using Fernet
- Encrypted local credential storage
- Add, view, search, list, and delete credentials
- Cryptographically secure password generation
- Atomic file writing
- Automated test suite with pytest

## Requirements

- Python 3.10+
- cryptography
- pytest (for testing)

## Installation

Clone the repository:

```bash
git clone https://github.com/zekolardev/secure-vault-cli.git
cd secure-vault-cli