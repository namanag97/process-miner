# PM4Py LLM Integration: Technical Architecture

> How pm4py's LLM features work under the hood

---

## Overview

PM4Py's LLM integration works through **abstraction layers** that convert process mining objects (logs, models, statistics) into **structured text representations** that LLMs can understand and reason about.

Think of it as: `Process Mining Data → Text Abstraction → LLM → Natural Language Response`

---

## Architecture Components

```
┌─────────────────┐
│  Process Data   │  (Event Logs, Models, OCEL)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Abstraction    │  pm4py.abstract_* functions
│     Layer       │  Convert to structured text
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Prompt     │  Templated prompts with context
│   Construction  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   LLM API       │  OpenAI, Claude, etc.
│  (GPT-4, etc)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Natural Lang.  │  User-friendly response
│    Response     │
└─────────────────┘
```

---

## 1. Abstraction Functions

### Purpose

Convert complex Python objects into **text descriptions** that preserve semantic meaning for LLMs.

### Event Log Abstraction

```python
import pm4py

# Your event log (Python object)
log = pm4py.read_xes("orders.xes")

# Convert to text description
text = pm4py.abstract_dfg(log)
```

**What it generates:**

```
The process contains the following activities:
- Create Order (100 occurrences)
- Check Credit (95 occurrences)
- Approve Order (92 occurrences)
- Ship Order (90 occurrences)

The following transitions exist:
- Create Order → Check Credit (95 times, avg 2.3 hours)
- Check Credit → Approve Order (92 times, avg 4.1 hours)
- Approve Order → Ship Order (90 times, avg 12.5 hours)

Start activities:
- Create Order (100 cases)

End activities:
- Ship Order (90 cases)
- Reject Order (10 cases)
```

### Technical Implementation

```python
# Simplified version of what pm4py does internally
def abstract_dfg(log):
    """Convert event log to DFG text representation."""

    # 1. Discover DFG
    dfg, start_acts, end_acts = pm4py.discover_dfg(log)

    # 2. Get performance metrics
    perf_dfg, _, _ = pm4py.discover_performance_dfg(log)

    # 3. Build text representation
    lines = []

    # Activities section
    activity_counts = {}
    for edge, count in dfg.items():
        for activity in edge:
            activity_counts[activity] = activity_counts.get(activity, 0) + count

    lines.append("The process contains the following activities:")
    for activity, count in sorted(activity_counts.items(), key=lambda x: -x[1]):
        lines.append(f"- {activity} ({count} occurrences)")

    # Transitions section
    lines.append("\nThe following transitions exist:")
    for (act_from, act_to), count in sorted(dfg.items(), key=lambda x: -x[1]):
        avg_time = perf_dfg.get((act_from, act_to), 0) / 3600  # to hours
        lines.append(f"- {act_from} → {act_to} ({count} times, avg {avg_time:.1f} hours)")

    # Start/End activities
    lines.append("\nStart activities:")
    for act, count in start_acts.items():
        lines.append(f"- {act} ({count} cases)")

    lines.append("\nEnd activities:")
    for act, count in end_acts.items():
        lines.append(f"- {act} ({count} cases)")

    return "\n".join(lines)
```

---

## 2. Available Abstraction Functions

### Log Abstractions

| Function                       | Input       | Output Description                        | Use Case              |
| ------------------------------ | ----------- | ----------------------------------------- | --------------------- |
| `abstract_dfg(log)`            | Event Log   | DFG with frequencies & performance        | Process overview      |
| `abstract_variants(log)`       | Event Log   | List of process variants with frequencies | Variant analysis      |
| `abstract_log_attributes(log)` | Event Log   | Available attributes and their values     | Data exploration      |
| `abstract_log_features(log)`   | Event Log   | Statistical features of the log           | Quantitative analysis |
| `abstract_event_stream(log)`   | Event Log   | Sequential event listing                  | Detailed inspection   |
| `abstract_case(case)`          | Single Case | Activities and timestamps for one case    | Case-level analysis   |

### Model Abstractions

| Function                             | Input            | Output Description        | Use Case            |
| ------------------------------------ | ---------------- | ------------------------- | ------------------- |
| `abstract_petri_net(net, im, fm)`    | Petri Net        | Places, transitions, arcs | Model explanation   |
| `abstract_declare(declare_model)`    | DECLARE Model    | Declarative constraints   | Compliance rules    |
| `abstract_log_skeleton(skeleton)`    | Log Skeleton     | Process constraints       | Behavioral patterns |
| `abstract_temporal_profile(profile)` | Temporal Profile | Time-based constraints    | Temporal analysis   |

### OCEL Abstractions

