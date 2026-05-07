# SPRINT 4: The GraphRAG Agent (Query & Generation)

## Objective
Build the retrieval and generation loop that actually writes content for Alex. This is the application layer that combines Graph Traversal with Tone Mapping.

## Architecture Details
1.  **The Prompt Input:** The user provides a prompt (e.g., "Write a LinkedIn post about why newsletters are a moat against algorithmic risk").
2.  **Hybrid Retrieval Logic:**
    * **Step A (Vector Search):** Embed the prompt and search the Neo4j Vector Index to find the entry nodes (e.g., the `[Newsletter]` and `[Algorithmic Risk]` nodes).
    * **Step B (Graph Traversal):** Execute a Cypher query starting from those entry nodes to expand 1-2 "hops" outwards. This pulls in related concepts (e.g., `[Trusted Distribution]`, `[Morning Brew]`, `[Owned Audience]`).
3.  **Context Assembly:** Combine the retrieved structured data (the subgraph) into a readable context string.
4.  **Tone Injection:** Load the `tone_and_replies.txt` file (created earlier) to act as a few-shot prompt for his specific cadence, vocabulary, and formatting.
5.  **Final Generation:** Pass the Prompt + Graph Context + Tone Context to Gemini to generate the final piece of content.

## CLI Instructions
* Write `sprint_4_agent.py`.
* Include the Neo4j querying logic to extract the context.
* Include the final, highly-tuned LLM prompt instructing Gemini to act as Alex Lieberman, utilizing *only* the retrieved graph data to form its arguments, and styling it based on the tone file.
* Output the final generated text.
