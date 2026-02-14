#!/usr/bin/env python3
"""
LogAnalyzer MCP Server
Provides tools to search logs and detect anomalies in Kubernetes pods
"""

from fastmcp import FastMCP
from datetime import datetime, UTC
import random
import re

# Initialize MCP server
mcp = FastMCP("log-analyzer", version="1.0.0")

# ---------------- SAMPLE LOG DATA ---------------- #

SAMPLE_LOGS = [
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

# ---------------- SEARCH LOGS IMPLEMENTATION ---------------- #

def _search_logs_impl(query: str, time_range: str = "5m", namespace: str = "default") -> dict:
    matching_logs = []

    try:
        pattern = re.compile(query, re.IGNORECASE)
        for log in SAMPLE_LOGS:
            if pattern.search(log):
                parts = log.split()
                matching_logs.append({
                    "timestamp": parts[0] + " " + parts[1],
                    "level": parts[2],
                    "message": " ".join(parts[3:]),
                    "pod": f"app-pod-{random.randint(1000, 9999)}",
                    "namespace": namespace
                })
    except re.error:
        for log in SAMPLE_LOGS:
            if query.lower() in log.lower():
                parts = log.split()
                matching_logs.append({
                    "timestamp": parts[0] + " " + parts[1],
                    "level": parts[2],
                    "message": " ".join(parts[3:]),
                    "pod": f"app-pod-{random.randint(1000, 9999)}",
                    "namespace": namespace
                })

    return {
        "query": query,
        "time_range": time_range,
        "namespace": namespace,
        "match_count": len(matching_logs),
        "logs": matching_logs,
        "search_timestamp": datetime.now(UTC).isoformat()
    }

# MCP TOOL
@mcp.tool()
def search_logs(query: str, time_range: str = "5m", namespace: str = "default") -> dict:
    """
    Search pod logs for a specific pattern or keyword.
    """
    return _search_logs_impl(query, time_range, namespace)

# ---------------- ANOMALY DETECTION IMPLEMENTATION ---------------- #

def _detect_anomaly_impl(pattern: str, threshold: float = 0.8) -> dict:
    pattern_count = sum(1 for log in SAMPLE_LOGS if pattern.upper() in log.upper())
    total_logs = len(SAMPLE_LOGS)
    frequency = pattern_count / total_logs if total_logs > 0 else 0

    is_anomaly = frequency >= threshold

    spikes = []
    current_spike = []

    for i, log in enumerate(SAMPLE_LOGS):
        if pattern.upper() in log.upper():
            parts = log.split()
            current_spike.append({
                "log_index": i,
                "timestamp": parts[0] + " " + parts[1],
                "message": " ".join(parts[3:])
            })
        else:
            if len(current_spike) >= 2:
                spikes.append({
                    "start_time": current_spike[0]["timestamp"],
                    "end_time": current_spike[-1]["timestamp"],
                    "occurrence_count": len(current_spike),
                    "logs": current_spike
                })
            current_spike = []

    if len(current_spike) >= 2:
        spikes.append({
            "start_time": current_spike[0]["timestamp"],
            "end_time": current_spike[-1]["timestamp"],
            "occurrence_count": len(current_spike),
            "logs": current_spike
        })

    severity = "high" if is_anomaly else "normal"
    if spikes:
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
        "analysis_timestamp": datetime.now(UTC).isoformat()
    }

# MCP TOOL
@mcp.tool()
def detect_anomaly(pattern: str, threshold: float = 0.8) -> dict:
    """
    Detect anomalies in log patterns.
    """
    return _detect_anomaly_impl(pattern, threshold)

# ---------------- RUN MCP SERVER ---------------- #

if __name__ == "__main__":
    mcp.run()