| Function                                 | Input | Output Description                  | Use Case                |
| ---------------------------------------- | ----- | ----------------------------------- | ----------------------- |
| `abstract_ocel(ocel)`                    | OCEL  | Object types, events, relationships | Object-centric overview |
| `abstract_ocel_ocdfg(ocel)`              | OCEL  | OC-DFG description                  | Multi-object flows      |
| `abstract_ocel_features(ocel, obj_type)` | OCEL  | Features for specific object type   | Object analysis         |

---

## 3. LLM Query Construction

### Basic Pattern

```python
import pm4py

# 1. Load your data
log = pm4py.read_xes("event_log.xes")

# 2. Create text abstraction
process_description = pm4py.abstract_dfg(log)

# 3. Construct prompt
prompt = f"""
You are a process mining expert. Analyze this process:

{process_description}

Question: {user_question}

Provide insights and recommendations.
"""

# 4. Query LLM
response = pm4py.openai_query(
    prompt=prompt,
    api_key="sk-...",
    model="gpt-4"
)

print(response)
```

### Advanced Pattern: Multi-Context

```python
# Combine multiple abstractions for richer context

log = pm4py.read_xes("event_log.xes")

# Get different perspectives
dfg_text = pm4py.abstract_dfg(log)
variants_text = pm4py.abstract_variants(log)
features_text = pm4py.abstract_log_features(log)

# Build comprehensive prompt
prompt = f"""
Analyze this business process:

## Process Flow
{dfg_text}

## Process Variants (Top 10)
{variants_text}

## Statistical Features
{features_text}

User Question: Why are some cases taking much longer than others?

Analyze the data and provide:
1. Potential root causes
2. Specific bottlenecks
3. Actionable recommendations
"""

response = pm4py.openai_query(prompt, api_key=api_key)
```

---

## 4. How `openai_query()` Works

### Implementation

```python
# Simplified version of pm4py's implementation

import openai

def openai_query(prompt: str, api_key: str, model: str = "gpt-4") -> str:
    """
    Query OpenAI API with a prompt.

    Args:
        prompt: The complete prompt (context + question)
        api_key: OpenAI API key
        model: Model to use (gpt-4, gpt-3.5-turbo, etc.)

    Returns:
        LLM response as text
    """
    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are an expert in process mining and business process analysis."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,  # Balance between creativity and consistency
        max_tokens=2000
    )

    return response.choices[0].message.content
```

### Key Parameters

- **model**: Which LLM to use (gpt-4, gpt-3.5-turbo, claude-3-opus, etc.)
- **temperature**: 0 = deterministic, 1 = creative (0.7 is good balance)
- **max_tokens**: Response length limit

---

## 5. Visualization Explanation Feature

### How It Works

```python
# Generate visualization with AI explanation
from pm4py.visualization.petri_net import visualizer as pn_vis

net, im, fm = pm4py.discover_petri_net_inductive(log)

# This generates BOTH visualization AND text explanation
explanation = pm4py.explain_visualization(
    pn_vis.apply,  # Visualization function
    net, im, fm    # Arguments to pass to visualizer
)
```

**Under the hood:**

1. Generates the visualization (returns image)
2. Abstracts the model to text
3. Sends abstraction to LLM with prompt: "Explain this process model"
4. Returns both image and explanation

**Example Output:**

```
This Petri net model shows an order fulfillment process with:

MAIN FLOW:
1. Orders start with "Create Order" activity
2. Parallel execution occurs at Place P3 where:
   - Credit check happens simultaneously
   - Inventory check is performed
3. Both checks must complete before approval
4. After approval, shipping or cancellation can occur

DECISION POINTS:
- After credit check: approve (80%) or reject (20%)
- After inventory check: sufficient (85%) or backorder (15%)

BOTTLENECKS:
- The synchronization point P5 creates waiting (both checks must complete)
- Average delay: 4.2 hours

RECOMMENDATIONS:
- Consider asynchronous approval for low-value orders
- Optimize credit check response time (currently 3.1 hours avg)
```

---

## 6. Example Use Cases in Your Application

### Use Case 1: Natural Language Process Query

```python
from fastapi import APIRouter
import pm4py

router = APIRouter()

@router.post("/processes/{process_id}/ask")
async def ask_question(
    process_id: str,
    question: str,
    db: AsyncSession
):
    # 1. Load event log from database
    event_log = await load_event_log(db, process_id)

    # 2. Convert to pm4py format
    pm4py_log = convert_to_pm4py(event_log)

    # 3. Create abstractions
    dfg_text = pm4py.abstract_dfg(pm4py_log)
    stats_text = pm4py.abstract_log_features(pm4py_log)

    # 4. Build prompt
    prompt = f"""
    Process Analysis Context:

    {dfg_text}

    Statistics:
    {stats_text}

    User Question: {question}

    Provide a clear, data-driven answer based on the process data above.
    """

    # 5. Query LLM
    response = pm4py.openai_query(
        prompt=prompt,
        api_key=get_openai_key(),
        model="gpt-4"
    )

    return {"answer": response}
```

