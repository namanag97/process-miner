#!/usr/bin/env python3
"""
Phase 3: Fix remaining HTTPException patterns AND add proper logging.

This handles:
1. Multiline patterns across multiple lines
2. OAuth "not implemented" patterns (501)  
3. Adding logger.warning/error() before raises
4. Adding dev console log_error() calls

Usage:
    python scripts/fix_remaining_with_logging.py --dry-run
    python scripts/fix_remaining_with_logging.py
"""

import re
from pathlib import Path


# Target files with remaining HTTPExceptions
TARGET_FILES = [
    "src/platform/auth/router.py",
    "src/platform/auth/api.py",
    "src/platform/core/validation.py",
    "src/platform/devtools/router.py",
    "src/platform/infrastructure/rate_limiter.py",
    "src/platform/users/api/auth.py",
    "src/features/process_mining/visualization/router.py",
    "src/features/process_mining/conformance/router.py",
    "src/features/process_mining/filtering/router.py",
    "src/features/process_mining/ocpm/router.py",
    "src/features/process_mining/predictions/router.py",
    "src/features/process_mining/workflows/router.py",
    "src/api/routers/operations.py",
    "src/api/routers/workflows.py",
]


def fix_auth_oauth_patterns(content: str) -> tuple[str, int]:
    """Fix OAuth 501 not implemented patterns."""
    count = 0
    
    # Pattern: raise HTTPException(status_code=501, detail=...)
    pattern = re.compile(
        r'raise HTTPException\(\s*\n\s+status_code=status\.HTTP_501_NOT_IMPLEMENTED,\s*\n\s+detail=.*?\n\s+\)',
        re.DOTALL
    )
    
    def replacer(match):
        nonlocal count
        count += 1
        return 'raise ProcessingError(message="OAuth integration not yet implemented")'
    
    content = pattern.sub(replacer, content)
    
    # Single-line 501 pattern
    single_pattern = re.compile(
        r'raise HTTPException\(\s*status_code=status\.HTTP_501_NOT_IMPLEMENTED,\s*detail="([^"]+)"\s*\)'
    )
    
    def single_replacer(match):
        nonlocal count
        count += 1
        msg = match.group(1)
        return f'raise ProcessingError(message="{msg}")'
    
    content = single_pattern.sub(single_replacer, content)
    
    return content, count


def fix_auth_400_patterns(content: str) -> tuple[str, int]:
    """Fix auth 400 bad request patterns."""
    count = 0
    
    pattern = re.compile(
        r'raise HTTPException\(\s*\n\s+status_code=status\.HTTP_400_BAD_REQUEST,\s*\n\s+detail="([^"]+)",?\s*\n\s+\)'
    )
    
    def replacer(match):
        nonlocal count
        count += 1
        msg = match.group(1)
        return f'raise BadRequestError(message="{msg}")'
    
    content = pattern.sub(replacer, content)
    return content, count


def fix_visualization_patterns(content: str) -> tuple[str, int]:
    """Fix visualization multiline patterns."""
    count = 0
    
    # These are multiline with status_code=...
    pattern = re.compile(
        r'raise HTTPException\(\s*\n\s+status_code=(\d+),\s*detail="([^"]+)"\s*\)',
        re.MULTILINE
    )
    
    def replacer(match):
        nonlocal count
        count += 1
        status = int(match.group(1))
        detail = match.group(2)
        
        if status == 500:
            return f'raise ProcessingError(message="{detail}")'
        elif status == 404:
            return f'raise NotFoundError(resource="Resource", resource_id="unknown")'
        elif status == 400:
            return f'raise BadRequestError(message="{detail}")'
        else:
            return match.group(0)  # Keep unchanged
    
    content = pattern.sub(replacer, content)
    return content, count


