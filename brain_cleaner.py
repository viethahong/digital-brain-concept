import os
import json
import re
import time
import urllib.request
import sys

# Paths
WIKI_DIR = "wiki"
INCUBATOR_DIR = os.path.join(WIKI_DIR, "05_incubator")
ARCHIVE_DIR = os.path.join(WIKI_DIR, "Archive")
SYNC_SCRIPT = "brain_sync.py"
WEAVE_SCRIPT = "brain_weaver.py"

# Predefined clusters (Person-based)
CLUSTERS = {
    "Elon Musk": ["elon", "musk"],
    "Naval Ravikant": ["naval", "ravikant"],
    "Alex Hormozi": ["hormozi", "100m", "leads", "offers", "money-models"],
    "Evan Spiegel & Snapchat": ["spiegel", "evan", "snapchat", "snap-ai"]
}

def get_env_key(key_name):
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith(key_name + '='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    return os.environ.get(key_name)

def call_ai(prompt):
    """Calls the primary AI with fallbacks within FPT (No Gemini)."""
    api_key = get_env_key('FPT_AI_API_KEY')
    base_url = get_env_key('FPT_BASE_URL') or 'https://mkp-api.fptcloud.com/v1'
    
    fpt_models = ["Llama-3.3-70B-Instruct", "gemma-4-31B-it", "gemma-4-26B-A4B-it"]
    
    for model_name in fpt_models:
        print(f"      🤖 Processing with FPT ({model_name})...")
        payload = {"model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'api-key': api_key,
            'x-api-key': api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        req = urllib.request.Request(f"{base_url.rstrip('/')}/chat/completions", data=json.dumps(payload).encode('utf-8'), headers=headers)
        try:
            response = urllib.request.urlopen(req, timeout=300)
            result = json.loads(response.read().decode('utf-8'))
            text = result['choices'][0]['message']['content'].strip()
            
            # Clean markdown code blocks
            if text.startswith('```'):
                text = re.sub(r'^```\w*\n', '', text)
                text = re.sub(r'\n```$', '', text)
            return True, text.strip()
        except Exception as e:
            print(f"      ⚠️ {model_name} failed: {e}. Trying next...")
            time.sleep(1)
            
    return False, "All FPT models failed."

def slugify(text):
    return text.lower().replace(' ', '-').replace('&', 'and')

def synthesize_cluster(name, files):
    print(f"🧬 Synthesizing cluster: {name} ({len(files)} files)")
    combined_content = ""
    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            combined_content += f"\n\n--- Source: {os.path.basename(fpath)} ---\n"
            combined_content += f.read()

    prompt = f"""Bạn là Chuyên gia Tổng hợp Tri thức của Digital Brain.
Hãy hợp nhất bộ tri thức dưới đây về nhân vật/chủ đề: {name}.

YÊU CẦU:
1. Hợp nhất thành 1 file Markdown DUY NHẤT.
2. Cấu trúc lại một cách logic bằng Heading (H1, H2, H3). Chia thành các phần như: "Tiểu sử & Sự nghiệp", "Triết lý sống", "Nguyên tắc kinh doanh", "Khung tư duy (Frameworks)", v.v.
3. Loại bỏ hoàn toàn các nội dung lặp lại nhưng phải GIỮ LẠI toàn bộ các ý tưởng độc đáo, con số và bài học cụ thể.
4. Giọng văn: Nghiêm túc, súc tích, mang tính đúc kết.
5. Tạo FRONTMATTER đầy đủ:
   ---
   title: "{name}"
   pillar: Incubator
   status: "evergreen"
   level: "1_Biet"
   tags: [synthesis, {slugify(name)}]
   ---

DỮ LIỆU ĐẦU VÀO:
{combined_content}

HÃY TRẢ VỀ NỘI DUNG MARKDOWN HOÀN CHỈNH:"""

    success, result = call_ai(prompt)
    if success:
        # Save Master Seed
        filename = f"{slugify(name)}.md"
        master_path = os.path.join(INCUBATOR_DIR, filename)
        with open(master_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✅ Master Seed Created: {master_path}")
        
        # Archive originals
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        for fpath in files:
            new_path = os.path.join(ARCHIVE_DIR, os.path.basename(fpath))
            try:
                os.rename(fpath, new_path)
            except:
                os.remove(fpath) # For duplicates or conflicts
        print(f"📦 Archived {len(files)} fragments.")
        return True
    else:
        print(f"❌ Failed synthesis for {name}: {result}")
        return False

def discover_clusters():
    """Groups files based on predefined CLUSTERS keys."""
    files = [f for f in os.listdir(INCUBATOR_DIR) if f.endswith(".md") and not f.startswith("template")]
    found_clusters = {k: [] for k in CLUSTERS}
    
    for f in files:
        path = os.path.join(INCUBATOR_DIR, f)
        for name, keywords in CLUSTERS.items():
            if any(kw in f.lower() for kw in keywords):
                found_clusters[name].append(path)
                break # Assign to first matching cluster
    
    # Filter out clusters with < 2 files (no need to merge)
    return {k: v for k, v in found_clusters.items() if len(v) >= 2}

if __name__ == "__main__":
    print("🚀 Starting Incubator Optimization...")
    clusters = discover_clusters()
    if not clusters:
        print("📭 No clusters found to optimize.")
        sys.exit(0)

    for name, files in clusters.items():
        synthesize_cluster(name, files)

    print("\n🔄 Running Sync & Weaver...")
    os.system(f"python3 {SYNC_SCRIPT}")
    os.system(f"python3 {WEAVE_SCRIPT}")
    print("\n✨ Optimization Complete!")
