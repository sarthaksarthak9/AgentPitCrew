# Dockerfile for LogAnalyzer MCP Server
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .

# Expose for health checks (optional)
EXPOSE 8080

# Run MCP server
CMD ["python", "server.py"]


