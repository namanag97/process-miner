# Admin Domain

**Owner**: Multi-tenancy & User Management  
**Bounded Context**: Authentication, Authorization, Organization Hierarchy

## Responsibilities

- User authentication (JWT-based)
- Organization management (root of multi-tenancy)
- Workspace management (collaborative contexts)
- Project management (dataset/analysis containers)
- Role-based access control (RBAC)
- Authorization services

## Models

| Model | Table | Description |
|-------|-------|-------------|
| `Organization` | `organizations` | Multi-tenant root entity |
| `User` | `users` | User accounts with auth providers |
| `Workspace` | `workspaces` | Work contexts within orgs |
| `WorkspaceMember` | `workspace_members` | User-workspace membership with roles |
| `Project` | `projects` | Containers for datasets/analyses |

## APIs

- `POST /auth/login` - JWT authentication
- `CRUD /organizations` - Organization management
- `CRUD /workspaces` - Workspace CRUD with RBAC
- `CRUD /projects` - Project management

## Dependencies

**Outbound**:
- Platform infrastructure (`AsyncJob`, `ErrorLog`)
- Shared utilities

**Inbound**:
- Datasets domain (references `Project`)
- Analysis domain (indirectly via datasets)

## Domain Rules

1. Organizations own workspaces and users
2. Workspaces contain projects and have members with roles
3. Projects belong to workspaces
4. Authorization hierarchy: Org → Workspace → Project → Dataset
5. Roles: `owner`, `admin`, `editor`, `viewer`

## Migration Notes

**Migrated from**:
- `src/platform/auth/` → `src/domains/admin/api/auth.py`
- `src/platform/organizations/` → `src/domains/admin/api/organizations.py`
- `src/platform/workspaces/` → `src/domains/admin/api/workspaces.py`
- `src/platform/projects/` → `src/domains/admin/api/projects.py`
- `src/platform/models.py` (partial) → `src/domains/admin/models/`

**Backward compatibility**: Legacy imports still work via re-exports.
