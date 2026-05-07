# Objective
Optimize the document ingestion speed using multithreading and modify the retrieval pipeline to inject the entirety of uploaded documents into the Gemini context window.

# Key Files & Context
- `backend/ghostwriter.py`: Contains the `store_document_chunks` (needs multithreading) and `retrieve_document_context` (needs to switch from vector search to full retrieval).
- `backend/api.py`: Needs to stop computing embeddings for the document retrieval phase since we are pulling the full document.

# Implementation Steps

1. **Multithreaded Upload (`backend/ghostwriter.py`):**
   - Import `ThreadPoolExecutor` from `concurrent.futures`.
   - In `store_document_chunks`, pull the embedding and Neo4j writing logic into a helper function (e.g., `process_and_store_chunk(chunk, session_id, filename)`).
   - Use `ThreadPoolExecutor(max_workers=10)` to map the helper function over the list of `chunks`.
   - Ensure the driver session creation happens *inside* the threaded helper so each thread gets its own connection to avoid race conditions. (Note: create the vector index once before the threads start).

2. **Full Document Retrieval (`backend/ghostwriter.py`):**
   - Refactor `retrieve_document_context`.
   - Remove `query_embedding` and `top_k` arguments.
   - Update the Cypher query to simply:
     ```cypher
     MATCH (n:UserDocumentChunk {session_id: $session_id})
     RETURN n.text AS text, n.filename AS filename
     ```
   - Concatenate all returned text into the `context_str` to provide the full document to the LLM.

3. **API Integration (`backend/api.py`):**
   - Refactor `fetch_document_data(session_id: str)`.
   - Remove the `embed_query(prompt)` step inside it.
   - Call `retrieve_document_context(session_id)`.
   - Update the thread pool execution in `chat_endpoint` to match the new signature: `future_doc = executor.submit(fetch_document_data, request.session_id)`.

# Verification & Testing
- Upload a large file and verify that the UI loading state is significantly faster.
- Submit a chat request and verify that the AI can accurately summarize or reference information from the very beginning or end of the uploaded document.