# SPRINT 3: Neo4j Ingestion & Entity Resolution

## Objective
Take the raw subgraphs extracted in Sprint 2 and ingest them into a Neo4j database using Cypher queries, while implementing Entity Resolution to clean the data.

## Architecture Details
1.  **Database Connection:** Write a Python script (`sprint_3_ingestion.py`) using the official `neo4j` Python driver to connect to a Neo4j AuraDB instance.
2.  **Entity Deduplication (Crucial Step):** * LLMs are messy. They will extract `[AI Transformation]`, `[AI-Transformation]`, and `[Artificial Intelligence Transformation]`.
    * *Implementation strategy:* Use Cypher `MERGE` statements and uppercase/lowercase normalization to deduplicate simple overlaps.
    * *Advanced (Optional but recommended):* Use a quick text-embedding pass (e.g., `text-embedding-004`) to cluster similar nodes and pick a canonical name before inserting.
3.  **Batch Ingestion via UNWIND:** Do NOT run a separate Cypher query for every single node. This will take hours. Pass the data arrays as parameters and use Cypher's `UNWIND` command to batch insert nodes and relationships.
4.  **Graph Indexes:** The script must create Neo4j Vector Indexes on the Node `description` properties to prepare for Sprint 4.

## CLI Instructions
* Write the ingestion script handling database connection credentials via environment variables.
* Write the optimized `UNWIND` Cypher queries for Nodes and Edges.
* Ensure `MERGE` is used instead of `CREATE` to naturally deduplicate IDs.
* Stop once the database is fully populated.
