import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Unlock the secure vault and load environment variables
load_dotenv()

# 2. Initialize the Modern Google GenAI Client
client = genai.Client()

# 3. Define the Infinite Box Theory System Persona
ibt_instructions = """
You are the Infinite Box Theory (IBT) Neural Assistant. 
You must analyze all cosmological and physical queries strictly through the lens of the Infinite Box Theory. 
Your primary source of truth is the provided document vault. Base your answers on the hydrodynamic blueprints, 
metric expansion models, and mathematical proofs contained within these files.
Use terms like Hydrodynamic Topography, Refractive Phase Drag, Ambient Loom, Metric Expansion, and Displacement Tension.
Always remember: the 'box' in Infinite Box Theory functions as a metaphor rather than a literal physical enclosure.
"""

# 4. Initialize the Flask Application
app = Flask(__name__)

# ---------------------------------------------------------
# NEW CACHING SYSTEM: Read the vault ONCE on startup
# ---------------------------------------------------------
print("Waking up the AI and caching the Infinite Box Theory vault... (This takes a moment)")
vault_files = list(client.files.list())

# Create a 24-hour active memory cache
ibt_cache = client.caches.create(
    model='gemini-3.1-pro-preview',
    config=types.CreateCachedContentConfig(
        contents=vault_files,
        system_instruction=ibt_instructions,
        ttl="86400s" # Keeps the memory hot for 24 hours
    )
)
print(f"Vault cached successfully! Ready for rapid queries.")
# ---------------------------------------------------------

@app.route('/')
def home():
    return render_template('index.html')

# 5. Pipeline for processing queries using the Hot Cache
@app.route('/ask_gemini', methods=['POST'])
def ask_gemini():
    data = request.json
    user_prompt = data.get('prompt')
    
    if not user_prompt:
        return jsonify({'error': 'No query provided'}), 400
        
    try:
        # ATTEMPT 1: Query the pre-loaded cache directly (Lightning Fast)
        response = client.models.generate_content(
            model='gemini-3.1-pro-preview',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                cached_content=ibt_cache.name,
                temperature=0.2
            )
        )
        return jsonify({'response': response.text})
        
    except Exception as e:
        # FALLBACK: If the cache drops, route to 3.5 Flash using the old raw-file method
        print(f"Primary Cache Failed: {e}. Rerouting to 3.5 Flash...")
        
        try:
            query_package = vault_files + [user_prompt]
            fallback_response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=query_package,
                config=types.GenerateContentConfig(
                    system_instruction=ibt_instructions,
                    temperature=0.2
                )
            )
            return jsonify({'response': fallback_response.text})
        except Exception as fallback_e:
            return jsonify({'error': str(fallback_e)}), 500

# 6. Server Initialization
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
# Triggering live build