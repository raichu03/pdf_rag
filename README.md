# PDF RAG Service

Lightweight Retrieval-Augmented Generation (RAG) backend that:
- Ingests PDF / DOCX / TXT documents
- Chunks and vectorizes text into Weaviate (multi2vec-clip)
- Stores metadata & tool outputs in SQLite
- Maintains per-user conversational memory in Redis
- Uses Google Gemini with function calling for: interview booking, schedule retrieval, contextual DB lookup


## Features

### Document & Data
- Upload: `.pdf`, `.txt`, `.docx` via REST ([`routes/ingest_document.py`](src/routes/ingest_document.py))
- Two chunking strategies: character-window (with overlap) & sentence-based ([`utils.chunking.TextProcessor`](src/utils/chunking.py))
- Vector store: Weaviate + `multi2vec-clip` module ([`docker-compose.yml`](docker-compose.yml))
- Metadata store: SQLite (`TextChunk`, `Meetings`) via SQLAlchemy ([`models/sql_models.py`](src/models/sql_models.py))
- Hybrid retrieval (semantic + keyword) using Weaviate's hybrid endpoint ([`SqlData._weaviate_data`](src/utils/retrieve_data.py))

### Conversational RAG
- Chat endpoint with per-user history in Redis ([`routes/chat.py`](src/routes/chat.py))
- Gemini model (`gemini-2.5-flash`) tool calling ([`services.chat_gemini.ChatRag`](src/services/chat_gemini.py))
- Tools defined dynamically from Python signatures ([`utils.functions.GetFunctions`](src/utils/functions.py))

### Tools / Functions
- Book interview → persists to `Meetings`
- Retrieve past schedules
- Get current time
- Retrieve contextual knowledge (RAG) from ingested documents

### Robust Ingestion Workflow
1. Extract text (PDF / DOCX / TXT)
2. Chunk text ([`TextProcessor.chunk_text`](src/utils/chunking.py))
3. Insert chunks into Weaviate ([`WeaviateCollection.import_data`](src/utils/store_weaviate.py))
4. Persist chunk UUID + raw text in SQLite ([`MetaData.add_data`](src/utils/store_metadata.py))

### Clean Separation of Concerns
- Services layer: ingestion + chat
- Utilities: chunking, persistence, retrieval, tool wrappers
- Models: DB schema + chat request models
- Routes: FastAPI endpoints


## High-Level Architecture

```
            +--------------------+
Upload ---> | FastAPI Ingestion  |----+
            +--------------------+    |
                       |              |
                       v              |
              +----------------+      |
              |  Chunking      |      |
              +----------------+      |
                       |              |
                       v              |
        +-------------------------+   |
        |  Weaviate (Vectors)     |<--+--- Hybrid Search (query)
        +-------------------------+   |
                       ^              |
                       |              |
                 +-----------+        |
                 |  SQLite   |<-------+
                 | (metadata)|  (UUID → text)
                 +-----------+
                       ^
                       |
             +------------------+
             | Gemini Chat RAG  |
             |  (Tool Calling)  |
             +------------------+
                       ^
                       |
                +-------------+
                | Redis (History)
                +-------------+
```

## Core Workflow Details

### 1. Ingestion Pipeline
| Step | Component | Code |
|------|-----------|------|
| Upload & validate file | FastAPI route | [`routes/ingest_document.py`](src/routes/ingest_document.py) |
| Extract text | `_extract_text_*` helpers | Same route file |
| Chunk text | `TextProcessor` | [`utils/chunking.py`](src/utils/chunking.py) |
| Insert vectors | `WeaviateCollection` | [`utils/store_weaviate.py`](src/utils/store_weaviate.py) |
| Persist metadata | `MetaData.add_data` | [`utils/store_metadata.py`](src/utils/store_metadata.py) |

### 2. Retrieval (RAG)
1. Hybrid search → get top UUIDs: [`SqlData._weaviate_data`](src/utils/retrieve_data.py)  
2. Map UUIDs to chunks (SQLite)  
3. Concatenate: [`SqlData.all_context`](src/utils/retrieve_data.py)

### 3. Conversation
- Start chat session with accumulated history: [`ChatRag.conversation`](src/services/chat_gemini.py)  
- Model may emit function calls via tool declarations  
- Function results fed back for final natural language response

