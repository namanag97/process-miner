#!/bin/bash
# Nuclear Cleanup Script - Frontend Radical Simplification
# Deletes ~470 unused files and consolidates the codebase

set -e
cd "$(dirname "$0")/.."

echo "🔥 NUCLEAR CLEANUP - Frontend Radical Simplification"
echo "======================================================"

# Count before
BEFORE=$(find . -type f \( -name "*.ts" -o -name "*.tsx" \) | wc -l | tr -d ' ')
echo "📊 Files before cleanup: $BEFORE"

# Phase 1: Delete libs/ directory (280 files - 0 imports)
echo ""
echo "🗑️  Phase 1: Deleting libs/ directory..."
if [ -d "libs" ]; then
    LIBS_COUNT=$(find libs -type f | wc -l | tr -d ' ')
    rm -rf libs/
    echo "   ✅ Deleted libs/ ($LIBS_COUNT files)"
else
    echo "   ⏭️  libs/ already deleted"
fi

# Phase 1b: Delete src/api/generated/ directory (173 files - 0 imports)
echo ""
echo "🗑️  Phase 1b: Deleting src/api/generated/..."
if [ -d "src/api/generated" ]; then
    GEN_COUNT=$(find src/api/generated -type f | wc -l | tr -d ' ')
    rm -rf src/api/generated/
    echo "   ✅ Deleted src/api/generated/ ($GEN_COUNT files)"
else
    echo "   ⏭️  src/api/generated/ already deleted"
fi

# Phase 1c: Delete .storybook infrastructure
echo ""
echo "🗑️  Phase 1c: Deleting Storybook infrastructure..."
if [ -d ".storybook" ]; then
    rm -rf .storybook/
    echo "   ✅ Deleted .storybook/"
else
    echo "   ⏭️  .storybook/ already deleted"
fi

# Delete all .stories.tsx files
STORIES_COUNT=$(find . -name "*.stories.tsx" 2>/dev/null | wc -l | tr -d ' ')
if [ "$STORIES_COUNT" -gt 0 ]; then
    find . -name "*.stories.tsx" -delete
    echo "   ✅ Deleted $STORIES_COUNT .stories.tsx files"
else
    echo "   ⏭️  No .stories.tsx files found"
fi

# Delete tsconfig.storybook.json
if [ -f "tsconfig.storybook.json" ]; then
    rm tsconfig.storybook.json
    echo "   ✅ Deleted tsconfig.storybook.json"
fi

# Phase 1d: Delete unused template directory
echo ""
echo "🗑️  Phase 1d: Deleting unused template..."
if [ -d "src/features/_template" ]; then
    rm -rf src/features/_template/
    echo "   ✅ Deleted src/features/_template/"
else
    echo "   ⏭️  src/features/_template/ already deleted"
fi

# Count after
AFTER=$(find . -type f \( -name "*.ts" -o -name "*.tsx" \) | wc -l | tr -d ' ')
echo ""
echo "======================================================"
echo "📊 Files after cleanup: $AFTER"
echo "🎯 Files removed: $((BEFORE - AFTER))"
echo "✨ Reduction: $(( (BEFORE - AFTER) * 100 / BEFORE ))%"
echo ""
echo "🚀 Nuclear cleanup complete!"
