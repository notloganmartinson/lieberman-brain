import ast
import os
import re

# Ignore directories for both Python backend and React frontend
IGNORE_DIRS = {'.git', '__pycache__', 'venv', 'venv-win', '.venv', '.pytest_cache', 'node_modules', 'dist', 'dist-ssr', 'frontend/node_modules'}

def format_py_function(node, indent=0):
    """Helper to format a Python function signature, return type, and brief docstring."""
    args = [arg.arg for arg in node.args.args]
    arg_str = ", ".join(args)
    
    # Safely extract return type if present (requires Python 3.9+)
    ret = ""
    if getattr(node, 'returns', None):
        try:
            ret = f" -> {ast.unparse(node.returns)}"
        except AttributeError:
            pass 

    # Extract just the first line of the docstring to save tokens
    doc = ast.get_docstring(node)
    doc_str = f" # {doc.splitlines()[0].strip()}" if doc else ""
    
    ind = " " * indent
    return f"{ind}def {node.name}({arg_str}){ret}:{doc_str}"

def parse_py_file(filepath):
    """Parses a Python file and returns its AST skeleton."""
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return []

    skeleton = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            doc_str = f" # {doc.splitlines()[0].strip()}" if doc else ""
            skeleton.append(f"class {node.name}:{doc_str}")
            
            for sub_node in node.body:
                if isinstance(sub_node, ast.FunctionDef):
                    skeleton.append(format_py_function(sub_node, indent=4))
                    
        elif isinstance(node, ast.FunctionDef):
            skeleton.append(format_py_function(node, indent=0))
            
    return skeleton

def parse_js_file(filepath):
    """Parses a JS/JSX file using regex to extract exported functions and components."""
    skeleton = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to catch standard functions and arrow functions (React components/API calls)
        func_pattern = re.compile(r'(?:export\s+)?(?:default\s+)?(?:function\s+([A-Za-z0-9_]+)\s*\(|const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z0-9_]+)\s*=>)')
        
        matches = func_pattern.findall(content)
        for m in matches:
            name = m[0] or m[1]
            if name:
                skeleton.append(f"function {name}(...)")
    except Exception:
        pass
        
    return skeleton

def generate_map(root_dir):
    """Walks the directory and builds the full-stack repo map."""
    repo_map = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filter out ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_dir).replace("\\", "/")
            
            skeleton = []
            if filename.endswith(".py"):
                skeleton = parse_py_file(filepath)
            # Parse React frontend files, ignoring config files to save tokens
            elif filename.endswith((".js", ".jsx")) and not filename.endswith(".config.js"):
                skeleton = parse_js_file(filepath)
                
            if skeleton:
                repo_map.append(f"\n# {rel_path}")
                repo_map.extend(skeleton)
                    
    return "\n".join(repo_map)

if __name__ == "__main__":
    # Assumes this script is placed in the project root directory.
    project_root = os.path.dirname(os.path.abspath(__file__))
    ast_map = generate_map(root_dir=project_root)
    
    # Custom preamble tailored to the Lieberman GraphRAG Architecture
    preamble = """# LIEBERMAN GRAPHRAG (BETTER-PERPLEXITY) REPO MAP
SYSTEM INSTRUCTIONS:
1. LOGIC OMITTED: Functions are NOT empty. Implementations are abstracted for context efficiency.
2. READ/WRITE PROTOCOL: To modify a function or component, you MUST ask the user to provide the specific file path first. Do NOT hallucinate modifications without the source file.
3. ARCHITECTURAL GROUNDING: This is a full-stack "Better-Perplexity" Content Consigliere. 
   - Backend: Python 3.12+, FastAPI, Neo4j AuraDB (Graph/Vector Hybrid Retrieval), Google Gemini API.
   - Frontend: React 18 + Vite, Tailwind CSS.
   - Core Pipeline: Live Web Search -> Neo4j Graph Traversal -> Gemini Synthesis -> React UI with Citations.
4. SCOPE BOUNDARIES: This project prioritizes GraphRAG architecture and web search integration over enterprise authentication. Keep the stack lean. Avoid over-engineering security beyond environment variables and parameterized Cypher queries.
5. PRECISION: Use exact class, function, component, and file names from this map.

---

"""
    
    output_path = os.path.join(project_root, "GEMINI.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(preamble)
        f.write("```text\n")
        f.write(ast_map)
        f.write("\n```\n")
        
    print(f"Successfully generated token-optimized Full-Stack map at: {output_path}")
