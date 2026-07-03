# Query execution engine coordinating parsing, indexing, and LLM communication
import os
from typing import Generator
from backend import parser
from backend import vector_db
from backend import llm

def index_codebase(folder_path: str, db: vector_db.LocalVectorDB, llm_client: llm.LMStudioClient) -> int:
    """
    Crawls a target folder, parses all Python files, generates vector
    embeddings for all chunks, and saves them to the custom local database.
    """
    # 1. Parse directory into abstract syntax tree chunks
    chunks = parser.parse_directory(folder_path)
    
    # 2. Reset database for a fresh indexing run
    db.clear()
    
    # 3. Generate embeddings and populate vector store
    for chunk in chunks:
        content = chunk["content"]
        metadata = chunk["metadata"]
        embedding = llm_client.get_embedding(content)
        db.add_chunk(content, metadata, embedding)
        
    # 4. Write data to json database file
    db.save()
    return len(chunks)

def find_import_chunks(matches: list, all_chunks: list, question: str) -> list:
    """Finds related code chunks from local modules imported by the matched chunks."""
    imported_modules = set()
    for match, _ in matches:
        f_path = match["metadata"].get("file_path")
        if f_path and os.path.exists(f_path):
            try:
                with open(f_path, "r", encoding="utf-8") as f:
                    for line in f.read().splitlines():
                        if line.strip().startswith(("import ", "from ")):
                            words = [w.strip() for w in line.replace(",", " ").replace(".", " ").split()]
                            imported_modules.update(w for w in words if w not in ("import", "from", "as", "*"))
            except Exception:
                continue
                
    extra_chunks, retrieved = [], {m[0]["metadata"]["name"] for m in matches}
    q_words = set(question.lower().split())
    for mod in imported_modules:
        candidates = [c for c in all_chunks if os.path.basename(c["metadata"]["filename"]).replace(".py", "") == mod 
                      and c["metadata"]["name"] not in retrieved]
        if candidates:
            best = next((c for c in candidates if any(w in c["metadata"]["name"].lower() for w in q_words)), candidates[0])
            extra_chunks.append(best)
            retrieved.add(best["metadata"]["name"])
    return extra_chunks

def build_synthesis_prompt(retrieved_chunks: list, question: str) -> list:
    """
    Constructs the system and user messages package for the LLM.
    Restricts the model to answer only using the provided codebase snippets.
    """
    system_instruction = (
        "You are an expert software developer assistant analyzing a local codebase.\n"
        "Your task is to answer user questions using ONLY the provided code chunks.\n"
        "Strict Guidelines:\n"
        "1. Answer based solely on the provided code blocks.\n"
        "2. If you are unsure or the context does not contain the answer, say exactly: "
        "'I could not find the answer in the codebase.'\n"
        "3. Cite the exact filename and line numbers when referencing code.\n"
        "4. Be concise and keep your explanations direct and clean."
    )
    
    # Format all retrieved chunks into a single readable context block
    context_blocks = []
    for chunk, score in retrieved_chunks:
        meta = chunk["metadata"]
        relation_type = "Direct Match" if score > 0.0 else "Related via Import"
        block = (
            f"--- File: {meta['filename']} (Lines: {meta['lines']}) [{relation_type}] ---\n"
            f"Type: {meta['type']}\n"
            f"Name: {meta['name']}\n"
            f"Code:\n{chunk['content']}\n"
        )
        context_blocks.append(block)
        
    context_str = "\n".join(context_blocks)
    
    # Append /no_think at the end of the user prompt to disable reasoning if desired
    user_content = (
        f"Here is the relevant code context from my repository:\n\n{context_str}\n\n"
        f"Question: {question}\n\n/no_think"
    )
    
    return [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": user_content}
    ]

def answer_question(
    question: str, 
    db: vector_db.LocalVectorDB, 
    llm_client: llm.LMStudioClient
) -> Generator[dict, None, None]:
    """
    Executes the deterministic 5-step codebase search and retrieval pipeline.
    Yields status dictionaries to track progress, followed by streamed answer tokens.
    """
    # Step 1: Embed query question
    yield {"step": "search", "detail": f"Generating vector embedding for query: '{question}'"}
    query_embedding = llm_client.get_embedding(question)
    
    # Step 2: Search NumPy index
    yield {"step": "retrieved", "detail": "Searching custom NumPy vector index for top matching nodes..."}
    matches = db.search(query_embedding, top_k=5)
    
    if not matches:
        yield {"step": "retrieved", "detail": "No matching code blocks found."}
        yield {"step": "imports", "detail": "Import walk: skipped (no source file matches)"}
        yield {"step": "context", "detail": "Context built: 0 chunks (0 tokens)"}
        # Yield final answer
        yield {"step": "answer", "token": "I could not find any matching code in the codebase."}
        return
        
    # Format file list detail
    found_details = ", ".join(
        f"{m[0]['metadata']['filename']} (lines {m[0]['metadata']['lines']})"
        for m in matches
    )
    yield {"step": "retrieved", "detail": f"Found matching blocks: {found_details}"}
    
    # Step 3: Import walk
    extra_chunks = find_import_chunks(matches, db.chunks, question)
    imported_filenames = list(set(c["metadata"]["filename"] for c in extra_chunks))
    yield {"step": "imports", "detail": f"Following imports: {imported_filenames}"}
    
    # Add extra chunks to matches (similarity score = 0.0 means related via import)
    matches = matches + [(chunk, 0.0) for chunk in extra_chunks]
    
    # Step 4: Build prompt context
    messages = build_synthesis_prompt(matches, question)
    # Estimate token count (1 token ≈ 4 characters rule-of-thumb)
    total_chars = sum(len(m["content"]) for m in messages)
    token_estimate = total_chars // 4
    yield {"step": "context", "detail": f"Compiled context package: {len(matches)} chunks ({token_estimate} estimated tokens)"}
    
    # Step 5: Stream the synthesis response from local LLM
    yield {"step": "answer", "token": ""}  # Start answer phase
    for token in llm_client.stream_chat(messages):
        yield {"step": "answer", "token": token}
