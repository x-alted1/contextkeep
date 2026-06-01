"""Shared Markdown chunking for seed and sync."""

SKIP_PREFIXES = ("#", "---", "```", "|", ">")


def chunk_markdown(md: str) -> list[str]:
    chunks: list[str] = []
    for raw in md.splitlines():
        s = raw.strip()
        if not s or s.startswith(SKIP_PREFIXES):
            continue
        s = s.lstrip("-*").strip()
        if len(s) >= 8:
            chunks.append(s)
    return chunks
