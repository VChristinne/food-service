from passlib.hash import sha256_crypt


def hash_password(password: str) -> str:
    hashed = sha256_crypt.using(rounds=1000).hash(password)
    return hashed

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return sha256_crypt.verify(plain_password, hashed_password)
