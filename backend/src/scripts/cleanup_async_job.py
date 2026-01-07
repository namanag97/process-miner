"""Dead Code Deletion Checklist.

This script lists all files and code that should be deleted
after successful migration to Temporal-native architecture.

Run this after Week 4 monitoring period is complete.

Usage:
    python -m src.scripts.cleanup_async_job --check     # Check what will be deleted
    python -m src.scripts.cleanup_async_job --execute   # Actually delete files
"""

import argparse
import os
from pathlib import Path

# Files and directories to delete
DELETE_FILES = [
    # Celery tasks (replaced by Temporal activities)
    "src/platform/infrastructure/tasks/dataset_tasks.py",
    "src/platform/infrastructure/tasks/analysis_tasks.py",
    "src/platform/infrastructure/tasks/ml_tasks.py",
    "src/platform/infrastructure/tasks/maintenance_tasks.py",
    "src/platform/infrastructure/tasks/base.py",
    "src/platform/infrastructure/tasks/__init__.py",
    # Legacy Temporal compat layer
    "src/platform/temporal/compat.py",
    # Old workflows (replaced by v2)
    # Keep these as backup until v2 is fully validated
    # "src/platform/temporal/workflows/ingestion.py",
    # "src/platform/temporal/workflows/analysis.py",
]

# Code to remove from files (search patterns)
CODE_TO_REMOVE = {
    "src/platform/models.py": [
        "class AsyncJob",  # Entire class
    ],
    "src/platform/infrastructure/repositories.py": [
        "class AsyncJobRepository",
        "class SQLAlchemyAsyncJobRepository",
    ],
    "src/shared/repositories.py": [
        "AsyncJobRepository",  # Any references
    ],
}

# Database migrations to create
MIGRATIONS_NEEDED = [
    {
        "name": "drop_async_jobs_table",
        "sql": "DROP TABLE IF EXISTS async_jobs CASCADE;",
        "description": "Drop the async_jobs table after migration complete",
    },
]


def check_deletions(base_path: Path) -> dict:
    """Check what will be deleted."""
    results = {
        "files_exist": [],
        "files_missing": [],
        "code_patterns": [],
        "migrations": MIGRATIONS_NEEDED,
    }

    for file_path in DELETE_FILES:
        full_path = base_path / file_path
        if full_path.exists():
            results["files_exist"].append(str(full_path))
        else:
            results["files_missing"].append(str(full_path))

    for file_path, patterns in CODE_TO_REMOVE.items():
        full_path = base_path / file_path
        if full_path.exists():
            with open(full_path) as f:
                content = f.read()
            for pattern in patterns:
                if pattern in content:
                    results["code_patterns"].append(f"{file_path}: {pattern}")

    return results


def execute_deletions(base_path: Path, dry_run: bool = True) -> None:
    """Execute file deletions."""

    for file_path in DELETE_FILES:
        full_path = base_path / file_path
        if full_path.exists():
            if dry_run:
                pass
            else:
                os.remove(full_path)
        else:
            pass


def main():
    parser = argparse.ArgumentParser(description="Cleanup AsyncJob dead code")
    parser.add_argument("--check", action="store_true", help="Check what will be deleted")
    parser.add_argument("--execute", action="store_true", help="Actually delete files")
    args = parser.parse_args()

    # Find the backend directory
    script_path = Path(__file__).resolve()
    base_path = script_path.parent.parent.parent  # Go up from scripts/

    results = check_deletions(base_path)

    for _f in results["files_exist"]:
        pass
    if results["files_missing"]:
        for _f in results["files_missing"]:
            pass

    for _pattern in results["code_patterns"]:
        pass

    for _migration in results["migrations"]:
        pass

    if args.execute:
        confirm = input("Are you sure you want to delete these files? (yes/no): ")
        if confirm.lower() == "yes":
            execute_deletions(base_path, dry_run=False)
        else:
            pass
    elif args.check:
        pass
    else:
        pass


if __name__ == "__main__":
    main()
