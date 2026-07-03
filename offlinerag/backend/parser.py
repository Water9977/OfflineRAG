# Abstract Syntax Tree (AST) Parser for Python codebases
import ast
import os
from typing import List, Dict, Optional

def should_skip_dir(directory_name: str) -> bool:
    """
    Checks if a directory should be excluded from codebase parsing.
    Filters out cache folders, virtual environments, and hidden git folders.
    """
    return (
        directory_name == "__pycache__"
        or directory_name == ".venv"
        or directory_name.startswith(".")
    )

def extract_node_data(
    node: ast.AST, 
    source_code: str, 
    relative_path: str, 
    file_path: str,
    node_type: str, 
    parent_class: Optional[str] = None
) -> Dict:
    """
    Constructs a dictionary containing the extracted source code and 
    metadata of a specific AST node (class, function, or method).
    """
    source_segment = ast.get_source_segment(source_code, node) or ""
    line_range = f"{node.lineno}-{node.end_lineno}" if hasattr(node, "lineno") else "unknown"
    docstring = ast.get_docstring(node)
    
    return {
        "content": source_segment,
        "metadata": {
            "filename": relative_path,
            "file_path": file_path,
            "name": getattr(node, "name", "unknown"),
            "type": node_type,
            "parent_class": parent_class,
            "lines": line_range,
            "docstring": docstring
        }
    }

def parse_file_nodes(source_code: str, relative_path: str, file_path: str) -> List[Dict]:
    """
    Parses a single Python file's source code using the AST module.
    Identifies top-level functions, classes, and class methods.
    """
    chunks = []
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        # Skip files that have syntax errors
        return chunks

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Global functions
            chunks.append(extract_node_data(node, source_code, relative_path, file_path, "function"))
            
        elif isinstance(node, ast.ClassDef):
            # Class definitions
            class_name = node.name
            chunks.append(extract_node_data(node, source_code, relative_path, file_path, "class"))
            
            # Extract methods inside this class
            for sub_node in node.body:
                if isinstance(sub_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    chunks.append(
                        extract_node_data(
                            sub_node, 
                            source_code, 
                            relative_path, 
                            file_path,
                            "method", 
                            parent_class=class_name
                        )
                    )
                    
    return chunks

def parse_directory(root_path: str) -> List[Dict]:
    """
    Recursively scans the provided directory for Python files.
    Parses each file and returns a list of all extracted functions, classes, and methods.
    """
    all_chunks = []
    # Convert path to absolute to avoid relative path inconsistencies
    abs_root_path = os.path.abspath(root_path)

    for current_dir, subdirs, files in os.walk(abs_root_path):
        # Exclude directories we do not want to scan in-place (updates the walk dynamically)
        subdirs[:] = [d for d in subdirs if not should_skip_dir(d)]
        
        for file in files:
            if not file.endswith(".py"):
                continue
                
            file_path = os.path.join(current_dir, file)
            relative_path = os.path.relpath(file_path, abs_root_path)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    source_code = f.read()
            except Exception:
                continue
                
            file_chunks = parse_file_nodes(source_code, relative_path, file_path)
            all_chunks.extend(file_chunks)
            
    return all_chunks
