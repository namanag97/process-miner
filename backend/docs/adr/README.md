# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) documenting significant architectural decisions made in this project.

## What is an ADR?

An ADR is a document that captures an important architectural decision, including the context, the decision, and the consequences.

## Index

| ADR                                       | Title                      | Status   |
| ----------------------------------------- | -------------------------- | -------- |
| [001](001-async-first-architecture.md)    | Async-First Architecture   | Accepted |
| [002](002-pm4py-as-core-engine.md)        | PM4Py as Core Engine       | Accepted |
| [003](003-event-log-as-aggregate-root.md) | EventLog as Aggregate Root | Accepted |
| [004](004-sqlite-for-simplicity.md)       | SQLite for Simplicity      | Accepted |
| [005](005-enterprise-error-handling.md)   | Enterprise Error Handling  | Accepted |

## Template

New ADRs should follow the template:

```markdown
# ADR-XXX: Title

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-YYY]

## Context

What is the issue that we're seeing that is motivating this decision?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

What becomes easier or more difficult to do because of this change?
```
