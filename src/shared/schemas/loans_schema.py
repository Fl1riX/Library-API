from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CreateLoan(BaseModel):
    book_id: int 
    reader_id: int
    loan_date: datetime
    return_date: datetime
    due_date: datetime
    
    model_config = ConfigDict(extra="forbid")
    

class GetLoan(CreateLoan):
    id: int
    
    class Config:
        from_attributes = True