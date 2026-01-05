
import sys
import os

# Add current directory to sys.path to allow importing src
sys.path.append(os.getcwd())

try:
    from src.api.main import app
    from fastapi.routing import APIRoute

    print(f"{'METHOD':<10} {'PATH'}")
    print("-" * 50)
    
    # Sort routes by path
    routes = sorted(app.routes, key=lambda x: x.path)
    
    for route in routes:
        if isinstance(route, APIRoute):
            methods = ", ".join(sorted(route.methods))
            print(f"{methods:<10} {route.path}")
except ImportError as e:
    print(f"Error importing app: {e}")
    # Print sys.path for debugging
    print("sys.path:", sys.path)
except Exception as e:
    print(f"An error occurred: {e}")

