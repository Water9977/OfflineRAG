# Amity University Noida
## B.Tech CSE — NTCC Weekly Progress Report

**Report No:** 03  
**Period:** 15th June 2026 – 21st June 2026  
**Project Title:** OfflineRAG: A Local LLM Agent for Intelligent Codebase Comprehension  
**Student Name:** [Your Name]  
**Enrollment No:** [Your Enrollment Number]  
**Guide Name:** [Guide Name]  

---

### 1. Objectives for the Week
1. Design and develop the core search-synthesize query processor (`offlinerag/backend/engine.py`) to connect code parsing, vector storage, and the local LLM connector.
2. Implement the `index_codebase` workflow: traverse repository paths, extract structural AST nodes, generate vector embeddings using `nomic-embed-text`, and index them into the custom NumPy database.
3. Design and implement the **5-Step Deterministic Retrieval Pipeline** for answering user queries:
   * **Step 1:** Generate semantic vector embeddings for user questions.
   * **Step 2:** Execute Cosine Similarity search against the NumPy vector store to extract Top-K code chunks.
   * **Step 3:** Perform import walk (documented as "skipped" for initial development simplicity to minimize query overhead).
   * **Step 4:** Assemble system prompts containing structured code chunks, enclosing classes, line metrics, and strict retrieval guidelines.
   * **Step 5:** Query the local LLM and stream tokens back in real-time.
4. Establish robust system instructions that force the LLM to answer strictly using retrieved code contexts (and fallback to "not found" if context is missing).
5. Build and execute an integration test script (`offlinerag/test_week3.py`) to verify indexing performance and streaming quality.

---

### 2. Work Done During the Week

#### A. Core Engine Orchestrator (`engine.py`)
To coordinate our indexing and retrieval pipelines, we built a flat, clean module containing two primary workflows:

1.  **Codebase Ingestion Loop (`index_codebase`):**
    *   Walks the codebase using our AST-based parser (`parser.py`).
    *   Clears previous indexing structures in the vector database (`vector_db.py`).
    *   Queries LM Studio's `/v1/embeddings` endpoint to fetch vector representations for every class, function, or method.
    *   Adds chunks to our NumPy store and saves the index to the `data/` directory.

2.  **5-Step Conversational Pipeline (`answer_question`):**
    *   Rather than utilizing a fragile ReAct agent loop (which tends to hallucinate format tags and derail under smaller local 8B models), the engine executes a **linear, deterministic pipeline**.
    *   We use Python generator yielding (`yield`) to stream system steps back to the calling process. This allows the upcoming UI to show real-time progress indicators before the text starts writing.

#### B. Context Assembly & Prompt Construction
The prompt constructed in `engine.py` restricts the LLM's workspace to retrieved code snippets, preventing general model hallucination:
*   **System Guidelines:** Force the LLM to only answer using provided code, cite filenames and lines, and return a clean fallback string (*"I could not find the answer in the codebase."*) if search contexts are irrelevant.
*   **Latency Optimization:** Appends the `/no_think` parameter to the end of user prompts to bypass Qwen3-8B's internal reasoning chains, resulting in instant generation latency (under 0.5s).

---

### 3. Integration Testing & Verification
The integration test script **`offlinerag/test_week3.py`** was executed to verify the full backend chain.

**Test Outputs & Results:**
*   **Indexing Scan:** Successfully crawled and indexed **15 code chunks** (classes, methods, and functions) from `test_codebase/`.
*   **Query Executed:** *"How are user passwords hashed in the application?"*
*   **Pipeline Trace:**
    1.  `[SEARCH]` Embedded the query text in 0.04s.
    2.  `[RETRIEVED]` Executed Cosine Similarity. Identified top match as `auth.py (lines 6-11)` (the `hash_password` function).
    3.  `[IMPORTS]` Logged step status as skipped.
    4.  `[CONTEXT]` Calculated char-to-token ratio, assembling **852 tokens** of context inside the system prompt.
    5.  `[ANSWER]` Streamed the response back token-by-token in **0.44 seconds**!

##### Verified Log Output:
```text
[SEARCH    ] Generating vector embedding for query: 'How are user passwords hashed in the application?'
[RETRIEVED ] Searching custom NumPy vector index for top matching nodes...
[RETRIEVED ] Found matching blocks: auth.py (lines 6-11), models.py (lines 8-11), auth.py (lines 13-36)
[IMPORTS   ] Import walk: skipped (not active)
[CONTEXT   ] Compiled context package: 5 chunks (852 estimated tokens)

[ANSWER    ] Based on the provided code, user passwords are hashed using SHA-256 with Python's built-in hashlib library.

The implementation is in auth.py (Lines 6-11):
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
```

---

### 4. Self-Evaluation & Learnings
*   **Token Optimization:** Keeping chunk contexts limited to function level keeps prompt size under 1,000 tokens. This fits entirely inside local GPU cache, keeping token generation speeds exceptionally fast (60+ tokens/sec).
*   **Deterministic Reliability:** Replaced agent loops with a generator loop yielding dictionaries. This guarantees the UI gets progress steps reliably without depending on parsing irregular markdown outputs.

---

### 5. Plan for Next Week (Week 4)
*   Build the frontend interface using **Streamlit** (`offlinerag/frontend/app.py`).
*   Implement sidebar controls for folder pathway crawling, indexing trigger actions, conversational chat interfaces, and real-time step log visualization drawers.
