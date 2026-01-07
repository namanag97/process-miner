#!/bin/bash
# Final batch fix for remaining HTTPExceptions

cd "$(dirname "$0")/.."

echo "Fixing remaining HTTPExceptions..."

# Count before
BEFORE=$(grep -r "raise HTTPException" src/ 2 | wc -l | tr -d ' ')
echo "Before: $BEFORE"

# Fix visualization 409 (the stubborn one) 
sed -i.bak '399,404s/raise HTTPException(/raise ConflictError(/; 399,404s/status_code=409,/message=/; 399,404s/detail=//' \
    src/features/process_mining/visualization/router.py

# Fix workflows router (401/500)
sed -i.bak 's/raise HTTPException(status_code=401, detail=\([^)]*\))/raise AuthenticationError(message=\1)/g' \
    src/features/process_mining/workflows/router.py
sed -i.bak 's/raise HTTPException(status_code=500, detail=\([^)]*\))/raise ProcessingError(message=\1)/g' \
    src/features/process_mining/workflows/router.py

# Fix operations.py
sed -i.bak 's/raise HTTPException(status_code=500, detail=\([^)]*\))/raise ProcessingError(message=\1)/g' \
    src/api/routers/operations.py

# Cleanup backups
find src/ -name "*.bak" -delete

# Count after  
AFTER=$(grep -r "raise HTTPException" src/ 2>/dev/null | wc -l | tr -d ' ')
echo "After: $AFTER"
echo "Fixed: $((BEFORE - AFTER))"

echo "✅ Batch fix complete"
