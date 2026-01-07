"""CQRS Projections - Event-Driven Read Model Updates.

Projections subscribe to domain events and update read models:
- Pre-compute expensive analytics
- Populate caches
- Build materialized views

The read models enable fast queries without touching the write database.

Usage:
    @event_publisher.subscribe(DatasetIngestedEvent)
    async def update_analytics_cache(event: DatasetIngestedEvent):
        await cache.set(f"dfg:{event.dataset_id}", compute_dfg(...))
"""
