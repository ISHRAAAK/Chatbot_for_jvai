\
from __future__ import annotations
import re
from typing import List, Dict, Tuple

def clean_text(text: str) -> str:
    # Normalize whitespace
    return re.sub(r"\s+", " ", text).strip()

def chunk_text(text: str, page: int, chunk_size: int = 700, chunk_overlap: int = 120) -> List[Dict]:
    """
    Split text into overlapping chunks while keeping track of the source page.
    """
    tokens = list(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk = "".join(tokens[start:end])
        chunk = clean_text(chunk)
        if chunk:
            chunks.append({"page": page, "text": chunk})
        start += (chunk_size - chunk_overlap)
    return chunks

def extract_keywords(question: str, prev_q: str | None = None) -> str:
    """
    Simple heuristic to help with short follow-ups like 'what about debt?'
    We just prepend the previous question to give the retriever more context.
    """
    if prev_q and len(question.split()) < 6:
        return prev_q + " " + question
    return question

def format_sources(hits: List[Tuple[int, float, Dict]]) -> str:
    """
    Format the top-k sources with page numbers and similarity scores.
    """
    lines = []
    for rank, (idx, score, meta) in enumerate(hits, start=1):
        lines.append(f"{rank}. page {meta['page']} (score {score:.3f})")
    return "\n".join(lines)
