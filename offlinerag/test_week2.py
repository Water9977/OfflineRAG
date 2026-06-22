# Verification script for Week 2 AST Parser
import sys
import os

# Ensure Python can import from backend/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.parser import parse_directory

def run_test():
    print("=" * 60)
    print("        OfflineRAG: Week 2 AST Parser Test Script")
    print("=" * 60)
    
    # Define target path to test_codebase
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_codebase = os.path.join(current_dir, "test_codebase")
    
    print(f"\nScanning directory: {target_codebase}...\n")
    chunks = parse_directory(target_codebase)
    
    print(f"Total searchable chunks extracted: {len(chunks)}")
    print("-" * 60)
    
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk["metadata"]
        print(f"\n[{i}] Name: {metadata['name']}")
        print(f"    File:         {metadata['filename']}")
        print(f"    Type:         {metadata['type']}")
        print(f"    Parent Class: {metadata['parent_class']}")
        print(f"    Lines:        {metadata['lines']}")
        print(f"    Docstring:    {repr(metadata['docstring'])}")
        
        # Print a preview of the source code (indented for clarity)
        code_lines = chunk["content"].splitlines()
        preview = "\n".join(f"        {line}" for line in code_lines[:3])
        if len(code_lines) > 3:
            preview += "\n        ..."
            
        print("    Code Preview:")
        print(preview)
        print("-" * 40)

if __name__ == "__main__":
    run_test()
