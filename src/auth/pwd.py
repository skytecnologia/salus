import secrets
import string
import bcrypt

LENGTH = 12


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def generate_random_password() -> str:
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = string.punctuation

    # Ensure the password has at least one of each character type
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        # secrets.choice(symbols)
    ]

    # Fill the rest with random choices from all sets combined
    all_chars = lowercase + uppercase + digits  # + symbols
    remaining = max(0, LENGTH - len(password))
    password += [secrets.choice(all_chars) for _ in range(remaining)]

    # Shuffle to avoid predictable pattern
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)
