\
"""
Build a searchable vector index from data/policy.pdf
Usage:
  python ingest.py
This will create files under index/
"""
import json
from pathlib import Path
import fitz  # PyMuPDF
import numpy as np
import faiss
from tqdm import tqdm
from sentence_transformers import SentenceTransformer

from utils import chunk_text, clean_text

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "policy.pdf"
INDEX_DIR = ROOT / "index"
INDEX_DIR.mkdir(exist_ok=True, parents=True)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def read_pdf_pages(pdf_path: Path):
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        yield page_num + 1, clean_text(text)  # 1-based page numbering
    doc.close()

def main():
    if not DATA.exists():
        raise FileNotFoundError(f"Could not find {DATA}. Put the policy PDF in data/policy.pdf")

    print(f"Loading embedding model: {MODEL_NAME}")
    embedder = SentenceTransformer(MODEL_NAME)

    all_chunks = []
    for page, text in read_pdf_pages(DATA):
        if not text:
            continue
        for ch in chunk_text(text, page=page, chunk_size=700, chunk_overlap=120):
            all_chunks.append(ch)

    texts = [c["text"] for c in all_chunks]
    print(f"Total chunks: {len(texts)}")

    # Compute embeddings (normalize for cosine similarity with inner product index)
    embeddings = embedder.encode(texts, convert_to_numpy=True, show_progress_bar=True, normalize_embeddings=True)

    d = embeddings.shape[1]
    index = faiss.IndexFlatIP(d)  # cosine via dot product of normalized vectors
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_DIR / "index.faiss"))
    # Save metadata and model name
    meta = {
        "model_name": MODEL_NAME,
        "chunks": all_chunks,  # list of dicts with page + text
    }
    with open(INDEX_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print("Index built successfully.")
    print("Files created:")
    print(f"- {INDEX_DIR / 'index.faiss'}")
    print(f"- {INDEX_DIR / 'meta.json'}")

if __name__ == "__main__":
    main()
