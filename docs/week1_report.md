# Amity University Noida
## B.Tech CSE — NTCC Weekly Progress Report

**Report No:** 01  
**Period:** 1st June 2026 – 7th June 2026  
**Project Title:** OfflineRAG: A Local LLM Agent for Intelligent Codebase Comprehension  
**Student Name:** Siddharth Sharma  
**Enrollment No:** A2305225258 
**Guide Name:** Ms. Dolly Sharma  

---

### 1. Objectives for the Week
1. Establish the repository folder structure and configure bare-minimum dependencies (`requirements.txt`).
2. Configure the **LM Studio** local server with **Qwen3-8B (Chat LLM)** and **nomic-embed-text (Embedding Model)** to run entirely locally in VRAM.
3. Write standard local Python connector class (`llm.py`) to stream tokens and request embeddings.
4. Develop a zero-dependency, pure Python and NumPy-based local vector store (`vector_db.py`) implementing exact **Cosine Similarity** under a scope-capped limit of 80 lines.
5. Create an automated integration test script (`test_week1.py`) to verify API connectivity, vector loading, search ranking, and streaming token generation.

---

### 2. Work Done During the Week
The first week was dedicated to establishing a bulletproof, zero-dependency core architecture that operates completely offline on consumer GPU hardware.

#### A. Repository Setup & Directory Structure
To isolate our application logic and ensure neat organization, the project structure was initialized strictly as follows:
```text
E:\Antigravity\Workspaces\OfflineRAG\
│
├── offlinerag/
│   ├── backend/
│   │   ├── llm.py             # Client wrapper connecting to local LM Studio
│   │   ├── vector_db.py       # Custom NumPy vector index (74 lines of pure Python)
│   │   └── __init__.py
│   │
│   ├── data/                  # Directory where NumPy indices (JSON) are stored
│   │   └── .gitkeep
│   │
│   ├── test_week1.py          # Integration test verifying the entire backend
│   └── requirements.txt       # Essential packages only (openai, numpy, streamlit)
│
└── docs/
    └── week1_report.md        # This progress report
```

#### B. Bare-Minimum Python Requirements
To avoid memory leaks, large virtual environments, and GPU clashes associated with heavy frameworks like PyTorch or HuggingFace, dependencies were capped strictly to:
*   `openai`: For clean, OpenAI-compatible HTTP communication with LM Studio's `/v1/` local server.
*   `numpy`: For high-speed, vectorized mathematical matrix operations.
*   `streamlit`: For our upcoming rapid-deployment frontend.

#### C. Local Dual-Model LM Studio Setup
Rather than running PyTorch models in our Python process (which would conflict with LM Studio for GPU memory resources), we loaded both the reasoning LLM and the embedding model inside LM Studio:
1.  **Qwen3-8B (Q4_K_M quantization - ~4.8 GB):** Loaded into 8GB VRAM with max GPU offload, leaving ~1.5 GB for context KV Cache.
2.  **nomic-embed-text (GGUF - ~300 MB):** Loaded side-by-side as the embedding endpoint.
3.  **Result:** Exposes completions and embeddings locally at `http://localhost:1234/v1`.

#### D. The Custom Pure-NumPy Vector Database
To maintain absolute mathematical and algorithmic transparency, a lightweight vector store was written in single-file pure Python using **NumPy** (`vector_db.py`). 

##### Mathematical Foundation
Semantic vector search calculates the angular similarity between the query coordinate vector $\mathbf{q}$ and the indexed code chunk vectors $\mathbf{c}_i$. The exact formula implemented is **Cosine Similarity**:

$$\text{Cosine Similarity}(\mathbf{c}_i, \mathbf{q}) = \frac{\mathbf{c}_i \cdot \mathbf{q}}{\|\mathbf{c}_i\| \|\mathbf{q}\|} = \frac{\sum_{j=1}^{d} c_{i,j} q_j}{\sqrt{\sum_{j=1}^{d} c_{i,j}^2} \sqrt{\sum_{j=1}^{d} q_j^2}}$$

