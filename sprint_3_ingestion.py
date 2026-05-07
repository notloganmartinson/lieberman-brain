import os
import json
import logging
import re
from typing import Dict, Any, List
from neo4j import GraphDatabase
from google import genai
from tenacity import retry, wait_exponential, stop_after_attempt
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

def normalize_id(concept_id: str) -> str:
    # Lowercase, replace spaces and hyphens with underscores, remove non-alphanumeric
    norm = concept_id.lower().strip()
    norm = re.sub(r'[\s\-]+', '_', norm)
    norm = re.sub(r'[^a-z0-9_]', '', norm)
    return norm

def load_and_resolve_entities(filepath: str):
    nodes_dict: Dict[str, dict] = {}
    edges_list: List[dict] = []
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            try:
                data = json.loads(line)
                extraction = data.get("extraction", {})
                
                for node in extraction.get("nodes", []):
                    node_id = normalize_id(node.get("id", ""))
                    if not node_id: continue
                    
                    # Deduplication: Keep the node with the longest description if it already exists
                    existing_node = nodes_dict.get(node_id)
                    if not existing_node or len(node.get("description", "")) > len(existing_node.get("description", "")):
                        nodes_dict[node_id] = {
                            "id": node_id,
                            "label": node.get("label", node_id),
                            "description": node.get("description", "")
                        }
                
                for edge in extraction.get("edges", []):
                    source = normalize_id(edge.get("source", ""))
                    target = normalize_id(edge.get("target", ""))
                    rel_type = edge.get("relationship_type", "RELATES_TO").upper()
                    rel_type = re.sub(r'[^A-Z0-9_]', '_', rel_type) # sanitize relationship type
                    if not rel_type:
                        rel_type = "RELATES_TO"
                    
                    if source and target:
                        edges_list.append({
                            "source": source,
                            "target": target,
                            "relationship_type": rel_type,
                            "justification": edge.get("justification", "")
                        })
            except json.JSONDecodeError:
                continue

    # Filter edges to only include those where both source and target exist in nodes_dict
    valid_edges = [e for e in edges_list if e["source"] in nodes_dict and e["target"] in nodes_dict]
    
    return list(nodes_dict.values()), valid_edges

@retry(wait=wait_exponential(multiplier=1, min=2, max=20), stop=stop_after_attempt(5))
def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    # Gemini models.embed_content takes a list of strings
    response = client.models.embed_content(
        model='gemini-embedding-2',
        contents=texts,
    )
    return [e.values for e in response.embeddings]

def generate_embeddings(nodes: List[dict]):
    logging.info(f"Generating embeddings for {len(nodes)} nodes...")
    batch_size = 100
    for i in range(0, len(nodes), batch_size):
        batch_nodes = nodes[i:i+batch_size]
        texts = [n["description"] if n["description"] else n["label"] for n in batch_nodes]
        try:
            embeddings = get_embeddings_batch(texts)
            for j, node in enumerate(batch_nodes):
                node["embedding"] = embeddings[j]
        except Exception as e:
            logging.error(f"Failed to generate embeddings for batch {i//batch_size}: {e}")
        if (i + batch_size) % 1000 == 0 or i + batch_size >= len(nodes):
            logging.info(f"Embedded {min(i + batch_size, len(nodes))} / {len(nodes)} nodes.")

def ingest_to_neo4j(nodes: List[dict], edges: List[dict]):
    logging.info("Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    with driver.session() as session:
        # Create constraint
        logging.info("Setting up database constraints and indexes...")
        session.run("CREATE CONSTRAINT concept_id IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE")
        
        # Create Vector Index
        # text-embedding-004 has 768 dimensions
        try:
            session.run("""
                CREATE VECTOR INDEX concept_description_embedding IF NOT EXISTS
                FOR (c:Concept) ON (c.embedding)
                OPTIONS {indexConfig: {
                    `vector.dimensions`: 768,
                    `vector.similarity_function`: 'cosine'
                }}
            """)
        except Exception as e:
            logging.warning(f"Could not create vector index (might already exist or not supported): {e}")

        # Ingest Nodes
        logging.info(f"Ingesting {len(nodes)} nodes via UNWIND...")
        node_query = """
        UNWIND $nodes AS node
        MERGE (c:Concept {id: node.id})
        SET c.label = node.label,
            c.description = node.description,
            c.embedding = node.embedding
        """
        # Batch nodes to avoid huge transactions
        batch_size = 1000
        for i in range(0, len(nodes), batch_size):
            session.run(node_query, nodes=nodes[i:i+batch_size])
            
        # Group edges by relationship type
        from collections import defaultdict
        edges_by_type = defaultdict(list)
        for edge in edges:
            edges_by_type[edge["relationship_type"]].append(edge)
            
        logging.info(f"Ingesting {len(edges)} edges across {len(edges_by_type)} relationship types...")
        for rel_type, rel_edges in edges_by_type.items():
            rel_query = f"""
            UNWIND $edges AS edge
            MATCH (source:Concept {{id: edge.source}})
            MATCH (target:Concept {{id: edge.target}})
            MERGE (source)-[r:{rel_type}]->(target)
            SET r.justification = edge.justification
            """
            for i in range(0, len(rel_edges), batch_size):
                session.run(rel_query, edges=rel_edges[i:i+batch_size])
                
    driver.close()
    logging.info("Neo4j ingestion complete!")

if __name__ == "__main__":
    logging.info("Verifying Neo4j connection before proceeding...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        driver.verify_connectivity()
        driver.close()
        logging.info("Neo4j connection verified successfully.")
    except Exception as e:
        logging.error(f"Failed to connect to Neo4j. Check credentials. Error: {e}")
        exit(1)

    nodes, edges = load_and_resolve_entities("extracted_subgraphs.jsonl")
    logging.info(f"Resolved to {len(nodes)} unique nodes and {len(edges)} valid edges.")
    generate_embeddings(nodes)
    
    # Filter out nodes that failed to get embeddings (if any)
    valid_nodes = [n for n in nodes if "embedding" in n]
    
    ingest_to_neo4j(valid_nodes, edges)
