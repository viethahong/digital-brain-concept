import os
import re
import json

# Paths
WIKI_DIR = "/Users/viethahong/Documents/digital-brain/wiki"
STATS_JS = "/Users/viethahong/Documents/digital-brain/stats.js"

def get_frontmatter(content):
    match = re.search(r'^---\s+(.*?)\s+---', content, re.DOTALL | re.MULTILINE)
    if match:
        return match.group(1)
    return ""

def parse_val(fm, key):
    match = re.search(rf'{key}:\s*(.*)', fm)
    return match.group(1).strip().replace('"', '').replace("'", "") if match else None

def sync():
    stats = {
        "knowledge": {"1_Biet": 0, "2_Hieu": 0, "3_Hanh": 0, "4_Thong": 0, "5_Tue": 0, "files": []},
        "principles": {"1_Biet": 0, "2_Hieu": 0, "3_Hanh": 0, "4_Thong": 0, "5_Tue": 0, "files": []},
        "philosophies": {"1_Biet": 0, "2_Hieu": 0, "3_Hanh": 0, "4_Thong": 0, "5_Tue": 0, "files": []},
        "relationships": {"1_Biet": 0, "2_Quen": 0, "3_Than": 0, "4_Thuong": 0, "5_Yeu": 0, "files": []},
        "incubator": {"1_Biet": 0, "2_Hieu": 0, "3_Hanh": 0, "4_Thong": 0, "5_Tue": 0, "files": []},
        "total_files": 0,
        "last_sync": "",
        "graph": {"nodes": [], "links": []}
    }

    folders = {
        "01_knowledge": "knowledge",
        "02_principles": "principles",
        "03_philosophies": "philosophies",
        "04_relationships": "relationships",
        "05_incubator": "incubator"
    }

    title_to_id = {}

    # First pass: Collect all valid nodes
    for folder_name, stat_key in folders.items():
        folder_path = os.path.join(WIKI_DIR, folder_name)
        if not os.path.exists(folder_path):
            continue
            
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".md") and not file.startswith("template"):
                    stats["total_files"] += 1
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, os.path.dirname(WIKI_DIR))
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        fm = get_frontmatter(content)
                        level = parse_val(fm, "level")
                        title_fm = parse_val(fm, "title")
                        title = title_fm or file.replace(".md", "").replace("-", " ").title()
                        
                        if level and level in stats[stat_key]:
                            stats[stat_key][level] += 1
                        
                        stats[stat_key]["files"].append({
                            "title": title,
                            "path": rel_path,
                            "level": level
                        })

                        # Node for graph
                        node_id = title.lower().replace(" ", "-")
                        stats["graph"]["nodes"].append({
                            "id": node_id,
                            "title": title,
                            "group": stat_key,
                            "level": level,
                            "path": rel_path
                        })
                        title_to_id[title.lower()] = node_id
                        # Also map filename without ext as potential link target
                        title_to_id[file.replace(".md", "").lower()] = node_id

    # Second pass: Collect links
    for folder_name, stat_key in folders.items():
        folder_path = os.path.join(WIKI_DIR, folder_name)
        if not os.path.exists(folder_path):
            continue
            
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".md") and not file.startswith("template"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        fm = get_frontmatter(content)
                        title_fm = parse_val(fm, "title")
                        source_title = title_fm or file.replace(".md", "").replace("-", " ").title()
                        source_id = source_title.lower().replace(" ", "-")

                        # Find [[links]]
                        links = re.findall(r'\[\[(.*?)\]\]', content)
                        for link in links:
                            target = link.strip().lower()
                            if target in title_to_id:
                                stats["graph"]["links"].append({
                                    "source": source_id,
                                    "target": title_to_id[target]
                                })

    from datetime import datetime
    stats["last_sync"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Output to stats.js
    with open(STATS_JS, 'w', encoding='utf-8') as f:
        f.write(f"const BRAIN_STATS = {json.dumps(stats, indent=4)};")
    
    print(f"✅ Brain Synced! Total files: {stats['total_files']} | Nodes: {len(stats['graph']['nodes'])} | Links: {len(stats['graph']['links'])}")

if __name__ == "__main__":
    sync()
