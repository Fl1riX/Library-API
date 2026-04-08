from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.infrastructure.db.database import get_db
from src.domain.services.loans_service import LoansService
from src.domain.services.exceptions import NotFoundException, ConflictException
from src.presentation.api.v1.exceptions import HTTPNotFound, HTTPConflict, HTTPBadRequest
from src.shared.schemas.loans_schema import GetLoan, CreateLoan

router = APIRouter(prefix="/loans", tags=["Выдачи"])

@router.get("/search")
async def search_loans(
    db: AsyncSession = Depends(get_db),
    book_id: int | None = Query(None, description="id книги"),
    reader_id: int | None = Query(None, description="id получателя"),
    loan_date: datetime | None = Query(None, description="Дата выдачи книги"),
    return_date: datetime | None = Query(None, description="Дата возврата книги"),
    due_date: datetime | None = Query(None, description="Дата, когда книга должна быть возвращена")
):
    try:
        loans, total = await LoansService.search_loan(
            db, book_id=book_id, reader_id=reader_id, loan_date=loan_date, 
            return_date=return_date, due_date=due_date
        )
    except NotFoundException:
        raise HTTPNotFound("Loans were not found")
    
    return loans, total

@router.get("/{loan_id}", response_model=GetLoan)
async def get_loan(
    loan_id: int,
    db: AsyncSession = Depends(get_db)
):
    if loan_id:
        try:
            loan = await LoansService.get_loan_by_id(loan_id, db)
        except NotFoundException:
            raise HTTPNotFound("Loan was not found")
        return loan
    else:
        raise HTTPBadRequest

@router.get("/", response_model=GetLoan)
async def get_loans(db: AsyncSession = Depends(get_db)):
    try:
        loans = await LoansService.get_loans(db)
    except NotFoundException:
        raise HTTPNotFound("Loans were not found")
    return loans

@router.put("/{looan_id}", response_model=GetLoan)
async def update_loan(
    loan_id: int,
    new_loan: CreateLoan,
    db: AsyncSession = Depends(get_db)
):
    if loan_id:
        try:
            updated_loan = await LoansService.update_loan(db, new_loan, loan_id)
        except NotFoundException:
            raise HTTPNotFound

        return updated_loan
    else:
        raise HTTPBadRequest

@router.delete("/{loan_id}")
async def delete_loan(
    loan_id: int,
    db: AsyncSession = Depends(get_db)
):
    if loan_id:
        try:
            await LoansService.delete_loan(db, loan_id)
        except NotFoundException:
            raise HTTPNotFound

        return {"success": True}
    raise HTTPBadRequest

@router.post("/")
async def create_loan(
    loan: CreateLoan,
    db: AsyncSession = Depends(get_db)
):
    if loan:
        try:
            new_loan = await LoansService.create_loan(loan, db)
        except ConflictException:
            raise HTTPConflict
        
        return new_loan
    else:
        raise HTTPBadRequest