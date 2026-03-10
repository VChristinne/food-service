from passlib.hash import sha256_crypt


def hash_password(password: str) -> str:
    hashed = sha256_crypt.using(rounds=1000).hash(password)
    return hashed