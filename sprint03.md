# SPRINT 3: Parallel Retrieval & Context Injection

The backend now has the documents in Neo4j. We must retrieve them during a user query and inject them into the RAG prompt alongside the live web and core graph data.

## Tasks
1. **Session Awareness (`backend/api.py`):**
   - Update `ChatRequest` Pydantic model to include `session_id: str`.

2. **Document Retrieval (`backend/ghostwriter.py`):**
   - Create `retrieve_document_context(query_embedding: List[float], session_id: str) -> tuple[str, list]`.
   - Write a Neo4j Vector Search query against `UserDocumentChunk` nodes, strictly filtering by `WHERE n.session_id = $session_id`. Return the top 3 most relevant chunks.
   - Format the returned string as `=== UPLOADED DOCUMENT CONTEXT ===\n[Chunks here]`.

3. **Parallel Execution (`backend/api.py`):**
   - In the "RESEARCH" intent path inside `/chat`, add the `retrieve_document_context` to the `ThreadPoolExecutor`.
   - Now we are running `get_web_context`, `fetch_graph_data`, AND `retrieve_document_context` concurrently.
   - Combine all three context strings and pass them into `generate_content`.

Output the updated `backend/api.py` and `backend/ghostwriter.py`.
