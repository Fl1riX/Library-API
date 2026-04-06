from src.infrastructure.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import Integer, DateTime, String, Boolean, ForeignKey
from datetime import datetime, timezone, timedelta

class Readers(Base):
    __tablename__ = "readers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    registration_date: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    password: Mapped[str] = mapped_column(String(120))

class Books(Base):
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False, index=True)
    year: Mapped[datetime] = mapped_column(Integer) 
    pages: Mapped[int] = mapped_column(Integer) 
    avalible: Mapped[bool] = mapped_column(Boolean)

    @validates("year")
    def validates_year(self, key, value):
        if value > 1000 and value <=2100:
            return value
        else:
            raise ValueError("Не верный год")
    
    @validates("pages")
    def validates_pages(self, key, value):
        if value > 0:
            return value
        else:
            raise ValueError("Количество страниц должно быть больше 0")

class Loans(Base):
    __tablename__ = "loans"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    reader_id: Mapped[int] = mapped_column(ForeignKey("readers.id"))
    load_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    return_date: Mapped[datetime] = mapped_column(DateTime, default=None)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc) + timedelta(days=14))