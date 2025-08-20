\
"""
Chatbot that answers questions about data/policy.pdf using vector search.
Two modes:
  1) CLI: python chat.py
  2) Gradio UI: python chat.py --ui
Optional: set OPENAI_API_KEY to enable LLM-generated answers; otherwise it replies extractively.
"""
import os
import argparse
import json
from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from utils import extract_keywords, format_sources

ROOT = Path(__file__).resolve().parent
INDEX_DIR = ROOT / "index"
META_FILE = INDEX_DIR / "meta.json"
INDEX_FILE = INDEX_DIR / "index.faiss"

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def load_index():
    if not (INDEX_FILE.exists() and META_FILE.exists()):
        raise FileNotFoundError("Vector index not found. Run: python ingest.py")

    index = faiss.read_index(str(INDEX_FILE))
    with open(META_FILE, "r", encoding="utf-8") as f:
        meta = json.load(f)
    model_name = meta.get("model_name", DEFAULT_MODEL)
    chunks = meta["chunks"]
    embedder = SentenceTransformer(model_name)
    return index, embedder, chunks

def retrieve(index, embedder, chunks: List[Dict], query: str, top_k: int = 5) -> List[Tuple[int, float, Dict]]:
    q_emb = embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    scores, idxs = index.search(q_emb, top_k)
    hits = []
    for i, score in zip(idxs[0], scores[0]):
        if int(i) >= 0:
            hits.append((int(i), float(score), chunks[int(i)]))
    return hits

def make_answer_offline(hits: List[Tuple[int, float, Dict]], question: str) -> str:
    """
    Simple extractive answer: stitch top chunks together.
    """
    context_parts = [h[2]["text"] for h in hits]
    context = "\n\n".join(context_parts)
    # Heuristic: return a concise answer using the most relevant lines (first ~600 chars)
    snippet = (context[:600] + "...") if len(context) > 600 else context
    answer = (
        "Here's what the policy says (most relevant excerpts):\n\n"
        f"{snippet}\n\n"
        "Sources (page numbers):\n" + format_sources(hits)
    )
    return answer

def make_answer_openai(hits: List[Tuple[int, float, Dict]], question: str) -> str:
    """
    If OPENAI_API_KEY is set, we can ask an LLM to write a concise answer grounded on the retrieved chunks.
    """
    try:
        from openai import OpenAI
    except Exception:
        return make_answer_offline(hits, question)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return make_answer_offline(hits, question)

    # Build context with page numbers for transparency
    context = "\n\n".join([f"(page {h[2]['page']}) {h[2]['text']}" for h in hits])

    client = OpenAI(api_key=api_key)
    prompt = f"""You are a helpful assistant. Answer the user's question ONLY using the context below.
If the answer is not contained in the context, say you couldn't find it in the document.
Show the pages you used at the end as: Sources: page X, page Y
Question: {question}
Context:
{context}
Answer:
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        text = resp.choices[0].message.content.strip()
        return text
    except Exception:
        return make_answer_offline(hits, question)

def chat_cli():
    index, embedder, chunks = load_index()
    print("Loaded index. Ask questions about the policy. Type 'exit' to quit.")
    prev_q = None
    while True:
        q = input("\nYou: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        q2 = extract_keywords(q, prev_q)
        hits = retrieve(index, embedder, chunks, q2, top_k=5)
        if not hits:
            print("Bot: Sorry, I couldn't find anything relevant in the document.")
            prev_q = q
            continue

        # Try OpenAI if available; fall back to offline extractive answer.
        answer = make_answer_openai(hits, q2)
        print(f"\nBot: {answer}")
        prev_q = q

def chat_ui():
    import gradio as gr
    index, embedder, chunks = load_index()

    state_prev_q = gr.State("")

    def respond(message, history, prev_q):
        q2 = extract_keywords(message, prev_q if prev_q else None)
        hits = retrieve(index, embedder, chunks, q2, top_k=5)
        if not hits:
            reply = "Sorry, I couldn't find anything relevant in the document."
        else:
            reply = make_answer_openai(hits, q2)

        history = history + [(message, reply)]
        return history, message  # store current message as prev_q

    with gr.Blocks(title="Policy Chatbot") as demo:
        gr.Markdown("# Policy Chatbot\nAsk questions about the financial policy document.")
        chatbot = gr.Chatbot(height=500)
        msg = gr.Textbox(label="Your question")
        clear = gr.Button("Clear")
        msg.submit(respond, [msg, chatbot, state_prev_q], [chatbot, state_prev_q])
        clear.click(lambda: ([], ""), None, [chatbot, state_prev_q])

    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ui", action="store_true", help="Launch Gradio UI")
    args = parser.parse_args()
    if args.ui:
        chat_ui()
    else:
        chat_cli()