## Project Structure

```
src/
  main.py
  routes/
    ingest_document.py   # /upload-docs/
    chat.py              # /chat, /chat-history
  services/
    data_ingest.py       # Orchestrates dual storage
    chat_gemini.py       # Gemini integration
  utils/
    chunking.py
    store_weaviate.py
    store_metadata.py
    retrieve_data.py
    functions.py         # Tool declarations
  models/
    sql_database.py
    sql_models.py
    weaviate_model.py
    chat_model.py
  type_definitions.py
  tests/
    test.py              # Standalone Gemini tool test harness
docker-compose.yml
.env (not committed with real key)
```

## Technology Stack

| Concern | Technology |
|---------|------------|
| API | FastAPI |
| Vectors | Weaviate (`multi2vec-clip`) |
| Embeddings | multi2vec-clip module (CLIP) |
| Metadata | SQLite (SQLAlchemy ORM) |
| Conversation Memory | Redis |
| LLM + Tools | Google Gemini function calling |
| Orchestration | Docker Compose |
| Runtime | Python 3.12 |


## Installation

### 1. Clone & Environment

```bash
git clone <repo>
cd pdf_rag
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env`:
```
GEMINI_API_KEY=YOUR_GEMINI_KEY
```

Security:
- Rotate any previously committed key.
- Do not commit real keys.

### 3. Start Weaviate + Embedding Module

```bash
docker compose up -d
# Verify:
curl -s http://localhost:8080/v1/.well-known/ready
```

### 4. Start Redis (choose one)

Local:
```bash
redis-server &
```

Docker:
```bash
docker run -d -p 6379:6379 --name redis redis:7
```

### 5. Run API

```bash
cd src
uvicorn main:app --reload
```

Health check:
```
GET http://localhost:8000/
```

## Usage

### Ingest a Document

```bash
curl -X POST \
  "http://localhost:8000/upload-docs/?chunking_strategy=sentence" \
  -F "file=@/path/to/document.pdf"
```

Response: success message with count.

### Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "Book an interview for Jane Doe on 2025-09-10 at 15:00 email jane@example.com"
  }'
```

### Retrieve Chat History

```bash
curl -X POST http://localhost:8000/chat-history \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123"}'
```


## Key Components (Links)

- Chunking: [`utils.chunking.TextProcessor`](src/utils/chunking.py)
- Vector Import: [`utils.store_weaviate.WeaviateCollection.import_data`](src/utils/store_weaviate.py)
- Collection Setup: [`models.weaviate_model.WeaviateManager.create_collection`](src/models/weaviate_model.py)
- Metadata Insert: [`utils.store_metadata.MetaData.add_data`](src/utils/store_metadata.py)
- Retrieval: [`utils.retrieve_data.SqlData.all_context`](src/utils/retrieve_data.py)
- Tools Wrapper: [`utils.functions.GetFunctions`](src/utils/functions.py)
- Chat Orchestrator: [`services.chat_gemini.ChatRag`](src/services/chat_gemini.py)
- Ingestion Orchestrator: [`services.data_ingest.AddRecords`](src/services/data_ingest.py)


## Data Models

| Table | Columns |
|-------|---------|
| TextChunk | id, sourceId, chunkID (Weaviate UUID), textChunk |
| Meetings | id, candidate_name, candidate_email, interview_date, interview_time |

See: [`models.sql_models`](src/models/sql_models.py)


## Tooling / Function Calling

Declared dynamically from Python signatures:
- `book_interview`
- `get_past_schedules`
- `get_current_time`
- `retrieve_database_info`

Declaration generator: [`GetFunctions.get_function_declaration`](src/utils/functions.py)


## Development Tips

| Task | Command |
|------|---------|
| Recreate venv | `rm -rf venv && python -m venv venv` |
| Freeze deps (if updated) | `pip freeze > requirements.txt` |
| Tail Weaviate logs | `docker compose logs -f weaviate` |
| Remove vector data | `docker compose down -v` |
| Reset SQLite | `rm src/metadata.db` |

## Possible Enhancements

- Add streaming responses
- Add chunk deduplication / compression
- Support batch deletion / document re-index
- Switch to async SQL driver
- Add evaluation harness (retrieval quality)
