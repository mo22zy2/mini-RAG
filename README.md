<div align="center">
  <h1>Mini RAG</h1>
  <p><strong>A lightweight, full-stack Retrieval-Augmented Generation pipeline</strong></p>

  <p>
    <img src="https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/MongoDB-7-47A248?logo=mongodb" alt="MongoDB">
    <img src="https://img.shields.io/badge/Qdrant-1.10-6600FF?logo=qdrant" alt="Qdrant">
    <img src="https://img.shields.io/badge/Cohere-395C8C?logo=cohere" alt="Cohere">
    <img src="https://img.shields.io/badge/OpenAI-412991?logo=openai" alt="OpenAI">
    <img src="https://img.shields.io/badge/Python-3.8+-3776AB?logo=python" alt="Python">
    <img src="https://img.shields.io/badge/LangChain-0.1.20-121212?logo=langchain" alt="LangChain">
  </p>
</div>

---

## Overview

**Mini RAG** is a complete, production-ready RAG (Retrieval-Augmented Generation) backend. It ingests documents, splits them into chunks, generates embeddings, stores them in a vector database, and answers questions using an LLM — all behind a clean FastAPI interface.

| Stage | Status |
|-------|--------|
| Document Upload | ✅ |
| Text Chunking | ✅ |
| Embedding Generation | ✅ |
| Vector DB Indexing (Qdrant) | ✅ |
| Semantic Search | ✅ |
| RAG Answer Generation | ✅ |
| Multi-Provider LLM | ✅ |

---

## Features

- **File Upload** — Upload TXT and PDF files (configurable max size)
- **Intelligent Chunking** — LangChain's `RecursiveCharacterTextSplitter` with adjustable chunk size / overlap
- **Embedding Generation** — Built-in support for Cohere and OpenAI embedding models
- **Vector Database** — Qdrant for efficient similarity search (configurable distance method)
- **Semantic Search** — Find relevant document chunks by meaning, not keywords
- **RAG Answers** — Generate contextual answers using retrieved chunks + LLM prompt templates
- **Pluggable Providers** — Swap between OpenAI and Cohere for both generation and embedding
- **Multi-Language Templates** — Prompt templates in English and Arabic (easily extensible)
- **Project Isolation** — All data (files, chunks, vectors) grouped by `project_id`
- **Reset Support** — Re-process or re-index documents without duplication
- **Async Throughout** — FastAPI + Motor (async MongoDB) + aiofiles for non-blocking I/O
- **Dockerized DB** — MongoDB 7 runs in a container via docker-compose

---

## Architecture

```
                   ┌─────────────────────────────┐
                   │       Client / User          │
                   └──────────┬──────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   FastAPI Server   │
                    │  (Uvicorn + ASGI)  │
                    └────┬──────┬───────┘
                         │      │
              ┌──────────▼┐  ┌──▼────────────┐
              │   MongoDB  │  │    Qdrant     │
              │  (Motor)   │  │  (Vector DB)  │
              └─────┬─────┘  └──────┬─────────┘
                    │               │
         ┌──────────▼───────────────▼──────────┐
         │        LLM Providers (Cohere/OpenAI)│
         │  ┌──────────────────────────────┐   │
         │  │  Embedding Model             │   │
         │  │  Generation Model            │   │
         │  └──────────────────────────────┘   │
         └─────────────────────────────────────┘
```

### Pipeline Flow

