#!/usr/bin/env python3

from fastmcp import FastMCP
from datetime import datetime, timezone
from typing import Any
import json
import re

mcp = FastMCP("k8s-remediator", version="1.0.0")

SECURITY_BLOCKLIST = {
    "namespaces": ["kube-system", "kube-public", "kube-node-lease"],
    "deployment_patterns": [".*control-plane.*", ".*etcd.*", ".*api-server.*"],
    "min_replicas": 1
}

audit_log: list[dict[str, Any]] = []

# ---------------- LOG ---------------- #

def log_action(action: str, target: str, result: str, details: dict[str, Any]):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "target": target,
        "result": result,
        "details": details
    }
    audit_log.append(entry)

# ---------------- SECURITY ---------------- #

def check_security_policy(namespace: str, resource_name: str, action: str, **kwargs):

    if namespace in SECURITY_BLOCKLIST["namespaces"]:
        return False, "Protected namespace"

    for pattern in SECURITY_BLOCKLIST["deployment_patterns"]:
        if re.match(pattern, resource_name):
            return False, "Protected deployment"

    if action == "scale" and kwargs.get("replicas", 1) < 1:
        return False, "Cannot scale below 1"

    return True, "Allowed"

# ---------------- INTERNAL FUNCTIONS ---------------- #

def scale_deployment_impl(namespace: str, name: str, replicas: int, dry_run=True):

    allowed, reason = check_security_policy(namespace, name, "scale", replicas=replicas)

    if not allowed:
        log_action("scale", f"{namespace}/{name}", "BLOCKED", {"reason": reason})
        return {"success": False, "status": "BLOCKED", "reason": reason}

    log_action("scale", f"{namespace}/{name}", "DRY-RUN", {"replicas": replicas})

    return {
        "success": True,
        "action": "scale_deployment",
        "namespace": namespace,
        "deployment": name,
        "previous_replicas": 2,
        "new_replicas": replicas,
        "status": "SIMULATED",
        "message": f"Would scale {name} to {replicas}"
    }


def restart_pod_impl(name: str, namespace="default", dry_run=True):

    allowed, reason = check_security_policy(namespace, name, "restart")

    if not allowed:
        log_action("restart", f"{namespace}/{name}", "BLOCKED", {"reason": reason})
        return {"success": False, "status": "BLOCKED", "reason": reason}

    log_action("restart", f"{namespace}/{name}", "DRY-RUN", {})

    return {
        "success": True,
        "action": "restart_pod",
        "namespace": namespace,
        "pod": name,
        "status": "SIMULATED",
        "message": f"Would restart {name}"
    }

# ---------------- MCP WRAPPERS ---------------- #

@mcp.tool()
def scale_deployment(namespace: str, name: str, replicas: int, dry_run=True):
    return scale_deployment_impl(namespace, name, replicas, dry_run)

@mcp.tool()
def restart_pod(name: str, namespace="default", dry_run=True):
    return restart_pod_impl(name, namespace, dry_run)

@mcp.tool()
def get_audit_log(limit: int = 10):
    return {"logs": audit_log[-limit:]}

if __name__ == "__main__":
    mcp.run()
