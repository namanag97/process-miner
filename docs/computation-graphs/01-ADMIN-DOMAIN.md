# Admin Domain - Computation Graph

## Domain Overview

The Admin domain handles multi-tenant authentication, organizations, workspaces, and projects.

## Entity Relationship

```mermaid
erDiagram
    User ||--o{ Organization : owns
    User ||--o{ WorkspaceMember : belongs_to
    Organization ||--o{ Workspace : contains
    Workspace ||--o{ WorkspaceMember : has
    Workspace ||--o{ Project : contains
    Project ||--o{ Dataset : contains
    WorkspaceMember }|--|| Role : has

    User {
        uuid id PK
        string email
        string hashed_password
        bool is_active
        datetime created_at
    }

    Organization {
        uuid id PK
        string name
        string billing_plan
        int usage_limit
        uuid owner_id FK
    }

    Workspace {
        uuid id PK
        string name
        string description
        uuid organization_id FK
    }

    WorkspaceMember {
        uuid id PK
        uuid workspace_id FK
        uuid user_id FK
        enum role
    }

    Project {
        uuid id PK
        string name
        string description
        uuid workspace_id FK
    }

    Role {
        string name
        string[] permissions
    }
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant AuthRouter
    participant AuthService
    participant JWTService
    participant Database

    %% Login Flow
    Client->>AuthRouter: POST /auth/login
    AuthRouter->>AuthService: authenticate(email, password)
    AuthService->>Database: get_user_by_email()
    Database-->>AuthService: User
    AuthService->>AuthService: verify_password()

    alt Password Valid
        AuthService->>JWTService: create_access_token(user_id)
        JWTService-->>AuthService: access_token
        AuthService->>JWTService: create_refresh_token(user_id)
        JWTService-->>AuthService: refresh_token
        AuthService-->>AuthRouter: TokenPair
        AuthRouter-->>Client: {access_token, refresh_token}
    else Invalid Credentials
        AuthService-->>AuthRouter: AuthenticationError
        AuthRouter-->>Client: 401 Unauthorized
    end

    %% Token Refresh Flow
    Client->>AuthRouter: POST /auth/refresh
    AuthRouter->>JWTService: decode_refresh_token()
    JWTService-->>AuthRouter: user_id

    alt Token Valid
        AuthRouter->>JWTService: create_access_token(user_id)
        JWTService-->>AuthRouter: new_access_token
        AuthRouter-->>Client: {access_token}
    else Token Expired
        AuthRouter-->>Client: 401 Token Expired
    end
```

## JWT Token Structure

```mermaid
graph TB
    subgraph "Access Token (15 min)"
        AT_HEAD[Header]
        AT_PAY[Payload]
        AT_SIG[Signature]

        AT_HEAD --> AT_ALG[alg: HS256]
        AT_HEAD --> AT_TYP[typ: JWT]

        AT_PAY --> AT_SUB[sub: user_id]
        AT_PAY --> AT_EXP[exp: timestamp]
        AT_PAY --> AT_TYPE[type: access]
    end

    subgraph "Refresh Token (7 days)"
        RT_HEAD[Header]
        RT_PAY[Payload]
        RT_SIG[Signature]

        RT_PAY --> RT_SUB[sub: user_id]
        RT_PAY --> RT_EXP[exp: timestamp]
        RT_PAY --> RT_TYPE[type: refresh]
    end
```

## Authorization Check Flow

```mermaid
flowchart TD
    REQ[Incoming Request] --> EXTRACT[Extract JWT Token]
    EXTRACT --> DECODE[Decode & Validate Token]

    DECODE --> VALID{Token Valid?}
    VALID -->|No| REJECT[401 Unauthorized]
    VALID -->|Yes| GET_USER[Get User from DB]

    GET_USER --> ACTIVE{User Active?}
    ACTIVE -->|No| REJECT
    ACTIVE -->|Yes| CHECK_RESOURCE[Check Resource Permission]

    CHECK_RESOURCE --> GET_WS[Get Workspace ID from Request]
    GET_WS --> GET_MEMBER[Get WorkspaceMember Record]

    GET_MEMBER --> HAS_MEMBER{Member Exists?}
    HAS_MEMBER -->|No| REJECT_403[403 Forbidden]
    HAS_MEMBER -->|Yes| CHECK_ROLE[Check Role Permission]

    CHECK_ROLE --> ROLE_MAP{Required Permission?}
    ROLE_MAP -->|owner| OWNER_CHECK[User is Owner?]
    ROLE_MAP -->|admin| ADMIN_CHECK[Role >= Admin?]
    ROLE_MAP -->|editor| EDITOR_CHECK[Role >= Editor?]
    ROLE_MAP -->|viewer| VIEWER_CHECK[Role >= Viewer?]

    OWNER_CHECK -->|Yes| ALLOW[Allow Request]
    OWNER_CHECK -->|No| REJECT_403
    ADMIN_CHECK -->|Yes| ALLOW
    ADMIN_CHECK -->|No| REJECT_403
    EDITOR_CHECK -->|Yes| ALLOW
    EDITOR_CHECK -->|No| REJECT_403
    VIEWER_CHECK -->|Yes| ALLOW
    VIEWER_CHECK -->|No| REJECT_403
```

## Organization Management

