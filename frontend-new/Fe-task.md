# Frontend Task Backlog — MVP Core Flow Audit

> Last Updated: 2024-12-30T23:10:00+05:30
> Current Sprint Focus: **FIX CORE FLOW BREAKAGES**

---

## 🚨 EXECUTIVE SUMMARY: CORE FLOW IS BROKEN

The MVP flow is: **Upload File → See Log → Explore Process**

### What's Actually Broken Right Now

| Step               | Status            | Problem                                           |
| ------------------ | ----------------- | ------------------------------------------------- |
| 1. Upload File     | ⚠️ Mostly Working | No timeout indicator, stuck state unclear         |
| 2. See Log in List | ✅ Working        | Uses real SDK                                     |
| 3. View Log Detail | ✅ Working        | Uses real SDK                                     |
| 4. Go to Explorer  | 🔴 **BROKEN**     | User sees FAKE MOCK LOGS, not their uploaded file |
| 5. Explore Process | ✅ Working        | Uses real SDK (if you get there)                  |

**User Impact**: After uploading a file, user clicks "Explore Process" from sidebar and sees **fake demo logs** — their actual uploaded file is NOT visible. They cannot complete the core flow.

---

## 🔴 P0 — CORE FLOW BLOCKERS

### TASK-001: ProcessExplorerIndexPage Uses Mock Data — User Can't Find Their Log

**Status**: ⚪ Not Started
**Severity**: 🔴 CRITICAL — Core flow completely broken
**Depends On**: None
**Blocks**: Entire MVP demo capability

**Problem**:
After a user uploads a file via the Upload Wizard:

1. They can see it in `/processes` (EventLogsPage) — ✅ works
2. They can click "Explore Process" button in LogDetailPage → navigates to `/explorer/:logId` — ✅ works
3. BUT if they click "Explorer" in sidebar → they see `/explorer` (ProcessExplorerIndexPage)
4. **THIS PAGE SHOWS HARDCODED MOCK DATA** from lines 12-41
5. **User's real uploaded log IS NOT VISIBLE**

**Root Cause**:
`/src/pages/explorer/ProcessExplorerIndexPage.tsx` lines 12-41:

```tsx
const mockEventLogs = [
  { id: '1', name: 'Orders_2024.csv', ... },
  { id: '2', name: 'Claims_Process.xes', ... },
  // ... all fake data
];
```

**Why This Is Critical**:

- User will be confused why their file isn't showing
- User will click fake logs → ProcessExplorerPage tries to load `sdk.discovery.buildDFG('1')` → 404 error
- Complete dead end in the core user journey

**Fix**:

1. Import `useSDK` and `useQuery`
2. Replace `mockEventLogs` with real SDK call:
   ```tsx
   const { data, isLoading, error } = useQuery({
     queryKey: ['processes'],
     queryFn: () => sdk.processes.list({ pageSize: 50 }),
   });
   const logs = data?.items ?? [];
   ```
3. Add loading state (show skeleton cards while loading)
4. Add error state (show alert with retry if backend is down)
5. Empty state already exists and works

**Files to Modify**:

- `src/pages/explorer/ProcessExplorerIndexPage.tsx`
  - Remove `mockEventLogs` constant (lines 12-41)
  - Add SDK query hook
  - Replace `mockEventLogs` with `logs` from query
  - Add loading/error states

**Acceptance Criteria**:

- [ ] User uploads a file → goes to Explorer sidebar → sees their file in the list
- [ ] Clicking their file opens the correct process map
- [ ] Loading spinner shows while fetching
- [ ] Error state shows if backend is unavailable with "Retry" button
- [ ] Empty state shows "No logs, upload one" when appropriate

**References**:

- Same pattern used in: `EventLogsPage.tsx` lines 56-61 (working example)

---

### TASK-002: Upload Progress Bar Shows Fake 50% — No Real Backend Progress

**Status**: ⚪ Not Started  
**Severity**: 🟠 HIGH — User has no idea what's happening
**Depends On**: None
**Blocks**: None

**Problem**:
When user clicks "Process" on upload step 3, the progress bar shows:

- `percent={ingestMutation.isPending ? 50 : 100}` (line 338)
- This is FAKE — it just shows 50% while pending, 100% when done
- For large files, user sees 50% for potentially minutes with no feedback
- User may think it's stuck, refresh the page, lose their progress

**Root Cause**:
`UploadWizardPage.tsx` line 337-340:

```tsx
<Progress
  percent={ingestMutation.isPending ? 50 : 100}
  status={ingestMutation.isPending ? 'active' : 'success'}
/>
```

**What Should Happen**:

- Either show indeterminate spinner ("Processing...") with estimated time
- Or show real progress if backend supports progress events
- Or show staged progress: "Uploading... → Parsing... → Analyzing..."

**Fix Options**:

**Option A (Simple — recommended for MVP)**:
Replace progress bar with indeterminate spinner + status text:

