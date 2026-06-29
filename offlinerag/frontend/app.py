# Streamlit web dashboard for OfflineRAG
import os
import sys
import streamlit as st

# Add the parent directory (offlinerag root) to sys.path to resolve backend imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from backend import engine
from backend.llm import LMStudioClient
from backend.vector_db import LocalVectorDB

# 1. Page configuration (plain layout, no custom CSS)
st.set_page_config(page_title="OfflineRAG", layout="wide")
st.title("OfflineRAG")

# 2. Session State Initialization
if "db" not in st.session_state:
    st.session_state.db = LocalVectorDB()
if "llm_client" not in st.session_state:
    st.session_state.llm_client = LMStudioClient()
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Sidebar Controls
st.sidebar.header("Codebase Settings")
codebase_path = st.sidebar.text_input(
    "Local Codebase Folder Path:",
    placeholder="e.g. E:\\Projects\\MyFlaskApp"
)

if st.sidebar.button("Index Codebase"):
    if not codebase_path:
        st.sidebar.error("Please enter a folder path.")
    elif not os.path.isdir(codebase_path):
        st.sidebar.error("Invalid directory path.")
    else:
        with st.sidebar.spinner("Scanning and embedding codebase..."):
            try:
                # Triggers crawling, AST parsing, embedding, and NumPy index generation
                count = engine.index_codebase(
                    codebase_path, 
                    st.session_state.db, 
                    st.session_state.llm_client
                )
                st.sidebar.success(f"Indexed {count} chunks!")
            except Exception as e:
                st.sidebar.error(f"Indexing failed: {e}")

# Sidebar status display
chunk_count = len(st.session_state.db.chunks)
if chunk_count > 0:
    st.sidebar.info(f"Status: Active Codebase ({chunk_count} chunks indexed)")
else:
    st.sidebar.warning("Status: Not Indexed (Please specify codebase path)")

# 4. Chat History Rendering
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        # Render the logged retrieval steps for previous assistant replies
        if msg["role"] == "assistant" and "steps" in msg and msg["steps"]:
            with st.expander("Retrieval steps"):
                for step in msg["steps"]:
                    st.write(f"**[{step['step'].upper()}]** {step['detail']}")

# 5. Active Chat Input & Response Loop
if user_query := st.chat_input("Ask a question about the codebase..."):
    # Render user query immediately
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    # Render assistant placeholder to stream the answer
    with st.chat_message("assistant"):
        # Storage to gather steps from the mixed generator outputs
        current_steps = []
        
        # Wrapper generator to yield ONLY token strings to st.write_stream
        def token_generator():
            try:
                response_gen = engine.answer_question(
                    user_query, 
                    st.session_state.db, 
                    st.session_state.llm_client
                )
                for item in response_gen:
                    if item["step"] == "answer":
                        yield item["token"]
                    else:
                        current_steps.append(item)
            except Exception as ex:
                yield f"\nConnection Error: {ex}"
        
        # Streams tokens to the page
        full_answer = st.write_stream(token_generator)
        
        # Display the expandable steps drawer directly below the answer
        if current_steps:
            with st.expander("Retrieval steps"):
                for step in current_steps:
                    st.write(f"**[{step['step'].upper()}]** {step['detail']}")
                    
        # Save assistant's reply and its retrieval logs to memory
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_answer,
            "steps": current_steps.copy()
        })
