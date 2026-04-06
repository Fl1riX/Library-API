from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from src.infrastructure.db.models import Readers
from src.domain.services.exceptions import NotFoundException
from src.shared.schemas.readers_schema import CreateReader

class ReadersService:
    
    @classmethod
    async def get_reader_by_id(cls, reader_id: int, db: AsyncSession) -> Readers | None:
        """Получаем пользователя по id"""
        try:
            result = await db.execute(select(Readers).where(
                Readers.id == reader_id
            ))
            reader = result.scalars().first()

            return reader
        except Exception as e:
            print(f"Ошибка: {e}")
    
    @staticmethod 
    async def get_all_readers(db: AsyncSession):
        """Получаем всех пользователей"""
        try:
            result = await db.execute(
                select(Readers)
            )
            readers = result.scalars().all()
            return readers
        except Exception as e:
            print(f"Ошибка: {e}")
            
    @staticmethod
    async def search_reader(
        db: AsyncSession,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        registration_date: datetime | None = None,
        skip: int = 10,
        limit: int = 20
    ):
        """Поиск пользователя с фильтрами"""
        query = select(Readers)
        count_query = select(func.count()).select_from(Readers)
        
        if full_name:
            query = query.where(Readers.full_name.ilike(f"%{full_name}%"))
            count_query = count_query.where(Readers.full_name.ilike(f"%{full_name}%"))
        if email:
            query = query.where(Readers.email == email)
            count_query = count_query.where(Readers.email == email)
        if phone:
            query = query.where(Readers.phone == phone)
            count_query = count_query.where(Readers.phone == phone)
        if registration_date:
            query = query.where(Readers.registration_date == registration_date)
            count_query = count_query.where(Readers.registration_date == registration_date)
        
        total = await db.scalar(count_query)
        if total == 0:
            raise NotFoundException
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        readers = result.scalars().all() 
        
        if not readers:
            raise NotFoundException
        
        return readers, total
    
    @classmethod
    async def find_reader_by_email(cls, email: str, db: AsyncSession):
        result = await db.execute(select(Readers).where(
                Readers.email == email
        ))
        reader = result.scalars().all()
        return reader
    
    @classmethod
    async def delete_reader(cls, reader_id: int, db: AsyncSession):
        exists = await cls.get_reader_by_id(reader_id, db)
        if not exists:
            raise NotFoundException
        try:
            await db.delete(select(Readers).where(
                Readers.id == reader_id
            ))
            return True
        except Exception:
            await db.rollback()
            raise
    
    @classmethod
    async def update_user(cls, reader_id: int, new_reader: CreateReader, db: AsyncSession):
        reader = await cls.get_reader_by_id(reader_id, db)
        if not reader:
            raise NotFoundException
        
        for key, value in new_reader.model_dump().items():
            if hasattr(new_reader, key):
                setattr(new_reader, key, value)
                
        new_reader = Readers(**reader)
        
        try:
            db.add(new_reader)
            await db.commit()
            await db.refresh(new_reader)
            
            return new_reader
        except Exception:
            await db.rollback()
            raise