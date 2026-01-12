from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, Token, User as UserSchema
from app.services import auth_service

router = APIRouter()

@router.post("/register", response_model=UserSchema)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registra um novo usuário no sistema."""
    return auth_service.register_new_user(db, user_in)

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Autêntica um usuário e retorna um token JWT."""
    return auth_service.authenticate_user(db, form_data)
