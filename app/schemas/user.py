from pydantic import BaseModel, Field, AliasChoices
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class FileOut(BaseModel):
    filename: str
    size: int
    # Suporta tanto o antigo 'last_modified' quanto o novo 'upload_date' do banco
    last_modified: datetime = Field(validation_alias=AliasChoices('upload_date', 'last_modified'))

    class Config:
        from_attributes = True
