from pydantic_settings import BaseSettings
from typing import Optional

# BaseSettings é uma classe que ajuda a carregar as configurações do arquivo .env
class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Database
    # Se não houver DATABASE_URL no .env, usa o SQLite como fallback
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
