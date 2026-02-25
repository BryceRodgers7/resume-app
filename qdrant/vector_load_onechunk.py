import os
import sys
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.models import PointStruct
from fastembed import TextEmbedding
import json

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = "knowledge_base"

# Specify the chunk ID to load — pass as CLI arg or hard-code as fallback
CHUNK_ID = sys.argv[1] if len(sys.argv) > 1 else "agent-sop-create-order"

# Load chunks from JSON
chunks_path = os.path.join(os.path.dirname(__file__), "chunks.json")
print(f"Loading chunks from: {chunks_path}")
with open(chunks_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    chunks = data["chunks"]

# Find the target chunk and its index (index is used as the stable Qdrant point ID)
chunk = None
chunk_index = None
for i, c in enumerate(chunks):
    if c["id"] == CHUNK_ID:
        chunk = c
        chunk_index = i
        break

if chunk is None:
    print(f"ERROR: No chunk found with id='{CHUNK_ID}'")
    sys.exit(1)

print(f"Found chunk at index {chunk_index}: '{chunk['title']}'")

# Connect and embed
print("Connecting to Qdrant...")
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

text = chunk["title"] + " " + chunk["content"]
vector = list(embedder.embed([text]))[0]
vector_list = [float(x) for x in vector]

# Build payload (rename 'id' -> 'chunk_id' to match convention in bulk loader)
payload = {**chunk}
payload["chunk_id"] = payload.pop("id")

# Check for an existing point and print its text before overwriting
existing = client.retrieve(collection_name=COLLECTION_NAME, ids=[chunk_index], with_payload=True)
if existing:
    old = existing[0].payload
    old_title = old.get("title", "(no title)")
    old_content = old.get("content", "(no content)")
    old_chunk_id = old.get("chunk_id", "(unknown)")
    print(f"\n--- Overwriting existing point (id={chunk_index}) ---")
    print(f"Chunk ID: {old_chunk_id}")
    print(f"Title:    {old_title}")
    print(f"Content:  {old_content}")
    print("---------------------------------------------------\n")
else:
    print(f"No existing point found at id={chunk_index} — inserting new.")

# Upsert — creates or overwrites the point at the stable index-based ID
print(f"Upserting chunk '{CHUNK_ID}' as point id={chunk_index}...")
client.upsert(
    collection_name=COLLECTION_NAME,
    points=[
        PointStruct(
            id=chunk_index,
            vector=vector_list,
            payload=payload,
        )
    ],
)

print(f"Done. Chunk '{CHUNK_ID}' upserted into collection '{COLLECTION_NAME}'.")
