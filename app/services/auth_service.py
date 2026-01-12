from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.models.user import User
from app.schemas.user import UserCreate
from app.core import security
from app.core.config import settings

async def register_new_user(db: AsyncSession, user_in: UserCreate) -> User:
    result = await db.execute(select(User).filter(User.username == user_in.username))
    user = result.scalars().first()
    
    if user:
        raise HTTPException(
            status_code=400,
            detail="O usuário já existe.",
        )
    
    db_user = User(
        username=user_in.username,
        hashed_password=security.get_password_hash(user_in.password),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, form_data: OAuth2PasswordRequestForm) -> dict:
    result = await db.execute(select(User).filter(User.username == form_data.username))
    user = result.scalars().first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Usuário inativo")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
