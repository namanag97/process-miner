import json
import urllib.request
import urllib.error
import sys
import time
import random

# Configuration
BASE_URL = "http://localhost:8001"
OPENAPI_PATH = "docs/openapi.json"
REPORT_FILE = "test/test_summary.txt"
FULL_REPORT_FILE = "test/full_report.txt"

class E2ETester:
    def __init__(self):
        self.base_url = BASE_URL
        self.spec = self.load_spec()
        self.token = None
        self.headers = {'Content-Type': 'application/json'}
        self.state = {
            "workspace_id": "00000000-0000-0000-0000-000000000000", # Fallback
            "project_id": "00000000-0000-0000-0000-000000000000"
        }
        self.results = []

    def load_spec(self):
        try:
            with open(OPENAPI_PATH, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {OPENAPI_PATH}: {e}")
            sys.exit(1)

    def log_result(self, method, path, status, code, msg=""):
        print(f"[{status}] {method} {path} ({code}) {msg}")
        self.results.append({
            "method": method,
            "path": path,
            "status": status,
            "code": code,
            "msg": msg
        })

    def request(self, method, path, data=None, expect=200):
        url = self.base_url + path
        # Substitute state variables
        for key, val in self.state.items():
            url = url.replace(f"{{{key}}}", str(val))
        
        # FORCE CRAWL: Substitute defined standard params with dummies if unresolved
        if "{" in url:
            standard_placeholders = {
                "{organization_id}": "11111111-1111-1111-1111-111111111111",
                "{workspace_id}": "22222222-2222-2222-2222-222222222222",
                "{project_id}": "33333333-3333-3333-3333-333333333333",
                "{dataset_id}": "44444444-4444-4444-4444-444444444444",
                "{job_id}": "55555555-5555-5555-5555-555555555555",
                "{resource}": "dummy-resource",
                "{predictor_id}": "66666666-6666-6666-6666-666666666666",
                "{case_id}": "dummy-case-001",
                "{user_id}": "77777777-7777-7777-7777-777777777777"
            }
            for ph, val in standard_placeholders.items():
                if ph in url:
                     url = url.replace(ph, val)

        if "{" in url:
            self.log_result(method, path, "SKIPPED", "-", "Unresolved parameters")
            return None

        body = None
        if data:
            body = json.dumps(data).encode('utf-8')

        req = urllib.request.Request(url, headers=self.headers, method=method, data=body)
        
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                resp_body = None
                try:
                    content = response.read().decode()
                    if content:
                        resp_body = json.loads(content)
                except:
                    pass
                
                status_cat = "PASS" if (200 <= response.status < 300) else "FAIL"
                # If we expected something else (like 4xx for negative test), handle here
                # For now we assume success is 2xx
                
                self.log_result(method, path, status_cat, response.status)
                return resp_body
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            print(f"    [Error Body] {err_body}")
            self.log_result(method, path, "FAIL", e.code, str(e))
            return None
        except urllib.error.URLError as e:
            self.log_result(method, path, "ERR", "-", str(e))
            return None

    def run_flow(self):
        print("\n[INFO] Starting E2E Flow (Attempting Registration)...")
        
        # 1. Register (Corrected Schema)
        print("\n--> Step 1: Registration")
        reg_data = {
            "email": f"tester_{int(time.time())}@example.com",
            "password": "Password123!",
            "name": "E2E Tester",               # Fixed: was full_name
            "organization_name": "Test Org"     # Fixed: was org_name
        }
        resp = self.request("POST", "/api/v1/auth/register", reg_data)
        
        if resp and "access_token" in resp:
            self.token = resp["access_token"]
            self.headers["Authorization"] = f"Bearer {self.token}"
            print("    [Success] Authenticated via Register.")
            
            # Capture Org ID from response if available (structure: user -> org_id)
            if "user" in resp and "id" in resp["user"]:
                 # Usually org_id is on the user object? Swagger says user response has it? 
                 # Checking previous view_file of auth/api.py: UserResponse has id, email... not direct org_id?
                 # Wait, _user_to_response in auth/api.py: UserResponse(id, email, name, role...)
                 # Let's rely on /me for state setting just to be safe.
                 pass
        else:
             print("    [Fail] Registration failed. Fallback to MVP ID Check...")

        # 2. Verify Identity (Token or Implict)
        
        # 1. Verify Implicit Auth (Dev Mode)
        print("\n--> Step 1: Verify Identity (Dev Mode)")
        me = self.request("GET", "/api/v1/auth/me")
        if me:
            print(f"    [Debug] /auth/me payload: {json.dumps(me)}")
            user_data = me.get('user', {})
            print(f"    [Success] Identified as: {user_data.get('email', 'Unknown')}")
            if "organization" in me and me["organization"]:
                self.state["org_id"] = me["organization"]["id"]
                print(f"    [State] org_id = {self.state['org_id']}")
        else:
            print("    [WARN] Could not get user info. Proceeding with hardcoded MVP IDs.")
            self.state["org_id"] = "11111111-1111-1111-1111-111111111111"

        # 2. Set MVP Workspace
        print("\n--> Step 2: Set MVP Workspace")
        # Hardcode the known seeded workspace
        self.state["workspace_id"] = "22222222-2222-2222-2222-222222222222"
        print(f"    [State] workspace_id = {self.state['workspace_id']}")
        
        # Verify it exists
        ws = self.request("GET", f"/api/v1/workspaces/{self.state['workspace_id']}")
        if ws:
             print("    [Success] MVP Workspace verified.")
        else:
             print("    [Fail] MVP Workspace not found. Creating fallback...")
             ws_data = {"name": "Fallback WS", "description": "Auto-created"}
             resp = self.request("POST", f"/api/v1/workspaces?org_id={self.state['org_id']}", ws_data)
             if resp and "id" in resp:
                 self.state["workspace_id"] = resp["id"]

        # 3. Get/Create Project
        print("\n--> Step 3: Get/Create Project")
        # Try to list projects in this workspace to find one
        projects = self.request("GET", f"/api/v1/workspaces/{self.state['workspace_id']}/projects")
        
        # Inspect structure of projects response - swagger says WorkspaceDetailResponse contains projects list?
        # Or /workspaces/{id} returns detail with projects.
        # Let's check the result of the workspace call above if it had projects.
        if ws and "projects" in ws and len(ws["projects"]) > 0:
             self.state["project_id"] = ws["projects"][0]["id"]
             print(f"    [State] Found existing project_id = {self.state['project_id']}")
        else:
             print("    [Info] No projects found. Creating new one.")
             proj_data = {"name": "MVP Project", "description": "Seeded for test"}
             resp = self.request("POST", f"/api/v1/projects?workspace_id={self.state['workspace_id']}", proj_data)
             if resp and "id" in resp:
                 self.state["project_id"] = resp["id"]
                 print(f"    [State] Created project_id = {self.state['project_id']}")
             else:
                 # Fallback for crawl
                 self.state["project_id"] = "33333333-3333-3333-3333-333333333333"

        # 4. Upload Dataset
        print("\n--> Step 4: Upload Dataset")
        # Need to construct multipart form-data. 
        # Since we are using standard lib, this is verbose. We will verify if /api/v1/datasets/upload endpoint exists and structure.
        # Swagger Check: POST /api/v1/datasets/upload (consumes multipart/form-data)
        # Params: project_id (query), file (form)
        
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        with open("test/dummy_log.csv", "rb") as f:
            file_content = f.read()
            
        # Construct body
        body_parts = []
        
        # Add project_id field
        body_parts.append(f'--{boundary}')
        body_parts.append('Content-Disposition: form-data; name="project_id"')
        body_parts.append('')
        body_parts.append(str(self.state['project_id']))
        
        # Add file field
        body_parts.append(f'--{boundary}')
        body_parts.append('Content-Disposition: form-data; name="file"; filename="dummy_log.csv"')
        body_parts.append('Content-Type: text/csv')
        body_parts.append('')
        body_parts.append(file_content.decode('utf-8'))
        
        body_parts.append(f'--{boundary}--')
        body_parts.append('')
        
        body_str = '\r\n'.join(body_parts)
        body_bytes = body_str.encode('utf-8')
        
        headers = self.headers.copy()
        headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
        
        # URL: /api/v1/datasets/ (Needs trailing slash for direct upload mapping)
        url = self.base_url + "/api/v1/datasets/"
        
        try:
            req = urllib.request.Request(url, headers=headers, method="POST", data=body_bytes)
            with urllib.request.urlopen(req, timeout=10) as response:
                 if 200 <= response.status < 300:
                     resp_json = json.loads(response.read().decode())
                     self.state["dataset_id"] = resp_json.get("id")
                     print(f"    [Success] Uploaded dataset. dataset_id = {self.state['dataset_id']}")
                     self.log_result("POST", url.replace(self.base_url, ""), "PASS", response.status)
                 else:
                     print(f"    [Fail] Upload failed: {response.status}")
                     self.log_result("POST", url.replace(self.base_url, ""), "FAIL", response.status, "Upload Failed")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            print(f"    [Fail] Upload HTTP Error: {e.code} - {err_body}")
            self.log_result("POST", url.replace(self.base_url, ""), "FAIL", e.code, f"{e} - {err_body}")
        except Exception as e:
            print(f"    [Fail] Upload exception: {e}")
            self.log_result("POST", url.replace(self.base_url, ""), "FAIL", 500, str(e))


    def crawl(self):
        print("\n[INFO] Starting Coverage Crawl (Remaining Endpoints)...")
        paths = self.spec.get("paths", {})
        
        # Shuffle to avoid order bias, but here simple iteration is fine
        for path, props in paths.items():
            for method in props.keys():
                if method not in ['get']: continue # Just GETs for safety during crawl
                
                # Check if we already tested this in flow (naive check)
                already_tested = any(r['path'] == path and r['method'].lower() == method for r in self.results)
                if already_tested:
                    continue
                    
                self.request(method.upper(), path)

    def generate_report(self):
        total = len(self.results)
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        skipped = len([r for r in self.results if r["status"] == "SKIPPED"])
        
        failures = [r for r in self.results if r["status"] in ["FAIL", "ERR"]]
        
        with open(FULL_REPORT_FILE, "w") as f:
            f.write("E2E API TEST REPORT\n")
            f.write("===================\n")
            f.write(f"Flow State: {json.dumps(self.state, indent=2)}\n\n")
            for r in self.results:
                f.write(f"[{r['status']}] {r['method']} {r['path']} ({r['code']}) {r['msg']}\n")
        
        summary = f"E2E Summary: {passed}/{total} Passed. {failed} Failures."
        if failures:
            summary += " Issues: " + ", ".join([f"{r['method']} {r['path']}" for r in failures[:3]])
            
        print("\n" + summary)
        with open(REPORT_FILE, "w") as f:
            f.write(summary)

if __name__ == "__main__":
    tester = E2ETester()
    tester.run_flow()
    tester.crawl()
    tester.generate_report()
