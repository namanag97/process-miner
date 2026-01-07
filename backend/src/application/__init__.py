"""Application Layer - CQRS Command/Query Handlers.

This layer contains:
- Commands: Write operations (create, update, delete)
- Queries: Read operations (list, get, search)
- Projections: Event-driven read model updates

All handlers are pure application logic, independent of web framework.
"""
