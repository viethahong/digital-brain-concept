import os
import sys
import re

def promote_seed(file_path, synthesis):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Frontmatter
    # Change pillar: Incubator to pillar: Knowledge
    content = re.sub(r'pillar:\s*Incubator', 'pillar: Knowledge', content, flags=re.IGNORECASE)
    # Change status: seed to status: evergreen (or similar)
    content = re.sub(r'status:\s*"seed"', 'status: "evergreen"', content)
    
    # 2. Append Synthesis
    connection_block = f"\n\n## 🧠 Chiêm nghiệm & Kết nối (Inside Connect)\n\n> {synthesis}\n"
    content += connection_block

    # 3. Determine new path
    filename = os.path.basename(file_path)
    new_path = os.path.join("wiki/01_knowledge", filename)

    # 4. Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # 5. Move file
    try:
        os.rename(file_path, new_path)
        print(f"✅ Promoted: {filename} moved to pillars/knowledge")
        
        # 6. Run sync
        os.system("python3 brain_sync.py")
    except Exception as e:
        print(f"❌ Error moving file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 promote_seed.py <file_path> <synthesis>")
    else:
        promote_seed(sys.argv[1], sys.argv[2])
