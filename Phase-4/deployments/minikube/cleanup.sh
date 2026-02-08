#!/bin/bash
# Cleanup script for Todo Chatbot Kubernetes deployment

set -e

echo "========================================="
echo "Cleaning up Todo Chatbot Deployment"
echo "========================================="
echo ""

RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}⚠ WARNING: This will delete all Todo Chatbot resources${NC}"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "Deleting all resources in todo-chatbot namespace..."

# Delete in reverse order of creation
kubectl delete -f deployments/minikube/frontend/hpa.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/backend/hpa.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/ingress/ingress.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/frontend/service.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/frontend/deployment.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/frontend/configmap.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/backend/service.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/backend/deployment.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/backend/configmap.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/postgresql/service.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/postgresql/deployment.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/postgresql/configmap.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/postgresql/pvc.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/security/network-policy.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/security/rbac.yaml --ignore-not-found=true
kubectl delete -f deployments/minikube/security/secrets.yaml --ignore-not-found=true

echo ""
echo -e "${YELLOW}Deleting namespace (this will remove any remaining resources)...${NC}"
kubectl delete -f deployments/minikube/namespace.yaml --ignore-not-found=true

echo ""
echo "✓ Cleanup completed"
