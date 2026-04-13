import os
import json
import time
import shutil
import urllib.request
import re

# Paths
RAW_DIR = "raw/outside"
ARCHIVE_DIR = "raw/archive"
WIKI_BASE = "wiki"
SYNC_SCRIPT = "brain_sync.py"

# Folder mapping for Pillars
FOLDER_MAP = {
    'Knowledge': '01_knowledge',
    'Principles': '02_principles',
    'Philosophies': '03_philosophies',
    'Relationships': '04_relationships',
    'Incubator': '05_incubator'
}

def get_env_key(key_name):
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith(key_name + '='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    return os.environ.get(key_name)

def chunk_text(text, limit=15000):
    """Splits text into chunks of roughly 'limit' characters, breaking at double newlines."""
    if len(text) <= limit:
        return [text]
    
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        
        # Look for a logical break point
        split_at = text.rfind('\n\n', 0, limit)
        if split_at == -1:
            split_at = text.rfind('\n', 0, limit)
        if split_at == -1:
            split_at = limit
        
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
    return chunks

def get_system_config():
    """Reads system AI configuration from .env."""
    config = {
        'provider': os.environ.get('SYSTEM_AI_PROVIDER', 'fpt'),
        'model': os.environ.get('SYSTEM_AI_MODEL', 'Llama-3.3-70B-Instruct'),
        'fpt_chain': ["Llama-3.3-70B-Instruct", "gemma-4-31B-it", "gemma-4-26B-A4B-it"]
    }
    # Double check .env file manually
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key == 'SYSTEM_AI_PROVIDER': config['provider'] = val
                    if key == 'SYSTEM_AI_MODEL': config['model'] = val
    return config
    # Double check .env file manually as fallback
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line:
                    key, val = line.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key in ['SYSTEM_AI_PROVIDER', 'SYSTEM_AI_MODEL', 'SYSTEM_FALLBACK_PROVIDER', 'SYSTEM_FALLBACK_MODEL']:
                        config[key.lower().replace('system_ai_', '').replace('system_', '')] = val
    return config

def call_ai(prompt, provider, model, api_key, base_url=None, system_msg=None):
    """Generic AI caller (Used by ingest step). Strictly FPT-only."""
    if provider != 'fpt':
        return False, "Gemini strictly disabled by policy."
        
    url = f"{base_url.rstrip('/')}/chat/completions" if base_url else "https://mkp-api.fptcloud.com/v1/chat/completions"
    msgs = []
    if system_msg:
        msgs.append({"role": "system", "content": system_msg})
    msgs.append({"role": "user", "content": prompt})
    
    payload = {"model": model, "messages": msgs, "temperature": 0.2}
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'api-key': api_key,
        'User-Agent': 'Mozilla/5.0'
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=120)
        result = json.loads(response.read().decode('utf-8'))
        text = result['choices'][0]['message']['content'].strip()
        
        # Clean markdown code blocks
        if text.startswith('```'):
            text = re.sub(r'^```\w*\n', '', text)
            text = re.sub(r'\n```$', '', text)
        return True, text.strip()
    except Exception as e:
        print(f"      ❌ FPT Error ({model}): {e}")
        return False, str(e)

def ingest_with_fallback(raw_text):
    config = get_system_config()
    
    # Try Primary
    print(f"   🤖 Primary: {config['provider'].upper()} ({config['model']})...")
    api_key = get_env_key('FPT_AI_API_KEY' if config['provider'] == 'fpt' else 'GEMINI_API_KEY')
    base_url = get_env_key('FPT_BASE_URL') if config['provider'] == 'fpt' else None
    
    system_msg = "Bạn là kiến trúc sư tri thức của Digital Brain. Chỉ trả về JSON duy nhất. Không giải thích."
    prompt = f"""Tiêu hóa đoạn văn bản sau thành file Wiki.
DỮ LIỆU: {raw_text}
TRẢ VỀ DUY NHẤT JSON:
{{
   "type": "inside" hoặc "outside",
   "pillar": "Incubator" hoặc tên một trong 4 pillar lõi,
   "slug": "ten-file-slug",
   "content": "Toàn bộ file markdown (có frontmatter chuẩn)"
}}"""

