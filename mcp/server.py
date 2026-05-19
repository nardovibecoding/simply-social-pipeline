"""simply-social-pipeline MCP server.

Tools for local content workflow:
  content_capture    - save draft-worthy moments while coding
  content_queue      - manage draft queue
  session_checkpoint - save local work state
  post_task_check    - check recent actions for useful public material
  set_reminder       - timed terminal alerts (HH:MM or Nm/Nh)

# Copyright (c) 2026 Nardo (nardovibecoding)
# SPDX-License-Identifier: AGPL-3.0-or-later
"""

import os
import subprocess
import sys
from pathlib import Path

# Ensure local lib is importable when run as a subprocess
sys.path.insert(0, str(Path(__file__).parent))

import lib as _lib
from patterns import check_patterns

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("mcp not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP("content-pipeline")

# In-memory session actions (shared with lib.session_actions)
_session_actions = _lib.session_actions


# --- Tool 1: content_capture ---
@mcp.tool()
def content_capture(moment: str, category: str = "insight") -> dict:
    """Save a content-worthy moment to the running draft log.

    Args:
        moment: what happened — the insight, discovery, result, or aha moment
        category: one of: insight, result, code, number, journey, mistake
    """
    return _lib.content_capture(moment, category)


# --- Tool 2: content_queue ---
@mcp.tool()
def content_queue(action: str = "list", tweet: str = "", priority: str = "normal") -> dict:
    """Manage social draft queue. Add drafts, list queue, get next draft.

    Args:
        action: "add" to add a draft, "list" to see queue, "next" to get highest priority, "posted" to mark top as done
        tweet: tweet text (required for "add")
        priority: "high", "normal", "low" (for "add")
    """
    return _lib.content_queue(action, tweet, priority)


# --- Tool 3: session_checkpoint ---
@mcp.tool()
def session_checkpoint(summary: str, key_decisions: list[str] = None, files_changed: list[str] = None) -> dict:
    """Save local work state to checkpoint file.

    Args:
        summary: what was accomplished (2-3 sentences)
        key_decisions: important decisions made (list of strings)
        files_changed: key files created or modified
    """
    return _lib.session_checkpoint(summary, key_decisions, files_changed)


# --- Tool 4: post_task_check ---
@mcp.tool()
def post_task_check() -> dict:
    """Check recent actions against known improvement patterns."""
    actions = list(_session_actions)
    suggestions = check_patterns(actions)

    # Check if session produced content-worthy material
    content_worthy = False
    content_signals = []
    for a in actions:
        detail = a.get("detail", "")
        act = a.get("action", "")
        if act in ("new_hook", "new_mcp_tool", "new_skill", "architecture_change"):
            content_worthy = True
            content_signals.append(f"{act}: {detail}")

    if content_worthy:
        suggestions.append(
            f"Content-worthy work block! Signals: {', '.join(content_signals[:5])}. "
            "Use content_capture to save moments."
        )

    return {
        "recent_actions": actions[-10:],
        "suggestions": suggestions,
        "content_worthy": content_worthy
    }


# --- Tool 5: set_reminder ---
@mcp.tool()
def set_reminder(time_spec: str, message: str) -> dict:
    """Set a timer reminder that alerts in the terminal.

    Args:
        time_spec: "16:55" for absolute local time (set TZ env var), or "30m"/"2h" for relative
        message: reminder text
    """
    import re as _re
    from datetime import datetime, timedelta
    import zoneinfo

    tz_name = os.environ.get("TZ", "UTC")
    try:
        tz = zoneinfo.ZoneInfo(tz_name)
    except Exception:
        tz = zoneinfo.ZoneInfo("UTC")
    now = datetime.now(tz)

    rel_match = _re.match(r"^(\d+)(m|h|min|hour)s?$", time_spec)
    abs_match = _re.match(r"^(\d{1,2}):(\d{2})$", time_spec)

    if rel_match:
        amount = int(rel_match.group(1))
        unit = rel_match.group(2)
        seconds = amount * 3600 if unit.startswith("h") else amount * 60
        target = now + timedelta(seconds=seconds)
    elif abs_match:
        hour, minute = int(abs_match.group(1)), int(abs_match.group(2))
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        seconds = int((target - now).total_seconds())
    else:
        return {"error": f"can't parse time: {time_spec}. Use HH:MM or Nm/Nh"}

    alert = f"⏰ Reminder: {message}"
    subprocess.Popen(
        ["bash", "-c", f"sleep {seconds} && echo -e '\\n\\n{alert}\\n'"],
        stdout=None, stderr=None
    )

    target_str = target.strftime(f"%H:%M {tz_name}")
    return {"set": True, "target": target_str, "seconds": seconds, "message": message}


# --- Tool 6: tweet_performance ---
@mcp.tool()
def tweet_performance(days: int = 7) -> dict:
    """Review locally logged posts from the last N days.

    This public template intentionally avoids cookie, session, browser, or
    account-login based analytics. It reads only the local posts.jsonl log
    written by the explicit posting script.

    Args:
        days: how many days back to look (default 7)
    """
    import json as _json
    from datetime import datetime, timedelta
    from pathlib import Path

    tweets_log = _lib.TWEETS_LOG
    if not tweets_log.exists():
        return {"error": "tweets.jsonl not found — no tweets logged yet"}

    cutoff = datetime.now() - timedelta(days=days)
    entries = []
    with open(tweets_log) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = _json.loads(line)
                posted_at = datetime.strptime(entry["posted_at"], "%Y-%m-%d %H:%M")
                if posted_at >= cutoff:
                    entries.append(entry)
            except (ValueError, KeyError):
                continue

    if not entries:
        return {"tweets": [], "days": days, "message": "no tweets in window"}

    raw = [
        {
            "tweet_id": e["tweet_id"],
            "text": e["text"],
            "posted_at": e["posted_at"],
            "url": e.get("url", ""),
            "likes": None,
            "retweets": None,
            "replies": None,
            "bookmarks": None,
            "views": None,
            "engagement_score": None,
        }
        for e in entries
    ]
    return {"tweets": raw, "days": days, "source": "local_log_only"}


if __name__ == "__main__":
    mcp.run()
