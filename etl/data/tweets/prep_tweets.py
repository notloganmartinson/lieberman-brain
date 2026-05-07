import json
import os

TWEETS_FILE = 'dataset_twitter-scraper_2026-05-06_19-54-42-514.json' 
GRAPH_OUTPUT = 'graph_frameworks.txt'
TONE_OUTPUT = 'tone_and_replies.txt'

def split_twitter_data():
    with open(TWEETS_FILE, 'r', encoding='utf-8') as f:
        tweets = json.load(f)

    graph_text = ""
    tone_text = ""
    graph_count = 0
    tone_count = 0

    for tweet in tweets:
        # FAIL-SAFE: If 'text' is null/None, force it to be an empty string
        text = tweet.get('text') or ""
        
        # Route 1: The Brain (GraphRAG) - Deep frameworks
        if len(text) > 80:
            graph_text += f"\n---TWEET---\n{text}\n"
            graph_count += 1
        # Route 2: The Voice (Tone Library) - Quick replies, slang, emojis
        elif len(text) > 0: # Ensures we don't save completely blank strings
            tone_text += f"\n{text}\n"
            tone_count += 1

    # Save the frameworks for Neo4j
    with open(GRAPH_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(graph_text)
        
    # Save the replies for the Ghostwriter Prompt
    with open(TONE_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(tone_text)

    print(f"Data Split Complete!")
    print(f"- Sent {graph_count} deep posts to The Brain (GraphRAG).")
    print(f"- Sent {tone_count} short replies to The Voice (Tone Library).")

if __name__ == "__main__":
    split_twitter_data()
