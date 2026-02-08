# Todo Chatbot Kubernetes Deployment

Complete Kubernetes deployment configuration for the Todo Chatbot application on local Kubernetes (Docker Desktop or Minikube).

## Prerequisites

- **Docker**: v24+ (installed ✓)
- **kubectl**: v1.28+ (installed ✓)
- **Helm**: v3.13+ (installed ✓)
- **Kubernetes Cluster**: Docker Desktop Kubernetes OR Minikube v1.32+
- **System Resources**: Minimum 4 CPU cores, 8GB RAM

## Quick Start

### 1. Enable Kubernetes

**For Docker Desktop (Recommended for Windows):**
1. Open Docker Desktop
2. Go to Settings → Kubernetes
3. Check "Enable Kubernetes"
4. Click "Apply & Restart"
5. Wait 2-3 minutes for Kubernetes to start

**For Minikube (Alternative):**
```bash
minikube start --cpus=4 --memory=8192 --driver=hyperv
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Update Secrets

**IMPORTANT**: Before deploying, update the secrets in `deployments/minikube/security/secrets.yaml`:

```yaml
stringData:
  postgres-password: "YOUR_SECURE_PASSWORD"
  jwt-secret: "YOUR_SECURE_JWT_SECRET"
  google-gemini-api-key: "YOUR_GEMINI_API_KEY"  # Optional
  groq-api-key: "YOUR_GROQ_API_KEY"  # Optional
```

Or create secrets via command line:
```bash
kubectl create secret generic todo-chatbot-secrets \
  --namespace=todo-chatbot \
  --from-literal=postgres-password=YOUR_SECURE_PASSWORD \
  --from-literal=jwt-secret=YOUR_SECURE_JWT_SECRET \
  --from-literal=google-gemini-api-key=YOUR_GEMINI_KEY \
  --from-literal=groq-api-key=YOUR_GROQ_KEY
```

### 3. Build Docker Images

```bash
cd deployments/minikube
chmod +x build-images.sh
./build-images.sh
```

This will:
- Build `todo-backend:latest` from `backend/Dockerfile`
- Build `todo-frontend:latest` from `frontend/Dockerfile`
- Load images into Kubernetes (if using Minikube)

### 4. Deploy Application

```bash
chmod +x deploy.sh
./deploy.sh
```

This automated script will:
1. Create the `todo-chatbot` namespace
2. Apply secrets and RBAC
3. Configure network policies
4. Deploy PostgreSQL with persistent storage
5. Deploy backend API
6. Deploy frontend
7. Configure ingress
8. Set up horizontal pod autoscaling

### 5. Configure Local Access

Add to your hosts file (`C:\Windows\System32\drivers\etc\hosts` on Windows):
```
127.0.0.1 todo.local
```

### 6. Access Application

Open your browser and navigate to:
- **Frontend**: http://todo.local
- **Backend API**: http://todo.local/api
- **Health Check**: http://todo.local/api/health

## Manual Deployment Steps

If you prefer manual deployment or need to troubleshoot:

### Step 1: Create Namespace
```bash
kubectl apply -f deployments/minikube/namespace.yaml
```

### Step 2: Create Secrets
```bash
kubectl apply -f deployments/minikube/security/secrets.yaml
```

### Step 3: Create RBAC
```bash
kubectl apply -f deployments/minikube/security/rbac.yaml
```

### Step 4: Create Network Policies
```bash
kubectl apply -f deployments/minikube/security/network-policy.yaml
```

### Step 5: Deploy PostgreSQL
```bash
kubectl apply -f deployments/minikube/postgresql/pvc.yaml
kubectl apply -f deployments/minikube/postgresql/configmap.yaml
kubectl apply -f deployments/minikube/postgresql/deployment.yaml
kubectl apply -f deployments/minikube/postgresql/service.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgresql -n todo-chatbot --timeout=120s
```

### Step 6: Deploy Backend
```bash
kubectl apply -f deployments/minikube/backend/configmap.yaml
kubectl apply -f deployments/minikube/backend/deployment.yaml
kubectl apply -f deployments/minikube/backend/service.yaml

# Wait for backend to be ready
kubectl wait --for=condition=ready pod -l app=backend -n todo-chatbot --timeout=120s
```

### Step 7: Deploy Frontend
```bash
kubectl apply -f deployments/minikube/frontend/configmap.yaml
kubectl apply -f deployments/minikube/frontend/deployment.yaml
kubectl apply -f deployments/minikube/frontend/service.yaml

# Wait for frontend to be ready
kubectl wait --for=condition=ready pod -l app=frontend -n todo-chatbot --timeout=120s
```

### Step 8: Deploy Ingress
```bash
kubectl apply -f deployments/minikube/ingress/ingress.yaml
```

### Step 9: Deploy HPAs (Optional)
```bash
kubectl apply -f deployments/minikube/backend/hpa.yaml
kubectl apply -f deployments/minikube/frontend/hpa.yaml
```

## Monitoring and Management

### Check Deployment Status
```bash
# All resources
kubectl get all -n todo-chatbot

# Pods only
kubectl get pods -n todo-chatbot

# Watch pods in real-time
kubectl get pods -n todo-chatbot -w
```

### View Logs
```bash
# Backend logs
kubectl logs -l app=backend -n todo-chatbot --tail=100 -f

# Frontend logs
kubectl logs -l app=frontend -n todo-chatbot --tail=100 -f

# PostgreSQL logs
kubectl logs -l app=postgresql -n todo-chatbot --tail=100 -f
```

### Check HPA Status
```bash
kubectl get hpa -n todo-chatbot
```

### Access Pod Shell
```bash
# Backend pod
kubectl exec -it deployment/backend -n todo-chatbot -- /bin/sh

