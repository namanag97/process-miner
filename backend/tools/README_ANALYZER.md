# DevConsole Log Analyzer

Automated analysis of your DevConsole telemetry using Claude AI to identify issues, patterns, and optimization opportunities.

## Quick Start

### 1. Install Dependencies

```bash
pip install anthropic requests
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. Run Analysis

**From DevConsole Export:**
```bash
# 1. In DevConsole UI, click "Export" button
# 2. Save as dev-console-export.json
# 3. Run analysis
python tools/analyze_devconsole_logs.py dev-console-export.json
```

**From Live Backend:**
```bash
# Fetch last 200 logs and analyze
python tools/analyze_devconsole_logs.py --fetch
```

---

## Usage Examples

### Basic Analysis
```bash
python tools/analyze_devconsole_logs.py logs.json
```

**Output:**
```
=== DEVCONSOLE LOG ANALYSIS ===
Period: 14:32:15 → 14:45:30 (798s)
Total Events: 156 | Errors: 16 (10.3%) | Slow Requests: 3

🎯 CRITICAL ISSUES (1)
- BinderException in DFG queries: 15 errors | Missing 'log_id' column in 'pc' table | Blocks all visualizations

⚠️  PERFORMANCE CONCERNS (2)
- Slow workspace query: 1373ms | Threshold: 100ms | Single occurrence at 16:36:13
- High error rate: 22.86% | Threshold: 5% | Correlates with DFG endpoint

📊 SYSTEM HEALTH
CPU: 34.6/60% | Memory: 78.5/85% | RPS: 0.6 | Avg Response: 97.87ms
Circuit Breakers: All Closed ✅ (pm4py, database, cache)

🔍 PATTERNS & INSIGHTS
- DFG endpoint error pattern: 100% failure rate on dataset 8a32cb6c | Schema migration needed
- Telemetry proxy errors: ClientDisconnect from frontend | Normal SSE behavior, ignorable

💡 RECOMMENDATIONS
1. Fix BinderException - Add 'log_id' column to 'pc' table - Restores all visualization features
2. Investigate slow workspace query - 1.3s is 13x over budget - Index workspace_id or cache results
3. Add error boundary for DFG - Graceful fallback for missing data - Better UX during migrations
```

### Use Opus for Deeper Analysis
```bash
python tools/analyze_devconsole_logs.py logs.json --model claude-opus-4-5
```

More detailed insights, better pattern recognition, higher cost.

### Analyze Live System
```bash
# Last 200 entries
python tools/analyze_devconsole_logs.py --fetch

# Last 500 entries
python tools/analyze_devconsole_logs.py --fetch --limit 500

# Different backend URL
python tools/analyze_devconsole_logs.py --fetch --api-url http://localhost:8080
```

### Save to File
```bash
python tools/analyze_devconsole_logs.py logs.json --output analysis.txt
```

---

## What It Analyzes

### 🔴 Critical Issues
- Recurring errors (same error multiple times)
- Database errors (connection, query, schema issues)
- Circuit breaker trips
- Memory leaks (increasing memory over time)
- Cascading failures

### ⚠️ Performance Concerns
- Slow queries (>100ms database operations)
- Slow requests (>1s API responses)
- CPU/memory spikes
- N+1 query patterns
- Inefficient PM4Py operations

### 📊 System Health
- CPU utilization trends
- Memory usage patterns
- Request throughput (RPS)
- Response time distribution
- Circuit breaker states

### 🔍 Patterns & Insights
- Error correlations (X causes Y)
- Traffic patterns (spike at specific times)
- Resource utilization trends
- PM4Py performance by algorithm
- Cache hit/miss rates

### 💡 Recommendations
- Prioritized action items
- Expected impact of fixes
- Quick wins vs. long-term improvements
- Migration strategies

---

## Advanced Usage

### Scripted Monitoring

**Hourly Analysis:**
```bash
#!/bin/bash
# cron: 0 * * * * /path/to/analyze_hourly.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="/var/log/devconsole_analysis"

mkdir -p "$OUTPUT_DIR"

python tools/analyze_devconsole_logs.py \
  --fetch \
  --limit 500 \
  --output "$OUTPUT_DIR/analysis_$TIMESTAMP.txt"

# Alert if critical issues found
if grep -q "🎯 CRITICAL ISSUES ([1-9]" "$OUTPUT_DIR/analysis_$TIMESTAMP.txt"; then
  echo "Critical issues detected!" | mail -s "DevConsole Alert" ops@example.com
fi
```

### CI/CD Integration

**Pre-deployment Analysis:**
```yaml
# .github/workflows/analyze.yml
name: Analyze DevConsole Logs

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Fetch and Analyze Logs
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          pip install anthropic requests
          python tools/analyze_devconsole_logs.py \
            --fetch \
            --api-url https://api.production.example.com \
            --output analysis.txt

      - name: Upload Analysis
        uses: actions/upload-artifact@v3
        with:
          name: devconsole-analysis
          path: analysis.txt

      - name: Post to Slack
        if: contains(github.event.head_commit.message, 'CRITICAL')
        run: |
          # Post analysis to Slack...
```

### Custom Analysis Prompt

**Modify the prompt for domain-specific analysis:**

```bash
# Edit prompts/devconsole_analyzer.md
# Add your specific business rules, thresholds, or focus areas