**User Experience:**

```
User: "Why do some orders take longer than others?"

System: "Based on the process data, there are three main causes:

1. Credit Check Delays (40% of slow cases)
   - Cases with credit scores 650-700 take 3.2x longer
   - These require manual review by senior staff

2. Inventory Backorders (30% of slow cases)
   - Products with <10 units in stock trigger backorder flow
   - Average additional delay: 5.3 days

3. International Shipping (20% of slow cases)
   - Cases with country != 'US' add customs clearance
   - Average additional delay: 2.1 days

Recommendation: Fast-track credit approvals for orders <$1000 to reduce delays."
```

### Use Case 2: Automated Process Documentation

```python
@router.get("/processes/{process_id}/documentation")
async def generate_documentation(
    process_id: str,
    db: AsyncSession
):
    pm4py_log = await get_pm4py_log(db, process_id)

    # Discover model
    net, im, fm = pm4py.discover_petri_net_inductive(pm4py_log)

    # Abstract model
    model_text = pm4py.abstract_petri_net(net, im, fm)
    stats_text = pm4py.abstract_log_features(pm4py_log)
    variants_text = pm4py.abstract_variants(pm4py_log)

    # Generate documentation
    prompt = f"""
    Create comprehensive process documentation in markdown format.

    Process Model:
    {model_text}

    Process Statistics:
    {stats_text}

    Common Variants:
    {variants_text}

    Generate:
    1. Executive Summary
    2. Process Description
    3. Key Performance Indicators
    4. Common Process Variants
    5. Identified Bottlenecks
    6. Recommendations for Improvement
    """

    documentation = pm4py.openai_query(prompt, api_key=get_openai_key())

    return {"documentation": documentation}
```

### Use Case 3: Smart Variant Comparison

```python
@router.post("/processes/{process_id}/compare-variants")
async def compare_variants(
    process_id: str,
    variant_ids: list[str],
    db: AsyncSession
):
    # Get specific variants
    variants_data = await get_variants(db, process_id, variant_ids)

    # Abstract each variant
    abstractions = []
    for variant in variants_data:
        variant_log = filter_by_variant(pm4py_log, variant)
        abstractions.append({
            "id": variant.id,
            "description": pm4py.abstract_variants(variant_log),
            "features": pm4py.abstract_log_features(variant_log)
        })

    # Build comparison prompt
    prompt = f"""
    Compare these process variants:

    Variant A:
    {abstractions[0]['description']}
    {abstractions[0]['features']}

    Variant B:
    {abstractions[1]['description']}
    {abstractions[1]['features']}

    Analyze:
    1. Key differences in behavior
    2. Performance differences
    3. Why Variant A might be faster/slower
    4. Which variant is preferred and why
    """

    comparison = pm4py.openai_query(prompt, api_key=get_openai_key())

    return {"comparison": comparison}
```

---

## 7. Token Management & Cost Optimization

### Problem: LLMs charge by token

**Naive approach (expensive):**

```python
# Sending entire event log (wasteful!)
log_string = str(event_log)  # Could be 100K+ tokens!
prompt = f"Analyze this: {log_string}"
# Cost: $5-50 per query 😱
```

**Smart approach (pm4py):**

```python
# Send only relevant abstraction (efficient)
dfg_text = pm4py.abstract_dfg(log)  # ~500-2000 tokens
prompt = f"Analyze this: {dfg_text}"
# Cost: $0.05-0.20 per query ✅
```

### Abstraction vs Raw Data Size

| Data Type                  | Raw Size     | Abstraction Size | Reduction    |
| -------------------------- | ------------ | ---------------- | ------------ |
| Event Log (10K events)     | ~500K tokens | ~2K tokens       | 250x smaller |
| Petri Net (50 transitions) | ~50K tokens  | ~1.5K tokens     | 33x smaller  |
| OCEL (5 object types)      | ~800K tokens | ~3K tokens       | 266x smaller |

### Cost Comparison

```python
# Example: 10,000 event log

# Approach 1: Send raw data
raw_tokens = 500_000
cost_per_query = (500_000 / 1000) * 0.01  # GPT-4 pricing
# = $5.00 per query

# Approach 2: Use pm4py abstraction
abstraction = pm4py.abstract_dfg(log)
abstract_tokens = 2_000
cost_per_query = (2_000 / 1000) * 0.01
# = $0.02 per query

# Savings: 250x cheaper! 🎉
```

---

## 8. Integration Architecture for Your System

### Recommended Implementation

