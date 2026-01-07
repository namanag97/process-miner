# Backend Application CLAUDE.md

## Overview
Application layer containing use cases, projections, and queries. This layer orchestrates business logic without being tied to HTTP concerns.

## Directory Structure

```
application/
├── bootstrap.py         # Application startup initialization
├── projections/         # Read-model projections
│   └── analytics_cache.py  # Cached analytics data
└── queries/             # Query handlers
    └── analytics_queries.py  # Analytics query functions
```

## Key Concepts

### Bootstrap
Application initialization:
- Database setup
- Seed data creation
- Service initialization

### Projections
Read-optimized views of data:
- Pre-computed analytics
- Cached aggregations
- Denormalized data for fast reads

### Queries
Query handlers following CQRS pattern:
- Read operations separated from writes
- Optimized for specific use cases

## Pattern Examples

### Query Handler
```python
class GetDatasetAnalyticsQuery:
    async def execute(self, dataset_id: UUID) -> AnalyticsResult:
        # Check cache first
        cached = await cache.get(f"analytics:{dataset_id}")
        if cached:
            return cached

        # Compute and cache
        result = await compute_analytics(dataset_id)
        await cache.set(f"analytics:{dataset_id}", result)
        return result
```

### Projection
```python
class AnalyticsProjection:
    """Maintains pre-computed analytics for fast retrieval."""

    async def update(self, event: DatasetProcessed):
        analytics = await compute_analytics(event.dataset_id)
        await self.store.save(analytics)
```

## Import Rules

- Can import from `infra/` for infrastructure
- Can import from `shared/` for utilities
- Cannot import from `api/` (avoid circular deps)
- Cannot import from `features/` directly (use interfaces)
