-- ============================================================================
-- PROCESS MINING SAAS PLATFORM - COMPLETE DATABASE SCHEMA
-- Version: 1.0.0
-- 
-- INSTRUCTIONS:
-- 1. Run this file against a fresh PostgreSQL database
-- 2. This creates ALL tables, indexes, and triggers for the MVP
-- 3. After running, use seed.sql to populate initial data
--
-- RULES FOR AI CODE GENERATION:
-- - ALL queries MUST filter by `deleted_at IS NULL`
-- - ALL queries use parameterized statements (never string concat)
-- - Column names in this file are the SOURCE OF TRUTH
-- ============================================================================

-- ============================================================================
-- EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- CUSTOM TYPES (ENUMS)
-- Match these EXACTLY in application code
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
-- TRIGGER FUNCTION (Create before tables)
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';

-- ============================================================================
-- USERS & AUTHENTICATION
-- ============================================================================

CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email               VARCHAR(255) NOT NULL,
    email_verified      BOOLEAN NOT NULL DEFAULT FALSE,
    email_verified_at   TIMESTAMP NULL,
    password_hash       VARCHAR(255) NULL,
    display_name        VARCHAR(255),
    avatar_url          VARCHAR(500),
    auth_provider       auth_provider NOT NULL DEFAULT 'email',
    auth_provider_id    VARCHAR(255) NULL,
    
    -- Security
    failed_login_count  INTEGER NOT NULL DEFAULT 0,
    locked_until        TIMESTAMP NULL,
    last_login_at       TIMESTAMP NULL,
    last_login_ip       INET NULL,
    
    -- Preferences
    timezone            VARCHAR(50) DEFAULT 'UTC',
    locale              VARCHAR(10) DEFAULT 'en',
    theme               VARCHAR(20) DEFAULT 'system',
    
    -- Audit fields
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    
    CONSTRAINT users_email_unique UNIQUE (email)
);

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE user_sessions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash          VARCHAR(255) NOT NULL,
    device_info         VARCHAR(500),
    ip_address          INET,
    expires_at          TIMESTAMP NOT NULL,
    last_used_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    revoked_at          TIMESTAMP NULL
);

