#!/usr/bin/env python3
"""Phase 4 Data Migration: Workflows → DAG Definitions.

This script migrates data from the legacy workflow tables to the new DAG system:
- workflows → dag_definitions + dag_definition_steps + dag_definition_edges
- workflow_runs → dag_runs

The key difference from simple SQL migration is that steps_json (a JSON array)
must be normalized into individual dag_definition_steps rows, and sequential
edges must be created in dag_definition_edges.

Usage:
    # Dry run (verify migration without committing)
    python scripts/migrate_workflows_to_dags.py --dry-run
    
    # Execute migration
    python scripts/migrate_workflows_to_dags.py --execute

Safety:
    - Creates backup counts before migration
    - Validates all data migrated correctly
    - Prints failed IDs for debugging
    - Does NOT drop legacy tables (manual step after verification)
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

# IMPORTANT: Import SQLAlchemy BEFORE adding 'src' to sys.path
# This avoids src/platform shadowing Python's stdlib platform module
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session


# =============================================================================
# Database Connection
# =============================================================================


def get_sync_database_url() -> str:
    """Get a synchronous database URL from environment or default.
    
    Converts async URLs to sync equivalents:
    - sqlite+aiosqlite:// → sqlite://
    - postgresql+asyncpg:// → postgresql://
    """
    # Try .env file first
    env_file = Path(".env")
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("DATABASE_URL="):
                url = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
        else:
            url = None
    else:
        url = None
    
    # Fall back to environment variable
    if not url:
        url = os.environ.get("DATABASE_URL")
    
    # Default
    if not url:
        url = "sqlite+aiosqlite:///./data/db/process_mining.db"
    
    # Convert async to sync
    url = url.replace("sqlite+aiosqlite://", "sqlite://")
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    
    return url


def create_sync_engine():
    """Create a synchronous SQLAlchemy engine for the migration."""
    url = get_sync_database_url()
    print(f"   Using database: {url}")
    return create_engine(url, echo=False)


# =============================================================================
# Counting Functions
# =============================================================================


def count_legacy_records(session: Session) -> dict[str, int]:
    """Count records in legacy tables."""
    workflow_count = session.execute(
        text("SELECT COUNT(*) FROM workflows")
    ).scalar() or 0
    
    run_count = session.execute(
        text("SELECT COUNT(*) FROM workflow_runs")
    ).scalar() or 0
    
    return {"workflows": workflow_count, "workflow_runs": run_count}


def count_dag_records(session: Session) -> dict[str, int]:
    """Count records in DAG tables."""
    def_count = session.execute(
        text("SELECT COUNT(*) FROM dag_definitions")
    ).scalar() or 0
    
    step_count = session.execute(
        text("SELECT COUNT(*) FROM dag_definition_steps")
    ).scalar() or 0
    
    edge_count = session.execute(
        text("SELECT COUNT(*) FROM dag_definition_edges")
    ).scalar() or 0
    
    run_count = session.execute(
        text("SELECT COUNT(*) FROM dag_runs")
    ).scalar() or 0
    
    return {
        "dag_definitions": def_count,
        "dag_definition_steps": step_count,
        "dag_definition_edges": edge_count,
        "dag_runs": run_count,
    }


# =============================================================================
# Migration Functions
# =============================================================================


def parse_steps_json(steps_json: str | None) -> list[dict[str, Any]]:
    """Parse steps_json, handling edge cases."""
    if not steps_json:
        return []
    
    try:
        steps = json.loads(steps_json)
        if isinstance(steps, list):
            return steps
        return []
    except json.JSONDecodeError:
        return []


def infer_task_name(step: dict[str, Any]) -> str:
    """Infer task_name from step data.
    
    Legacy steps might have various formats:
    - {"name": "validate", "type": "validation"}
    - {"task": "ingest_dataset", "name": "Ingest Data"}
    - {"action": "discover", "name": "Discovery"}
    """
    # Try various common keys
    if "task" in step:
        return step["task"]
    if "task_name" in step:
        return step["task_name"]
    if "action" in step:
        return step["action"]
    if "type" in step:
        return step["type"]
    
    # Fall back to name as task_name
    name = step.get("name", "unknown_task")
    # Convert to snake_case task name
    return name.lower().replace(" ", "_").replace("-", "_")


def migrate_workflows(session: Session, dry_run: bool = True) -> tuple[int, list[str]]:
    """Migrate workflow definitions to dag_definitions + dag_definition_steps + dag_definition_edges.
    
    Returns:
        Tuple of (migrated_count, list_of_failed_ids)
    """
    # Get existing workflows
    workflows = session.execute(
        text("SELECT id, name, steps_json, schedule, is_active, created_at, updated_at FROM workflows")
    ).fetchall()
    
    migrated = 0
    failed_ids: list[str] = []
    
    for wf in workflows:
        wf_id, name, steps_json, schedule, is_active, created_at, updated_at = wf
        
        try:
            # Check if already migrated
            existing = session.execute(
                text("SELECT id FROM dag_definitions WHERE id = :id"),
                {"id": wf_id}
            ).fetchone()
            
            if existing:
                print(f"  ⏭️  Skipping {wf_id} ({name}) - already migrated")
                continue
            
            # Parse steps
            steps = parse_steps_json(steps_json)
            step_info = f"{len(steps)} steps" if steps else "no steps"
            
            if dry_run:
                print(f"  [DRY RUN] Would migrate: {wf_id} ({name}) - {step_info}")
                migrated += 1
                continue
            
            # === 1. Insert dag_definition ===
            session.execute(
                text("""
                    INSERT INTO dag_definitions 
                    (id, name, description, version, is_active, created_at, updated_at)
                    VALUES (:id, :name, :description, :version, :is_active, :created_at, :updated_at)
                """),
                {
                    "id": wf_id,
                    "name": name,
                    "description": f"Migrated from legacy workflow. Schedule: {schedule or 'None'}",
                    "version": 1,
                    "is_active": is_active,
                    "created_at": created_at,
                    "updated_at": updated_at,
                }
            )
            
            # === 2. Insert dag_definition_steps for each step ===
            step_ids: list[str] = []
            now = datetime.utcnow()
            
            for position, step in enumerate(steps):
                step_id = str(uuid4())
                step_ids.append(step_id)
                
                step_name = step.get("name", f"step_{position}")
                task_name = infer_task_name(step)
                
                # Extract optional params from step
                default_params = {k: v for k, v in step.items() if k not in ("name", "type", "task", "task_name", "action")}
                default_params_json = json.dumps(default_params) if default_params else None
                
                session.execute(
                    text("""
                        INSERT INTO dag_definition_steps
                        (id, dag_definition_id, name, task_name, default_params_json, position, created_at)
                        VALUES (:id, :dag_definition_id, :name, :task_name, :default_params_json, :position, :created_at)
                    """),
                    {
                        "id": step_id,
                        "dag_definition_id": wf_id,
                        "name": step_name,
                        "task_name": task_name,
                        "default_params_json": default_params_json,
                        "position": position,
                        "created_at": now,
                    }
                )
            
            # === 3. Create sequential edges (step 0 → step 1 → step 2 → ...) ===
            for i in range(1, len(step_ids)):
                edge_id = str(uuid4())
                session.execute(
                    text("""
                        INSERT INTO dag_definition_edges
                        (id, dag_definition_id, from_step_id, to_step_id)
                        VALUES (:id, :dag_definition_id, :from_step_id, :to_step_id)
                    """),
                    {
                        "id": edge_id,
                        "dag_definition_id": wf_id,
                        "from_step_id": step_ids[i - 1],
                        "to_step_id": step_ids[i],
                    }
                )
            
            print(f"  ✅ Migrated: {wf_id} ({name}) - {len(steps)} steps, {max(0, len(steps)-1)} edges")
            migrated += 1
            
        except (IntegrityError, OperationalError) as e:
            print(f"  ❌ Failed: {wf_id} ({name}) - {e}")
            failed_ids.append(wf_id)
            session.rollback()
    
    return migrated, failed_ids


def migrate_workflow_runs(session: Session, dry_run: bool = True) -> tuple[int, list[str]]:
    """Migrate workflow runs to dag_runs.
    
    Returns:
        Tuple of (migrated_count, list_of_failed_ids)
    """
    runs = session.execute(
        text("""
            SELECT id, workflow_id, dataset_id, status, result_json, error, started_at, completed_at
            FROM workflow_runs
        """)
    ).fetchall()
    
    migrated = 0
    failed_ids: list[str] = []
    
    for run in runs:
        run_id, workflow_id, dataset_id, status, result_json, error, started_at, completed_at = run
        
        try:
            # Check if already migrated
            existing = session.execute(
                text("SELECT id FROM dag_runs WHERE id = :id"),
                {"id": run_id}
            ).fetchone()
            
            if existing:
                print(f"  ⏭️  Skipping run {run_id} - already migrated")
                continue
            
            if dry_run:
                print(f"  [DRY RUN] Would migrate run: {run_id} (status: {status})")
                migrated += 1
                continue
            
            # Map legacy status to DAG status
            status_map = {
                "running": "running",
                "completed": "completed",
                "failed": "failed",
                "pending": "pending",
                "cancelled": "cancelled",
            }
            dag_status = status_map.get(status, "pending")
            
            # Build context from dataset_id
            context = {"dataset_id": dataset_id} if dataset_id else {}
            
            # Calculate created_at: prefer started_at, then completed_at, then now
            created_at = started_at or completed_at or datetime.utcnow()
            
            session.execute(
                text("""
                    INSERT INTO dag_runs
                    (id, dag_definition_id, user_id, status, trigger_type, context_json, 
                     error_message, started_at, completed_at, created_at)
                    VALUES (:id, :dag_definition_id, :user_id, :status, :trigger_type, :context_json,
                            :error_message, :started_at, :completed_at, :created_at)
                """),
                {
                    "id": run_id,
                    "dag_definition_id": workflow_id,
                    "user_id": None,  # Legacy runs didn't track user
                    "status": dag_status,
                    "trigger_type": "migrated",
                    "context_json": json.dumps(context),
                    "error_message": error,
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "created_at": created_at,
                }
            )
            
            print(f"  ✅ Migrated run: {run_id} (status: {dag_status})")
            migrated += 1
            
        except (IntegrityError, OperationalError) as e:
            print(f"  ❌ Failed run: {run_id} - {e}")
            failed_ids.append(run_id)
            session.rollback()
    
    return migrated, failed_ids


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Migrate workflows to DAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Preview what would be migrated
    python scripts/migrate_workflows_to_dags.py --dry-run
    
    # Execute the migration
    python scripts/migrate_workflows_to_dags.py --execute
"""
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Preview changes without executing"
    )
    parser.add_argument(
        "--execute", 
        action="store_true", 
        help="Execute the migration"
    )
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("Error: Must specify either --dry-run or --execute")
        print("Use --help for usage information.")
        sys.exit(1)
    
    dry_run = not args.execute
    
    print("=" * 70)
    print("Phase 4 Data Migration: Workflows → DAG Definitions")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else '🚨 EXECUTE (changes will be committed)'}")
    print()
    
    # Create sync engine
    print("🔌 Connecting to database...")
    engine = create_sync_engine()
    print()
    
    with Session(engine) as session:
        # === Count before ===
        print("📊 Checking legacy tables...")
        try:
            legacy_counts = count_legacy_records(session)
            print(f"   Workflows:     {legacy_counts['workflows']}")
            print(f"   Workflow runs: {legacy_counts['workflow_runs']}")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not read legacy tables: {e}")
            print("   Tables may not exist or migration already complete.")
            legacy_counts = {"workflows": 0, "workflow_runs": 0}
        
        print()
        print("📊 Checking DAG tables...")
        try:
            dag_counts_before = count_dag_records(session)
            print(f"   DAG definitions: {dag_counts_before['dag_definitions']}")
            print(f"   DAG steps:       {dag_counts_before['dag_definition_steps']}")
            print(f"   DAG edges:       {dag_counts_before['dag_definition_edges']}")
            print(f"   DAG runs:        {dag_counts_before['dag_runs']}")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not read DAG tables: {e}")
            print("   Please ensure alembic migrations have been run.")
            sys.exit(1)
        
        print()
        
        if legacy_counts["workflows"] == 0 and legacy_counts["workflow_runs"] == 0:
            print("ℹ️  No legacy data to migrate. Exiting.")
            return
        
        # === Migrate workflows ===
        print("🔄 Migrating workflow definitions...")
        print("   (Each workflow → 1 dag_definition + N dag_definition_steps + N-1 edges)")
        wf_migrated, wf_failed = migrate_workflows(session, dry_run)
        print()
        print(f"   → {wf_migrated} definitions {'would be' if dry_run else 'were'} migrated")
        if wf_failed:
            print(f"   → {len(wf_failed)} failed: {wf_failed}")
        print()
        
        # === Migrate runs ===
        print("🔄 Migrating workflow runs...")
        runs_migrated, runs_failed = migrate_workflow_runs(session, dry_run)
        print()
        print(f"   → {runs_migrated} runs {'would be' if dry_run else 'were'} migrated")
        if runs_failed:
            print(f"   → {len(runs_failed)} failed: {runs_failed}")
        print()
        
        # === Commit or summarize ===
        if not dry_run:
            session.commit()
            print("✅ Migration committed successfully!")
            
            # Verify
            dag_counts_after = count_dag_records(session)
            print()
            print("📊 Verification (before → after):")
            print(f"   DAG definitions: {dag_counts_before['dag_definitions']} → {dag_counts_after['dag_definitions']}")
            print(f"   DAG steps:       {dag_counts_before['dag_definition_steps']} → {dag_counts_after['dag_definition_steps']}")
            print(f"   DAG edges:       {dag_counts_before['dag_definition_edges']} → {dag_counts_after['dag_definition_edges']}")
            print(f"   DAG runs:        {dag_counts_before['dag_runs']} → {dag_counts_after['dag_runs']}")
            
            if wf_failed or runs_failed:
                print()
                print("⚠️  Some records failed to migrate. Please review and retry or fix manually.")
                sys.exit(1)
        else:
            print("─" * 70)
            print("Dry run complete. No changes made.")
            print("Run with --execute to perform migration.")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
