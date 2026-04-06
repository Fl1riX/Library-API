from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime

from src.domain.services.exceptions import NotFoundException, ConflictException
from src.infrastructure.db.models import Loans
from src.shared.schemas.loans_schema import CreateLoan

class LoansService:
    
    @classmethod
    async def get_loan_by_id(cls, loan_id: int, db: AsyncSession):
        result = await db.execute(select(Loans).where(
            Loans.id == loan_id
        ))
        loan = result.scalars().first()
        if not loan:
            raise NotFoundException
        return loan
    
    @staticmethod
    async def get_loans(db: AsyncSession):
        result = await db.execute(select(Loans))
        loans = result.scalars().all()
        if not loans:
            raise NotFoundException
        return loans
    
    @staticmethod
    async def search_loan(
        db: AsyncSession,
        book_id: int | None = None,
        reader_id: int | None = None,
        loan_date: datetime | None = None,
        return_date: datetime | None = None,
        due_date: datetime | None = None,
        skip: int = 10,
        limit: int = 20
    ):
        query = select(Loans)
        count_query = select(func.count().select_from(Loans))
        
        if book_id:
            query = query.where(Loans.book_id.ilike(f"%{book_id}%"))
            count_query = count_query.where(Loans.book_id.ilike(f"%{book_id}%"))
        if reader_id:
            query = query.where(Loans.reader_id.ilike(f"%{reader_id}%"))
            count_query = count_query.where(Loans.reader_id.ilike(f"%{reader_id}%"))
        if loan_date:
            query = query.where(Loans.load_date.ilike(f"%{loan_date}%"))
            count_query = count_query.where(Loans.load_date.ilike(f"%{loan_date}%"))
        if return_date:
            query = query.where(Loans.return_date.ilike(f"%{return_date}%"))
            count_query = count_query.where(Loans.return_date.ilike(f"%{return_date}%"))
        if due_date:
            query = query.where(Loans.due_date.ilike(f"%{due_date}%"))
            count_query = count_query.where(Loans.due_date.ilike(f"%{due_date}%"))
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        loans = result.scalars().all()
        if not loans:
            raise NotFoundException
        
        total = await db.scalar(count_query)
        if total == 0:
            raise NotFoundException
        
        return loans, total
    
    @classmethod
    async def update_loan(
        cls,
        db: AsyncSession,
        new_loan: CreateLoan,
        loan_id: int
    ):
        loan = await cls.get_loan_by_id(loan_id, db)
        
        for key, value in new_loan.model_dump().items():
            if hasattr(loan, key):
                setattr(loan, key, value)
        
        updated_loan = Loans(**loan)
        
        try:
            db.add(updated_loan)
            await db.commit()
            await db.refresh(updated_loan)
            return updated_loan
        except Exception:
            await db.rollback()
            raise
        
    @classmethod
    async def delete_loan(cls, db: AsyncSession, loan_id: int):
        loan = await cls.get_loan_by_id(loan_id, db)
        
        try:
            await db.delete(loan)
            await db.commit()
            return True
        except Exception:
            await db.rollback()
            raise
    
    @classmethod
    async def find_loan(
        cls, 
        book_id: int, 
        reader_id: int, 
        loan_date: datetime,
        db: AsyncSession
    ):
        result = await db.execute(select(Loans).where(
            Loans.book_id == book_id,
            Loans.reader_id == reader_id,
            Loans.load_date == loan_date
        ))
        loan = result.scalars().first()
        return loan
    
    @classmethod
    async def create_loan(cls, loan: CreateLoan, db: AsyncSession):
        exists = await cls.find_loan(loan.book_id, loan.reader_id, loan.loan_date, db)
        if exists:
            raise ConflictException
        new_loan = Loans(**loan.model_dump())
        try:
            if loan:
                db.add(new_loan)
                await db.commit()
                await db.refresh(new_loan)
        except Exception:
            await db.rollback()
            raise