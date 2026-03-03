# Zoho CRM MCP Server (SkanderBS2024/zoho-mcp)
# Uses stdio transport; for backend use, run with -i and attach to stdin/stdout.
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir zoho-crm-mcp
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["zoho-mcp"]
