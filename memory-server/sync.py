"""
sync.py
-------
Re-index context/context.md into the vector store (same logic as seed).

Run after editing the Master Context File or merging inbox.md into context.md.

Usage:
    docker compose exec memory python sync.py
or:
    make sync
"""

import os

import context_io as ctx_io
import memory_layer as ml
from chunking import chunk_markdown

USER = os.environ.get("CONTEXT_USER_ID", "me")
PATH = os.environ.get("CONTEXT_FILE", "/context/context.md")


def main() -> None:
    if not os.path.exists(PATH):
        raise SystemExit(f"Context file not found at {PATH}.")

    try:
        ml.ensure_ready()
    except (RuntimeError, ValueError) as e:
        raise SystemExit(str(e)) from e

    with open(PATH, encoding="utf-8") as f:
        md = f.read()

    chunks = chunk_markdown(md)
    inbox_lines = ctx_io.inbox_line_count()
    stored = len(ml.get_all(user_id=USER))

    print(f"Syncing {len(chunks)} lines from {PATH} for user '{USER}' ...")
    print(f"(inbox: {inbox_lines} pending lines | vector store: {stored} memories before sync)\n")

    for i, c in enumerate(chunks, 1):
        try:
            ml.add(c, user_id=USER, record_inbox=False)
            print(f"  [{i}/{len(chunks)}] ok: {c[:70]}")
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}/{len(chunks)}] FAILED: {e}")

    after = len(ml.get_all(user_id=USER))
    print(f"\nDone. Vector store now has {after} memories for '{USER}'.")
    if inbox_lines:
        print(f"Inbox still has {inbox_lines} lines — merge into context.md when ready.")


if __name__ == "__main__":
    main()
