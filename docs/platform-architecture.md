# Platform System Architecture

> **Complete System Architecture for Platform APIs**
> Generated: 2026-01-05
> Modules: Health, Jobs, Auth, Workspaces, Projects

## Overview

The Platform layer provides core SaaS infrastructure components that are independent of domain-specific features. It follows a modular monolith architecture with clear separation of concerns.

## Architecture Diagrams

### 1. System Overview - Platform Layer Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Browser[Web Browser]
        Mobile[Mobile App]
        CLI[CLI Tools]
    end

    subgraph "API Gateway Layer"
        Gateway[API Gateway<br/>FastAPI Application]
        Auth[JWT Authentication<br/>Middleware]
        CORS[CORS Handler]
        RateLimit[Rate Limiter]
    end

    subgraph "Platform APIs"
        HealthAPI[Health API<br/>/health/*]
        AuthAPI[Auth API<br/>/auth/*]
        WorkspaceAPI[Workspaces API<br/>/workspaces/*]
        ProjectAPI[Projects API<br/>/projects/*]
        JobsAPI[Jobs API<br/>/jobs/*]
    end

    subgraph "Authorization Layer"
        AuthZ[Authorization Service<br/>- RBAC<br/>- Permission Checks<br/>- Workspace Membership]
        Permissions[Permission System<br/>- Roles<br/>- Granular Permissions]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL Database<br/>- Organizations<br/>- Workspaces<br/>- Users<br/>- Projects<br/>- AsyncJobs)]
        Cache[(In-Memory Cache<br/>- Session Data<br/>- Auth Tokens)]
        FileStorage[File Storage<br/>- Uploads<br/>- Exports]
    end

    subgraph "External Services"
        OAuth[OAuth Providers<br/>- Google<br/>- GitHub]
        Email[Email Service<br/>- Notifications]
        Monitoring[Monitoring<br/>- Prometheus<br/>- Grafana]
    end

    Browser --> Gateway
    Mobile --> Gateway
    CLI --> Gateway

    Gateway --> Auth
    Auth --> CORS
    CORS --> RateLimit

    RateLimit --> HealthAPI
    RateLimit --> AuthAPI
    RateLimit --> WorkspaceAPI
    RateLimit --> ProjectAPI
    RateLimit --> JobsAPI

    AuthAPI --> AuthZ
    WorkspaceAPI --> AuthZ
    ProjectAPI --> AuthZ
    JobsAPI --> AuthZ

    AuthZ --> Permissions

    HealthAPI --> DB
    HealthAPI --> Cache
    AuthAPI --> DB
    WorkspaceAPI --> DB
    ProjectAPI --> DB
    JobsAPI --> DB

    AuthAPI --> OAuth
    AuthAPI --> Email
    HealthAPI --> Monitoring

    WorkspaceAPI --> FileStorage
    ProjectAPI --> FileStorage

    style HealthAPI fill:#90EE90
    style AuthAPI fill:#FFB6C1
    style WorkspaceAPI fill:#87CEEB
    style ProjectAPI fill:#DDA0DD
    style JobsAPI fill:#F0E68C
```

### 2. Database Schema - Complete Platform ERD

```mermaid
erDiagram
    Organization ||--o{ Workspace : "contains"
    Organization ||--o{ User : "employs"

    Workspace ||--o{ WorkspaceMember : "has members"
    Workspace ||--o{ Project : "contains"

    User ||--o{ WorkspaceMember : "member of"
    User ||--o{ AsyncJob : "creates"

    Project }o--|| Workspace : "belongs to"
    Project ||--o{ Dataset : "contains"

    AsyncJob }o--|| AsyncJob : "parent-child"

    Organization {
        string id PK "UUID"
        string name "Organization name"
        string slug UK "unique slug"
        string plan "free/pro/enterprise"
        datetime created_at
        datetime updated_at
    }

    Workspace {
        string id PK "UUID"
        string org_id FK "CASCADE to org"
        string name
        text description
        datetime created_at
        datetime updated_at
    }

    WorkspaceMember {
        string id PK "UUID"
        string workspace_id FK "CASCADE"
        string user_id FK "CASCADE"
        string role "owner/admin/editor/analyst/viewer"
        datetime joined_at
    }

    User {
        string id PK "UUID"
        string org_id FK "SET NULL"
        string email UK "unique"
        string name
        string auth_provider "local/oauth"
        string auth_provider_id
        string role "admin/member"
        string password_hash "bcrypt"
        datetime created_at
        datetime last_login_at
    }

    Project {
        string id PK "UUID"
        string workspace_id FK "SET NULL"
        string name
        text description
        text tags_json "JSON array"
        int total_files
        int total_analyses
        datetime created_at
        datetime updated_at
    }

    AsyncJob {
        string id PK "UUID"
        string task_id UK "Celery task ID"
        string user_id FK
        string job_type "ingestion/discovery/analysis"
        string status "pending/running/completed/failed"
        int progress "0-100"
        string stage
        string entity_type "project/dataset/analysis"
        string entity_id
        string parent_job_id FK "self-reference"
        text parameters_json
        text result_json
        text error
        text error_message
        datetime created_at
        datetime started_at
        datetime completed_at
        datetime updated_at
    }

    Dataset {
        string id PK "UUID"
        string project_id FK
        string name
        string file_path
        datetime created_at
    }

    ErrorLog {
        string id PK "UUID"
        datetime timestamp
        string level "error/warning/info"
        string exception_type
        text exception_message
        text stack_trace
        string request_id
        string user_id
        string endpoint
        string method
        text context_json
        boolean resolved
        datetime resolved_at
        string resolved_by
        text notes
    }
```

### 3. Health API - Endpoints & Architecture

```mermaid
graph TB
    subgraph "Health Check Endpoints"
        Live[GET /health/live<br/>Liveness Probe<br/>Returns 200 if alive]
        Ready[GET /health/ready<br/>Readiness Probe<br/>Checks DB connectivity]
        Startup[GET /health/startup<br/>Startup Probe<br/>Checks initialization]
        Detailed[GET /health/detailed<br/>Detailed Status<br/>All components]
        Basic[GET /health<br/>Basic Check<br/>Quick response]
    end

    subgraph "Health Checkers"
        DBCheck[Database Checker<br/>- Connection test<br/>- Latency measurement]
        CacheCheck[Cache Checker<br/>- In-memory cache<br/>- Optional component]
        PM4PyCheck[PM4Py Checker<br/>- Library availability<br/>- Version check]
        CircuitCheck[Circuit Breaker<br/>- Check circuit states<br/>- Degraded if open]
        DiskCheck[Disk Space<br/>- Check free space<br/>- Warn at 80%<br/>- Critical at 90%]
    end

    subgraph "Response Models"
        HealthStatus[HealthStatus<br/>- status: healthy/degraded/unhealthy<br/>- timestamp]
        ComponentHealth[ComponentHealth<br/>- name<br/>- status<br/>- latency_ms<br/>- message<br/>- details]
        DetailedResponse[DetailedHealthResponse<br/>- status<br/>- version<br/>- uptime_seconds<br/>- components[]]
    end

    subgraph "K8s Integration"
        K8s[Kubernetes<br/>- Liveness probe → restart pod<br/>- Readiness probe → route traffic<br/>- Startup probe → wait for init]
    end

    Live --> HealthStatus
    Ready --> DBCheck
    Ready --> HealthStatus
    Startup --> HealthStatus
    Basic --> HealthStatus

    Detailed --> DBCheck
    Detailed --> CacheCheck
    Detailed --> PM4PyCheck
    Detailed --> CircuitCheck
    Detailed --> DiskCheck
    Detailed --> DetailedResponse

    DBCheck --> ComponentHealth
    CacheCheck --> ComponentHealth
    PM4PyCheck --> ComponentHealth
    CircuitCheck --> ComponentHealth
    DiskCheck --> ComponentHealth

    Ready -.-> K8s
    Live -.-> K8s
    Startup -.-> K8s

    style Live fill:#90EE90
    style Ready fill:#FFD700
    style Startup fill:#87CEEB
    style Detailed fill:#DDA0DD
```

### 4. Auth API - Authentication & Authorization Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant API as Auth API
    participant DB as Database
    participant JWT as JWT Service
    participant OAuth as OAuth Provider

    %% Registration Flow
    rect rgb(220, 240, 255)
        Note over C,OAuth: User Registration
        C->>API: POST /auth/register<br/>{email, password, name, org_name}
        API->>DB: Check email exists
        alt Email exists
            DB-->>API: User found
            API-->>C: 400 Email already registered
        else New user
            DB-->>API: Not found
            API->>DB: CREATE Organization
            API->>DB: CREATE User (bcrypt password)
            API->>DB: CREATE Default Workspace
            API->>DB: CREATE WorkspaceMember (owner)
            DB-->>API: User created
            API->>JWT: Generate access + refresh tokens
            JWT-->>API: TokenPair
            API-->>C: 201 {access_token, refresh_token, user}
        end
    end

    %% Login Flow
    rect rgb(220, 255, 220)
        Note over C,OAuth: User Login
        C->>API: POST /auth/login<br/>{email, password}
        API->>DB: SELECT User WHERE email=xxx
        DB-->>API: User
        API->>API: verify_password(bcrypt)
        alt Password valid
            API->>DB: UPDATE last_login_at
            API->>JWT: Generate tokens
            JWT-->>API: TokenPair
            API-->>C: 200 {access_token, refresh_token, user}
        else Password invalid
            API-->>C: 401 Invalid credentials
        end
    end

    %% Get Current User
    rect rgb(255, 240, 220)
        Note over C,OAuth: Get User Context
        C->>API: GET /auth/me<br/>Authorization: Bearer {token}
        API->>JWT: Validate JWT token
        JWT-->>API: TokenData {sub, email}
        API->>DB: SELECT User WHERE id=xxx
        API->>DB: SELECT Organization
        API->>DB: SELECT Workspaces via WorkspaceMember
        DB-->>API: User + Org + Workspaces
        API-->>C: 200 CurrentUserResponse
    end

    %% Token Refresh
    rect rgb(240, 220, 255)
        Note over C,OAuth: Refresh Token
        C->>API: POST /auth/refresh<br/>{refresh_token}
        API->>JWT: validate_refresh_token()
        JWT-->>API: TokenData
        API->>DB: SELECT User WHERE id=xxx
        DB-->>API: User exists
        API->>JWT: Generate new tokens
        JWT-->>API: New TokenPair
        API-->>C: 200 {access_token, refresh_token}
    end

    %% OAuth Flow (Future)
    rect rgb(255, 220, 220)
        Note over C,OAuth: OAuth Login (Future)
        C->>API: GET /auth/oauth/google
        API-->>C: Redirect to Google
        C->>OAuth: Authenticate
        OAuth-->>C: Redirect with code
        C->>API: GET /auth/oauth/callback?code=xxx
        API->>OAuth: Exchange code for token
        OAuth-->>API: User info
        API->>DB: Find or create User
        API->>JWT: Generate tokens
        JWT-->>API: TokenPair
        API-->>C: 200 {access_token, refresh_token, user}
    end
```

### 5. Workspaces API - Complete CRUD Operations

```mermaid
classDiagram
    class WorkspaceRouter {
        +GET /workspaces
        +GET /workspaces/:id
        +POST /workspaces
        +PUT /workspaces/:id
        +DELETE /workspaces/:id
        +POST /workspaces/:id/projects/:projectId
        +DELETE /workspaces/:id/projects/:projectId
    }

    class AuthorizationService {
        -db: AsyncSession
        +get_workspace_membership(workspace_id, user_id)
        +require_workspace_membership(workspace_id, user_id)
        +check_permission(workspace_id, user_id, permission)
        +get_user_workspaces(user_id)
        +verify_org_access(user, org_id)
        +get_workspace_by_id(workspace_id)
        +verify_workspace_access(workspace_id, user, permission)
    }

    class PermissionSystem {
        <<Enumeration>>
        WORKSPACE_READ
        WORKSPACE_UPDATE
        WORKSPACE_INVITE
        WORKSPACE_REMOVE_MEMBERS
        WORKSPACE_DELETE
        PROJECT_CREATE
        PROJECT_READ
        PROJECT_UPDATE
        PROJECT_DELETE
    }

    class RoleSystem {
        <<RBAC Roles>>
        owner: full control (all permissions)
        admin: manage members, update (no delete)
        editor: read, update projects/workspaces
        analyst: read, create analyses
        viewer: read-only access
    }

    class WorkspaceSchemas {
        WorkspaceCreateRequest
        WorkspaceUpdateRequest
        WorkspaceResponse
        WorkspaceListResponse
        WorkspaceDetailResponse
    }

    WorkspaceRouter --> AuthorizationService : uses
    AuthorizationService --> PermissionSystem : checks
    AuthorizationService --> RoleSystem : validates
    WorkspaceRouter --> WorkspaceSchemas : request/response

    note for AuthorizationService "Enforces Row-Level Security\nand RBAC permissions"
    note for RoleSystem "Hierarchical permission inheritance:\nowner > admin > editor > analyst > viewer"
```

### 6. Projects API - CRUD with Authorization

```mermaid
stateDiagram-v2
    [*] --> Unauthenticated

    Unauthenticated --> Authenticated: Login with JWT

    Authenticated --> CheckWorkspace: Request project operation

    CheckWorkspace --> CheckMembership: Valid workspace
    CheckWorkspace --> Forbidden: Invalid workspace

    CheckMembership --> CheckPermission: User is member
    CheckMembership --> Forbidden: Not a member

    CheckPermission --> ExecuteOperation: Has permission
    CheckPermission --> Forbidden: Lacks permission

    state ExecuteOperation {
        [*] --> CreateProject: POST /projects
        [*] --> ListProjects: GET /projects
        [*] --> GetProject: GET /projects/:id
        [*] --> UpdateProject: PUT /projects/:id
        [*] --> DeleteProject: DELETE /projects/:id
        [*] --> AddDataset: POST /projects/:id/files/:datasetId
        [*] --> RemoveDataset: DELETE /projects/:id/files/:datasetId

        CreateProject --> Success: PROJECT_CREATE permission
        ListProjects --> Success: PROJECT_READ permission
        GetProject --> Success: PROJECT_READ permission
        UpdateProject --> Success: PROJECT_UPDATE permission
        DeleteProject --> Success: PROJECT_DELETE permission
        AddDataset --> Success: PROJECT_UPDATE permission
        RemoveDataset --> Success: PROJECT_UPDATE permission
    }

    ExecuteOperation --> [*]: Return response
    Forbidden --> [*]: 403 Forbidden

    note right of CheckMembership
        Checks workspace_members table
        for active membership
    end note

    note right of CheckPermission
        Validates user role against
        required permission using RBAC
    end note
```

### 7. Jobs API - Async Job Management

```mermaid
graph TB
    subgraph "Job Lifecycle"
        Create[Job Created<br/>status: pending]
        Start[Job Started<br/>status: running<br/>progress: 0-100]
        Progress[Job Progress<br/>Updates via SSE stream]
        Complete[Job Completed<br/>status: completed<br/>result_json populated]
        Failed[Job Failed<br/>status: failed<br/>error populated]
        Cancelled[Job Cancelled<br/>status: cancelled]
    end

    subgraph "Job Endpoints"
        List[GET /jobs<br/>List jobs with filters<br/>- job_type<br/>- status<br/>- entity_id<br/>- user_id]
        Get[GET /jobs/:id<br/>Get job status]
        Stream[GET /jobs/:id/stream<br/>SSE real-time updates]
        Cancel[DELETE /jobs/:id<br/>Cancel job]
    end

    subgraph "Job Types"
        Ingestion[ingestion<br/>Data upload & parsing]
        Discovery[discovery<br/>Process model generation]
        Analysis[analysis<br/>Process analytics]
        Conformance[conformance<br/>Conformance checking]
        Export[export<br/>Data export]
    end

    subgraph "SSE Streaming"
        SSEConnect[Client connects to SSE]
        SSEInitial[Send initial job state]
        SSESubscribe[Subscribe to Redis pubsub]
        SSEPoll[Fallback: Poll DB every 1s]
        SSEEvent[Send progress events]
        SSEClose[Connection closes on completion]
    end

    Create --> Start
    Start --> Progress
    Progress --> Complete
    Progress --> Failed
    Start --> Cancelled

    List -.-> Get
    Get -.-> Stream
    Stream --> SSEConnect
    SSEConnect --> SSEInitial
    SSEInitial --> SSESubscribe
    SSESubscribe --> SSEEvent
    SSESubscribe -.fallback.-> SSEPoll
    SSEPoll --> SSEEvent
    SSEEvent --> SSEClose

    Ingestion -.example.-> Create
    Discovery -.example.-> Create
    Analysis -.example.-> Create

    style Create fill:#FFD700
    style Start fill:#87CEEB
    style Progress fill:#90EE90
    style Complete fill:#98FB98
    style Failed fill:#FFB6C1
    style Cancelled fill:#D3D3D3
```

### 8. Complete API Endpoint Map

```mermaid
mindmap
  root((Platform APIs))
    Health API
      GET /health/live
      GET /health/ready
      GET /health/startup
      GET /health/detailed
      GET /health
    Auth API
      POST /auth/register
      POST /auth/login
      POST /auth/refresh
      POST /auth/logout
      GET /auth/me
      GET /auth/me/legacy (deprecated)
    Workspaces API
      GET /workspaces
      GET /workspaces/:id
      POST /workspaces
      PUT /workspaces/:id
      DELETE /workspaces/:id
      POST /workspaces/:id/projects/:projectId
      DELETE /workspaces/:id/projects/:projectId
    Projects API
      GET /projects
      GET /projects/:id
      POST /projects
      PUT /projects/:id
      DELETE /projects/:id
      POST /projects/:id/files/:datasetId
      DELETE /projects/:id/files/:datasetId
    Jobs API
      GET /jobs
      GET /jobs/:id
      GET /jobs/:id/stream (SSE)
      DELETE /jobs/:id
```

### 9. Authorization & Permission Flow

```mermaid
flowchart TD
    Start([API Request]) --> ExtractToken[Extract JWT from Header]
    ExtractToken --> ValidateToken{Valid Token?}

    ValidateToken -->|No| Unauthorized[401 Unauthorized]
    ValidateToken -->|Yes| ExtractUser[Extract User from Token]

    ExtractUser --> CheckWorkspace{Requires Workspace?}

    CheckWorkspace -->|No| ExecuteNoAuth[Execute Request]
    CheckWorkspace -->|Yes| GetWorkspace[Get Workspace from Request]

    GetWorkspace --> VerifyOrg{User in same Org?}

    VerifyOrg -->|No| Forbidden1[403 Forbidden: Wrong Org]
    VerifyOrg -->|Yes| GetMembership[Get WorkspaceMember]

    GetMembership --> IsMember{Is Member?}

    IsMember -->|No| Forbidden2[403 Forbidden: Not a Member]
    IsMember -->|Yes| GetRole[Get User Role]

    GetRole --> CheckPerm[Check Permission for Role]

    CheckPerm --> HasPerm{Has Permission?}

    HasPerm -->|No| Forbidden3[403 Forbidden: Insufficient Permission]
    HasPerm -->|Yes| ExecuteRequest[Execute Authorized Request]

    ExecuteRequest --> Success[200/201 Response]
    ExecuteNoAuth --> Success

    style Start fill:#90EE90
    style Success fill:#98FB98
    style Unauthorized fill:#FFB6C1
    style Forbidden1 fill:#FFB6C1
    style Forbidden2 fill:#FFB6C1
    style Forbidden3 fill:#FFB6C1
    style HasPerm fill:#FFD700
    style IsMember fill:#FFD700
```

### 10. Data Flow - Complete Platform Operations

```mermaid
sequenceDiagram
    participant U as User/Client
    participant G as API Gateway
    participant A as Auth Middleware
    participant W as Workspace API
    participant P as Projects API
    participant J as Jobs API
    participant AuthZ as Authorization Service
    participant DB as PostgreSQL
    participant Cache as Cache

    %% User Registration & Setup
    rect rgb(240, 248, 255)
        Note over U,Cache: New User Onboarding
        U->>G: POST /auth/register
        G->>A: Validate request
        A->>W: Create organization
        W->>DB: INSERT Organization
        A->>W: Create default workspace
        W->>DB: INSERT Workspace
        A->>DB: INSERT User (owner role)
        A->>DB: INSERT WorkspaceMember
        DB-->>A: All entities created
        A->>A: Generate JWT tokens
        A-->>U: 201 {tokens, user, workspace}
    end

    %% Authenticated Request
    rect rgb(255, 250, 240)
        Note over U,Cache: User Creates Project
        U->>G: POST /projects?workspace_id=xxx<br/>Authorization: Bearer {token}
        G->>A: Validate JWT
        A->>Cache: Check token cache
        Cache-->>A: Token valid
        A->>AuthZ: verify_workspace_access(workspace_id, user, PROJECT_CREATE)
        AuthZ->>DB: SELECT WorkspaceMember
        DB-->>AuthZ: Member found with 'editor' role
        AuthZ->>AuthZ: check_permission('editor', PROJECT_CREATE)
        AuthZ-->>A: ✓ Authorized
        A->>P: create_project()
        P->>DB: INSERT Project
        DB-->>P: Project created
        P-->>U: 201 ProjectResponse
    end

    %% Async Job Flow
    rect rgb(240, 255, 240)
        Note over U,Cache: User Starts Analysis Job
        U->>G: POST /datasets/:id/analyze
        G->>J: Create async job
        J->>DB: INSERT AsyncJob (status=pending)
        J-->>U: 202 {job_id}

        Note over U,J: User subscribes to job progress
        U->>G: GET /jobs/:id/stream
        G->>J: Start SSE stream
        J->>DB: SELECT AsyncJob
        J-->>U: SSE: initial state

        Note over J,DB: Background worker processes job
        J->>DB: UPDATE AsyncJob (status=running, progress=25)
        J-->>U: SSE: progress 25%
        J->>DB: UPDATE AsyncJob (progress=50)
        J-->>U: SSE: progress 50%
        J->>DB: UPDATE AsyncJob (progress=100, status=completed)
        J-->>U: SSE: completed
        U->>U: Close SSE connection
    end

    %% List Projects with RLS
    rect rgb(255, 240, 255)
        Note over U,Cache: User Lists Projects
        U->>G: GET /projects
        G->>A: Validate JWT
        A->>P: list_projects(user)
        P->>DB: SELECT Projects<br/>JOIN Workspaces<br/>JOIN WorkspaceMembers<br/>WHERE user_id=xxx
        Note over P,DB: Row-Level Security applied automatically
        DB-->>P: Projects user has access to
        P-->>U: 200 ProjectListResponse
    end
```

## Key Architectural Patterns

### 1. Multi-Tenancy Hierarchy
- **Organization** (root): Top-level tenant
- **Workspace**: Collaboration context within org
- **Projects**: Containers for work items
- **Row-Level Security**: Automatic filtering by workspace membership

### 2. Role-Based Access Control (RBAC)
- **Roles**: owner, admin, editor, analyst, viewer
- **Permissions**: Granular (e.g., `project:create`, `dataset:read`)
- **Hierarchy**: Roles inherit permissions from lower roles

### 3. Authentication & Authorization
- **JWT Tokens**: Stateless authentication with access + refresh tokens
- **Token Expiry**: Access tokens expire in 30 minutes, refresh in 7 days
- **Workspace Membership**: Checked on every workspace-scoped request
- **Permission Validation**: Role → Permission mapping enforced

### 4. Async Job Pattern
- **Job-Centric**: Long-running operations return job IDs
- **Progress Tracking**: Real-time updates via SSE streams
- **Status Enum**: pending → running → completed/failed/cancelled
- **Parent-Child**: Jobs can spawn sub-jobs for complex workflows

### 5. Health Monitoring
- **Kubernetes Probes**: liveness, readiness, startup
- **Component Health**: Database, cache, dependencies, disk
- **Circuit Breakers**: Graceful degradation when services fail
- **Monitoring Integration**: Prometheus metrics, Grafana dashboards

## Security Considerations

### Authentication
- ✅ Bcrypt password hashing (cost factor 12)
- ✅ JWT with RS256 (asymmetric signing)
- ✅ Refresh token rotation
- ✅ Token expiration enforcement
- 🔄 OAuth 2.0 integration (planned)
- 🔄 Multi-factor authentication (planned)

### Authorization
- ✅ Workspace-scoped RBAC
- ✅ Row-level security via ORM
- ✅ Permission checks on every mutation
- ✅ Organization boundary enforcement
- 🔄 Audit logging for all access (planned)

### API Security
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (SQLAlchemy)
- ✅ XSS prevention (no raw HTML)
- 🔄 API key authentication (planned)
- 🔄 IP whitelisting (planned)

## Performance Optimizations

### Database
- Indexed foreign keys on all relationships
- Composite indexes on frequently queried columns
- Eager loading with `selectin` strategy
- Connection pooling with async engine

### Caching
- In-memory cache for JWT token validation
- Query result caching for frequently accessed data
- Cache invalidation on mutations

### API Optimization
- Pagination on all list endpoints (max 100 items)
- Sparse fieldsets for large responses
- Async/await throughout for I/O operations
- Background job processing for heavy operations

## Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx / ALB]
    end

    subgraph "Application Tier"
        API1[FastAPI Instance 1]
        API2[FastAPI Instance 2]
        API3[FastAPI Instance 3]
    end

    subgraph "Worker Tier"
        W1[Celery Worker 1]
        W2[Celery Worker 2]
        W3[Celery Worker 3]
    end

    subgraph "Data Tier"
        PG[(PostgreSQL Primary)]
        PGR[(PostgreSQL Replica)]
        Redis[(Redis Cache)]
    end

    subgraph "Storage"
        S3[S3 / Object Storage]
    end

    subgraph "Monitoring"
        Prom[Prometheus]
        Graf[Grafana]
        Logs[Log Aggregation]
    end

    LB --> API1
    LB --> API2
    LB --> API3

    API1 --> PG
    API2 --> PG
    API3 --> PG

    API1 --> Redis
    API2 --> Redis
    API3 --> Redis

    W1 --> PG
    W2 --> PG
    W3 --> PG

    API1 --> S3
    API2 --> S3
    API3 --> S3

    PG -.replication.-> PGR

    API1 -.metrics.-> Prom
    API2 -.metrics.-> Prom
    API3 -.metrics.-> Prom
    W1 -.metrics.-> Prom
    W2 -.metrics.-> Prom
    W3 -.metrics.-> Prom

    Prom --> Graf

    API1 -.logs.-> Logs
    API2 -.logs.-> Logs
    API3 -.logs.-> Logs
```

## API Response Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST creating resource |
| 202 | Accepted | Async job started |
| 204 | No Content | Successful DELETE with no response body |
| 400 | Bad Request | Invalid input, validation errors |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Pydantic validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 503 | Service Unavailable | Dependency failure (DB down) |

## Testing Strategy

### Unit Tests
- Service layer logic
- Permission checking
- JWT token generation/validation
- Password hashing/verification

### Integration Tests
- API endpoint responses
- Database transactions
- Authorization flows
- Job lifecycle

### End-to-End Tests
- User registration → workspace creation → project creation
- Complete auth flow with token refresh
- Async job submission and completion
- Multi-user workspace collaboration

## Future Enhancements

### Planned Features
- 🔄 OAuth 2.0 integration (Google, GitHub, Microsoft)
- 🔄 Multi-factor authentication (TOTP, SMS)
- 🔄 API key management for programmatic access
- 🔄 Webhook notifications for job completion
- 🔄 Enhanced audit logging with event sourcing
- 🔄 Team management UI
- 🔄 Usage analytics and billing integration

### Scalability Improvements
- 🔄 Distributed caching with Redis Cluster
- 🔄 Database sharding by organization
- 🔄 Read replicas for reporting queries
- 🔄 CDN integration for static assets
- 🔄 GraphQL API alongside REST

---

**Document Version**: 1.0
**Last Updated**: 2026-01-05
**Maintained By**: Platform Team
