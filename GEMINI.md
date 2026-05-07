# LIEBERMAN GRAPHRAG (BETTER-PERPLEXITY) REPO MAP
SYSTEM INSTRUCTIONS:
1. LOGIC OMITTED: Functions are NOT empty. Implementations are abstracted for context efficiency.
2. READ/WRITE PROTOCOL: To modify a function or component, you MUST ask the user to provide the specific file path first. Do NOT hallucinate modifications without the source file.
3. ARCHITECTURAL GROUNDING: This is a full-stack "Better-Perplexity" Content Consigliere. 
   - Backend: Python 3.12+, FastAPI, Neo4j AuraDB (Graph/Vector Hybrid Retrieval), Google Gemini API.
   - Frontend: React 18 + Vite, Tailwind CSS.
   - Core Pipeline: Live Web Search -> Neo4j Graph Traversal -> Gemini Synthesis -> React UI with Citations.
4. SCOPE BOUNDARIES: This project prioritizes GraphRAG architecture and web search integration over enterprise authentication. Keep the stack lean. Avoid over-engineering security beyond environment variables and parameterized Cypher queries.
5. PRECISION: Use exact class, function, component, and file names from this map.

---

```text

# sprint_3_ingestion.py
def normalize_id(concept_id) -> str:
def load_and_resolve_entities(filepath):
def get_embeddings_batch(texts) -> List[List[float]]:
def generate_embeddings(nodes):
def ingest_to_neo4j(nodes, edges):

# audit_neo4j.py
def run_audit():

# audit_extraction.py
class Node:
class Edge:
class Extraction:
class Chunk:
def run_audit(file_path):

# generate_repo_ast.py
def format_py_function(node, indent): # Helper to format a Python function signature, return type, and brief docstring.
def parse_py_file(filepath): # Parses a Python file and returns its AST skeleton.
def parse_js_file(filepath): # Parses a JS/JSX file using regex to extract exported functions and components.
def generate_map(root_dir): # Walks the directory and builds the full-stack repo map.

# ghostwriter.py
def embed_query(query) -> List[float]:
def retrieve_context(query_embedding, top_k) -> str:
def get_tone_context() -> str:
def generate_content(query, context, tone) -> str:
def main():

# sprint_1_chunker.py
def create_chunks():

# tweets/prep_tweets.py
def split_twitter_data():

# linkedin/clean_linkedin.py
def clean_linkedin_data():

# youtube/clean_yt_transcripts.py
def clean_vtt_files():
```