```tsx
<div style={{ textAlign: 'center' }}>
  <Spin size="large" />
  <Title level={4}>Processing your file...</Title>
  <Text type="secondary">This may take a few moments for larger files</Text>
</div>
```

**Option B (Better UX — if backend supports)**:
Add SSE/WebSocket for real progress updates from backend

**Files to Modify**:

- `src/pages/logs/UploadWizardPage.tsx` lines 333-348

**Acceptance Criteria**:

- [ ] User sees clear "processing" indicator
- [ ] User doesn't think app is stuck
- [ ] After ~15 seconds, show "Still processing large file..." message
- [ ] Error state is clear with retry option (already exists)

---

### TASK-003: No Global "Backend Unavailable" Indicator

**Status**: ⚪ Not Started
**Severity**: 🟠 HIGH — User doesn't know why nothing works
**Depends On**: None
**Blocks**: None

**Problem**:
If the backend server is down (not running on port 8001):

1. SDK has retry logic with 30 second timeout — good
2. SDK throws clean error "Unable to reach the backend server" — good
3. **Individual pages show error but there's no GLOBAL indicator**
4. User might navigate to 5 different pages all failing with no clear pattern
5. User has no idea the backend is down vs each feature being broken

**What Should Happen**:

- When first API call fails with network error → show persistent banner at top
- Banner: "⚠️ Cannot connect to server. Check that backend is running. [Retry]"
- Banner should persist across page navigation until connection restored
- Auto-retry periodically + manual retry button

**Current Behavior**:
Each page independently shows `<Alert message="Failed to load..." />` — user has to discover this on every page

**Fix**:

1. Add `BackendHealthContext` provider in App.tsx
2. On first network error, set `isBackendDown = true`
3. When `isBackendDown`, show persistent top banner in AppShell
4. Banner has "Retry" button that calls `sdk.checkHealth()`
5. If health check passes, clear banner and refetch queries

**Files to Create**:

- `src/context/BackendHealthContext.tsx` — context for health state

**Files to Modify**:

- `src/App.tsx` — add BackendHealthProvider
- `libs/shared/design-system/src/components/AppShell.tsx` — add banner slot
- SDK already has `checkHealth()` method (line 67-77)

**Acceptance Criteria**:

- [ ] Backend not running → persistent banner appears after first failed request
- [ ] User sees ONE clear message, not 5 different page errors
- [ ] "Retry" button tests connection and clears banner if successful
- [ ] After backend comes back, data automatically refreshes

---

### TASK-004: Clicking Fake Log in Explorer → 404 Error with No Recovery

**Status**: ⚪ Not Started
**Severity**: 🟠 HIGH — Dead end in user journey
**Depends On**: TASK-001 (but still important to understand)
**Blocks**: None

**Problem**:
Right now (before TASK-001 fix), if user clicks a mock log card:

1. Navigates to `/explorer/1` (fake ID)
2. `sdk.processes.get('1')` → 404 from backend
3. `sdk.discovery.buildDFG('1')` → 404 from backend
4. Page shows error state: "Failed to load process map"
5. **But error message doesn't explain the file doesn't exist**
6. User might think the system is broken vs "log not found"

**Root Cause**:
ProcessExplorerPage.tsx line 481-500 shows generic error without distinguishing 404 vs network error

**Fix**:

1. Check if error is 404 specifically
2. If 404: "This event log was not found. It may have been deleted. [Go to Event Logs]"
3. If network error: "Unable to connect to server. [Retry]"
4. If other: current behavior

**Files to Modify**:

- `src/pages/explorer/ProcessExplorerPage.tsx` lines 481-500

**Acceptance Criteria**:

- [ ] 404 error → shows "Log not found, go back" message
- [ ] Network error → shows "Server unavailable, retry" message
- [ ] User can recover without getting stuck

---

## 🟠 P1 — User Experience Gaps in Core Flow

### TASK-005: Upload Wizard — No Cancel Confirmation

**Status**: ⚪ Not Started
**Depends On**: None

**Problem**:
User is mid-upload at step 2 or 3. They click "Cancel" or navigate away. Everything is lost without warning.

**Fix**:
Add `beforeunload` event and React Router blocker when form is dirty.

---

### TASK-006: Upload Wizard — Stuck on Column Detection

**Status**: ⚪ Not Started
**Depends On**: None

**Problem**:
If `detectColumnsMutation` hangs (backend slow or file very large):

- User sees "Detecting columns..." in upload zone
- Upload zone is disabled
- No way to cancel or reset
- No timeout indication

**Current Code** (`UploadWizardPage.tsx` line 173-179):

```tsx
disabled={detectColumnsMutation.isPending}
...
{detectColumnsMutation.isPending ? 'Detecting columns...' : 'Drag & drop your file here'}
```

**Fix**:

1. Add cancel button when `isPending`
2. Add timeout warning after 30 seconds
3. Add "Try a smaller file" suggestion

---

### TASK-007: Upload Wizard — What If Wrong Column Selected?

**Status**: ⚪ Not Started
**Depends On**: None

