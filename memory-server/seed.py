"""
seed.py
-------
One-time (or re-runnable) ingestion of your Master Context File into memory.

Each meaningful line/bullet becomes a candidate memory. mem0 itself runs the
local LLM to extract, de-duplicate, and consolidate facts — so re-running this
after edits is safe (it won't blindly create duplicates, though it may cost a
few local-LLM calls per line).

Usage (inside the running stack):
    docker compose exec memory python seed.py
or via the Makefile:
    make seed
"""

import os

import memory_layer as ml
from chunking import chunk_markdown

USER = os.environ.get("CONTEXT_USER_ID", "me")
PATH = os.environ.get("CONTEXT_FILE", "/context/context.md")


def main() -> None:
    if not os.path.exists(PATH):
        raise SystemExit(f"Context file not found at {PATH}. Mount it or set CONTEXT_FILE.")

    try:
        ml.ensure_ready()
    except (RuntimeError, ValueError) as e:
        raise SystemExit(str(e)) from e

    with open(PATH, encoding="utf-8") as f:
        md = f.read()

    chunks = chunk_markdown(md)
    print(f"Seeding {len(chunks)} candidate memories for user '{USER}' from {PATH} ...")
    print("(each item triggers a local-LLM extraction call; this can take a while)\n")

    for i, c in enumerate(chunks, 1):
        try:
            ml.add(c, user_id=USER, record_inbox=False)
            print(f"  [{i}/{len(chunks)}] ok: {c[:70]}")
        except Exception as e:  # noqa: BLE001 - we want to keep going on a single failure
            print(f"  [{i}/{len(chunks)}] FAILED: {e}")

    print("\nDone. Verify with:  make list")


if __name__ == "__main__":
    main()
