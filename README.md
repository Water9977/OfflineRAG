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
streamlit   the web interface (coming in week 4)
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
│   │   └── engine.py       # the deterministic 5 step search pipeline
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
│   └── requirements.txt
│
└── docs/                   # weekly progress reports
    ├── week1_report.md
    ├── week2_report.md
    └── week3_report.md
```

---

## Progress week by week

### Week 1: foundation
Set up the local AI stack. Wrote `llm.py` to talk to LM Studio for both chat streaming and embeddings, and `vector_db.py`, a vector store under 80 lines that finds the closest code match using Cosine Similarity in pure NumPy. Confirmed both models run together on 8GB VRAM.

### Week 2: reading code
Built a small sample app with five files that behave like a real login system, so there was something genuine to test against. Then wrote `parser.py`, which uses Python's AST module to pull every function and class out of a file as a clean piece, along with its file name, line numbers, and docstring. It correctly extracted 15 pieces from the sample app.

### Week 3: the engine
Connected the three parts into one flow. `engine.py` indexes a codebase once, then answers questions through a fixed 5 step pipeline: embed the question, search the index, note imports, build the prompt, and stream the answer. The answer is told to use only the provided code and to cite exact file names and line numbers. Tested with "how are user passwords hashed?" and got a correct answer citing `auth.py` lines 6 to 11.

### Week 4: web dashboard (planned)
A Streamlit interface with a chat window and a visible step log under each answer, so anyone can see exactly which files the system read before responding.

### Week 5: benchmarks and final report (planned)
Measure speed and memory use, write the final NTCC report, and prepare the live offline demo.

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
```

---

## A note on how this was built

The code was written with the help of AI coding tools and reviewed line by line for understanding. The whole point of the project is to learn how a local RAG system works from the inside, so every file is kept small and readable on purpose, following clean code practices. Written explanations in the reports were passed through a humanizer pass to keep them plain and readable.

---

## License

MIT
