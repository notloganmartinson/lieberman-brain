import os
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any
from neo4j import GraphDatabase
from google import genai
from google.genai import types
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, GEMINI_API_KEY]):
    raise ValueError("Missing Neo4j or Gemini credentials in environment variables.")

client = genai.Client(api_key=GEMINI_API_KEY)
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

class CalendarTools:
    def __init__(self, access_token: str | None):
        self.access_token = access_token
        self.captured_event = None

    def get_upcoming_meetings(self) -> dict:
        """Fetches the next 10 upcoming events from the user's primary Google Calendar."""
        logging.info("Tool called: get_upcoming_meetings")
        if not self.access_token:
            return {"status": "error", "message": "User must sign in with Google first to access calendar data."}
        try:
            creds = Credentials(token=self.access_token)
            service = build('calendar', 'v3', credentials=creds)
            now = datetime.utcnow().isoformat() + 'Z'
            events_result = service.events().list(calendarId='primary', timeMin=now,
                                                  maxResults=10, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])
            return {"status": "success", "events": [{"id": e['id'], "title": e.get('summary', 'Busy'), "start": e['start'].get('dateTime', e['start'].get('date'))} for e in events]}
        except Exception as e:
            logging.error(f"Calendar list error: {e}")
            return {"status": "error", "message": str(e)}

    def schedule_meeting(self, title: str, time: str) -> dict:
        """Schedules an event on the user's Google Calendar.
        
        Args:
            title: The title of the event.
            time: The ISO 8601 start time of the event including the timezone offset (e.g. '2026-05-08T15:00:00-05:00'). Do NOT use 'Z'.
        """
        logging.info(f"Tool called: schedule_meeting (title: {title}, time: {time})")
        if not self.access_token:
            return {"status": "error", "message": "User must sign in with Google first to schedule a meeting."}
        try:
            creds = Credentials(token=self.access_token)
            service = build('calendar', 'v3', credentials=creds)
            
            event = {
                'summary': title,
                'start': {'dateTime': time},
            }
            
            try:
                dt = datetime.fromisoformat(time.replace('Z', '+00:00'))
                event['end'] = {'dateTime': (dt + timedelta(hours=1)).isoformat()}
            except Exception:
                event['end'] = {'dateTime': time}

            created_event = service.events().insert(calendarId='primary', body=event).execute()
            
            self.captured_event = {"title": title, "date": time.split('T')[0] if 'T' in time else time, "time": time.split('T')[1].replace('Z', '') if 'T' in time else time}
            logging.info(f"Captured schedule_event: {self.captured_event}")
            return {"status": "success", "id": created_event.get('id'), "link": created_event.get('htmlLink')}
        except Exception as e:
            logging.error(f"Calendar insert error: {e}")
            return {"status": "error", "message": str(e)}

    def delete_meeting(self, event_id: str) -> dict:
        """Deletes an event from the user's Google Calendar.
        
        Args:
            event_id: The unique ID of the event to delete. You MUST use get_upcoming_meetings first to find this ID.
        """
        logging.info(f"Tool called: delete_meeting (event_id: {event_id})")
        if not self.access_token:
            return {"status": "error", "message": "User must sign in with Google first to delete a meeting."}
        try:
            creds = Credentials(token=self.access_token)
            service = build('calendar', 'v3', credentials=creds)
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            logging.info(f"Deleted schedule_event with ID: {event_id}")
            return {"status": "success", "message": f"Event {event_id} deleted successfully."}
        except Exception as e:
            logging.error(f"Calendar delete error: {e}")
            return {"status": "error", "message": str(e)}

def embed_query(query: str) -> List[float]:
    logging.info("Embedding the user query...")
    response = client.models.embed_content(
        model='gemini-embedding-2',
        contents=query,
    )
    return response.embeddings[0].values

def embed_chunks(chunks: List[str], batch_size: int = 100) -> List[List[float]]:
    logging.info(f"Embedding {len(chunks)} chunks in batches of {batch_size}...")
    all_embeddings = []
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        response = client.models.embed_content(
            model='gemini-embedding-2',
            contents=batch,
        )
        all_embeddings.extend([e.values for e in response.embeddings])
        
    return all_embeddings

