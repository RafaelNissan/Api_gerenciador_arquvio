import asyncio
from app.core.database import engine, Base
from app.models import User, FileModel

async def init_db():
    print("Criando tabelas no banco de dados...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Tabelas criadas com sucesso!")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
