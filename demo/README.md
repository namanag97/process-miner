# PM4Py Event Log Analysis

This directory contains the PM4Py analysis tool for processing event logs.

## Setup

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install pm4py and dependencies
pip install pm4py
```

## Usage

### Analyze an Event Log

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run analysis on XES file
python3 pm4py-capabilities.py <input_file.xes> [output.json]

# Example
python3 pm4py-capabilities.py BPI_Challenge_2019.xes pm4py_analysis_results.json
```

### Analyze CSV Event Log

```bash
# For CSV files
python3 pm4py-capabilities.py Insurance_claims_event_log.csv results.json
```

## Output

The analysis generates a JSON file containing:
- Event data statistics
- Directly-Follows Graph (DFG)
- Process discovery results (Alpha, Inductive, Heuristics miners)
- Conformance checking metrics
- Quality dimensions (fitness, precision, generalization, simplicity)
- Social network analysis
- Organizational roles
- Temporal statistics
- And 20+ other process mining analyses

## Deactivate Virtual Environment

```bash
deactivate
```

## Files

- `pm4py-capabilities.py` - Main analysis script
- `venv/` - Python virtual environment (created after setup)
- `BPI_Challenge_2019.xes` - Example XES event log
- `Insurance_claims_event_log.csv` - Example CSV event log
- `pm4py_analysis_results.json` - Analysis output (generated)