# Frontend pod
kubectl exec -it deployment/frontend -n todo-chatbot -- /bin/sh

# PostgreSQL pod
kubectl exec -it statefulset/postgresql -n todo-chatbot -- /bin/sh
```

### Port Forwarding (Alternative Access)
```bash
# Frontend
kubectl port-forward -n todo-chatbot svc/frontend 3000:3000

# Backend
kubectl port-forward -n todo-chatbot svc/backend 8000:8000

# PostgreSQL
kubectl port-forward -n todo-chatbot svc/postgresql 5432:5432
```

## Scaling

### Manual Scaling
```bash
# Scale backend
kubectl scale deployment backend -n todo-chatbot --replicas=3

# Scale frontend
kubectl scale deployment frontend -n todo-chatbot --replicas=3
```

### Auto-scaling
HPAs are configured to automatically scale based on:
- CPU utilization > 70%
- Memory utilization > 80%
- Min replicas: 2
- Max replicas: 5

## Updating the Application

### Update Docker Images
```bash
# Rebuild images
./build-images.sh

# Restart deployments to use new images
kubectl rollout restart deployment/backend -n todo-chatbot
kubectl rollout restart deployment/frontend -n todo-chatbot
```

### Update Configuration
```bash
# Update ConfigMap
kubectl apply -f deployments/minikube/backend/configmap.yaml

# Restart deployment to pick up changes
kubectl rollout restart deployment/backend -n todo-chatbot
```

### Update Secrets
```bash
# Update secrets
kubectl apply -f deployments/minikube/security/secrets.yaml

# Restart deployments
kubectl rollout restart deployment/backend -n todo-chatbot
kubectl rollout restart statefulset/postgresql -n todo-chatbot
```

## Rollback

### Rollback Deployment
```bash
# View rollout history
kubectl rollout history deployment/backend -n todo-chatbot

# Rollback to previous version
kubectl rollout undo deployment/backend -n todo-chatbot

# Rollback to specific revision
kubectl rollout undo deployment/backend -n todo-chatbot --to-revision=2
```

## Cleanup

### Remove All Resources
```bash
chmod +x cleanup.sh
./cleanup.sh
```

Or manually:
```bash
kubectl delete namespace todo-chatbot
```

**Note**: This will delete all data including the PostgreSQL database.

## Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-chatbot

# Check events
kubectl get events -n todo-chatbot --sort-by='.lastTimestamp'
```

### Image Pull Errors
- For Docker Desktop: Images should be automatically available
- For Minikube: Run `minikube image load <image-name>`
- Verify images exist: `docker images | grep todo-`

### Database Connection Issues
```bash
# Check PostgreSQL is running
kubectl get pods -l app=postgresql -n todo-chatbot

# Check PostgreSQL logs
kubectl logs -l app=postgresql -n todo-chatbot

# Test database connection from backend pod
kubectl exec -it deployment/backend -n todo-chatbot -- sh
# Inside pod: nc -zv postgresql.todo-chatbot.svc.cluster.local 5432
```

### Ingress Not Working
```bash
# Check ingress status
kubectl get ingress -n todo-chatbot

# Check ingress controller
kubectl get pods -n ingress-nginx

# For Docker Desktop, ingress controller should be running
# For Minikube: minikube addons enable ingress
```

### Network Policy Issues
If services can't communicate:
```bash
# Temporarily disable network policies for testing
kubectl delete networkpolicy --all -n todo-chatbot

# Re-apply after identifying the issue
kubectl apply -f deployments/minikube/security/network-policy.yaml
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Ingress (todo.local)                  │
│                  nginx-ingress-controller                │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │     Backend     │
│   (Next.js)     │───▶│    (FastAPI)    │
│   Port: 3000    │    │   Port: 8000    │
│   Replicas: 2   │    │   Replicas: 2   │
└─────────────────┘    └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   Port: 5432    │
                       │   StatefulSet   │
                       │   PVC: 5Gi      │
                       └─────────────────┘
```

## Security Features

- **Network Policies**: Default-deny with explicit allow rules
- **RBAC**: Least-privilege service accounts
- **Secrets Management**: Sensitive data in Kubernetes Secrets
- **Non-root Containers**: All containers run as non-root users
- **Resource Limits**: CPU and memory limits enforced
- **Read-only Filesystems**: Where applicable

## Performance Features

- **Horizontal Pod Autoscaling**: Automatic scaling based on metrics
- **Resource Requests/Limits**: Guaranteed resources and limits
- **Health Checks**: Liveness, readiness, and startup probes
- **Rolling Updates**: Zero-downtime deployments
- **Connection Pooling**: PostgreSQL connection management

## Next Steps

1. **Enable Monitoring**: Deploy Prometheus and Grafana
2. **Set up CI/CD**: Automate builds and deployments
3. **Configure Backups**: Set up Velero for backup/restore
4. **Add TLS**: Configure TLS certificates for HTTPS
5. **Production Deployment**: Adapt for cloud Kubernetes (EKS, GKE, AKS)

## Files Structure

```
deployments/minikube/
├── namespace.yaml
├── postgresql/
│   ├── pvc.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   └── service.yaml
├── backend/
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── frontend/
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
├── ingress/
│   └── ingress.yaml
├── security/
│   ├── rbac.yaml
│   ├── network-policy.yaml
│   └── secrets.yaml
├── deploy.sh
├── build-images.sh
└── cleanup.sh
```

## Support

For issues or questions:
- Check logs: `kubectl logs <pod-name> -n todo-chatbot`
- Check events: `kubectl get events -n todo-chatbot`
- Describe resources: `kubectl describe <resource> <name> -n todo-chatbot`
