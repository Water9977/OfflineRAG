# Amity University Noida
## B.Tech CSE — NTCC Weekly Progress Report

**Report No:** 04  
**Period:** 22nd June 2026 – 28th June 2026  
**Project Title:** OfflineRAG: A Local LLM Agent for Intelligent Codebase Comprehension  
**Student Name:** [Your Name]  
**Enrollment No:** [Your Enrollment Number]  
**Guide Name:** [Guide Name]  

---

### 1. Objectives for the Week
1. Fix the relative path default configuration inside the custom NumPy database (`vector_db.py`) to prevent folder duplication bugs.
2. Develop a rapid-deployment web dashboard (`offlinerag/frontend/app.py`) using **Streamlit** to act as our primary developer chat console.
3. Configure **Streamlit Session State** variables to store the database, LLM client connection state, and message logs between reruns.
4. Implement Sidebar controls: directory input fields, indexing trigger buttons, and codebase status indicators showing total chunks loaded.
5. Create a generator splitter pattern in `app.py` to stream tokens to `st.write_stream()` while capturing and displaying logs inside an expandable retrieval drawer below each answer.
6. Test running the complete system locally.

---

### 2. Work Done During the Week

#### A. Fixing the NumPy Database Directory Default
Previously, the default path for indexing was hardcoded to `offlinerag/data`, which caused duplicate folders when running commands from different root directories. We refactored `vector_db.py` to dynamically locate the backend folder using python's file system variables and resolve directories relative to that:
```python
base = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base, "..", "data")
```
This forces all indexes to be saved consistently inside `offlinerag/data/`.

#### B. Bare-Minimum Web UI Design
We avoided complex custom styling, CSS templates, and session-state wrappers. The interface is written in pure Python using Streamlit:
1.  **Sidebar Configuration:**
    *   `st.text_input` captures the absolute folder path of the codebase to crawl.
    *   `st.button` triggers the `index_codebase` orchestrator.
    *   Dynamic checks display the indexing state (e.g. *Active Codebase (15 chunks indexed)* or a warning *Not Indexed*).
2.  **Main Conversational Interface:**
    *   Renders messages from `st.session_state.messages` using `st.chat_message`.
    *   `st.chat_input` captures queries.

#### C. The Generator Splitter Wrapper
`st.write_stream` expects a generator yielding raw strings. However, `engine.answer_question()` yields status dictionaries containing logs. To solve this, we implemented a generator wrapper:
```python
current_steps = []

def token_generator():
    response_gen = engine.answer_question(user_query, st.session_state.db, st.session_state.llm_client)
    for item in response_gen:
        if item["step"] == "answer":
            yield item["token"]
        else:
            current_steps.append(item)
```
This loops through the engine, redirects non-answer logs to a list, and yields only text tokens to Streamlit. Right after the stream finishes, we render the logged steps inside `st.expander` and append them to memory.

---

### 3. Integration Testing & Verification
The interface was successfully launched and accessed via the local network at `http://localhost:8501`.

*   **Ingestion Test:** Paste path `E:\OfflineRAG\offlinerag\test_codebase` into the sidebar. Press "Index Codebase". The system scanned, converted, and stored the 15 code chunks, updating the sidebar status instantly.
*   **Chat Test:** Sent query *"Explain the register_user route"*. The dashboard streamed the explanation instantly and loaded the steps inside the dropdown expander below the reply.

---

### 4. Plan for Next Week (Week 5)
*   Perform profiling evaluations (RAM/VRAM consumption, token speed, and retrieval precision).
*   Compile the **Final B.Tech CSE NTCC Project Report** (approx. 40-50 pages following Amity guidelines).
*   Prepare viva slide deck and test the "zero-internet" demo mode.
