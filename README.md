# OfflineRAG

### A Local LLM Agent for Intelligent Codebase Comprehension

OfflineRAG is a developer tool that lets you ask plain English questions about a Python codebase and get answers that quote the real code. Everything runs on your own machine. No cloud service, no API key, no uploading source files to a third party server.

This is a B.Tech CSE NTCC project built at Amity University Noida.

---

## Why this exists

Tools like GitHub Copilot and ChatGPT are useful for understanding code, but they need you to send your code to an external server. For anyone working on something private or sensitive, that is not acceptable. OfflineRAG is an attempt to build something with similar usefulness without that tradeoff. The model runs locally, the search runs locally, and nothing about your code ever leaves the laptop.

---

## How it works

The system has four small parts that connect in a straight line:

```
Your question
     |
     v
[1] Question turned into numbers          (embedding model)
     |
     v
[2] Closest code pieces found             (NumPy vector search)
     |
     v
[3] Code pieces packed into a prompt      (engine)
     |
     v
[4] Local AI reads code and answers       (chat model)
     |
     v
Streamed answer with file and line citations
```

The important idea is that the code is not chopped up randomly. It is read with Python's own Abstract Syntax Tree module, so every function and every class comes out as a whole, complete piece with its file name and line numbers attached. That is what lets the answers cite exact locations instead of guessing.

---

## Models used

Everything is served locally through [LM Studio](https://lmstudio.ai), which exposes an OpenAI compatible API at `http://localhost:1234/v1`.

| Job | Model | Quant | Why |
|-----|-------|-------|-----|
| Answering questions | Qwen3.5 9B | Q4_K_M | Fits fully inside 8GB VRAM, strong at code reasoning, 262K context window. Released March 2026. |
| Turning text into vectors | nomic-embed-text v1.5 | Q4_K_M | Tiny footprint, runs beside the chat model without fighting for memory. Produces 768 number vectors. |

Both models run at the same time on an 8GB GPU with no memory overflow. Picking models that fit entirely in VRAM was a deliberate choice: a bigger model that spills into system RAM crawls, because system memory is far slower than GPU memory.

---

## Tech stack

Three packages only. PyTorch and the heavy machine learning libraries were deliberately left out, since LM Studio handles all the model serving.

```
openai      talks to LM Studio
numpy       vector math for search
streamlit   the web interface
```

---

## Project structure

```
OfflineRAG/
|
├── offlinerag/
│   ├── backend/
│   │   ├── llm.py          # connects to LM Studio for chat and embeddings
│   │   ├── parser.py       # reads Python files using the AST module
│   │   ├── vector_db.py    # NumPy vector store with Cosine Similarity search
│   │   └── engine.py       # the deterministic 5 step search and import walk pipeline
│   │
│   ├── frontend/
│   │   └── app.py          # Streamlit chat dashboard
│   │
│   ├── test_codebase/      # a small sample Flask style app to test against
│   │   ├── app.py
│   │   ├── auth.py
│   │   ├── models.py
│   │   ├── database.py
│   │   └── config.py
│   │
│   ├── test_week1.py       # checks LM Studio connection and vector search
│   ├── test_week2.py       # checks the AST parser
│   ├── test_week3.py       # checks the full question answering pipeline
│   ├── test_week5.py       # performance benchmarks
│   └── requirements.txt
│
└── docs/                   # weekly progress reports
    ├── week1_report.md
    ├── week2_report.md
    ├── week3_report.md
    ├── week4_report.md
    └── week5_report.md
```

---

## Progress week by week

### Week 1: foundation
Set up the local AI stack. Wrote `llm.py` to talk to LM Studio for both chat streaming and embeddings, and `vector_db.py`, a vector store under 80 lines that finds the closest code match using Cosine Similarity in pure NumPy. Confirmed both models run together on 8GB VRAM.

### Week 2: reading code
Built a small sample app with five files that behave like a real login system, so there was something genuine to test against. Then wrote `parser.py`, which uses Python's AST module to pull every function and class out of a file as a clean piece, along with its file name, line numbers, and docstring. It correctly extracted 15 pieces from the sample app.

### Week 3: the engine
Connected the three parts into one flow. `engine.py` indexes a codebase once, then answers questions through a fixed 5 step pipeline: embed the question, search the index, note imports, build the prompt, and stream the answer. The answer is told to use only the provided code and to cite exact file names and line numbers. Tested with "how are user passwords hashed?" and got a correct answer citing `auth.py` lines 6 to 11.

### Week 4: web dashboard
Built a Streamlit interface with a chat window and a visible step log under each answer, so anyone can see exactly which files the system read before responding. Also fixed a bug where the vector database folder path depended on which directory the app was launched from.

### Week 5: import walk, benchmarks, and cleanup
Added a real import walk to the engine, so a question about one file also pulls in code from files it imports, instead of relying on keyword matching alone. Built a benchmarking script that measured indexing speed, embedding speed, and search speed, all of which are fast. The one slow part is answer generation itself, which takes 20 to 30 seconds because Qwen3.5 9B reasons internally before every answer regardless of instructions telling it not to. This was confirmed by testing a plain five word question with no code context at all, which took the same amount of time. It is a genuine speed versus depth tradeoff rather than a bug. Also caught and fixed a leftover model name from week 1 that never got updated after switching models.

---

## Running it yourself

You need [LM Studio](https://lmstudio.ai) installed with both models loaded and the local server started on port 1234.

```bash
# install the three packages
pip install -r offlinerag/requirements.txt

# from inside the offlinerag folder, run any week's test
cd offlinerag
python test_week1.py   # connection and search
python test_week2.py   # parser
python test_week3.py   # full pipeline
python test_week5.py   # performance benchmarks

# or launch the web dashboard
streamlit run frontend/app.py
```

Open the sidebar, paste the path to any Python folder on your machine, click Index Codebase, and start asking questions in the chat box.

---

## A note on how this was built

The code was written with the help of AI coding tools and reviewed line by line for understanding. The whole point of the project is to learn how a local RAG system works from the inside, so every file is kept small and readable on purpose, following clean code practices. Written explanations in the reports were passed through a humanizer pass to keep them plain and readable.

---

## License

MIT
