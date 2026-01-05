# Process Mining SaaS Platform - Complete Technical Specification
## MVP Foundation Document v1.0

---

# Table of Contents
1. [Platform Feature Map](#1-platform-feature-map)
2. [Complete Database Schema](#2-complete-database-schema)
3. [API Contract Specification](#3-api-contract-specification)
4. [Shared Type Definitions](#4-shared-type-definitions)
5. [AI Development Context](#5-ai-development-context)
6. [Implementation Checklist](#6-implementation-checklist)

---

# 1. Platform Feature Map

## 1.1 Feature Priority Matrix

| Priority | Category | Features | MVP? |
|----------|----------|----------|------|
| P0 | Authentication | Login, Register, Password Reset, Session Management | ✅ |
| P0 | Multi-tenancy | Org → Workspace → Project hierarchy | ✅ |
| P0 | Authorization | RBAC at org/workspace level | ✅ |
| P0 | File Upload | Chunked upload, validation, storage | ✅ |
| P0 | Background Jobs | Queue, status tracking, retries | ✅ |
| P1 | Team Management | Invitations, role assignment | ✅ |
| P1 | User Profile | Settings, preferences, password change | ✅ |
| P1 | Notifications | In-app notifications | ✅ |
| P1 | Audit Log | Activity tracking | ✅ |
| P2 | Billing | Stripe integration, plans, usage | Phase 2 |
| P2 | API Keys | Developer access, rate limiting | Phase 2 |
| P2 | OAuth/SSO | Google, Microsoft login | Phase 2 |
| P3 | Enterprise | SAML, SCIM, MFA | Phase 3 |

## 1.2 Complete Feature Breakdown

### Authentication & Identity
- [ ] User registration (email/password)
- [ ] Email verification flow
- [ ] Login with email/password
- [ ] Logout (invalidate session)
- [ ] Password reset request
- [ ] Password reset confirmation
- [ ] Session management (JWT + refresh tokens)
- [ ] Token refresh endpoint
- [ ] Account lockout (5 failed attempts)
- [ ] Remember me (extended session)
- [ ] OAuth: Google (P2)
- [ ] OAuth: Microsoft (P2)
- [ ] SAML SSO (P3)
- [ ] MFA/2FA (P3)

### Organization Management
- [ ] Create organization (on registration)
- [ ] Update organization profile
- [ ] Upload organization logo
- [ ] Organization settings page
- [ ] View organization members
- [ ] Change member role
- [ ] Remove member
- [ ] Transfer ownership
- [ ] Delete organization (with confirmation)

### Team & Invitations
- [ ] Invite user by email
- [ ] Pending invitations list
- [ ] Resend invitation
- [ ] Revoke invitation
- [ ] Accept invitation flow
- [ ] Invitation expiry (7 days)
- [ ] Bulk invite via CSV (P2)
- [ ] Role assignment on invite

### User Profile & Settings
- [ ] View/edit profile (name, avatar)
- [ ] Change password
- [ ] Change email (with verification)
- [ ] Notification preferences
- [ ] Timezone preference
- [ ] Language preference (P2)
- [ ] Theme preference (light/dark)
- [ ] Delete account request
- [ ] Export my data (GDPR)

### Workspace Management
- [ ] Create workspace
- [ ] List workspaces (user's)
- [ ] View workspace details
- [ ] Update workspace
- [ ] Delete workspace (soft)
- [ ] Workspace members list
- [ ] Add member to workspace
- [ ] Change member role
- [ ] Remove member from workspace

### Project Management
- [ ] Create project
- [ ] List projects (in workspace)
- [ ] View project details
- [ ] Update project
- [ ] Delete project (soft)
- [ ] Project tags
- [ ] Project search/filter

### Dataset Management
- [ ] Upload dataset file
- [ ] Upload progress tracking
- [ ] File validation (type, size)
- [ ] List datasets (in project)
- [ ] View dataset details
- [ ] Dataset status tracking
- [ ] Delete dataset
- [ ] Re-process dataset
- [ ] Download original file

### File Upload System
- [ ] Chunked upload endpoint
- [ ] Resume interrupted upload
- [ ] File type validation
- [ ] File size limits (per plan)
- [ ] Virus scanning (P2)
- [ ] Storage quota tracking
- [ ] Signed download URLs
- [ ] File cleanup job

### Background Job System
- [ ] Job queue (Redis/DB based)
- [ ] Job status: pending/processing/completed/failed
- [ ] Job progress percentage
- [ ] Job cancellation
- [ ] Job retry (max 3)
- [ ] Job result storage
- [ ] Job cleanup (after 30 days)
- [ ] Webhook on completion (P2)

### Notifications
- [ ] In-app notification center
- [ ] Unread count badge
- [ ] Mark as read
- [ ] Mark all as read
- [ ] Delete notification
- [ ] Notification types/categories
- [ ] Email notifications
- [ ] Email digest settings (P2)
- [ ] Real-time updates (WebSocket/SSE)

### Audit & Activity Log
- [ ] Log all write operations
- [ ] Log authentication events
- [ ] Log: who, what, when, resource, IP
- [ ] View activity log (org admins)
- [ ] Filter by user/action/date
- [ ] Export activity log
- [ ] Retention policy (90 days)

### API & Developer Access (P2)
- [ ] Generate API key
- [ ] List API keys
- [ ] Revoke API key
- [ ] API key scopes
- [ ] API usage tracking
- [ ] Rate limiting
- [ ] API documentation page
- [ ] Webhook configuration
- [ ] Webhook delivery log

### Billing & Subscriptions (P2)
- [ ] Plan definitions
- [ ] Feature flags per plan
- [ ] Usage limits per plan
- [ ] Stripe integration
- [ ] Credit card management
- [ ] Billing history
- [ ] Plan upgrade
- [ ] Plan downgrade
- [ ] Trial management
- [ ] Failed payment handling

---

# 2. Complete Database Schema

```sql
-- ============================================================================
-- PROCESS MINING SAAS PLATFORM - COMPLETE DATABASE SCHEMA
-- Version: 1.0.0
-- Last Updated: 2024-XX-XX
-- ============================================================================

-- ============================================================================
-- EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- CUSTOM TYPES (ENUMS)
-- ============================================================================

CREATE TYPE org_role AS ENUM ('owner', 'admin', 'member');
CREATE TYPE workspace_role AS ENUM ('owner', 'admin', 'editor', 'viewer');
CREATE TYPE plan_type AS ENUM ('free', 'pro', 'enterprise');
CREATE TYPE dataset_status AS ENUM ('pending', 'processing', 'ready', 'error', 'archived');
CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
CREATE TYPE invitation_status AS ENUM ('pending', 'accepted', 'expired', 'revoked');
CREATE TYPE notification_type AS ENUM ('info', 'success', 'warning', 'error');
CREATE TYPE auth_provider AS ENUM ('email', 'google', 'microsoft', 'saml');

-- ============================================================================
-- CORE TABLES: AUTHENTICATION & USERS
-- ============================================================================

CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email               VARCHAR(255) NOT NULL,
    email_verified      BOOLEAN NOT NULL DEFAULT FALSE,
    email_verified_at   TIMESTAMP NULL,
    password_hash       VARCHAR(255) NULL, -- NULL for OAuth users
    display_name        VARCHAR(255),
    avatar_url          VARCHAR(500),
    auth_provider       auth_provider NOT NULL DEFAULT 'email',
    auth_provider_id    VARCHAR(255) NULL, -- OAuth provider user ID
    
    -- Security
    failed_login_count  INTEGER NOT NULL DEFAULT 0,
    locked_until        TIMESTAMP NULL,
    last_login_at       TIMESTAMP NULL,
    last_login_ip       INET NULL,
    
    -- Preferences
    timezone            VARCHAR(50) DEFAULT 'UTC',
    locale              VARCHAR(10) DEFAULT 'en',
    theme               VARCHAR(20) DEFAULT 'system',
    
    -- Audit fields (REQUIRED ON ALL TABLES)
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    
    CONSTRAINT users_email_unique UNIQUE (email) WHERE deleted_at IS NULL
);

CREATE TABLE user_sessions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id),
    token_hash          VARCHAR(255) NOT NULL, -- Hashed refresh token
    device_info         VARCHAR(500),
    ip_address          INET,
    expires_at          TIMESTAMP NOT NULL,
    last_used_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked_at          TIMESTAMP NULL
);

CREATE TABLE password_reset_tokens (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id),
    token_hash          VARCHAR(255) NOT NULL,
    expires_at          TIMESTAMP NOT NULL,
    used_at             TIMESTAMP NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_verification_tokens (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id),
    email               VARCHAR(255) NOT NULL, -- Email being verified
    token_hash          VARCHAR(255) NOT NULL,
    expires_at          TIMESTAMP NOT NULL,
    verified_at         TIMESTAMP NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- CORE TABLES: ORGANIZATIONS & MULTI-TENANCY
-- ============================================================================

CREATE TABLE organizations (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(255) NOT NULL,
    slug                VARCHAR(100) NOT NULL,
    logo_url            VARCHAR(500),
    
    -- Billing
    plan                plan_type NOT NULL DEFAULT 'free',
    plan_started_at     TIMESTAMP NULL,
    trial_ends_at       TIMESTAMP NULL,
    stripe_customer_id  VARCHAR(255) NULL,
    
    -- Settings
    settings_json       JSONB DEFAULT '{}',
    
    -- Audit fields
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    created_by          UUID REFERENCES users(id),
    
    CONSTRAINT organizations_slug_unique UNIQUE (slug) WHERE deleted_at IS NULL
);

CREATE TABLE organization_members (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id),
    user_id             UUID NOT NULL REFERENCES users(id),
    role                org_role NOT NULL DEFAULT 'member',
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    invited_by          UUID REFERENCES users(id),
    
    CONSTRAINT org_members_unique UNIQUE (organization_id, user_id) WHERE deleted_at IS NULL
);

CREATE TABLE invitations (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id),
    workspace_id        UUID NULL, -- NULL = org-level invite
    email               VARCHAR(255) NOT NULL,
    role                VARCHAR(20) NOT NULL, -- org_role or workspace_role
    token_hash          VARCHAR(255) NOT NULL,
    status              invitation_status NOT NULL DEFAULT 'pending',
    
    expires_at          TIMESTAMP NOT NULL,
    accepted_at         TIMESTAMP NULL,
    accepted_by         UUID REFERENCES users(id),
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    invited_by          UUID NOT NULL REFERENCES users(id),
    
    CONSTRAINT invitations_unique UNIQUE (organization_id, email, workspace_id) 
        WHERE status = 'pending'
);

-- ============================================================================
-- CORE TABLES: WORKSPACES & PROJECTS
-- ============================================================================

CREATE TABLE workspaces (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id),
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    
    -- Settings
    settings_json       JSONB DEFAULT '{}',
    
    -- Audit fields
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    created_by          UUID REFERENCES users(id)
);

CREATE TABLE workspace_members (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id        UUID NOT NULL REFERENCES workspaces(id),
    user_id             UUID NOT NULL REFERENCES users(id),
    role                workspace_role NOT NULL DEFAULT 'viewer',
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    added_by            UUID REFERENCES users(id),
    
    CONSTRAINT workspace_members_unique UNIQUE (workspace_id, user_id) WHERE deleted_at IS NULL
);

CREATE TABLE projects (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id        UUID NOT NULL REFERENCES workspaces(id),
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    tags                JSONB DEFAULT '[]',
    
    -- Stats (denormalized for performance)
    dataset_count       INTEGER NOT NULL DEFAULT 0,
    total_cases         INTEGER NOT NULL DEFAULT 0,
    
    -- Audit fields
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    created_by          UUID REFERENCES users(id)
);

-- ============================================================================
-- CORE TABLES: DATASETS & FILES
-- ============================================================================

CREATE TABLE datasets (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id),
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    
    -- Source file info
    source_filename     VARCHAR(255) NOT NULL,
    source_file_path    VARCHAR(500) NOT NULL,
    file_size_bytes     BIGINT NOT NULL,
    file_type           VARCHAR(50) NOT NULL, -- csv, xes, xlsx
    file_hash           VARCHAR(64), -- SHA-256 for deduplication
    
    -- Processing status
    status              dataset_status NOT NULL DEFAULT 'pending',
    error_message       TEXT NULL,
    error_details       JSONB NULL,
    processing_started_at TIMESTAMP NULL,
    processed_at        TIMESTAMP NULL,
    
    -- Parsed data stats
    case_count          INTEGER NULL,
    event_count         INTEGER NULL,
    activity_count      INTEGER NULL,
    date_range_start    TIMESTAMP NULL,
    date_range_end      TIMESTAMP NULL,
    
    -- Column mapping (user-defined)
    column_mapping      JSONB NULL,
    /*
    {
        "case_id": "CaseID",
        "activity": "Activity",
        "timestamp": "Timestamp",
        "resource": "Resource",
        "custom_attributes": ["Cost", "Priority"]
    }
    */
    
    -- Audit fields
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    created_by          UUID REFERENCES users(id)
);

CREATE TABLE file_uploads (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id),
    
    -- Upload tracking
    filename            VARCHAR(255) NOT NULL,
    file_size_bytes     BIGINT NOT NULL,
    mime_type           VARCHAR(100),
    
    -- Chunked upload support
    upload_id           VARCHAR(255) NULL, -- S3 multipart upload ID
    chunks_total        INTEGER NOT NULL DEFAULT 1,
    chunks_uploaded     INTEGER NOT NULL DEFAULT 0,
    
    -- Storage
    storage_path        VARCHAR(500) NULL,
    storage_provider    VARCHAR(50) NOT NULL DEFAULT 'local', -- local, s3
    
    -- Status
    status              VARCHAR(20) NOT NULL DEFAULT 'pending',
    completed_at        TIMESTAMP NULL,
    expires_at          TIMESTAMP NOT NULL, -- Cleanup incomplete uploads
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID REFERENCES users(id)
);

-- ============================================================================
-- CORE TABLES: BACKGROUND JOBS
-- ============================================================================

CREATE TABLE jobs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id),
    
    -- Job definition
    job_type            VARCHAR(100) NOT NULL, -- dataset_processing, report_generation, export
    job_data            JSONB NOT NULL, -- Input parameters
    priority            INTEGER NOT NULL DEFAULT 0,
    
    -- Status tracking
    status              job_status NOT NULL DEFAULT 'pending',
    progress_percent    INTEGER NOT NULL DEFAULT 0,
    progress_message    VARCHAR(500),
    
    -- Execution details
    started_at          TIMESTAMP NULL,
    completed_at        TIMESTAMP NULL,
    worker_id           VARCHAR(100) NULL,
    
    -- Results
    result_data         JSONB NULL,
    error_message       TEXT NULL,
    error_stack         TEXT NULL,
    
    -- Retry logic
    attempt_count       INTEGER NOT NULL DEFAULT 0,
    max_attempts        INTEGER NOT NULL DEFAULT 3,
    next_retry_at       TIMESTAMP NULL,
    
    -- Cleanup
    result_expires_at   TIMESTAMP NULL,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID REFERENCES users(id)
);

-- ============================================================================
-- CORE TABLES: NOTIFICATIONS
-- ============================================================================

CREATE TABLE notifications (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id),
    
    -- Content
    type                notification_type NOT NULL DEFAULT 'info',
    title               VARCHAR(255) NOT NULL,
    message             TEXT NOT NULL,
    
    -- Linking
    resource_type       VARCHAR(50) NULL, -- project, dataset, job
    resource_id         UUID NULL,
    action_url          VARCHAR(500) NULL,
    
    -- Status
    read_at             TIMESTAMP NULL,
    
    -- Delivery
    email_sent_at       TIMESTAMP NULL,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at          TIMESTAMP NULL -- Auto-cleanup old notifications
);

CREATE TABLE notification_preferences (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id),
    
    -- Channel preferences
    in_app_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    email_enabled       BOOLEAN NOT NULL DEFAULT TRUE,
    email_digest        VARCHAR(20) NOT NULL DEFAULT 'instant', -- instant, daily, weekly
    
    -- Category preferences (JSONB for flexibility)
    category_settings   JSONB DEFAULT '{}',
    /*
    {
        "job_completed": { "in_app": true, "email": true },
        "team_invite": { "in_app": true, "email": true },
        "dataset_error": { "in_app": true, "email": true }
    }
    */
    
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT notification_prefs_user_unique UNIQUE (user_id)
);

-- ============================================================================
-- CORE TABLES: AUDIT LOG
-- ============================================================================

CREATE TABLE audit_logs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID REFERENCES organizations(id), -- NULL for system events
    
    -- Actor
    user_id             UUID REFERENCES users(id),
    user_email          VARCHAR(255), -- Denormalized for history
    ip_address          INET,
    user_agent          VARCHAR(500),
    
    -- Action
    action              VARCHAR(100) NOT NULL, -- user.login, project.create, dataset.delete
    resource_type       VARCHAR(50) NULL,
    resource_id         UUID NULL,
    resource_name       VARCHAR(255) NULL, -- Denormalized
    
    -- Details
    old_values          JSONB NULL, -- For updates
    new_values          JSONB NULL, -- For creates/updates
    metadata            JSONB NULL, -- Extra context
    
    -- Timestamp (no updated_at - logs are immutable)
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Partition audit logs by month for performance (optional)
-- CREATE TABLE audit_logs_y2024m01 PARTITION OF audit_logs
--     FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- ============================================================================
-- CORE TABLES: USAGE & BILLING (P2)
-- ============================================================================

CREATE TABLE usage_records (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id),
    
    -- Usage period
    period_start        DATE NOT NULL,
    period_end          DATE NOT NULL,
    
    -- Metrics
    storage_bytes       BIGINT NOT NULL DEFAULT 0,
    datasets_count      INTEGER NOT NULL DEFAULT 0,
    cases_processed     INTEGER NOT NULL DEFAULT 0,
    api_calls           INTEGER NOT NULL DEFAULT 0,
    team_members        INTEGER NOT NULL DEFAULT 0,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT usage_records_unique UNIQUE (organization_id, period_start)
);

CREATE TABLE api_keys (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id),
    user_id             UUID NOT NULL REFERENCES users(id),
    
    name                VARCHAR(255) NOT NULL,
    key_prefix          VARCHAR(10) NOT NULL, -- First 8 chars for identification
    key_hash            VARCHAR(255) NOT NULL,
    
    -- Permissions
    scopes              JSONB NOT NULL DEFAULT '["read"]', -- ["read", "write", "admin"]
    
    -- Limits
    rate_limit          INTEGER NOT NULL DEFAULT 1000, -- Requests per hour
    
    -- Usage
    last_used_at        TIMESTAMP NULL,
    usage_count         INTEGER NOT NULL DEFAULT 0,
    
    expires_at          TIMESTAMP NULL,
    revoked_at          TIMESTAMP NULL,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PROCESS MINING TABLES: ANALYSIS & RESULTS
-- ============================================================================

CREATE TABLE process_models (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id          UUID NOT NULL REFERENCES datasets(id),
    
    -- Model info
    name                VARCHAR(255) NOT NULL,
    algorithm           VARCHAR(50) NOT NULL, -- alpha, heuristic, inductive
    parameters          JSONB NULL,
    
    -- Model data
    model_data          JSONB NOT NULL, -- Nodes, edges, frequencies
    bpmn_xml            TEXT NULL, -- BPMN 2.0 export
    
    -- Stats
    fitness_score       DECIMAL(5,4) NULL,
    precision_score     DECIMAL(5,4) NULL,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID REFERENCES users(id)
);

CREATE TABLE saved_filters (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id),
    user_id             UUID NOT NULL REFERENCES users(id),
    
    name                VARCHAR(255) NOT NULL,
    filter_config       JSONB NOT NULL,
    /*
    {
        "date_range": { "start": "2024-01-01", "end": "2024-12-31" },
        "activities": ["Submit", "Review", "Approve"],
        "duration_min": 3600,
        "variants": ["variant_1", "variant_2"]
    }
    */
    
    is_shared           BOOLEAN NOT NULL DEFAULT FALSE,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dashboards (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id),
    
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    
    -- Layout & widgets
    layout_config       JSONB NOT NULL DEFAULT '{"widgets": []}',
    
    is_default          BOOLEAN NOT NULL DEFAULT FALSE,
    is_shared           BOOLEAN NOT NULL DEFAULT FALSE,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID REFERENCES users(id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Users
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_user_sessions_user ON user_sessions(user_id) WHERE revoked_at IS NULL;
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at) WHERE revoked_at IS NULL;

-- Organizations
CREATE INDEX idx_org_members_user ON organization_members(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_org_members_org ON organization_members(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_invitations_email ON invitations(email) WHERE status = 'pending';
CREATE INDEX idx_invitations_org ON invitations(organization_id) WHERE status = 'pending';

-- Workspaces & Projects
CREATE INDEX idx_workspaces_org ON workspaces(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_workspace_members_user ON workspace_members(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_workspace_members_ws ON workspace_members(workspace_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_projects_workspace ON projects(workspace_id) WHERE deleted_at IS NULL;

-- Datasets
CREATE INDEX idx_datasets_project ON datasets(project_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_datasets_status ON datasets(status) WHERE deleted_at IS NULL;

-- Jobs
CREATE INDEX idx_jobs_status ON jobs(status) WHERE status IN ('pending', 'processing');
CREATE INDEX idx_jobs_org ON jobs(organization_id);
CREATE INDEX idx_jobs_type_status ON jobs(job_type, status);

-- Notifications
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, created_at DESC) WHERE read_at IS NULL;
CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);

-- Audit Logs
CREATE INDEX idx_audit_logs_org ON audit_logs(organization_id, created_at DESC);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action, created_at DESC);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMPS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_org_members_updated_at BEFORE UPDATE ON organization_members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspaces_updated_at BEFORE UPDATE ON workspaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspace_members_updated_at BEFORE UPDATE ON workspace_members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_datasets_updated_at BEFORE UPDATE ON datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_invitations_updated_at BEFORE UPDATE ON invitations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

# 3. API Contract Specification

## 3.1 API Design Principles

```yaml
# Standard response envelope
ApiResponse:
  success: boolean
  data: T | null
  error: ApiError | null
  meta: { timestamp, requestId }

# Standard error format
ApiError:
  code: string  # Machine-readable: UNAUTHORIZED, NOT_FOUND, VALIDATION_ERROR
  message: string  # Human-readable
  details: object | null  # Field-level errors for validation

# HTTP Status Code Usage
200: Success (GET, PATCH)
201: Created (POST)
204: No Content (DELETE)
400: Bad Request (validation errors)
401: Unauthorized (not logged in)
403: Forbidden (no permission)
404: Not Found
409: Conflict (duplicate)
422: Unprocessable Entity
429: Rate Limited
500: Internal Server Error
```

## 3.2 API Endpoint Catalog

### Authentication Endpoints
```
POST   /api/v1/auth/register           # Create account
POST   /api/v1/auth/login              # Login, get tokens
POST   /api/v1/auth/logout             # Invalidate session
POST   /api/v1/auth/refresh            # Refresh access token
POST   /api/v1/auth/forgot-password    # Request reset email
POST   /api/v1/auth/reset-password     # Confirm reset
POST   /api/v1/auth/verify-email       # Verify email token
GET    /api/v1/auth/me                 # Get current user
```

### User Endpoints
```
GET    /api/v1/users/me                # Get profile
PATCH  /api/v1/users/me                # Update profile
PATCH  /api/v1/users/me/password       # Change password
PATCH  /api/v1/users/me/email          # Change email (sends verification)
DELETE /api/v1/users/me                # Delete account (soft)
GET    /api/v1/users/me/notifications  # List notifications
PATCH  /api/v1/users/me/notifications/:id  # Mark read
DELETE /api/v1/users/me/notifications/:id  # Delete
```

### Organization Endpoints
```
GET    /api/v1/organizations           # List user's orgs
POST   /api/v1/organizations           # Create org
GET    /api/v1/organizations/:id       # Get org
PATCH  /api/v1/organizations/:id       # Update org
DELETE /api/v1/organizations/:id       # Delete org (soft)

GET    /api/v1/organizations/:id/members     # List members
PATCH  /api/v1/organizations/:id/members/:userId  # Update role
DELETE /api/v1/organizations/:id/members/:userId  # Remove member

POST   /api/v1/organizations/:id/invitations    # Create invite
GET    /api/v1/organizations/:id/invitations    # List invites
DELETE /api/v1/organizations/:id/invitations/:id # Revoke invite
POST   /api/v1/invitations/:token/accept        # Accept invite
```

### Workspace Endpoints
```
GET    /api/v1/workspaces              # List (filtered by org)
POST   /api/v1/workspaces              # Create
GET    /api/v1/workspaces/:id          # Get
PATCH  /api/v1/workspaces/:id          # Update
DELETE /api/v1/workspaces/:id          # Delete (soft)

GET    /api/v1/workspaces/:id/members  # List members
POST   /api/v1/workspaces/:id/members  # Add member
PATCH  /api/v1/workspaces/:id/members/:userId  # Update role
DELETE /api/v1/workspaces/:id/members/:userId  # Remove member
```

### Project Endpoints
```
GET    /api/v1/projects                # List (filtered by workspace)
POST   /api/v1/projects                # Create
GET    /api/v1/projects/:id            # Get
PATCH  /api/v1/projects/:id            # Update
DELETE /api/v1/projects/:id            # Delete (soft)
```

### Dataset Endpoints
```
GET    /api/v1/datasets                # List (filtered by project)
POST   /api/v1/datasets                # Create (with file)
GET    /api/v1/datasets/:id            # Get
PATCH  /api/v1/datasets/:id            # Update
DELETE /api/v1/datasets/:id            # Delete (soft)
POST   /api/v1/datasets/:id/reprocess  # Reprocess
GET    /api/v1/datasets/:id/download   # Get download URL
```

### File Upload Endpoints
```
POST   /api/v1/uploads/init            # Initialize upload
POST   /api/v1/uploads/:id/chunk       # Upload chunk
POST   /api/v1/uploads/:id/complete    # Complete upload
DELETE /api/v1/uploads/:id             # Cancel upload
```

### Job Endpoints
```
GET    /api/v1/jobs                    # List (filtered)
GET    /api/v1/jobs/:id                # Get status
DELETE /api/v1/jobs/:id                # Cancel job
```

### Audit Log Endpoints (Admin)
```
GET    /api/v1/audit-logs              # List (filtered)
GET    /api/v1/audit-logs/export       # Export CSV
```

---

# 4. Shared Type Definitions

```typescript
// ============================================================================
// types/shared.ts - IMPORT THIS EVERYWHERE
// ============================================================================

// ============================================================================
// ENUMS (Must match database CHECK constraints exactly)
// ============================================================================

export const ORG_ROLES = ['owner', 'admin', 'member'] as const;
export type OrgRole = typeof ORG_ROLES[number];

export const WORKSPACE_ROLES = ['owner', 'admin', 'editor', 'viewer'] as const;
export type WorkspaceRole = typeof WORKSPACE_ROLES[number];

export const PLAN_TYPES = ['free', 'pro', 'enterprise'] as const;
export type PlanType = typeof PLAN_TYPES[number];

export const DATASET_STATUSES = ['pending', 'processing', 'ready', 'error', 'archived'] as const;
export type DatasetStatus = typeof DATASET_STATUSES[number];

export const JOB_STATUSES = ['pending', 'processing', 'completed', 'failed', 'cancelled'] as const;
export type JobStatus = typeof JOB_STATUSES[number];

export const INVITATION_STATUSES = ['pending', 'accepted', 'expired', 'revoked'] as const;
export type InvitationStatus = typeof INVITATION_STATUSES[number];

export const NOTIFICATION_TYPES = ['info', 'success', 'warning', 'error'] as const;
export type NotificationType = typeof NOTIFICATION_TYPES[number];

export const AUTH_PROVIDERS = ['email', 'google', 'microsoft', 'saml'] as const;
export type AuthProvider = typeof AUTH_PROVIDERS[number];

// ============================================================================
// ERROR CODES
// ============================================================================

export const ERROR_CODES = {
  // Auth errors
  UNAUTHORIZED: 'UNAUTHORIZED',
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  ACCOUNT_LOCKED: 'ACCOUNT_LOCKED',
  EMAIL_NOT_VERIFIED: 'EMAIL_NOT_VERIFIED',
  
  // Permission errors
  FORBIDDEN: 'FORBIDDEN',
  INSUFFICIENT_ROLE: 'INSUFFICIENT_ROLE',
  NOT_MEMBER: 'NOT_MEMBER',
  
  // Resource errors
  NOT_FOUND: 'NOT_FOUND',
  ALREADY_EXISTS: 'ALREADY_EXISTS',
  CONFLICT: 'CONFLICT',
  
  // Validation errors
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_INPUT: 'INVALID_INPUT',
  
  // Limit errors
  QUOTA_EXCEEDED: 'QUOTA_EXCEEDED',
  RATE_LIMITED: 'RATE_LIMITED',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  
  // System errors
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];

// ============================================================================
// BASE TYPES
// ============================================================================

export interface BaseEntity {
  id: string;
  createdAt: string;  // ISO 8601
  updatedAt: string;
  deletedAt: string | null;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: {
    timestamp: string;
    requestId: string;
  };
}

export interface ApiError {
  code: ErrorCode;
  message: string;
  details?: Record<string, string[]>;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    pageSize: number;
    totalCount: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface PaginationParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// ============================================================================
// DOMAIN ENTITIES
// ============================================================================

export interface User extends BaseEntity {
  email: string;
  emailVerified: boolean;
  displayName: string | null;
  avatarUrl: string | null;
  authProvider: AuthProvider;
  timezone: string;
  locale: string;
  theme: string;
  lastLoginAt: string | null;
}

export interface Organization extends BaseEntity {
  name: string;
  slug: string;
  logoUrl: string | null;
  plan: PlanType;
  trialEndsAt: string | null;
  createdBy: string | null;
}

export interface OrganizationMember {
  id: string;
  organizationId: string;
  userId: string;
  role: OrgRole;
  createdAt: string;
  user?: User; // Populated on join
}

export interface Workspace extends BaseEntity {
  organizationId: string;
  name: string;
  description: string | null;
  createdBy: string | null;
}

export interface WorkspaceMember {
  id: string;
  workspaceId: string;
  userId: string;
  role: WorkspaceRole;
  createdAt: string;
  user?: User;
}

export interface Project extends BaseEntity {
  workspaceId: string;
  name: string;
  description: string | null;
  tags: string[];
  datasetCount: number;
  totalCases: number;
  createdBy: string | null;
}

export interface Dataset extends BaseEntity {
  projectId: string;
  name: string;
  description: string | null;
  sourceFilename: string;
  fileSizeBytes: number;
  fileType: string;
  status: DatasetStatus;
  errorMessage: string | null;
  processedAt: string | null;
  caseCount: number | null;
  eventCount: number | null;
  activityCount: number | null;
  dateRangeStart: string | null;
  dateRangeEnd: string | null;
  columnMapping: ColumnMapping | null;
  createdBy: string | null;
}

export interface ColumnMapping {
  caseId: string;
  activity: string;
  timestamp: string;
  resource?: string;
  customAttributes?: string[];
}

export interface Invitation {
  id: string;
  organizationId: string;
  workspaceId: string | null;
  email: string;
  role: string;
  status: InvitationStatus;
  expiresAt: string;
  createdAt: string;
  invitedBy: string;
}

export interface Job {
  id: string;
  organizationId: string;
  jobType: string;
  status: JobStatus;
  progressPercent: number;
  progressMessage: string | null;
  startedAt: string | null;
  completedAt: string | null;
  errorMessage: string | null;
  createdAt: string;
}

export interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  resourceType: string | null;
  resourceId: string | null;
  actionUrl: string | null;
  readAt: string | null;
  createdAt: string;
}

export interface AuditLog {
  id: string;
  organizationId: string | null;
  userId: string | null;
  userEmail: string | null;
  ipAddress: string | null;
  action: string;
  resourceType: string | null;
  resourceId: string | null;
  resourceName: string | null;
  createdAt: string;
}

// ============================================================================
// REQUEST/INPUT TYPES
// ============================================================================

// Auth
export interface RegisterInput {
  email: string;
  password: string;
  displayName?: string;
  organizationName?: string;
}

export interface LoginInput {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface ResetPasswordInput {
  token: string;
  password: string;
}

// Organization
export interface CreateOrganizationInput {
  name: string;
  slug?: string;
}

export interface UpdateOrganizationInput {
  name?: string;
  logoUrl?: string;
}

// Workspace
export interface CreateWorkspaceInput {
  organizationId: string;
  name: string;
  description?: string;
}

export interface UpdateWorkspaceInput {
  name?: string;
  description?: string;
}

// Project
export interface CreateProjectInput {
  workspaceId: string;
  name: string;
  description?: string;
  tags?: string[];
}

export interface UpdateProjectInput {
  name?: string;
  description?: string;
  tags?: string[];
}

// Dataset
export interface CreateDatasetInput {
  projectId: string;
  name: string;
  description?: string;
  fileUploadId: string; // Reference to completed upload
}

export interface UpdateDatasetInput {
  name?: string;
  description?: string;
  columnMapping?: ColumnMapping;
}

// Invitation
export interface CreateInvitationInput {
  email: string;
  role: OrgRole | WorkspaceRole;
  workspaceId?: string;
}

// ============================================================================
// VALIDATION RULES (Use with Zod)
// ============================================================================

export const VALIDATION = {
  email: {
    maxLength: 255,
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  password: {
    minLength: 8,
    maxLength: 128,
    // At least: 1 uppercase, 1 lowercase, 1 number
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
  },
  name: {
    minLength: 1,
    maxLength: 255,
  },
  slug: {
    minLength: 2,
    maxLength: 100,
    pattern: /^[a-z0-9-]+$/,
  },
  description: {
    maxLength: 2000,
  },
  tags: {
    maxCount: 20,
    maxTagLength: 50,
  },
} as const;

// ============================================================================
// PLAN LIMITS
// ============================================================================

export const PLAN_LIMITS: Record<PlanType, PlanLimit> = {
  free: {
    maxWorkspaces: 2,
    maxProjectsPerWorkspace: 5,
    maxDatasetsPerProject: 10,
    maxStorageBytes: 1 * 1024 * 1024 * 1024, // 1 GB
    maxFileSizeBytes: 50 * 1024 * 1024, // 50 MB
    maxTeamMembers: 3,
    maxCasesPerDataset: 10000,
  },
  pro: {
    maxWorkspaces: 10,
    maxProjectsPerWorkspace: 50,
    maxDatasetsPerProject: 100,
    maxStorageBytes: 50 * 1024 * 1024 * 1024, // 50 GB
    maxFileSizeBytes: 500 * 1024 * 1024, // 500 MB
    maxTeamMembers: 25,
    maxCasesPerDataset: 500000,
  },
  enterprise: {
    maxWorkspaces: -1, // Unlimited
    maxProjectsPerWorkspace: -1,
    maxDatasetsPerProject: -1,
    maxStorageBytes: -1,
    maxFileSizeBytes: 2 * 1024 * 1024 * 1024, // 2 GB
    maxTeamMembers: -1,
    maxCasesPerDataset: -1,
  },
};

export interface PlanLimit {
  maxWorkspaces: number;
  maxProjectsPerWorkspace: number;
  maxDatasetsPerProject: number;
  maxStorageBytes: number;
  maxFileSizeBytes: number;
  maxTeamMembers: number;
  maxCasesPerDataset: number;
}
```

---

# 5. AI Development Context

Save this as `PROJECT_CONTEXT.md` and include with EVERY AI prompt:

```markdown
# PROJECT CONTEXT - PROCESS MINING SAAS PLATFORM

## Project Overview
- Name: [Your Platform Name]
- Stage: MVP
- Stack: [e.g., Next.js 14, FastAPI, PostgreSQL, Redis]

## CRITICAL RULES FOR AI CODE GENERATION

### Database Rules
1. ALL queries MUST filter by `deleted_at IS NULL` (soft delete pattern)
2. ALL inserts MUST use database defaults for `created_at`, `updated_at`
3. ALL updates MUST trigger the `update_updated_at_column()` function (automatic)
4. Use parameterized queries ONLY - NEVER string concatenation
5. Reference PLATFORM_SPECIFICATION.md Section 2 for all table/column names
6. Use UUID for all IDs (uuid_generate_v4())
7. Always include proper JOINs for related data

### API Rules
1. ALL responses MUST use the ApiResponse<T> wrapper format
2. ALL endpoints require authentication except /api/v1/auth/*
3. Return correct HTTP status codes (see Section 3.1)
4. Validate ALL inputs using Zod schemas before processing
5. Authorization checks MUST happen before any business logic
6. Log ALL errors with correlation ID (requestId)
7. Include pagination for all list endpoints

### Authorization Rules
1. Check organization membership first
2. Then check workspace membership if applicable
3. Verify role has required permission level
4. Use consistent permission checking utility

```typescript
// Permission hierarchy
const ROLE_HIERARCHY = {
  org: { owner: 3, admin: 2, member: 1 },
  workspace: { owner: 4, admin: 3, editor: 2, viewer: 1 }
};

// Minimum roles for actions
const REQUIRED_ROLES = {
  'workspace.delete': 'owner',
  'workspace.update': 'admin',
  'project.create': 'editor',
  'project.read': 'viewer',
};
```

### Frontend Rules
1. ALL API calls go through the api-client module
2. ALL forms use react-hook-form with Zod validation
3. Handle ALL states: loading, error, empty, success
4. Use shared types from types/shared.ts (NO 'any' type)
5. NO inline styles - use Tailwind classes only
6. Show toast notifications for all mutations
7. Implement optimistic updates where appropriate

### Error Handling
- Backend: Throw typed AppError, catch at middleware level
- Frontend: Use error boundaries + toast notifications
- NEVER silently swallow errors
- Always log errors with context

### Naming Conventions
- Database: snake_case (organization_id, created_at)
- API JSON: camelCase (organizationId, createdAt)
- Files: kebab-case (workspace-service.ts)
- React Components: PascalCase (WorkspaceList.tsx)
- Constants: UPPER_SNAKE_CASE (MAX_FILE_SIZE)

### File Structure
```
/src
  /api              # API routes/controllers
  /services         # Business logic
  /repositories     # Database access
  /middleware       # Auth, error handling, logging
  /utils            # Helpers, constants
  /types            # Shared types
  /components       # React components
  /hooks            # Custom React hooks
  /stores           # State management
```

## Reference Files
- Database Schema: PLATFORM_SPECIFICATION.md Section 2
- API Endpoints: PLATFORM_SPECIFICATION.md Section 3
- Shared Types: PLATFORM_SPECIFICATION.md Section 4
```

---

# 6. Implementation Checklist

## Phase 1: Foundation (Week 1)

### Day 1-2: Database & Core Setup
- [ ] Run database schema
- [ ] Verify all tables created
- [ ] Create seed data script
- [ ] Set up migration system
- [ ] Configure environment variables

### Day 3-4: Authentication
- [ ] User registration endpoint
- [ ] Email verification flow
- [ ] Login endpoint (JWT + refresh)
- [ ] Logout endpoint
- [ ] Password reset flow
- [ ] Auth middleware
- [ ] Session management

### Day 5: Base Infrastructure
- [ ] API response wrapper
- [ ] Error handling middleware
- [ ] Request logging
- [ ] Validation utilities (Zod)
- [ ] Base repository class

## Phase 2: Core Entities (Week 2)

### Day 1: Organizations
- [ ] CRUD endpoints
- [ ] Member management
- [ ] Organization context/middleware

### Day 2-3: Workspaces
- [ ] CRUD endpoints
- [ ] Member management
- [ ] Permission checks

### Day 4-5: Projects & Datasets
- [ ] Project CRUD
- [ ] Dataset CRUD
- [ ] File upload integration
- [ ] Status tracking

## Phase 3: Supporting Features (Week 3)

### Day 1-2: Invitations
- [ ] Create invitation
- [ ] Email sending
- [ ] Accept flow
- [ ] Expiry handling

### Day 3: Notifications
- [ ] Notification service
- [ ] In-app notifications API
- [ ] Preference management

### Day 4: Background Jobs
- [ ] Job queue setup
- [ ] Worker process
- [ ] Status tracking API
- [ ] Retry logic

### Day 5: Audit Logging
- [ ] Audit log service
- [ ] Automatic logging middleware
- [ ] Query endpoints

## Phase 4: Frontend (Week 4)

### Day 1: Auth UI
- [ ] Login page
- [ ] Register page
- [ ] Password reset pages
- [ ] Email verification page

### Day 2-3: Core Navigation
- [ ] Layout with sidebar
- [ ] Organization switcher
- [ ] Workspace selector
- [ ] User menu

### Day 4-5: CRUD Pages
- [ ] Workspace list/detail
- [ ] Project list/detail
- [ ] Dataset list/upload
- [ ] Settings pages

## Quality Gates (Apply Throughout)

### Before Each Feature
- [ ] Types defined in shared.ts
- [ ] Database migration ready
- [ ] API contract documented

### Before Each PR
- [ ] Soft delete filter in all queries
- [ ] Authorization check present
- [ ] Input validation with Zod
- [ ] Error handling complete
- [ ] Loading/error/empty states
- [ ] No TypeScript 'any' types

### Before Each Release
- [ ] All migrations applied
- [ ] Environment variables documented
- [ ] API documentation updated
- [ ] Basic smoke tests passing

---

*Document Version: 1.0.0*
*Last Updated: [Date]*
