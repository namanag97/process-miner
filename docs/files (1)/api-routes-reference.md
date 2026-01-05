# API Routes Reference - Process Mining MVP

> Base URL: `/api/v1`

---

## 📋 Route Summary

| Module | Routes | Auth Required |
|--------|--------|---------------|
| Health | 3 | ❌ No |
| Auth | 13 | Partial |
| Organizations | 11 | ✅ Yes |
| Workspaces | 9 | ✅ Yes |
| Projects | 7 | ✅ Yes |
| Datasets | 20 | ✅ Yes |
| Jobs | 4 | ✅ Yes |
| Admin | 8 | ✅ Yes (Admin only) |
| **Total** | **75** | |

---

## 💚 Health & System

| Method | Route | Description | Auth |
|--------|-------|-------------|------|
| `GET` | `/health` | Basic health check | ❌ |
| `GET` | `/health/ready` | Readiness (DB, S3, Redis connected) | ❌ |
| `GET` | `/health/live` | Liveness probe for k8s | ❌ |

---

## 🔐 Authentication

### Core Auth

| Method | Route | Description | Auth |
|--------|-------|-------------|------|
| `POST` | `/auth/register` | Create new account | ❌ |
| `POST` | `/auth/login` | Login, get JWT tokens | ❌ |
| `POST` | `/auth/logout` | Invalidate refresh token | ✅ |
| `POST` | `/auth/refresh` | Get new access token | 🔄 Refresh token |
| `POST` | `/auth/forgot-password` | Request password reset email | ❌ |
| `POST` | `/auth/reset-password` | Set new password with token | ❌ |
| `GET` | `/auth/me` | Get current user profile | ✅ |
| `PUT` | `/auth/me` | Update profile (name, etc.) | ✅ |
| `POST` | `/auth/change-password` | Change password (logged in) | ✅ |

### OAuth Providers

| Method | Route | Description | Auth |
|--------|-------|-------------|------|
| `GET` | `/auth/oauth/google` | Initiate Google OAuth flow | ❌ |
| `GET` | `/auth/oauth/google/callback` | Google OAuth callback | ❌ |
| `GET` | `/auth/oauth/github` | Initiate GitHub OAuth flow | ❌ |
| `GET` | `/auth/oauth/github/callback` | GitHub OAuth callback | ❌ |

---

## 🏢 Organizations

### Core Operations

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `GET` | `/organizations` | List user's organizations | Member |
| `POST` | `/organizations` | Create new organization | Any user |
| `GET` | `/organizations/:org_id` | Get organization details | Member |
| `PUT` | `/organizations/:org_id` | Update organization | Admin |
| `DELETE` | `/organizations/:org_id` | Delete organization | Owner |

### Members

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `GET` | `/organizations/:org_id/members` | List members | Member |
| `POST` | `/organizations/:org_id/members/invite` | Invite user | Admin |
| `DELETE` | `/organizations/:org_id/members/:user_id` | Remove member | Admin |
| `PUT` | `/organizations/:org_id/members/:user_id/role` | Change role | Owner |

### Billing (Future)

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `GET` | `/organizations/:org_id/billing` | Get billing info | Admin |
| `GET` | `/organizations/:org_id/usage` | Get usage stats | Admin |

---

## 📂 Workspaces

### Core Operations

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `GET` | `/workspaces` | List workspaces | Member |
| `POST` | `/workspaces` | Create workspace | Org Admin |
| `GET` | `/workspaces/:ws_id` | Get workspace details | Member |
| `PUT` | `/workspaces/:ws_id` | Update workspace | WS Admin |
| `DELETE` | `/workspaces/:ws_id` | Delete workspace | WS Owner |

**Query Parameters:**
- `?org_id=xxx` - Filter by organization

### Members

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `GET` | `/workspaces/:ws_id/members` | List members | Member |
| `POST` | `/workspaces/:ws_id/members` | Add member | Admin |
| `PUT` | `/workspaces/:ws_id/members/:user_id` | Update role | Admin |
| `DELETE` | `/workspaces/:ws_id/members/:user_id` | Remove member | Admin |

