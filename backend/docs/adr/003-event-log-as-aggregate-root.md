# ADR-003: EventLog as Aggregate Root

## Status

Accepted

## Context

In Domain-Driven Design, an Aggregate Root is an entity that:

- Other objects reference by identity
- Enforces invariants across its boundary
- Acts as the consistency boundary for transactions

Our domain has several candidate aggregates:

- Project (collection of event logs)
- EventLog (cases, events, analyses)
- ProcessModel (discovered models)
- Analysis (conformance results, statistics)

## Decision

**EventLog is the primary Aggregate Root** for process mining operations.

### Design

```
EventLog (Aggregate Root)
├── ProcessCase[] (Entity)
│   └── ProcessEvent[] (Value Object)
├── ProcessModel[] (Entity)
└── Analysis[] (Entity)
```

### Invariants Enforced

1. **Case integrity** - All events belong to a valid case
2. **Temporal consistency** - Events within a case are time-ordered
3. **Statistics consistency** - Counts match actual data
4. **Model validity** - Models reference valid event logs

### Implementation

```python
class EventLog(Base):
    """Aggregate root for process mining domain."""

    id: Mapped[str] = mapped_column(primary_key=True)

    # Aggregated children
    cases: Mapped[list["ProcessCase"]] = relationship(
        cascade="all, delete-orphan",  # Lifetime bound to aggregate
    )
    models: Mapped[list["ProcessModel"]] = relationship(
        cascade="all, delete-orphan",
    )

    def add_case(self, case: ProcessCase) -> None:
        """Add case with invariant validation."""
        if case.log_id != self.id:
            raise ValueError("Case must belong to this log")
        self.cases.append(case)
        self._update_statistics()
```

## Consequences

### Positive

- **Clear ownership** - Models, analyses belong to event logs
- **Transaction boundaries** - All changes through aggregate root
- **Cascade deletes** - Deleting log cleans up all related data
- **Consistency** - Statistics always match underlying data

### Negative

- **Large aggregates** - Event logs with millions of events are expensive to load
- **Lock contention** - Concurrent modifications require careful handling
- **Complex queries** - Some queries need to bypass aggregate

### Mitigation

- **Lazy loading** - Cases loaded on demand, not by default
- **Lightweight reads** - Statistics cached on aggregate, avoid loading cases
- **Repository pattern** - Data access abstracted for optimization
