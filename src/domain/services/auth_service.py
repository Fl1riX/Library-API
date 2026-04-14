from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from src.infrastructure.db.models import Readers
from .exceptions import ConflictException, InvalidDataException
from src.shared.schemas.readers_schema import CreateReader
from .jwt_service import hash_password

class AuthService:
    
    @staticmethod
    async def find_user_by_id(user_id: int, db: AsyncSession):
        result = await db.execute(select(Readers).where(
            Readers.id == user_id
        ))
        user = result.scalars().first()
        return user
    
    @classmethod
    async def find_user_by_login(cls, login: str, db: AsyncSession) -> Readers | None:
        result = await db.execute(select(Readers).where(
            or_(
                Readers.email == login,
                Readers.phone == login
            )
        ))
        reader = result.scalars().first()
        if not reader:
            return None
        return reader
    
    @classmethod
    async def create_user(cls, new_user: CreateReader, db: AsyncSession):
        exists_email = await cls.find_user_by_login(new_user.email, db)
        exists_phone = await cls.find_user_by_login(new_user.phone, db)
        
        if exists_email is not None and exists_phone is not None:
            raise ConflictException
        
        new_password = hash_password(new_user.password)
        new_user.password = new_password
        
        reader = Readers(**new_user.model_dump())
        try:
            db.add(reader)
            await db.commit()
            await db.refresh(reader)
            return reader
        except Exception:
            await db.rollback()
            raise 
    
    @staticmethod
    async def change_password(
        password: str, 
        new_password: str, 
        reader: Readers, 
        db: AsyncSession
    ) -> bool:
        if password == new_password:
            raise InvalidDataException
        
        reader.password = hash_password(new_password)
        
        try:
            db.add(reader)
            await db.commit()
            
            return True
        except Exception as e:
            await db.rollback()
            print(f"Error: {e}!")
            raise
        
        