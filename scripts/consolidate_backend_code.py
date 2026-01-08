#!/usr/bin/env python3
"""
Script to consolidate all backend-relevant code into a single text file.
This includes Python source files, configuration files, and documentation.
"""

import os
from pathlib import Path
from typing import List, Set

# Define the backend directory
BACKEND_DIR = Path(__file__).parent.parent / "backend"
OUTPUT_FILE = Path(__file__).parent.parent / "backend_code_consolidated.txt"

# File extensions to include
INCLUDE_EXTENSIONS = {
    # Python files
    ".py",
    # Configuration files
    ".toml",
    ".ini",
    ".yaml",
    ".yml",
    ".json",
    ".env.example",
    # Documentation
    ".md",
    # Database
    ".dbml",
    # Makefile
    "",  # For Makefile without extension
}

# Directories to exclude
EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".import_linter_cache",
    "node_modules",
    ".git",
    ".claude",
    "frontend-new",
    "agent-sessions",
}

# Files to exclude
EXCLUDE_FILES = {
    ".DS_Store",
    "process_mining.db",
    ".env",  # Exclude actual .env for security
    "openapi_extracted.json",  # Too large
    "schemas_extracted.json",  # Too large
}


def should_include_file(file_path: Path) -> bool:
    """Determine if a file should be included in the consolidation."""
    # Check if file is in excluded directories
    for parent in file_path.parents:
        if parent.name in EXCLUDE_DIRS:
            return False
    
    # Check if file is in exclude list
    if file_path.name in EXCLUDE_FILES:
        return False
    
    # Check extension
    if file_path.suffix in INCLUDE_EXTENSIONS:
        return True
    
    # Special case for Makefile
    if file_path.name == "Makefile":
        return True
    
    return False


def collect_files(root_dir: Path) -> List[Path]:
    """Collect all relevant files from the backend directory."""
    files = []
    
    for item in root_dir.rglob("*"):
        if item.is_file() and should_include_file(item):
            files.append(item)
    
    # Sort files for consistent output
    files.sort()
    return files


def write_consolidated_file(files: List[Path], output_path: Path, root_dir: Path):
    """Write all files to a single consolidated text file."""
    with open(output_path, "w", encoding="utf-8") as outfile:
        # Write header
        outfile.write("=" * 80 + "\n")
        outfile.write("BACKEND CODE CONSOLIDATION\n")
        outfile.write(f"Generated from: {root_dir}\n")
        outfile.write(f"Total files: {len(files)}\n")
        outfile.write("=" * 80 + "\n\n")
        
        # Write table of contents
        outfile.write("TABLE OF CONTENTS\n")
        outfile.write("-" * 80 + "\n")
        for idx, file_path in enumerate(files, 1):
            rel_path = file_path.relative_to(root_dir)
            outfile.write(f"{idx}. {rel_path}\n")
        outfile.write("\n" + "=" * 80 + "\n\n")
        
        # Write each file
        for idx, file_path in enumerate(files, 1):
            rel_path = file_path.relative_to(root_dir)
            
            outfile.write("\n" + "=" * 80 + "\n")
            outfile.write(f"FILE {idx}/{len(files)}: {rel_path}\n")
            outfile.write("=" * 80 + "\n\n")
            
            try:
                with open(file_path, "r", encoding="utf-8") as infile:
                    content = infile.read()
                    outfile.write(content)
                    
                    # Ensure file ends with newline
                    if content and not content.endswith("\n"):
                        outfile.write("\n")
                        
            except Exception as e:
                outfile.write(f"[ERROR READING FILE: {e}]\n")
            
            outfile.write("\n")


def main():
    """Main function to consolidate backend code."""
    print(f"Backend directory: {BACKEND_DIR}")
    print(f"Output file: {OUTPUT_FILE}")
    print()
    
    # Collect files
    print("Collecting files...")
    files = collect_files(BACKEND_DIR)
    print(f"Found {len(files)} files to consolidate")
    print()
    
    # Show file breakdown by extension
    extensions = {}
    for file_path in files:
        ext = file_path.suffix if file_path.suffix else "no extension"
        extensions[ext] = extensions.get(ext, 0) + 1
    
    print("File breakdown by type:")
    for ext, count in sorted(extensions.items(), key=lambda x: -x[1]):
        print(f"  {ext}: {count} files")
    print()
    
    # Write consolidated file
    print("Writing consolidated file...")
    write_consolidated_file(files, OUTPUT_FILE, BACKEND_DIR)
    
    # Show output file size
    size_mb = OUTPUT_FILE.stat().st_size / (1024 * 1024)
    print(f"✓ Consolidation complete!")
    print(f"  Output: {OUTPUT_FILE}")
    print(f"  Size: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
