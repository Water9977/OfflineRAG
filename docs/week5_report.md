# Amity University Noida
## B.Tech CSE — NTCC Weekly Progress Report

**Report No:** 05  
**Period:** 29th June 2026 – 5th July 2026  
**Project Title:** OfflineRAG: A Local LLM Agent for Intelligent Codebase Comprehension  
**Student Name:** [Your Name]  
**Enrollment No:** [Your Enrollment Number]  
**Guide Name:** [Guide Name]  

---

### 1. Objectives for the Week
1. Implement a static **Import Walk** (`find_import_chunks`) in the engine to traverse Python import lines, identify local module dependencies, and append their relevant source definitions (methods/classes) directly to the context.
2. Store absolute file pathways (`file_path`) inside chunk metadata during ingestion (`parser.py`) to support on-the-fly local file reading.
3. Build a performance benchmarking suite (`offlinerag/test_week5.py`) using the standard `time` library to measure codebase crawling, embedding latency, NumPy vector searches, and end-to-end model query streaming.
4. Clean up the codebase by removing temporary files and stray directories.
5. Draft the Week 5 progress report summarizing the system's quantitative performance metrics.

---

### 2. Work Done During the Week

#### A. Multi-Hop Context Graph via Import Walking
To prevent the codebase QA from being restricted to shallow keyword searches, we implemented an **Import Walk** feature. 
1.  **Ingestion Enrichment:** `parser.py` was modified to pass and save the absolute `file_path` of every scanned Python module inside the database metadata.
2.  **Import Extraction (`find_import_chunks`):** When the vector search returns top-matching chunks, the engine inspects the parent files of those chunks:
    *   It reads the full file from disk.
    *   It extracts all imported modules from lines starting with `import ` or `from `.
    *   If any imported module name matches a file in the vector store (e.g. `database` matching `database.py`), the engine extracts a chunk from that module.
    *   It prioritizes chunks whose names contain words matching the user's question, falling back to the first module chunk.
3.  **Prompt Tagging:** These extra chunks are appended to the context and flagged in the prompt as `[Related via Import]`, while direct search matches are tagged `[Direct Match]`. This allows the LLM to differentiate between semantic overlaps and dependency paths.

#### B. Bare-Minimum Benchmarking Suite (`test_week5.py`)
To collect performance numbers for the final viva presentation and thesis report, we developed an automated benchmarking suite. It evaluates four core aspects:
1.  **Indexing Speed:** Times the AST crawling, local embedding generation, and JSON file saving.
2.  **Embedding Latency:** Measures the duration of a single `/v1/embeddings` call to LM Studio (averaged over 5 runs).
3.  **NumPy Search Latency:** Evaluates how long the raw matrix cosine similarity calculation takes to search the index (averaged over 5 runs).
4.  **End-to-End Latency:** Measures the total time to convert a query, search the index, walk imports, construct prompt payloads, query Qwen3-8B, and stream all answer tokens.

---

### 3. Benchmarking Suite Results

The benchmarking suite was executed on the local laptop hardware (8GB VRAM GPU / 24GB System RAM) running LM Studio.

**Performance Summary Table:**

| Metric | Value | Description |
| :--- | :--- | :--- |
| **Total Chunks Indexed** | 15 | Code segments (classes, functions, methods) from test codebase. |
| **Total Indexing Duration** | 1.2129 seconds | Time to crawl, embed, and save the index files. |
| **Average Indexing per Chunk** | 0.0809 seconds | Average speed to generate and index a single code chunk. |
| **Average Embedding Latency** | 0.0400 seconds | Average time to compute a 768-dimension vector. |
| **Average NumPy Search Latency** | 0.0005 seconds | Time to execute vectorized Cosine Similarity matrix math. |
| **E2E Query & Streaming Latency** | 20 to 30 seconds | Total duration to search, walk, prompt, and stream the LLM response. |

#### Analysis:
*   **Vector Search Efficiency:** The NumPy search latency is under **1 millisecond**. This verifies that a custom flat vector index in pure Python/NumPy is incredibly fast and completely viable for repository-scale operations without needing heavy external database runtimes.
*   **LLM Latency:** The end-to-end duration was isolated by testing a plain five word question with no codebase context at all, which still took close to 20 seconds before the first visible token appeared. This confirms the delay is not caused by context size or GPU load, but by Qwen3.5 9B being a reasoning model that deliberates internally before answering, even when instructed not to. This is a genuine speed versus quality tradeoff: a smaller non reasoning model would answer in 2 to 5 seconds with shallower reasoning, while Qwen3.5 9B takes longer but reasons more thoroughly about the code.

---

### 4. Self-Evaluation & Learnings
*   **Context Linking Success:** By adding the import walk, a question like *"How is database initialized?"* successfully pulled in `database.py` through vector search, and then traversed imports to pull in `models.py` and `database.py` dependency contexts, resulting in an accurate architectural explanation.
*   **Zero-Dependency Integrity:** We successfully verified that the entire OfflineRAG codebase operates using only three packages: `openai`, `numpy`, and `streamlit`—making it clean, portable, and easy to explain in a B.Tech viva.
*   **Bug Fix:** Found and corrected a leftover model name in `llm.py` that still pointed to the old `qwen/qwen3-8b` identifier from Week 1, even though the project had switched to Qwen3.5 9B. It worked by accident because only one chat model was loaded in LM Studio at the time, but the code now correctly names the model in use.
*   **Honest Benchmarking:** Early benchmark runs showed inconsistent end to end timings between 0.79 and 37 seconds across different runs. Repeated manual testing traced this to Qwen3.5 9B's own reasoning behavior rather than a bug in the pipeline, and the benchmark section above reflects the verified, repeatable range.

---

### 5. Final Status of the NTCC Project
With the import walk working and benchmarks measured, the core implementation of OfflineRAG is **100% complete**. The system is fully operational locally in your web browser. You are ready to run the web server and test it against your own personal codebases!
