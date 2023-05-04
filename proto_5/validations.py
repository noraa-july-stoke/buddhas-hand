def is_not_email(value):
    if "@" in value:
        raise ValueError("Value must not be an email address")

def is_email(value):
    if "@" not in value:
        raise ValueError("Value must be an email address")

def name_length_check(value):
    if (len(value) < 3) or (len(value) > 50):
        raise ValueError("Name must be at least 3 characters long")

def is_string(value):
    if not isinstance(value, str):
        raise ValueError("Value must be a string")
