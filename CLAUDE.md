# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the application

```bash
# Quick start (from project root)
./run.sh

# Manual start
cd backend && uv run uvicorn app:app --reload --port 8000
```

The app serves at `http://localhost:8000`. The frontend is static files served by FastAPI; there is no separate frontend build step.

## Environment setup

Always use `uv` — never `pip` or bare `python` directly.

```bash
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
uv sync
```

## Key configuration

All tunable parameters live in `backend/config.py`:
- `ANTHROPIC_MODEL` — Claude model used for generation
- `EMBEDDING_MODEL` — sentence-transformers model for ChromaDB (`all-MiniLM-L6-v2`)
- `CHUNK_SIZE` / `CHUNK_OVERLAP` — document chunking parameters
- `MAX_RESULTS` — top-k chunks returned per search
- `MAX_HISTORY` — number of prior exchanges kept in session context
- `CHROMA_PATH` — where ChromaDB persists its data (`./chroma_db` relative to `backend/`)

## Architecture

### Request flow

1. Browser (`frontend/script.js`) POSTs `{query, session_id}` to `/api/query`
2. `app.py` creates a session if needed, delegates to `RAGSystem.query()`
3. `RAGSystem` loads conversation history and calls `AIGenerator.generate_response()` with the `search_course_content` tool available
4. Claude either answers directly (`stop_reason=end_turn`) or calls the tool (`stop_reason=tool_use`)
5. If tool use: `CourseSearchTool` queries ChromaDB for top-k semantically similar chunks, formats them, then a second Claude call generates the grounded answer
6. The exchange is saved to `SessionManager` and the response returned to the browser

### ChromaDB collections

Two collections are maintained in `VectorStore`:
- `course_catalog` — one document per course (title + metadata); used for fuzzy course-name resolution via semantic search
- `course_content` — chunked lesson text; used for the actual RAG retrieval

Course titles are used as IDs in `course_catalog`, so re-ingesting a course that already exists is a no-op.

### Document format

Course files (`.txt`, `.pdf`, `.docx`) in `docs/` must follow this header format:
```
Course Title: <title>
Course Link: <url>
Course Instructor: <name>

Lesson 1: <title>
Lesson Link: <url>
<lesson content>

Lesson 2: <title>
...
```

`DocumentProcessor` parses this structure into `Course` / `Lesson` / `CourseChunk` Pydantic models before ingestion.

### Adding a new tool

1. Subclass `Tool` (abstract base in `search_tools.py`) and implement `get_tool_definition()` and `execute()`
2. Register with `tool_manager.register_tool(your_tool)` in `RAGSystem.__init__()`
3. If the tool returns sources to display in the UI, add a `last_sources` list attribute — `ToolManager.get_last_sources()` will pick it up automatically