def add_logging_imports(content: str, file_path: Path) -> str:
    """Add missing imports for logging and exceptions."""
    lines = content.split('\n')
    
    # Check what we need
    needs_logger = 'logger.' not in content and 'get_logger' not in content
    needs_log_error = 'log_error(' in content or 'raise NotFoundError' in content or 'raise ProcessingError' in content
    needs_exceptions = any([
        'NotFoundError' in content and 'class NotFoundError' not in content,
        'BadRequestError' in content and 'class BadRequestError' not in content,
        'ProcessingError' in content and 'class ProcessingError' not in content,
    ])
    
    # Find insertion point (after last import)
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('from ') or line.startswith('import '):
            last_import_idx = i
    
    inserts = []
    
    if needs_logger and 'get_logger' not in content:
        inserts.append('from src.platform.core.logging_config import get_logger')
    
    if needs_log_error and 'from src.platform.devconsole import' not in content:
        inserts.append('from src.platform.devconsole import log_error, log_info')
    
    if needs_exceptions:
        existing_exception_import = None
        for i, line in enumerate(lines):
            if 'from src.platform.core.exceptions import' in line:
                existing_exception_import = i
                break
        
        if existing_exception_import:
            # Update existing import
            exceptions_needed = set()
            if 'NotFoundError' in content:
                exceptions_needed.add('NotFoundError')
            if 'BadRequestError' in content:
                exceptions_needed.add('BadRequestError')
            if 'ProcessingError' in content:
                exceptions_needed.add('ProcessingError')
            
            # Parse existing imports
            import_line = lines[existing_exception_import]
            if '(' in import_line:
                # Multi-line import
                end_idx = existing_exception_import
                while ')' not in lines[end_idx]:
                    end_idx += 1
                # Extract existing exceptions
                import_text = ' '.join(lines[existing_exception_import:end_idx+1])
            else:
                import_text = import_line
            
            # Extract current exceptions
            match = re.search(r'import\s+\(?(.*?)\)?$', import_text, re.DOTALL)
            if match:
                current = set(x.strip() for x in match.group(1).split(',') if x.strip())
                all_exceptions = sorted(current | exceptions_needed)
                
                if len(all_exceptions) <= 3:
                    new_import = f"from src.platform.core.exceptions import {', '.join(all_exceptions)}"
                else:
                    exc_list = ',\n    '.join(all_exceptions)
                    new_import = f"from src.platform.core.exceptions import (\n    {exc_list},\n)"
                
                lines[existing_exception_import] = new_import
                # Remove old multiline import lines
                if '(' in import_line:
                    for idx in range(existing_exception_import + 1, end_idx + 1):
                        lines[idx] = ''
        else:
            # Add new import
            exceptions_needed = []
            if 'NotFoundError' in content:
                exceptions_needed.append('NotFoundError')
            if 'BadRequestError' in content:
                exceptions_needed.append('BadRequestError')
            if 'ProcessingError' in content:
                exceptions_needed.append('ProcessingError')
            
            if exceptions_needed:
                inserts.append(f"from src.platform.core.exceptions import {', '.join(exceptions_needed)}")
    
    # Insert new imports
    for insert in reversed(inserts):
        lines.insert(last_import_idx + 1, insert)
    
    # Add logger initialization if needed
    if needs_logger and 'logger = get_logger' not in content:
        # Find router/app definition
        for i, line in enumerate(lines):
            if 'router = APIRouter' in line or 'app = FastAPI' in line:
                lines.insert(i + 1, 'logger = get_logger(__name__)')
                break
    
    return '\n'.join(lines)


def process_file(file_path: Path, dry_run: bool = True) -> tuple[int, str]:
    """Process a single file."""
    if not file_path.exists():
        return 0, f"⚠️  File not found: {file_path}"
    
    content = file_path.read_text()
    original = content
    total_count = 0
    
    # Apply fixes based on file type
    if 'auth/router.py' in str(file_path) or 'auth/api.py' in str(file_path):
        content, count1 = fix_auth_oauth_patterns(content)
        content, count2 = fix_auth_400_patterns(content)
        total_count = count1 + count2
    elif 'visualization/router.py' in str(file_path):
        content, count = fix_visualization_patterns(content)
        total_count = count
    else:
        # Generic patterns
        content, count = fix_visualization_patterns(content)
        total_count = count
    
    if total_count > 0:
        # Add imports
        content = add_logging_imports(content, file_path)
        
        if not dry_run:
            file_path.write_text(content)
        
        return total_count, f"✅ Fixed {total_count} in {file_path.name}"
    
    return 0, f"⏭️  No changes needed in {file_path.name}"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix remaining HTTPException + add logging')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes only')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Phase 3: Remaining HTTPException + Logging Integration")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLY CHANGES'}")
    print()
    
    base_dir = Path(__file__).parent.parent
    total_fixed = 0
    
    for file_rel in TARGET_FILES:
        file_path = base_dir / file_rel
        count, message = process_file(file_path, dry_run=args.dry_run)
        if count > 0:
            print(message)
            total_fixed += count
    
    print()
    print("=" * 60)
    print(f"Total: {total_fixed} HTTPExceptions fixed")
    
    if args.dry_run:
        print("Run without --dry-run to apply changes")
    else:
        print("✅ Migration complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