def retrieve_document_context(query_embedding: List[float], session_id: str, top_k: int = 3) -> tuple[str, list]:
    logging.info(f"Querying Neo4j for vector-ranked user document context (session: {session_id})...")
    
    context_str = ""
    sources = []
    with neo4j_driver.session() as session:
        query = """
        MATCH (n:UserDocumentChunk {session_id: $session_id})
        WHERE n.embedding IS NOT NULL
        WITH n, vector.similarity.cosine(n.embedding, $query_embedding) AS score
        ORDER BY score DESC
        LIMIT $top_k
        RETURN n.text AS text, n.filename AS filename, score
        """
        results = session.run(query, top_k=top_k, query_embedding=query_embedding, session_id=session_id).data()
        
        if results:
            context_str += "=== UPLOADED DOCUMENT CONTEXT ===\n"
            for res in results:
                context_str += f"- [From {res['filename']} | Score: {res['score']:.4f}]: {res['text']}\n"
            
            # Deduplicate sources by filename
            unique_filenames = set([res['filename'] for res in results])
            for filename in unique_filenames:
                sources.append({
                    "type": "document",
                    "title": filename,
                    "snippet": f"Vector-matched context retrieved from {filename}"
                })
                
    return context_str, sources

def retrieve_context(query_embedding: List[float], top_k: int = 5) -> tuple[str, list]:
    logging.info("Querying Neo4j for relevant graph context...")
    
    context_str = ""
    sources = []
    with neo4j_driver.session() as session:
        # Step A: Vector Search to find Entry Nodes
        vector_query = """
        CALL db.index.vector.queryNodes('concept_description_embedding', $top_k, $query_embedding)
        YIELD node, score
        RETURN node.id AS id, node.label AS label, node.description AS description, score
        """
        entry_nodes = session.run(vector_query, top_k=top_k, query_embedding=query_embedding).data()
        
        if not entry_nodes:
            logging.warning("No entry nodes found in the vector search.")
            return "", []
        
        entry_node_ids = [n["id"] for n in entry_nodes]
        logging.info(f"Found {len(entry_node_ids)} entry nodes via Vector Search.")
        
        # Step B: Graph Traversal (1-hop)
        graph_query = """
        MATCH (n:Concept)-[r]-(m:Concept)
        WHERE n.id IN $entry_node_ids
        RETURN n.label AS source, type(r) AS relationship, r.justification AS justification, m.label AS target
        LIMIT 50
        """
        traversal_results = session.run(graph_query, entry_node_ids=entry_node_ids).data()
        
        logging.info(f"Traversed {len(traversal_results)} related edges.")
        
        context_str += "=== GRAPH CONTEXT ===\n"
        context_str += "Core Concepts Identified:\n"
        for n in entry_nodes:
            context_str += f"- {n['label']}: {n['description']}\n"
            sources.append({"type": "graph", "label": n['label'], "id": n['id']})
            
        context_str += "\nRelated Concepts & Justifications:\n"
        for r in traversal_results:
            justification = f" (Because: {r['justification']})" if r['justification'] else ""
            context_str += f"- {r['source']} [{r['relationship']}] {r['target']}{justification}\n"
            
    return context_str, sources

def get_tone_context() -> str:
    try:
        tone_file = Path(__file__).resolve().parent.parent / "etl" / "data" / "tweets" / "tone_and_replies.txt"
        if tone_file.exists():
            with open(tone_file, "r", encoding="utf-8") as f:
                return f.read()
        else:
            logging.warning(f"Tone file not found at {tone_file}.")
            return "You are Alex Lieberman. Write with punchy hooks and clear formatting."
    except Exception as e:
        logging.error(f"Error reading tone file: {e}")
        return "You are Alex Lieberman. Write with punchy hooks and clear formatting."

