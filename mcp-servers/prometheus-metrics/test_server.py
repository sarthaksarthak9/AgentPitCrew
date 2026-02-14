#!/usr/bin/env python3
"""
Manual test script for PrometheusMetrics MCP Server
Run the server and manually test the tools
"""

print("""
========================================
PrometheusMetrics MCP Server - Manual Test
========================================

To test this server:

1. Start the server in one terminal:
   cd /home/sarthak/AgentPitCrew/mcp-servers/prometheus-metrics
   python server.py

2. The server will run in stdio mode - you can test with MCP inspector
   or integrate it directly with Archestra

3. Available tools:
   - query_cpu_usage(cluster_name, namespace)
   - get_alerts(namespace, severity)

Example tool calls (in JSON-RPC format):
{
  "method": "tools/call",
  "params": {
    "name": "query_cpu_usage",
    "arguments": {
      "cluster_name": "production",
      "namespace": "default"
    }
  }
}

========================================
✅ Server implementation complete
Ready for Archestra integration (Phase 2)
========================================
""")
