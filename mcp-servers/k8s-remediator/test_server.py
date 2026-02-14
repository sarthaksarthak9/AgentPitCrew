#!/usr/bin/env python3
"""
Test script for K8sRemediator MCP Server
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import scale_deployment, restart_pod, get_audit_log

def test_scale_deployment():
    """Test deployment scaling tool"""
    print("\n=== Testing scale_deployment ===")
    
    # Test allowed scaling
    result = scale_deployment("default", "web-app", 5, dry_run=True)
    print(f"Action: {result['action']}")
    print(f"Deployment: {result['namespace']}/{result['deployment']}")
    print(f"Replicas: {result.get('previous_replicas', 'N/A')} → {result.get('new_replicas', 'N/A')}")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    assert result['success'] == True
    print("test_scale_deployment (allowed) PASSED")
    
    # Test blocked scaling (protected namespace)
    print("\n--- Testing security guardrails ---")
    result = scale_deployment("kube-system", "coredns", 3, dry_run=True)
    print(f"Status: {result['status']}")
    print(f"Reason: {result['reason']}")
    
    assert result['success'] == False
    assert result['status'] == "BLOCKED"
    print("test_scale_deployment (blocked) PASSED")


def test_restart_pod():
    """Test pod restart tool"""
    print("\n=== Testing restart_pod ===")
    
    result = restart_pod("app-pod-1234", "default", dry_run=True)
    print(f"Action: {result['action']}")
    print(f"Pod: {result['namespace']}/{result['pod']}")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    assert result['success'] == True
    print("test_restart_pod PASSED")


def test_audit_log():
    """Test audit log retrieval"""
    print("\n=== Testing get_audit_log ===")
    
    result = get_audit_log(limit=5)
    print(f"Total entries: {result['total_entries']}")
    print(f"Returned: {result['returned_entries']}")
    
    if result['logs']:
        print("\nRecent actions:")
        for log in result['logs']:
            print(f"  [{log['timestamp']}] {log['action']} on {log['target']}: {log['result']}")
    
    assert "logs" in result
    print("test_audit_log PASSED")


if __name__ == "__main__":
    print("Testing K8sRemediator MCP Server")
    print("=" * 50)
    
    try:
        test_scale_deployment()
        test_restart_pod()
        test_audit_log()
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED")
        print("=" * 50)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)
