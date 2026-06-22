# Verification test script for Week 3 Engine Routing
import sys
import os

# Ensure Python can import from backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.llm import LMStudioClient
from backend.vector_db import LocalVectorDB
from backend import engine

def run_test():
    print("=" * 60)
    print("        OfflineRAG: Week 3 Engine Pipeline Test Script")
    print("=" * 60)

    # 1. Initialize Clients
    print("\nInitializing local API clients and NumPy vector database...")
    try:
        llm_client = LMStudioClient()
        db = LocalVectorDB()
    except Exception as e:
        print(f" -> ERROR: Initialization failed. Check if LM Studio is running. {e}")
        return

    # 2. Run codebase indexing
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_codebase = os.path.join(current_dir, "test_codebase")
    
    print(f"\n[INDEXING] Crawling and embedding target repository: {target_codebase}...")
    try:
        count = engine.index_codebase(target_codebase, db, llm_client)
        print(f" -> SUCCESS: Indexed {count} classes, methods, and functions into database!")
    except Exception as e:
        print(f" -> ERROR: Indexing codebase failed.\n{e}")
        return

    # 3. Test Question Answering Pipeline
    question = "How are user passwords hashed in the application?"
    print(f"\n[QUERY] Question: '{question}'")
    print("\nRunning the 5-step deterministic search pipeline:\n")

    try:
        response_generator = engine.answer_question(question, db, llm_client)
        
        answer_started = False
        for status in response_generator:
            step = status["step"]
            detail = status.get("detail", "")
            token = status.get("token", "")
            
            if step != "answer":
                # Print status steps with formatting
                print(f"[{step.upper():<10}] {detail}")
            else:
                if not answer_started:
                    print(f"\n[{step.upper():<10}] ", end="", flush=True)
                    answer_started = True
                # Print answer tokens inline
                print(token, end="", flush=True)
                
        print("\n\n" + "=" * 60)
        print("    ALL WEEK 3 PIPELINE TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n -> ERROR: Pipeline execution failed.\n{e}")
        return

if __name__ == "__main__":
    run_test()
