# SPRINT 1: Semantic Chunking & Data Preparation

## Objective
Convert massive, continuous text files (`clean_transcripts.txt`, `graph_frameworks.txt`, `clean_linkedin.txt`) into intelligently sized chunks suitable for LLM extraction without losing context.

## The Problem
Standard chunking (e.g., splitting by exactly 1,000 characters) cuts paragraphs in half, destroying the relationships between entities before the AI even reads them.

## Execution Requirements
1.  **Implement Semantic Chunking:** Write a Python script using a library like `LangChain` (specifically `RecursiveCharacterTextSplitter` or semantic chunkers) or `LlamaIndex` to parse the files.
2.  **Chunk Size and Overlap:**
    * Target chunk size: ~1,500 - 2,000 tokens (provides enough context for the LLM to identify relationships without overwhelming it).
    * Overlap: ~200 tokens. This ensures that if a framework starts at the end of Chunk A and finishes in Chunk B, the relationship edge is not lost.
3.  **Metadata Tagging:** The script must attach metadata to every chunk before saving it.
    * `source`: (YouTube, Twitter, or LinkedIn)
    * `chunk_id`: A unique UUID.
4.  **Output:** The script should output a structured JSON array of these chunks, ready to be fed iteratively into the extraction pipeline in Sprint 2.

## CLI Instructions
* Build the `sprint_1_chunker.py` script.
* Ensure it handles UTF-8 encoding safely.
* Verify it outputs a `chunked_data.json` file.
* Do not proceed to extraction. Stop here.
