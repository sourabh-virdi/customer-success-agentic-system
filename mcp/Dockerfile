FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt pyproject.toml ./
COPY agents/shared ./agents/shared
COPY mcp ./mcp
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY agents/shared ./agents/shared
COPY mcp ./mcp
ENV PYTHONPATH=/app/agents/shared:/app/mcp/src
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8000/metrics || exit 1
CMD ["uvicorn", "cs_mcp.main:app", "--host", "0.0.0.0", "--port", "8000"]
