# Workspace & Project Management: End-to-End Architecture

This document details the logical architecture, data models, and user flows for the Workspace & Project Management modules.

## 1. Entity Relationship Diagram (ERD)
The core hierarchy follows a standard SaaS Multi-tenancy model: `Organization` → `Workspace` → `Project`.

```mermaid
erDiagram
    Organization ||--|{ Workspace : "owns"
    Organization ||--|{ User : "contains"
    
    User ||--|{ WorkspaceMember : "has membership"
    Workspace ||--|{ WorkspaceMember : "has members"
    
    Workspace ||--|{ Project : "contains"
    Project ||--|{ Dataset : "groups"
    Project ||--|{ Analysis : "groups"
    
    Dataset ||--|{ ProcessCase : "contains"
    Dataset ||--|{ ProcessModel : "source for"

    %% Attributes
    Organization {
        string id PK
        string name
        string plan "free/pro"
        string slug
    }

    User {
        string id PK
        string email
        string org_id FK
        string auth_provider
    }

    Workspace {
        string id PK
        string org_id FK "Owner Org"
        string name
        text description
    }

    WorkspaceMember {
        string id PK
        string workspace_id FK
        string user_id FK
        string role "owner|admin|member|viewer"
    }

    Project {
        string id PK
        string workspace_id FK
        string name
        json tags_json
        int total_files
    }

    Dataset {
        string id PK
        string project_id FK
        string name
        string status "pending|ready|error"
        string source_file
    }
```

## 2. System Architecture & Data Flow

This diagram illustrates how a user interacts with the system to create projects and how data flows through the backend services.

```mermaid
graph TD
    %% Actors
    User([User])
    
    %% Frontend Layer
    subgraph Frontend ["Frontend (Explorer/Platform)"]
        UI_Context["Workspace Context Provider"]
        UI_Projects["Project List Page"]
        UI_Create["Create Project Modal"]
        API_Client["API Client (Axios)"]
    end

    %% Backend Layer
    subgraph Backend ["Backend API"]
        Router["/api/v1/projects"]
        AuthService["AuthorizationService"]
        Repo["ProjectRepository"]
        Storage["StorageService"]
    end

    %% Data Layer
    subgraph Database ["Persistence"]
        DB[(PostgreSQL/SQLite)]
        FS[("File Storage (Local/S3)")]
    end

    %% Flows
    User -->|1. Selects Workspace| UI_Context
    UI_Context -->|2. Stores Active WorkspaceID| UI_Projects
    
    User -->|3. Clicks 'New Project'| UI_Create
    UI_Create -->|4. POST /projects (name, workspace_id)| API_Client
    API_Client -->|5. HTTP Request| Router
    
    Router -->|6. Check Permissions| AuthService
    AuthService -->|7. Verify WorkspaceMember| DB
    
    AuthService -- "Valid (Admin/Editor)" --> Router
    Router -->|8. Create Record| Repo
    
    Repo -->|9. INSERT Project| DB
    Repo -->|10. Create Project Folder| Storage
    Storage -->|11. mkdir {workspace_id}/{project_id}| FS
    
    Repo -- "Success" --> Router
    Router -- "201 Created" --> API_Client
    API_Client -->|12. Refresh List| UI_Projects
```

## 3. Authorization Logic (RBAC)

The `AuthorizationService` enforces permissions at each level of the hierarchy.

```mermaid
flowchart TD
    Start([Request Resource]) --> AuthCheck{Is Authenticated?}
    AuthCheck -- No --> 401[401 Unauthorized]
    AuthCheck -- Yes --> OrgCheck{User in Resource Org?}
    
    OrgCheck -- No --> 403[403 Forbidden - Org Mismatch]
    OrgCheck -- Yes --> LevelCheck{Resource Level}
    
    LevelCheck -- "Workspace Scoped" --> WS_Member{Is Workspace Member?}
    
    WS_Member -- No --> 403_WS[403 Forbidden - Not Member]
    WS_Member -- Yes --> RoleCheck{Has Required Role?}
    
    RoleCheck -- No (e.g. Viewer trying to Edit) --> 403_Role[403 Forbidden - Insufficient Role]
    RoleCheck -- Yes --> Success([Access Granted])
```

## 4. Storage Structure
Physical storage mirrors the logical hierarchy to ensure isolation and easy cleanup.

```mermaid
graph LR
    Root["/storage_root/"]
    
    subgraph Tenant_A [Organization A]
        W1[Workspace_1]
        W2[Workspace_2]
        
        subgraph P1 [Project 1]
            D1[Dataset_Alpha.csv]
            D2[Dataset_Beta.xes]
        end
        
        subgraph P2 [Project 2]
            D3[Log_2024.csv]
        end
    end
    
    Root --> Tenant_A
    Tenant_A --> W1
    Tenant_A --> W2
    W1 --> P1
    W1 --> P2
    P1 --> D1
    P1 --> D2
    W2 --> D3
```
