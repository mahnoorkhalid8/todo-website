# Quickstart: Kubernetes Minikube Deployment

## Prerequisites
- Docker installed and running
- kubectl installed (v1.28+)
- Minikube installed (v1.32+)
- 8GB+ RAM available (12GB+ recommended)
- 4+ CPU cores

## Setup Instructions

### 1. Start Minikube
```bash
# Start Minikube with adequate resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Prepare Namespace and Configuration
```bash
# Create namespace
kubectl create namespace todo-chatbot

# Create secrets (replace with actual values)
kubectl create secret generic todo-chatbot-secrets \
  --namespace=todo-chatbot \
  --from-literal=postgres-password=secretpassword \
  --from-literal=jwt-secret=yoursecretkey \
  --from-literal=google-gemini-api-key=yourkey \
  --from-literal=groq-api-key=yourkey
```

### 3. Deploy PostgreSQL
```bash
# Create PostgreSQL PVC
kubectl apply -f deployments/minikube/postgresql/pvc.yaml

# Deploy PostgreSQL
kubectl apply -f deployments/minikube/postgresql/deployment.yaml
kubectl apply -f deployments/minikube/postgresql/service.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgresql --timeout=120s
```

### 4. Deploy Application Components
```bash
# Deploy backend
kubectl apply -f deployments/minikube/backend/deployment.yaml
kubectl apply -f deployments/minikube/backend/service.yaml

# Deploy frontend
kubectl apply -f deployments/minikube/frontend/deployment.yaml
kubectl apply -f deployments/minikube/frontend/service.yaml

# Wait for deployments
kubectl wait --for=condition=ready pod -l app=backend --timeout=120s
kubectl wait --for=condition=ready pod -l app=frontend --timeout=120s
```

### 5. Configure Ingress
```bash
# Apply ingress configuration
kubectl apply -f deployments/minikube/ingress/ingress.yaml

# Get Minikube IP for hosts file
minikube ip
```

### 6. Verify Deployment
```bash
# Check all resources
kubectl get all -n todo-chatbot

# Check application logs
kubectl logs -l app=backend -n todo-chatbot
kubectl logs -l app=frontend -n todo-chatbot

# Test ingress
curl -H "Host: todo.local" $(minikube ip)/api/health
```

## Local Development Workflow
```bash
# Update application images
# (build and push to minikube registry if needed)

# Apply configuration changes
kubectl apply -f <updated-config-file>

# Rollback deployment if needed
kubectl rollout undo deployment/<deployment-name> -n todo-chatbot
```