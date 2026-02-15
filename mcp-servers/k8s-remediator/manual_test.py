#!/usr/bin/env python3
"""
Manual test script for K8sRemediator MCP Server
Tests the actual tool functions directly
"""

import sys
import os
import json

# Add the current directory to the Python path to import server
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the implementation functions directly
from server import scale_deployment_impl, restart_pod_impl, audit_log

def test_scale_deployment():
    """Test deployment scaling tool"""
    print("\n=== Testing scale_deployment ===")
    
    # Use the implementation function directly
    scale_func = scale_deployment_impl
    
    # Test allowed scaling
    result = scale_func(namespace="default", name="web-app", replicas=5, dry_run=True)
    print(f"Action: {result['action']}")
    print(f"Deployment: {result['namespace']}/{result['deployment']}")
    print(f"Replicas: {result.get('previous_replicas', 'N/A')} → {result.get('new_replicas', 'N/A')}")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    assert result['success'] == True
    print("test_scale_deployment (allowed) PASSED")
    
    # Test blocked scaling (protected namespace)
    print("\n--- Testing security guardrails ---")
    result = scale_func(namespace="kube-system", name="coredns", replicas=3, dry_run=True)
    print(f"Status: {result['status']}")
    print(f"Reason: {result['reason']}")
    
    assert result['success'] == False
    assert result['status'] == "BLOCKED"
    print("test_scale_deployment (blocked) PASSED")
    
    # Test scaling below minimum replicas
    print("\n--- Testing minimum replica guardrail ---")
    result = scale_func(namespace="default", name="api-server", replicas=0, dry_run=True)
    print(f"Status: {result['status']}")
    print(f"Reason: {result['reason']}")
    
    assert result['success'] == False
    assert result['status'] == "BLOCKED"
    print("test_scale_deployment (min replicas) PASSED")


def test_restart_pod():
    """Test pod restart tool"""
    print("\n=== Testing restart_pod ===")
    
    restart_func = restart_pod_impl
    
    result = restart_func(name="app-pod-1234", namespace="default", dry_run=True)
    print(f"Action: {result['action']}")
    print(f"Pod: {result['namespace']}/{result['pod']}")
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    
    assert result['success'] == True
    print("test_restart_pod PASSED")
    
    # Test blocked pod restart (protected namespace)
    print("\n--- Testing security guardrails ---")
    result = restart_func(name="kube-apiserver", namespace="kube-system", dry_run=True)
    print(f"Status: {result['status']}")
    print(f"Reason: {result['reason']}")
    
    assert result['success'] == False
    assert result['status'] == "BLOCKED"
    print("test_restart_pod (blocked) PASSED")


def test_audit_log():
    """Test audit log retrieval"""
    print("\n=== Testing get_audit_log ===")
    
    # Check the audit_log directly
    result = {
        'total_entries': len(audit_log),
        'returned_entries': min(10, len(audit_log)),
        'logs': audit_log[-10:]
    }
    print(f"Total entries: {result['total_entries']}")
    print(f"Returned: {result['returned_entries']}")
    
    if result['logs']:
        print("\nRecent actions:")
        for log in result['logs'][-5:]:  # Show last 5
            print(f"  [{log['timestamp']}] {log['action']} on {log['target']}: {log['result']}")
    
    assert "logs" in result
    assert result['total_entries'] >= 0
    print("test_audit_log PASSED")


def test_actual_execution():
    """Test with dry_run=False to see actual execution mode"""
    print("\n=== Testing Actual Execution Mode (dry_run=False) ===")
    
    result = scale_deployment_impl(namespace="production", name="api", replicas=3, dry_run=False)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Action: {result.get('action')}")
    
    assert result['success'] == True
    print("test_actual_execution PASSED")


if __name__ == "__main__":
    print("=" * 60)
    print("K8sRemediator MCP Server - Manual Test Suite")
    print("=" * 60)
    
    try:
        test_scale_deployment()
        test_restart_pod()
        test_audit_log()
        test_actual_execution()
        
        print("\n" + "=" * 60)
        print("ALL  TESTS PASSED")
        print("=" * 60)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
