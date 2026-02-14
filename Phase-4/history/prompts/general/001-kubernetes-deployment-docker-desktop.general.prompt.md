---
id: 001
title: Kubernetes Deployment to Docker Desktop
stage: green
date: 2026-02-14
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: SEVEN86 COMPUTES
command: continue deployment
labels: ["kubernetes", "docker", "deployment", "debugging", "infrastructure"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/Dockerfile
  - backend/db.py
  - deployments/minikube/backend/deployment.yaml
  - deployments/minikube/frontend/deployment.yaml
  - frontend/Dockerfile
  - frontend/next.config.js
tests:
  - Backend health endpoint: http://localhost:8000/health
  - Frontend deployment verification
  - PostgreSQL database connectivity
---

## Prompt

Continue Kubernetes deployment of Todo Chatbot application from previous session. Deploy all components (frontend Next.js, backend FastAPI, PostgreSQL) to Docker Desktop Kubernetes. Fix blocking issues preventing successful deployment. Complete the deployment tasks. Ensure backend connects to PostgreSQL database correctly. Build and deploy both frontend and backend Docker images.

## Response snapshot

Successfully deployed the Todo Chatbot application to Docker Desktop Kubernetes with the following accomplishments:

**Docker Images Built:**
- `todo-backend:latest` (77MB compressed, 388MB uncompressed) - FastAPI backend with PostgreSQL connectivity
- `todo-frontend:latest` (52.6MB compressed, 222MB uncompressed) - Next.js frontend with standalone output

**Issues Fixed:**

1. **Backend ASGI Loading Error**: Removed `--factory` flag from Dockerfile CMD since `main:app` is already an instantiated FastAPI object, not a factory function.

2. **Database Connection Error**: Modified `backend/db.py` to construct DATABASE_URL from individual environment variables (DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, POSTGRES_PASSWORD) instead of expecting pre-built URL with shell-style variable substitution.

3. **Frontend Build Failure**:
   - Added `output: 'standalone'` to `next.config.js` to enable standalone mode
   - Modified Dockerfile to create empty public directory instead of copying non-existent one

4. **Image Pull Policy**: Changed `imagePullPolicy: Never` to `imagePullPolicy: IfNotPresent` in deployment manifests for Docker Desktop Kubernetes compatibility.

5. **Health Check Path**: Fixed backend startup probe from `/api/health` to `/health` to match actual endpoint.

6. **Memory Limits**: Increased backend memory limits from 512Mi to 1Gi to prevent OOMKilled errors (exit code 137).

**Kubernetes Resources Deployed:**

PostgreSQL:
- StatefulSet with 1 replica
- PersistentVolumeClaim (10Gi)
- Service (ClusterIP on port 5432)
- ConfigMap with initialization scripts
- Databases created: postgres, todo_chatbot

Backend:
- Deployment with 2 replicas
- Service (ClusterIP on port 8000)
- ConfigMap with environment variables
- Health checks: startup, liveness, readiness probes
- Resource limits: 1Gi memory, 1000m CPU

Frontend:
- Deployment with 2 replicas
- Service (ClusterIP on port 3000)
- ConfigMap with Next.js environment variables
- HorizontalPodAutoscaler (2-5 replicas, 70% CPU, 80% memory)
- Health checks: startup, liveness, readiness probes

**Final Status:**
All pods running successfully:
- backend-7d7967d4cd-mghlr: 1/1 Running
- backend-7d7967d4cd-mplgp: 1/1 Running
- frontend-6f6756dbc4-rm6pj: 1/1 Running
- frontend-6f6756dbc4-rmftt: 1/1 Running
- postgresql-0: 1/1 Running

Backend health endpoint verified: `{"status":"healthy","timestamp":"2026-02-14T11:58:48.486689+00:00","version":"2.3"}`

## Outcome

- ✅ Impact: Successfully deployed full-stack Todo Chatbot application to Docker Desktop Kubernetes with all components running and healthy
- 🧪 Tests: Backend health endpoint verified, PostgreSQL connectivity confirmed, all pods passing readiness probes
- 📁 Files: Modified 7 files (Dockerfiles, deployment manifests, database connection logic, Next.js config)
- 🔁 Next prompts: Install ingress controller for external access, test full application functionality (auth, tasks, AI chat), configure persistent storage backup
- 🧠 Reflection: Key learning was adapting Minikube deployment to Docker Desktop Kubernetes (imagePullPolicy differences, resource constraints). Memory limits were critical - backend required 1Gi instead of 512Mi to avoid OOMKilled errors.

## Evaluation notes (flywheel)

- Failure modes observed: ASGI factory flag mismatch, shell-style variable substitution in Kubernetes env vars, Next.js standalone mode not configured, memory limits too low causing OOMKilled
- Graders run and results (PASS/FAIL): Backend health check PASS, PostgreSQL connectivity PASS, Pod readiness probes PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test with lower memory limits (768Mi) to optimize resource usage while maintaining stability
