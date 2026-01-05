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
            self.log_result(method, path, "FAIL", e.code, str(e))
            return None
        except urllib.error.URLError as e:
            self.log_result(method, path, "ERR", "-", str(e))
            return None

    def run_flow(self):
        print("\n[INFO] Starting E2E Business Logic Flow...")
        
        # 1. Register (Auth)
        print("\n--> Step 1: Registration")
        reg_data = {
            "email": f"tester_{int(time.time())}@example.com",
            "password": "Password123!",
            "full_name": "E2E Tester",
            "org_name": "Test Org"
        }
        resp = self.request("POST", "/api/v1/auth/register", reg_data)
        if resp and "access_token" in resp:
            self.token = resp["access_token"]
            self.headers["Authorization"] = f"Bearer {self.token}"
            print("    [Success] Authenticated via Register.")
        else:
            print("    [Fail] Registration failed. Trying Login fallback...")
            # Fallback to login
            login_data = {"email": "test@example.com", "password": "password"}
            resp = self.request("POST", "/api/v1/auth/login", login_data)
            if resp and "access_token" in resp:
                self.token = resp["access_token"]
                self.headers["Authorization"] = f"Bearer {self.token}"
                print("    [Success] Authenticated via Login.")
            else:
                print("    [CRITICAL] Authentication failed completely. Aborting flow.")
                return

        # 2. Get User Info
        print("\n--> Step 2: Verification")
        me = self.request("GET", "/api/v1/auth/me")
        if me and "organization" in me:
            self.state["org_id"] = me["organization"]["id"]
            print(f"    [State] org_id = {self.state['org_id']}")

        # 3. Create Workspace
        print("\n--> Step 3: Create Workspace")
        ws_data = {
            "name": f"Test WS {int(time.time())}",
            "description": "Created by E2E Tester"
        }
        # Assuming query param org_id based on swagger inspection earlier, or body?
        # Swagger said: POST /api/v1/workspaces?org_id=...
        # Wait, earlier view_file showed param org_id in query for POST.
        path = f"/api/v1/workspaces?org_id={self.state.get('org_id', 'default')}"
        resp = self.request("POST", path, ws_data)
        if resp and "id" in resp:
            self.state["workspace_id"] = resp["id"]
            print(f"    [State] workspace_id = {self.state['workspace_id']}")
        
        # 4. Create Project
        print("\n--> Step 4: Create Project")
        # Swagger: POST /api/v1/projects?workspace_id=...
        proj_data = {
            "name": "E2E Project",
            "description": "Test Project"
        }
        path = f"/api/v1/projects?workspace_id={self.state['workspace_id']}"
        resp = self.request("POST", path, proj_data)
        if resp and "id" in resp:
            self.state["project_id"] = resp["id"]
            print(f"    [State] project_id = {self.state['project_id']}")

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
