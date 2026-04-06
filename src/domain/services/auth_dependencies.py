#from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

#from infrastructure.db.database import get_db
from src.domain.services.jwt_service import decode_token
from src.presentation.api.v1.exceptions import HTTPNotAuthorized

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user_id(
    token: str = Depends(oauth2_scheme)
) -> int | None:
    if not token:
        raise HTTPNotAuthorized("Token Not Found")
    
    try:
        payload = decode_token(token)
    except Exception as e:
        print(f"Ошибка в определении id текущего пользователя: {e}")
        raise
    
    if not payload:
        raise ValueError
    
    user_id = payload.get("sub")
    
    if user_id is None:
        return None
    user_id = int(user_id)
    
    return user_id