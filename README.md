# Lieberman GraphRAG: Better-Perplexity Edition

An enterprise-grade GraphRAG (Retrieval-Augmented Generation) architecture upgraded into a "Persona-Grounded Perplexity" web application. This system synthesizes live internet search results with a structured Neo4j knowledge graph to write topical content in Alex Lieberman's authentic voice and business frameworks.

## 🏗️ Architecture Overview

1. **Backend (FastAPI + Neo4j):**
   - **Semantic Router:** Categorizes user intent. Schedule-related requests take a "Fast Path" directly to the Calendar Agent.
   - **Hybrid Retrieval:** Standard research queries trigger a "Deep Path" combining live web search (DuckDuckGo) with Neo4j graph traversal.
   - **Agentic Calendar:** Uses Gemini Function Calling to extract event details and manage a virtual calendar.

2. **Frontend (React + Vite + Tailwind):**
   - **Generative UI:** A clean, minimalistic chat interface that renders real-time citations and a dynamic calendar notification system.
   - **Markdown Precision:** Uses `react-markdown` with Tailwind Typography for premium text rendering.
   - **Persona-Grounded:** Grounded in a verified "tone file" to ensure output matches the target's unique cadence and vocabulary.

## 🚀 Getting Started

### Prerequisites
- Python 3.12+ & Node.js
- A Neo4j Aura Database instance
- A Google Gemini API Key

### Installation

1. **Backend Setup:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   # Create .env with credentials
   python -m uvicorn backend.api:app --reload
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🛠️ Technologies Used
- **Knowledge Graph:** Neo4j
- **LLM / Embeddings:** Google Gemini (`gemini-2.5-flash`, `gemini-embedding-2`)
- **Web Search:** DuckDuckGo (`ddgs`)
- **Frontend:** React, Vite, Tailwind CSS, React-Markdown
- **API:** FastAPI