##### Vectorized NumPy Implementation
By converting our lists of embeddings into a 2D matrix, we perform this mathematical search in parallel using optimized C-level CPU/GPU matrix algebra:
```python
# Convert lists of embeddings to a 2D matrix
embeddings_matrix = np.array([c["embedding"] for c in self.chunks], dtype=np.float32)
q = np.array(query_embedding, dtype=np.float32)

# Compute dot products in parallel
dot_product = np.dot(embeddings_matrix, q)

# Compute vectors norms
matrix_norms = np.linalg.norm(embeddings_matrix, axis=1)
query_norm = np.linalg.norm(q)

# Calculate similarity scores with a tiny safety epsilon (1e-9) to avoid division by zero
similarities = dot_product / (matrix_norms * query_norm + 1e-9)
```

---

### 3. Integration Testing & Verification
The automated verification script **`offlinerag/test_week1.py`** was executed to validate the architecture. 

**Test Log Results:**
```text
============================================================
        OfflineRAG: Week 1 Integration Test Script
============================================================

[TEST 1] Connecting to LM Studio Local Server...
 -> Success: OpenAI client initialized pointing to http://localhost:1234/v1

[TEST 2] Generating Local Text Embedding via nomic-embed-text...
 -> Sending sample text: 'def connect_to_database(): return db_session.connect()'
 -> Success: Embedding vector generated successfully!
 -> Vector Dimension: 768
 -> Latency: 0.0412 seconds
 -> First 5 numbers: [-0.0435, 0.0211, -0.0984, 0.0154, 0.0332]

[TEST 3] Loading Custom NumPy Vector Database...
 -> Success: LocalVectorDB instantiated and cleared.
 -> Encoding and indexing 3 mock codebase chunks...
   * Embedding chunk from database.py...
   * Embedding chunk from auth.py...
   * Embedding chunk from models.py...
 -> Success: 3 chunks saved successfully to data/vector_index.json

[TEST 4] Testing Semantic Vector Search...
 -> User Query: 'database connection and query setup'
 -> Generating query embedding...
 -> Running NumPy Cosine Similarity calculation (Top 2)...

   [Rank 1] Cosine Similarity Score: 0.8124
   [File] database.py (Lines 12-15)
   [Content]:
   def connect_to_database():
       return db_session.connect()

   [Rank 2] Cosine Similarity Score: 0.6120
   [File] models.py (Lines 5-10)
   [Content]:
   class UserModel(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       username = db.Column(db.String)

 -> Success: Semantic retrieval verified!

[TEST 5] Testing Qwen3-8B LLM Token Streaming...
 -> Sending prompt to Qwen3-8B local server...
 -> Response: print("Welcome to OfflineRAG! Your privacy-first, fully local codebase assistant.")
 -> Success: Streaming completed in 0.84 seconds!

============================================================
    ALL WEEK 1 INTEGRATION TESTS COMPLETED SUCCESSFULLY!
============================================================
```

---

### 4. Self-Evaluation & Learnings
*   **VRAM Containment:** Confirmed that by keeping the model sizes modest (Qwen3-8B and nomic-embed-text), both reside fully on the GPU, yielding embedding generation speeds under **50ms** and LLM generation under **1 second**—proving the viability of fully local operations.
*   **Clean Code Separation:** Separating the vector search mathematical operations (`vector_db.py`) from the API communication wrapper (`llm.py`) keeps our modules isolated, simple to explain, and easy to grade.

---

### 5. Plan for Next Week
*   Implement `parser.py` recursively crawling directories, ignoring files specified in `.gitignore`.
*   Integrate Python's native `ast` (Abstract Syntax Tree) module to parse Python files and extract structured chunks (class declarations and function scopes with correct line numbers and surrounding comments) instead of doing naive line splits.
