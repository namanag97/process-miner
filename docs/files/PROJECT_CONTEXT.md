# PROJECT CONTEXT - PROCESS MINING SAAS PLATFORM
# Include this file with EVERY AI code generation prompt

## Project Overview
- **Name**: Process Mining SaaS Platform
- **Stage**: MVP
- **Stack**: [FILL IN: e.g., Next.js 14, FastAPI/Express, PostgreSQL, Redis]

---

## CRITICAL RULES FOR AI CODE GENERATION

### 1. Database Rules
```
✅ ALWAYS filter by `deleted_at IS NULL` in queries
✅ ALWAYS use parameterized queries (never string concatenation)
✅ ALWAYS use UUIDs for IDs (uuid_generate_v4())
✅ Timestamps are auto-managed by triggers (created_at, updated_at)
❌ NEVER write raw SQL without deleted_at filter
❌ NEVER hardcode IDs or use sequential integers
```

**Example Query Pattern:**
```typescript
// ✅ CORRECT
const workspaces = await db.query(`
  SELECT * FROM workspaces 
  WHERE organization_id = $1 
  AND deleted_at IS NULL
  ORDER BY created_at DESC
`, [orgId]);

// ❌ WRONG - Missing deleted_at filter
const workspaces = await db.query(`
  SELECT * FROM workspaces WHERE organization_id = $1
`, [orgId]);
```

### 2. API Response Rules
```
✅ ALWAYS wrap responses in ApiResponse<T> format
✅ ALWAYS return appropriate HTTP status codes
✅ ALWAYS validate input before processing
✅ ALWAYS check authorization before business logic
❌ NEVER return raw data without wrapper
❌ NEVER skip input validation
```

**Response Format:**
```typescript
// Success
{
  "success": true,
  "data": { ... },
  "meta": { "timestamp": "...", "requestId": "..." }
}

// Error
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human readable message",
    "details": { "email": ["Invalid format"] }
  }
}
```

**HTTP Status Codes:**
- 200: Success (GET, PATCH)
- 201: Created (POST)
- 204: No Content (DELETE)
- 400: Bad Request (validation errors)
- 401: Unauthorized (not logged in)
- 403: Forbidden (no permission)
- 404: Not Found
- 409: Conflict (duplicate)
- 429: Rate Limited
- 500: Internal Server Error

### 3. Authorization Rules
```
✅ ALWAYS check org membership first
✅ THEN check workspace membership if applicable
✅ THEN verify role has required permission
✅ Use the WORKSPACE_ACTION_REQUIRED_ROLES from shared.ts
```

**Authorization Flow:**
```typescript
// 1. User must be authenticated
if (!currentUser) throw new UnauthorizedError();

// 2. User must be org member
const orgMember = await getOrgMember(currentUser.id, orgId);
if (!orgMember) throw new ForbiddenError('NOT_MEMBER');

// 3. For workspace resources, check workspace membership
const wsMember = await getWorkspaceMember(currentUser.id, workspaceId);
if (!wsMember) throw new ForbiddenError('NOT_MEMBER');

// 4. Check role has permission
if (!canPerformWorkspaceAction(wsMember.role, 'project.create')) {
  throw new ForbiddenError('INSUFFICIENT_ROLE');
}
```

### 4. Frontend Rules
```
✅ ALWAYS use shared types from types/shared.ts
✅ ALWAYS handle: loading, error, empty, success states
✅ ALWAYS use the api-client for HTTP calls
✅ ALWAYS show toast notifications for mutations
❌ NEVER use 'any' type
❌ NEVER use inline styles (use Tailwind)
❌ NEVER skip error handling
```

**Component State Pattern:**
```tsx
// ✅ CORRECT - All states handled
function WorkspaceList() {
  const { data, isLoading, error } = useWorkspaces();
  
  if (isLoading) return <Skeleton />;
  if (error) return <ErrorState error={error} onRetry={refetch} />;
  if (!data?.length) return <EmptyState onCreate={...} />;
  
  return <List items={data} />;
}
```

### 5. Error Handling
```
✅ Backend: Throw typed AppError, catch at middleware
✅ Frontend: Use error boundaries + toast notifications
✅ ALWAYS log errors with context
❌ NEVER silently swallow errors
❌ NEVER use generic catch without handling
```

---

## NAMING CONVENTIONS

| Context | Convention | Example |
|---------|------------|---------|
| Database columns | snake_case | organization_id, created_at |
| API JSON fields | camelCase | organizationId, createdAt |
| File names | kebab-case | workspace-service.ts |
| React components | PascalCase | WorkspaceList.tsx |
| Constants | UPPER_SNAKE | MAX_FILE_SIZE |
| Functions | camelCase | getWorkspaceById |
| CSS classes | Tailwind | className="flex gap-4" |

