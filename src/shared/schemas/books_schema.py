from pydantic import BaseModel, Field, ConfigDict

class CreateBook(BaseModel):
    """  
    Схема создания книги
        title: str = max_length=200
        author: str = max_length=100
        isbn: str = max_length=13, min_length=13
        year: int
        pages: int
        avalible: bool
    """
    title: str = Field(max_length=200)
    author: str = Field(max_length=100)
    isbn: str = Field(max_length=13, min_length=13)
    year: int
    pages: int
    avalible: bool
    
    model_config = ConfigDict(extra="forbid")

class GetBook(CreateBook):
    """  
    Схема ответа с информацией о книге
        id: int
        title: str = max_length=200
        author: str = max_length=100
        isbn: str = max_length=13, min_length=13
        year: int
        pages: int
        avalible: bool
    """
    
    id: int
    
    class Config:
        from_attributes = True
        
