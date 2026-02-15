# SRE Dashboard Helm Chart

Deploy the complete SRE Dashboard with MCP servers using Helm.

## Prerequisites

- Kubernetes cluster (1.19+)
- Helm 3.x
- Docker images built

## Installation

### Quick Install
```bash
# From deployment/helm directory
helm install sre-dashboard .
```

### Custom Values
```bash
helm install sre-dashboard . -f custom-values.yaml
```

### Install to specific namespace
```bash
helm install sre-dashboard . --namespace archestra-system --create-namespace
```

## Configuration

Edit `values.yaml` to customize:

- **Replicas**: Scale each MCP server
- **Resources**: CPU/memory limits
- **Environment**: Prometheus URL, namespaces, etc.
- **RBAC**: Allowed/blocked namespaces

### Example Custom Values

```yaml
prometheusMetrics:
  replicas: 2
  env:
    prometheusUrl: "http://my-prometheus:9090"

k8sRemediator:
  env:
    dryRunMode: "false"  # Enable real operations
```

## Upgrade

```bash
helm upgrade sre-dashboard .
```

## Uninstall

```bash
helm uninstall sre-dashboard
```

## Components

This chart deploys:
- PrometheusMetrics MCP server
- LogAnalyzer MCP server
- K8sRemediator MCP server
- RBAC (ServiceAccount, ClusterRole, ClusterRoleBinding)

## Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.namespace` | Namespace for all resources | `archestra-system` |
| `prometheusMetrics.enabled` | Deploy PrometheusMetrics server | `true` |
| `logAnalyzer.enabled` | Deploy LogAnalyzer server | `true` |
| `k8sRemediator.enabled` | Deploy K8sRemediator server | `true` |
| `rbac.create` | Create RBAC resources | `true` |

See `values.yaml` for complete list.

## Testing

```bash
# Dry run
helm install sre-dashboard . --dry-run --debug

# Template output
helm template sre-dashboard .
```