---

## FILE REFERENCES

When generating code, reference these files:

1. **Database Schema**: `schema.sql`
   - All table definitions
   - Column types and constraints
   - Indexes

2. **Shared Types**: `src/types/shared.ts`
   - All TypeScript types
   - Enums matching database
   - Validation rules
   - Plan limits

3. **This Context**: `PROJECT_CONTEXT.md`
   - Coding rules
   - Patterns to follow

---

## CODE GENERATION CHECKLIST

Before accepting AI-generated code, verify:

### Database/Repository Layer
- [ ] Uses `deleted_at IS NULL` filter?
- [ ] Uses parameterized queries?
- [ ] Column names match schema.sql?
- [ ] Returns proper types from shared.ts?
- [ ] Handles null/undefined cases?

### API/Controller Layer
- [ ] Input validation with Zod present?
- [ ] Auth check before business logic?
- [ ] Returns ApiResponse wrapper?
- [ ] Correct HTTP status codes?
- [ ] Errors caught and formatted?

### Frontend/Component Layer
- [ ] Loading state handled?
- [ ] Error state handled?
- [ ] Empty state handled?
- [ ] Uses types from shared.ts?
- [ ] No 'any' types?
- [ ] Uses api-client for HTTP?
- [ ] Toast on mutation success/error?

### General
- [ ] No hardcoded values?
- [ ] No console.log left behind?
- [ ] Follows naming conventions?
- [ ] No security issues?

---

## PROMPT TEMPLATES

### For Repository/Database Layer
```
Context: [Paste this PROJECT_CONTEXT.md]

Task: Create the [Entity]Repository class

Requirements:
1. Implement: findById, findBy[Parent], create, update, softDelete
2. All queries filter by deleted_at IS NULL
3. Use parameterized queries only
4. Return types from shared.ts

Schema for this entity:
[Paste relevant table from schema.sql]

Generate ONLY the repository class.
```

### For API Endpoints
```
Context: [Paste this PROJECT_CONTEXT.md]

Task: Create [Entity] API router/controller

Requirements:
1. Implement CRUD endpoints
2. Validate input with Zod
3. Check authorization
4. Return ApiResponse format
5. Use [Entity]Repository (assume exists)

Generate the complete router file.
```

### For React Components
```
Context: [Paste this PROJECT_CONTEXT.md]

Task: Create [Component] React component

Requirements:
1. Handle: loading, error, empty, success states
2. Use shared types
3. Use Tailwind for styling
4. Use api-client for HTTP calls
5. Show toast notifications

Generate the component file.
```

---

## COMMON PATTERNS TO FOLLOW

### Soft Delete Pattern
```typescript
// Repository
async softDelete(id: string): Promise<void> {
  await db.query(`
    UPDATE workspaces 
    SET deleted_at = CURRENT_TIMESTAMP 
    WHERE id = $1 AND deleted_at IS NULL
  `, [id]);
}

// All reads filter by deleted_at
async findById(id: string): Promise<Workspace | null> {
  const result = await db.query(`
    SELECT * FROM workspaces 
    WHERE id = $1 AND deleted_at IS NULL
  `, [id]);
  return result.rows[0] || null;
}
```

### API Error Handling Pattern
```typescript
// Middleware catches all errors
app.use((err, req, res, next) => {
  if (err instanceof AppError) {
    return res.status(err.httpCode).json({
      success: false,
      error: {
        code: err.code,
        message: err.message,
        details: err.details
      }
    });
  }
  
  // Unknown error
  logger.error(err);
  return res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred'
    }
  });
});
```

### Frontend Data Fetching Pattern
```typescript
// Custom hook with proper typing
function useWorkspaces(orgId: string) {
  return useQuery({
    queryKey: ['workspaces', orgId],
    queryFn: () => api.get<Workspace[]>(`/workspaces?orgId=${orgId}`),
  });
}

// Component usage
function WorkspaceList({ orgId }: { orgId: string }) {
  const { data, isLoading, error, refetch } = useWorkspaces(orgId);
  
  if (isLoading) return <WorkspacesSkeleton />;
  if (error) return <ErrorState error={error} onRetry={refetch} />;
  if (!data?.length) return <EmptyWorkspaces onCreate={openModal} />;
  
  return (
    <div className="grid gap-4">
      {data.map(ws => <WorkspaceCard key={ws.id} workspace={ws} />)}
    </div>
  );
}
```
