FROM python:3.12-slim

WORKDIR /app

# System deps kept minimal; mem0 NLP extras (spacy) are optional and omitted.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY memory_layer.py server.py seed.py ./

EXPOSE 8080

# Healthcheck hits the MCP HTTP mount; adjust path if you change transport.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 \
  CMD python -c "import socket,os; s=socket.socket(); s.settimeout(3); s.connect(('127.0.0.1', int(os.environ.get('MCP_PORT','8080')))); s.close()" || exit 1

CMD ["python", "server.py"]
