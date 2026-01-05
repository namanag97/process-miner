# Backend Architecture: Platform/Feature Separation

## Layer Structure

```
src/
├── platform/           # Generic SaaS infrastructure (NEVER imports features)
│   ├── core/           # Config, exceptions, security, logging
│   ├── infrastructure/ # Cache, rate limiting, tracing, tasks
│   ├── auth/           # Authentication router
│   ├── users/          # User models
│   ├── workspaces/     # Authorization, workspace management
│   ├── projects/       # Project management
│   ├── storage/        # File storage services
│   └── jobs/           # Background job infrastructure
│
├── features/           # Domain-specific (CAN import platform)
│   └── process_mining/
│       ├── models/     # Dataset, Analysis, ProcessCase, etc.
│       ├── discovery/  # Mining algorithms, DFG generation
│       ├── conformance/# Token replay, alignment
│       ├── analytics/  # Performance analytics, KPIs
│       ├── ingestion/  # Event log parsing
│       └── visualization/ # Graph rendering data
│
└── shared/             # Cross-cutting (both layers can import)
    ├── types/
    ├── utils/
    └── constants/
```

## Import Rules

```python
# ✅ ALLOWED
from src.platform.core.config import get_settings     # Platform internal
from src.features.process_mining.models import Dataset  # Feature internal
from src.platform.workspaces import AuthorizationService  # Feature → Platform

# ❌ FORBIDDEN
from src.features.* import *  # Platform NEVER imports features
```

## Backwards Compatibility

During migration, old imports still work with deprecation warnings:
- `src.core.*` → `src.platform.core.*`
- `src.infrastructure.*` → `src.platform.infrastructure.*`

## Verification

```bash
cd backend && source .venv/bin/activate
python -c "from src.platform.core.config import get_settings; print('OK')"
python -c "from src.features.process_mining.models import Dataset; print('OK')"
```
