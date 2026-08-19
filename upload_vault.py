import os
import time
from google import genai
from dotenv import load_dotenv

# 1. Unlock the secure vault
load_dotenv()

# Initialize the modern AI Client (it automatically detects your API key)
client = genai.Client()

vault_dir = "static"

print("--- INITIATING VAULT UPLOAD ---")

# 2. Crawl the static folder and upload every PDF
for filename in os.listdir(vault_dir):
    if filename.endswith(".pdf"):
        file_path = os.path.join(vault_dir, filename)
        print(f"Uploading: {filename}...")
        
        try:
            # Upload the document to Google's secure servers
            uploaded_file = client.files.upload(file=file_path)
            print(f"Success! Neural ID: {uploaded_file.name}")
            
            # Pause for 2 seconds to avoid rate limit crashes
            time.sleep(2)
        except Exception as e:
            print(f"Failed to upload {filename}: {e}")

print("--- UPLOAD SEQUENCE COMPLETE ---")