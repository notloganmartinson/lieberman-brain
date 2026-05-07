# SPRINT 1: The FastAPI & Web Search Backend

## Objective
Convert `ghostwriter.py` into a robust REST API using FastAPI and integrate live web search to satisfy the "Perplexity" requirement.

## Architecture Details
1. **FastAPI Setup:** Create a new file `api.py` (or modify `ghostwriter.py`). Initialize a FastAPI app with CORS middleware enabled (allowing `localhost:5173` for React testing).
2. **Web Search Integration:** * Integrate a lightweight web search function (e.g., using `duckduckgo-search` python package, or the Tavily API if the user provides a key).
   * It should take the user's prompt, search the web, and return the top 3 contextual snippets and URLs.
3. **The Synthesis Pipeline:** Modify the existing generation function to execute the following pipeline in a single `POST /chat` endpoint:
   * Step 1: Run the Web Search (get `web_context`).
   * Step 2: Run the Neo4j Graph/Vector Retrieval (get `graph_context`).
   * Step 3: Combine both contexts.
   * Step 4: Call Gemini with a system prompt instructing it to answer the query using the `web_context` for facts and the `graph_context` for tone/mental models.
4. **Structured Output:** The endpoint must return a JSON response containing:
   * `reply`: The generated text.
   * `sources`: An array of objects detailing the web links and graph nodes used, so the frontend can display citations.

## CLI Instructions
* Write the `api.py` script.
* Ensure all database and API keys are loaded via `python-dotenv`.
* Stop when the API can be run locally via `uvicorn api:app --reload` and tested via cURL or Postman.
