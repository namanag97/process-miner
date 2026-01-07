#!/usr/bin/env python3
"""
Bulk HTTPException → AppException Migration Script

This script automates the conversion of raw HTTPException raises to our 
standardized AppException hierarchy for RFC 7807 compliance.

Usage:
    # Dry run (preview changes)
    python scripts/bulk_fix_httpexception.py --dry-run

    # Apply changes to specific file
    python scripts/bulk_fix_httpexception.py src/features/process_mining/conformance/router.py

    # Apply to all files
    python scripts/bulk_fix_httpexception.py --all

    # Generate report only
    python scripts/bulk_fix_httpexception.py --report
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# ============================================================================
# PATTERN MATCHING RULES
# ============================================================================

@dataclass
class ReplacementRule:
    """Rule for converting HTTPException to AppException."""
    status_code: int
    detail_pattern: str  # Regex pattern to match detail string
    exception_class: str
    arg_template: str    # Template for exception arguments
    priority: int = 0    # Higher = more specific


RULES: list[ReplacementRule] = [
    # ---------------------------------------------------------------------
    # 404 Not Found → NotFoundError hierarchy (most specific first)
    # ---------------------------------------------------------------------
    ReplacementRule(
        status_code=404,
        detail_pattern=r"Project.*not found|Project not found",
        exception_class="ProjectNotFoundError",
        arg_template="project_id={resource_id}",
        priority=10,
    ),
    ReplacementRule(
        status_code=404,
        detail_pattern=r"Model.*not found|Process model not found",
        exception_class="ModelNotFoundError",
        arg_template="model_id={resource_id}",
        priority=10,
    ),
    ReplacementRule(
        status_code=404,
        detail_pattern=r"Dataset.*not found|Event log not found",
        exception_class="NotFoundError",
        arg_template="resource='Dataset', resource_id={resource_id}",
        priority=5,
    ),
    ReplacementRule(
        status_code=404,
        detail_pattern=r"OCEL.*not found",
        exception_class="NotFoundError",
        arg_template="resource='OCEL Log', resource_id={resource_id}",
        priority=5,
    ),
    ReplacementRule(
        status_code=404,
        detail_pattern=r"OC-PN.*not found",
        exception_class="NotFoundError",
        arg_template="resource='OC-PN Model', resource_id={resource_id}",
        priority=5,
    ),
    ReplacementRule(
        status_code=404,
        detail_pattern=r"Predictor.*not found",
        exception_class="NotFoundError",
        arg_template="resource='Predictor', resource_id={resource_id}",
        priority=5,
    ),
    ReplacementRule(
        status_code=404,
        detail_pattern=r"Conformance.*not found",
        exception_class="NotFoundError",
        arg_template="resource='Conformance Result', resource_id={resource_id}",
        priority=5,
    ),
    ReplacementRule(
        status_code=404,
        detail_pattern=r"Analysis.*not found",
        exception_class="NotFoundError",
        arg_template="resource='Analysis', resource_id={resource_id}",
        priority=5,
    ),
    ReplacementRule(
        status_code=404,
        detail_pattern=r"Workflow.*not found",
        exception_class="NotFoundError",
        arg_template="resource='Workflow', resource_id={resource_id}",
        priority=5,
    ),
    ReplacementRule(
        status_code=404,
        detail_pattern=r"Workspace.*not found",
        exception_class="NotFoundError",
        arg_template="resource='Workspace', resource_id={resource_id}",
        priority=5,
    ),
    # Generic 404 fallback
    ReplacementRule(
        status_code=404,
        detail_pattern=r".*not found.*",
        exception_class="NotFoundError",
        arg_template="resource='Resource', resource_id='unknown'",
        priority=0,
    ),
    
    # ---------------------------------------------------------------------
    # 500 Processing Errors → ProcessingError hierarchy
    # ---------------------------------------------------------------------
    ReplacementRule(
        status_code=500,
        detail_pattern=r"Conformance.*failed|conformance.*failed",
        exception_class="ConformanceError",
        arg_template="message={detail}",
        priority=10,
    ),
    ReplacementRule(
        status_code=500,
        detail_pattern=r"Discovery.*failed|discovery.*failed|OC-PN discovery",
        exception_class="DiscoveryError",
        arg_template="message={detail}",
        priority=10,
    ),
    ReplacementRule(
        status_code=500,
        detail_pattern=r"OC-DFG.*failed",
        exception_class="ProcessingError",
        arg_template="message={detail}",
        priority=5,
    ),
    ReplacementRule(
        status_code=500,
        detail_pattern=r".*failed.*|.*error.*",
        exception_class="ProcessingError",
        arg_template="message={detail}",
        priority=0,
    ),
    
    # ---------------------------------------------------------------------
    # 400 Bad Request → BadRequestError
    # ---------------------------------------------------------------------
    ReplacementRule(
        status_code=400,
        detail_pattern=r"Invalid|Unsupported|Malformed",
        exception_class="BadRequestError",
        arg_template="message={detail}",
        priority=5,
    ),
    ReplacementRule(
        status_code=400,
        detail_pattern=r".*not stored.*|.*missing.*|.*has no.*",
        exception_class="BadRequestError",
        arg_template="message={detail}",
        priority=5,
    ),
    ReplacementRule(
        status_code=400,
        detail_pattern=r".*",
        exception_class="BadRequestError",
        arg_template="message={detail}",
        priority=0,
    ),
    
    # ---------------------------------------------------------------------
    # 409 Conflict → ConflictError
    # ---------------------------------------------------------------------
    ReplacementRule(
        status_code=409,
        detail_pattern=r".*",
        exception_class="ConflictError",
        arg_template="message={detail}",
        priority=0,
    ),
    
    # ---------------------------------------------------------------------
    # 422 Validation → ValidationError
    # ---------------------------------------------------------------------
    ReplacementRule(
        status_code=422,
        detail_pattern=r".*",
        exception_class="ValidationError",
        arg_template="message={detail}",
        priority=0,
    ),
    
    # ---------------------------------------------------------------------
    # 401/403 Auth → AuthenticationError/ForbiddenError
    # ---------------------------------------------------------------------
    ReplacementRule(
        status_code=401,
        detail_pattern=r".*",
        exception_class="AuthenticationError",
        arg_template="message={detail}",
        priority=0,
    ),
    ReplacementRule(
        status_code=403,
        detail_pattern=r".*",
        exception_class="ForbiddenError",
        arg_template="message={detail}",
        priority=0,
    ),
    
    # ---------------------------------------------------------------------
    # 503 Service Unavailable → ServiceUnavailableError
    # ---------------------------------------------------------------------
    ReplacementRule(
        status_code=503,
        detail_pattern=r".*",
        exception_class="ServiceUnavailableError",
        arg_template="service='External'",
        priority=0,
    ),
]


# ============================================================================
# REGEX PATTERNS
# ============================================================================

# Match: raise HTTPException(status_code=404, detail="...")
HTTPEXCEPTION_PATTERN = re.compile(
    r'raise\s+HTTPException\s*\(\s*'
    r'status_code\s*=\s*(\d+)\s*,\s*'
    r'detail\s*=\s*(["\'].*?["\']|f["\'].*?["\']|[^)]+)'
    r'\s*\)',
    re.DOTALL
)

# Match: raise HTTPException(...)multiline
HTTPEXCEPTION_MULTILINE = re.compile(
    r'raise\s+HTTPException\s*\(',
    re.MULTILINE
)


@dataclass
class HTTPExceptionMatch:
    """Represents a found HTTPException in code."""
    file_path: str
    line_number: int
    status_code: int
    detail: str
    full_match: str
    suggestion: Optional[str] = None


def extract_resource_id(detail: str, file_content: str = "") -> str:
    """Try to extract the resource ID variable from context."""
    # Look for common patterns like {dataset_id}, {model_id}, etc.
    if "dataset_id" in detail or "dataset_id" in file_content:
        return "dataset_id"
    if "model_id" in detail or "model_id" in file_content:
        return "model_id"
    if "project_id" in detail or "project_id" in file_content:
        return "project_id"
    if "predictor_id" in detail or "predictor_id" in file_content:
        return "predictor_id"
    if "result_id" in detail or "result_id" in file_content:
        return "result_id"
    if "workflow_id" in detail or "workflow_id" in file_content:
        return "workflow_id"
    if "ocel_id" in detail or "ocel_id" in file_content:
        return "ocel_id"
    if "log_id" in detail or "log_id" in file_content:
        return "log_id"
    return "'unknown'"


def find_matching_rule(status_code: int, detail: str) -> Optional[ReplacementRule]:
    """Find the best matching rule for a given HTTPException."""
    matching_rules = []
    
    for rule in RULES:
        if rule.status_code != status_code:
            continue
        if re.search(rule.detail_pattern, detail, re.IGNORECASE):
            matching_rules.append(rule)
    
    if not matching_rules:
        return None
    
    # Return highest priority rule
    return max(matching_rules, key=lambda r: r.priority)


def generate_replacement(rule: ReplacementRule, detail: str, context: str = "") -> str:
    """Generate the replacement exception code."""
    resource_id = extract_resource_id(detail, context)
    
    # Build argument string
    args = rule.arg_template.format(
        detail=detail,
        resource_id=resource_id,
    )
    
    return f"raise {rule.exception_class}({args})"


def scan_file(file_path: Path) -> list[HTTPExceptionMatch]:
    """Scan a single file for HTTPException patterns."""
    matches = []
    content = file_path.read_text()
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        if 'raise HTTPException' in line:
            # Try to extract full statement (may span multiple lines)
            match = HTTPEXCEPTION_PATTERN.search(line)
            if match:
                status_code = int(match.group(1))
                detail = match.group(2).strip()
                
                # Find matching rule
                rule = find_matching_rule(status_code, detail)
                suggestion = None
                if rule:
                    suggestion = generate_replacement(rule, detail, line)
                
                matches.append(HTTPExceptionMatch(
                    file_path=str(file_path),
                    line_number=i,
                    status_code=status_code,
                    detail=detail,
                    full_match=match.group(0),
                    suggestion=suggestion,
                ))
    
    return matches


def get_required_imports(matches: list[HTTPExceptionMatch]) -> set[str]:
    """Get the set of exception classes needed for imports."""
    classes = set()
    for m in matches:
        if m.suggestion:
            # Extract class name from "raise ClassName(...)"
            class_name = m.suggestion.split('(')[0].replace('raise ', '').strip()
            classes.add(class_name)
    return classes


def generate_import_statement(classes: set[str]) -> str:
    """Generate the import statement for required exception classes."""
    if not classes:
        return ""
    sorted_classes = sorted(classes)
    if len(sorted_classes) <= 3:
        return f"from src.infra.core.exceptions import {', '.join(sorted_classes)}"
    else:
        class_list = ',\n    '.join(sorted_classes)
        return f"from src.infra.core.exceptions import (\n    {class_list},\n)"


def generate_report(all_matches: list[HTTPExceptionMatch]) -> str:
    """Generate a detailed migration report."""
    report = []
    report.append("# HTTPException Migration Report\n")
    report.append(f"**Total Instances Found:** {len(all_matches)}\n")
    
    # Group by status code
    by_status = {}
    for m in all_matches:
        by_status.setdefault(m.status_code, []).append(m)
    
    for status in sorted(by_status.keys()):
        matches = by_status[status]
        report.append(f"\n## Status {status} ({len(matches)} instances)\n")
        
        for m in matches[:10]:  # Limit for readability
            report.append(f"- **{Path(m.file_path).name}:{m.line_number}**")
            report.append(f"  - Before: `{m.full_match[:60]}...`")
            if m.suggestion:
                report.append(f"  - After: `{m.suggestion}`")
            report.append("")
        
        if len(matches) > 10:
            report.append(f"... and {len(matches) - 10} more\n")
    
    return '\n'.join(report)


def apply_fixes(file_path: Path, matches: list[HTTPExceptionMatch], dry_run: bool = True) -> str:
    """Apply fixes to a file."""
    content = file_path.read_text()
    
    # Sort matches by line number descending (to not shift positions)
    sorted_matches = sorted(matches, key=lambda m: m.line_number, reverse=True)
    
    for m in sorted_matches:
        if m.suggestion:
            content = content.replace(m.full_match, m.suggestion)
    
    # Check if we need to add imports
    needed_imports = get_required_imports(matches)
    if needed_imports:
        import_stmt = generate_import_statement(needed_imports)
        # Add after existing imports (simple heuristic)
        if 'from src.infra.core.exceptions import' not in content:
            # Find last import line
            lines = content.split('\n')
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    last_import_idx = i
            lines.insert(last_import_idx + 1, import_stmt)
            content = '\n'.join(lines)
    
    if not dry_run:
        file_path.write_text(content)
        return f"✅ Fixed {len(matches)} instances in {file_path.name}"
    else:
        return f"🔍 Would fix {len(matches)} instances in {file_path.name}"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulk fix HTTPException → AppException')
    parser.add_argument('files', nargs='*', help='Files to process')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes only')
    parser.add_argument('--all', action='store_true', help='Process all Python files in src/')
    parser.add_argument('--report', action='store_true', help='Generate report only')
    args = parser.parse_args()
    
    # Determine files to process
    src_dir = Path(__file__).parent.parent / 'src'
    
    if args.all:
        files = list(src_dir.rglob('*.py'))
    elif args.files:
        files = [Path(f) for f in args.files]
    else:
        files = list(src_dir.rglob('*.py'))
    
    # Scan all files
    all_matches = []
    for f in files:
        if f.exists():
            matches = scan_file(f)
            all_matches.extend(matches)
    
    if args.report:
        print(generate_report(all_matches))
        return
    
    # Apply fixes
    print(f"\n{'='*60}")
    print(f"HTTPException → AppException Migration")
    print(f"{'='*60}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'APPLY CHANGES'}")
    print(f"Files: {len(files)}")
    print(f"Total HTTPExceptions: {len(all_matches)}")
    print(f"{'='*60}\n")
    
    # Group by file
    by_file = {}
    for m in all_matches:
        by_file.setdefault(m.file_path, []).append(m)
    
    for file_path, matches in by_file.items():
        result = apply_fixes(Path(file_path), matches, dry_run=args.dry_run)
        print(result)
    
    print(f"\n{'='*60}")
    if args.dry_run:
        print("Run without --dry-run to apply changes")
    else:
        print("✅ Migration complete! Run type checker to verify.")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
