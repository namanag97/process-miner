#!/bin/bash
# Final sed-based fix for remaining HTTPExceptions

cd "$(dirname "$0")/.."

echo "Fixing final HTTPExceptions..."

# Filtering router - 404
perl -i -pe 's/raise HTTPException\(\s*status_code=404,\s*detail=f"Filtered log \{filtered_id\} not found.*?\)/raise NotFoundError(resource='\''Filtered Log'\'', resource_id=filtered_id)/s' \
  src/features/process_mining/filtering/router.py

# Operations router - 400  
perl -i -pe 's/raise HTTPException\(\s*status_code=400,\s*detail=f"Operation not completed.*?\)/raise BadRequestError(message=f"Operation not completed. Status: {desc.status.name if desc.status else '\''UNKNOWN'\''}")/s' \
  src/api/routers/operations.py

# Rate limiter - 429  
perl -i -pe 's/raise HTTPException\(\s*status_code=429,.*?headers=\{.*?\},.*?\)/from src.platform.core.exceptions import RateLimitError\n                raise RateLimitError(limit=requests, window_seconds=window, retry_after=retry_after)/s' \
  src/platform/infrastructure/rate_limiter.py

# Count after
AFTER=$(grep -r "raise HTTPException" src/ 2>/dev/null | grep -v "^#" | grep -v "//" | wc -l | xargs)
echo "Remaining: $AFTER"
