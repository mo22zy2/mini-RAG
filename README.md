<div align="center">
  <h1>Mini RAG</h1>
  <p><strong>A lightweight, full-stack Retrieval-Augmented Generation pipeline</strong></p>

  <p>
    <img src="https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/Qdrant-1.10-6600FF?logo=qdrant" alt="Qdrant">
    <img src="https://img.shields.io/badge/Python-3.8+-3776AB?logo=python" alt="Python">
    <img src="https://img.shields.io/badge/Ollama-000?logo=ollama" alt="Ollama">
    <img src="https://img.shields.io/badge/LangChain-0.1.20-121212?logo=langchain" alt="LangChain">
    <img src="https://img.shields.io/badge/Alembic-1.14-EE0000?logo=alembic" alt="Alembic">
  </p>
</div>

---

## Overview

**Mini RAG** is a complete, production-ready RAG (Retrieval-Augmented Generation) backend. It ingests documents, splits them into chunks, generates embeddings, stores them in a vector database, and answers questions using an LLM — all behind a clean FastAPI interface. Works with OpenAI, Cohere, **or local models via Ollama**.

| Stage | Status |
|-------|--------|
| Document Upload | ✅ |
| Text Chunking | ✅ |
| Embedding Generation | ✅ |
| Vector DB Indexing (Qdrant, pgvector) | ✅ |
| Semantic Search | ✅ |
| RAG Answer Generation | ✅ |
| Multi-Provider LLM | ✅ |
| Template Parser Integration | ✅ |

> **Latest**: Added pgvector support alongside Qdrant. Switched from Cohere to OpenAI-compatible Ollama embeddings. Vector index type configurable via `VECTOR_DB_INDEX_TYPE` (HNSW / IVFFLAT). Added `EUCLIDEAN` distance method.

---

## Features

- **File Upload** — Upload TXT and PDF files (configurable max size)
- **Text Chunking** — Custom line-based splitter with adjustable chunk size
- **Embedding Generation** — Support for OpenAI, Cohere, and Ollama embedding models
- **Vector Database** — Qdrant and pgvector (PostgreSQL) with configurable index type (HNSW / IVFFLAT) and distance method (cosine, dot, euclidean)
- **Semantic Search** — Find relevant document chunks by meaning, not keywords
- **RAG Answers** — Generate contextual answers using retrieved chunks + LLM prompt templates
- **Pluggable Providers** — Swap between OpenAI, Cohere, or Ollama for both generation and embedding
- **Local-First** — Run entirely offline using local models via Ollama (no API keys required)
- **Multi-Language Templates** — Prompt templates in English and Arabic (easily extensible)
- **Project Isolation** — All data (files, chunks, vectors) grouped by `project_id`
- **Reset Support** — Re-process or re-index documents without duplication
- **Async Throughout** — FastAPI + SQLAlchemy (async) + asyncpg for non-blocking I/O
- **Dockerized DB** — pgvector (PostgreSQL 18 with vector extension) runs in a container via docker-compose
- **Alembic Migrations** — Schema versioning with auto-generation support

---

## Architecture

```
                    ┌─────────────────────────────┐
                    │       Client / User          │
                    └──────────┬──────────────────┘
                               │
                      ┌────────▼─────────┐
                      │   FastAPI Server   │
                      │  (Uvicorn + ASGI)  │
                      └────┬──────┬───────┘
                           │      │
                ┌──────────▼┐  ┌──▼──────────────┐
                │ PostgreSQL  │  │  PostgreSQL     │
                │ (asyncpg)   │  │  pgvector       │
                │ (metadata)  │  │  (vectors)      │
                └─────────────┘  └─────────────────┘
                      │               │
            ┌──────────▼───────────────▼──────────┐
            │    LLM Providers (OpenAI/Cohere/Ollama)│
            │  ┌──────────────────────────────┐   │
            │  │  Embedding Model             │   │
            │  │  Generation Model            │   │
            │  └──────────────────────────────┘   │
            └─────────────────────────────────────┘
```

### Pipeline Flow

