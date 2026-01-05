
import sys
import os
import inspect

# Add current directory to sys.path
sys.path.append(os.getcwd())

try:
    from src.api.main import app
    from fastapi.routing import APIRoute

    print(f"{'METHOD':<10} {'PATH':<50} {'SUMMARY':<10} {'DESC':<10} {'TAGS'}")
    print("-" * 100)
    
    routes = sorted(app.routes, key=lambda x: x.path)
    
    missing_docs = []
    total_endpoints = 0
    
    for route in routes:
        if isinstance(route, APIRoute):
            total_endpoints += 1
            methods = ", ".join(sorted(route.methods))
            
            has_summary = bool(route.summary)
            has_description = bool(route.description)
            tags = ", ".join(route.tags) if route.tags else "MISSING"
            
            # Check if docstring is used as description
            if not has_description and route.endpoint.__doc__:
                has_description = True
            
            status_summary = "OK" if has_summary else "MISSING"
            status_desc = "OK" if has_description else "MISSING"
            
            if not has_summary or not has_description or not route.tags:
                missing_docs.append({
                    "method": methods,
                    "path": route.path,
                    "summary": status_summary,
                    "desc": status_desc,
                    "tags": tags
                })
                
            # Truncate path for display
            display_path = (route.path[:47] + '...') if len(route.path) > 50 else route.path
            print(f"{methods:<10} {display_path:<50} {status_summary:<10} {status_desc:<10} {tags}")

    print("\n" + "="*100)
    print(f"Total Endpoints: {total_endpoints}")
    print(f"Endpoints with missing docs: {len(missing_docs)}")
    
    if missing_docs:
        print("\nMissing Documentation Details:")
        print(f"{'METHOD':<10} {'PATH':<50} {'SUMMARY':<10} {'DESC':<10} {'TAGS'}")
        print("-" * 100)
        for doc in missing_docs:
             display_path = (doc['path'][:47] + '...') if len(doc['path']) > 50 else doc['path']
             print(f"{doc['method']:<10} {display_path:<50} {doc['summary']:<10} {doc['desc']:<10} {doc['tags']}")

except ImportError as e:
    print(f"Error importing app: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
