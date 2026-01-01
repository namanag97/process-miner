# ADR-002: PM4Py as Core Engine

## Status

Accepted

## Context

Process mining requires sophisticated algorithms for:

- Process model discovery (Alpha, Inductive, Heuristics miners)
- Conformance checking (Token replay, Alignments)
- Performance analysis (Bottleneck detection, SLA monitoring)
- Visualization (Petri nets, BPMN, DFG)

Building these from scratch would require years of development and domain expertise.

## Decision

We use **PM4Py** as our core process mining engine.

### Rationale

1. **Industry Standard** - Most widely used open-source process mining library
2. **Comprehensive** - Covers all major process mining operations
3. **Research-Backed** - Developed by process mining researchers
4. **Active Development** - Regular updates and new algorithms
5. **MIT License** - Permissive licensing for commercial use

### Integration Strategy

```python
# PM4Py operations wrapped in service layer
class MiningService:
    @staticmethod
    async def discover_model(log: EventLog, miner: MinerType) -> ProcessModel:
        # Convert our domain model to PM4Py format
        df = await EventLogLoader.load(log.id)

        # Execute PM4Py in thread pool (CPU-bound)
        net, im, fm = await asyncio.to_thread(
            pm4py.discover_petri_net_inductive,
            df
        )

        # Convert back to our domain model
        return ProcessModel.from_pm4py(net, im, fm)
```

### Abstraction Layer

We wrap PM4Py with our own service layer to:

- Provide consistent async interface
- Handle data format conversions
- Add caching and error handling
- Enable potential future library swaps

## Consequences

### Positive

- **Mature algorithms** - Well-tested implementations
- **Rapid development** - Focus on product rather than algorithms
- **Research parity** - Access to latest academic advances
- **Community support** - Active user community

### Negative

- **Dependency risk** - Tight coupling to external library
- **Performance overhead** - Generic library may not be optimized for our use cases
- **API changes** - PM4Py updates may require code changes
- **Sync operations** - PM4Py is synchronous, requires bridging

### Mitigation

- Service layer abstracts PM4Py from rest of codebase
- Pinned versions with careful upgrade process
- Thread pool execution for async integration
