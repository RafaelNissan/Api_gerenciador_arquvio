import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import UploadFile, HTTPException, status

UPLOAD_ROOT = Path("uploads")

async def get_user_upload_path(user_id: int) -> Path:
    """Retorna o caminho do diretório de uploads do usuário."""
    return (UPLOAD_ROOT / str(user_id)).resolve()

async def ensure_user_directory(user_id: int) -> Path:
    """Garante que o diretório do usuário exista."""
    user_dir = await get_user_upload_path(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir

async def save_user_file(user_id: int, file: UploadFile, custom_filename: Optional[str] = None) -> str:
    """Salva um arquivo na pasta do usuário com verificação de duplicata."""
    user_dir = await ensure_user_directory(user_id)
    filename = custom_filename or file.filename
    file_path = user_dir / filename
    
    if file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Doidão, já existe um arquivo chamado '{filename}'! Tente outro nome."
        )
    
    # Operação de I/O em bloco, mas em uma função assíncrona para compatibilidade
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        return filename

async def list_user_files(user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Lista arquivos do usuário com suporte a paginação."""
    user_dir = await ensure_user_directory(user_id)
    all_files = []
    for f in user_dir.iterdir():
        if f.is_file():
            stats = f.stat()
            all_files.append({
                "filename": f.name,
                "size": stats.st_size,
                "last_modified": datetime.fromtimestamp(stats.st_mtime)
            })
    
    # Ordenar por data de modificação (mais recentes primeiro)
    all_files.sort(key=lambda x: x["last_modified"], reverse=True)
    
    # Aplicar paginação
    return all_files[skip : skip + limit]

async def get_user_file_path(user_id: int, filename: str) -> Optional[Path]:
    """Retorna o caminho seguro de um arquivo do usuário."""
    user_dir = await ensure_user_directory(user_id)
    file_path = (user_dir / filename).resolve()
    
    # Prevenção de Path Traversal
    if not str(file_path).startswith(str(user_dir)):
        return None
        
    return file_path

async def delete_user_file(user_id: int, filename: str) -> bool:
    """Deleta um arquivo do usuário de forma segura."""
    file_path = await get_user_file_path(user_id, filename)
    if file_path and file_path.exists():
        file_path.unlink()
        return True
    return False
