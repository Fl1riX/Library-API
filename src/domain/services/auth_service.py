from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from src.infrastructure.db.models import Readers
from .exceptions import ConflictException, InvalidDataException
from src.shared.schemas.readers_schema import CreateReader
from .jwt_service import hash_password

class AuthService:
    
    @classmethod
    async def find_user_by_login(cls, email: str, phone: str, db: AsyncSession) -> Readers | None:
        result = await db.execute(select(Readers).where(
            or_(
                Readers.email == email,
                Readers.phone == phone
            )
        ))
        reader = result.scalars().first()
        if not reader:
            return None
        return reader
    
    @classmethod
    async def create_user(cls, new_user: CreateReader, db: AsyncSession):
        exists = await cls.find_user_by_login(new_user.email, new_user.phone, db)
        if exists is not None:
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
        
        