CREATE TABLE password_reset_tokens (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash          VARCHAR(255) NOT NULL,
    expires_at          TIMESTAMP NOT NULL,
    used_at             TIMESTAMP NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE email_verification_tokens (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email               VARCHAR(255) NOT NULL,
    token_hash          VARCHAR(255) NOT NULL,
    expires_at          TIMESTAMP NOT NULL,
    verified_at         TIMESTAMP NULL,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- ORGANIZATIONS & MULTI-TENANCY
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
    
    CONSTRAINT organizations_slug_unique UNIQUE (slug)
);

CREATE TRIGGER update_organizations_updated_at 
    BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE organization_members (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role                org_role NOT NULL DEFAULT 'member',
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    invited_by          UUID REFERENCES users(id),
    
    CONSTRAINT org_members_unique UNIQUE (organization_id, user_id)
);

CREATE TRIGGER update_org_members_updated_at 
    BEFORE UPDATE ON organization_members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE invitations (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    workspace_id        UUID NULL,
    email               VARCHAR(255) NOT NULL,
    role                VARCHAR(20) NOT NULL,
    token_hash          VARCHAR(255) NOT NULL,
    status              invitation_status NOT NULL DEFAULT 'pending',
    
    expires_at          TIMESTAMP NOT NULL,
    accepted_at         TIMESTAMP NULL,
    accepted_by         UUID REFERENCES users(id),
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    invited_by          UUID NOT NULL REFERENCES users(id)
);

CREATE TRIGGER update_invitations_updated_at 
    BEFORE UPDATE ON invitations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- WORKSPACES & PROJECTS
-- ============================================================================

CREATE TABLE workspaces (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    settings_json       JSONB DEFAULT '{}',
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    created_by          UUID REFERENCES users(id)
);

CREATE TRIGGER update_workspaces_updated_at 
    BEFORE UPDATE ON workspaces
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add foreign key for invitations now that workspaces exists
ALTER TABLE invitations 
    ADD CONSTRAINT invitations_workspace_fk 
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE;

CREATE TABLE workspace_members (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role                workspace_role NOT NULL DEFAULT 'viewer',
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    added_by            UUID REFERENCES users(id),
    
    CONSTRAINT workspace_members_unique UNIQUE (workspace_id, user_id)
);

CREATE TRIGGER update_workspace_members_updated_at 
    BEFORE UPDATE ON workspace_members
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE projects (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id        UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    tags                JSONB DEFAULT '[]',
    
    -- Denormalized stats
    dataset_count       INTEGER NOT NULL DEFAULT 0,
    total_cases         INTEGER NOT NULL DEFAULT 0,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    created_by          UUID REFERENCES users(id)
);

CREATE TRIGGER update_projects_updated_at 
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- DATASETS & FILES
-- ============================================================================

CREATE TABLE datasets (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    
    -- Source file
    source_filename     VARCHAR(255) NOT NULL,
    source_file_path    VARCHAR(500) NOT NULL,
    file_size_bytes     BIGINT NOT NULL,
    file_type           VARCHAR(50) NOT NULL,
    file_hash           VARCHAR(64),
    
    -- Status
    status              dataset_status NOT NULL DEFAULT 'pending',
    error_message       TEXT NULL,
    error_details       JSONB NULL,
    processing_started_at TIMESTAMP NULL,
    processed_at        TIMESTAMP NULL,
    
    -- Parsed stats
    case_count          INTEGER NULL,
    event_count         INTEGER NULL,
    activity_count      INTEGER NULL,
    date_range_start    TIMESTAMP NULL,
    date_range_end      TIMESTAMP NULL,
    
    -- Column mapping
    column_mapping      JSONB NULL,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at          TIMESTAMP NULL,
    created_by          UUID REFERENCES users(id)
);

CREATE TRIGGER update_datasets_updated_at 
    BEFORE UPDATE ON datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE file_uploads (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    filename            VARCHAR(255) NOT NULL,
    file_size_bytes     BIGINT NOT NULL,
    mime_type           VARCHAR(100),
    
    -- Chunked upload
    upload_id           VARCHAR(255) NULL,
    chunks_total        INTEGER NOT NULL DEFAULT 1,
    chunks_uploaded     INTEGER NOT NULL DEFAULT 0,
    
    -- Storage
    storage_path        VARCHAR(500) NULL,
    storage_provider    VARCHAR(50) NOT NULL DEFAULT 'local',
    
    status              VARCHAR(20) NOT NULL DEFAULT 'pending',
    completed_at        TIMESTAMP NULL,
    expires_at          TIMESTAMP NOT NULL,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID REFERENCES users(id)
);

-- ============================================================================
-- BACKGROUND JOBS
-- ============================================================================

CREATE TABLE jobs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    job_type            VARCHAR(100) NOT NULL,
    job_data            JSONB NOT NULL,
    priority            INTEGER NOT NULL DEFAULT 0,
    
    status              job_status NOT NULL DEFAULT 'pending',
    progress_percent    INTEGER NOT NULL DEFAULT 0,
    progress_message    VARCHAR(500),
    
    started_at          TIMESTAMP NULL,
    completed_at        TIMESTAMP NULL,
    worker_id           VARCHAR(100) NULL,
    
    result_data         JSONB NULL,
    error_message       TEXT NULL,
    error_stack         TEXT NULL,
    
    attempt_count       INTEGER NOT NULL DEFAULT 0,
    max_attempts        INTEGER NOT NULL DEFAULT 3,
    next_retry_at       TIMESTAMP NULL,
    
    result_expires_at   TIMESTAMP NULL,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID REFERENCES users(id)
);

CREATE TRIGGER update_jobs_updated_at 
    BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- NOTIFICATIONS
-- ============================================================================

CREATE TABLE notifications (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    type                notification_type NOT NULL DEFAULT 'info',
    title               VARCHAR(255) NOT NULL,
    message             TEXT NOT NULL,
    
    resource_type       VARCHAR(50) NULL,
    resource_id         UUID NULL,
    action_url          VARCHAR(500) NULL,
    
    read_at             TIMESTAMP NULL,
    email_sent_at       TIMESTAMP NULL,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at          TIMESTAMP NULL
);

CREATE TABLE notification_preferences (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    in_app_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
    email_enabled       BOOLEAN NOT NULL DEFAULT TRUE,
    email_digest        VARCHAR(20) NOT NULL DEFAULT 'instant',
    category_settings   JSONB DEFAULT '{}',
    
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT notification_prefs_user_unique UNIQUE (user_id)
);

-- ============================================================================
-- AUDIT LOG
-- ============================================================================