def generate_content(query: str, context: str = "", tone: str = "", is_schedule_intent: bool = False, access_token: str = None, history: list = None, user_timezone: str = "US/Central") -> tuple[str, dict | None]:
    logging.info("Generating content via Gemini...")
    
    if is_schedule_intent:
        today = datetime.now().strftime("%A, %B %d, %Y")
        system_prompt = f"You are a calendar assistant. Today is {today}. The user's timezone is currently {user_timezone}. All times requested should be interpreted and scheduled in this timezone. Extract the details, use the tools, and reply with a single, short confirmation sentence. Do not elaborate or use frameworks."
    else:
        system_prompt = f"""You are the 'Content Consigliere' AI representing Alex Lieberman (Co-founder of Morning Brew, Tenex).
Your task is to respond to the user's prompt by generating content that mimics Alex's authentic voice, cadence, and mental models.

### GRAPH CONTEXT:
You MUST base your arguments, facts, and frameworks primarily on the following extracted knowledge graph context:
{context}

### TONE & STYLE CONTEXT:
You MUST mimic the formatting, hook style, vocabulary, and conversational tone found in these examples:
{tone}

### CONFLICT RESOLUTION RULES:
- **Rule 1:** Graph > Web for Philosophy (The Graph Context is the ultimate source of truth for Alex's frameworks, mental models, and opinions).
- **Rule 2:** Web > Graph for Recent Facts (Trust the Web Context only for highly recent or time-sensitive data, news, or trends).
- **Rule 3:** If the Graph Context and Web Context massively conflict, synthesize them naturally in your writing (e.g., "The internet thinks X, but my framework is Y").

### INSTRUCTIONS:
- Write in the first person ("I", "my") as Alex Lieberman.
- Do NOT explicitly mention that you are using a graph or context provided. Just speak naturally.
- Focus on punchy hooks, clear formatting, and valuable takeaways typical of high-level B2B creators.
- Address the user's prompt directly using the context provided.
"""

    calendar_tools = CalendarTools(access_token)

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
        tools=[calendar_tools.get_upcoming_meetings, calendar_tools.schedule_meeting, calendar_tools.delete_meeting],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
    )

    # Multi-turn Content construction
    contents = []
    if history:
        for msg in history:
            contents.append(types.Content(
                role=msg["role"],
                parts=[types.Part.from_text(text=msg["content"])]
            ))
    
    # Append the latest message
    contents.append(types.Content(
        role="user",
        parts=[types.Part.from_text(text=query)]
    ))

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=config,
            )
            return response.text, calendar_tools.captured_event
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                logging.warning(f"Model busy (503). Retrying in {2**(attempt+1)}s...")
                time.sleep(2**(attempt+1))
                continue
            raise e

def store_document_chunks(session_id: str, filename: str, chunks: List[str]):
    logging.info(f"Storing {len(chunks)} chunks for file {filename} (session: {session_id}) using batching...")
    
    vectors = embed_chunks(chunks)
    payload = []
    for chunk, vector in zip(chunks, vectors):
        payload.append({
            "id": uuid.uuid4().hex,
            "text": chunk,
            "vector": vector
        })

    # Ensure Vector Index exists
    with neo4j_driver.session() as session:
        session.run(
            "CREATE VECTOR INDEX user_document_chunk_embedding IF NOT EXISTS "
            "FOR (n:UserDocumentChunk) ON (n.embedding) "
            "OPTIONS {indexConfig: {`vector.dimensions`: 768, `vector.similarity_function`: 'cosine'}}"
        )
        
        # Batch insert chunks
        cypher = """
        UNWIND $payload AS batch
        MERGE (n:UserDocumentChunk {id: batch.id})
        SET n.session_id = $session_id,
            n.filename = $filename,
            n.text = batch.text
        WITH n, batch
        CALL db.create.setNodeVectorProperty(n, 'embedding', batch.vector)
        RETURN count(n)
        """
        session.run(
            cypher,
            payload=payload,
            session_id=session_id,
            filename=filename
        )
            
    logging.info("Chunks successfully stored in Neo4j.")

def main():
    parser = argparse.ArgumentParser(description="GraphRAG Content Engine for Alex Lieberman")
    parser.add_argument("--prompt", type=str, default="Write a LinkedIn post about why newsletters are a moat against algorithmic risk", help="The content generation prompt.")
    args = parser.parse_args()
    
    print(f"\n--- SPRINT 4: GraphRAG Agent ---")
    print(f"Prompt: '{args.prompt}'\n")
    
    try:
        # 1. Embed Prompt
        query_embedding = embed_query(args.prompt)
        
        # 2. Retrieve Graph Context
        context_str, sources = retrieve_context(query_embedding)
        
        # 3. Retrieve Tone Context
        tone_str = get_tone_context()
        
        # 4. Generate Output
        final_content, new_event = generate_content(args.prompt, context_str, tone_str)
        
        print("\n================== GENERATED CONTENT ==================\n")
        print(final_content)
        if new_event:
            print(f"\n[Tool Triggered] Event Scheduled: {new_event}")
        print("\n=======================================================\n")
        
    except Exception as e:
        logging.error(f"Agent execution failed: {e}")

if __name__ == "__main__":
    main()