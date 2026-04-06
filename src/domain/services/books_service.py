from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy import select
from datetime import datetime

from src.infrastructure.db.models import Books
from src.shared.schemas.books_schema import CreateBook
from src.domain.services.exceptions import NotFoundException

class BooksService:
    
    @classmethod
    async def get_book_by_isbn(cls, db: AsyncSession, book_isbn: str) -> Books | None:
        """  
        Получаем книгу по id
        """
        try:
            result = await db.execute(
                select(Books).where(
                    Books.isbn == book_isbn
                )
            )

            book = result.scalars().first()
            return book
        except Exception as e:
            print(f"Ошибка: {e}")
    
    @staticmethod
    async def get_all_books(db: AsyncSession):
        """  
        Получаем все книги
        """
        try:
            result = await db.execute(
                select(Books)
            )
            books = result.scalars().all()
            return books
        except Exception as e:
            print(f"Ошибка: {e}")
    
    @classmethod
    async def create_book(cls, db: AsyncSession, book: CreateBook) -> Books | None:
        """  
        Создаем книгу
        """
        try:
            exists = await cls.get_book_by_isbn(db, book.isbn)
            new_book = Books(**book.model_dump())
            if exists:
                return None

            db.add(new_book)
            await db.commit()
            await db.refresh(new_book)
            return new_book
        except Exception as e:
            await db.rollback()
            print(f"Ошибка: {e}")
            raise
    
    @classmethod
    async def delete_book(cls, db: AsyncSession, isbn: str) -> bool:
        """Удаляем книгу"""
        try:
            book = await cls.get_book_by_isbn(db, isbn)
            if not book:
                return False

            await db.delete(book)
            await db.commit()
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            await db.rollback()
            raise
    
    @classmethod
    async def update_book(cls, db: AsyncSession, book_isbn: str, new_info: CreateBook) -> Books | None:
        """Обновляем мнформацю о книге"""
        try:
            book = await cls.get_book_by_isbn(db, book_isbn)
            if not book:
                return None
            
            for key, value in new_info.model_dump().items():
                if hasattr(book, key):
                    setattr(book, key, value)
            
            new_book = Books(**book)
            
            db.add(new_book)
            await db.commit()
            await db.refresh(new_book)
            
            return new_book
            
        except Exception as e:
            print(f"Ошибка: {e}")
    
    @classmethod
    async def search_book(cls, 
        db: AsyncSession,
        title: str | None = None,
        author: str | None = None,
        isbn: str | None = None,
        year: datetime | None = None,
        pages: int | None = None,
        avalible: bool | None = None,
        skip: int = 0,
        limit: int = 20
    ):
        """Поиск книг с фильтрами"""
        query = select(Books)
        count_query = select(func.count()).select_from(Books) # инструкция: посчитай все строки в таблице
        
        if title:
            query = query.where(Books.title.ilike(f"%{title}%")) # посчитай строки, где title похож на
            count_query = count_query.where(Books.title.ilike(f"%{title}%"))
        if author:
            query = query.where(Books.author.ilike(f"%{author}%"))
            count_query = count_query.where(Books.author.ilike(f"%{author}%"))
        if isbn:
            query = query.where(Books.isbn == isbn)
            count_query = count_query.where(Books.isbn == isbn)
        if year:
            query = query.where(Books.year == year)
            count_query = count_query.where(Books.year == year)
        if pages:
            query = query.where(Books.pages >= pages)
            count_query = count_query.where(Books.pages >= pages)
        if avalible:
            query = query.where(Books.avalible == avalible)
            count_query = count_query.where(Books.avalible == avalible)
            
        total = await db.scalar(count_query) # подсчитываем количество строк, подходящих под условия
        if total == 0:
            raise NotFoundException
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        books = result.scalars().all()
        
        if not books:
            raise NotFoundException
        
        return books, total