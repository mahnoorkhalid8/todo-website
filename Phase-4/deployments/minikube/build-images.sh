#!/bin/bash
# Build Docker images for Todo Chatbot

set -e

echo "========================================="
echo "Building Docker Images"
echo "========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Build backend image
echo "Building backend image..."
cd backend
docker build -t todo-backend:latest .
echo -e "${GREEN}✓ Backend image built${NC}"
cd ..
echo ""

# Build frontend image
echo "Building frontend image..."
cd frontend
docker build -t todo-frontend:latest .
echo -e "${GREEN}✓ Frontend image built${NC}"
cd ..
echo ""

# Load images into Kubernetes (Docker Desktop or Minikube)
echo "Loading images into Kubernetes..."
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo "Loading images into Minikube..."
    minikube image load todo-backend:latest
    minikube image load todo-frontend:latest
    echo -e "${GREEN}✓ Images loaded into Minikube${NC}"
else
    echo -e "${YELLOW}Using Docker Desktop Kubernetes - images are already available${NC}"
fi
echo ""

echo -e "${GREEN}✓ All images built successfully!${NC}"
echo ""
echo "Images:"
docker images | grep todo-