```
Upload ──► Validate ──► Save to Disk ──► Asset Record (MongoDB)
                                                │
                                                ▼
Process ──► LangChain Loader ──► Split Text ──► Chunks (MongoDB)
                                                │
                                                ▼
Index ──► Embed Chunks ──► Store Vectors ──► Qdrant Collection
                                                │
                                                ▼
Search/Answer ──► Embed Query ──► Vector Search ──► LLM Generation
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI + Uvicorn |
| Document Database | MongoDB (Motor async driver) |
| Vector Database | Qdrant |
| Document Parsing | LangChain (TextLoader, PyMuPDFLoader) |
| Text Splitting | RecursiveCharacterTextSplitter |
| Embedding | Cohere / OpenAI |
| Generation | Cohere / OpenAI |
| Configuration | Pydantic Settings + `.env` |
| Containerization | Docker (MongoDB) |

---

## Quick Start

### Prerequisites

- Python 3.8+
- Docker & Docker Compose

### 1. Start MongoDB

```bash
cd docker
docker-compose up -d
```

### 2. Install dependencies

```bash
cd src
pip install -r requirments.txt
```

### 3. Configure environment

Copy `src/.env.example` to `src/.env` and customize:

```env
# App
APP_NAME="mini-RAG"
APP_VERSION="0.1"

# File upload limits
FILE_ALLOWED_TYPES=["text/plain","application/pdf"]
FILE_MAX_SIZE=16                          # MB
FILE_DEFAULT_CHUNK_SIZE=512000            # Bytes for upload streaming

# MongoDB
MONGODB_URL="mongodb://admin:admin@localhost:27017"
MONGODB_DATABASE="mini-rag"

# LLM Backend (Cohere or OPENAI)
GENERATION_BACKEND="COHERE"
EMBEDDING_BACKEND="COHERE"

OPENAI_API_KEY="sk-..."
COHERE_API_KEY="cohere_..."

GENERATION_MODEL_ID="command-a-03-2025"
EMBEDDING_MODEL_ID="embed-multilingual-light-v3.0"
EMBEDDING_MODEL_SIZE=384

# Generation parameters
INPUT_DEFAULT_MAX_CHARS=1024
GENERATION_DEFAULT_MAX_TOKENS=200
GENERATION_DEFAULT_TEMPERATURE=0.1

# Vector Database
VECTOR_DB_BACKEND="QDRANT"
VECTOR_DB_PATH="qdrant_db"
VECTOR_DB_DISTANCE_METHOD="cosine"

# Templates
DEFAULT_LANGUAGE="en"
```

### 4. Run the server

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
│   ├── docker-compose.yml          # MongoDB 7 container
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
│   │   ├── BaseDataModel.py        # Base MongoDB model
│   │   ├── ProjectModel.py         # Project CRUD
│   │   ├── ChunkModel.py           # Chunk CRUD (paginated, bulk insert)
│   │   ├── AssetModel.py           # File asset CRUD
│   │   ├── db_schemas/
│   │   │   ├── project.py          # Project Pydantic schema
│   │   │   ├── data_chunk.py       # Chunk & RetrievedDocument schemas
│   │   │   └── asset.py            # Asset Pydantic schema
│   │   └── enums/
│   │       ├── ProcessingEnum.py   # File extension types
│   │       ├── DataBaseEnum.py     # MongoDB collection names
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

Configure via `GENERATION_BACKEND` and `EMBEDDING_BACKEND` in `.env`.

### Vector DB Providers

| Provider | Status |
|----------|--------|
| **Qdrant** | ✅ Fully supported |

Configure via `VECTOR_DB_BACKEND` in `.env`.

### Template System

RAG prompts are defined as modular templates in `stores/templates/locales/{lang}/rag.py`. Currently supports:
- **English** (`en`)
- **Arabic** (`ar`)

Add a new language by creating a new locale directory and implementing the prompt templates.

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
motor==3.4.0
openai==1.75.0
cohere==5.5.8
qdrant-client==1.10.1
```

---

## Roadmap

- [x] Document upload (TXT, PDF)
- [x] Text chunking with LangChain
- [x] MongoDB storage for chunks & assets
- [x] Embedding generation (Cohere / OpenAI)
- [x] Vector database indexing (Qdrant)
- [x] Semantic search
- [x] RAG answer generation
- [ ] File type expansion (DOCX, Markdown, HTML)
- [ ] Authentication & rate limiting
- [ ] Streaming responses
- [ ] Web UI / playground
- [ ] Alternative vector DBs (pgvector, Pinecone, Weaviate)

---

## License

MIT
