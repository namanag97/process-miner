---
description: Start the entire Temporal stack (Server + Workers)
---
This workflow starts the Temporal infrastructure required for async tasks. This is separate from the main Backend API server.

1. Start Temporal Server (Docker)
2. Start Python Workers

```bash
cd backend
make temporal-up
make temporal-workers
```

> **Note**: You can stop everything with `make temporal-down` and `make temporal-stop`.
