# Tasks: Kubernetes Minikube Deployment

**Input**: Design documents from `.specify/specs/001-k8s-minikube-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are excluded.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Infrastructure manifests: `deployments/minikube/`
- Helm charts: `deployments/helm-charts/`
- Container definitions: `backend/Dockerfile`, `frontend/Dockerfile`
- Documentation: `.specify/specs/001-k8s-minikube-deployment/`

---

## Phase 1: Setup (Environment & Tooling)

**Purpose**: Initialize local Kubernetes environment and required tooling

- [ ] T001 Install and verify Minikube v1.32+ with Docker driver
- [ ] T002 Install and verify kubectl v1.28+ CLI tool
- [ ] T003 [P] Install and verify Helm v3.13+ package manager
- [ ] T004 [P] Configure kubectl-ai for AI-assisted Kubernetes operations
- [ ] T005 Start Minikube cluster with 4 CPUs and 8GB RAM minimum
- [ ] T006 [P] Enable Minikube ingress addon for external access
- [ ] T007 [P] Enable Minikube metrics-server addon for HPA support
- [x] T008 Create project directory structure in deployments/minikube/
- [x] T009 Create Helm chart directory structure in deployments/helm-charts/todo-chatbot/

---

## Phase 2: Foundational (Containerization & Base Infrastructure)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Containerization

- [x] T010 [P] Create multi-stage Dockerfile for Next.js frontend in frontend/Dockerfile
- [x] T011 [P] Create multi-stage Dockerfile for FastAPI backend in backend/Dockerfile
- [x] T012 [P] Create .dockerignore file for frontend in frontend/.dockerignore
- [x] T013 [P] Create .dockerignore file for backend in backend/.dockerignore
- [ ] T014 Build frontend Docker image and tag as todo-frontend:latest
- [ ] T015 Build backend Docker image and tag as todo-backend:latest
- [ ] T016 Load frontend image into Minikube registry using minikube image load
- [ ] T017 Load backend image into Minikube registry using minikube image load
- [ ] T018 Verify images are available in Minikube with minikube image ls

### Base Kubernetes Resources

- [x] T019 Create todo-chatbot namespace manifest in deployments/minikube/namespace.yaml
- [ ] T020 Apply namespace to Minikube cluster
- [x] T021 [P] Create RBAC service account manifest in deployments/minikube/security/rbac.yaml
- [x] T022 [P] Create base network policy with default-deny in deployments/minikube/security/network-policy.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 & 4 - Deploy Application with Data Persistence (Priority: P1) 🎯 MVP

**Goal**: Deploy the complete Todo Chatbot application on Minikube with persistent database storage

**Independent Test**: Deploy all components to Minikube, verify frontend is accessible via ingress, backend responds to API calls, and data persists across pod restarts

**User Stories Covered**:
- US1: Developer Deploys Application on Local Kubernetes
- US4: System Maintains Data Persistence

### Database Deployment with Persistence

- [x] T023 [P] [US1] [US4] Create PostgreSQL PersistentVolumeClaim manifest in deployments/minikube/postgresql/pvc.yaml
- [x] T024 [P] [US1] [US4] Create PostgreSQL ConfigMap with init scripts in deployments/minikube/postgresql/configmap.yaml
- [x] T025 [US1] [US4] Create PostgreSQL StatefulSet manifest in deployments/minikube/postgresql/deployment.yaml
- [x] T026 [US1] [US4] Create PostgreSQL Service manifest (ClusterIP) in deployments/minikube/postgresql/service.yaml
- [ ] T027 [US1] [US4] Apply PostgreSQL PVC to cluster
- [ ] T028 [US1] [US4] Apply PostgreSQL ConfigMap to cluster
- [ ] T029 [US1] [US4] Apply PostgreSQL StatefulSet to cluster
- [ ] T030 [US1] [US4] Apply PostgreSQL Service to cluster
- [ ] T031 [US1] [US4] Verify PostgreSQL pod is running and ready with kubectl wait

### Backend Deployment

- [x] T032 [P] [US1] Create backend ConfigMap with non-sensitive config in deployments/minikube/backend/configmap.yaml
- [x] T033 [US1] Create backend Deployment manifest with resource limits in deployments/minikube/backend/deployment.yaml
- [x] T034 [US1] Create backend Service manifest (ClusterIP) in deployments/minikube/backend/service.yaml
- [ ] T035 [US1] Apply backend ConfigMap to cluster
- [ ] T036 [US1] Apply backend Deployment to cluster
- [ ] T037 [US1] Apply backend Service to cluster
- [ ] T038 [US1] Verify backend pods are running and ready with kubectl wait

### Frontend Deployment

- [x] T039 [P] [US1] Create frontend ConfigMap with API endpoint config in deployments/minikube/frontend/configmap.yaml
- [x] T040 [US1] Create frontend Deployment manifest with resource limits in deployments/minikube/frontend/deployment.yaml
- [x] T041 [US1] Create frontend Service manifest (ClusterIP) in deployments/minikube/frontend/service.yaml
- [ ] T042 [US1] Apply frontend ConfigMap to cluster
- [ ] T043 [US1] Apply frontend Deployment to cluster
- [ ] T044 [US1] Apply frontend Service to cluster
- [ ] T045 [US1] Verify frontend pods are running and ready with kubectl wait

### Ingress Configuration

- [x] T046 [US1] Create Ingress manifest with path routing in deployments/minikube/ingress/ingress.yaml
- [ ] T047 [US1] Apply Ingress configuration to cluster
- [ ] T048 [US1] Get Minikube IP and configure local hosts file for todo.local
- [ ] T049 [US1] Verify ingress routes traffic to frontend and backend services

### Data Persistence Validation

- [ ] T050 [US4] Create test data in database via backend API
- [ ] T051 [US4] Delete PostgreSQL pod to trigger restart
- [ ] T052 [US4] Verify data persists after pod restart by querying API
- [ ] T053 [US4] Perform rolling update of backend deployment
- [ ] T054 [US4] Verify data persists through rolling update

**Checkpoint**: At this point, the complete application is deployed and accessible with persistent data storage

---

## Phase 4: User Story 2 - Secure Configuration Management (Priority: P1)

**Goal**: Implement secure management of environment variables and sensitive credentials using Kubernetes ConfigMaps and Secrets

**Independent Test**: Verify secrets are stored securely, configuration can be updated without redeployment, and applications pick up new configuration

**User Story Covered**:
- US2: Admin Configures Environment Variables and Secrets

### Secrets Management

- [x] T055 [P] [US2] Create Kubernetes Secret manifest for PostgreSQL password in deployments/minikube/security/secrets.yaml
- [x] T056 [P] [US2] Add JWT secret key to secrets manifest
- [x] T057 [P] [US2] Add Google Gemini API key to secrets manifest
- [x] T058 [P] [US2] Add Groq API key to secrets manifest
- [ ] T059 [US2] Apply secrets to cluster with kubectl apply
- [ ] T060 [US2] Update backend Deployment to mount secrets as environment variables
- [ ] T061 [US2] Update PostgreSQL StatefulSet to use secret for password
- [ ] T062 [US2] Apply updated backend Deployment manifest
- [ ] T063 [US2] Apply updated PostgreSQL StatefulSet manifest
- [ ] T064 [US2] Verify backend pods restart and load secrets correctly

### Configuration Updates

- [ ] T065 [US2] Update backend ConfigMap with new configuration value
- [ ] T066 [US2] Apply updated ConfigMap to cluster
- [ ] T067 [US2] Trigger rolling restart of backend deployment
- [ ] T068 [US2] Verify backend picks up new configuration without data loss
- [ ] T069 [US2] Document configuration update procedure in deployments/minikube/README.md

### Security Validation

- [ ] T070 [US2] Verify secrets are not visible in pod descriptions with kubectl describe
- [ ] T071 [US2] Verify secrets are base64 encoded in etcd
- [ ] T072 [US2] Verify ConfigMaps do not contain sensitive data
- [ ] T073 [US2] Update network policies to restrict secret access in deployments/minikube/security/network-policy.yaml

**Checkpoint**: Configuration and secrets are managed securely and can be updated independently

---

## Phase 5: User Story 3 - Horizontal Pod Autoscaling (Priority: P2)

**Goal**: Implement automatic scaling of application pods based on CPU and memory utilization

**Independent Test**: Simulate load on the application and verify pods scale up automatically, then verify scale-down when load decreases

**User Story Covered**:
- US3: System Scales Application Automatically

### HPA Configuration

- [x] T074 [P] [US3] Create HorizontalPodAutoscaler manifest for backend in deployments/minikube/backend/hpa.yaml
- [x] T075 [P] [US3] Create HorizontalPodAutoscaler manifest for frontend in deployments/minikube/frontend/hpa.yaml
- [ ] T076 [US3] Configure backend HPA with CPU threshold at 70% and min/max replicas
- [ ] T077 [US3] Configure frontend HPA with CPU threshold at 70% and min/max replicas
- [ ] T078 [US3] Apply backend HPA to cluster
- [ ] T079 [US3] Apply frontend HPA to cluster
- [ ] T080 [US3] Verify HPA resources are created with kubectl get hpa

### Resource Limits Configuration

- [ ] T081 [US3] Update backend Deployment with CPU/memory requests and limits
- [ ] T082 [US3] Update frontend Deployment with CPU/memory requests and limits
- [ ] T083 [US3] Apply updated backend Deployment manifest
- [ ] T084 [US3] Apply updated frontend Deployment manifest
- [ ] T085 [US3] Verify resource limits are applied with kubectl describe pod

### Scaling Validation

- [ ] T086 [US3] Install load testing tool (hey or ab) for generating traffic
- [ ] T087 [US3] Generate sustained load on backend API to exceed CPU threshold
- [ ] T088 [US3] Monitor HPA status and verify pods scale up within 2 minutes
- [ ] T089 [US3] Stop load generation and verify pods scale down after cooldown period
- [ ] T090 [US3] Document scaling behavior and thresholds in deployments/minikube/README.md

**Checkpoint**: Application automatically scales based on resource utilization

---

## Phase 6: User Story 5 - Health Monitoring & Self-Healing (Priority: P2)

**Goal**: Implement comprehensive health checks and enable Kubernetes self-healing capabilities

**Independent Test**: Cause failures in application components and verify Kubernetes automatically restarts unhealthy pods

**User Story Covered**:
- US5: System Monitors Health and Recovers Automatically

### Health Probes Implementation

- [ ] T091 [US5] Add liveness probe to backend Deployment manifest (HTTP /api/health endpoint)
- [ ] T092 [US5] Add readiness probe to backend Deployment manifest (HTTP /api/health endpoint)
- [ ] T093 [US5] Add startup probe to backend Deployment manifest for slow starts
- [ ] T094 [US5] Add liveness probe to frontend Deployment manifest (HTTP / endpoint)
- [ ] T095 [US5] Add readiness probe to frontend Deployment manifest (HTTP / endpoint)
- [ ] T096 [US5] Add liveness probe to PostgreSQL StatefulSet (pg_isready command)
- [ ] T097 [US5] Add readiness probe to PostgreSQL StatefulSet (pg_isready command)
- [ ] T098 [US5] Apply updated backend Deployment with health probes
- [ ] T099 [US5] Apply updated frontend Deployment with health probes
- [ ] T100 [US5] Apply updated PostgreSQL StatefulSet with health probes

### Self-Healing Validation

- [ ] T101 [US5] Simulate backend pod crash by killing process inside container
- [ ] T102 [US5] Verify Kubernetes automatically restarts crashed backend pod
- [ ] T103 [US5] Verify service availability is maintained during pod restart
- [ ] T104 [US5] Simulate unresponsive backend by blocking health endpoint
- [ ] T105 [US5] Verify Kubernetes marks pod as unhealthy and restarts it
- [ ] T106 [US5] Verify readiness probe prevents traffic to unhealthy pods
- [ ] T107 [US5] Document health check configuration in deployments/minikube/README.md

### Monitoring Setup (Optional Enhancement)

- [ ] T108 [P] [US5] Create Prometheus deployment manifest in deployments/minikube/monitoring/prometheus/
- [ ] T109 [P] [US5] Create Grafana deployment manifest in deployments/minikube/monitoring/grafana/
- [ ] T110 [US5] Configure Prometheus to scrape metrics from application pods
- [ ] T111 [US5] Create Grafana dashboard for application health metrics
- [ ] T112 [US5] Apply monitoring stack to cluster

**Checkpoint**: All application components have health checks and self-healing capabilities

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Helm Chart Creation

- [ ] T113 [P] Create Helm Chart.yaml in deployments/helm-charts/todo-chatbot/Chart.yaml
- [ ] T114 [P] Create Helm values.yaml with configurable parameters in deployments/helm-charts/todo-chatbot/values.yaml
- [ ] T115 [P] Create Helm deployment template in deployments/helm-charts/todo-chatbot/templates/deployment.yaml
- [ ] T116 [P] Create Helm service template in deployments/helm-charts/todo-chatbot/templates/service.yaml
- [ ] T117 [P] Create Helm ingress template in deployments/helm-charts/todo-chatbot/templates/ingress.yaml
- [ ] T118 [P] Create Helm PVC template in deployments/helm-charts/todo-chatbot/templates/pvc.yaml
- [ ] T119 Test Helm chart installation with helm install
- [ ] T120 Test Helm chart upgrade with helm upgrade
- [ ] T121 Test Helm chart rollback with helm rollback

### Kustomize Overlays

- [ ] T122 [P] Create base kustomization.yaml in deployments/minikube/ci-cd/kustomization.yaml
- [ ] T123 [P] Create development overlay in deployments/minikube/ci-cd/overlays/dev/
- [ ] T124 [P] Create production overlay in deployments/minikube/ci-cd/overlays/prod/
- [ ] T125 Test kustomize build for development environment
- [ ] T126 Test kustomize build for production environment

### Documentation & Validation

- [ ] T127 [P] Create comprehensive deployment guide in deployments/minikube/README.md
- [ ] T128 [P] Document rollback procedures in deployments/minikube/ROLLBACK.md
- [ ] T129 [P] Document troubleshooting guide in deployments/minikube/TROUBLESHOOTING.md
- [ ] T130 Create deployment validation script in deployments/minikube/scripts/validate-deployment.sh
- [ ] T131 Create cleanup script in deployments/minikube/scripts/cleanup.sh
- [ ] T132 Run complete quickstart.md validation from fresh Minikube cluster
- [ ] T133 Verify all success criteria from spec.md are met
- [ ] T134 Document known limitations and future improvements

### Security Hardening

- [ ] T135 [P] Implement Pod Security Standards (restricted) in namespace
- [ ] T136 [P] Configure non-root user for all container images
- [ ] T137 [P] Enable read-only root filesystem where possible
- [ ] T138 [P] Drop unnecessary Linux capabilities from containers
- [ ] T139 Run security scan on deployed configuration with kubesec or similar
- [ ] T140 Address any high or critical security findings

### Performance Optimization

- [ ] T141 [P] Configure resource quotas for namespace in deployments/minikube/resource-quota.yaml
- [ ] T142 [P] Configure limit ranges for namespace in deployments/minikube/limit-range.yaml
- [ ] T143 Optimize container image sizes by reviewing Dockerfile layers
- [ ] T144 Configure pod disruption budgets for high availability
- [ ] T145 Test zero-downtime deployment with rolling update strategy

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 & US4 (Phase 3): Can start after Foundational - No dependencies on other stories
  - US2 (Phase 4): Can start after Foundational - Enhances US1 but independently testable
  - US3 (Phase 5): Depends on US1 completion (needs deployments to scale)
  - US5 (Phase 6): Can start after Foundational - Enhances US1 but independently testable
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 & 4 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 but independently testable
- **User Story 3 (P2)**: Depends on US1 completion - Requires deployments to exist for scaling
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Enhances US1 but independently testable

### Within Each User Story

- Database before backend (backend depends on database connection)
- Backend before frontend (frontend calls backend API)
- Services before ingress (ingress routes to services)
- Deployments before HPA (HPA scales deployments)
- Resource limits before HPA (HPA requires resource requests)

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational containerization tasks marked [P] can run in parallel
- Within US1: PostgreSQL ConfigMap and PVC can be created in parallel
- Within US1: Backend and frontend ConfigMaps can be created in parallel
- Within US2: All secret additions can be done in parallel
- Within US3: Backend and frontend HPA manifests can be created in parallel
- Within US5: Health probes for all components can be added in parallel
- Within Polish: Documentation tasks can run in parallel
- US2 and US5 can be worked on in parallel by different team members after US1 completes

---

## Parallel Example: User Story 1 & 4

```bash
# Launch database configuration tasks together:
Task: "Create PostgreSQL PersistentVolumeClaim manifest"
Task: "Create PostgreSQL ConfigMap with init scripts"

