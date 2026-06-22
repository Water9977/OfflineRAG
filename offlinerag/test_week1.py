import sys
import os
import time

# Ensure Python can import from backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.llm import LMStudioClient
from backend.vector_db import LocalVectorDB

def run_test():
    print("=" * 60)
    print("        OfflineRAG: Week 1 Integration Test Script")
    print("=" * 60)
    
    # 1. Initialize LM Studio local API client
    print("\n[TEST 1] Connecting to LM Studio Local Server...")
    try:
        client = LMStudioClient()
        print(" -> Success: OpenAI client initialized pointing to http://127.0.0.1:1234/v1")
    except Exception as e:
        print(f" -> ERROR: Initialization failed. {e}")
        return

    # 2. Test nomic-embed-text embedding model
    print("\n[TEST 2] Generating Local Text Embedding via nomic-embed-text-v1.5@q8_0...")
    try:
        sample_text = "def connect_to_database(): return db_session.connect()"
        print(f" -> Sending sample text: '{sample_text}'")
        
        start_time = time.time()
        embedding = client.get_embedding(sample_text)
        latency = time.time() - start_time
        
        print(" -> Success: Embedding vector generated successfully!")
        print(f" -> Vector Dimension: {len(embedding)}")
        print(f" -> Latency: {latency:.4f} seconds")
        print(f" -> First 5 numbers: {embedding[:5]}")
    except Exception as e:
        print(f" -> ERROR: Embedding generation failed.\n{e}")
        print("\n[HELP] Please make sure of the following:")
        print(" 1. LM Studio is open and local server is started (port 1234).")
        print(" 2. 'text-embedding-nomic-embed-text-v1.5@q8_0' model is loaded in the Server dropdown.")
        return

    # 3. Test Local NumPy Vector Database and Cosine Similarity
    print("\n[TEST 3] Loading Custom NumPy Vector Database...")
    try:
        db = LocalVectorDB()
        db.clear() # Clear previous runs
        print(" -> Success: LocalVectorDB instantiated and cleared.")
        
        # We will embed and add 3 different code structures to mock a mini repository
        mock_chunks = [
            (
                "def connect_to_database():\n    return db_session.connect()", 
                {"filename": "database.py", "lines": "12-15"}
            ),
            (
                "def register_user(username, password):\n    hash = bcrypt.hash(password)\n    return db.insert(username, hash)", 
                {"filename": "auth.py", "lines": "25-30"}
            ),
            (
                "class UserModel(db.Model):\n    id = db.Column(db.Integer, primary_key=True)\n    username = db.Column(db.String)", 
                {"filename": "models.py", "lines": "5-10"}
            )
        ]
        
        print(" -> Encoding and indexing 3 mock codebase chunks...")
        for content, metadata in mock_chunks:
            print(f"   * Embedding chunk from {metadata['filename']}...")
            vec = client.get_embedding(content)
            db.add_chunk(content, metadata, vec)
            
        db.save()
        print(" -> Success: 3 chunks saved successfully to data/vector_index.json")
    except Exception as e:
        print(f" -> ERROR: Database indexing failed.\n{e}")
        return

    # 4. Perform Cosine Similarity Semantic Search
    print("\n[TEST 4] Testing Semantic Vector Search...")
    try:
        search_query = "database connection and query setup"
        print(f" -> User Query: '{search_query}'")
        
        print(" -> Generating query embedding...")
        query_vec = client.get_embedding(search_query)
        
        print(" -> Running NumPy Cosine Similarity calculation (Top 2)...")
        matches = db.search(query_vec, top_k=2)
        
        for rank, (chunk, score) in enumerate(matches, 1):
            print(f"\n   [Rank {rank}] Cosine Similarity Score: {score:.4f}")
            print(f"   [File] {chunk['metadata']['filename']} (Lines {chunk['metadata']['lines']})")
            print(f"   [Content]:\n{chunk['content']}")
            
        print("\n -> Success: Semantic retrieval verified!")
    except Exception as e:
        print(f" -> ERROR: Search failed.\n{e}")
        return

    # 5. Test Qwen3-8B Chat Completions with Streaming
    print("\n[TEST 5] Testing Qwen3-8B LLM Token Streaming...")
    try:
        messages = [
            {"role": "system", "content": "You are a professional coding assistant."},
            {"role": "user", "content": "Write a 1-line Python print statement welcoming developers to OfflineRAG. /no_think"}
        ]
        print(" -> Sending prompt to Qwen3-8B local server...")
        print(" -> Response: ", end="", flush=True)
        
        start_time = time.time()
        for token in client.stream_chat(messages):
            print(token, end="", flush=True)
        print()
        
        latency = time.time() - start_time
        print(f" -> Success: Streaming completed in {latency:.2f} seconds!")
    except Exception as e:
        print(f"\n -> ERROR: Chat generation failed.\n{e}")
        print("\n[HELP] Please make sure of the following:")
        print(" 1. 'qwen/qwen3-8b' is loaded in LM Studio server dropdown.")
        print(" 2. Server is active.")
        return

    print("\n" + "=" * 60)
    print("    ALL WEEK 1 INTEGRATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_test()