```python
# backend/src/services/llm_service.py

import pm4py
from openai import AsyncOpenAI
from typing import Optional

class LLMService:
    """LLM-powered process analysis."""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"  # Or Claude, Gemini, etc.

    async def answer_question(
        self,
        pm4py_log,
        question: str,
        context: Optional[dict] = None
    ) -> str:
        """Answer natural language questions about a process."""

        # Build context from abstractions
        dfg_context = pm4py.abstract_dfg(pm4py_log)
        stats_context = pm4py.abstract_log_features(pm4py_log)

        # System prompt
        system_prompt = """You are an expert process mining analyst.
        Analyze process data and provide clear, actionable insights.
        Always cite specific numbers from the data."""

        # User prompt with context
        user_prompt = f"""
        Process Overview:
        {dfg_context}

        Statistics:
        {stats_context}

        Question: {question}

        Provide a data-driven answer with specific metrics and recommendations.
        """

        # Query LLM
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Lower for more factual answers
            max_tokens=1500
        )

        return response.choices[0].message.content

    async def explain_model(
        self,
        net,
        im,
        fm
    ) -> str:
        """Generate natural language explanation of a process model."""

        model_abstraction = pm4py.abstract_petri_net(net, im, fm)

        prompt = f"""
        Explain this process model in business terms:

        {model_abstraction}

        Provide:
        1. Main process flow (step by step)
        2. Decision points and branches
        3. Parallel activities
        4. Potential bottlenecks
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        return response.choices[0].message.content

    async def suggest_optimizations(
        self,
        pm4py_log,
        current_performance: dict
    ) -> list[dict]:
        """AI-powered optimization suggestions."""

        # Get comprehensive context
        dfg = pm4py.abstract_dfg(pm4py_log)
        variants = pm4py.abstract_variants(pm4py_log)
        features = pm4py.abstract_log_features(pm4py_log)

        prompt = f"""
        Analyze this process and suggest optimizations:

        Current Process:
        {dfg}

        Variants:
        {variants}

        Performance Metrics:
        {features}

        Current KPIs:
        - Average duration: {current_performance.get('avg_duration')} hours
        - SLA compliance: {current_performance.get('sla_compliance')}%
        - Cost per case: ${current_performance.get('avg_cost')}

        Suggest 5 specific, actionable optimizations with:
        1. What to change
        2. Expected impact
        3. Implementation difficulty (low/medium/high)
        4. Estimated ROI

        Format as JSON array.
        """

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}  # Get structured output
        )

        import json
        return json.loads(response.choices[0].message.content)
```

### API Endpoint

```python
# backend/src/api/routers/ai.py

from fastapi import APIRouter, HTTPException
from src.services.llm_service import LLMService
from src.services.mining import mining_service

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/processes/{process_id}/ask")
async def ask_ai(
    process_id: str,
    question: str,
    db: AsyncSession
):
    """Ask natural language questions about a process."""

    # Load log
    event_log = await get_event_log(db, process_id)
    pm4py_log = mining_service._to_pm4py_log(event_log)

    # Initialize LLM service
    llm = LLMService(api_key=get_openai_key())

    # Get answer
    answer = await llm.answer_question(pm4py_log, question)

    return {"question": question, "answer": answer}
```

---

## 9. Security & Privacy Considerations

### Data Sensitivity

```python
class SecureLLMService:
    """LLM service with data anonymization."""

    async def answer_question(self, pm4py_log, question: str):
        # Option 1: Anonymize before sending
        anonymized_log = self._anonymize_log(pm4py_log)
        abstraction = pm4py.abstract_dfg(anonymized_log)

        # Option 2: Use local LLM instead of API
        if self.use_local_llm:
            return await self._query_local_llm(abstraction, question)

        # Option 3: Enterprise OpenAI with data retention agreement
        return await self._query_openai_secure(abstraction, question)

    def _anonymize_log(self, log):
        """Remove sensitive information before LLM processing."""
        # Replace customer names/IDs with generic placeholders
        # Remove monetary values if needed
        # Keep only structural information
        return anonymized_log
```

---

## Summary: Technical Architecture

**What pm4py provides:**

1. **Abstraction Layer**: Converts process data → text
2. **Prompt Templates**: Structured prompts for process mining tasks
3. **API Integration**: OpenAI wrapper (you can swap for Claude/Gemini)

**What you need to build:**

1. **Backend endpoints**: Expose LLM features via API
2. **Prompt engineering**: Craft effective prompts for your use cases
3. **Caching layer**: Cache common questions to reduce costs
4. **UI components**: Natural language query interface

**Key Technical Benefits:**

- Token efficiency (250x smaller than raw data)
- Semantic preservation (keeps meaning, not raw bytes)
- Model-agnostic (works with any LLM API)
- Cost-effective (~$0.02 per query vs $5+)

The LLM integration is essentially a **smart compression layer** that turns process mining objects into LLM-readable text while preserving all the semantic information needed for analysis.
