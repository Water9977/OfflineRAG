# Performance benchmarking script for OfflineRAG
import sys
import os
import time

# Ensure Python can import from backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.llm import LMStudioClient
from backend.vector_db import LocalVectorDB
from backend import engine

def run_benchmarks():
    print("=" * 60)
    print("        OfflineRAG: Performance Benchmarking Suite")
    print("=" * 60)

    # Initialize clients
    try:
        llm_client = LMStudioClient()
        db = LocalVectorDB()
    except Exception as e:
        print(f" -> ERROR: Client initialization failed: {e}")
        return

    # Define target path to test_codebase
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_codebase = os.path.join(current_dir, "test_codebase")

    # 1. Measure Indexing Time
    print("\n[BENCHMARK 1] Measuring Indexing Speed...")
    start_time = time.time()
    num_chunks = engine.index_codebase(target_codebase, db, llm_client)
    indexing_time = time.time() - start_time
    avg_indexing_time = indexing_time / num_chunks if num_chunks > 0 else 0
    print(f" -> Result: Indexed {num_chunks} chunks in {indexing_time:.4f} seconds.")
    print(f" -> Average Time per Chunk: {avg_indexing_time:.4f} seconds.")

    # 2. Measure Embedding Latency (5 runs)
    print("\n[BENCHMARK 2] Measuring Embedding Model Latency (5 runs)...")
    sample_text = "def calculate_cosine_similarity(v1, v2): return np.dot(v1, v2)"
    embedding_times = []
    for i in range(5):
        run_start = time.time()
        _ = llm_client.get_embedding(sample_text)
        run_time = time.time() - run_start
        embedding_times.append(run_time)
        print(f"   * Run {i+1}: {run_time:.4f} seconds")
    avg_embedding_latency = sum(embedding_times) / 5

    # 3. Measure Search Latency (5 runs)
    print("\n[BENCHMARK 3] Measuring Vector Database Search Latency (5 runs)...")
    sample_vector = llm_client.get_embedding("user database configuration")
    search_times = []
    for i in range(5):
        run_start = time.time()
        _ = db.search(sample_vector, top_k=5)
        run_time = time.time() - run_start
        search_times.append(run_time)
        print(f"   * Run {i+1}: {run_time:.6f} seconds")
    avg_search_latency = sum(search_times) / 5

    # 4. Measure End-to-End Answer Latency
    print("\n[BENCHMARK 4] Measuring End-to-End Streaming Answer Latency...")
    question = "How is database initialized in database.py?"
    print(f" -> Query: '{question}'")
    
    e2e_start = time.time()
    generator = engine.answer_question(question, db, llm_client)
    
    # Drain generator fully
    tokens_streamed = 0
    for update in generator:
        if update["step"] == "answer":
            tokens_streamed += len(update["token"].split())
            
    e2e_time = time.time() - e2e_start
    print(f" -> Result: Streamed response complete in {e2e_time:.4f} seconds.")

    # 5. Render Final Performance Summary Table
    print("\n" + "=" * 60)
    print("              FINAL PERFORMANCE BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"| Metric                           | Value                  |")
    print(f"|----------------------------------|------------------------|")
    print(f"| Total Chunks Indexed             | {num_chunks:<22} |")
    print(f"| Total Indexing Duration          | {indexing_time:.4f} seconds        |")
    print(f"| Average Indexing Time per Chunk  | {avg_indexing_time:.4f} seconds        |")
    print(f"| Average Embedding Call Latency   | {avg_embedding_latency:.4f} seconds        |")
    print(f"| Average NumPy Search Latency     | {avg_search_latency:.6f} seconds        |")
    print(f"| E2E Query & Streaming Latency   | {e2e_time:.4f} seconds        |")
    print("=" * 60)

if __name__ == "__main__":
    run_benchmarks()
