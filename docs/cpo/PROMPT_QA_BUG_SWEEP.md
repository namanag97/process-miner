# QA TASK: Full Bug Sweep

## Your Mission

Find EVERY bug across the entire application. This is not flow-specific — this is a comprehensive sweep of everything that's broken.

---

## Bug Hunting Checklist

### Console Errors (DevTools → Console)

Navigate to each page and check for:

- [ ] JavaScript errors (red)
- [ ] Warnings (yellow) — note but lower priority
- [ ] Network failures logged

**Pages to check:**

- [ ] Login page
- [ ] Home/Dashboard
- [ ] Workspace list
- [ ] Project list
- [ ] Upload wizard
- [ ] Log detail
- [ ] Process Explorer
- [ ] Any other accessible pages

### Network Errors (DevTools → Network)

Check for:

- [ ] 4xx errors (400, 401, 403, 404)
- [ ] 5xx errors (500, 502, 503)
- [ ] Requests that hang (pending forever)
- [ ] CORS errors

### UI/UX Issues

**Spinners that never resolve:**

- [ ] Loading states that hang indefinitely
- [ ] Progress indicators that don't complete
- [ ] "Please wait" that never finishes

**Buttons that don't work:**

- [ ] Click produces no response
- [ ] Click produces error
- [ ] Disabled buttons with no explanation

**Links that go nowhere:**

- [ ] 404 pages
- [ ] Broken navigation
- [ ] Dead links

**Empty states:**

- [ ] Blank pages where data should show
- [ ] Missing content
- [ ] "No data" when data exists

**Form issues:**

- [ ] Validation not working
- [ ] Submit button disabled incorrectly
- [ ] Error messages not appearing
- [ ] Success messages not appearing

---

## Bug Inventory Table

| Bug ID  | Page/Location | Type | Description | Severity | Console Error | Network Error | Repro Steps |
| ------- | ------------- | ---- | ----------- | -------- | ------------- | ------------- | ----------- |
| BUG-001 |               |      |             |          |               |               |             |
| BUG-002 |               |      |             |          |               |               |             |
| BUG-003 |               |      |             |          |               |               |             |
| ...     |               |      |             |          |               |               |             |

### Type Categories:

- `JS_ERROR` - JavaScript exception
- `API_FAIL` - Network request fails
- `UI_BROKEN` - Button/link doesn't work
- `HANG` - Infinite loading
- `EMPTY` - Missing expected content
- `VALIDATION` - Form validation issue
- `NAV` - Navigation broken
- `UX` - Confusing behavior (works but wrong)

### Severity:

- **P0** - Completely blocks a core flow
- **P1** - Major feature broken
- **P2** - Minor issue, workaround exists
- **P3** - Cosmetic/polish

---

## Priority Summary

After completing sweep, summarize:

| Priority      | Count | Sample Issues |
| ------------- | ----- | ------------- |
| P0 (Blocking) |       |               |
| P1 (Major)    |       |               |
| P2 (Minor)    |       |               |
| P3 (Cosmetic) |       |               |
| **TOTAL**     |       |               |

---

## Top 10 Bugs (Ranked by Impact)

List the 10 most important bugs to fix for MVP:

| Rank | Bug ID | Summary | Why it matters |
| ---- | ------ | ------- | -------------- |
| 1    |        |         |                |
| 2    |        |         |                |
| 3    |        |         |                |
| 4    |        |         |                |
| 5    |        |         |                |
| 6    |        |         |                |
| 7    |        |         |                |
| 8    |        |         |                |
| 9    |        |         |                |
| 10   |        |         |                |

---

## Page-by-Page Health Report

| Page             | Works?   | Bugs Found | Notes |
| ---------------- | -------- | ---------- | ----- |
| Login            | ✅/⚠️/❌ |            |       |
| Dashboard        |          |            |       |
| Workspace List   |          |            |       |
| Project List     |          |            |       |
| Upload Wizard    |          |            |       |
| Log Detail       |          |            |       |
| Process Explorer |          |            |       |
| Other:           |          |            |       |

---

## Overall Application Health

Based on this sweep:

- **Total Bugs Found:** \_\_
- **P0 Bugs:** \_\_
- **P1 Bugs:** \_\_
- **Estimated Fix Time:** (CTO to assess)
- **Demo Ready?:** YES / WITH WORKAROUNDS / NO

---

## Report To

**Deliver to:** CPO
**Update:** `/docs/cpo/CPO_KNOWLEDGE_BASE.md` → Bug Inventory section
