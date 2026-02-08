# Data Model: Kubernetes Minikube Deployment

## Key Entities

### 1. Application Deployment
- **Components**: frontend, backend, database
- **Configuration**: Resource requests/limits, environment variables
- **Relationships**: Connects to services, uses persistent volumes
- **Validation**: Resource limits must not exceed cluster capacity

### 2. Kubernetes Service
- **Fields**: Service type (ClusterIP, NodePort, LoadBalancer), port mappings
- **Relationships**: Connects deployments internally, connects to ingress externally
- **State**: Active, Pending, Terminated

### 3. Persistent Volume
- **Fields**: Storage class, size, access mode, reclaim policy
- **Relationships**: Bound to StatefulSets (database), mounted to containers
- **Validation**: Storage must be available in cluster, size must be sufficient

### 4. Configuration (ConfigMap/Secret)
- **Fields**: Key-value pairs, namespace scope
- **Relationships**: Mounted to deployments as environment variables or volumes
- **Validation**: Sensitive data must be stored in Secrets, not ConfigMaps

### 5. Network Policy
- **Fields**: Ingress/egress rules, pod selectors, namespace selectors
- **Relationships**: Applied to namespaces and pods
- **Validation**: Rules must not prevent required service communication

### 6. Ingress Resource
- **Fields**: Hostnames, path mappings, TLS configuration
- **Relationships**: Routes external traffic to services
- **Validation**: Hostnames must be resolvable, paths must match service endpoints