```
Upload ──► Validate ──► Save to Disk ──► Asset Record (PostgreSQL)
                                                 │
                                                 ▼
Process ──► Loader ──► Split Text ──► Chunks (PostgreSQL, with metadata)
                                                 │
                                                 ▼
Index ──► Embed Chunks ──► Store Vectors ──► pgvector / Qdrant
                                                 │
                                                 ▼
Search/Answer ──► Embed Query ──► Vector Search ──► LLM Generation
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI + Uvicorn |
| Database | PostgreSQL 17 (asyncpg) + pgvector |
| Vector Database | pgvector / Qdrant |
| Document Parsing | LangChain (TextLoader, PyMuPDFLoader) |
| Text Splitting | Custom line-based splitter |
| Embedding | OpenAI / Cohere / Ollama |
| Generation | OpenAI / Cohere / Ollama |
| Configuration | Pydantic Settings + `.env` |
| Containerization | Docker (PostgreSQL) |
| Migrations | Alembic |

---

## Quick Start

### Prerequisites

- Python 3.8+
- Docker & Docker Compose

### 1. Start PostgreSQL (with pgvector)

```bash
cd docker
docker-compose up -d
```

### 2. Apply database migrations

```bash
cd src/models/db_schemas/mini_rag
alembic upgrade head
```

### 3. Install dependencies

```bash
cd src
pip install -r requirments.txt
```

> **Ubuntu**: If `psycopg2` fails, run `sudo apt install libpq-dev gcc python3-dev` first.

### 4. Configure environment

Copy `src/.env.example` to `src/.env` and customize:

```env
APP_NAME="mini-RAG"
APP_VERSION="0.1"

FILE_ALLOWED_TYPES=["text/plain","application/pdf"]
FILE_MAX_SIZE=16
FILE_DEFAULT_CHUNK_SIZE=512000

# PostgreSQL
POSTGRES_USERNAME="postgres"
POSTGRES_PASSWORD=""
POSTGRES_HOST="localhost"
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE="mini_rag"

GENERATION_BACKEND="OPENAI"
EMBEDDING_BACKEND="OPENAI"

OPENAI_API_KEY=""
OPENAI_BASE_URL=""
COHERE_API_KEY=""

GENERATION_MODEL_ID="gpt-4o-mini"
EMBEDDING_MODEL_ID="text-embedding-3-small"
EMBEDDING_MODEL_SIZE=1536

INPUT_DEFAULT_MAX_CHARS=1024
GENERATION_DEFAULT_MAX_TOKENS=200
GENERATION_DEFAULT_TEMPERATURE=0.1

VECTOR_DB_BACKEND="PGVECTOR"
VECTOR_DB_PATH="qdrant_db"
VECTOR_DB_DISTANCE_METHOD="cosine"
VECTOR_DB_PGVEC_INDEX_THRESHOLD=150
VECTOR_DB_INDEX_TYPE="IVFFLAT"

DEFAULT_LANGUAGE="en"
```

### 5. Run the server

```bash
cd src
uvicorn main:app --reload
```

The API is available at `http://localhost:8000`.

---

## API Reference

### Health

#### `GET /api/v1/`

Returns the application name and version.

```json
{
  "message": "Hello Landing Page!",
  "app_name": "mini-RAG",
  "app_version": "0.1"
}
```

---

### Ingestion

#### `POST /api/v1/data/upload/{project_id}`

Upload a file (TXT or PDF) to a project.

| Parameter | Type | Description |
|-----------|------|-------------|
| `project_id` | path | Project identifier (alphanumeric) |
| `file` | form-data | The file to upload |

**Response:**
```json
{
  "signal": "File upload Succeed",
  "file_id": "abc123def456_my_document.pdf"
}
```

#### `POST /api/v1/data/process/{project_id}`

Split an uploaded file into overlapping text chunks.

