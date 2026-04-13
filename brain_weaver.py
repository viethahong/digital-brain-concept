import os
import json
import re
import time
import urllib.request
import sys

# Paths
WIKI_DIR = "wiki"
STATS_JS = "stats.js"
SYNC_SCRIPT = "brain_sync.py"

def get_env_key(key_name):
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith(key_name + '='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    return os.environ.get(key_name)

def get_existing_titles():
    """Extracts all node titles from stats.js."""
    if not os.path.exists(STATS_JS):
        return []
    try:
        with open(STATS_JS, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove JS variable prefix
            json_str = content.replace('const BRAIN_STATS = ', '').strip().rstrip(';')
            data = json.loads(json_str)
            return [node['title'] for node in data.get('graph', {}).get('nodes', [])]
    except Exception as e:
        print(f"Error reading vocabulary: {e}")
        return []

def get_system_config():
    """Reads system AI configuration from .env."""
    config = {
        'provider': os.environ.get('SYSTEM_AI_PROVIDER', 'gemini'),
        'model': os.environ.get('SYSTEM_AI_MODEL', 'gemini-2.5-flash-lite'),
        'fallback_provider': os.environ.get('SYSTEM_FALLBACK_PROVIDER', 'gemini'),
        'fallback_model': os.environ.get('SYSTEM_FALLBACK_MODEL', 'gemini-2.5-flash-lite')
    }
    # Double check .env file manually
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

def call_ai(prompt, provider, model, api_key, base_url=None):
    """Generic AI caller supporting Gemini and FPT AI."""
    if provider == 'gemini':
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.1}}
        headers = {'Content-Type': 'application/json'}
    else: # FPT AI/OpenAI format
        url = f"{base_url.rstrip('/')}/chat/completions" if base_url else "https://mkp-api.fptcloud.com/v1/chat/completions"
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'api-key': api_key,
            'x-api-key': api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=60)
        result = json.loads(response.read().decode('utf-8'))
        if provider == 'gemini':
            text = result['candidates'][0]['content']['parts'][0]['text'].strip()
        else:
            text = result['choices'][0]['message']['content'].strip()
        
        # Clean up code blocks
        if text.startswith('```'):
            text = re.sub(r'^```\w*\n', '', text)
            text = re.sub(r'\n```$', '', text)
        return True, text.strip()
    except Exception as e:
        return False, str(e)

def filter_vocabulary(content, all_titles, limit=30):
    """Filters the vocabulary to only titles that appear as partial matches or related keywords."""
    # This is a simple pass to avoid overwhelming the AI.
    # We look for keywords from the content in the titles.
    words = set(re.findall(r'\w+', content.lower()))
    relevant = []
    for title in all_titles:
        clean_title = re.sub(r'[\[\]]', '', title).lower()
        title_words = set(re.findall(r'\w+', clean_title))
        if words.intersection(title_words):
            relevant.append(title)
        
    return relevant[:limit]

def weave_links_with_fallback(content, vocabulary):
    config = get_system_config()
    
    # Pass 1: Filter vocabulary to make it more digestible for AI
    filtered_vocab = filter_vocabulary(content, vocabulary)
    
    # FPT Model Chain (Strictly No Gemini)
    fpt_models = ["Llama-3.3-70B-Instruct", "gemma-4-31B-it", "gemma-4-26B-A4B-it"]
    
    success = False
    result = ""
    
    vocab_str = ", ".join(filtered_vocab)
    prompt = f"""Bạn là Quản thư của Digital Brain. Hãy dệt các liên kết tri thức [[Tiêu đề]] vào văn bản dưới đây.

DANH SÁCH TIÊU ĐỀ LIÊN QUAN: [{vocab_str}]

QUY TẮC WEAVER 2.0 (Bắt buộc):
1. CHỈ dệt link cho tối đa 5-7 cụm từ QUAN TRỌNG NHẤT và CÓ Ý NGHĨA nhất. 
2. Dệt link tự nhiên vào trong câu văn. KHÔNG liệt kê link ở cuối bài.
3. Hỗ trợ "Liên kết linh hoạt" (Synonyms): Nếu văn bản có cụm từ tương đồng với Tiêu đề (ví dụ: "chiến lược gia" liên quan đến "Tư vấn chiến lược"), hãy dệt link tới Tiêu đề đó.
4. KHÔNG tự ý tạo link cho những từ không có trong danh sách.
5. Giữ nguyên định dạng Markdown và nội dung nguyên bản.

VĂN BẢN CẦN XỬ LÝ: 
{content}

HÃY TRẢ VỀ TOÀN BỘ NỘI DUNG SAU KHI DỆT LINK:"""

    for model_name in fpt_models:
        print(f"      🤖 Weaving with FPT ({model_name})...")
        api_key = get_env_key('FPT_AI_API_KEY')
        base_url = get_env_key('FPT_BASE_URL')
        
        success, result = call_ai(prompt, "fpt", model_name, api_key, base_url)
        
        # Heuristic Check: If result is too short or just a list, it's a failure
        if success:
            if len(result) < len(content) * 0.4 or result.count('[[') > 15:
                print(f"      ⚠️ Output from {model_name} failed heuristic check. Retrying with next model...")
                success = False
                continue
            break # Success!
        else:
            print(f"      ⚠️ {model_name} failed: {result}. Trying next fallback...")
            time.sleep(1) # Breathe
            
    return success, result
        
    return success, result

def process_weaving(dry_run=False, limit=None, skip=0):
    vocabulary = get_existing_titles()
    print(f"📚 Loaded {len(vocabulary)} existing titles from Brain Index.")
    
    if not vocabulary:
        print("📭 Vocabulary is empty. Run sync first.")
        return

    # Scan for markdown files
    md_files = []
    for root, _, files in os.walk(WIKI_DIR):
        for file in files:
            if file.endswith(".md") and not file.startswith("template"):
                md_files.append(os.path.join(root, file))

    if limit:
        md_files = md_files[:limit]
        print(f"🧪 DRY RUN / TRIAL: Limited to {limit} files.")

    print(f"🕸️ Starting to weave {len(md_files)} files {'(DRY RUN)' if dry_run else ''}...")

    processed_count = 0
    for i, file_path in enumerate(md_files):
        if i < skip:
            continue
        print(f"   ⏳ [{i+1}/{len(md_files)}] Weaving: {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            success, new_content = weave_links_with_fallback(content, vocabulary)
            if success:
                if dry_run:
                    print(f"   🔎 [DRY RUN] Result snippet: {new_content[:100]}...")
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"   ✅ Links woven.")
                processed_count += 1
            else:
                print(f"   ❌ Failed weaving: {new_content}")
            
            # Rate limiting
            time.sleep(1.0)
        except Exception as e:
            print(f"   💥 Error: {e}")

    print(f"\n✨ Weaving complete! Processed {processed_count} files.")
    if not dry_run:
        print("🔄 Running Sync...")
        os.system(f"python3 {SYNC_SCRIPT}")

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    limit = None
    skip = 0
    for arg in sys.argv:
        if arg.startswith("--limit="):
            limit = int(arg.split("=")[1])
        if arg.startswith("--skip="):
            skip = int(arg.split("=")[1])
    
    if skip > 0:
        print(f"⏩ Resuming from index: {skip}")
        
    process_weaving(dry_run=dry_run, limit=limit, skip=skip)