**Problem**:
User selects wrong column for Case ID. Process completes "successfully" but resulting process map is garbage. User doesn't know why until much later.

**What Should Happen**:

- After column selection, show validation:
  - "Case ID column has 1,250 unique values — looks reasonable ✓"
  - "Activity column has 45 unique values — looks reasonable ✓"
  - "Timestamp format detected: YYYY-MM-DD HH:mm:ss ✓"
- If Case ID has only 3 values → warning: "Very few case IDs. Are you sure?"
- If Activity has 10,000 values → warning: "Very many activities. Check this is correct."

**Fix**:
Add validation summary card after column mapping step before processing.

---

### TASK-008: Log Detail Page — "Open in Explorer" Works, but "View Analytics" Goes Nowhere

**Status**: ⚪ Not Started
**Depends On**: None

**Problem**:
`LogDetailPage.tsx` line 250-254:

```tsx
<Button onClick={() => navigate(`/analytics?logId=${logId}`)}>
  View Analytics
</Button>
```

But `AnalyticsPage` doesn't read `logId` from query params. User clicks → goes to analytics → doesn't see their log's data.

**Fix**:

1. AnalyticsPage should read `?logId=` from URL
2. Show log selector defaulting to the logId in URL
3. Or remove the button until analytics properly supports log selection

---

### TASK-009: After Successful Upload — User Wants to See Process Map Immediately

**Status**: ⚪ Not Started
**Depends On**: None

**Problem**:
After upload success (line 303-311):

```tsx
<Button type="primary" onClick={handleViewLog}>
  View Event Log
</Button>
```

This takes user to Log Detail page. But the **core action** they want is **see their process map**.

**Fix**:
Add primary CTA: "Explore Process" that goes straight to `/explorer/${uploadedLogId}`
Make "View Event Log" secondary.

---

## 🟢 P2 — Polish (After Core Flow Works)

### TASK-010: HomePage Uses Mock Data

Same as previously identified. Not blocking core flow but inconsistent.

### TASK-011: Add Error Boundaries

Previously identified. Important for crash recovery.

### TASK-012: Download Feature

Previously identified. Not blocking MVP.

---

## 📊 Execution Priority

### Immediate (Today/Tomorrow)

1. **TASK-001**: Fix ProcessExplorerIndexPage mock data — ~30 min
2. **TASK-002**: Fix upload progress indicator — ~15 min
3. **TASK-003**: Add backend unavailable banner — ~1 hour

### This Week

4. **TASK-004**: Better 404 handling in Explorer — ~20 min
5. **TASK-006**: Upload wizard cancel/timeout — ~30 min
6. **TASK-009**: Add "Explore Process" button after upload — ~5 min

### Next Week

7. **TASK-007**: Column validation summary
8. **TASK-008**: Analytics log selection

---

## 🧪 Testing the Core Flow

After fixes, manually test:

1. **Start Backend**: `cd backend && uvicorn api.main:app --reload --port 8001`
2. **Start Frontend**: `npm run start`
3. **Login**: Use any email/password or "Continue as Guest"
4. **Upload Flow**:
   - Navigate to Event Logs → Upload File
   - Upload a CSV with case_id, activity, timestamp columns
   - Map columns correctly
   - Click Process
   - **VERIFY**: Processing indicator is clear, not fake 50%
5. **After Upload**:
   - Click "View Event Log" → verify log details show
   - Click "Explore Process" button → verify process map loads
6. **Explorer Flow**:
   - Click "Explorer" in sidebar
   - **VERIFY**: Your uploaded file appears in the list (not mock data!)
   - Click your file → verify process map loads correctly
7. **Error Handling**:
   - Stop backend (`Ctrl+C`)
   - Navigate to any page
   - **VERIFY**: Error message is clear, not silent failure
   - **VERIFY**: Retry button works when backend restarts

---

## 📋 Task Index

| ID       | Title                                 | Priority | Impact             |
| -------- | ------------------------------------- | -------- | ------------------ |
| TASK-001 | ExplorerIndex uses mock data          | P0       | Core flow broken   |
| TASK-002 | Upload progress fake 50%              | P0       | User confusion     |
| TASK-003 | No backend unavailable banner         | P0       | User confusion     |
| TASK-004 | 404 error unclear in Explorer         | P1       | Dead end           |
| TASK-005 | No cancel confirmation in upload      | P1       | Data loss          |
| TASK-006 | Column detection can get stuck        | P1       | Dead end           |
| TASK-007 | No column validation feedback         | P1       | Garbage results    |
| TASK-008 | Analytics doesn't read logId param    | P1       | Feature incomplete |
| TASK-009 | No "Explore Process" CTA after upload | P1       | UX friction        |
| TASK-010 | HomePage mock data                    | P2       | Inconsistency      |
| TASK-011 | Error boundaries                      | P2       | Crash recovery     |
| TASK-012 | Download feature                      | P2       | Feature incomplete |

---

_Audit focused on MVP core flow: Upload → Explore_
_Generated by Sprint Planner after deep code trace_
