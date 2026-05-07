import os
import json
import logging
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from pydantic import BaseModel, Field
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google import genai
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define Pydantic models for structured output
class Node(BaseModel):
    id: str = Field(description="Unique identifier for the node, ideally normalized (e.g., 'morning_brew').")
    label: str = Field(description="The display name or concept name.")
    description: str = Field(description="Detailed explanation of the concept, crucial for vector search later.")

class Edge(BaseModel):
    source: str = Field(description="ID of the source node.")
    target: str = Field(description="ID of the target node.")
    relationship_type: str = Field(description="The relationship type (e.g., 'FOUNDED', 'IS_A', 'RELATES_TO').")
    justification: str = Field(description="A brief explanation of why this edge exists based on the text.")

class GraphExtraction(BaseModel):
    nodes: list[Node]
    edges: list[Edge]

# Initialize Gemini client
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is missing.")
client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """You are an expert Graph Data Architect tasked with analyzing content by Alex Lieberman.
Your goal is to extract conceptual frameworks, mental models, entities, and relationships into a structured graph format.
Identify key people, companies, frameworks, platforms, and concepts.
Merge identical concepts using consistent IDs.
Always provide rich descriptions for nodes to aid in future semantic search.
Ensure edge relationships are logically sound and justified by the text.

You MUST return a valid JSON object matching the following structure:
{
  "nodes": [
    {"id": "string", "label": "string", "description": "string"}
  ],
  "edges": [
    {"source": "string", "target": "string", "relationship_type": "string", "justification": "string"}
  ]
}
"""

@retry(
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logging.warning(f"Retrying after error: {retry_state.outcome.exception()}")
)
def extract_graph_from_chunk(text: str) -> GraphExtraction:
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite-preview',
        contents=text,
        config={
            "system_instruction": SYSTEM_PROMPT,
            "response_mime_type": "application/json",
            "temperature": 0.1,
        },
    )
    return GraphExtraction.model_validate_json(response.text)

def process_chunks(input_file="chunked_data.json", output_file="extracted_subgraphs.jsonl", limit=None):
    if not os.path.exists(input_file):
        logging.error(f"Input file {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    if limit:
        chunks = chunks[:limit]
        logging.info(f"Processing limited to {limit} chunks for testing.")
    else:
        logging.info(f"Processing all {len(chunks)} chunks.")

    processed_count = 0
    
    with open(output_file, "a", encoding="utf-8") as out_f:
        for chunk in chunks:
            chunk_id = chunk.get("chunk_id")
            logging.info(f"Processing chunk {chunk_id} ({processed_count + 1}/{len(chunks)})...")
            
            try:
                extraction = extract_graph_from_chunk(chunk.get("text", ""))
                
                # Create a record that includes the original metadata and the extraction
                record = {
                    "chunk_id": chunk_id,
                    "source": chunk.get("source"),
                    "source_file": chunk.get("source_file"),
                    "extraction": extraction.model_dump()
                }
                
                # Append to JSONL
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                out_f.flush()
                processed_count += 1
                
            except Exception as e:
                logging.error(f"Failed to process chunk {chunk_id} after retries. Error: {e}")

    logging.info(f"Completed processing. Successfully extracted {processed_count} subgraphs.")

if __name__ == "__main__":
    process_chunks()
       return None, (chunk_id, e)

    processed_count = 0
    with open(output_file, "a", encoding="utf-8") as out_f:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_chunk = {executor.submit(_process_single, chunk): chunk for chunk in chunks_to_process}
            
            for future in as_completed(future_to_chunk):
                record, error = future.result()
                if error:
                    chunk_id, e = error
                    logging.error(f"Failed to process chunk {chunk_id} after retries. Error: {e}")
                elif record:
                    out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    out_f.flush()
                    processed_count += 1
                    if processed_count % 10 == 0:
                         logging.info(f"Processed {processed_count}/{len(chunks_to_process)} remaining chunks...")

    logging.info(f"Completed processing. Successfully extracted {processed_count} subgraphs in this run.")

if __name__ == "__main__":
    process_chunks()
