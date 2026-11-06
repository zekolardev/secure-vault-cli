import pytest

from src.generator import generate_password


def test_default_password_length():
    password = generate_password()

    assert len(password) == 20


def test_custom_password_length():
    password = generate_password(32)

    assert len(password) == 32


def test_password_contains_all_character_types():
    password = generate_password()

    assert any(c.islower() for c in password)
    assert any(c.isupper() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(not c.isalnum() for c in password)


def test_lowercase_only():
    password = generate_password(
        length=12,
        use_uppercase=False,
        use_digits=False,
        use_special=False,
    )

    assert password.islower()
    assert password.isalpha()


def test_uppercase_only():
    password = generate_password(
        length=12,
        use_lowercase=False,
        use_digits=False,
        use_special=False,
    )

    assert password.isupper()
    assert password.isalpha()


def test_digits_only():
    password = generate_password(
        length=12,
        use_lowercase=False,
        use_uppercase=False,
        use_special=False,
    )

    assert password.isdigit()


def test_special_characters_only():
    password = generate_password(
        length=12,
        use_lowercase=False,
        use_uppercase=False,
        use_digits=False,
    )

    assert not password.isalnum()


def test_no_character_set_enabled():
    with pytest.raises(ValueError):
        generate_password(
            use_lowercase=False,
            use_uppercase=False,
            use_digits=False,
            use_special=False,
        )


def test_passwords_are_random():
    passwords = {
        generate_password()
        for _ in range(10)
    }

    assert len(passwords) == 10


def test_invalid_short_length():
    with pytest.raises(ValueError):
        generate_password(3)


def test_invalid_length_type():
    with pytest.raises(TypeError):
        generate_password("20")


def test_boolean_length_is_rejected():
    with pytest.raises(TypeError):
        generate_password(True)