import os
import re

# Set the path to your youtube folder
YOUTUBE_DIR = "./youtube"

def clean_vtt_files():
    for filename in os.listdir(YOUTUBE_DIR):
        if filename.endswith(".vtt"):
            filepath = os.path.join(YOUTUBE_DIR, filename)
            
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

            # Remove WEBVTT header and kind/Language metadata
            content = re.sub(r'WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
            # Remove timestamp lines (e.g., 00:00:00.000 --> 00:00:02.000)
            content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*\n', '', content)
            # Remove subtitle alignment tags (like <c> or <00:00:00>)
            content = re.sub(r'<[^>]+>', '', content)
            # Clean up excessive newlines
            content = re.sub(r'\n+', ' ', content).strip()

            # Save as a clean .txt file
            new_filepath = os.path.join(YOUTUBE_DIR, filename.replace(".vtt", ".txt"))
            with open(new_filepath, 'w', encoding='utf-8') as new_file:
                new_file.write(content)

            # Optional: Delete the original .vtt file to keep the folder clean
            os.remove(filepath)
            
            print(f"Cleaned and converted: {filename}")

if __name__ == "__main__":
    print("Starting transcript cleanup...")
    clean_vtt_files()
    print("All YouTube transcripts are now clean text!")
