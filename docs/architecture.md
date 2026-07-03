# OfflineRAG: Architecture and Project History

This document explains what OfflineRAG is, how it works end to end, what was built each week, and what the project has actually achieved. It is meant to be read on its own, without needing the weekly reports, though those go into more detail on any single week.

---

## 1. What this project is

OfflineRAG is a tool that lets a developer ask plain English questions about a Python codebase and get answers that quote the real code, with file names and line numbers attached. The entire thing runs on one laptop. There is no cloud API call, no uploading of source code anywhere, and no internet connection needed once the models are downloaded.

The motivation is simple. Tools like Copilot or ChatGPT are useful, but they require sending your code to someone else's server. For anyone working on private, sensitive, or simply personal code, that is not always acceptable. OfflineRAG proves that a useful version of the same idea, question answering grounded in real code, can run entirely on consumer hardware with 8GB of GPU memory.

This is a five week B.Tech CSE NTCC project built at Amity University Noida.

---

## 2. The end to end flow

A single question passes through five fixed steps, always in the same order. Nothing in this pipeline is left for the AI to decide on its own. The order is deterministic, which makes it predictable and easy to explain and debug.

```
Your question
     |
     v
[1] SEARCH     Turn the question into a 768 number vector using nomic-embed-text
     |
     v
[2] RETRIEVE   Compare that vector against every indexed code chunk using
               Cosine Similarity, in pure NumPy, and take the top 5 matches
     |
     v
[3] IMPORTS    Read the files those top 5 chunks came from, find their
               import statements, and pull in one relevant chunk from
               each imported local file
     |
     v
[4] CONTEXT    Pack all retrieved chunks (direct matches and import matches)
               into a single prompt, each one labeled with its file name,
               line numbers, and whether it was a direct match or pulled
               in through an import
     |
     v
[5] ANSWER     Send the prompt to Qwen3.5 9B running in LM Studio, and
               stream the answer back token by token, with a rule that
               the model must only use the provided code and must cite
               file names and line numbers
```

Why this design instead of a more common "agent" approach where the AI decides what to search for and when to stop: agent loops that let a small local model decide its own next action are unreliable in practice, especially on consumer hardware. A fixed, deterministic pipeline is not only easier to reason about, it is also easier to demonstrate and defend in a viva, because every step happens the same way every time.

---

## 3. Models used and why

