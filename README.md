<<<<<<< HEAD
# jvai_policy_chatbot
assignment
=======
# JVAI Policy Chatbot (Beginner-Friendly)

This project builds a simple **AI-powered** chatbot that can answer questions about a financial policy PDF using **vector search** + (optional) LLM. It is designed for beginners and follows the exact assignment steps.

> The included PDF is the policy document you sent. The assignment brief is also included for easy reference.

---

## 1) What you will build

- A script to **extract** text from the policy PDF and split it into chunks.
- A **vector database** (FAISS) built from those chunks using a local embedding model (`all-MiniLM-L6-v2`).
- A chatbot that:
  - finds the most relevant chunks for your question (**vector search**),
  - answers:
    - **Offline (no API key needed):** shows the most relevant excerpts and page numbers.
    - **Optional (if you have OPENAI_API_KEY):** asks a small LLM to write a concise answer grounded in those excerpts.
  - keeps **simple conversation memory** so follow-ups like “What about debt?” make sense.

---

## 2) Quick start (5 steps)

> Works on Windows/Mac/Linux. Requires Python 3.10+

1. **Open a terminal** in this folder: `/mnt/data/jvai_policy_chatbot`  
2. **Create a virtual environment** and activate it
   - Windows (PowerShell):
     ```pwsh
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - macOS/Linux (bash/zsh):
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Build the vector index**
   ```bash
   python ingest.py
   ```
   This reads `data/policy.pdf`, splits into chunks with page numbers, embeds them, and saves an index in `index/`.
5. **Run the chatbot**
   - **CLI (terminal):**
     ```bash
     python chat.py
     ```
   - **Gradio UI (nice web app):**
     ```bash
     python chat.py --ui
     ```
     Open http://127.0.0.1:7860 in your browser.

> Optional LLM answers: set your key before running (totally optional)
>
> **Windows (PowerShell)**:
> ```pwsh
> $env:OPENAI_API_KEY="sk-..."
> ```
> **macOS/Linux**:
> ```bash
> export OPENAI_API_KEY="sk-..."
> ```

---

## 3) How it works (step-by-step, in plain English)

### A. Extract Data (from the PDF)
- File: `ingest.py`
- Library: **PyMuPDF** reads the PDF **page by page**. Each page’s text is cleaned and split into overlapping **chunks** (700 chars with 120 overlap).
- We **remember the page number** with each chunk. This lets the bot tell you **which page** it used.
- We turn each chunk into a vector using the small, free **`all-MiniLM-L6-v2`** embedding model.

### B. Set up the Database for Search
- Library: **FAISS** (fast vector search).
- We store all chunk embeddings into a FAISS index and save it under `index/index.faiss`. The chunk metadata (text + page) goes into `index/meta.json`.
- When you ask a question, we embed your question, then **search** the index for the **closest** chunks.

### C. Build the Chatbot
- File: `chat.py`
- We:
  - Load the index + metadata.
  - Retrieve top-k chunks (with **page numbers**).
  - **Conversation memory**: if your new question is very short (like “what about debt?”), we **prepend your previous question** to give more context for retrieval.
  - **Answering**:
    - **Offline (default):** show the most relevant excerpts and the pages.
    - **Optional LLM:** If `OPENAI_API_KEY` is set, we ask the LLM to write a concise answer, but **only using the retrieved chunks**. It prints sources as “page X, page Y”.

---

## 4) Testing ideas (example questions)

Try these after you run the chatbot:

- “What are the strategic priorities in this budget?”  
- “Do they aim to keep a balanced budget?”  
- “What about debt levels?” (short follow-up to test memory)  
- “How are net assets expected to change?”  
- “What is the target for superannuation liabilities funding?”

> The policy talks about a balanced budget over the economic cycle, low debt, maintaining AAA rating, and a 90% funding target for superannuation liabilities by 2039–40 (see pages in the sources the bot returns).

---

## 5) Project structure

```
jvai_policy_chatbot/
├─ data/
│  └─ policy.pdf                 # your policy PDF (already provided)
├─ index/
│  ├─ index.faiss                # created by ingest.py
│  └─ meta.json                  # created by ingest.py (stores chunks + pages)
├─ chat.py                       # chatbot (CLI + Gradio UI)
├─ ingest.py                     # builds the vector index
├─ utils.py                      # small helpers (chunking, memory, etc.)
├─ requirements.txt
└─ Assignment Task.pdf           # your assignment brief (for your reference)
```

---

## 6) How to submit (GitHub + email)

1. Create a new GitHub repo (public).
2. In this folder, run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: JVAI policy chatbot"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```
3. Email your repo link to the address mentioned in the assignment brief.

---

## 7) Troubleshooting

- **`ModuleNotFoundError`**: run `pip install -r requirements.txt` inside your **activated** virtual environment.
- **FAISS wheel issues (very old CPUs/OS)**: try `pip install faiss-cpu==1.7.4` explicitly.
- **Slow first run**: the embedding model downloads once; afterwards it’s cached.
- **No LLM**: totally fine—offline mode still passes the assignment because answers cite exact page numbers.

---

## 8) Why this meets the assignment

- **Extract Data**: we parse the PDF and keep **page numbers** for every chunk.
- **Database for Search**: we use **FAISS** with a solid local embedding model.
- **Chatbot**: answers questions, includes simple **conversation memory**, and grounds answers in retrieved text. Clear and helpful.

Good luck—you’ve got this 🚀
>>>>>>> fee19ab (Initial Commit: JVAI policy chatbot)
