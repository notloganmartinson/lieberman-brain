import json
import os

LINKEDIN_FILE = 'dataset_linkedin-post_2026-05-06_20-12-00-847.json' 
CLEAN_OUTPUT = 'clean_linkedin.txt'

def clean_linkedin_data():
    with open(LINKEDIN_FILE, 'r', encoding='utf-8') as f:
        posts = json.load(f)

    clean_text = ""
    valid_post_count = 0

    for post in posts:
        # Grabs the main post text, ignores everything else
        text = post.get('text') or ""
        
        # Filter: LinkedIn posts are long. If it's under 100 chars, it's likely just a shared link or noise.
        if len(text) > 100:
            clean_text += f"\n---LINKEDIN POST---\n{text}\n"
            valid_post_count += 1

    with open(CLEAN_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(clean_text)

    print(f"LinkedIn Data Cleaned!")
    print(f"- Extracted {valid_post_count} high-value professional frameworks.")
    print(f"- Saved to {CLEAN_OUTPUT}. Ready for Gemini CLI extraction.")

if __name__ == "__main__":
    clean_linkedin_data()
