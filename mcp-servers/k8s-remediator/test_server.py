#!/usr/bin/env python3

from server import scale_deployment_impl, restart_pod_impl, audit_log

print("Testing K8sRemediator MCP Server")
print("="*50)

print("\n=== Testing scale_deployment ===")
result = scale_deployment_impl("default", "web-app", 5)
print(result)
assert result["success"] == True

print("\n=== Testing blocked scaling ===")
result = scale_deployment_impl("kube-system", "coredns", 3)
print(result)
assert result["success"] == False

print("\n=== Testing restart_pod ===")
result = restart_pod_impl("app-pod-1234")
print(result)
assert result["success"] == True

print("\n=== Testing audit log ===")
print(audit_log)

print("\nALL TESTS PASSED")
