from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Criar engine assíncrona do banco de dados
# O connect_args={"check_same_thread": False} só é necessário para o SQLite
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {}
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
