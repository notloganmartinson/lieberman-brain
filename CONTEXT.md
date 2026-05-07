# MISSION
You are an Elite Principal AI Engineer expanding a FastAPI + Neo4j + React RAG architecture. We are adding a highly robust "Document Ingestion Pipeline" to support PDF, DOCX, CSV, and TXT file uploads.

# TECH STACK
- Backend: FastAPI, Python 3.12+
- Parsing: `pymupdf` (PDF), `python-docx` (DOCX), standard `csv` module
- AI: `gemini-embedding-2` (Chunk embedding), `gemini-2.5-flash` (Generation)
- Vector Store: Neo4j (Nodes labeled `UserDocumentChunk`)

# ARCHITECTURAL PRINCIPLES
1. **Stateless Namespacing:** Uploaded document chunks must be tagged with a unique `session_id` passed from the frontend so user data doesn't bleed together.
2. **Deterministic Parsing:** Handle specific MIME types explicitly. Do not guess.
3. **Semantic Chunking:** Documents must be chunked with a defined overlap to prevent "Lost in the Middle" syndrome before being vectorized.
4. **Parallel Retrieval:** Document context retrieval must run concurrently alongside Web Search and Knowledge Graph retrieval in the RAG pipeline.
