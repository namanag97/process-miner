#!/usr/bin/env python3
"""
DevConsole Log Analyzer

Analyzes exported DevConsole logs using an LLM agent to provide
concise, actionable insights about system health and performance.

Usage:
    # From DevConsole export (JSON file)
    python analyze_devconsole_logs.py export.json

    # Fetch recent logs from running backend
    python analyze_devconsole_logs.py --fetch --limit 200

    # Use specific model
    python analyze_devconsole_logs.py export.json --model claude-opus-4-5

    # Save analysis to file
    python analyze_devconsole_logs.py export.json --output analysis.txt
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def load_prompt_template() -> str:
    """Load the analysis prompt template."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "devconsole_analyzer.md"

    if not prompt_path.exists():
        print(f"❌ Prompt template not found at: {prompt_path}", file=sys.stderr)
        sys.exit(1)

    return prompt_path.read_text()


def fetch_recent_logs(api_url: str = "http://localhost:8001", limit: int = 200) -> List[Dict]:
    """Fetch recent logs from running backend."""
    if not REQUESTS_AVAILABLE:
        print("❌ requests library required for fetching logs: pip install requests", file=sys.stderr)
        sys.exit(1)

    try:
        response = requests.get(
            f"{api_url}/api/v1/dev/logs/recent",
            params={"limit": limit},
            timeout=10
        )
        response.raise_for_status()
        logs = response.json()

        if isinstance(logs, dict) and "error" in logs:
            print(f"❌ Backend error: {logs['error']}", file=sys.stderr)
            sys.exit(1)

        print(f"✓ Fetched {len(logs)} recent log entries from {api_url}")
        return logs

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch logs from {api_url}: {e}", file=sys.stderr)
        sys.exit(1)


def load_logs_from_file(filepath: str) -> List[Dict]:
    """Load logs from JSON export file.

    Handles both old format (plain array) and new format (object with metadata).
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Handle new export format (v1.0+) with metadata wrapper
        if isinstance(data, dict) and 'logs' in data:
            logs = data['logs']

            # Print export metadata if available
            if 'export' in data:
                export_meta = data['export']
                print(f"✓ Export metadata:")
                print(f"  - Timestamp: {export_meta.get('timestamp', 'unknown')}")
                print(f"  - Version: {export_meta.get('version', 'unknown')}")
                print(f"  - Source: {export_meta.get('source', 'unknown')}")

                if 'time_range' in export_meta and export_meta['time_range']:
                    time_range = export_meta['time_range']
                    print(f"  - Time Range: {time_range.get('start')} → {time_range.get('end')}")

            # Print summary if available
            if 'summary' in data:
                summary = data['summary']
                print(f"  - Errors: {summary.get('errors', 0)}")
                print(f"  - Slow Requests: {summary.get('slow_requests', 0)}")
                print(f"  - Avg Duration: {summary.get('avg_duration', 0)}ms")

            print(f"✓ Loaded {len(logs)} log entries from {filepath}")
            return logs

        # Handle old format (plain array)
        elif isinstance(data, list):
            print(f"⚠️  Old export format detected (plain array)")
            print(f"✓ Loaded {len(data)} log entries from {filepath}")
            return data

        else:
            print(f"❌ Unexpected export format in {filepath}", file=sys.stderr)
            sys.exit(1)

    except FileNotFoundError:
        print(f"❌ File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {filepath}: {e}", file=sys.stderr)
        sys.exit(1)


def prepare_log_summary(logs: List[Dict]) -> Dict[str, Any]:
    """Generate statistics about the logs for context."""
    if not logs:
        return {"error": "No logs to analyze"}

    total = len(logs)
    errors = sum(1 for log in logs if log.get("level") == "error")
    slow_requests = sum(1 for log in logs if log.get("duration", 0) > 1000)

    # Time range
    timestamps = [log.get("timestamp") for log in logs if log.get("timestamp")]
    time_range = "Unknown"
    if timestamps:
        try:
            times = sorted([datetime.fromisoformat(ts.replace("Z", "+00:00")) for ts in timestamps])
            start = times[0].strftime("%H:%M:%S")
            end = times[-1].strftime("%H:%M:%S")
            duration = (times[-1] - times[0]).total_seconds()
            time_range = f"{start} → {end} ({duration:.0f}s)"
        except:
            pass

    # Level breakdown
    levels = {}
    for log in logs:
        level = log.get("level", "unknown")
        levels[level] = levels.get(level, 0) + 1

    return {
        "total": total,
        "errors": errors,
        "error_rate": round(errors / total * 100, 1) if total > 0 else 0,
        "slow_requests": slow_requests,
        "time_range": time_range,
        "level_breakdown": levels,
    }


def analyze_logs(logs: List[Dict], model: str = "claude-sonnet-4-5") -> str:
    """Analyze logs using Claude."""
    if not ANTHROPIC_AVAILABLE:
        print("❌ anthropic library required: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    # Load prompt template
    prompt_template = load_prompt_template()

    # Prepare log data
    summary = prepare_log_summary(logs)

    # Truncate logs if too large (keep first 100 and last 100)
    if len(logs) > 200:
        print(f"⚠️  Truncating {len(logs)} logs to 200 (first 100 + last 100) to fit context window")
        logs = logs[:100] + logs[-100:]

    # Format logs as JSON
    logs_json = json.dumps(logs, indent=2)

    # Build full prompt
    full_prompt = f"""{prompt_template}

