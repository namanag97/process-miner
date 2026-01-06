# Admin Domain

User administration and multi-tenancy management.

## Responsibilities
- Authentication (JWT)
- Organizations (multi-tenancy root)
- Workspaces (work contexts)
- Projects (containers for datasets)
- Users and roles

## Usage
```python
from src.domains.admin.models import Organization, Workspace, User
from src.domains.admin.services import AuthorizationService
```
