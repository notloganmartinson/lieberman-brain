# Sprint 2: High-Performance Database Ingestion (Batching)

We are refactoring document ingestion in `backend/ghostwriter.py` to eliminate sequential multi-threaded database hits in favor of a single, highly optimized batch transaction.

## Instructions:
1. **Remove the Anti-Pattern:**
   - Delete the `process_and_store_chunk` helper function entirely.
   - In `store_document_chunks`, remove the `ThreadPoolExecutor`.

2. **Implement Batch Cypher Insertion:**
   - Inside `store_document_chunks`, iterate over the `chunks` array in Python to create a list of dictionaries (the payload). Each dictionary should contain an `id` (using `uuid.uuid4().hex`), the `text` of the chunk, and its `vector` (via `embed_query(chunk)`).
   - Write a new Cypher query using `UNWIND $payload AS batch`.
   - The query should `MERGE` the node using `batch.id`, `SET` the `session_id`, `filename`, and `text`, and call `db.create.setNodeVectorProperty` to set the `embedding`.
   - Execute this query in a single `session.run()` call using the global `neo4j_driver`.

Execute these changes in `backend/ghostwriter.py`.
