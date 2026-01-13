from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, Token, User as UserSchema
from app.services import auth_service

router = APIRouter()

# Registra um novo usuário no sistema
@router.post("/register", response_model=UserSchema)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registra um novo usuário no sistema."""
    return await auth_service.register_new_user(db, user_in)


# Autentica um usuário e retorna um token JWT
@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Autêntica um usuário e retorna um token JWT."""
    return await auth_service.authenticate_user(db, form_data)