## Log Summary
- Total entries: {summary['total']}
- Errors: {summary['errors']} ({summary['error_rate']}%)
- Slow requests (>1s): {summary['slow_requests']}
- Time range: {summary['time_range']}
- Level breakdown: {json.dumps(summary['level_breakdown'], indent=2)}

## Log Data
```json
{logs_json}
```

Provide your 15-20 line analysis now:
"""

    # Call Claude
    try:
        client = anthropic.Anthropic()

        print(f"\n🤖 Analyzing with {model}...\n")

        message = client.messages.create(
            model=model,
            max_tokens=2000,
            temperature=0.3,  # Lower temperature for more consistent analysis
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )

        analysis = message.content[0].text
        return analysis

    except anthropic.AuthenticationError:
        print("❌ Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze DevConsole logs using an LLM agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze exported logs
  %(prog)s logs.json

  # Fetch and analyze recent logs
  %(prog)s --fetch --limit 200

  # Use Opus model for deeper analysis
  %(prog)s logs.json --model claude-opus-4-5

  # Save analysis to file
  %(prog)s logs.json --output analysis.txt
        """
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="JSON file with DevConsole export (or omit with --fetch)"
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="Fetch recent logs from running backend instead of using file"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=200,
        help="Number of recent logs to fetch (default: 200)"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8001",
        help="Backend API URL (default: http://localhost:8001)"
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-5",
        choices=["claude-sonnet-4-5", "claude-opus-4-5", "claude-haiku-4"],
        help="Claude model to use (default: claude-sonnet-4-5)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Save analysis to file instead of printing to stdout"
    )

    args = parser.parse_args()

    # Validate input
    if not args.fetch and not args.file:
        parser.error("Either provide a log file or use --fetch")

    if args.fetch and args.file:
        parser.error("Cannot use both file and --fetch")

    # Load logs
    if args.fetch:
        logs = fetch_recent_logs(args.api_url, args.limit)
    else:
        logs = load_logs_from_file(args.file)

    if not logs:
        print("❌ No logs to analyze", file=sys.stderr)
        sys.exit(1)

    # Analyze
    analysis = analyze_logs(logs, args.model)

    # Output
    if args.output:
        Path(args.output).write_text(analysis)
        print(f"✓ Analysis saved to {args.output}")
    else:
        print(analysis)


if __name__ == "__main__":
    main()
