#!/bin/bash
# Quick deployment script for MCP servers

set -e

echo "================================================"
echo "AgentPitCrew - SRE Dashboard Deployment"
echo "================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

echo ""
echo "📦 Building Docker images..."
echo ""

# Build all MCP servers
cd /home/sarthak/AgentPitCrew/deployment/docker
docker-compose build

echo ""
echo "✅ Docker images built successfully!"
echo ""
echo "🚀 Starting all services..."
echo ""

# Start services
docker-compose up -d

echo ""
echo "✅ All services started!"
echo ""
echo "================================================"
echo "Service Status:"
echo "================================================"
docker-compose ps

echo ""
echo "================================================"
echo "Access Points:"
echo "================================================"
echo "📊 Prometheus:     http://localhost:9090"
echo "📈 Grafana:        http://localhost:3000"
echo "                   (admin/admin)"
echo ""
echo "MCP Servers (running internally):"
echo "  • prometheus-metrics"
echo "  • log-analyzer"
echo "  • k8s-remediator"
echo ""
echo "================================================"
echo "Next Steps:"
echo "================================================"
echo "1. Deploy Archestra platform (if not already running)"
echo "2. Apply Archestra configs:"
echo "   kubectl apply -f /home/sarthak/AgentPitCrew/archestra-config/"
echo "3. Test with demo prompts"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"
echo "================================================"
