import os
import json
import re
import time
import urllib.request
import sys

# Paths
WIKI_DIR = "wiki"
INCUBATOR_DIR = os.path.join(WIKI_DIR, "05_incubator")
SYNC_SCRIPT = "brain_sync.py"
WEAVE_SCRIPT = "brain_weaver.py"

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
        print(f"      🤖 Condensing with FPT ({model_name})...")
        payload = {"model": model_name, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
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

def condense_file(file_path):
    print(f"🔬 Condensing: {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip files that are already very short
    if len(content.split()) < 400:
        print(f"   ⏩ Skipping (Already concise: {len(content.split())} words)")
        return True

    prompt = f"""Bạn là Chuyên gia Tinh lọc Tri thức của Digital Brain.
Hãy rút gọn tệp tri thức dưới đây để trở nên súc tích, cô đọng và dễ hấp thụ nhất.

YÊU CẦU:
1. GIỮ NGUYÊN Frontmatter (phần nằm giữa ---).
2. Rút gọn nội dung văn bản xuống còn khoảng 40-50% độ dài hiện tại.
3. Chỉ giữ lại Frameworks, Principles, Key Takeaways và các con số quan trọng.
4. Loại bỏ các đoạn diễn giải lan man, ví dụ lặp lại hoặc câu chữ rườm rà.
5. CẤU TRÚC: Sử dụng Bullet points và Heading để tối ưu hóa việc quét mắt (Skimming).
6. **BẮT BUỘC**: Phải giữ lại TOÀN BỘ các liên kết `[[Tiêu đề]]` đã có sẵn trong văn bản.

VĂN BẢN GỐC:
{content}

HÃY TRẢ VỀ NỘI DUNG MARKDOWN ĐÃ RÚT GỌN:"""

    success, result = call_ai(prompt)
    if success:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"   ✅ Condensed.")
        return True
    else:
        print(f"   ❌ Failed: {result}")
        return False

def run_condensation():
    print("🚀 Starting Incubator Condensation...")
    files = [f for f in os.listdir(INCUBATOR_DIR) if f.endswith(".md") and not f.startswith("template")]
    
    count = 0
    for f in files:
        path = os.path.join(INCUBATOR_DIR, f)
        if condense_file(path):
            count += 1
        time.sleep(1.0) # Rate limiting
    
    print(f"\n✅ Condensed {count} files.")
    print("\n🔄 Running Weaver & Sync to refresh links...")
    os.system(f"python3 {WEAVE_SCRIPT}")
    os.system(f"python3 {SYNC_SCRIPT}")
    print("\n✨ Brain refined and re-woven!")

if __name__ == "__main__":
    run_condensation()
