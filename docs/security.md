# Security & privacy notes

**This stack holds personal data and ships with no built-in authentication.**
Treat the MCP endpoint as sensitive.

## Do
- Keep the MCP port bound to loopback + reach it via Tailscale (default here).
- Run full-disk encryption on the host (LUKS / FileVault / BitLocker).
- Back up the `qdrant_data` volume and your `./context` directory.
- Keep your Master Context File free of secrets (see context.md section 10).

## Don't
- Don't publish port 8080 to 0.0.0.0 / the public internet without an
  authenticating reverse proxy in front.
- Don't put API keys, passwords, health, or NDA'd material into memory.

## "Is it really fully local?"
Yes, in the default config: fact extraction (LLM) and embeddings both run in
the Ollama container, and vectors live in your Qdrant volume. Nothing is sent
to any third party.

**The moment you change `MEM0_LLM_MODEL` / `MEM0_EMBED_MODEL` to a cloud
provider, your memories transit that provider's API during extraction.** That
is a deliberate trade (speed/quality vs. privacy), not the default.

## Backups
    # vector store
    docker run --rm -v contextkeep_qdrant_data:/data -v "$PWD":/backup alpine \
      tar czf /backup/qdrant-backup.tgz -C /data .
    # source of truth
    cp -r context context-backup-$(date +%F)

## Updating
    docker compose pull && docker compose up -d --build
Re-test after upgrades: mem0 / mcp APIs can change between releases.
