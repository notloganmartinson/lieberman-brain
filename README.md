# Lieberman GraphRAG: Better-Perplexity Edition

An enterprise-grade GraphRAG (Retrieval-Augmented Generation) architecture upgraded into a "Persona-Grounded Perplexity" web application. This system synthesizes live internet search results with a structured Neo4j knowledge graph to write topical content in Alex Lieberman's authentic voice and business frameworks.

## Architecture Overview

1. **Backend (FastAPI + Neo4j):**
   - **Semantic Router:** Categorizes user intent. Schedule-related requests take a "Fast Path" directly to the Calendar Agent. Powered by the ultra-fast `gemini-1.5-flash-8b` model for minimum latency.
   - **Hybrid Retrieval:** Standard research queries trigger a "Deep Path" combining live web search (DuckDuckGo) with Neo4j graph traversal.
   - **Multi-Turn Chat Memory:** The system maintains full conversational context. Frontend message history is mapped to Gemini's native `Content` objects, allowing for follow-up questions and complex, multi-step workflows.
   - **Document Ingestion Pipeline:** Users can upload PDF, DOCX, CSV, and TXT files. Chunks are extracted, semantically chunked, and ingested into Neo4j using highly optimized batch transactions (`UNWIND` Cypher queries) for maximum database efficiency.
   - **Session-Aware Vector Search:** User-uploaded documents are queried from Neo4j using true cosine similarity vector search scoped to their `session_id`.
   - **Embedding Optimization:** The RAG pipeline computes the user prompt embedding exactly once and shares it across all parallel retrieval tasks (Graph and Docs).
   - **GSuite Calendar Agent:** Uses Gemini Function Calling and Google OAuth to natively manage the user's calendar. Calendar tools are cleanly encapsulated in an object-oriented `CalendarTools` class.
   - **Localized Timezone Handling:** Automatically receives and respects the user's dynamic local timezone for all calendar operations.
   - **Production-Ready:** Configured with robust cross-platform path resolution, dynamic CORS origins, and global database connection pooling.

2. **Frontend (React + Vite + Tailwind):**
   - **Generative UI:** A clean, minimalistic chat interface that renders real-time citations and a dynamic calendar notification system.
   - **Multipart File Uploads:** Users can seamlessly attach files to their chat prompts. The UI updates dynamically, rendering the attached file directly inside the chat bubble (like Gemini).
   - **Professional Request Cancellation:** Leveraging the native Javascript `AbortController`, users can instantly halt in-flight AI generations. Cancelled requests visually transform into a grey bubble state.
   - **OAuth Integration:** Secure Google Sign-In button that manages access tokens and securely passes them to the backend API.
   - **Markdown Precision:** Uses `react-markdown` with Tailwind Typography for premium text rendering.
   - **Persona-Grounded:** Grounded in a verified "tone file" to ensure output matches the target's unique cadence and vocabulary.

## Getting Started

### Prerequisites
- Python 3.12+ & Node.js
- A Neo4j Aura Database instance
- A Google Gemini API Key
- A Google OAuth Client ID (for Calendar access)

### Installation

1. **Backend Setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   # Create .env with NEO4J and GEMINI credentials
   python -m uvicorn backend.api:app --reload
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   # Create .env with VITE_GOOGLE_CLIENT_ID
   npm run dev
   ```

## Technologies Used
- **Knowledge Graph:** Neo4j
- **LLM / Embeddings:** Google Gemini (gemini-2.5-flash, gemini-embedding-2)
- **Web Search:** DuckDuckGo (ddgs)
- **Frontend:** React, Vite, Tailwind CSS, React-Markdown
- **API:** FastAPI
