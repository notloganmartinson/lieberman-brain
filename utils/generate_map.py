import os
import ast

def format_py_function(node, indent):
    """Helper to format a Python function signature."""
    args = [arg.arg for arg in node.args.args]
    return f"{'  ' * indent}def {node.name}({', '.join(args)}):"

def parse_py_file(filepath):
    """Parses a Python file and returns its AST skeleton."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        structure = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                structure.append(format_py_function(node, 0))
            elif isinstance(node, ast.ClassDef):
                structure.append(f"class {node.name}:")
                for subnode in node.body:
                    if isinstance(subnode, ast.FunctionDef):
                        structure.append(format_py_function(subnode, 1))
        return structure
    except Exception:
        return []

def generate_map(root_dir="."):
    """Walks the directory and builds the full-stack repo map."""
    repo_map = []
    for root, dirs, files in os.walk(root_dir):
        if any(x in root for x in ["venv", ".git", "__pycache__"]):
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.relpath(os.path.join(root, file), root_dir)
                repo_map.append(f"\n# {path}")
                repo_map.extend(parse_py_file(os.path.join(root, file)))
    
    with open("GEMINI.md", "w", encoding="utf-8") as f:
        f.write("# LIEBERMAN GRAPHRAG REPO MAP\n")
        f.write("```text\n")
        f.write("\n".join(repo_map))
        f.write("\n```")
    print("GEMINI.md updated with production-ready repo map.")

if __name__ == "__main__":
    generate_map()
