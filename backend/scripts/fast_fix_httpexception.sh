#!/bin/bash
# ============================================================================
# FAST HTTPException → AppException Migration Script
# ============================================================================
# 
# This script uses sed for FAST bulk replacement of common patterns.
# Run the Python script for more complex/edge cases.
#
# Usage:
#   ./scripts/fast_fix_httpexception.sh --dry-run   # Preview changes
#   ./scripts/fast_fix_httpexception.sh             # Apply changes
#
# ============================================================================

set -e
cd "$(dirname "$0")/.."

DRY_RUN=false
if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
    echo "🔍 DRY RUN MODE - No changes will be made"
fi

echo "=============================================="
echo "HTTPException Fast Fix Script"
echo "=============================================="

# Count before
BEFORE=$(grep -r "raise HTTPException" src/ 2>/dev/null | wc -l | tr -d ' ')
echo "📊 HTTPExceptions before: $BEFORE"
echo ""

# ============================================================================
# PHASE 1: Fix 404 Not Found (simplest patterns)
# ============================================================================
echo "🔧 Phase 1: Fixing 404 Not Found patterns..."

FILES_404=$(grep -rl "HTTPException.*404" src/ 2>/dev/null || true)

for PATTERN in \
    's/raise HTTPException(status_code=404, detail="Event log not found")/raise NotFoundError(resource="Event Log", resource_id=dataset_id)/g' \
    's/raise HTTPException(status_code=404, detail="Dataset not found")/raise NotFoundError(resource="Dataset", resource_id=dataset_id)/g' \
    's/raise HTTPException(status_code=404, detail="Analysis not found")/raise NotFoundError(resource="Analysis", resource_id=analysis_id)/g' \
    's/raise HTTPException(status_code=404, detail="OCEL log not found")/raise NotFoundError(resource="OCEL Log", resource_id=ocel_id)/g' \
    's/raise HTTPException(status_code=404, detail="OC-PN model not found")/raise NotFoundError(resource="OC-PN Model", resource_id=model_id)/g' \
    's/raise HTTPException(status_code=404, detail="Conformance result not found")/raise NotFoundError(resource="Conformance Result", resource_id=result_id)/g' \
    's/raise HTTPException(status_code=404, detail="Project not found")/raise ProjectNotFoundError(project_id=project_id)/g' \
    's/raise HTTPException(status_code=404, detail="Process model not found")/raise ModelNotFoundError(model_id=model_id)/g' \
    's/raise HTTPException(status_code=404, detail="Workspace not found")/raise NotFoundError(resource="Workspace", resource_id=workspace_id)/g'
do
    if [ "$DRY_RUN" == "true" ]; then
        grep -rn "$(echo $PATTERN | cut -d'/' -f2)" src/ 2>/dev/null | head -3 || true
    else
        for f in $FILES_404; do
            sed -i.bak "$PATTERN" "$f" 2>/dev/null || true
        done
    fi
done

# ============================================================================
# PHASE 2: Fix 500 Processing Errors
# ============================================================================
echo "🔧 Phase 2: Fixing 500 Processing errors..."

FILES_500=$(grep -rl "HTTPException.*500" src/ 2>/dev/null || true)

# These are trickier - use simpler patterns
if [ "$DRY_RUN" == "true" ]; then
    echo "  Would replace HTTPException(status_code=500, detail=f\"...) → ProcessingError(message=f\"...)"
    grep -rn "HTTPException.*500.*detail" src/ 2>/dev/null | head -5 || true
else
    for f in $FILES_500; do
        # Replace: raise HTTPException(status_code=500, detail=X) → raise ProcessingError(message=X)
        sed -i.bak 's/raise HTTPException(status_code=500, detail=\([^)]*\))/raise ProcessingError(message=\1)/g' "$f" 2>/dev/null || true
    done
fi

# ============================================================================
# PHASE 3: Fix 400 Bad Request
# ============================================================================
echo "🔧 Phase 3: Fixing 400 Bad Request patterns..."

FILES_400=$(grep -rl "HTTPException.*400" src/ 2>/dev/null || true)

if [ "$DRY_RUN" == "true" ]; then
    echo "  Would replace HTTPException(status_code=400, detail=...) → BadRequestError(message=...)"  
    grep -rn "HTTPException.*400" src/ 2>/dev/null | head -5 || true
else
    for f in $FILES_400; do
        sed -i.bak 's/raise HTTPException(status_code=400, detail=\([^)]*\))/raise BadRequestError(message=\1)/g' "$f" 2>/dev/null || true
    done
fi

# ============================================================================
# PHASE 4: Fix 409 Conflict
# ============================================================================
echo "🔧 Phase 4: Fixing 409 Conflict patterns..."

FILES_409=$(grep -rl "HTTPException.*409" src/ 2>/dev/null || true)

if [ "$DRY_RUN" == "true" ]; then
    grep -rn "HTTPException.*409" src/ 2>/dev/null | head -3 || true
else
    for f in $FILES_409; do
        sed -i.bak 's/raise HTTPException(status_code=409, detail=\([^)]*\))/raise ConflictError(message=\1)/g' "$f" 2>/dev/null || true
    done
fi

# ============================================================================
# PHASE 5: Add imports (simplified)
# ============================================================================
echo "🔧 Phase 5: Adding missing imports..."

# This needs to be smarter - check what exceptions are used in each file
# For now, just show what files need updates
echo "  Files needing import updates:"
grep -rl "NotFoundError\|ProcessingError\|BadRequestError\|ConflictError" src/ 2>/dev/null | \
    xargs -I{} sh -c 'grep -L "from src.platform.core.exceptions import" {} 2>/dev/null' | head -10

# ============================================================================
# CLEANUP
# ============================================================================
if [ "$DRY_RUN" == "false" ]; then
    echo ""
    echo "🧹 Cleaning up backup files..."
    find src/ -name "*.bak" -delete 2>/dev/null || true
fi

# Count after
AFTER=$(grep -r "raise HTTPException" src/ 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo "=============================================="
echo "📊 HTTPExceptions after: $AFTER"
echo "📈 Reduced by: $((BEFORE - AFTER))"
echo "=============================================="

if [ "$DRY_RUN" == "true" ]; then
    echo ""
    echo "Run without --dry-run to apply changes"
fi
