# utils/password.py
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

passwordHasher = PasswordHasher()

def make_password(password: str) -> str:
    return passwordHasher.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        return passwordHasher.verify(hashed, password)
    except VerifyMismatchError:
        return False