**Workspace Roles:**
- `owner` - Full control
- `admin` - Manage members, all CRUD
- `editor` - Create/edit projects & datasets
- `analyst` - View & analyze only
- `viewer` - Read-only

---

## 📁 Projects

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `GET` | `/projects` | List projects | WS Member |
| `POST` | `/projects` | Create project | Editor+ |
| `GET` | `/projects/:proj_id` | Get project details | Viewer+ |
| `PUT` | `/projects/:proj_id` | Update project | Editor+ |
| `DELETE` | `/projects/:proj_id` | Delete project | Admin+ |
| `POST` | `/projects/:proj_id/archive` | Archive project | Editor+ |
| `POST` | `/projects/:proj_id/restore` | Restore project | Editor+ |

**Query Parameters:**
- `?workspace_id=xxx` - Filter by workspace (required)
- `?archived=true|false` - Filter archived
- `?search=term` - Search by name

---

## 📊 Datasets (Critical Module)

### CRUD Operations

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `GET` | `/datasets` | List datasets | Viewer+ |
| `GET` | `/datasets/:ds_id` | Get dataset with metadata | Viewer+ |
| `PUT` | `/datasets/:ds_id` | Update dataset info | Editor+ |
| `DELETE` | `/datasets/:ds_id` | Delete dataset | Admin+ |

**Query Parameters:**
- `?project_id=xxx` - Filter by project (required)
- `?status=xxx` - Filter by status

### Upload Operations

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `POST` | `/datasets` | Direct upload (≤50MB) | Editor+ |
| `POST` | `/datasets/presign` | Get presigned S3 URL | Editor+ |
| `POST` | `/datasets/:ds_id/uploaded` | Confirm upload complete | Editor+ |

**Request: POST /datasets/presign**
```
{
  "project_id": "uuid",
  "filename": "events.csv",
  "file_size": 104857600,
  "mime_type": "text/csv"
}
```

### Column Mapping (⚠️ Critical)

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `GET` | `/datasets/:ds_id/columns` | Get detected columns + suggestions | Viewer+ |
| `POST` | `/datasets/:ds_id/mapping` | Submit column mapping | Editor+ |
| `GET` | `/datasets/:ds_id/mapping` | Get current mapping | Viewer+ |
| `PUT` | `/datasets/:ds_id/mapping` | Update mapping | Editor+ |
| `POST` | `/datasets/:ds_id/preview` | Preview mapped data | Editor+ |

**Request: POST /datasets/:ds_id/mapping**
```
{
  "case_id_column": "order_id",
  "activity_column": "status",
  "timestamp_column": "created_at",
  "timestamp_format": "auto",       // or "ISO8601", "epoch", custom
  "resource_column": "handler",     // optional
  "additional_columns": ["region", "value"]  // optional
}
```

**Response: GET /datasets/:ds_id/columns**
```
{
  "columns": [
    {
      "name": "order_id",
      "dtype": "string",
      "sample_values": ["ORD-001", "ORD-002"],
      "null_percentage": 0.0,
      "unique_count": 15420
    }
  ],
  "suggestions": {
    "case_id": { "column": "order_id", "confidence": 0.92 },
    "activity": { "column": "status", "confidence": 0.87 },
    "timestamp": { "column": "created_at", "confidence": 0.95, "format": "ISO8601" },
    "resource": { "column": "handler", "confidence": 0.65 }
  },
  "requires_user_input": false
}
```

### Ingestion

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `POST` | `/datasets/:ds_id/ingest` | Start ingestion job | Editor+ |
| `POST` | `/datasets/:ds_id/reingest` | Re-ingest with new mapping | Editor+ |

