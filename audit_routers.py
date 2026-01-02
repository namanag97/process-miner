import os
import re

router_dir = "backend/src/api/routers"
output = []

for filename in os.listdir(router_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        filepath = os.path.join(router_dir, filename)
        with open(filepath, "r") as f:
            content = f.read()
            
            # Find all routes
            # Pattern for @router.METHOD("PATH", ...)
            # Followed by def FUNCTION_NAME(...)
            route_matches = re.finditer(r'@router\.(get|post|put|delete|patch|websocket)\("([^"]+)"', content)
            
            for match in route_matches:
                method = match.group(1).upper()
                path = match.group(2)
                
                # Find the function name after the decorator
                # Search for the next 'def ' after the current match position
                search_from = match.end()
                def_match = re.search(r'def\s+([a-zA-Z0-9_]+)\s*\(', content[search_from:])
                if def_match:
                    handler = def_match.group(1)
                else:
                    handler = "UNKNOWN"
                
                output.append({
                    "router": filename,
                    "path": path,
                    "method": method,
                    "handler": handler
                })

for entry in output:
    print(f"{entry['router']}|{entry['path']}|{entry['method']}|{entry['handler']}")
