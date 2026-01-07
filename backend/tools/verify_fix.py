import time
import requests
import sys

API_URL = "http://localhost:8001"
WORKSPACE_ID = "mvp-ws-001"

def check_health():
    try:
        r = requests.get(f"{API_URL}/health/detailed")
        if r.status_code != 200:
            print(f"Health check failed: {r.status_code} {r.text}")
            return None
        return r.json()
    except Exception as e:
        print(f"Health check failed: {e}")
        return None

def main():
    print("Starting verification...")
    
    # Check if requests is available (redundant if import works)
    
    # 1. Initial Health
    health_start = check_health()
    if not health_start:
        print("Cannot verify, server not reachable.")
        sys.exit(1)
    
    # uptime_seconds key might vary, let's check keys
    # Assuming standard health check response
    # If not, we might need to rely on PID or start_time
    # common keys: status, uptime, version
    start_uptime = health_start.get("uptime_seconds", 0) 
    print(f"Initial uptime: {start_uptime}")

    # 2. Create Project
    print("Creating project...")
    project_id = None
    try:
        r = requests.post(f"{API_URL}/api/v1/projects", json={
            "name": "Verification Project",
            "workspace_id": WORKSPACE_ID,
            "description": "Temp project for verifying upload fix"
        })
        if r.status_code == 200:
            project_id = r.json()["id"]
        elif r.status_code == 409 or "already exists" in r.text.lower():
             # Try to find it?
             pass
        
        if not project_id:
            # List projects
            print(f"Create project status {r.status_code}. Listing projects...")
            r = requests.get(f"{API_URL}/api/v1/projects", params={"workspace_id": WORKSPACE_ID})
            if r.status_code == 200:
                items = r.json().get("items", [])
                if items:
                    project_id = items[0]["id"]
            
            if not project_id:
                print("Could not create or find a project.")
                sys.exit(1)

    except Exception as e:
        print(f"Project op failed: {e}")
        sys.exit(1)

    print(f"Using Project ID: {project_id}")

    # 3. Upload File
    print("Uploading file...")
    try:
        # Create dummy CSV content
        files = {'file': ('test_verify.csv', 'case_id,activity,timestamp\n1,Start,2023-01-01T10:00:00Z', 'text/csv')}
        data = {'project_id': project_id}
        r = requests.post(f"{API_URL}/api/v1/datasets/", files=files, data=data)
        if r.status_code != 200:
            print(f"Upload failed: {r.text}")
            sys.exit(1)
        print("Upload success.")
    except Exception as e:
        print(f"Upload op failed: {e}")
        sys.exit(1)

    # 4. Wait and Check Health
    print("Waiting 3 seconds...")
    time.sleep(3)
    
    health_end = check_health()
    if not health_end:
        print("Server unreachable after upload (Restarting?).")
        sys.exit(1)
        
    end_uptime = health_end.get("uptime_seconds", 0)
    print(f"Final uptime: {end_uptime}")
    
    # If uptime reset (smaller than start + wait), restart happened
    # Allow some jitter, but usually uptime is monotonic
    if end_uptime >= start_uptime + 3:
        print("SUCCESS: Uptime increased correctly (NO restart detected).")
    else:
        print(f"FAILURE: Uptime reset detected! ({start_uptime} -> {end_uptime})")
        sys.exit(1)

if __name__ == "__main__":
    main()
