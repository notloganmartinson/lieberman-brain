import json
from pydantic import BaseModel, ValidationError
from typing import List

class Node(BaseModel):
    id: str
    label: str
    description: str

class Edge(BaseModel):
    source: str
    target: str
    relationship_type: str
    justification: str

class Extraction(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

class Chunk(BaseModel):
    chunk_id: str
    source: str
    source_file: str
    extraction: Extraction

def run_audit(file_path):
    total_chunks = 0
    validation_errors = 0
    unique_nodes = set()
    total_nodes = 0
    total_edges = 0

    print("Starting audit...")
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            total_chunks += 1
            try:
                data = json.loads(line)
                chunk = Chunk(**data)
                
                total_nodes += len(chunk.extraction.nodes)
                for node in chunk.extraction.nodes:
                    unique_nodes.add(node.id)
                
                total_edges += len(chunk.extraction.edges)

            except ValidationError as e:
                print(f"Validation error on line {line_num}:")
                for err in e.errors():
                    print(f"  - {err['loc']}: {err['msg']}")
                validation_errors += 1
            except Exception as e:
                print(f"Error on line {line_num}: {e}")
                validation_errors += 1

    avg_nodes = total_nodes / total_chunks if total_chunks > 0 else 0
    avg_edges = total_edges / total_chunks if total_chunks > 0 else 0

    print("--- Audit Results ---")
    print(f"Total lines/chunks: {total_chunks}")
    print(f"Schema validation errors: {validation_errors}")
    print(f"Unique node IDs extracted: {len(unique_nodes)}")
    print(f"Total edges extracted: {total_edges}")
    print(f"Average nodes per chunk: {avg_nodes:.2f}")
    print(f"Average edges per chunk: {avg_edges:.2f}")

if __name__ == "__main__":
    run_audit('/home/logan/lieberman-brain/extracted_subgraphs.jsonl')
