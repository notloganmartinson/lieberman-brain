import logging
import re
import time
import os
import httpx
from typing import List, Dict, Any, Optional
import json
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.responses import JSONResponse
import filetype
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ddgs import DDGS
from google.genai import types
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from backend.ghostwriter import (
    embed_query,
    retrieve_context,
    retrieve_document_context,
    get_tone_context,
    generate_content,
    client,
    store_document_chunks,
    neo4j_driver
)
from backend.document_parser import process_file

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    logging.info("Shutting down Neo4j driver connections...")
    neo4j_driver.close()

# Initialize FastAPI App
app = FastAPI(title="Lieberman GraphRAG API", description="Better Perplexity Backend", lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled Exception: {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# Add CORS Middleware to allow React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://lieberman-brain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    if request.url.path == "/upload":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024: # 10 MB limit
            return JSONResponse(status_code=413, content={"detail": "Payload too large."})
    return await call_next(request)

class ChatRequest(BaseModel):
    prompt: str
    session_id: str
    access_token: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = []
    user_timezone: Optional[str] = "US/Central"

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

def fetch_graph_data(query_embedding: List[float]) -> tuple[str, List[Dict[str, Any]]]:
    """Helper function to run retrieval sequentially for the thread pool using pre-computed embedding."""
    try:
        return retrieve_context(query_embedding)
    except Exception as e:
        logging.error(f"Graph retrieval failed: {e}")
        return "", []

def fetch_document_data(query_embedding: List[float], session_id: str) -> tuple[str, List[Dict[str, Any]]]:
    """Helper function to retrieve user document context for the thread pool using pre-computed embedding."""
    try:
        return retrieve_document_context(query_embedding, session_id)
    except Exception as e:
        logging.error(f"Document retrieval failed: {e}")
        return "", []

@app.post("/upload")
@limiter.limit("3/minute")
async def upload_document(request: Request, session_id: str = Form(...), file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        
        # Magic Bytes Verification
        kind = filetype.guess(file_bytes)
        if kind is not None:
            if kind.mime.startswith("application/x-") or kind.mime in ["application/x-msdownload", "application/x-executable"]:
                raise HTTPException(status_code=415, detail="Unsupported or malicious file type detected.")
            # Alternatively, specifically whitelist allowed mime types
            allowed_mimes = ["application/pdf", "text/plain", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
            if kind.mime not in allowed_mimes and not kind.mime.startswith("text/") and not kind.mime.startswith("image/"):
                raise HTTPException(status_code=415, detail=f"File type {kind.mime} is not supported.")

        chunks = await run_in_threadpool(process_file, file.filename, file_bytes)
        await run_in_threadpool(store_document_chunks, session_id, file.filename, chunks)
        return {"status": "success", "filename": file.filename, "chunks_processed": len(chunks)}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to process upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
def chat_endpoint(request: Request, payload: ChatRequest):
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
        
    prompt = payload.prompt
    logging.info(f"Received chat request with prompt: {prompt}")

    # Secure Token Extraction
    auth_header = request.headers.get("Authorization")
    access_token = payload.access_token
    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ")[1]

    # Token Validation
    if access_token:
        try:
            with httpx.Client() as client:
                resp = client.get(f"https://oauth2.googleapis.com/tokeninfo?access_token={access_token}", timeout=5.0)
                if resp.status_code != 200:
                    logging.warning(f"Token validation failed with status {resp.status_code}")
                    raise HTTPException(status_code=401, detail="Invalid or expired authentication token")
                
                token_data = resp.json()
                expected_aud = os.environ.get("GOOGLE_CLIENT_ID")
                if expected_aud and token_data.get("aud") != expected_aud:
                    logging.warning(f"Token validation failed: audience mismatch")
                    raise HTTPException(status_code=401, detail="Invalid or expired authentication token")
        except httpx.RequestError as e:
            logging.error(f"Network error during token validation: {e}")
            raise HTTPException(status_code=500, detail="Authentication service unavailable")

    # LLM Semantic Router
    intent = classify_intent(prompt)
    is_schedule = (intent == "SCHEDULE")

    if is_schedule:
        logging.info("Intent classified as SCHEDULE. Taking fast path.")
        try:
            reply, new_event = generate_content(prompt, is_schedule_intent=True, access_token=access_token, history=payload.history)
            # Add visual distinction using Markdown instead of raw HTML
            reply = f"📅 **[Calendar Agent]** {reply}"
        except Exception as e:
            logging.error(f"Content generation failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate response.")
        
        all_sources = []
    else:
        logging.info("Intent classified as RESEARCH. Taking deep path.")
        
        # Optimize: Compute embedding once and share across parallel tasks
        query_embedding = embed_query(prompt)

        # Parallel I/O Retrieval
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_web = executor.submit(get_web_context, prompt)
            future_graph = executor.submit(fetch_graph_data, query_embedding)
            future_doc = executor.submit(fetch_document_data, query_embedding, payload.session_id)
            
            web_context_str, web_sources = future_web.result()
            graph_context_str, graph_sources = future_graph.result()
            doc_context_str, doc_sources = future_doc.result()

        # 3. Tone Context
        tone_str = get_tone_context()

        # 4. Combine Contexts for the Generation System Prompt
        combined_context = f"{web_context_str}\n\n{graph_context_str}\n\n{doc_context_str}"

        # 5. Generate Response using the combined context
        try:
            reply, new_event = generate_content(prompt, combined_context, tone_str, is_schedule_intent=False, access_token=access_token, history=payload.history, user_timezone=payload.user_timezone)
        except Exception as e:
            logging.error(f"Content generation failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate response.")

        # Combine sources
        all_sources = web_sources + graph_sources + doc_sources

    return ChatResponse(
        reply=reply,
        sources=all_sources,
        new_event=new_event
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