# Launch application ConfigMaps together:
Task: "Create backend ConfigMap with non-sensitive config"
Task: "Create frontend ConfigMap with API endpoint config"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 4 Only)

1. Complete Phase 1: Setup (Environment & Tooling)
2. Complete Phase 2: Foundational (Containerization) - CRITICAL
3. Complete Phase 3: User Story 1 & 4 (Deploy with Persistence)
4. Complete Phase 4: User Story 2 (Secure Configuration)
5. **STOP and VALIDATE**: Test complete application deployment independently
6. Deploy/demo if ready - this is a production-ready MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 & US4 → Test independently → Deploy/Demo (Basic deployment with persistence)
3. Add US2 → Test independently → Deploy/Demo (Secure configuration added)
4. Add US3 → Test independently → Deploy/Demo (Auto-scaling added)
5. Add US5 → Test independently → Deploy/Demo (Self-healing added)
6. Add Polish → Complete production-ready deployment
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 & 4 (Deploy with Persistence)
   - Developer B: User Story 2 (Configuration) - can start in parallel
   - Developer C: User Story 5 (Health Monitoring) - can start in parallel
3. After US1 completes:
   - Developer D: User Story 3 (Auto-scaling) - requires US1
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All Kubernetes manifests should be applied with `kubectl apply -f` for declarative management
- Use `kubectl wait` to verify resources are ready before proceeding
- Test rollback procedures after each major deployment
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Resource limits are critical for HPA to function properly
- Network policies should be tested to ensure they don't block required communication
