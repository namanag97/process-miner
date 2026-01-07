#!/usr/bin/env python3
"""
Phase 2: Fix multiline HTTPException patterns with dict details.

These patterns have structured error responses like:
    raise HTTPException(
        status_code=404,
        detail={
            "error": "Project not found",
            "error_code": "PROJ_NOT_FOUND",
            ...
        },
    )

Usage:
    python scripts/fix_multiline_httpexception.py --dry-run
    python scripts/fix_multiline_httpexception.py
"""

import re
from pathlib import Path


# Files with multiline HTTPException patterns
TARGET_FILES = [
    "src/platform/projects/api.py",
    "src/platform/workspaces/api.py", 
    "src/platform/auth/api.py",
    "src/platform/auth/router.py",
    "src/platform/core/validation.py",
    "src/platform/devtools/router.py",
    "src/platform/devtools/dev_data.py",
]

# Multiline pattern: raise HTTPException(\n    status_code=XXX,\n    detail={...}\n)
MULTILINE_PATTERN = re.compile(
    r'raise HTTPException\(\s*\n\s*status_code\s*=\s*(\d+)\s*,\s*\n\s*detail\s*=\s*(\{[^}]+\})\s*,?\s*\n\s*\)',
    re.MULTILINE | re.DOTALL
)


def extract_error_message(detail_dict_str: str) -> str:
    """Extract the error message from a detail dict string."""
    # Look for "error": "..."
    match = re.search(r'"error"\s*:\s*"([^"]+)"', detail_dict_str)
    if match:
        return match.group(1)
    return "Operation failed"


def extract_resource_id_var(detail_dict_str: str) -> str:
    """Try to find a resource ID variable in the details."""
    # Look for "project_id": project_id or similar
    match = re.search(r'"(\w+_id)"\s*:\s*(\w+_id)', detail_dict_str)
    if match:
        return match.group(2)
    return "'unknown'"


def generate_replacement(status_code: int, detail_dict_str: str, original: str) -> str:
    """Generate the AppException replacement."""
    error_msg = extract_error_message(detail_dict_str)
    resource_id_var = extract_resource_id_var(detail_dict_str)
    
    if status_code == 404:
        if "project" in error_msg.lower():
            return f"raise ProjectNotFoundError(project_id={resource_id_var})"
        elif "workspace" in error_msg.lower():
            return f"raise NotFoundError(resource='Workspace', resource_id={resource_id_var})"
        elif "model" in error_msg.lower():
            return f"raise ModelNotFoundError(model_id={resource_id_var})"
        else:
            return f"raise NotFoundError(resource='Resource', resource_id={resource_id_var})"
    
    elif status_code == 400:
        return f'raise BadRequestError(message="{error_msg}")'
    
    elif status_code == 500:
        return f'raise ProcessingError(message="{error_msg}")'
    
    elif status_code == 401:
        return f'raise AuthenticationError(message="{error_msg}")'
    
    elif status_code == 403:
        return f'raise ForbiddenError(message="{error_msg}")'
    
    elif status_code == 409:
        return f'raise ConflictError(message="{error_msg}")'
    
    elif status_code == 413:
        return f'raise BadRequestError(message="{error_msg}")'
    
    else:
        return f'raise ProcessingError(message="{error_msg}")'


def process_file(file_path: Path, dry_run: bool = True) -> tuple[int, list[str]]:
    """Process a single file, return (count, changes)."""
    if not file_path.exists():
        return 0, []
    
    content = file_path.read_text()
    changes = []
    count = 0
    
    # Find all matches
    for match in MULTILINE_PATTERN.finditer(content):
        status_code = int(match.group(1))
        detail_dict = match.group(2)
        original = match.group(0)
        
        replacement = generate_replacement(status_code, detail_dict, original)
        changes.append(f"  Line ~?: {status_code} → {replacement}")
        
        if not dry_run:
            content = content.replace(original, replacement)
        
        count += 1
    
    if not dry_run and count > 0:
        file_path.write_text(content)
    
    return count, changes


def add_imports_to_file(file_path: Path, dry_run: bool = True) -> bool:
    """Add missing exception imports to a file."""
    if not file_path.exists():
        return False
    
    content = file_path.read_text()
    
    # Check what exceptions are used
    exceptions_used = set()
    exception_names = [
        'NotFoundError', 'ProjectNotFoundError', 'ModelNotFoundError',
        'BadRequestError', 'ProcessingError', 'AuthenticationError',
        'ForbiddenError', 'ConflictError', 'ValidationError',
    ]
    
    for exc in exception_names:
        if exc in content and f"class {exc}" not in content:
            exceptions_used.add(exc)
    
    if not exceptions_used:
        return False
    
    # Check if we already have an import
    if 'from src.platform.core.exceptions import' in content:
        # Already has import line, need to update it
        return False  # For now, skip these
    
    # Add import after existing imports
    import_line = f"from src.platform.core.exceptions import {', '.join(sorted(exceptions_used))}\n"
    
    # Find the last import line
    lines = content.split('\n')
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            last_import_idx = i
    
    if not dry_run:
        lines.insert(last_import_idx + 1, import_line)
        file_path.write_text('\n'.join(lines))
        return True
    
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix multiline HTTPException patterns')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes only')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Phase 2: Multiline HTTPException Migration")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLY CHANGES'}")
    print()
    
    base_dir = Path(__file__).parent.parent
    total_fixed = 0
    
    for file_rel in TARGET_FILES:
        file_path = base_dir / file_rel
        count, changes = process_file(file_path, dry_run=args.dry_run)
        
        if count > 0:
            prefix = "🔍" if args.dry_run else "✅"
            print(f"{prefix} {file_path.name}: {count} instances")
            for change in changes[:3]:
                print(change)
            if len(changes) > 3:
                print(f"    ... and {len(changes) - 3} more")
            total_fixed += count
    
    print()
    print("=" * 60)
    print(f"Total: {total_fixed} multiline HTTPExceptions")
    
    if args.dry_run:
        print("Run without --dry-run to apply changes")
    else:
        print("✅ Migration complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
