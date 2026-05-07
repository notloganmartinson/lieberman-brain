# Objective
Fix the document retrieval pipeline to use a true, session-scoped cosine similarity vector search (preventing LLM context window bloat), and optimize the API by calculating the prompt embedding only once before parallel execution.

# Key Files & Context
- `backend/ghostwriter.py`: The `retrieve_document_context` function needs its Cypher query rewritten to score embeddings.
- `backend/api.py`: The helper functions and the main chat endpoint need to be refactored to pass a pre-computed embedding.

# Implementation Steps

1. **Optimize Embedding I/O (`backend/api.py`):**
   - Update `fetch_graph_data` signature to `def fetch_graph_data(query_embedding: List[float]) -> tuple[str, List[Dict[str, Any]]]:`
   - Remove `query_embedding = embed_query(prompt)` from inside `fetch_graph_data`.
   - Update `fetch_document_data` signature to `def fetch_document_data(query_embedding: List[float], session_id: str) -> tuple[str, List[Dict[str, Any]]]:`
   - In `chat_endpoint`, inside the `else:` block (RESEARCH intent):
     - Add `query_embedding = embed_query(prompt)` right before `with ThreadPoolExecutor(max_workers=3) as executor:`.
     - Update the executor submissions:
       - `future_graph = executor.submit(fetch_graph_data, query_embedding)`
       - `future_doc = executor.submit(fetch_document_data, query_embedding, request.session_id)`

2. **Fix Vector Search (`backend/ghostwriter.py`):**
   - Update `retrieve_document_context` signature to `def retrieve_document_context(query_embedding: List[float], session_id: str, top_k: int = 3) -> tuple[str, list]:`
   - Replace the Cypher query with:
     ```cypher
     MATCH (n:UserDocumentChunk {session_id: $session_id})
     WHERE n.embedding IS NOT NULL
     WITH n, vector.similarity.cosine(n.embedding, $query_embedding) AS score
     ORDER BY score DESC
     LIMIT $top_k
     RETURN n.text AS text, n.filename AS filename, score
     ```
   - Update the `session.run` parameters to pass `query_embedding=query_embedding` and `top_k=top_k`.
   - Loop through `results` to build the `context_str`, appending the score: `context_str += f"- [From {res['filename']} | Score: {res['score']:.4f}]: {res['text']}\n"`.
   - Ensure the deduplication logic for `sources` remains intact (using a set of filenames).

# Verification & Testing
- Ensure the backend compiles without error.
- Check that the Gemini API is only hit once per chat request for embedding generation.
- Ensure only the top `k` most relevant document chunks are returned instead of the whole file.