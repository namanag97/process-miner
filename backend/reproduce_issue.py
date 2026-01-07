
import requests
import time
import os

API_BASE = "http://localhost:8001"
PROJECT_ID = "mvp-org-001" # Assuming from seed data

# Create a dummy CSV file
csv_content = "case_id,activity,timestamp\n1,Start,2023-01-01T10:00:00Z\n1,End,2023-01-01T10:05:00Z"
filename = "test_log.csv"
with open(filename, "w") as f:
    f.write(csv_content)

try:
    print(f"Uploading {filename}...")
    files = {"file": (filename, open(filename, "rb"), "text/csv")}
    data = {"project_id": "mvp-ws-001"} # Using workspace ID as project ID for simpler direct mapping? 
    # Wait, check valid project ID from seed? 
    # Seed data creates Org and Workspace. Does it create a Project?
    # No. But upload.py requires project_id.
    # We might need to create a project first or use the workspace ID if the system conflates them (unlikely).
    # Let's try listing projects first.
    
    # 1. List Projects
    print("Listing projects...")
    resp = requests.get(f"{API_BASE}/api/v1/projects")
    if resp.status_code == 200:
        projects = resp.json().get("items", [])
        if projects:
            project_id = projects[0]["id"]
            print(f"Using existing project: {project_id}")
        else:
            # Create project
            print("Creating project...")
            resp = requests.post(f"{API_BASE}/api/v1/projects", json={
                "name": "RCA Test Project",
                "workspace_id": "mvp-ws-001"
            })
            if resp.status_code in (200, 201):
                project_id = resp.json()["id"]
                print(f"Created project: {project_id}")
            else:
                print(f"Failed to create project: {resp.text}")
                exit(1)
    else:
        print(f"Failed to list projects: {resp.text}")
        # Try to proceed with a dummy ID just in case?
        project_id = "test-project"

    # 2. Upload File
    data["project_id"] = project_id
    resp = requests.post(f"{API_BASE}/api/v1/datasets/", files=files, data=data)
    
    if resp.status_code != 200:
        print(f"Upload failed: {resp.status_code} {resp.text}")
        exit(1)
        
    dataset_id = resp.json()["id"]
    print(f"Upload success! Dataset ID: {dataset_id}")
    
    # 3. Get Sheets (Immediately)
    print("Fetching sheets...")
    start_time = time.time()
    try:
        resp = requests.get(f"{API_BASE}/api/v1/datasets/{dataset_id}/sheets")
        print(f"Sheets response: {resp.status_code}")
        print(resp.text)
    except requests.exceptions.ConnectionError:
        print(f"Connection Error! Server likely down/restarting. Took {time.time() - start_time:.2f}s")
    except Exception as e:
        print(f"Exception fetching sheets: {e}")

finally:
    if os.path.exists(filename):
        os.remove(filename)
