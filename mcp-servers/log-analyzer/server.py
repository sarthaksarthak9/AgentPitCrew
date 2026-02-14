#!/usr/bin/env python3
"""
LogAnalyzer MCP Server
Provides tools to search logs and detect anomalies in Kubernetes pods
"""

from fastmcp import FastMCP
from datetime import datetime, timedelta
from typing import Optional
import random
import re

# Initialize MCP server
mcp = FastMCP("log-analyzer", version="1.0.0")

# Mock log entries for demo
SAMPLE_LOGS = [
    "2024-02-14 12:00:01 INFO Starting application server on port 8080",
    "2024-02-14 12:00:05 INFO Connected to database successfully",
    "2024-02-14 12:01:23 WARN High memory usage detected: 78%",
    "2024-02-14 12:02:45 ERROR Failed to process request: Connection timeout",
    "2024-02-14 12:03:12 ERROR Database query failed: too many connections",
    "2024-02-14 12:03:15 ERROR Retry attempt 1 failed",
    "2024-02-14 12:03:18 ERROR Retry attempt 2 failed",
    "2024-02-14 12:04:01 WARN Request latency exceeds threshold: 2500ms",
    "2024-02-14 12:05:30 INFO Request processed successfully",
    "2024-02-14 12:06:15 ERROR Out of memory exception in worker thread",
]


@mcp.tool()
def search_logs(query: str, time_range: str = "5m", namespace: str = "default") -> dict:
    """
    Search pod logs for a specific pattern or keyword.
    
    Args:
        query: Search pattern or keyword to find in logs
        time_range: Time range for log search (e.g., "5m", "1h", "24h")
        namespace: Kubernetes namespace to search (default: "default")
    
    Returns:
        Dictionary containing matching log entries
    """
    # Filter logs based on query pattern
    matching_logs = []
    
    try:
        pattern = re.compile(query, re.IGNORECASE)
        for log in SAMPLE_LOGS:
            if pattern.search(log):
                matching_logs.append({
                    "timestamp": log.split()[0] + " " + log.split()[1],
                    "level": log.split()[2],
                    "message": " ".join(log.split()[3:]),
                    "pod": f"app-pod-{random.randint(1000, 9999)}",
                    "namespace": namespace
                })
    except re.error:
        # If regex fails, do simple string search
        for log in SAMPLE_LOGS:
            if query.lower() in log.lower():
                matching_logs.append({
                    "timestamp": log.split()[0] + " " + log.split()[1],
                    "level": log.split()[2],
                    "message": " ".join(log.split()[3:]),
                    "pod": f"app-pod-{random.randint(1000, 9999)}",
                    "namespace": namespace
                })
    
    return {
        "query": query,
        "time_range": time_range,
        "namespace": namespace,
        "match_count": len(matching_logs),
        "logs": matching_logs,
        "search_timestamp": datetime.utcnow().isoformat() + "Z"
    }


@mcp.tool()
def detect_anomaly(pattern: str, threshold: float = 0.8) -> dict:
    """
    Detect anomalies in log patterns based on frequency analysis.
    
    Args:
        pattern: Log pattern to analyze (e.g., "ERROR", "WARN")
        threshold: Anomaly detection threshold (0.0-1.0, default: 0.8)
    
    Returns:
        Dictionary containing anomaly detection results
    """
    # Count pattern occurrences
    pattern_count = sum(1 for log in SAMPLE_LOGS if pattern.upper() in log.upper())
    total_logs = len(SAMPLE_LOGS)
    frequency = pattern_count / total_logs if total_logs > 0 else 0
    
    # Determine if this is anomalous
    is_anomaly = frequency >= threshold
    
    # Identify spike windows (group consecutive matching logs)
    spikes = []
    current_spike = []
    
    for i, log in enumerate(SAMPLE_LOGS):
        if pattern.upper() in log.upper():
            current_spike.append({
                "log_index": i,
                "timestamp": log.split()[0] + " " + log.split()[1],
                "message": " ".join(log.split()[3:])
            })
        else:
            if len(current_spike) >= 2:  # At least 2 consecutive occurrences
                spikes.append({
                    "start_time": current_spike[0]["timestamp"],
                    "end_time": current_spike[-1]["timestamp"],
                    "occurrence_count": len(current_spike),
                    "logs": current_spike
                })
            current_spike = []
    
    # Check last spike
    if len(current_spike) >= 2:
        spikes.append({
            "start_time": current_spike[0]["timestamp"],
            "end_time": current_spike[-1]["timestamp"],
            "occurrence_count": len(current_spike),
            "logs": current_spike
        })
    
    severity = "high" if is_anomaly else "normal"
    if len(spikes) > 0:
        severity = "critical"
    
    return {
        "pattern": pattern,
        "threshold": threshold,
        "frequency": round(frequency, 3),
        "occurrence_count": pattern_count,
        "total_logs_analyzed": total_logs,
        "is_anomaly": is_anomaly,
        "severity": severity,
        "spikes_detected": len(spikes),
        "spike_details": spikes,
        "recommendation": f"Investigate {pattern} pattern - detected {len(spikes)} spike(s)" if spikes else "No anomalous behavior detected",
        "analysis_timestamp": datetime.utcnow().isoformat() + "Z"
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
