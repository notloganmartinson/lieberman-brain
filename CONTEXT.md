# CONTEXT: The Lieberman GraphRAG Architecture

## 1. The Ultimate Objective
We are building a production-grade, enterprise-level AI Content Engine designed specifically to automate the "Content Consigliere" role for Alex Lieberman (Co-founder of Morning Brew, Tenex). 
The core of this engine is a **Graph-based Retrieval-Augmented Generation (GraphRAG)** system. This system will ingest his historical content, map his mental models, and generate net-new, highly accurate content in his voice.

## 2. The Data Assets (The "Brain" Material)
We have successfully acquired and cleaned three distinct datasets, currently residing in local directories:
1.  **YouTube Transcripts (`clean_transcripts.txt`)**: Deep, long-form insights, frameworks, and cadences.
2.  **Twitter/X Frameworks (`graph_frameworks.txt`)**: Punchy, high-signal business models and hooks.
3.  **LinkedIn Posts (`clean_linkedin.txt`)**: Professional B2B storytelling and enterprise consulting philosophies.
*Note: A separate `tone_and_replies.txt` exists to train the final generation layer on his casual voice, completely separate from the graph database.*

## 3. The Architecture Philosophy (Rules of Engagement for the CLI)
To ensure this system is production-ready (not a toy script), the AI CLI must adhere to these strict architectural principles:
* **No Single-Shot Processing:** Do NOT attempt to read all data and output a graph in one prompt. You will hit token limits and suffer from "Lost in the Middle" cognitive degradation. 
* **Iterative Subgraph Extraction:** Data must be chunked and processed iteratively. 
* **Entity Resolution is Mandatory:** The system must merge identical concepts (e.g., "Morning Brew", "The Brew", "MorningBrew") to prevent graph fragmentation.
* **Hybrid Retrieval (Graph + Vector):** The final querying mechanism will combine Vector Search (for semantic similarity) with Graph Traversal (for multi-hop logical reasoning).
* **Database:** We are targeting **Neo4j** (AuraDB) as the graph database. Cypher is the query language of choice.

## 4. How to Use the Sprint Files
The build process has been divided into distinct `sprint_*.md` files. 
When interacting with the Gemini CLI, feed it this `CONTEXT.md` file first to ground it. Then, feed it one Sprint file at a time, instructing it to execute *only* the code and architecture specified in that specific sprint. Do not let the CLI hallucinate future steps.
