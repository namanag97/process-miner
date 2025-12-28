# Process Mining SaaS Platform

A comprehensive Process Mining platform powered by **PM4Py** with a FastAPI backend and TypeScript SDK.

## 🚀 Quick Start

```bash
# Install all dependencies
make install

# Start the backend
make dev

# Run all checks
make check
```

## Project Structure

```
system/
├── backend/          # FastAPI backend (Python)
│   ├── src/          # Application code
│   └── tests/        # Test suite
├── sdk/              # TypeScript SDK
│   └── src/          # SDK source
└── docs/             # Documentation
```

## Development Commands

| Command           | Description                     |
| ----------------- | ------------------------------- |
| `make install`    | Install all dependencies        |
| `make lint`       | Run linters (Ruff + ESLint)     |
| `make typecheck`  | Run type checkers (mypy + tsc)  |
| `make security`   | Run security scans (Bandit)     |
| `make test`       | Run all tests (pytest + vitest) |
| `make check`      | Run lint + typecheck + security |
| `make all`        | Run check + test (full CI)      |
| `make dev`        | Start development server        |
| `make pre-commit` | Install pre-commit hooks        |

## API Access

| Endpoint                           | Description        |
| ---------------------------------- | ------------------ |
| http://localhost:8001/docs         | Swagger UI         |
| http://localhost:8001/redoc        | ReDoc              |
| http://localhost:8001/metrics      | Prometheus metrics |
| http://localhost:8001/health/live  | Liveness probe     |
| http://localhost:8001/health/ready | Readiness probe    |

## Key Features

- **Event Log Management**: Upload CSV/XES files, quality assessment
- **Process Discovery**: Alpha, Heuristic, Inductive miners
- **Conformance Checking**: Fitness, precision, alignments
- **Performance Analysis**: Bottleneck detection, KPIs
- **Object-Centric PM**: OCEL 2.0 support
- **Organizational Mining**: SNA, role discovery

## Components

### [Backend](./backend/)

FastAPI application with 17 API routers and 150+ endpoints.

### [SDK](./sdk/)

TypeScript SDK with 13 domain-specific clients following business-verb naming.

## License

MIT
