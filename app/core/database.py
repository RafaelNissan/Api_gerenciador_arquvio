from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Criar engine assíncrona do banco de dados
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Criar fábrica de sessões assíncronas
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False, 
    autocommit=False, 
    autoflush=False
)

# Base para os modelos
Base = declarative_base()


async def get_db():
    """Dependency assíncrona para obter sessão do banco de dados"""
    async with AsyncSessionLocal() as session:
        yield session
