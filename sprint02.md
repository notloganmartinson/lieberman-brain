# SPRINT 2: Vector Storage & Upload Endpoint

We need to vectorize the chunks and store them securely in Neo4j, then expose an endpoint for the React frontend.

## Tasks
1. **Neo4j Storage (`backend/ghostwriter.py`):**
   - Import `document_parser.py`.
   - Create a function `store_document_chunks(session_id: str, filename: str, chunks: List[str])`.
   - Inside, loop through the chunks, call `embed_query()` on each to get the vector.
   - Save to Neo4j. Cypher logic: `MERGE (n:UserDocumentChunk {id: random_uuid}) SET n.session_id = $session_id, n.filename = $filename, n.text = $text CALL db.create.setNodeVectorProperty(n, 'embedding', $vector)`. *(Ensure a vector index exists or create one dynamically for `UserDocumentChunk`)*.

2. **Upload API (`backend/api.py`):**
   - Add `python-multipart` support (FastAPI `UploadFile`, `File`, `Form`).
   - Create a new `POST /upload` endpoint.
   - It must accept a `file: UploadFile` and a `session_id: str = Form(...)`.
   - Read the file bytes, call `process_file()`, then call `store_document_chunks()`.
   - Return `{"status": "success", "filename": file.filename, "chunks_processed": len(chunks)}`.

Output only the updated `backend/ghostwriter.py` and `backend/api.py`.
