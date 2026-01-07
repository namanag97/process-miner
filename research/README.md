# Research Agent System

This directory contains research outputs from **Research Agents** - cheaper/lighter AI agents that prepare work before expensive implementation agents take over.

## Philosophy

**Research agents can:**
- ✅ Read all code files
- ✅ Search the codebase
- ✅ Search the internet
- ✅ Edit markdown and text files
- ❌ **Cannot edit code files**

This separation ensures:
1. **Cost efficiency**: Use cheaper models for research
2. **Safety**: Research agents can't break anything
3. **Quality**: Implementation agents get pre-digested context
4. **Auditability**: All research is documented

## Directory Structure

```
research/
├── README.md                    # This file
├── requirements/                # Requirements clarification documents
│   └── {topic}_requirements.md
├── scope/                       # Scope definition documents
│   └── {topic}_scope.md
├── solutions/                   # Internet research findings
│   └── {topic}_research.md
├── benchmarks/                  # Industry benchmark analyses
│   └── {topic}_benchmark.md
├── codebase/                    # Deep codebase analysis reports
│   └── {topic}_analysis.md
└── RESEARCH_REPORT_{topic}.md   # Final compiled reports
```

## Workflows (Slash Commands)

| Command | Purpose | Output |
|---------|---------|--------|
| `/research_requirements` | Clarify ambiguous requirements | `requirements/{topic}_requirements.md` |
| `/research_scope` | Define implementation scope | `scope/{topic}_scope.md` |
| `/research_internet` | Find best practices online | `solutions/{topic}_research.md` |
| `/research_benchmark` | Compare against industry | `benchmarks/{topic}_benchmark.md` |
| `/research_codebase` | Deep dive into code for bugs | `codebase/{topic}_analysis.md` |
| `/research_report` | Compile all findings | `RESEARCH_REPORT_{topic}.md` |

## Typical Research Flow

```mermaid
graph TD
    A[User Request] --> B[/research_requirements]
    B --> C[/research_scope]
    C --> D[/research_internet]
    C --> E[/research_benchmark]
    C --> F[/research_codebase]
    D --> G[/research_report]
    E --> G
    F --> G
    G --> H[Implementation Agent]
```

### Step-by-Step

1. **Requirements** (`/research_requirements`): Parse request, identify ambiguities
2. **Scope** (`/research_scope`): Define boundaries, list affected files
3. **Internet** (`/research_internet`): Find best practices, stable solutions
4. **Benchmark** (`/research_benchmark`): Compare against process mining industry
5. **Codebase** (`/research_codebase`): Find bugs, patterns, improvement opportunities
6. **Report** (`/research_report`): Compile everything for implementation agent

## Usage Examples

### Finding Bugs
```
User: Find bugs in the dataset upload flow

Agent runs:
1. /research_codebase upload ingestion
2. /research_report upload_bugs
```

### Implementing New Feature
```
User: Add real-time collaboration to workspaces

Agent runs:
1. /research_requirements realtime_collab
2. /research_scope realtime_collab
3. /research_internet websockets fastapi react
4. /research_benchmark collaboration_features
5. /research_report realtime_collab
```

### Performance Improvement
```
User: Make process discovery faster

Agent runs:
1. /research_codebase discovery performance
2. /research_benchmark discovery_algorithms
3. /research_internet pm4py optimization
4. /research_report discovery_performance
```

## Report Quality Checklist

Before handing off to implementation agent, verify:

- [ ] All ambiguities resolved or documented as assumptions
- [ ] Affected files enumerated with paths
- [ ] Bugs prioritized (Critical/Major/Minor or P0/P1/P2)
- [ ] Best practices cited with sources
- [ ] Recommendations are actionable
- [ ] Handoff notes include "what to do first"

## For Implementation Agents

When you receive a research report:

1. Read the **Executive Summary** first
2. Check **P0 items** - these block release
3. Review **Dependencies** before starting
4. Follow the **Recommended Patterns** section
5. Update the research doc as you implement

## Notes

- Research docs are living documents - update as work progresses
- Link to research from PR descriptions
- Keep research even after implementation for future reference
