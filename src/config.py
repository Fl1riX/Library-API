import os
from dotenv import load_dotenv

load_dotenv()

def get_secret_key() -> str:
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY не указан в .env")
    return SECRET_KEY

def get_algorithm() -> str:
    ALGORITHM = os.getenv("ALGORITHM")
    if not ALGORITHM:
        raise ValueError("ALGORITHM отсутствует в .env")
    return ALGORITHM