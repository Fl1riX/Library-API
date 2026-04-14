from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class CreateReader(BaseModel):
    full_name: str = Field(max_length=150)
    email: str = Field(max_length=100)
    phone: str = Field(max_length=20)
    password: str = Field(max_length=120, min_length=8)
    
    model_config = ConfigDict(extra='forbid')

class LoginReader(BaseModel):
    login: str = Field(max_length=50, min_length=5)
    password: str = Field(max_length=255, min_length=8)
    
    model_config = ConfigDict(extra='forbid')

class GetReader(CreateReader):
    id: int
    registration_date: datetime
    
    class Config:
        from_attributes = True
        
class ChangePassword(BaseModel):
    password: str = Field(max_length=120)
    new_password: str = Field(max_length=120)
    
    model_config = ConfigDict(extra="forbid")
