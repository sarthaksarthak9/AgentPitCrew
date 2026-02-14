#!/usr/bin/env python3
"""
K8sRemediator MCP Server
Provides tools to execute Kubernetes remediation actions with security guardrails
"""

from fastmcp import FastMCP
from datetime import datetime
from typing import Optional, Any
from itertools import islice
import json

# Initialize MCP server
mcp = FastMCP("k8s-remediator", version="1.0.0")

# Security guardrails - blocked actions
SECURITY_BLOCKLIST = {
    "namespaces": ["kube-system", "kube-public", "kube-node-lease"],
    "deployment_patterns": [".*control-plane.*", ".*etcd.*", ".*api-server.*"],
    "min_replicas": 1  # Never scale below this
}

# Audit log storage (in-memory for demo)
audit_log: list[dict[str, Any]] = []


def log_action(action: str, target: str, result: str, details: dict[str, Any]):
    """Log all remediation actions for audit trail"""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "target": target,
        "result": result,
        "details": details
    }
    audit_log.append(entry)
    print(f"[AUDIT] {json.dumps(entry)}")


def check_security_policy(namespace: str, resource_name: str, action: str, **kwargs) -> tuple[bool, str]:
    """
    Check if action violates security policy.
    
    Returns:
        (is_allowed, reason)
    """
    # Check namespace blocklist
    namespaces_blocklist = SECURITY_BLOCKLIST.get("namespaces", [])
    if isinstance(namespaces_blocklist, list) and namespace in namespaces_blocklist:
        return False, f"Action blocked: {namespace} is a protected system namespace"
    
    # Check deployment name patterns
    import re
    deployment_patterns = SECURITY_BLOCKLIST.get("deployment_patterns", [])
    if isinstance(deployment_patterns, list):
        for pattern in deployment_patterns:
            if re.match(pattern, resource_name):
                return False, f"Action blocked: {resource_name} matches protected pattern"
    
    # Check replica count for scale operations
    if action == "scale" and "replicas" in kwargs:
        if kwargs["replicas"] < SECURITY_BLOCKLIST["min_replicas"]:
            return False, f"Action blocked: Cannot scale below {SECURITY_BLOCKLIST['min_replicas']} replicas"
    
    return True, "Action allowed"


@mcp.tool()
def scale_deployment(namespace: str, name: str, replicas: int, dry_run: bool = True) -> dict:
    """
    Scale a Kubernetes deployment to specified replica count.
    
    Args:
        namespace: Kubernetes namespace
        name: Deployment name
        replicas: Desired number of replicas
        dry_run: If True, simulate without making actual changes (default: True)
    
    Returns:
        Dictionary containing scaling operation results
    """
    # Security check
    is_allowed, reason = check_security_policy(namespace, name, "scale", replicas=replicas)
    
    if not is_allowed:
        log_action(
            action="scale_deployment",
            target=f"{namespace}/{name}",
            result="BLOCKED",
            details={"reason": reason, "requested_replicas": replicas}
        )
        return {
            "success": False,
            "action": "scale_deployment",
            "namespace": namespace,
            "deployment": name,
            "requested_replicas": replicas,
            "status": "BLOCKED",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    # Simulate the scaling operation
    mode = "DRY-RUN" if dry_run else "EXECUTED"
    current_replicas = 2  # Mock current state
    
    result = {
        "success": True,
        "action": "scale_deployment",
        "namespace": namespace,
        "deployment": name,
        "previous_replicas": current_replicas,
        "new_replicas": replicas,
        "mode": mode,
        "status": "COMPLETED" if not dry_run else "SIMULATED",
        "message": f"Scaled deployment {name} from {current_replicas} to {replicas} replicas" if not dry_run 
                   else f"[DRY-RUN] Would scale deployment {name} from {current_replicas} to {replicas} replicas",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    log_action(
        action="scale_deployment",
        target=f"{namespace}/{name}",
        result=mode,
        details={"from": current_replicas, "to": replicas}
    )
    
    return result


@mcp.tool()
def restart_pod(name: str, namespace: str = "default", dry_run: bool = True) -> dict:
    """
    Restart a Kubernetes pod by deleting it (will be recreated by controller).
    
    Args:
        name: Pod name
        namespace: Kubernetes namespace (default: "default")
        dry_run: If True, simulate without making actual changes (default: True)
    
    Returns:
        Dictionary containing restart operation results
    """
    # Security check
    is_allowed, reason = check_security_policy(namespace, name, "restart")
    
    if not is_allowed:
        log_action(
            action="restart_pod",
            target=f"{namespace}/{name}",
            result="BLOCKED",
            details={"reason": reason}
        )
        return {
            "success": False,
            "action": "restart_pod",
            "namespace": namespace,
            "pod": name,
            "status": "BLOCKED",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    # Simulate the restart operation
    mode = "DRY-RUN" if dry_run else "EXECUTED"
    
    result = {
        "success": True,
        "action": "restart_pod",
        "namespace": namespace,
        "pod": name,
        "mode": mode,
        "status": "COMPLETED" if not dry_run else "SIMULATED",
        "message": f"Pod {name} deleted and will be recreated by controller" if not dry_run
                   else f"[DRY-RUN] Would delete pod {name} (will be recreated by controller)",
        "expected_restart_time": "30-60 seconds",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    log_action(
        action="restart_pod",
        target=f"{namespace}/{name}",
        result=mode,
        details={"pod_name": name}
    )
    
    return result


@mcp.tool()
def get_audit_log(limit: int = 10) -> dict:
    """
    Retrieve recent audit log entries for all remediation actions.
    
    Args:
        limit: Maximum number of log entries to return (default: 10)
    
    Returns:
        Dictionary containing recent audit log entries
    """
    # Get the most recent log entries
    start_index = max(0, len(audit_log) - limit)
    recent_logs = audit_log[start_index:]  # type: ignore[misc]
    
    return {
        "total_entries": len(audit_log),
        "returned_entries": len(recent_logs),
        "logs": recent_logs,
        "query_timestamp": datetime.utcnow().isoformat() + "Z"
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
