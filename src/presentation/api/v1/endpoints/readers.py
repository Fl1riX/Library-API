from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.infrastructure.db.database import get_db
from src.domain.services.readers_service import ReadersService
from src.presentation.api.v1.exceptions import HTTPNotFound, HTTPBadRequest
from src.shared.schemas.readers_schema import CreateReader, GetReader
from src.domain.services.exceptions import NotFoundException

router = APIRouter(prefix="/readers", tags=["Читатели"])

@router.get("/{reader_id}", response_model=GetReader)
async def get_reader(
    reader_id: int,
    db: AsyncSession = Depends(get_db)
):
    if reader_id:
        reader = await ReadersService.get_reader_by_id(reader_id, db)
        if reader is None:
            raise HTTPNotFound("User was not found")
        return reader
    else:
        raise HTTPBadRequest

@router.get("/")
async def get_readers(
    db: AsyncSession = Depends(get_db)
):
    readers = await ReadersService.get_all_readers(db)
    if not readers:
        raise HTTPNotFound
    return readers

@router.get("/search")
async def search_user(
    db: AsyncSession = Depends(get_db),
    full_name: str | None = Query(None, description="ФИО пользователя"),
    email: str | None = Query(None, description="email пользователя"),
    phone: str | None = Query(None, description="Телефонный номер пользователя"),
    registration_date: datetime | None = Query(None, description="Дата регистрации"),
    skip: int = Query(10, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    try:
        readers, total = await ReadersService.search_reader(
            db, full_name, email,phone, registration_date, skip, limit
        )
    except NotFoundException:
        raise HTTPNotFound("Readers was not found")
    
    return readers, total

@router.delete("/{reader_id}")
async def delete_reader(
    reader_id: int,
    db: AsyncSession = Depends(get_db)
):
    if reader_id:
        try:
            await ReadersService.delete_reader(reader_id, db)
        except NotFoundException:
            raise HTTPNotFound

        return {"success": True}
    else:
        raise HTTPBadRequest

@router.put("/{reader_id}")
async def update_reader(
    reader_id: int,
    new_reader: CreateReader,
    db: AsyncSession = Depends(get_db)
):
    if reader_id:
        try: 
            updated_reader = await ReadersService.update_user(reader_id, new_reader, db)
        except NotFoundException:
            raise HTTPNotFound

        return updated_reader
    else:
        raise HTTPBadRequest