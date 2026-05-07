# CONTEXT: Lieberman GraphRAG - "Better Perplexity" Upgrade

## 1. The Ultimate Objective
We are upgrading an existing local Python CLI GraphRAG agent (`ghostwriter.py`) into a full-stack, production-ready web application to serve as a take-home assignment for an elite engineering agency (Tenex). 
The prompt we are fulfilling is "Better-Perplexity": A web-based chat agent with live internet search capabilities, plus a "creative leap" to demonstrate extreme technical strength.

## 2. The "Creative Leap" (The Architecture)
A standard Perplexity clone just summarizes web results. Our leap is **Persona-Grounded Perplexity**.
We will take live web search results and cross-reference them against our existing Neo4j Knowledge Graph. The agent will synthesize live news with Alex Lieberman's stored mental models to write topical content in his exact voice.

## 3. Current State vs. Target State
* **Current:** A Python script (`ghostwriter.py`) that queries a Neo4j AuraDB via Vector/Cypher search and generates text via Gemini.
* **Target Backend (FastAPI):** We need to wrap the existing logic in a FastAPI server, adding a live Web Search API (like Tavily, Serper, or DuckDuckGo) to the retrieval pipeline.
* **Target Frontend (React):** A sleek, minimalistic React chat interface (built with Vite + Tailwind) that displays chat messages and explicitly cites its sources (differentiating between 🌐 Web Sources and 🧠 Graph Sources).

## 4. Rules of Engagement for the AI
* **No Bloat:** Do not suggest complex auth (OAuth, JWT) or heavy state management (Redux). Keep the stack lean: FastAPI, React, Tailwind.
* **Security:** Ensure all Neo4j URIs, Web Search API keys, and Gemini keys remain strictly in the backend `.env` file. Do not expose them to the React frontend.
* **Iterative Execution:** Do not attempt to build the frontend and backend simultaneously. Wait for the user to provide specific `sprint_x.md` files. Follow the instructions in those files explicitly without hallucinating future steps.
