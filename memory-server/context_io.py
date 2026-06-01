"""Read/write Master Context File and runtime inbox on the mounted context volume."""

from __future__ import annotations

import os
from datetime import datetime, timezone

INBOX_HEADER = """---
# Runtime memory inbox
# Lines appended automatically when AI clients call add_memory.
# Review periodically and merge valuable facts into context.md, then run: make sync
---

"""


def context_paths() -> tuple[str, str]:
    master = os.environ.get("CONTEXT_FILE", "/context/context.md")
    inbox = os.environ.get("CONTEXT_INBOX", "/context/inbox.md")
    return master, inbox


def append_inbox(text: str, user_id: str) -> None:
    """Append a timestamped line to inbox.md (best-effort; never blocks memory store)."""
    _, inbox = context_paths()
    try:
        if not os.path.exists(inbox):
            with open(inbox, "w", encoding="utf-8") as f:
                f.write(INBOX_HEADER)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"- [{ts}] ({user_id}) {text.strip()}\n"
        with open(inbox, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        # Volume may be read-only in misconfigured deployments.
        pass


def inbox_line_count() -> int:
    _, inbox = context_paths()
    if not os.path.exists(inbox):
        return 0
    with open(inbox, encoding="utf-8") as f:
        return sum(
            1
            for raw in f
            if (s := raw.strip()) and s.startswith("- [") and not s.startswith("#")
        )
