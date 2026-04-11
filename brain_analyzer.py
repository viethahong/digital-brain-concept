import os
import json
import random

# Paths (Use relative paths)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATS_JS = os.path.join(BASE_DIR, "stats.js")
INQUIRY_JS = os.path.join(BASE_DIR, "inquiry.js")

def analyze():
    try:
        if not os.path.exists(STATS_JS):
            print("Stats file not found. Run brain_sync.py first.")
            return

        with open(STATS_JS, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract JSON from "const BRAIN_STATS = {...};"
            json_str = content.replace("const BRAIN_STATS = ", "").rstrip(";")
            stats = json.loads(json_str)
    except Exception as e:
        print(f"Error reading stats: {e}")
        return

    nodes = stats.get("graph", {}).get("nodes", [])
    links = stats.get("graph", {}).get("links", [])
    
    inquiries = []

    # 1. Tìm các nút "Cô đơn" (không có liên kết nào)
    node_ids_with_links = set([l["source"] for l in links] + [l["target"] for l in links])
    isolated_nodes = [n for n in nodes if n["id"] not in node_ids_with_links]
    
    for node in isolated_nodes[:3]:
        inquiries.append({
            "type": "isolated",
            "title": node["title"],
            "path": node["path"],
            "question": f"Trang '{node['title']}' hiện đang bị cô lập. Bạn có thể kết nối nó với Nguyên tắc hay Tri thức nào khác không?"
        })

    # 2. Tìm các nút "Sơ khai" (Level 1 hoặc 2)
    basic_nodes = [n for n in nodes if n.get("level") in ["1_Biet", "2_Hieu"]]
    random.shuffle(basic_nodes)
    
    for node in basic_nodes[:3]:
        inquiries.append({
            "type": "low_level",
            "title": node["title"],
            "path": node["path"],
            "question": f"Tri thức về '{node['title']}' mới dừng lại ở mức '{node['level']}'. Bạn đã có trải nghiệm thực tế nào để nâng cấp nó lên mức 'Hành' chưa?"
        })

    # Output to inquiry.js
    with open(INQUIRY_JS, 'w', encoding='utf-8') as f:
        f.write(f"const BRAIN_INQUIRIES = {json.dumps(inquiries, indent=4)};")
    
    print(f"✅ Analysis complete! Found {len(inquiries)} curiosities.")

if __name__ == "__main__":
    analyze()
