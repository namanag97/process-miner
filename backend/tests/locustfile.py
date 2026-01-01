"""Load testing scenarios with Locust.

Tests API performance under load with realistic user scenarios:
- Browsing processes and projects
- Uploading event logs
- Running process discovery
- Viewing analytics

Usage:
    # Install locust: pip install locust
    # Run: locust -f tests/locustfile.py --host=http://localhost:8001
    # Open http://localhost:8089 for web UI
"""

import json
import random
from locust import HttpUser, task, between, tag


class ProcessMiningUser(HttpUser):
    """Simulates a typical process mining user."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Initialize user state."""
        self.project_ids = []
        self.process_ids = []
        self.model_ids = []
    
    # =========================================================================
    # Health & Discovery Tasks (Light)
    # =========================================================================
    
    @task(5)
    @tag("light", "health")
    def health_check(self):
        """Check API health."""
        self.client.get("/health")
    
    @task(3)
    @tag("light", "discovery")
    def list_miners(self):
        """List available process miners."""
        self.client.get("/api/v1/discovery/miners")
    
    # =========================================================================
    # Project Tasks
    # =========================================================================
    
    @task(4)
    @tag("projects", "read")
    def list_projects(self):
        """List all projects."""
        response = self.client.get("/api/v1/projects")
        if response.status_code == 200:
            projects = response.json()
            self.project_ids = [p["id"] for p in projects]
    
    @task(2)
    @tag("projects", "write")
    def create_project(self):
        """Create a new project."""
        response = self.client.post(
            "/api/v1/projects",
            json={
                "name": f"Load Test Project {random.randint(1, 10000)}",
                "description": "Created during load testing",
            },
        )
        if response.status_code == 201:
            project = response.json()
            self.project_ids.append(project["id"])
    
    @task(3)
    @tag("projects", "read")
    def get_project(self):
        """Get project details."""
        if self.project_ids:
            project_id = random.choice(self.project_ids)
            self.client.get(f"/api/v1/projects/{project_id}")
    
    # =========================================================================
    # Process Tasks
    # =========================================================================
    
    @task(5)
    @tag("processes", "read")
    def list_processes(self):
        """List all processes/event logs."""
        response = self.client.get("/api/v1/processes/")
        if response.status_code == 200:
            processes = response.json()
            self.process_ids = [p["id"] for p in processes]
    
    @task(4)
    @tag("processes", "read")
    def get_process(self):
        """Get process details."""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.get(f"/api/v1/processes/{process_id}")
    
    @task(3)
    @tag("processes", "read")
    def get_process_statistics(self):
        """Get process statistics."""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.get(f"/api/v1/processes/{process_id}/statistics")
    
    # =========================================================================
    # Analytics Tasks
    # =========================================================================
    
    @task(3)
    @tag("analytics", "read")
    def get_variants(self):
        """Get process variants."""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.get(f"/api/v1/analytics/{process_id}/variants")
    
    @task(2)
    @tag("analytics", "read")
    def get_dfg(self):
        """Get directly-follows graph."""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.get(f"/api/v1/analytics/{process_id}/dfg")
    
    @task(2)
    @tag("analytics", "read")
    def get_activity_statistics(self):
        """Get activity statistics."""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.get(f"/api/v1/analytics/{process_id}/statistics/activities")
    
    # =========================================================================
    # Discovery Tasks (Heavy)
    # =========================================================================
    
    @task(1)
    @tag("discovery", "write", "heavy")
    def discover_model(self):
        """Discover a process model."""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            miner_type = random.choice(["alpha", "inductive", "heuristics"])
            
            response = self.client.post(
                f"/api/v1/discovery/{process_id}/discover",
                json={"miner_type": miner_type},
            )
            
            if response.status_code == 200:
                result = response.json()
                if "model_id" in result:
                    self.model_ids.append(result["model_id"])


class AnalystUser(HttpUser):
    """Simulates an analyst user focused on analytics."""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Get available processes."""
        response = self.client.get("/api/v1/processes/")
        if response.status_code == 200:
            self.process_ids = [p["id"] for p in response.json()]
        else:
            self.process_ids = []
    
    @task(5)
    @tag("analytics")
    def browse_variants(self):
        """Browse process variants."""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.get(f"/api/v1/analytics/{process_id}/variants")
    
    @task(4)
    @tag("analytics")
    def view_dfg(self):
        """View DFG."""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.get(f"/api/v1/analytics/{process_id}/dfg")
    
    @task(3)
    @tag("analytics")
    def check_statistics(self):
        """Check process statistics."""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.get(f"/api/v1/processes/{process_id}/statistics")
    
    @task(2)
    @tag("conformance")
    def run_conformance(self):
        """Run conformance checking."""
        if self.process_ids:
            process_id = random.choice(self.process_ids)
            self.client.post(
                f"/api/v1/conformance/{process_id}/token-replay",
                json={},
            )


class ReadOnlyUser(HttpUser):
    """Simulates a read-only dashboard user."""
    
    wait_time = between(1, 2)
    
    @task(10)
    @tag("light")
    def health(self):
        self.client.get("/health")
    
    @task(5)
    @tag("light")
    def list_processes(self):
        self.client.get("/api/v1/processes/")
    
    @task(3)
    @tag("light")
    def list_projects(self):
        self.client.get("/api/v1/projects")


# =============================================================================
# Custom Load Shapes
# =============================================================================

class StepLoadShape:
    """Custom load shape that increases users in steps.
    
    Usage: Inherit from both this and LoadTestShape
    """
    
    step_time = 60  # seconds per step
    step_users = 10  # users per step
    max_users = 100
    
    def tick(self):
        run_time = self.get_run_time()
        
        if run_time > self.step_time * (self.max_users / self.step_users):
            return None  # Stop the test
        
        current_step = run_time // self.step_time
        current_users = min((current_step + 1) * self.step_users, self.max_users)
        
        return (int(current_users), self.step_users)
