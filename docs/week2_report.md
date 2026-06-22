# Amity University Noida
## B.Tech CSE — NTCC Weekly Progress Report

**Report No:** 02  
**Period:** 8th June 2026 – 14th June 2026  
**Project Title:** OfflineRAG: A Local LLM Agent for Intelligent Codebase Comprehension  
**Student Name:** [Your Name]  
**Enrollment No:** [Your Enrollment Number]  
**Guide Name:** [Guide Name]  

---

### 1. Objectives for the Week
1. Create a structured test codebase representing a realistic Python/Flask application (`offlinerag/test_codebase/`) containing files for routing, database helpers, database configurations, schemas/models, and user authentication logic.
2. Develop an AST-based parser (`offlinerag/backend/parser.py`) in pure Python to recursively crawl folders, parse Python files, and extract functions, classes, and methods.
3. Keep the parser logic simple, flat (no classes inside `parser.py`), and capped to under 2 nested logic levels to ensure high readability and clean code.
4. Verify code chunk extraction with correct line boundaries, enclosing parent classes, types, names, docstrings, and source segments.
5. Create an automated test runner (`offlinerag/test_week2.py`) to verify the chunker output.

---

### 2. Work Done During the Week

#### A. Creation of the Target Codebase (`test_codebase/`)
To test our parser on a real-world pattern, we built a mock Flask codebase with the following modular files:
*   `config.py`: Configuration variables (database name, port, keys).
*   `database.py`: Function to initialize tables and fetch SQLite rows.
*   `models.py`: Defines two distinct classes (`User`, `Post`) with initializers and object-to-dictionary serializer methods.
*   `auth.py`: Functions to hash passwords using SHA-256 and validate login credentials.
*   `app.py`: Functions representing API HTTP routes (home, register, login).

#### B. The Python AST Code Parser (`parser.py`)
Standard text chunkers split files using character count limits, which breaks python blocks (such as slicing a function mid-definition). This breaks LLM logical synthesis. 

To solve this, we used Python's built-in **Abstract Syntax Tree (AST)** module to identify logical blocks.

##### AST Traversal Architecture
*   **Recursive Walk:** The parser uses `os.walk` but dynamically filters out directory names matching `__pycache__`, `.venv`, and hidden folders (starting with `.`) by modifying the `subdirs` list in place. This avoids scanning unwanted files.
*   **AST Node Identification:**
    *   `ast.ClassDef`: Represents Class declarations (e.g. `class User:`).
    *   `ast.FunctionDef` / `ast.AsyncFunctionDef`: Represents Functions (e.g. `def hash_password():`) or class Methods if nested within a class.
*   **Exact Source Extraction:** Uses Python's native `ast.get_source_segment(source, node)` to retrieve the exact character slice from the file corresponding to the parsed block.
*   **Metadata Construction:** Saves starting and ending line numbers (`lineno` and `end_lineno`), name, type (`function`, `class`, `method`), and the enclosing class name (`parent_class`).

---

### 3. Integration Testing & Verification
The verification script **`offlinerag/test_week2.py`** was executed to scan `test_codebase/` and print extracted chunks.

**Test Outputs & Chunks Extracted:**
*   **Total searchable chunks extracted:** 15
*   **Functions extracted:** 9 (including `hash_password`, `register_user`, `verify_login`, `get_db_connection`, `initialize_database`, etc.)
*   **Classes extracted:** 2 (`User`, `Post`)
*   **Methods extracted:** 4 (`__init__` and `to_dict` inside `User` and `Post` classes)

##### Verified Log Snippet:
```text
============================================================
        OfflineRAG: Week 2 AST Parser Test Script
============================================================

Scanning directory: E:\OfflineRAG\offlinerag\test_codebase...

Total searchable chunks extracted: 15
------------------------------------------------------------

[1] Name: handle_home_route
    File:         app.py
    Type:         function
    Parent Class: None
    Lines:        4-9
    Docstring:    'Simulates loading the home page of the application.\nReturns a simple welcome text.'
    Code Preview:
        def handle_home_route() -> str:
            """
            Simulates loading the home page of the application.
        ...
----------------------------------------
...
[11] Name: __init__
    File:         models.py
    Type:         method
    Parent Class: User
    Lines:        8-11
    Docstring:    None
    Code Preview:
        def __init__(self, user_id: int, username: str, password_hash: str):
                self.user_id = user_id
                self.username = username
        ...
```

---

### 4. Self-Evaluation & Clean Code Practices
*   **Nesting Level Control:** The parser functions use quick returns (`if not file.endswith(".py"): continue`) to keep the loop nesting depth at a maximum of 2, preventing nested loop readability decay.
*   **Ast Segment Safety:** Checking for syntax errors with a clean try-except block around `ast.parse` prevents the program from crashing on corrupt files.

---

### 5. Plan for Next Week (Week 3)
*   Build the unified `engine.py` coordinating the RAG query execution.
*   Implement a semantic query pipeline: Embed user questions, perform Cosine Similarity search against our NumPy index, walk file imports, construct prompt payloads, and stream local responses.
