import os
import re

WIKI_DIR = "wiki"

def purify_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove "## 🔗 Networking" section and everything after it
    content = re.sub(r'## 🔗 Networking.*$', '', content, flags=re.DOTALL)

    # 2. Find and remove blocks of consecutive links (more than 5 links in a tight block)
    # This pattern matches rows of [[Link]] that are close together
    link_block_pattern = r'(\[\[[^\]]+\]\][\s,]*){10,}'
    content = re.sub(link_block_pattern, '', content)

    # 3. Clean up multiple newlines at the end
    content = content.strip() + "\n"

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def run_purification():
    print("🧹 Starting Knowledge Purification...")
    count = 0
    for root, dirs, files in os.walk(WIKI_DIR):
        for file in files:
            if file.endswith(".md"):
                path = os.path.join(root, file)
                purify_file(path)
                count += 1
    print(f"✅ Purified {count} files.")

if __name__ == "__main__":
    run_purification()
