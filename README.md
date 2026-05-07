# Lieberman GraphRAG: Content Consigliere

An enterprise-grade GraphRAG (Retrieval-Augmented Generation) architecture designed to act as an autonomous "Content Consigliere" and ghostwriter. This system synthesizes vast amounts of unstructured knowledge (tweets, newsletters, transcripts, and LinkedIn posts) into a structured Neo4j graph database, enabling highly contextual, tone-accurate content generation.

> **Note:** This project was originally conceptualized and built in response to Alex Lieberman's LinkedIn post seeking an AI-assisted "Content Consigliere" / ghostwriter capable of mimicking his authentic voice and business frameworks.

## 🏗️ Architecture Overview

The system is built across four distinct execution sprints:

1. **Semantic Chunking (`sprint_1_chunker.py`)**
   - Ingests raw data from YouTube transcripts, Twitter threads, and LinkedIn posts.
   - Utilizes LangChain's `RecursiveCharacterTextSplitter` for intelligent chunking.
   - Ensures metadata (source, chunk ID) is perfectly tracked.

2. **Graph Extraction (`sprint_2_extractor.py`)**
   - Processes chunks using Google's Gemini models.
   - Employs strict JSON schemas to extract conceptual entities (Nodes) and semantic relationships with justifications (Edges).
   - Extracts dense, descriptive representations of mental models and frameworks.

3. **Neo4j Ingestion & Entity Resolution (`sprint_3_ingestion.py`)**
   - Performs entity deduplication and ID normalization.
   - Generates 3072-dimensional vector embeddings (`gemini-embedding-2`) for all concept descriptions.
   - Loads the nodes and edges into a remote Neo4j graph database using highly optimized `UNWIND` Cypher queries.
   - Establishes a native Vector Index for hybrid retrieval.

4. **Generation Agent (`ghostwriter.py`)**
   - The final application layer.
   - Takes a user prompt, generates an embedding, and queries the Neo4j Vector Index.
   - Traverses 1-2 hops into the graph to pull related relational context and justifications.
   - Injects a verified "tone file" to guarantee the output matches the target's unique cadence, vocabulary, and formatting.
   - Generates the final, highly accurate content.

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- A Neo4j Aura Database instance
- A Google Gemini API Key

### Installation

1. **Clone the repository and set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration:**
   Create a `.env` file in the root directory and add your credentials:
   ```ini
   NEO4J_URI="neo4j+s://your-instance.databases.neo4j.io"
   NEO4J_USERNAME="neo4j"
   NEO4J_PASSWORD="your_neo4j_password"
   GEMINI_API_KEY="your_gemini_api_key"
   ```

### Usage

Run the ghostwriter agent directly from the CLI:

```bash
python ghostwriter.py --prompt "Write a short thread about the biggest mistake founders make when hiring an executive team."
```

## 🛠️ Technologies Used
- **Knowledge Graph:** Neo4j
- **LLM / Embeddings:** Google Gemini (`gemini-3.1-flash-lite-preview`, `gemini-embedding-2`)
- **Orchestration:** LangChain (Chunking), Pydantic (Schema Validation), Tenacity (Backoff/Retry)
- **Language:** Python
