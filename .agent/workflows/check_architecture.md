---
description: Detect architectural issues (circular imports, boundary violations, layering)
---
Analyze codebase for common architectural anti-patterns.

### 1. Check import boundaries (backend)
// turbo
```bash
cd backend && .venv/bin/python -m import_linter
```

### 2. Find circular imports
```bash
cd backend && .venv/bin/python -c "
import sys
from importlib import import_module
import pkgutil

def find_cycles():
    visited = set()
    path = []
    
    def dfs(module_name):
        if module_name in path:
            cycle_start = path.index(module_name)
            print(f'🔄 Circular import: {\" -> \".join(path[cycle_start:])} -> {module_name}')
            return
        if module_name in visited:
            return
        visited.add(module_name)
        path.append(module_name)
        # Check direct imports
        path.pop()
    
    print('Checking for circular imports...')
    # Run ruff for import issues
    import subprocess
    subprocess.run(['python', '-m', 'ruff', 'check', 'src/', '--select', 'I'])
"
```

### 3. Find god classes (files > 500 lines)
```bash
cd backend && find src -name "*.py" -exec wc -l {} + | awk '$1 > 500 {print "⚠️  Large file:", $2, "("$1" lines)"}' | sort -rn
```

### 4. Find deep nesting
```bash
cd frontend-new && find src -name "*.tsx" -path "*/*/\*/*/*/*" -type f | head -20
```

### 5. Check for feature coupling
Look for imports crossing feature boundaries:
```bash
cd backend && grep -rn "from src.features" src/features --include="*.py" | grep -v "__pycache__" | awk -F: '{print $1": "$3}' | grep -v "from src.features.\$(dirname $1 | xargs basename)"
```