CREATE TABLE audit_logs (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID REFERENCES organizations(id) ON DELETE SET NULL,
    
    user_id             UUID REFERENCES users(id) ON DELETE SET NULL,
    user_email          VARCHAR(255),
    ip_address          INET,
    user_agent          VARCHAR(500),
    
    action              VARCHAR(100) NOT NULL,
    resource_type       VARCHAR(50) NULL,
    resource_id         UUID NULL,
    resource_name       VARCHAR(255) NULL,
    
    old_values          JSONB NULL,
    new_values          JSONB NULL,
    metadata            JSONB NULL,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- USAGE & BILLING (Phase 2)
-- ============================================================================

CREATE TABLE usage_records (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    
    period_start        DATE NOT NULL,
    period_end          DATE NOT NULL,
    
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
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    name                VARCHAR(255) NOT NULL,
    key_prefix          VARCHAR(10) NOT NULL,
    key_hash            VARCHAR(255) NOT NULL,
    
    scopes              JSONB NOT NULL DEFAULT '["read"]',
    rate_limit          INTEGER NOT NULL DEFAULT 1000,
    
    last_used_at        TIMESTAMP NULL,
    usage_count         INTEGER NOT NULL DEFAULT 0,
    
    expires_at          TIMESTAMP NULL,
    revoked_at          TIMESTAMP NULL,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- PROCESS MINING TABLES
-- ============================================================================

CREATE TABLE process_models (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dataset_id          UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    
    name                VARCHAR(255) NOT NULL,
    algorithm           VARCHAR(50) NOT NULL,
    parameters          JSONB NULL,
    
    model_data          JSONB NOT NULL,
    bpmn_xml            TEXT NULL,
    
    fitness_score       DECIMAL(5,4) NULL,
    precision_score     DECIMAL(5,4) NULL,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID REFERENCES users(id)
);

CREATE TABLE saved_filters (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    name                VARCHAR(255) NOT NULL,
    filter_config       JSONB NOT NULL,
    is_shared           BOOLEAN NOT NULL DEFAULT FALSE,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dashboards (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    layout_config       JSONB NOT NULL DEFAULT '{"widgets": []}',
    
    is_default          BOOLEAN NOT NULL DEFAULT FALSE,
    is_shared           BOOLEAN NOT NULL DEFAULT FALSE,
    
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by          UUID REFERENCES users(id)
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Users & Auth
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_user_sessions_user ON user_sessions(user_id) WHERE revoked_at IS NULL;
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at) WHERE revoked_at IS NULL;
CREATE INDEX idx_password_reset_tokens_user ON password_reset_tokens(user_id) WHERE used_at IS NULL;

-- Organizations
CREATE INDEX idx_org_members_user ON organization_members(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_org_members_org ON organization_members(organization_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_invitations_email ON invitations(email) WHERE status = 'pending';
CREATE INDEX idx_invitations_org ON invitations(organization_id) WHERE status = 'pending';
CREATE INDEX idx_invitations_token ON invitations(token_hash) WHERE status = 'pending';

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
CREATE INDEX idx_jobs_retry ON jobs(next_retry_at) WHERE status = 'failed' AND attempt_count < max_attempts;

-- Notifications
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, created_at DESC) WHERE read_at IS NULL;
CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);

-- Audit Logs
CREATE INDEX idx_audit_logs_org ON audit_logs(organization_id, created_at DESC);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action, created_at DESC);

-- File Uploads
CREATE INDEX idx_file_uploads_org ON file_uploads(organization_id);
CREATE INDEX idx_file_uploads_status ON file_uploads(status) WHERE status = 'pending';
CREATE INDEX idx_file_uploads_expires ON file_uploads(expires_at) WHERE status = 'pending';

-- API Keys
CREATE INDEX idx_api_keys_org ON api_keys(organization_id) WHERE revoked_at IS NULL;
CREATE INDEX idx_api_keys_prefix ON api_keys(key_prefix) WHERE revoked_at IS NULL;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE users IS 'All user accounts. Soft delete with deleted_at.';
COMMENT ON TABLE organizations IS 'Tenant organizations. Soft delete with deleted_at.';
COMMENT ON TABLE workspaces IS 'Workspaces within orgs. Soft delete with deleted_at.';
COMMENT ON TABLE projects IS 'Projects within workspaces. Soft delete with deleted_at.';
COMMENT ON TABLE datasets IS 'Event log datasets. Soft delete with deleted_at.';
COMMENT ON TABLE jobs IS 'Background job queue for async processing.';
COMMENT ON TABLE audit_logs IS 'Immutable audit trail. No soft delete.';

COMMENT ON COLUMN users.password_hash IS 'NULL for OAuth users who login via external provider';
COMMENT ON COLUMN organizations.settings_json IS 'Flexible org-level settings as JSON';
COMMENT ON COLUMN datasets.column_mapping IS 'User-defined mapping of CSV columns to event log fields';
COMMENT ON COLUMN jobs.job_data IS 'Input parameters for the job processor';
COMMENT ON COLUMN jobs.result_data IS 'Output data from completed job';
