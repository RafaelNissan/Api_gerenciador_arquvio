from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path
import os
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.services import file_service
from app.schemas.user import FileOut
from app.core.database import get_db

router = APIRouter()

# Configurações de Segurança
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.txt', '.docx', '.xlsx', '.zip'} # Tipos de arquivos permitidos
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB Tamanho maximo do arquivo

def sanitize_filename(filename: str) -> str:
    """Sanitiza nome do arquivo para evitar path traversal."""
    return Path(filename).name

@router.get("/", response_model=List[FileOut])
async def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Lista arquivos do usuário com paginação e metadados."""
    return await file_service.list_user_files(db, current_user.id, skip=skip, limit=limit)

@router.get("/{filename}")
async def download_file( 
    filename: str, # Nome do arquivo
    current_user: User = Depends(deps.get_current_user) # Usuario logado
):
    """Baixa um arquivo do usuário com validação de escopo."""
    safe_filename = sanitize_filename(filename) # Sanitiza nome do arquivo
    file_path = await file_service.get_user_file_path(current_user.id, safe_filename) # Caminho do arquivo
    
    if not file_path or not file_path.exists(): # Verifica se o arquivo existe
        raise HTTPException( # Lança exceção se o arquivo não existir
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado"
        )
    
    # Dupla verificação de segurança (Cross-check)
    user_dir = await file_service.get_user_upload_path(current_user.id) # Caminho do arquivo do usuario
    try:
        file_path.relative_to(user_dir)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, # Lança exceção se o arquivo não existir
            detail="Acesso negado"
        )
    
    return FileResponse( # Retorna o arquivo
        path=str(file_path), # Caminho do arquivo
        filename=safe_filename, # Nome do arquivo
        media_type="application/octet-stream" # Tipo do arquivo
    )

@router.delete("/{filename}")
async def delete_file(
    filename: str, # Nome do arquivo
    db: AsyncSession = Depends(get_db), # Sessão do banco de dados
    current_user: User = Depends(deps.get_current_user) # Usuario logado
):
    """Deleta um arquivo do usuário logado."""
    safe_filename = sanitize_filename(filename) # Sanitiza nome do arquivo
    success = await file_service.delete_user_file(db, current_user.id, safe_filename) # Deleta o arquivo
    
    if not success: # Verifica se o arquivo foi deletado
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo não encontrado ou erro ao deletar"
        )
    
    return {"message": f"Arquivo {safe_filename} deletado com sucesso"}

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...), # Arquivo a ser enviado
    db: AsyncSession = Depends(get_db), # Sessão do banco de dados
    current_user: User = Depends(deps.get_current_user) # Usuario logado
):
    """Upload de arquivo com validações de tamanho, extensão e segurança."""
    
    # Validar extensão antes de ler o conteúdo (Performance)
    file_ext = os.path.splitext(file.filename)[1].lower() # Extensão do arquivo
    if file_ext not in ALLOWED_EXTENSIONS: # Verifica se a extensão do arquivo é permitida
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não permitido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Ler conteúdo para validar tamanho
    contents = await file.read() # Leitura do arquivo
    if len(contents) > MAX_FILE_SIZE: # Verifica se o arquivo é maior que o tamanho maximo
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo muito grande. Máximo: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Sanitizar nome
    safe_filename = sanitize_filename(file.filename) # Sanitiza nome do arquivo
    
    try:
        # Voltar o cursor para o início antes de salvar através do serviço
        await file.seek(0)
        filename = await file_service.save_user_file(db, current_user.id, file, safe_filename) # Salva o arquivo
        
        return { # Retorna o arquivo
            "message": "Arquivo enviado com sucesso",
            "filename": filename,
            "size": len(contents),
            "url": f"/api/files/{filename}"
        }
    except HTTPException:
        # Re-lança exceções do FastAPI (como a de duplicata)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )