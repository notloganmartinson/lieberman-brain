import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ddgs import DDGS

from backend.ghostwriter import (
    embed_query,
    retrieve_context,
    get_tone_context,
    generate_content,
    client
)

# Initialize FastAPI App
app = FastAPI(title="Lieberman GraphRAG API", description="Better Perplexity Backend")

# Add CORS Middleware to allow React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

class Source(BaseModel):
    type: str  # "web" or "graph"
    title: str = None
    url: str = None
    label: str = None
    id: str = None

class ChatResponse(BaseModel):
    reply: str
    sources: List[Source]

def get_web_context(query: str, max_results: int = 3) -> tuple[str, List[Dict[str, Any]]]:
    """Fetches live web results via DuckDuckGo and returns formatted context + sources list."""
    logging.info(f"Running web search for: {query}")
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "", []
        
        web_context = "=== WEB CONTEXT ===\n"
        sources = []
        for i, res in enumerate(results):
            title = res.get('title', 'No Title')
            href = res.get('href', '')
            body = res.get('body', '')
            
            web_context += f"Source {i+1}:\nTitle: {title}\nURL: {href}\nSnippet: {body}\n\n"
            sources.append({
                "type": "web",
                "title": title,
                "url": href
            })
        return web_context, sources
    except Exception as e:
        logging.error(f"Web search failed: {e}")
        return "", []

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
        
    prompt = request.prompt
    logging.info(f"Received chat request with prompt: {prompt}")

    # 1. Web Search
    web_context_str, web_sources = get_web_context(prompt)
    
    # 2. Graph Retrieval
    try:
        query_embedding = embed_query(prompt)
        graph_context_str, graph_sources = retrieve_context(query_embedding)
    except Exception as e:
        logging.error(f"Graph retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve graph context.")

    # 3. Tone Context
    tone_str = get_tone_context()

    # 4. Combine Contexts for the Generation System Prompt
    combined_context = f"{web_context_str}\n\n{graph_context_str}"

    # 5. Generate Response using the combined context
    try:
        reply = generate_content(prompt, combined_context, tone_str)
    except Exception as e:
        logging.error(f"Content generation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response.")

    # Combine sources
    all_sources = web_sources + graph_sources

    return ChatResponse(
        reply=reply,
        sources=all_sources
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
