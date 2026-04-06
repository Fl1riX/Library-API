import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import List

from src.domain.services.books_service import BooksService
from src.infrastructure.db.models import Books
from src.domain.services.exceptions import NotFoundException

@pytest.mark.asyncio
async def test_get_book_by_isbn_found():
    fake_book = MagicMock(spec=Books)
    fake_book.isbn = "1234567898642"
    fake_book.title = "Test Book"
    
    mock_db = AsyncMock() # Создаем мок сессии, который будет имитировать асинхронное подключение к бд
    
    # Мокаем результат вызова бд
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = fake_book
    mock_db.execute.return_value = mock_result
    
    # Вызываем тестируемый метод
    result = await BooksService.get_book_by_isbn(mock_db, "1234567898642")
    
    # Проверяем что метод вызвал db.execute только 1 раз 
    mock_db.execute.assert_called_once()
    
    assert result == fake_book

@pytest.mark.asyncio
async def test_get_book_by_isbn_not_found():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    
    mock_result.scalars().first.return_value = None
    mock_db.execute.return_value = mock_result
    
    result = await BooksService.get_book_by_isbn(mock_db, "test")
    
    assert result is None
    
@pytest.mark.asyncio
async def test_title_search_book():
    mock_db = AsyncMock()
    fake_books = [MagicMock(), MagicMock()]
    fake_books[0].title = "Test Title"
    fake_books[1].title = "Test Title2"
    
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = fake_books
    mock_db.scalar.return_value = 1
    mock_db.execute.return_value = mock_result
    
    books, total = await BooksService.search_book(db=mock_db, title="Test Title")
    
    assert books == fake_books
    assert total == 1

@pytest.mark.asyncio
async def test_search_book_none():
    mock_db =  AsyncMock()
    mock_result = MagicMock()
    
    mock_db.scalar.return_value = 0
    mock_result.scalars().all.return_value = []
    mock_db.execute.return_value = mock_result
    
    with pytest.raises(NotFoundException):
        await BooksService.search_book(mock_db)
    