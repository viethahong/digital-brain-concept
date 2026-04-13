import http.server
import socketserver
import json
import os
import re
import urllib.request
import urllib.error

PORT = 8080

def get_env_key(key_name):
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith(key_name + '='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    return os.environ.get(key_name)

def get_gemini_key():
    return get_env_key('GEMINI_API_KEY')

def get_relevant_context(query, top_k=7):
    """
    RAG Implementation:
    1. Always includes Core Files (Principles, Philosophies, Frameworks).
    2. Scores other files based on keyword relevance to the user query.
    """
    core_folders = ["02_principles", "03_philosophies"]
    context_parts = []
    scored_files = []
    
    # Pre-process query keywords
    keywords = re.findall(r'\w+', query.lower())
    stop_words = {'là', 'của', 'với', 'cho', 'trong', 'được', 'và', 'cái', 'này', 'the', 'and', 'for', 'with', 'what', 'how'}
    query_keywords = [w for w in keywords if w not in stop_words and len(w) > 1]

    for root, dirs, files in os.walk("wiki"):
        for file in files:
            if not file.endswith(".md") or file.startswith("template"):
                continue
            
            file_path = os.path.join(root, file)
            is_core = any(folder in file_path for folder in core_folders) or "framework" in file.lower()
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    if is_core:
                        # ALWAYS add core files to context
                        context_parts.append(f"--- CORE FILE: {file_path} ---\n{content}\n")
                    else:
                        # SCORE other files
                        score = 0
                        content_lower = content.lower()
                        for kw in query_keywords:
                            if kw in content_lower:
                                score += content_lower.count(kw)
                        
                        if score > 0:
                            scored_files.append((score, file_path, content))
            except Exception:
                pass

    # Sort scored files and take TOP K
    scored_files.sort(key=lambda x: x[0], reverse=True)
    for score, path, content in scored_files[:top_k]:
        # Limit content size per file to avoid blowups
        safe_content = content[:8000] + "..." if len(content) > 8000 else content
        context_parts.append(f"--- RELEVANT FILE (Score {score}): {path} ---\n{safe_content}\n")

    return "\n".join(context_parts)

def chat_processor(provider, model, messages, system_prompt):
    if provider == 'gemini':
        # ... (Gemini logic)
        api_key = get_env_key('GEMINI_API_KEY')
        if not api_key: return False, "Missing GEMINI_API_KEY in .env"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            
        formatted_messages = []
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            formatted_messages.append({"role": role, "parts": [{"text": m["content"]}]})
            
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": formatted_messages,
            "generationConfig": {"temperature": 0.7}
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        try:
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode('utf-8'))
            text = result['candidates'][0]['content']['parts'][0]['text']
            return True, text
        except Exception as e:
            return False, f"Gemini API Error: {str(e)}"
            
    elif provider == 'fpt':
        api_key = get_env_key('FPT_AI_API_KEY')
        base_url = get_env_key('FPT_BASE_URL') or 'https://mkp-api.fptcloud.com/v1'
        if not api_key: return False, "Missing FPT_AI_API_KEY in .env"
        
        target_suffix = "/chat/completions"
        if target_suffix in base_url:
            url = base_url
        else:
            url = f"{base_url.rstrip('/')}{target_suffix}"
            
        print(f"📡 Calling FPT AI: {url}")
        
        msgs = [{"role": "system", "content": system_prompt}] + messages
        payload = {"model": model, "messages": msgs, "temperature": 0.7}
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'api-key': api_key,
            'x-api-key': api_key,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        try:
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode('utf-8'))
            text = result['choices'][0]['message']['content']
            return True, text
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            return False, f"FPT AI API Error: {e.code} {e.reason}. Body: {error_body}"
        except urllib.error.URLError as e:
            return False, f"FPT AI Connectivity Error: {str(e.reason)}. Check FPT_BASE_URL (Current: {url})"
        except Exception as e:
            return False, f"FPT AI API Error: {str(e)}"
            
    return False, "Unknown provider"

def get_fpt_config():
    return {
        "api_key": get_env_key('FPT_AI_API_KEY'),
        "base_url": get_env_key('FPT_BASE_URL') or 'https://mkp-api.fptcloud.com/v1',
        "chain": ["Llama-3.3-70B-Instruct", "gemma-4-31B-it", "gemma-4-26B-A4B-it"]
    }

def call_fpt_chain(prompt, system_msg=None, temperature=0.2):
    config = get_fpt_config()
    for model_name in config["chain"]:
        url = f"{config['base_url'].rstrip('/')}/chat/completions"
        msgs = []
        if system_msg: msgs.append({"role": "system", "content": system_msg})
        msgs.append({"role": "user", "content": prompt})
        
        payload = {"model": model_name, "messages": msgs, "temperature": temperature}
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {config["api_key"]}',
            'api-key': config["api_key"],
            'User-Agent': 'Mozilla/5.0'
        }
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
        try:
            response = urllib.request.urlopen(req, timeout=60)
            result = json.loads(response.read().decode('utf-8'))
            return True, result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"      ⚠️ FPT Fallback: {model_name} failed: {e}")
            time.sleep(1)
    return False, "All FPT models failed."

