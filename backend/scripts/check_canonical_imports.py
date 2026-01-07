#!/usr/bin/env python3
"""Check for imports from deprecated/duplicate code paths.

This script ensures that imports use canonical paths rather than deprecated
duplicate paths. Run as part of CI to prevent duplicate code from returning.

Canonical import paths:
- Models: src.features.process_mining.models
- Datasets API: src.features.process_mining.datasets.api
- Ingestion: src.features.process_mining.ingestion

Deprecated paths (should not be imported from):
- src.features.process_mining.api.datasets (deleted - was duplicate of datasets.api)
- src.features.process_mining.datasets.models (deleted - was duplicate of models)
- src.features.process_mining.services.ingestion (shim - use ingestion directly)
- src.features.process_mining.datasets.services.ingestion (shim - use ingestion directly)
"""

import subprocess
import sys
from pathlib import Path

# Paths that should never be imported from (outside their own modules)
DEPRECATED_PATHS = [
    ("src.features.process_mining.api.datasets", "src.features.process_mining.datasets.api"),
    ("src.features.process_mining.datasets.models", "src.features.process_mining.models"),
    ("src.features.process_mining.services.ingestion", "src.features.process_mining.ingestion"),
    (
        "src.features.process_mining.datasets.services.ingestion",
        "src.features.process_mining.ingestion",
    ),
]


def check_deprecated_imports(src_dir: Path) -> list[str]:
    """Check for imports from deprecated paths.

    Args:
        src_dir: The source directory to check.

    Returns:
        List of error messages for any deprecated imports found.
    """
    errors = []

    for deprecated_path, canonical_path in DEPRECATED_PATHS:
        # Convert module path to directory path for exclusion
        deprecated_dir = deprecated_path.replace(".", "/")

        # Search for imports from this deprecated path
        # Exclude files within the deprecated path itself (they're allowed to import from each other)
        patterns = [
            f"from {deprecated_path}",
            f"import {deprecated_path}",
        ]

        for pattern in patterns:
            result = subprocess.run(
                [
                    "grep",
                    "-r",
                    "--include=*.py",
                    f"--exclude-dir={deprecated_dir.split('/')[-1]}",
                    pattern,
                    str(src_dir),
                ],
                capture_output=True,
                text=True,
            )

            if result.stdout.strip():
                # Filter out matches from within the deprecated module itself
                for line in result.stdout.strip().split("\n"):
                    file_path = line.split(":")[0]
                    # Skip if the file is within the deprecated directory
                    if deprecated_dir not in file_path:
                        errors.append(
                            f"DEPRECATED IMPORT: {line}\n"
                            f"  -> Use canonical path: {canonical_path}"
                        )

    return errors


def check_for_duplicate_modules(src_dir: Path) -> list[str]:
    """Check if any deleted duplicate modules have been recreated.

    Args:
        src_dir: The source directory to check.

    Returns:
        List of error messages for any recreated duplicate modules.
    """
    errors = []

    # Paths that should not exist (they were deleted duplicates)
    forbidden_paths = [
        src_dir / "features/process_mining/api/datasets",
        src_dir / "features/process_mining/datasets/models",
    ]

    for path in forbidden_paths:
        if path.exists():
            errors.append(
                f"DUPLICATE MODULE RECREATED: {path}\n"
                f"  -> This path was deleted to eliminate duplication. "
                f"Do not recreate it."
            )

    return errors


def main() -> int:
    """Main entry point.

    Returns:
        Exit code: 0 for success, 1 for errors found.
    """
    # Determine the source directory
    script_dir = Path(__file__).parent
    src_dir = script_dir.parent / "src"

    if not src_dir.exists():
        print(f"ERROR: Source directory not found: {src_dir}")
        return 1

    print(f"Checking canonical imports in: {src_dir}")
    print("-" * 60)

    all_errors = []

    # Check for deprecated imports
    import_errors = check_deprecated_imports(src_dir)
    all_errors.extend(import_errors)

    # Check for recreated duplicate modules
    module_errors = check_for_duplicate_modules(src_dir)
    all_errors.extend(module_errors)

    if all_errors:
        print("ERRORS FOUND:")
        print()
        for error in all_errors:
            print(f"  {error}")
            print()
        print("-" * 60)
        print(f"Total errors: {len(all_errors)}")
        print()
        print("To fix: Update imports to use canonical paths as indicated above.")
        return 1

    print("OK: All imports use canonical paths.")
    print("OK: No duplicate modules found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
