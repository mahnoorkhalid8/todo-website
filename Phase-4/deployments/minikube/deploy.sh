#!/bin/bash
# Deployment script for Todo Chatbot on Kubernetes
# This script deploys the complete application stack

set -e

echo "========================================="
echo "Todo Chatbot Kubernetes Deployment"
echo "========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    echo "Please ensure Docker Desktop Kubernetes is enabled or Minikube is running"
    exit 1
fi

echo -e "${GREEN}✓ Kubernetes cluster is accessible${NC}"
echo ""

# Step 1: Create namespace
echo "Step 1: Creating namespace..."
kubectl apply -f deployments/minikube/namespace.yaml
echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

# Step 2: Create secrets
echo "Step 2: Creating secrets..."
echo -e "${YELLOW}⚠ WARNING: Please ensure you've updated secrets in deployments/minikube/security/secrets.yaml${NC}"
read -p "Have you updated the secrets? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Deployment cancelled. Please update secrets first.${NC}"
    exit 1
fi
kubectl apply -f deployments/minikube/security/secrets.yaml
echo -e "${GREEN}✓ Secrets created${NC}"
echo ""

# Step 3: Create RBAC
echo "Step 3: Creating RBAC resources..."
kubectl apply -f deployments/minikube/security/rbac.yaml
echo -e "${GREEN}✓ RBAC resources created${NC}"
echo ""

# Step 4: Create network policies
echo "Step 4: Creating network policies..."
kubectl apply -f deployments/minikube/security/network-policy.yaml
echo -e "${GREEN}✓ Network policies created${NC}"
echo ""

# Step 5: Deploy PostgreSQL
echo "Step 5: Deploying PostgreSQL..."
kubectl apply -f deployments/minikube/postgresql/pvc.yaml
kubectl apply -f deployments/minikube/postgresql/configmap.yaml
kubectl apply -f deployments/minikube/postgresql/deployment.yaml
kubectl apply -f deployments/minikube/postgresql/service.yaml
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgresql -n todo-chatbot --timeout=120s
echo -e "${GREEN}✓ PostgreSQL deployed and ready${NC}"
echo ""

# Step 6: Deploy Backend
echo "Step 6: Deploying Backend..."
kubectl apply -f deployments/minikube/backend/configmap.yaml
kubectl apply -f deployments/minikube/backend/deployment.yaml
kubectl apply -f deployments/minikube/backend/service.yaml
echo "Waiting for Backend to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n todo-chatbot --timeout=120s
echo -e "${GREEN}✓ Backend deployed and ready${NC}"
echo ""

# Step 7: Deploy Frontend
echo "Step 7: Deploying Frontend..."
kubectl apply -f deployments/minikube/frontend/configmap.yaml
kubectl apply -f deployments/minikube/frontend/deployment.yaml
kubectl apply -f deployments/minikube/frontend/service.yaml
echo "Waiting for Frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n todo-chatbot --timeout=120s
echo -e "${GREEN}✓ Frontend deployed and ready${NC}"
echo ""

# Step 8: Deploy Ingress
echo "Step 8: Deploying Ingress..."
kubectl apply -f deployments/minikube/ingress/ingress.yaml
echo -e "${GREEN}✓ Ingress deployed${NC}"
echo ""

# Step 9: Deploy HPAs
echo "Step 9: Deploying Horizontal Pod Autoscalers..."
kubectl apply -f deployments/minikube/backend/hpa.yaml
kubectl apply -f deployments/minikube/frontend/hpa.yaml
echo -e "${GREEN}✓ HPAs deployed${NC}"
echo ""

# Display deployment status
echo "========================================="
echo "Deployment Status"
echo "========================================="
kubectl get all -n todo-chatbot
echo ""

echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Add '127.0.0.1 todo.local' to your hosts file"
echo "2. Access the application at http://todo.local"
echo "3. Monitor with: kubectl get pods -n todo-chatbot -w"
