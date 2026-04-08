from fastapi import APIRouter, Depends, Query
from src.infrastructure.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.domain.services.books_service import BooksService
from src.presentation.api.v1.exceptions import HTTPNotFound, HTTPConflict, HTTPBadRequest
from src.shared.schemas.books_schema import GetBook, CreateBook
from src.domain.services.exceptions import NotFoundException


router = APIRouter(prefix="/books", tags=["Книги"])

@router.get("/search")
async def search_book(
    title: str | None = Query(None, description="Название книги"),
    author: str | None = Query(None, description="Автор"),
    isbn: str | None = Query(None, description="isbn"),
    year: datetime | None = Query(None, description="Год издания"),
    pages: int | None = Query(None, description="Количество страниц"),
    avalible: bool | None = Query(None, description="Наличие книги"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    
    try:
        books, total = await BooksService.search_book(
            db, title, author, isbn, year, pages, avalible, skip, limit
        )
    except NotFoundException:
        raise HTTPNotFound("Books not found")
    
    return books, total

@router.get("/{book_isbn}", response_model=GetBook)
async def get_book(
    book_isbn: str, 
    db: AsyncSession = Depends(get_db)
):
    if book_isbn:
        if book_isbn:
            book = await BooksService.get_book_by_isbn(db, book_isbn)
            if book is None:
                raise HTTPNotFound("Book not found")

            return book
    else:
        raise HTTPBadRequest

@router.get("/")
async def get_books(
    db: AsyncSession = Depends(get_db)
):
    books = await BooksService.get_all_books(db)
    if books is None:
        raise HTTPNotFound
    return books

@router.post("/", response_model=GetBook)
async def create_book(
    book: CreateBook,
    db: AsyncSession = Depends(get_db)    
):
    new_book = await BooksService.create_book(db=db, book=book)
    if new_book is None:
        raise HTTPConflict
    
    return new_book

@router.delete("/{book_isbn}")
async def delete_book(
    book_isbn: str,
    db: AsyncSession = Depends(get_db)
):
    deleted = await BooksService.delete_book(db, book_isbn)
    if not deleted:
        raise HTTPNotFound
    return True

@router.put("{book_isbn}", response_model=GetBook)
async def update_book(
    book_isbn: str,
    new_info: CreateBook,
    db: AsyncSession = Depends(get_db)
):
    if book_isbn:
        book_update = await BooksService.update_book(db, book_isbn, new_info)
        if book_update is None:
            raise HTTPNotFound

        return book_update
    else:
        raise HTTPBadRequest

