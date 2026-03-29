import requests

API_KEY = "gb_api_SASmcjPqTIPlVqAO5AJRisoQfnmnSB7MNSFxzPoO"
SPACE_ID = "uC7n6pIvGxsVIjPjTZYb"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
BASE_URL = f"https://api.gitbook.com/v1/spaces/{SPACE_ID}"

def create_markdown_to_gitbook_ast(filepath):
    nodes = []
    with open(filepath, 'r') as f:
        content = f.read()
    blocks = content.split("\n\n")
    in_code_block = False
    code_content = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        if block.startswith("```"):
            if "```" in block[3:]:
                 # inline or single block
                 code_text = block.replace("```python", "").replace("```json", "").replace("```", "").strip()
                 nodes.append({"object": "block", "type": "code", "nodes": [{"object": "text", "text": code_text}]})
            else:
                 in_code_block = True
                 code_content.append(block)
            continue
            
        if in_code_block:
            code_content.append(block)
            if "```" in block:
                in_code_block = False
                code_text = "\n\n".join(code_content).replace("```python", "").replace("```json", "").replace("```", "").strip()
                nodes.append({"object": "block", "type": "code", "nodes": [{"object": "text", "text": code_text}]})
                code_content = []
            continue

        if block.startswith("# "):
            nodes.append({"object": "block", "type": "heading-1", "nodes": [{"object": "text", "text": block[2:]}]})
        elif block.startswith("## "):
            nodes.append({"object": "block", "type": "heading-2", "nodes": [{"object": "text", "text": block[3:]}]})
        elif block.startswith("### "):
            nodes.append({"object": "block", "type": "heading-3", "nodes": [{"object": "text", "text": block[4:]}]})
        else:
            nodes.append({"object": "block", "type": "paragraph", "nodes": [{"object": "text", "text": block}]})

    # Let's encapsulate as a single page or just paragraphs. Wait! GitBook API specifies the document structure carefully.
    return {"document": {"object": "document", "nodes": nodes}}

def upload_to_gitbook():
    create_markdown_to_gitbook_ast("PIXELENGINE_MANUAL.md")
    
    # 1. Create a change request
    print("Creating Change Request...")
    cr_res = requests.post(f"{BASE_URL}/change-requests", headers=HEADERS, json={"subject": "Import PixelEngine Manual"})
    if cr_res.status_code >= 400:
         print("Failed CR:", cr_res.text)
         return
    
    cr_id = cr_res.json()["id"]
    revision_id = cr_res.json()["revision"] if "revision" in cr_res.json() else None
    print(f"CR Created: {cr_id}, Revision: {revision_id}")
    
    # Gitbook v1 API uses the change request ID in the URL structure for mutations? No, it uses the revision tree.
    # Wait, usually a space has a root page. Let's see if there is one.
    rev_url = f"{BASE_URL}/revisions/{cr_id}" if not revision_id else f"{BASE_URL}/revisions/{revision_id}"
    
    print("Trying to update content...")
    # Actually, the GitBook API uses `PATCH /v1/spaces/{spaceId}/revisions/{changeRequestId}/page/{pageId}` or similar.
    # If there are no pages, you create one via POST /v1/spaces/{spaceId}/revisions/{changeRequestId}/pages
    res = requests.post(f"{rev_url}/pages", headers=HEADERS, json={"title": "PixelEngine Manual"})
    
    if res.status_code >= 400:
         print("Failed to create page. Let's try to fetch existing pages instead...", res.text)
         # Maybe the space inherently has a root page?
         # ...
    else:
         page_id = res.json()["id"]
         print(f"Created page: {page_id}")
         
print("Script parsed successfully.")
upload_to_gitbook()
