#!/bin/bash
# Complete deployment script for Kubernetes

set -e

echo "================================================"
echo "AgentPitCrew - Kubernetes Deployment"
echo "================================================"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check cluster connectivity
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster. Please configure kubectl."
    exit 1
fi

echo "✅ Connected to Kubernetes cluster"
echo ""

# Apply RBAC
echo "📝 Creating RBAC resources..."
kubectl apply -f rbac.yaml

echo ""
echo "🐳 Building Docker images..."
echo ""

# Build and load images (for local k8s like minikube/kind)
cd ../../mcp-servers

docker build -t agentpitcrew/prometheus-metrics:latest prometheus-metrics/
docker build -t agentpitcrew/log-analyzer:latest log-analyzer/
docker build -t agentpitcrew/k8s-remediator:latest k8s-remediator/

echo ""
echo "✅ Docker images built"
echo ""

# If using minikube, load images
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo "📦 Loading images to minikube..."
    minikube image load agentpitcrew/prometheus-metrics:latest
    minikube image load agentpitcrew/log-analyzer:latest
    minikube image load agentpitcrew/k8s-remediator:latest
fi

cd ../../deployment/kubernetes

# Deploy MCP servers
echo "🚀 Deploying MCP servers..."
kubectl apply -f deployments.yaml

echo ""
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l component=mcp-server -n archestra-system --timeout=120s || true

echo ""
echo "================================================"
echo "Deployment Status:"
echo "================================================"
kubectl get pods -n archestra-system

echo ""
echo "================================================"
echo "Next Steps:"
echo "================================================"
echo "1. Deploy Archestra agents:"
echo "   kubectl apply -f ../../archestra-config/mcp-servers/registry.yaml"
echo "   kubectl apply -f ../../archestra-config/agents/"
echo ""
echo "2. Test with demo prompts from demo/demo-prompts.md"
echo ""
echo "To view logs: kubectl logs -f -l component=mcp-server -n archestra-system"
echo "================================================"
