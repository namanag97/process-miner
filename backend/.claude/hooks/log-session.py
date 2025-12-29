#!/usr/bin/env python3
"""
Claude Code Hook: Log all tool usage to session files
Captures every tool execution and stores it in agent-sessions/ folder
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path

def log_tool_usage():
    """Main hook function to log tool usage to session files."""
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error parsing hook input: {e}", file=sys.stderr)
        return 0  # Don't block Claude even if parsing fails

    # Setup session directory
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", ".")
    session_dir = Path(project_dir) / "agent-sessions"
    session_dir.mkdir(parents=True, exist_ok=True)

    # Get session details
    session_id = input_data.get("session_id", "unknown")
    hook_event = input_data.get("hook_event_name", "unknown")
    tool_name = input_data.get("tool_name", "N/A")

    # Create session file (use first 8 chars of session_id for filename)
    session_file = session_dir / f"{session_id[:8]}.jsonl"

    # Prepare log entry with comprehensive data
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": hook_event,
        "tool": tool_name,
        "session_id": session_id,
        "cwd": input_data.get("cwd", ""),
        "permission_mode": input_data.get("permission_mode", ""),
        "tool_input": input_data.get("tool_input", {}),
        "tool_response": input_data.get("tool_response", {}),
    }

    # Write to session file (append mode)
    try:
        with open(session_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error writing to session file: {e}", file=sys.stderr)
        return 0  # Don't block Claude even if writing fails

    return 0  # Success - don't block the tool execution

if __name__ == "__main__":
    sys.exit(log_tool_usage())
