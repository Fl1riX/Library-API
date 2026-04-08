from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.infrastructure.db.database import get_db
from src.domain.services.jwt_service import verify_password, create_access_token
from src.domain.services.auth_service import AuthService
from ..exceptions import HTTPConflict, HTTPNotAuthorized, HTTPNotFound, HTTPBadRequest
from src.shared.schemas.readers_schema import CreateReader, ChangePassword, LoginReader
from src.domain.services.exceptions import ConflictException, InvalidDataException
from src.domain.services.auth_dependencies import get_current_user_id

router = APIRouter(prefix="/auth", tags=["Авторизация"])

@router.post("/login")
async def login(
    reader: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
): 
    found_reader = await AuthService.find_user_by_login(reader.username, db)
    if found_reader is None:
        raise HTTPNotFound
    
    if not verify_password(reader.password, found_reader.password):
        raise HTTPNotAuthorized
    
    try:
        token = create_access_token(found_reader.id)
    except Exception as e:
        print(f"Ошибка: {e}")
        raise
        
    return {
        "access_token": token,
        "token_type": "Bearer"
    }
    
@router.post("/register")
async def register(
    reader: CreateReader,
    db: AsyncSession = Depends(get_db)
):  
    try:
        new_reader = await AuthService.create_user(reader, db)
    except ConflictException:
        raise HTTPConflict("User already exists")
    
    try:
        token = create_access_token(new_reader.id)
    except Exception as e:
        print(f"Ошибка: {e}")
    
    return {
        "reader": new_reader,
        "access_token": token,
        "token_type": "Bearer"
    }
    
@router.post("/change_password")
async def change_password(
    user_data: ChangePassword,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    user = await AuthService.find_user_by_id(current_user_id, db)
    if user is None:
        raise HTTPNotFound
    
    if current_user_id != user.id:
        raise HTTPNotAuthorized
    
    try: 
        await AuthService.change_password(user_data.password, user_data.new_password, user, db)
    except InvalidDataException:
        raise HTTPBadRequest("Passwords match")
    
    return {"succes": True}