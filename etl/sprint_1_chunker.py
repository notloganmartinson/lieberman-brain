import os
import json
import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter

def create_chunks():
    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=2000,
        chunk_overlap=200,
        separators=["---TWEET---", "---LINKEDIN POST---", "\n\n", "\n", " ", ""]
    )
    
    all_chunks = []
    
    # Process YouTube Transcripts
    youtube_dir = "./data/youtube"
    if os.path.exists(youtube_dir):
        for filename in os.listdir(youtube_dir):
            if filename.endswith(".txt") and filename != "clean_yt_transcripts.txt":
                filepath = os.path.join(youtube_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                chunks = text_splitter.split_text(content)
                for chunk in chunks:
                    all_chunks.append({
                        "chunk_id": str(uuid.uuid4()),
                        "source": "YouTube",
                        "source_file": filename,
                        "text": chunk
                    })
                    
    # Process Twitter Frameworks
    twitter_file = "./data/tweets/graph_frameworks.txt"
    if os.path.exists(twitter_file):
        with open(twitter_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        chunks = text_splitter.split_text(content)
        for chunk in chunks:
            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "source": "Twitter",
                "source_file": os.path.basename(twitter_file),
                "text": chunk
            })
            
    # Process LinkedIn Posts
    linkedin_file = "./data/linkedin/clean_linkedin.txt"
    if os.path.exists(linkedin_file):
        with open(linkedin_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        chunks = text_splitter.split_text(content)
        for chunk in chunks:
            all_chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "source": "LinkedIn",
                "source_file": os.path.basename(linkedin_file),
                "text": chunk
            })
            
    # Export to JSON
    output_file = "./data/processed/chunked_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully generated {len(all_chunks)} chunks and saved to {output_file}.")

if __name__ == "__main__":
    print("Starting semantic chunking process...")
    create_chunks()
