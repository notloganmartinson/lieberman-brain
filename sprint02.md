# SPRINT 2: Iterative Graph Extraction Pipeline

## Objective
Feed the `chunked_data.json` array into the Gemini API one chunk at a time to extract structured Nodes and Edges, building "subgraphs" for each chunk.

## Architecture Details
1.  **Schema Definition:** The script must enforce a strict JSON schema using Gemini's Structured Outputs (or robust system prompting).
    * **Node Object:** `{"id": "string", "label": "string", "description": "string"}` (The description is crucial for Vector hybrid search later).
    * **Edge Object:** `{"source": "string", "target": "string", "type": "string", "justification": "string"}`
2.  **Iterative Loop:** Write a Python script (`sprint_2_extractor.py`) that:
    * Loads `chunked_data.json`.
    * Loops through each chunk.
    * Calls the Gemini API.
    * Includes rate-limit handling (e.g., `time.sleep()`, exponential backoff, or Tenacity library) to prevent 429 Too Many Requests errors.
3.  **Batch Saving:** Save the extracted subgraphs incrementally (e.g., append to a JSON Lines `.jsonl` file or save individual JSONs in a `subgraphs/` directory) so progress isn't lost if the script crashes on chunk 499.

## CLI Instructions
* Write the extraction script utilizing the official `google-genai` SDK.
* Craft the exact System Prompt required to instruct the model to act as a Graph Data Architect for Alex Lieberman.
* Ensure the output strictly conforms to the JSON schema.
* Do not write Neo4j Cypher queries yet. Stop here.
