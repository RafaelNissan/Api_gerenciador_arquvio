# API Gerenciador de Arquivos

API desenvolvida com FastAPI para gerenciamento de arquivos.

## Estrutura do Projeto

```
Api_gerenciador_arquvio/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação principal FastAPI
│   ├── api/                 # Endpoints da API
│   │   └── __init__.py
│   ├── core/                # Configurações centrais
│   │   ├── __init__.py
│   │   ├── config.py        # Configurações da aplicação
│   │   └── database.py      # Configuração do banco de dados
│   ├── models/              # Modelos do banco de dados (SQLAlchemy)
│   │   └── __init__.py
│   ├── schemas/             # Schemas Pydantic (validação)
│   │   └── __init__.py
│   └── services/            # Lógica de negócio
│       └── __init__.py
├── venv/                    # Ambiente virtual
├── .env                     # Variáveis de ambiente (criar a partir do .env.example)
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
└── requirements.txt         # Dependências do projeto
```

## Configuração do Ambiente

### 1. Ativar o ambiente virtual

```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure as variáveis:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações.

### 4. Executar a aplicação

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: `http://localhost:8000`

Documentação interativa (Swagger): `http://localhost:8000/docs`

Documentação alternativa (ReDoc): `http://localhost:8000/redoc`

## Próximos Passos

1. Criar modelos no diretório `app/models/`
2. Criar schemas no diretório `app/schemas/`
3. Criar rotas no diretório `app/api/`
4. Criar serviços no diretório `app/services/`
5. Configurar Alembic para migrações de banco de dados

## Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para banco de dados
- **Alembic**: Gerenciamento de migrações
- **Pydantic**: Validação de dados
- **Uvicorn**: Servidor ASGI
- **Passlib**: Hash de senhas
- **Python-JOSE**: Tokens JWT
- **Aiosmtplib**: Envio assíncrono de emails
