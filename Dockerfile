FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WIND_USE_PROXY=1 \
    PORT=8888

WORKDIR /app

RUN apt-get update \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY docs/README_WindPy_MCP.md ./README_WindPy_MCP.md

EXPOSE 8888

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('127.0.0.1', 8888), 3).close()"

CMD ["sh", "-c", "python src/wind_mcp_direct_server.py --wind-proxy --host 0.0.0.0 --port ${PORT}"]
