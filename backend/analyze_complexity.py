import ast
import os
import sys
from collections import defaultdict

def get_cyclomatic_complexity(node):
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.Assert, ast.ExceptHandler, ast.With, ast.AsyncWith, ast.AsyncFor)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity

def analyze_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        loc = len(content.splitlines())
        
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                cc = get_cyclomatic_complexity(node)
                functions.append({'name': node.name, 'cc': cc, 'lineno': node.lineno})
            elif isinstance(node, ast.ClassDef):
                # Class complexity is sum of method complexities + 1 (simplified)
                # Or just list it differently. Let's just track methods for now and maybe class avg.
                pass
                
        return {'loc': loc, 'functions': functions, 'error': None}
    except Exception as e:
        return {'loc': 0, 'functions': [], 'error': str(e)}

def main():
    root_dir = 'src'
    results = []
    
    for root, dirs, files in os.walk(root_dir):
        if 'test' in root: continue # Skip tests
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                analysis = analyze_file(path)
                if analysis['error']:
                    continue
                    
                for func in analysis['functions']:
                    results.append({
                        'file': path,
                        'type': 'function',
                        'name': func['name'],
                        'cc': func['cc'],
                        'loc': analysis['loc'] # File LOC
                    })

    # Sort by CC descending
    results.sort(key=lambda x: x['cc'], reverse=True)
    
    print(f"{'File':<60} | {'Name':<30} | {'CC':<5} | {'FileLOC':<5}")
    print("-" * 110)
    for r in results[:20]:
        print(f"{r['file']:<60} | {r['name']:<30} | {r['cc']:<5} | {r['loc']:<5}")

if __name__ == '__main__':
    main()