# Example additions:
# - "Focus on conformance checking performance"
# - "Alert if discovery takes >5s for datasets <10k events"
# - "Track variant explosion (>1000 variants)"
```

---

## Model Selection Guide

| Model | Use Case | Cost | Speed | Depth |
|-------|----------|------|-------|-------|
| **Haiku** | Quick checks, CI/CD, frequent analysis | $ | ⚡⚡⚡ | Basic |
| **Sonnet** (default) | Daily analysis, balanced insights | $$ | ⚡⚡ | Good |
| **Opus** | Deep investigation, post-mortem analysis | $$$ | ⚡ | Excellent |

**When to use Opus:**
- Post-incident analysis
- Performance regression investigation
- Capacity planning
- Complex multi-system issues
- Before major releases

**When to use Haiku:**
- CI/CD checks
- Hourly monitoring
- Quick health checks
- Cost-sensitive environments

---

## Troubleshooting

### "API key not found"
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Or add to ~/.bashrc or ~/.zshrc
```

### "Failed to fetch logs"
Check backend is running:
```bash
curl http://localhost:8001/health
```

Enable debug mode in backend:
```bash
DEBUG=true uvicorn src.api.main:app --reload --port 8001
```

### "No logs to analyze"
DevConsole logs are ephemeral (last 500 entries). For longer retention:
1. Increase buffer size in `src/infrastructure/log_broker.py` (line 50)
2. Use `--fetch` immediately after the issue
3. Or export from DevConsole UI before clearing

### "Analysis is too generic"
1. Use Opus model for deeper insights
2. Provide more logs (increase --limit)
3. Customize the prompt template for your domain
4. Include longer time periods

---

## Output Format

The analysis follows this strict format:

```
=== DEVCONSOLE LOG ANALYSIS ===
Period: [time range]
Total Events: [N] | Errors: [N] ([%]) | Slow Requests: [N]

🎯 CRITICAL ISSUES ([count])
- [Issue]: [Impact] | [Scope] | [Example/Evidence]

⚠️  PERFORMANCE CONCERNS ([count])
- [Concern]: [Metric] | [Threshold] | [Pattern]

📊 SYSTEM HEALTH
[Key metrics in one line]
[Circuit breaker summary]

🔍 PATTERNS & INSIGHTS
- [Pattern]: [Observation + Business Impact]

💡 RECOMMENDATIONS ([prioritized])
1. [Action] - [Rationale] - [Expected Impact]
2. [Action] - [Rationale] - [Expected Impact]
3. [Action] - [Rationale] - [Expected Impact]
```

**Always 15-20 lines**, each providing actionable insight.

---

## Tips for Best Results

1. **Provide Context**: Include logs from before and after an issue
2. **Time Range**: At least 5 minutes of data for pattern detection
3. **Include Success Cases**: Mix of errors and successes shows baselines
4. **Regular Analysis**: Daily checks catch issues before they escalate
5. **Compare Analyses**: Track trends over time (is error rate improving?)
6. **Act on Recommendations**: The analysis is only valuable if you fix things!

---

## Integration with DevConsole UI

You can trigger analysis directly from the DevConsole:

1. Click "Export" button → saves `dev-console-export.json`
2. Run: `python tools/analyze_devconsole_logs.py dev-console-export.json`
3. Review analysis and fix issues
4. Re-export and re-analyze to verify fixes

Or use the **planned "Analyze" button** (coming soon) for one-click analysis in-browser.

---

## FAQ

**Q: Does this send my logs to Anthropic?**
A: Yes, the logs are sent to Claude API for analysis. Don't use with sensitive production data without reviewing the logs first.

**Q: Can I use a different LLM?**
A: Yes, modify `analyze_logs()` function to use OpenAI, local LLM, etc. The prompt format is LLM-agnostic.

**Q: How much does it cost?**
A: ~$0.01-0.05 per analysis with Sonnet, depending on log volume. Opus costs ~3x more.

**Q: Can I customize the analysis focus?**
A: Yes! Edit `prompts/devconsole_analyzer.md` to add domain-specific rules, thresholds, or focus areas.

**Q: What if I don't have ANTHROPIC_API_KEY?**
A: You can use OpenAI API instead by modifying the script, or run a local LLM like Ollama with LLaMA.

---

## Example: Finding Root Cause

```bash
# User reports: "Visualizations are broken"

# 1. Export recent logs from DevConsole
# 2. Analyze
python tools/analyze_devconsole_logs.py logs.json

# Output shows:
# 🎯 CRITICAL ISSUES (1)
# - BinderException: Missing 'log_id' column in 'pc' table
#
# 💡 RECOMMENDATIONS
# 1. Run migration: ALTER TABLE pc ADD COLUMN log_id UUID

# 3. Fix the issue
alembic revision --autogenerate -m "Add log_id to pc table"
alembic upgrade head

# 4. Verify fix
python tools/analyze_devconsole_logs.py --fetch

# Output shows:
# 🎯 CRITICAL ISSUES (0)
# ✅ All systems healthy
```

**Time saved: 2 hours → 5 minutes**

---

## Support

For issues or improvements:
1. Check the prompt template: `prompts/devconsole_analyzer.md`
2. Review the script: `tools/analyze_devconsole_logs.py`
3. Adjust thresholds, add custom patterns, or modify output format

**Happy analyzing!** 🚀