**Request body:**
```json
{
  "file_id": "abc123def456_my_document.pdf",
  "chunck_size": 100,
  "overlap_size": 20,
  "do_reset": 0
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `file_id` | string | — | Specific file to process (omit to process all) |
| `chunck_size` | int | 100 | Chunk size in characters |
| `overlap_size` | int | 20 | Overlap between consecutive chunks |
| `do_reset` | int | 0 | Set to `1` to delete existing chunks first |

**Response:**
```json
{
  "signal": "File Processing SUCESS",
  "inserted_chunks": 15,
  "processed_files": 1
}
```

---

### Vector Indexing

#### `POST /api/v1/nlp/index/push/{project_id}`

Embed all chunks for a project and store them in Qdrant.

**Request body:**
```json
{
  "do_reset": 0
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `do_reset` | int | 0 | Set to `1` to reset the vector collection before indexing |

**Response:**
```json
{
  "signal": "Done inserting into Vector DB",
  "inserted_items_count": 15
}
```

#### `GET /api/v1/nlp/index/info/{project_id}`

Retrieve information about a project's vector collection.

**Response:**
```json
{
  "signal": "Vector DB Collection Retrived",
  "collection_info": { ... }
}
```

---

### Search & Generation

#### `POST /api/v1/nlp/index/search/{project_id}`

Semantic search: find relevant chunks for a query.

**Request body:**
```json
{
  "text": "What is this document about?",
  "limit": 5
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | string | — | The search query |
| `limit` | int | 5 | Maximum number of results |

**Response:**
```json
{
  "signal": "Done searching in Vector DB",
  "results": [
    {
      "text": "...",
      "score": 0.89,
      ...
    }
  ]
}
```

#### `POST /api/v1/nlp/index/answer/{project_id}`

Full RAG pipeline: search relevant chunks and generate an answer using the configured LLM.

**Request body:**
(Same as search — `text` and `limit`)

**Response:**
```json
{
  "signal": "Done generating The RAG Answer",
  "answer": "The document discusses...",
  "full_prompt": "...",
  "chat_history": [...]
}
```

---

## Project Structure

```
mini_RAG/
├── docker/
│   ├── docker-compose.yml          # pgvector + MongoDB containers
│   ├── .env                        # Docker credentials
│   └── .env.example
├── src/
│   ├── main.py                     # FastAPI entry point + startup wiring
│   ├── .env                        # Environment configuration
│   ├── requirments.txt             # Python dependencies
│   ├── helpers/
│   │   └── config.py               # Settings via pydantic-settings
│   ├── routes/
│   │   ├── base.py                 # GET /api/v1/ health check
│   │   ├── data.py                 # Upload & process endpoints
│   │   ├── nlp.py                  # Index, search & answer endpoints
│   │   └── schemes/
│   │       ├── data.py             # Process request schema
│   │       └── nlp.py              # Push & search request schemas
│   ├── controllers/
│   │   ├── BaseController.py       # Shared utilities (paths, random strings)
│   │   ├── DataController.py       # File validation & naming
│   │   ├── ProjectController.py    # Project directory management
│   │   ├── ProccesController.py    # LangChain loading & chunking
│   │   └── NLPController.py        # Embedding, vector DB ops, RAG pipeline
│   ├── models/
│   │   ├── BaseDataModel.py        # Base SQLAlchemy model
│   │   ├── ProjectModel.py         # Project CRUD (SQLAlchemy)
│   │   ├── ChunkModel.py           # Chunk CRUD (SQLAlchemy)
│   │   ├── AssetModel.py           # File asset CRUD (SQLAlchemy)
│   │   ├── db_schemas/
│   │   │   └── mini_rag/
│   │   │       ├── alembic/        # Migration scripts
│   │   │       ├── schemes/
│   │   │       │   ├── project.py  # Project ORM model
│   │   │       │   ├── data_chunks.py  # Chunk + RetrivedDocument ORM models
│   │   │       │   └── asset.py    # Asset ORM model
│   │   │       └── alembic.ini     # Alembic config
│   │   └── enums/
│   │       ├── ProcessingEnum.py   # File extension types
│   │       ├── DataBaseEnum.py     # Collection names (legacy)
│   │       ├── AssetTypeEnum.py    # Asset type constants
│   │       └── response_enums.py   # API response signals
│   ├── stores/
│   │   ├── llm/
│   │   │   ├── LLMInterface.py     # Abstract LLM provider
│   │   │   ├── LLMEnums.py         # Provider & role enums
│   │   │   ├── LLMProviderFactory.py
│   │   │   └── providers/
│   │   │       ├── OpenAIProvider.py
│   │   │       └── CoHereProvider.py
│   │   ├── vectordb/
│   │   │   ├── VectortDBInterface.py
│   │   │   ├── VectorDBProviderFactory.py
│   │   │   ├── VectorDBEnums.py
│   │   │   └── providers/
│   │   │       └── QdrantDBProvider.py
│   │   └── templates/
│   │       ├── template_parser.py  # Prompt template parser
│   │       └── locales/
│   │           ├── en/rag.py       # English RAG prompts
│   │           └── ar/rag.py       # Arabic RAG prompts
│   └── assets/files/               # Uploaded file storage
└── AGENT.md
```

---

## Provider System

Mini RAG uses a clean factory/interface pattern for both LLMs and vector databases.

### LLM Providers

| Provider | Generation | Embedding |
|----------|-----------|-----------|
| **OpenAI** | ✅ GPT models | ✅ text-embedding-* |
| **Cohere** | ✅ Command models | ✅ embed-* models |
| **Ollama** | ✅ Any GGUF model | ✅ Any embedding model |

Configure via `GENERATION_BACKEND` and `EMBEDDING_BACKEND` in `.env`.

> **Ollama**: Point `OPENAI_BASE_URL` to your Ollama server (e.g. `http://localhost:11434/v1`) and use any Ollama model as `GENERATION_MODEL_ID` / `EMBEDDING_MODEL_ID`. No API keys needed.

### Vector DB Providers

| Provider | Status |
|----------|--------|
| **Qdrant** | ✅ Fully supported |
| **pgvector** (PostgreSQL) | ✅ Fully supported |

Configure via `VECTOR_DB_BACKEND` in `.env`. For pgvector, index type (`HNSW` / `IVFFLAT`) and distance method (`cosine`, `dot`, `euclidean`) are configurable.

### Template System

RAG prompts are defined as modular templates in `stores/templates/locales/{lang}/rag.py`. Currently supports:
- **English** (`en`)
- **Arabic** (`ar`)

Add a new language by creating a new locale directory and implementing the prompt templates.

---

## Recent Changes

### v0.3 — pgvector Support & Search Fixes

- **pgvector**: Added full PostgreSQL vector support alongside Qdrant. New `PGVectorProvider` with configurable index type (HNSW / IVFFLAT) and distance methods (cosine, dot, euclidean)
- **Index type config**: `VECTOR_DB_INDEX_TYPE` env var to switch between HNSW and IVFFLAT without code changes
- **Search bug fix**: `search_vector_db_collection` returns `None` on failure instead of `False` — now properly caught by route's `is None` check
- **Embedding fix**: Cohere provider returns all embeddings (not just the first one)
- **Config path fix**: `env_file` resolved relative to `config.py` so it works from any working directory
- **chunk_order**: Column type changed from `String` to `Integer`
- **Metadata enrichment**: Chunk records now store `asset_id`, `file_name`, `project_id`, `chunk_order`

### v0.2 — PostgreSQL Migration & Bug Fixes

- **Database**: MongoDB → PostgreSQL 18 (asyncpg + SQLAlchemy 2.0 async)
- **Migrations**: Added Alembic for schema versioning
- **Models**: Rewrote `ProjectModel`, `ChunkModel`, `AssetModel` from Motor to SQLAlchemy ORM
- **Connection string**: Fixed bug using `POSTGRES_PASSWORD` instead of `POSTGRES_PORT`
- **Shutdown**: Fixed missing `await` on `engine.dispose()`
- **Config**: Made MongoDB fields optional, all nullable fields use `Optional[...]`
- **Schemas**: Fixed `relationship()` case, added `default`+`server_default` to `updated_at`
- **Type fixes**: `ObjectId()` removed from PostgreSQL int PKs, `chunk_metadata` JSON-serialized, `chunk_order`/`asset_size` cast to string
- **Imports**: Removed dead `bson`/`pymongo` imports, fixed broken module paths

---

## Dependencies

```
fastapi==0.110.2
uvicorn[standard]==0.29.0
python-multipart==0.0.9
python-dotenv==1.0.1
pydantic-settings==2.2.1
aiofiles==23.2.1
langchain==0.1.20
PyMuPDF==1.24.3
openai==1.75.0
cohere==5.5.8
qdrant-client==1.10.1
sqlalchemy
asyncpg
alembic==1.14
psycopg2==2.9.10
```

---

## Roadmap

- [x] Document upload (TXT, PDF)
- [x] Text chunking with LangChain
- [x] PostgreSQL storage for projects, chunks & assets (SQLAlchemy)
- [x] Embedding generation (OpenAI / Cohere / Ollama)
- [x] Vector database indexing (Qdrant + pgvector)
- [x] Semantic search
- [x] RAG answer generation
- [x] Alembic database migrations
- [x] pgvector support
- [x] Configurable index type (HNSW / IVFFLAT)
- [x] Metadata enrichment for chunks
- [ ] File type expansion (DOCX, Markdown, HTML)
- [ ] Authentication & rate limiting
- [ ] Streaming responses
- [ ] Web UI / playground
- [ ] Frontend for RAG (chat interface)
- [ ] Hybrid search (vector + keyword)
- [ ] Re-ranking (Cohere Rerank / cross-encoder)
- [ ] Query expansion
- [ ] Language auto-detection
- [ ] Cross-encoder reranking

---

## License

MIT
