from pydantic import BaseModel, Field, AliasChoices
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel): # Modelo base do usuario
    username: str # Nome do usuario

class UserCreate(UserBase): # Modelo de criacao do usuario
    password: str # Senha do usuario

class User(UserBase): # Modelo do usuario
    id: int # ID do usuario
    is_active: bool # Status do usuario

    class Config: # Configuracao do modelo
        from_attributes = True

class Token(BaseModel): # Modelo do token
    access_token: str # Token de acesso
    token_type: str # Tipo do token

class TokenData(BaseModel): # Modelo do token
    username: Optional[str] = None # Nome do usuario

class FileOut(BaseModel): # Modelo do arquivo
    filename: str # Nome do arquivo
    size: int # Tamanho do arquivo

    # Suporta tanto o antigo 'last_modified' quanto o novo 'upload_date' do banco
    last_modified: datetime = Field(validation_alias=AliasChoices('upload_date', 'last_modified')) # Data de upload do arquivo

    class Config: # Configuracao do modelo
        from_attributes = True 
