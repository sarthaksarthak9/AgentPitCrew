#!/usr/bin/env python3
"""
PrometheusMetrics MCP Server
Provides tools to query Prometheus metrics and alerts for SRE monitoring
"""

try:
    from fastmcp import FastMCP
except ImportError:
    raise ImportError("fastmcp module is not installed. Install it using: pip install fastmcp")
from datetime import datetime
from typing import Optional
import random

# Initialize MCP server
mcp = FastMCP("prometheus-metrics", version="1.0.0")

@mcp.tool()
def query_cpu_usage(cluster_name: str, namespace: str = "default") -> dict:
    """
    Query CPU usage percentage for a given cluster and namespace.
    
    Args:
        cluster_name: Name of the Kubernetes cluster
        namespace: Kubernetes namespace (default: "default")
    
    Returns:
        Dictionary containing CPU usage metrics
    """
    # Mock realistic CPU data with some randomization for demo
    cpu_percent = random.uniform(75.0, 95.0)
    is_high = cpu_percent > 80.0
    
    return {
        "cluster": cluster_name,
        "namespace": namespace,
        "cpu_usage_percent": round(cpu_percent, 2),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "threshold": 80.0,
        "status": "high" if is_high else "normal",
        "recommendation": "Scale up replicas" if is_high else "CPU usage within normal range"
    }


@mcp.tool()
def get_alerts(namespace: str = "default", severity: str = "warning") -> dict:
    """
    Get active Prometheus alerts for a namespace.
    
    Args:
        namespace: Kubernetes namespace to query (default: "default")
        severity: Alert severity level - warning, critical, or info (default: "warning")
    
    Returns:
        Dictionary containing active alerts
    """
    # Mock alert data based on severity
    alerts_data = {
        "warning": [
            {
                "name": "HighCPUUsage",
                "namespace": namespace,
                "severity": "warning",
                "message": f"CPU usage above 80% in namespace {namespace}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "labels": {
                    "app": "web-app",
                    "pod": "web-app-5d7f8c9b4-xyz12"
                }
            },
            {
                "name": "MemoryPressure",
                "namespace": namespace,
                "severity": "warning",
                "message": f"Memory usage at 75% in namespace {namespace}",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "labels": {
                    "app": "api-service",
                    "pod": "api-service-7c9d4f5a-abc34"
                }
            }
        ],
        "critical": [
            {
                "name": "PodCrashLooping",
                "namespace": namespace,
                "severity": "critical",
                "message": f"Pod in {namespace} is crash looping",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "labels": {
                    "app": "database",
                    "pod": "postgres-0"
                }
            }
        ],
        "info": []
    }
    
    selected_alerts = alerts_data.get(severity.lower(), alerts_data["warning"])
    
    return {
        "namespace": namespace,
        "severity": severity,
        "alert_count": len(selected_alerts),
        "alerts": selected_alerts,
        "query_timestamp": datetime.utcnow().isoformat() + "Z"
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