### Data Access

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `GET` | `/datasets/:ds_id/events` | Query events (paginated) | Viewer+ |
| `GET` | `/datasets/:ds_id/cases` | Query cases (paginated) | Viewer+ |
| `GET` | `/datasets/:ds_id/activities` | List unique activities | Viewer+ |
| `GET` | `/datasets/:ds_id/metadata` | Get computed metadata | Viewer+ |

**Query Parameters for /events:**
- `?page=1&limit=100` - Pagination
- `?case_id=xxx` - Filter by case
- `?activity=xxx` - Filter by activity
- `?from=ISO_DATE&to=ISO_DATE` - Date range

### Export

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `POST` | `/datasets/:ds_id/export` | Export to CSV/XES (async) | Editor+ |
| `GET` | `/datasets/:ds_id/download` | Download original file | Editor+ |

---

## ⚡ Async Jobs

| Method | Route | Description | Permission |
|--------|-------|-------------|------------|
| `GET` | `/jobs` | List user's jobs | Any |
| `GET` | `/jobs/:job_id` | Get job status + progress | Owner |
| `POST` | `/jobs/:job_id/cancel` | Cancel running job | Owner |
| `GET` | `/jobs/:job_id/logs` | Get job execution logs | Owner |

**Query Parameters:**
- `?status=pending|running|completed|failed|cancelled`
- `?job_type=validation|ingestion|export|analysis`
- `?entity_type=dataset|project`
- `?entity_id=xxx`

**Response: GET /jobs/:job_id**
```
{
  "id": "uuid",
  "job_type": "ingestion",
  "status": "running",
  "progress": 45,
  "stage": "Transforming data",
  "entity_type": "dataset",
  "entity_id": "uuid",
  "created_at": "ISO_DATE",
  "started_at": "ISO_DATE",
  "error": null
}
```

---

## 🛡️ Admin (Superuser Only)

### User Management

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/admin/users` | List all users |
| `GET` | `/admin/users/:user_id` | Get user details |
| `PUT` | `/admin/users/:user_id` | Update user |
| `POST` | `/admin/users/:user_id/disable` | Disable user account |

### Error Management

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/admin/errors` | List error logs |
| `GET` | `/admin/errors/:error_id` | Get error details |
| `PUT` | `/admin/errors/:error_id/resolve` | Mark as resolved |

### System

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/admin/stats` | System-wide statistics |

---

## 🔒 Permission Matrix

| Role | View | Create | Edit | Delete | Manage Members |
|------|------|--------|------|--------|----------------|
| **viewer** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **analyst** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **editor** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **admin** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **owner** | ✅ | ✅ | ✅ | ✅ | ✅ + Transfer |

---

## 📊 Dataset Status Flow

```
PENDING → UPLOADED → VALIDATING → AWAITING_MAPPING → MAPPED → INGESTING → READY
                         ↓                                        ↓
                       ERROR ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
```

| Status | Description | Next Actions |
|--------|-------------|--------------|
| `PENDING` | Presigned URL generated, awaiting upload | Upload file |
| `UPLOADED` | File received, queued for validation | Wait |
| `VALIDATING` | Checking file, detecting columns | Wait |
| `AWAITING_MAPPING` | Needs user to map columns | POST /mapping |
| `MAPPED` | Mapping complete, ready to ingest | POST /ingest |
| `INGESTING` | Processing file into events | Wait |
| `READY` | Dataset available for analysis | Query data |
| `ERROR` | Something failed | Retry or delete |

---

## 🌐 Common Response Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `202` | Accepted (async job queued) |
| `400` | Bad request (validation error) |
| `401` | Unauthorized (no/invalid token) |
| `403` | Forbidden (no permission) |
| `404` | Not found |
| `409` | Conflict (duplicate, etc.) |
| `422` | Unprocessable entity |
| `429` | Rate limited |
| `500` | Server error |

---

## 📝 Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid column mapping",
    "details": [
      {
        "field": "timestamp_column",
        "message": "Column 'created' not found in dataset"
      }
    ]
  }
}
```
