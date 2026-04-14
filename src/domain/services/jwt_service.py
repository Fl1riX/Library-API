from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta

from src.config import get_algorithm, get_secret_key

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """Создание хэша пароля"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяем подлинность пароля"""
    return pwd_context.verify(password, hashed_password)

def create_access_token(user_id: int) -> str:
    """Создание JWT токена"""
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode = {
        "exp": expires_at,
        "sub": user_id
    }
    encoded_jwt = jwt.encode(to_encode, get_secret_key(), algorithm=get_algorithm())
    
    if not encoded_jwt:
        raise ValueError
    
    return encoded_jwt

def decode_token(token: str) -> dict | None:
    """Раскодирование токена"""
    try:
        decoded_token = jwt.decode(
            token, 
            get_secret_key(), 
            algorithms=[get_algorithm()], 
            options={
                "require_exp": True,
                "verify_signature": True
            }
        )

        user_id = decoded_token.get("sub")
        if user_id:
            user_id = int(user_id)

        if not user_id or not isinstance(user_id, int):
            return None

        return {"sub": user_id}
    except JWTError as e:
        print(f"Невалидный токен: {e}")
        return None
    
    
    