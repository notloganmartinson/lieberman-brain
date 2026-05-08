# Sprint 1: Global State & Tool Refactoring

We are refactoring `backend/ghostwriter.py` to fix connection pooling and scope issues.

## Instructions:
1. **Neo4j Driver Connection Pooling:**
   - Remove the `GraphDatabase.driver(...)` instantiation from inside `retrieve_document_context`, `retrieve_context`, `process_and_store_chunk`, and `store_document_chunks`.
   - Instantiate a single global `neo4j_driver` at the top of `ghostwriter.py` (right after loading environment variables).
   - Update all functions to use `with neo4j_driver.session() as session:` instead of creating and closing a local driver.

2. **Tool Extraction:**
   - Move the inner functions `get_upcoming_meetings`, `schedule_meeting`, and `delete_meeting` OUT of `generate_content`.
   - Place them at the module level in `ghostwriter.py`.
   - Refactor these tools so they can still access the user's `access_token`. You may pass `access_token` explicitly or update how the tools are passed to the Gemini configuration. (Hint: Gemini tools usually don't accept dynamic kwargs easily at runtime, so consider passing the tools cleanly or using a class/closure if needed to bind the token).

Execute these changes in `backend/ghostwriter.py`.
