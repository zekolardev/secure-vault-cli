import secrets
import string


DEFAULT_LENGTH = 20

LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SPECIAL_CHARACTERS = "!@#$%^&*()-_=+[]{};:,.?"


def generate_password(
    length=DEFAULT_LENGTH,
    use_lowercase=True,
    use_uppercase=True,
    use_digits=True,
    use_special=True,
):
    """Generate a cryptographically secure random password."""

    if not isinstance(length, int) or isinstance(length, bool):
        raise TypeError("Password length must be an integer.")

    if length < 4:
        raise ValueError("Password length must be at least 4.")

    character_sets = []

    if use_lowercase:
        character_sets.append(LOWERCASE)

    if use_uppercase:
        character_sets.append(UPPERCASE)

    if use_digits:
        character_sets.append(DIGITS)

    if use_special:
        character_sets.append(SPECIAL_CHARACTERS)

    if not character_sets:
        raise ValueError("At least one character set must be enabled.")

    if length < len(character_sets):
        raise ValueError("Password length is too short for selected options.")

    password = [
        secrets.choice(characters)
        for characters in character_sets
    ]

    all_characters = "".join(character_sets)

    password.extend(
        secrets.choice(all_characters)
        for _ in range(length - len(password))
    )

    secrets.SystemRandom().shuffle(password)

    return "".join(password)