Everything is served locally through [LM Studio](https://lmstudio.ai), which exposes an OpenAI compatible API at `http://127.0.0.1:1234/v1`. Two models are loaded into LM Studio at the same time.

| Job | Model | Quantization | Size | Why this one |
|---|---|---|---|---|
| Answering questions | Qwen3.5 9B | Q4_K_M | about 5.7 GB | Fits entirely inside 8GB of GPU memory, strong at reasoning about code, 262K token context window, released March 2026 |
| Turning text into vectors | nomic-embed-text v1.5 | Q4_K_M | about 274 MB | Tiny, runs alongside the chat model without competing for GPU memory, produces 768 number vectors |

Both models sit in VRAM together with no overflow into system RAM. This was a deliberate choice made early in the project. A larger model that does not fully fit in GPU memory spills into system RAM, and system RAM is far slower than GPU memory, which makes generation crawl. Staying under the 8GB VRAM limit was the single biggest constraint that shaped every model decision.

**Known tradeoff:** Qwen3.5 9B is a reasoning model. It internally deliberates before producing an answer, and this cannot be turned off with a simple instruction in the prompt. This was confirmed directly during Week 5 testing: even a plain five word question with no codebase context attached still took close to 20 seconds before the first token appeared. Search and retrieval, by contrast, are close to instant. So the honest performance story is: finding the right code is fast, but getting the AI to phrase the answer takes 20 to 30 seconds. A smaller non reasoning model could be swapped in for faster but shallower answers.

---

## 4. Tech stack

Only three external Python packages are used in the entire project.

```
openai      talks to LM Studio's OpenAI compatible local server
numpy       vector math for the custom search index
streamlit   the web dashboard
```

PyTorch and the usual machine learning libraries were deliberately left out. LM Studio already handles loading and running the models, so there was no need to duplicate that inside the Python code. Keeping the dependency list this short also makes the whole project easier to install, explain, and grade.

---

## 5. Project structure

```
OfflineRAG/
|
├── offlinerag/
│   ├── backend/
│   │   ├── llm.py          connects to LM Studio for chat streaming and embeddings
│   │   ├── parser.py       reads Python files using the AST module
│   │   ├── vector_db.py    NumPy vector store with Cosine Similarity search
│   │   └── engine.py       the 5 step search, import walk, and answer pipeline
│   │
│   ├── frontend/
│   │   └── app.py          Streamlit chat dashboard
│   │
│   ├── test_codebase/      a small sample Flask style app used to test the system
│   │   ├── app.py
│   │   ├── auth.py
│   │   ├── models.py
│   │   ├── database.py
│   │   └── config.py
│   │
│   ├── test_week1.py       checks LM Studio connection, embeddings, and vector search
│   ├── test_week2.py       checks the AST parser
│   ├── test_week3.py       checks the full question answering pipeline
│   ├── test_week5.py       measures indexing, embedding, search, and answer speed
│   └── requirements.txt
│
└── docs/
    ├── architecture.md     this file
    ├── week1_report.md
    ├── week2_report.md
    ├── week3_report.md
    ├── week4_report.md
    └── week5_report.md
```

---

## 6. What each file actually does

**`llm.py`**
A small client class that talks to LM Studio. It has two jobs: turn text into a 768 number vector (`get_embedding`), and stream a chat answer token by token (`stream_chat`). Both use the standard `openai` Python package pointed at a local address instead of the real OpenAI service, since LM Studio speaks the same API language.

**`parser.py`**
Reads a folder of Python files using Python's own Abstract Syntax Tree (AST) module, the same tool Python uses internally to understand its own code. Instead of chopping files into arbitrary blocks of text, which can cut a function in half, it walks the real structure of the code and pulls out every function, class, and method as one complete, correctly bounded piece. Each piece comes with its file name, absolute file path, exact line numbers, and docstring attached.

**`vector_db.py`**
A vector database written from scratch in under 80 lines of NumPy. It stores every code piece as a list of numbers (its embedding) alongside its original text and metadata, saved to a plain JSON file on disk. Searching means comparing a question's vector against every stored vector using Cosine Similarity, a standard formula that measures how closely two vectors point in the same direction, and returning the closest matches. On this project's scale, a few thousand chunks at most, this search takes under a millisecond.

**`engine.py`**
The coordinator that ties everything together. It has two main jobs: index a codebase once (parse it, embed every chunk, store it), and answer a question through the fixed 5 step pipeline described in section 2. This is also where the import walk lives, the logic that looks at what files the top matches import and pulls in relevant code from those files too, so multi file questions like "how does the database get set up" can be answered properly instead of only matching on the literal word "database".

**`frontend/app.py`**
A Streamlit page. The sidebar lets you point the tool at any folder and index it. The main area is a chat box. Every answer streams in live, and underneath each answer is a collapsible drawer showing the exact retrieval steps that were taken to produce it, including which files were direct matches and which were pulled in through the import walk.

---

## 7. Week by week history

### Week 1: foundation
Set up the local AI stack from nothing. Configured LM Studio to run Qwen3.5 9B and nomic-embed-text at the same time on 8GB of VRAM with no memory overflow. Wrote `llm.py` to handle both chat streaming and embeddings, and `vector_db.py`, a from scratch vector store using Cosine Similarity in pure NumPy. Verified the whole chain worked with an integration test.

### Week 2: reading code properly
Built a small five file sample app that behaves like a real login system, purely to have something genuine to test against. Wrote `parser.py`, which uses Python's AST module to correctly extract every function and class in a file as a whole piece, with accurate file names, line numbers, and docstrings. It correctly pulled 15 pieces out of the sample app on the first real run.

### Week 3: connecting the pieces
Built `engine.py`, which links the parser, the vector database, and the language model into one working pipeline. Indexing a folder became a single function call. Asking a question became a fixed 5 step process ending in a streamed, cited answer. Tested with "how are user passwords hashed" and got a correct answer that cited the exact file and line numbers where the hashing function lives.

### Week 4: a real interface
Built a Streamlit web dashboard so the tool no longer needed to be run from the terminal. Added a sidebar for picking and indexing a folder, a chat interface for asking questions, and a retrieval steps drawer under every answer so the process stays transparent. Also fixed a bug where the vector database's save location depended on which folder the app was launched from, which could quietly create duplicate, disconnected databases.

### Week 5: making it smarter, and being honest about speed
Added the import walk, so the tool can now follow real code relationships between files instead of relying on keyword overlap alone. Built a benchmarking script and measured every stage of the pipeline. Indexing, embedding, and searching all turned out to be extremely fast. The one slow part is generating the final answer, which takes 20 to 30 seconds, and this was traced directly to Qwen3.5 9B's own internal reasoning behavior rather than any flaw in the pipeline, confirmed by testing a trivial question with zero code context and getting the same delay. Also found and corrected a leftover model name bug from Week 1 that had gone unnoticed because LM Studio was silently working around it, and cleaned up a stray duplicate folder left over from an earlier bug.

---

## 8. What has been achieved, honestly

- A fully offline, working RAG pipeline that indexes real Python code and answers questions about it, verified against a sample codebase with correct, cited answers
- A search and retrieval layer that is fast enough to feel instant, well under a second combined
- A code aware chunking system that respects real function and class boundaries instead of naive text splitting
- A multi file reasoning capability through the import walk, so answers are not limited to a single matched file
- A usable web interface with visible, step by step transparency into how each answer was produced
- An honest, measured understanding of where the system's real bottleneck is, and why, which is more valuable for a viva than a system that just claims to be fast

## 9. Known limitations

- Answer generation takes 20 to 30 seconds because of the reasoning model's behavior. A faster non reasoning model would reduce this significantly at some cost to answer depth.
- The import walk uses simple text matching on import lines rather than a full AST based import resolver, which is a reasonable scope decision for a project this size but would not handle more complex import patterns like relative imports with aliases.
- The parser only understands Python. Extending it to other languages would need a different parsing approach for each language.
- The vector database is a flat NumPy index, which is simple and fast at this scale, but would need a proper indexing structure to remain fast on codebases with hundreds of thousands of chunks.

---

## 10. Running it

You need [LM Studio](https://lmstudio.ai) installed, with Qwen3.5 9B and nomic-embed-text v1.5 both loaded and the local server started on port 1234.

```bash
pip install -r offlinerag/requirements.txt

cd offlinerag
python test_week1.py     # connection, embeddings, and search
python test_week2.py     # parser
python test_week3.py     # full question answering pipeline
python test_week5.py     # performance benchmarks

streamlit run frontend/app.py    # the web dashboard
```

In the dashboard, paste the path to any Python folder into the sidebar, click Index Codebase, and start asking questions.
