# Platform Feature Checklist
# Copy this to your project management tool (Notion, Linear, etc.)
# Status: [ ] Not Started, [~] In Progress, [x] Done

## Phase 1: Foundation (Week 1)
### Database & Setup
- [ ] Run schema.sql on PostgreSQL
- [ ] Verify all tables created
- [ ] Create seed data script
- [ ] Set up migration tool (e.g., Flyway, Prisma)
- [ ] Configure environment variables
- [ ] Set up logging infrastructure

### Authentication
- [ ] POST /api/v1/auth/register
- [ ] POST /api/v1/auth/login
- [ ] POST /api/v1/auth/logout
- [ ] POST /api/v1/auth/refresh
- [ ] POST /api/v1/auth/forgot-password
- [ ] POST /api/v1/auth/reset-password
- [ ] POST /api/v1/auth/verify-email
- [ ] GET /api/v1/auth/me
- [ ] Auth middleware (JWT validation)
- [ ] Session management

### Base Infrastructure
- [ ] ApiResponse wrapper utility
- [ ] Error handling middleware
- [ ] Request logging middleware
- [ ] Validation utilities (Zod schemas)
- [ ] Base repository class
- [ ] Database connection pool

---

## Phase 2: Core Entities (Week 2)
### Organizations
- [ ] GET /api/v1/organizations
- [ ] POST /api/v1/organizations
- [ ] GET /api/v1/organizations/:id
- [ ] PATCH /api/v1/organizations/:id
- [ ] DELETE /api/v1/organizations/:id
- [ ] GET /api/v1/organizations/:id/members
- [ ] PATCH /api/v1/organizations/:id/members/:userId
- [ ] DELETE /api/v1/organizations/:id/members/:userId
- [ ] Organization context middleware

### Workspaces
- [ ] GET /api/v1/workspaces
- [ ] POST /api/v1/workspaces
- [ ] GET /api/v1/workspaces/:id
- [ ] PATCH /api/v1/workspaces/:id
- [ ] DELETE /api/v1/workspaces/:id
- [ ] GET /api/v1/workspaces/:id/members
- [ ] POST /api/v1/workspaces/:id/members
- [ ] PATCH /api/v1/workspaces/:id/members/:userId
- [ ] DELETE /api/v1/workspaces/:id/members/:userId
- [ ] Workspace authorization checks

### Projects
- [ ] GET /api/v1/projects
- [ ] POST /api/v1/projects
- [ ] GET /api/v1/projects/:id
- [ ] PATCH /api/v1/projects/:id
- [ ] DELETE /api/v1/projects/:id
- [ ] Project authorization (inherits from workspace)

### Datasets
- [ ] GET /api/v1/datasets
- [ ] POST /api/v1/datasets
- [ ] GET /api/v1/datasets/:id
- [ ] PATCH /api/v1/datasets/:id
- [ ] DELETE /api/v1/datasets/:id
- [ ] POST /api/v1/datasets/:id/reprocess
- [ ] GET /api/v1/datasets/:id/download
- [ ] Dataset status machine

---

## Phase 3: Supporting Features (Week 3)
### File Upload
- [ ] POST /api/v1/uploads/init
- [ ] POST /api/v1/uploads/:id/chunk
- [ ] POST /api/v1/uploads/:id/complete
- [ ] DELETE /api/v1/uploads/:id
- [ ] File type validation
- [ ] File size limits
- [ ] Storage service (local/S3)
- [ ] Cleanup job for incomplete uploads

### Invitations
- [ ] POST /api/v1/organizations/:id/invitations
- [ ] GET /api/v1/organizations/:id/invitations
- [ ] DELETE /api/v1/organizations/:id/invitations/:id
- [ ] POST /api/v1/invitations/:token/accept
- [ ] Email sending service
- [ ] Invitation expiry job

### Background Jobs
- [ ] Job queue setup (Redis/DB)
- [ ] Job worker process
- [ ] GET /api/v1/jobs
- [ ] GET /api/v1/jobs/:id
- [ ] DELETE /api/v1/jobs/:id (cancel)
- [ ] Job retry logic
- [ ] Job cleanup

### Notifications
- [ ] Notification service
- [ ] GET /api/v1/users/me/notifications
- [ ] PATCH /api/v1/users/me/notifications/:id
- [ ] DELETE /api/v1/users/me/notifications/:id
- [ ] WebSocket/SSE for real-time

### Audit Log
- [ ] Audit log service
- [ ] Auto-logging middleware
- [ ] GET /api/v1/audit-logs
- [ ] GET /api/v1/audit-logs/export

---

## Phase 4: Frontend (Week 4)
### Auth Pages
- [ ] Login page
- [ ] Register page
- [ ] Forgot password page
- [ ] Reset password page
- [ ] Email verification page
- [ ] Auth context/provider

### Layout & Navigation
- [ ] Main layout with sidebar
- [ ] Top navigation bar
- [ ] Organization switcher
- [ ] Workspace selector dropdown
- [ ] User menu (profile, logout)
- [ ] Mobile responsive

### Workspace Pages
- [ ] Workspace list page
- [ ] Workspace detail page
- [ ] Create workspace modal
- [ ] Edit workspace modal
- [ ] Workspace settings
- [ ] Workspace members page

### Project Pages
- [ ] Project list page
- [ ] Project detail page
- [ ] Create project modal
- [ ] Edit project modal
- [ ] Project settings

### Dataset Pages
- [ ] Dataset list page
- [ ] Dataset detail page
- [ ] Upload dataset flow
- [ ] Column mapping UI
- [ ] Dataset status display
- [ ] Reprocess action

### Settings Pages
- [ ] User profile settings
- [ ] Change password
- [ ] Notification preferences
- [ ] Organization settings (admin)
- [ ] Team members management

### Components Library
- [ ] Button variants
- [ ] Form inputs
- [ ] Modal/Dialog
- [ ] Toast notifications
- [ ] Loading skeletons
- [ ] Empty states
- [ ] Error states
- [ ] Data tables
- [ ] Pagination

---

## Quality Gates

### Before Each Feature
- [ ] Types defined in shared.ts
- [ ] Database migration ready
- [ ] API contract documented

### Before Each PR
- [ ] Soft delete filter in all queries
- [ ] Authorization check present
- [ ] Input validation complete
- [ ] Error handling complete
- [ ] All UI states handled
- [ ] No TypeScript errors
- [ ] No console.log

### Before Release
- [ ] All migrations applied
- [ ] Environment vars documented
- [ ] API docs updated
- [ ] Smoke tests passing
- [ ] Security review done

---

## Future Phases (Post-MVP)

### Phase 5: Billing (Week 5-6)
- [ ] Stripe integration
- [ ] Plan management
- [ ] Usage tracking
- [ ] Billing portal
- [ ] Upgrade/downgrade flows

### Phase 6: Process Mining Core (Week 7-8)
- [ ] XES parser
- [ ] CSV parser with mapping
- [ ] Process discovery algorithm
- [ ] Process map visualization
- [ ] Case list view
- [ ] Basic analytics

### Phase 7: Enterprise (Week 9-10)
- [ ] OAuth (Google, Microsoft)
- [ ] SAML SSO
- [ ] API keys management
- [ ] Advanced audit logs
- [ ] Custom domains
