from bcrypt import hashpw, gensalt, checkpw


def hash_password(password: str):
    password = password.encode()
    password = hashpw(password, salt=gensalt())
    password = password.decode()
    return password


def check_password(password: str, hashed_password: str):
    return checkpw(password.encode(), hashed_password=hashed_password.encode())