def evaluate_with_fpt(seed_content, synthesis):
    prompt = f"""Bạn là một Giám khảo học thuật khắt khe. Nhiệm vụ: Chấm điểm bài thu hoạch tri thức.
    NỘI DUNG GỐC: {seed_content}
    BÀI LÀM CỦA HỌC VIÊN: {synthesis}
    ĐÁNH GIÁ: Học viên có hiểu đúng bản chất không? Trả lời DUY NHẤT một chuỗi JSON hợp lệ theo format sau:
    {{
      "score": (số từ 0-100),
      "level": "1_Biet", "2_Hieu" hoặc "3_Hanh",
      "feedback": "Nhận xét",
      "missing_concepts": []
    }}"""
    
    success, text = call_fpt_chain(prompt)
    if success:
        try:
            # Clean up possible Markdown code blocks
            if text.startswith('```json'): text = text[7:]
            if text.startswith('```'): text = text[3:]
            if text.endswith('```'): text = text[:-3]
            data = json.loads(text.strip())
            return data.get('score', 0), data.get('feedback', ''), data.get('level', '1_Biet'), data.get('missing_concepts', [])
        except: pass
    return 0, "Lỗi xử lý kết quả AI", "1_Biet", []

def ingest_with_fpt(raw_text):
    prompt = f"""Bạn là kiến trúc sư tri thức của Digital Brain. Tiêu hóa dữ liệu thô sau:
    {raw_text}
    TRẢ VỀ DUY NHẤT JSON:
    {{
       "type": "inside" hoặc "outside",
       "pillar": "Incubator" hoặc tên pillar core,
       "slug": "ten-file",
       "content": "markdown content"
    }}"""
    
    success, text = call_fpt_chain(prompt)
    if success:
        try:
            if text.startswith('```json'): text = text[7:]
            if text.startswith('```'): text = text[3:]
            if text.endswith('```'): text = text[:-3]
            return True, json.loads(text.strip())
        except: pass
    return False, "AI failed to parse ingestion"

class BrainHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def guess_type(self, path):
        if path.endswith(".md"):
            return "text/plain"
        return super().guess_type(path)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        if self.path == '/promote':
            file_path = data.get('file_path')
            synthesis = data.get('synthesis')

            success, message, new_level, score, missing = self.promote_file(file_path, synthesis)

            self.send_response(200 if success else 400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "success": success, 
                "message": message, 
                "level": new_level,
                "score": score,
                "missing": missing
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif self.path == '/ingest':
            raw_text = data.get('content')
            success, result_or_err = ingest_with_fpt(raw_text)
            
            if success:
                res_data = result_or_err
                t = res_data.get('type', 'outside')
                p = res_data.get('pillar', 'Incubator')
                slug = res_data.get('slug', 'untitled')
                content = res_data.get('content', '')
                
                # Setup paths
                import time
                timestamp = int(time.time())
                raw_dir = f"raw/{t}"
                os.makedirs(raw_dir, exist_ok=True)
                raw_path = f"{raw_dir}/{slug}_{timestamp}.txt"
                
                # Determine folder mapping
                folder_map = {
                    'Knowledge': '01_knowledge',
                    'Principles': '02_principles',
                    'Philosophies': '03_philosophies',
                    'Relationships': '04_relationships',
                    'Incubator': '05_incubator'
                }
                wk_folder = folder_map.get(p, '05_incubator')
                wiki_path = f"wiki/{wk_folder}/{slug}.md"
                
                # Save raw backup
                with open(raw_path, 'w', encoding='utf-8') as f:
                    f.write(raw_text)
                
                # Save structured wiki
                os.makedirs(f"wiki/{wk_folder}", exist_ok=True)
                with open(wiki_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                os.system("python3 brain_sync.py")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps({"success": True, "path": wiki_path, "type": t}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": result_or_err}).encode('utf-8'))

        elif self.path == '/chat':
            provider = data.get('provider', 'fpt')
            model = data.get('model', 'Llama-3.3-70B-Instruct')
            messages = data.get('messages', [])
            
            # Extract last user message for RAG scoring
            user_query = ""
            for msg in reversed(messages):
                if msg["role"] == "user":
                    user_query = msg["content"]
                    break

            brain_context = get_relevant_context(user_query)
            system_prompt = f"Bạn là trợ lý AI nội bộ của hệ thống Digital Brain.\nQuy tắc:\n1. Nguồn dữ liệu duy nhất của bạn là kho tri thức cục bộ.\n2. Bạn PHẢI ưu tiên đọc các file có nhãn 'CORE FILE' vì chúng chứa nguyên tắc và triết lý sống của người dùng.\n3. Trả lời dựa trên các file RELEVANT FILE được cung cấp.\n4. Trả lời chi tiết, dẫn chiếu đến các File liên quan nếu có.\n5. Nếu thông tin không có trong kho gốc, hãy nói rõ là 'Thông tin này không có trong bộ não số' trước khi trả lời theo kiến thức ngoài.\n\n--- KHO TRI THỨC (CỐT LÕI & LIÊN QUAN) ---\n{brain_context}"

            success, response_text = chat_processor(provider, model, messages, system_prompt)

            if success:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": response_text}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": response_text}).encode('utf-8'))

        elif self.path == '/trash':
            file_path = data.get('file_path')
            if not file_path or not file_path.startswith('wiki/'):
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Invalid file path"}).encode('utf-8'))
                return

            try:
                trash_dir = "wiki/.trash"
                os.makedirs(trash_dir, exist_ok=True)
                
                filename = os.path.basename(file_path)
                import time
                new_filename = f"{int(time.time())}_{filename}"
                new_path = os.path.join(trash_dir, new_filename)
                
                if os.path.exists(file_path):
                    os.rename(file_path, new_path)
                    os.system("python3 brain_sync.py")
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "message": f"Moved to trash: {new_filename}"}).encode('utf-8'))
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "message": "File not found"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode('utf-8'))

        elif self.path == '/save':
            file_path = data.get('file_path')
            content = data.get('content')
            if not file_path or not file_path.startswith('wiki/'):
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": "Invalid file path"}).encode('utf-8'))
                return

            try:
                # Ensure directories exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Trigger sync
                os.system("python3 brain_sync.py")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "message": "Saved successfully"}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode('utf-8'))

    def promote_file(self, file_path, synthesis):
        if not os.path.exists(file_path):
            return False, f"File {file_path} not found.", "1_Biet"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # The Gatekeeper check (Using FPT Chain)
            score, feedback, ai_level, missing = evaluate_with_fpt(content, synthesis)

            # 1. Update File Content
            # Find or Create Connection Block
            marker = "## 🧠 Chiêm nghiệm & Kết nối (Inside Connect)"
            if marker in content:
                parts = content.split(marker)
                base_content = parts[0].strip()
                # If score is 100, we'll replace the old connections with a final one
                # If score < 100, we append
            else:
                base_content = content.strip()

            if score < 100:
                # Append current attempt
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                new_block = f"\n\n{marker}\n\n**[Thử nghiệm lúc {timestamp}] Score: {score}%**\n> {synthesis}\n\n*Gợi ý từ AI:* {feedback}\n"
                if marker in content:
                    # Keep old history if partial (as per user request "ghi nhận và kết nối")
                    updated_content = content.rstrip() + f"\n\n---\n**[Bổ sung {timestamp}] Score: {score}%**\n> {synthesis}\n\n*Cần bổ sung:* {', '.join(missing) if missing else feedback}"
                else:
                    updated_content = base_content + new_block
                
                # Update Frontmatter progress
                if "learning_progress:" in updated_content:
                    updated_content = re.sub(r'learning_progress:\s*\d+', f'learning_progress: {score}', updated_content)
                else:
                    updated_content = re.sub(r'---', f'---\nlearning_progress: {score}', updated_content, count=1)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                return True, f"Tiến độ: {score}%. {feedback}", ai_level, score, missing

            else:
                # FINAL PROMOTION (Score 100)
                # Clean up history, keep only final synthesis
                updated_content = base_content + f"\n\n{marker}\n\n**Cấp độ Master: {ai_level}**\n\n> {synthesis}\n\n*Lời phê cuối:* {feedback}"
                
                # Update Frontmatter for Promotion
                updated_content = re.sub(r'pillar:\s*Incubator', 'pillar: Knowledge', updated_content, flags=re.IGNORECASE)
                updated_content = re.sub(r'status:\s*"seed"', 'status: "evergreen"', updated_content)
                updated_content = re.sub(r'learning_progress:\s*\d+', '', updated_content) # Clear progress
                
                if "level:" in updated_content:
                    updated_content = re.sub(r'level:\s*\w+', f'level: {ai_level}', updated_content)
                else:
                    # Inject level if missing
                    updated_content = re.sub(r'---', f'---\nlevel: {ai_level}', updated_content, count=1)
                
                # Move to Knowledge
                filename = os.path.basename(file_path)
                new_path = os.path.join("wiki/01_knowledge", filename)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                os.rename(file_path, new_path)
                os.system("python3 brain_sync.py")
                
                return True, f"Tuyệt vời! Mastered. {feedback}", ai_level, 100, []

        except Exception as e:
            return False, str(e), "1_Biet", 0, []

def run_server():
    handler = BrainHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"🚀 Digital Brain Engine running at http://localhost:{PORT}")
        print(f"📱 Truy cập từ điện thoại: http://192.168.1.26:{PORT}/index.html")
        print("Waiting for actions...")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()

