import os
import logging
import argparse
from typing import List, Dict, Any
from neo4j import GraphDatabase
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, GEMINI_API_KEY]):
    raise ValueError("Missing Neo4j or Gemini credentials in environment variables.")

client = genai.Client(api_key=GEMINI_API_KEY)

def embed_query(query: str) -> List[float]:
    logging.info("Embedding the user query...")
    response = client.models.embed_content(
        model='gemini-embedding-2',
        contents=query,
    )
    return response.embeddings[0].values

def retrieve_context(query_embedding: List[float], top_k: int = 5) -> str:
    logging.info("Querying Neo4j for relevant graph context...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    context_str = ""
    with driver.session() as session:
        # Step A: Vector Search to find Entry Nodes
        vector_query = """
        CALL db.index.vector.queryNodes('concept_description_embedding', $top_k, $query_embedding)
        YIELD node, score
        RETURN node.id AS id, node.label AS label, node.description AS description, score
        """
        entry_nodes = session.run(vector_query, top_k=top_k, query_embedding=query_embedding).data()
        
        if not entry_nodes:
            logging.warning("No entry nodes found in the vector search.")
            return ""
        
        entry_node_ids = [n["id"] for n in entry_nodes]
        logging.info(f"Found {len(entry_node_ids)} entry nodes via Vector Search.")
        
        # Step B: Graph Traversal (1-hop)
        graph_query = """
        MATCH (n:Concept)-[r]-(m:Concept)
        WHERE n.id IN $entry_node_ids
        RETURN n.label AS source, type(r) AS relationship, r.justification AS justification, m.label AS target
        LIMIT 50
        """
        traversal_results = session.run(graph_query, entry_node_ids=entry_node_ids).data()
        
        logging.info(f"Traversed {len(traversal_results)} related edges.")
        
        context_str += "=== GRAPH CONTEXT ===\n"
        context_str += "Core Concepts Identified:\n"
        for n in entry_nodes:
            context_str += f"- {n['label']}: {n['description']}\n"
            
        context_str += "\nRelated Concepts & Justifications:\n"
        for r in traversal_results:
            justification = f" (Because: {r['justification']})" if r['justification'] else ""
            context_str += f"- {r['source']} [{r['relationship']}] {r['target']}{justification}\n"
            
    driver.close()
    return context_str

def get_tone_context() -> str:
    tone_file = "tweets/tone_and_replies.txt"
    if os.path.exists(tone_file):
        with open(tone_file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        logging.warning(f"Tone file not found at {tone_file}.")
        return ""

def generate_content(query: str, context: str, tone: str) -> str:
    logging.info("Generating content via Gemini...")
    
    system_prompt = f"""You are the 'Content Consigliere' AI representing Alex Lieberman (Co-founder of Morning Brew, Tenex).
Your task is to respond to the user's prompt by generating content that mimics Alex's authentic voice, cadence, and mental models.

### GRAPH CONTEXT:
You MUST base your arguments, facts, and frameworks primarily on the following extracted knowledge graph context:
{context}

### TONE & STYLE CONTEXT:
You MUST mimic the formatting, hook style, vocabulary, and conversational tone found in these examples:
{tone}

### INSTRUCTIONS:
- Write in the first person ("I", "my") as Alex Lieberman.
- Do NOT explicitly mention that you are using a graph or context provided. Just speak naturally.
- Focus on punchy hooks, clear formatting, and valuable takeaways typical of high-level B2B creators.
- Address the user's prompt directly using the context provided.
"""

    response = client.models.generate_content(
        model='gemini-3.1-flash-lite-preview',
        contents=query,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
        ),
    )
    return response.text

def main():
    parser = argparse.ArgumentParser(description="GraphRAG Content Engine for Alex Lieberman")
    parser.add_argument("--prompt", type=str, default="Write a LinkedIn post about why newsletters are a moat against algorithmic risk", help="The content generation prompt.")
    args = parser.parse_args()
    
    print(f"\n--- SPRINT 4: GraphRAG Agent ---")
    print(f"Prompt: '{args.prompt}'\n")
    
    try:
        # 1. Embed Prompt
        query_embedding = embed_query(args.prompt)
        
        # 2. Retrieve Graph Context
        context_str = retrieve_context(query_embedding)
        
        # 3. Retrieve Tone Context
        tone_str = get_tone_context()
        
        # 4. Generate Output
        final_content = generate_content(args.prompt, context_str, tone_str)
        
        print("\n================== GENERATED CONTENT ==================\n")
        print(final_content)
        print("\n=======================================================\n")
        
    except Exception as e:
        logging.error(f"Agent execution failed: {e}")

if __name__ == "__main__":
    main()