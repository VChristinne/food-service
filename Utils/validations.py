from passlib.hash import sha256_crypt
import re


def hash_password(password: str) -> str:
    hashed = sha256_crypt.using(rounds=1000).hash(password)
    return hashed

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return sha256_crypt.verify(plain_password, hashed_password)

def sanitize_user_agent(user_agent: str | None, max_length: int = 256) -> str:
    if not user_agent:
        return "unknown"
    user_agent = user_agent[:max_length]
    user_agent = re.sub(r'[^\w\s/().;,_:\-]', '', user_agent)   # whitelist common characters
    return user_agent.strip() or "unknown"