```mermaid
flowchart LR
    subgraph "Create Organization"
        CO_REQ[POST /organizations] --> CO_VAL[Validate Input]
        CO_VAL --> CO_CREATE[Create Org Record]
        CO_CREATE --> CO_WS[Create Default Workspace]
        CO_WS --> CO_MEMBER[Add Owner as Member]
        CO_MEMBER --> CO_RESP[Return Organization]
    end

    subgraph "List Organizations"
        LO_REQ[GET /organizations] --> LO_AUTH[Get User from Token]
        LO_AUTH --> LO_QUERY[Query Orgs where Owner = User]
        LO_QUERY --> LO_RESP[Return Organization List]
    end

    subgraph "Update Organization"
        UO_REQ[PATCH /organizations/:id] --> UO_AUTH[Verify Owner]
        UO_AUTH --> UO_UPDATE[Update Fields]
        UO_UPDATE --> UO_RESP[Return Updated Org]
    end
```

## Workspace RBAC Model

```mermaid
graph TB
    subgraph "Permission Matrix"
        direction LR

        subgraph "Role: Owner"
            O_ALL[All Permissions]
            O_DELETE[Delete Workspace]
            O_TRANSFER[Transfer Ownership]
        end

        subgraph "Role: Admin"
            A_MANAGE[Manage Members]
            A_CREATE[Create Projects]
            A_DELETE_PROJ[Delete Projects]
        end

        subgraph "Role: Editor"
            E_EDIT[Edit Resources]
            E_UPLOAD[Upload Datasets]
            E_ANALYZE[Run Analysis]
        end

        subgraph "Role: Viewer"
            V_VIEW[View Resources]
            V_EXPORT[Export Data]
        end
    end

    O_ALL --> A_MANAGE
    O_ALL --> A_CREATE
    O_ALL --> A_DELETE_PROJ

    A_MANAGE --> E_EDIT
    A_CREATE --> E_EDIT
    A_DELETE_PROJ --> E_EDIT

    E_EDIT --> V_VIEW
    E_UPLOAD --> V_VIEW
    E_ANALYZE --> V_EXPORT
```

## Project Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Created: POST /projects
    Created --> Active: Add Datasets
    Active --> Active: Run Analysis
    Active --> Archived: Archive Project
    Archived --> Active: Restore Project
    Archived --> [*]: Delete Project

    note right of Created
        Empty project with
        name and description
    end note

    note right of Active
        Has datasets and/or
        analysis results
    end note
```

## Workspace Member Operations

```mermaid
sequenceDiagram
    participant Admin
    participant API
    participant AuthService
    participant Database
    participant Notification

    %% Add Member
    Admin->>API: POST /workspaces/:id/members
    API->>AuthService: require_workspace_permission(admin)
    AuthService-->>API: Authorized

    API->>Database: Check user exists
    Database-->>API: User found

    API->>Database: Check not already member
    Database-->>API: Not a member

    API->>Database: Create WorkspaceMember
    Database-->>API: Member created

    API->>Notification: Send invite email
    API-->>Admin: 201 Member Added

    %% Update Role
    Admin->>API: PATCH /workspaces/:id/members/:userId
    API->>AuthService: require_workspace_permission(admin)
    API->>Database: Update role
    API-->>Admin: 200 Role Updated

    %% Remove Member
    Admin->>API: DELETE /workspaces/:id/members/:userId
    API->>AuthService: require_workspace_permission(admin)
    API->>Database: Delete WorkspaceMember
    API-->>Admin: 204 Member Removed
```

## API Endpoints Structure

```mermaid
graph TD
    subgraph "Auth Endpoints"
        AUTH_LOGIN[POST /auth/login]
        AUTH_REFRESH[POST /auth/refresh]
        AUTH_LOGOUT[POST /auth/logout]
        AUTH_ME[GET /auth/me]
    end

    subgraph "Organization Endpoints"
        ORG_LIST[GET /organizations]
        ORG_CREATE[POST /organizations]
        ORG_GET[GET /organizations/:id]
        ORG_UPDATE[PATCH /organizations/:id]
        ORG_DELETE[DELETE /organizations/:id]
    end

    subgraph "Workspace Endpoints"
        WS_LIST[GET /workspaces]
        WS_CREATE[POST /workspaces]
        WS_GET[GET /workspaces/:id]
        WS_UPDATE[PATCH /workspaces/:id]
        WS_DELETE[DELETE /workspaces/:id]
        WS_MEMBERS[GET /workspaces/:id/members]
        WS_ADD_MEMBER[POST /workspaces/:id/members]
        WS_REMOVE_MEMBER[DELETE /workspaces/:id/members/:userId]
    end

    subgraph "Project Endpoints"
        PROJ_LIST[GET /projects]
        PROJ_CREATE[POST /projects]
        PROJ_GET[GET /projects/:id]
        PROJ_UPDATE[PATCH /projects/:id]
        PROJ_DELETE[DELETE /projects/:id]
    end
```

## Key Files Reference

| Component | Path |
|-----------|------|
| User Models | `src/infra/users/models.py` |
| Auth Service | `src/infra/users/auth_service.py` |
| JWT Utilities | `src/infra/core/security.py` |
| Organization Models | `src/infra/organizations/models.py` |
| Workspace Models | `src/infra/workspaces/models.py` |
| Project Models | `src/infra/projects/models.py` |
| Permission Checks | `src/infra/core/permissions.py` |
| Auth Router | `src/api/routers/auth.py` |
| Organizations Router | `src/api/routers/organizations.py` |
| Workspaces Router | `src/api/routers/workspaces.py` |
| Projects Router | `src/api/routers/projects.py` |
