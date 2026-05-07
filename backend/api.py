import logging
import re
from typing import List, Dict, Any, Optional
import json
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ddgs import DDGS
from google.genai import types

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
    access_token: Optional[str] = None

class Source(BaseModel):
    type: str  # "web" or "graph"
    title: str = None
    url: str = None
    label: str = None
    id: str = None

class ChatResponse(BaseModel):
    reply: str
    sources: List[Source]
    new_event: Optional[Dict[str, str]] = None

class IntentSchema(BaseModel):
    intent: str

def classify_intent(prompt: str) -> str:
    """Uses Gemini to deterministically classify intent as RESEARCH or SCHEDULE."""
    try:
        logging.info(f"Classifying intent for prompt: {prompt}")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Classify the intent of the following prompt. It must be either 'RESEARCH' or 'SCHEDULE'. Prompt: {prompt}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=IntentSchema,
                temperature=0.0,
            ),
        )
        # Parse JSON output strictly
        intent_data = json.loads(response.text)
        intent = intent_data.get("intent", "RESEARCH").upper()
        if intent not in ["RESEARCH", "SCHEDULE"]:
            return "RESEARCH"
        return intent
    except Exception as e:
        logging.error(f"Intent classification failed: {e}. Defaulting to RESEARCH.")
        return "RESEARCH"

import time

def get_web_context(query: str, max_results: int = 3) -> tuple[str, List[Dict[str, Any]]]:
    """Fetches live web results via DuckDuckGo and returns formatted context + sources list."""
    logging.info(f"Running web search for: {query}")
    max_retries = 2
    for attempt in range(max_retries + 1):
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
            error_msg = str(e).lower()
            if ("429" in error_msg or "ratelimit" in error_msg) and attempt < max_retries:
                logging.warning(f"Web search rate limited. Retrying in 1.5s... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(1.5)
                continue
            logging.error(f"Web search failed: {e}")
            fallback_context = "=== WEB CONTEXT ===\n[SYSTEM NOTE: Live web search is currently unavailable due to network limits. You must answer relying EXCLUSIVELY on the Graph Context.]\n"
            return fallback_context, []

def fetch_graph_data(prompt: str) -> tuple[str, List[Dict[str, Any]]]:
    """Helper function to run embedding and retrieval sequentially for the thread pool."""
    try:
        query_embedding = embed_query(prompt)
        return retrieve_context(query_embedding)
    except Exception as e:
        logging.error(f"Graph retrieval failed: {e}")
        return "", []

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
        
    prompt = request.prompt
    logging.info(f"Received chat request with prompt: {prompt}")

    # LLM Semantic Router
    intent = classify_intent(prompt)
    is_schedule = (intent == "SCHEDULE")

    if is_schedule:
        logging.info("Intent classified as SCHEDULE. Taking fast path.")
        try:
            reply, new_event = generate_content(prompt, is_schedule_intent=True, access_token=request.access_token)
            # Add visual distinction using Markdown instead of raw HTML
            reply = f"📅 **[Calendar Agent]** {reply}"
        except Exception as e:
            logging.error(f"Content generation failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate response.")
        
        all_sources = []
    else:
        logging.info("Intent classified as RESEARCH. Taking deep path.")
        
        # Parallel I/O Retrieval
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_web = executor.submit(get_web_context, prompt)
            future_graph = executor.submit(fetch_graph_data, prompt)
            
            web_context_str, web_sources = future_web.result()
            graph_context_str, graph_sources = future_graph.result()

        # 3. Tone Context
        tone_str = get_tone_context()

        # 4. Combine Contexts for the Generation System Prompt
        combined_context = f"{web_context_str}\n\n{graph_context_str}"

        # 5. Generate Response using the combined context
        try:
            reply, new_event = generate_content(prompt, combined_context, tone_str, is_schedule_intent=False, access_token=access_token)
        except Exception as e:
            logging.error(f"Content generation failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate response.")

        # Combine sources
        all_sources = web_sources + graph_sources

    return ChatResponse(
        reply=reply,
        sources=all_sources,
        new_event=new_event
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)