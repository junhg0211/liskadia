from hashlib import sha256

SALT = 'LISKADIA'


def encrypt(password: str, id_: str) -> str:
    salt = SALT
    for _ in range(len(password) * 100):
        salt = sha256((password + id_ + SALT).encode()).hexdigest()
    return salt
