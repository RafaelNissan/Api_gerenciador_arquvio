import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.models.file import FileModel

UPLOAD_ROOT = Path("uploads")

async def get_user_upload_path(user_id: int) -> Path: 
    """Retorna o caminho do diretório de uploads do usuário."""
    return (UPLOAD_ROOT / str(user_id)).resolve()

async def ensure_user_directory(user_id: int) -> Path:
    """Garante que o diretório do usuário exista."""
    user_dir = await get_user_upload_path(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

async def save_user_file(db: AsyncSession, user_id: int, file: UploadFile, custom_filename: Optional[str] = None) -> str:
    """Salva um arquivo na pasta do usuário e registra no banco de dados."""
    user_dir = await ensure_user_directory(user_id)
    filename = custom_filename or file.filename
    file_path = user_dir / filename
    
    if file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um arquivo chamado '{filename}'!"
        )
    
    # 1. Salvar arquivo físico
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar arquivo físico: {str(e)}"
        )

    # 2. Registrar no Banco de Dados
    try:
        # Obter tamanho do arquivo
        file_stats = file_path.stat()
        
        db_file = FileModel( # Registra o arquivo no banco de dados
            filename=filename, # Nome do arquivo
            content_type=file.content_type, # Tipo do arquivo
            size=file_stats.st_size, # Tamanho do arquivo
            user_id=user_id # ID do usuário
        )
        db.add(db_file) # Adiciona o arquivo ao banco de dados
        await db.commit() # Comita a transação
        return filename # Retorna o nome do arquivo
    except Exception as e:
        # Se falhar no banco, deleta o arquivo físico para manter consistência
        if file_path.exists(): # Verifica se o arquivo existe
            file_path.unlink() # Deleta o arquivo
        await db.rollback() # Desfaz a transação
        raise HTTPException( # Lança uma exceção
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar no banco: {str(e)}"
        )

async def list_user_files(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> List[FileModel]:
    """Lista arquivos do usuário consultando o banco de dados."""
    result = await db.execute(
        select(FileModel) # Seleciona todos os arquivos do usuario
        .filter(FileModel.user_id == user_id) # Filtra pelo id do usuario
        .order_by(FileModel.upload_date.desc()) # Ordena pelo data de upload
        .offset(skip) # Pula os arquivos
        .limit(limit) # Limita a quantidade de arquivos
    )
    return result.scalars().all()

async def get_user_file_path(user_id: int, filename: str) -> Optional[Path]:
    """Retorna o caminho seguro de um arquivo do usuário."""
    user_dir = await get_user_upload_path(user_id)
    file_path = (user_dir / filename).resolve()
    
    if not str(file_path).startswith(str(user_dir)):
        return None
        
    return file_path

async def delete_user_file(db: AsyncSession, user_id: int, filename: str) -> bool:
    """Deleta um arquivo do banco e do sistema de arquivos."""
    # 1. Remover do Banco
    result = await db.execute(
        delete(FileModel).where(FileModel.user_id == user_id, FileModel.filename == filename) # Deleta o arquivo do banco
    )
    await db.commit()
    
    if result.rowcount == 0: # Verifica se o arquivo foi deletado
        return False

    # 2. Remover do Sistema de Arquivos
    file_path = await get_user_file_path(user_id, filename) # Pega o caminho do arquivo
    if file_path and file_path.exists(): # Verifica se o arquivo existe
        file_path.unlink() # Deleta o arquivo
        return True
    
    return True
