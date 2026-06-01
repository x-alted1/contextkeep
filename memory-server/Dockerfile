FROM python:3.12-slim

WORKDIR /app

# System deps kept minimal; mem0 NLP extras (spacy) are optional and omitted.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY memory_layer.py server.py seed.py sync.py context_io.py chunking.py healthcheck.py ./

EXPOSE 8080

# Any HTTP response from /mcp (including 4xx) means the MCP server is listening.
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=5 \
  CMD ["python", "healthcheck.py"]

CMD ["python", "server.py"]
