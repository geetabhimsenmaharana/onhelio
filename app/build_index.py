"""Step 6: load the extracted PDF text into ChromaDB so it can be searched.

Input:  data/processed/<manufacturer>/*.json   (from extract_text.py)
Output: db/chroma/                              (the searchable database)

Run again any time you add or change PDFs; existing entries are updated, not duplicated.
"""
import json
from pathlib import Path

import chromadb

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
DB_PATH = ROOT / "db" / "chroma"
COLLECTION = "onhelio_docs"

CHUNK_SIZE = 1000   # characters per chunk
OVERLAP = 150       # characters shared between neighbouring chunks


def split_text(text):
    """Split a page into overlapping chunks so long pages stay searchable."""
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - OVERLAP
    return chunks


def main():
    client = chromadb.PersistentClient(path=str(DB_PATH))
    collection = client.get_or_create_collection(COLLECTION)

    ids, docs, metas = [], [], []
    for json_file in sorted(PROCESSED.glob("*/*.json")):
        record = json.loads(json_file.read_text())
        for page in record["pages"]:
            for i, chunk in enumerate(split_text(page["text"])):
                ids.append(f"{record['manufacturer']}|{record['source_file']}|p{page['page']}|c{i}")
                docs.append(chunk)
                metas.append({
                    "manufacturer": record["manufacturer"],
                    "source_file": record["source_file"],
                    "page": page["page"],
                })

    if not docs:
        print("No text found. Run extract_text.py first.")
        return

    collection.upsert(ids=ids, documents=docs, metadatas=metas)
    print(f"Stored {len(docs)} chunks in ChromaDB ({DB_PATH})")

    # Quick test search
    question = "How many years is the power optimizer warranty?"
    result = collection.query(query_texts=[question], n_results=3)
    print(f"\nTest question: {question}")
    for doc, meta in zip(result["documents"][0], result["metadatas"][0]):
        preview = " ".join(doc.split())[:200]
        print(f"\n- {meta['source_file']} (page {meta['page']})\n  {preview}...")


if __name__ == "__main__":
    main()