def ingest_with_fallback(raw_text):
    config = get_system_config()
    system_msg = "Bạn là kiến trúc sư tri thức của Digital Brain. Chỉ trả về JSON duy nhất. Không giải thích."
    prompt = f"""Tiêu hóa đoạn văn bản sau thành file Wiki.
DỮ LIỆU: {raw_text}
TRẢ VỀ DUY NHẤT JSON:
{{
   "type": "inside" hoặc "outside",
   "pillar": "Incubator" hoặc tên một trong 4 pillar lõi,
   "slug": "ten-file-slug",
   "content": "Toàn bộ file markdown (có frontmatter chuẩn)"
}}"""

    def try_parse_json(text):
        try:
            # Look for everything between the first { and the last }
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return True, json.loads(json_match.group(0))
            return False, "No JSON found"
        except Exception as e:
            return False, str(e)

    # FPT Only Chain
    for model_name in config['fpt_chain']:
        print(f"   🤖 Trying FPT ({model_name})...")
        api_key = get_env_key('FPT_AI_API_KEY')
        base_url = get_env_key('FPT_BASE_URL')
        
        success, result = call_ai(prompt, "fpt", model_name, api_key, base_url, system_msg)
        
        parsed_success = False
        data = None
        if success:
            parsed_success, data = try_parse_json(result)
            if parsed_success:
                return True, data
            else:
                print(f"      ⚠️ {model_name} failed JSON check. Trying next model...")
        else:
            print(f"      ⚠️ {model_name} failed API call. Trying next model...")
            time.sleep(1)

    return False, "All FPT models failed or returned invalid JSON for this chunk."

def process_all():
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    files = [f for f in os.listdir(RAW_DIR) if f.endswith('.md') or f.endswith('.txt')]
    if not files:
        print("📭 No files found in raw/outside.")
        return

    print(f"🚀 Starting Batch Ingest for {len(files)} files...")

    for filename in files:
        file_path = os.path.join(RAW_DIR, filename)
        print(f"\n📄 Processing: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use chunks for safety
            chunks = chunk_text(content)
            print(f"   -> Split into {len(chunks)} chunks.")

            for i, chunk in enumerate(chunks):
                print(f"   ⏳ Ingesting chunk {i+1}/{len(chunks)}...")
                success, data = ingest_with_fallback(chunk)
                
                if success:
                    pillar = data.get('pillar', 'Incubator')
                    slug = data.get('slug', f"ingested-{int(time.time())}")
                    final_content = data.get('content', '')
                    
                    folder_name = FOLDER_MAP.get(pillar, '05_incubator')
                    target_dir = os.path.join(WIKI_BASE, folder_name)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # Prevent overwriting too easily by adding index if multiple chunks
                    final_slug = f"{slug}-{i}" if len(chunks) > 1 else slug
                    wiki_path = os.path.join(target_dir, f"{final_slug}.md")
                    
                    with open(wiki_path, 'w', encoding='utf-8') as f:
                        f.write(final_content)
                    
                    print(f"   ✅ Saved to: {wiki_path}")
                else:
                    print(f"   ❌ Failed to ingest chunk {i+1}: {data}")
                
                # Small delay to respect rate limits
                time.sleep(1)

            # Move to archive
            dest_path = os.path.join(ARCHIVE_DIR, filename)
            # Handle collision in archive
            if os.path.exists(dest_path):
                dest_path = os.path.join(ARCHIVE_DIR, f"{int(time.time())}_{filename}")
            
            shutil.move(file_path, dest_path)
            print(f"📦 Moved {filename} to Archive.")

        except Exception as e:
            print(f"💥 Error processing {filename}: {str(e)}")

    print("\n✨ Batch Ingest Complete!")
    print("🔄 Running Sync...")
    os.system(f"python3 {SYNC_SCRIPT}")

if __name__ == "__main__":
    import sys
    source_dir = RAW_DIR
    for arg in sys.argv:
        if arg.startswith("--dir="):
            source_dir = arg.split("=")[1]
    
    # Temporarily override RAW_DIR if arg provided
    RAW_DIR = source_dir
    process_all()
