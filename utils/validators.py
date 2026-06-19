import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email):
    return bool(email) and bool(EMAIL_RE.match(email))


def require_fields(data, fields):
    missing = [f for f in fields if not data.get(f)]
    return missing
