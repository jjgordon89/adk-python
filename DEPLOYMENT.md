# SafetyCulture ADK Agent - Production Deployment Guide

**Version:** 1.0.0  
**Last Updated:** 2025-01-30  
**Status:** Production Ready ✅

This comprehensive guide covers deploying the SafetyCulture ADK Agent system to production environments, including Docker, Google Cloud Run, and Google Kubernetes Engine (GKE).

## Table of Contents

- [Overview](#overview)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Architecture Overview](#architecture-overview)
- [Local Development Deployment](#local-development-deployment)
- [Docker Deployment](#docker-deployment)
- [Google Cloud Run Deployment](#google-cloud-run-deployment)
- [Google Kubernetes Engine (GKE) Deployment](#google-kubernetes-engine-gke-deployment)
- [Production Best Practices](#production-best-practices)
- [Environment Configuration](#environment-configuration)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Observability](#monitoring--observability)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Cost Optimization](#cost-optimization)
- [Disaster Recovery](#disaster-recovery)

---

## Overview

The SafetyCulture ADK Agent consists of two main components:

1. **Backend Agent** - Python-based ADK agent with FastAPI server
2. **Frontend GUI** - React TypeScript application (optional)

### System Requirements

**Backend:**
- Python 3.10+
- Google Cloud Platform access (Vertex AI enabled)
- SafetyCulture API credentials
- SQLite database storage
- Memory service storage

**Frontend (Optional):**
- Node.js 18+ (for building)
- Static file hosting (production)

---

## Pre-Deployment Checklist

### 1. Required Credentials & API Keys

- [ ] **SafetyCulture API Token**
  - Generate at: https://app.safetyculture.com/account/api-tokens
  - Permissions: Read assets, templates, inspections; Write inspections
  
- [ ] **Google Cloud Project**
  - Project ID configured
  - Vertex AI API enabled: `gcloud services enable aiplatform.googleapis.com`
  - Billing enabled
  - Region selected (recommended: `us-central1`)

- [ ] **Service Account** (Production)
  - Create service account with roles:
    - `roles/aiplatform.user` (Vertex AI access)
    - `roles/storage.objectViewer` (if using GCS)
    - `roles/logging.logWriter` (Cloud Logging)
  - Generate and download JSON key file

- [ ] **Optional Provider Keys**
  - Nvidia API key (if using Nvidia models)
  - Ollama setup (for local development)

### 2. GCP Project Setup

```bash
# Set your project
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

# Configure gcloud
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION

# Enable required APIs
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com

# Create service account
gcloud iam service-accounts create safetyculture-agent \
  --display-name="SafetyCulture ADK Agent Service Account"

# Grant required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:safetyculture-agent@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:safetyculture-agent@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

### 3. Network Requirements

- [ ] Outbound HTTPS access to:
  - `aiplatform.googleapis.com` (Vertex AI)
  - `api.safetyculture.io` (SafetyCulture API)
  - `build.nvidia.com` (if using Nvidia)
  - `ollama.ai` (if using Ollama)

### 4. Storage Requirements

- [ ] **SQLite Database Volume** - Persistent storage for asset tracking
- [ ] **Memory Service Storage** - Persistent storage for ADK MemoryService
- [ ] **Logs Storage** - Log aggregation setup

### 5. Security Checklist

⚠️ **CRITICAL SECURITY REQUIREMENTS:**

- [ ] Never commit `.env` files or credentials to version control
- [ ] Use Google Secret Manager or equivalent for production secrets
- [ ] Enable Cloud Armor for DDoS protection (if public-facing)
- [ ] Configure VPC Service Controls (for sensitive workloads)
- [ ] Enable Cloud Audit Logs
- [ ] Set up alerts for unauthorized access attempts
- [ ] Use service accounts with least-privilege access
- [ ] Enable TLS/SSL for all endpoints
- [ ] Implement authentication for GUI (if public)
- [ ] Regular security scanning of dependencies

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Load Balancer                           │
│                    (Cloud Load Balancer)                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │                               │
        ▼                               ▼
┌────────────────┐              ┌────────────────┐
│  Backend Agent │              │  Frontend GUI  │
│  (Cloud Run)   │              │  (Cloud Run)   │
│  Port: 8000    │◄─────────────│  Port: 80      │
└────────┬───────┘              └────────────────┘
         │
         ├──────────► Google Cloud Storage (Memory/Database)
         │
         ├──────────► Vertex AI (Gemini Models)
         │
         ├──────────► SafetyCulture API
         │
         └──────────► Secret Manager (Credentials)
```

---

## Local Development Deployment

### Quick Start (Development)

```bash
# 1. Clone and navigate to project
git clone https://github.com/yourusername/adk-python.git
cd adk-python

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r safetyculture_agent/requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Authenticate with Google Cloud
gcloud auth application-default login

# 6. Start backend
adk web safetyculture_agent/agent.py --host 0.0.0.0 --port 8000

# 7. In another terminal, start GUI (optional)
cd adk-gui
npm install
cp .env.example .env
npm run dev
```

### Development with Ollama (Zero API Costs)

```bash
# Install Ollama
# macOS/Linux: curl -fsSL https://ollama.ai/install.sh | sh
# Windows: Download from https://ollama.ai/download

# Pull model
ollama pull llama3

# Configure environment
export MODEL_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434

# Start agent
adk web safetyculture_agent/agent.py
```

---

## Docker Deployment

### Backend Dockerfile

Create [`Dockerfile.backend`](Dockerfile.backend):

```dockerfile
# Multi-stage build for optimized production image
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy and install Python dependencies
COPY safetyculture_agent/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 agent && \
    mkdir -p /app/data /app/logs && \
    chown -R agent:agent /app

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/agent/.local

# Copy application code
COPY --chown=agent:agent safetyculture_agent/ ./safetyculture_agent/

# Copy ADK source if needed
COPY --chown=agent:agent src/ ./src/

# Switch to non-root user
USER agent

# Add local Python packages to PATH
ENV PATH=/home/agent/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["adk", "web", "safetyculture_agent/agent.py", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create [`Dockerfile.frontend`](Dockerfile.frontend):

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /build

# Copy package files
COPY adk-gui/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY adk-gui/ ./

# Build production bundle
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine

# Copy custom nginx config
COPY <<EOF /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # SPA routing
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Copy built assets
COPY --from=builder /build/dist /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose Setup

Create [`docker-compose.yml`](docker-compose.yml):

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: safetyculture-agent
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - SAFETYCULTURE_API_TOKEN=${SAFETYCULTURE_API_TOKEN}
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
      - GOOGLE_CLOUD_REGION=${GOOGLE_CLOUD_REGION}
      - GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
    volumes:
      # Persistent storage for database
      - agent-data:/app/data
      # Persistent storage for memory
      - agent-memory:/app/.adk/memory
      # Logs
      - agent-logs:/app/logs
      # GCP credentials
      - ./secrets/gcp-key.json:/secrets/gcp-key.json:ro
    networks:
      - agent-network
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: safetyculture-gui
    restart: unless-stopped
    ports:
      - "3000:80"
    environment:
      - VITE_ADK_API_URL=http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - agent-network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 3s
      retries: 3

volumes:
  agent-data:
    driver: local
  agent-memory:
    driver: local
  agent-logs:
    driver: local

networks:
  agent-network:
    driver: bridge
```

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Production Docker Commands

```bash
# Build with version tag
docker build -f Dockerfile.backend -t safetyculture-agent:1.0.0 .
docker build -f Dockerfile.frontend -t safetyculture-gui:1.0.0 .

# Tag for container registry
docker tag safetyculture-agent:1.0.0 gcr.io/${PROJECT_ID}/safetyculture-agent:1.0.0
docker tag safetyculture-gui:1.0.0 gcr.io/${PROJECT_ID}/safetyculture-gui:1.0.0

# Push to Google Container Registry
docker push gcr.io/${PROJECT_ID}/safetyculture-agent:1.0.0
docker push gcr.io/${PROJECT_ID}/safetyculture-gui:1.0.0
```

---

## Google Cloud Run Deployment

Cloud Run provides serverless container deployment with automatic scaling and zero infrastructure management.

### Prerequisites

```bash
# Set variables
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export SERVICE_ACCOUNT="safetyculture-agent@${PROJECT_ID}.iam.gserviceaccount.com"
```

### Store Secrets in Secret Manager

```bash
# Create secrets
echo -n "your-safetyculture-token" | \
  gcloud secrets create safetyculture-api-token \
  --data-file=- \
  --replication-policy="automatic"

# For service account key (if not using Workload Identity)
gcloud secrets create gcp-service-account-key \
  --data-file=./secrets/gcp-key.json \
  --replication-policy="automatic"

# Grant service account access to secrets
gcloud secrets add-iam-policy-binding safetyculture-api-token \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding gcp-service-account-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

### Backend Deployment

Create [`cloudrun-backend.yaml`](cloudrun-backend.yaml):

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: safetyculture-agent
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/launch-stage: BETA
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: '1'
        autoscaling.knative.dev/maxScale: '10'
        run.googleapis.com/cpu-throttling: 'false'
        run.googleapis.com/startup-cpu-boost: 'true'
    spec:
      serviceAccountName: safetyculture-agent@PROJECT_ID.iam.gserviceaccount.com
      timeoutSeconds: 300
      containerConcurrency: 80
      containers:
      - image: gcr.io/PROJECT_ID/safetyculture-agent:1.0.0
        ports:
        - name: http1
          containerPort: 8000
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "PROJECT_ID"
        - name: GOOGLE_CLOUD_REGION
          value: "us-central1"
        - name: SAFETYCULTURE_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: safetyculture-api-token
              key: latest
        resources:
          limits:
            cpu: '2'
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 5
          failureThreshold: 12
```

Deploy using gcloud:

```bash
# Build and push image
gcloud builds submit --tag gcr.io/${PROJECT_ID}/safetyculture-agent:1.0.0 \
  --dockerfile Dockerfile.backend

# Deploy to Cloud Run
gcloud run deploy safetyculture-agent \
  --image gcr.io/${PROJECT_ID}/safetyculture-agent:1.0.0 \
  --region ${REGION} \
  --platform managed \
  --service-account ${SERVICE_ACCOUNT} \
  --set-env-vars GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_REGION=${REGION} \
  --set-secrets SAFETYCULTURE_API_TOKEN=safetyculture-api-token:latest \
  --cpu 2 \
  --memory 4Gi \
  --timeout 300 \
  --concurrency 80 \
  --min-instances 1 \
  --max-instances 10 \
  --cpu-boost \
  --no-allow-unauthenticated

# Get service URL
gcloud run services describe safetyculture-agent \
  --region ${REGION} \
  --format 'value(status.url)'
```

### Frontend Deployment

```bash
# Build with backend URL
cd adk-gui
export BACKEND_URL=$(gcloud run services describe safetyculture-agent --region ${REGION} --format 'value(status.url)')

# Create production .env
cat > .env.production <<EOF
VITE_ADK_API_URL=${BACKEND_URL}
VITE_ADK_API_TIMEOUT=30000
VITE_SSE_RECONNECT_DELAY=3000
VITE_ENABLE_DEBUG=false
EOF

# Build
npm run build

# Deploy to Cloud Run
cd ..
gcloud builds submit --tag gcr.io/${PROJECT_ID}/safetyculture-gui:1.0.0 \
  --dockerfile Dockerfile.frontend

gcloud run deploy safetyculture-gui \
  --image gcr.io/${PROJECT_ID}/safetyculture-gui:1.0.0 \
  --region ${REGION} \
  --platform managed \
  --allow-unauthenticated \
  --cpu 1 \
  --memory 512Mi \
  --min-instances 0 \
  --max-instances 5
```

### Cloud Run Scaling Configuration

```bash
# Auto-scaling based on CPU
gcloud run services update safetyculture-agent \
  --region ${REGION} \
  --cpu-throttling \
  --concurrency 80 \
  --min-instances 1 \
  --max-instances 10

# Auto-scaling based on requests
gcloud run services update safetyculture-agent \
  --region ${REGION} \
  --no-cpu-throttling \
  --concurrency 100 \
  --min-instances 2 \
  --max-instances 20
```

### Cloud Run Cost Optimization

```bash
# Development: Scale to zero
gcloud run services update safetyculture-agent \
  --region ${REGION} \
  --min-instances 0 \
  --max-instances 3 \
  --cpu 1 \
  --memory 2Gi

# Production: Keep warm instances
gcloud run services update safetyculture-agent \
  --region ${REGION} \
  --min-instances 2 \
  --max-instances 10 \
  --cpu 2 \
  --memory 4Gi

# High-traffic: Aggressive scaling
gcloud run services update safetyculture-agent \
  --region ${REGION} \
  --min-instances 5 \
  --max-instances 50 \
  --cpu 4 \
  --memory 8Gi
```

---

## Google Kubernetes Engine (GKE) Deployment

For complex deployments requiring advanced orchestration, stateful sets, or custom networking.

### GKE Cluster Setup

```bash
# Create GKE cluster
gcloud container clusters create safetyculture-cluster \
  --region ${REGION} \
  --num-nodes 2 \
  --machine-type n2-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10 \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-ip-alias \
  --workload-pool=${PROJECT_ID}.svc.id.goog \
  --addons HorizontalPodAutoscaling,HttpLoadBalancing,GcePersistentDiskCsiDriver

# Get credentials
gcloud container clusters get-credentials safetyculture-cluster --region ${REGION}

# Verify connection
kubectl cluster-info
```

### Kubernetes Manifests

#### Namespace

Create [`k8s/namespace.yaml`](k8s/namespace.yaml):

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: safetyculture
  labels:
    name: safetyculture
    app: adk-agent
```

#### ConfigMap

Create [`k8s/configmap.yaml`](k8s/configmap.yaml):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-config
  namespace: safetyculture
data:
  GOOGLE_CLOUD_PROJECT: "your-project-id"
  GOOGLE_CLOUD_REGION: "us-central1"
  ADK_LOG_LEVEL: "INFO"
  ADK_MAX_RETRIES: "3"
  ADK_TIMEOUT: "300"
```

#### Secrets

Create [`k8s/secrets.yaml`](k8s/secrets.yaml):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: agent-secrets
  namespace: safetyculture
type: Opaque
stringData:
  SAFETYCULTURE_API_TOKEN: "your-token-here"
  # Or use External Secrets Operator to sync from Secret Manager
```

Better approach - use External Secrets:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: gcpsm-secret-store
  namespace: safetyculture
spec:
  provider:
    gcpsm:
      projectID: "your-project-id"
      auth:
        workloadIdentity:
          clusterLocation: us-central1
          clusterName: safetyculture-cluster
          serviceAccountRef:
            name: agent-sa
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: agent-secrets
  namespace: safetyculture
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: gcpsm-secret-store
    kind: SecretStore
  target:
    name: agent-secrets
    creationPolicy: Owner
  data:
  - secretKey: SAFETYCULTURE_API_TOKEN
    remoteRef:
      key: safetyculture-api-token
```

#### Persistent Volumes

Create [`k8s/pvc.yaml`](k8s/pvc.yaml):

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: agent-data-pvc
  namespace: safetyculture
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard-rwo
  resources:
    requests:
      storage: 10Gi
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: agent-memory-pvc
  namespace: safetyculture
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: standard-rwo
  resources:
    requests:
      storage: 5Gi
```

#### Backend Deployment

Create [`k8s/backend-deployment.yaml`](k8s/backend-deployment.yaml):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: safetyculture-agent
  namespace: safetyculture
  labels:
    app: safetyculture-agent
    component: backend
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: safetyculture-agent
      component: backend
  template:
    metadata:
      labels:
        app: safetyculture-agent
        component: backend
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: agent-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: agent
        image: gcr.io/PROJECT_ID/safetyculture-agent:1.0.0
        imagePullPolicy: Always
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        envFrom:
        - configMapRef:
            name: agent-config
        - secretRef:
            name: agent-secrets
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 0
          periodSeconds: 5
          timeoutSeconds: 5
          failureThreshold: 30
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: memory
          mountPath: /app/.adk/memory
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: agent-data-pvc
      - name: memory
        persistentVolumeClaim:
          claimName: agent-memory-pvc
```

#### Service

Create [`k8s/backend-service.yaml`](k8s/backend-service.yaml):

```yaml
apiVersion: v1
kind: Service
metadata:
  name: safetyculture-agent
  namespace: safetyculture
  labels:
    app: safetyculture-agent
    component: backend
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: safetyculture-agent
    component: backend
```

#### Horizontal Pod Autoscaler

Create [`k8s/hpa.yaml`](k8s/hpa.yaml):

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: safetyculture-agent-hpa
  namespace: safetyculture
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: safetyculture-agent
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 60
      selectPolicy: Max
```

#### Ingress

Create [`k8s/ingress.yaml`](k8s/ingress.yaml):

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: safetyculture-ingress
  namespace: safetyculture
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "safetyculture-ip"
    networking.gke.io/managed-certificates: "safetyculture-cert"
    kubernetes.io/ingress.allow-http: "true"
spec:
  rules:
  - host: agent.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: safetyculture-agent
            port:
              number: 8000
  - host: gui.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: safetyculture-gui
            port:
              number: 80
```

#### Managed Certificate (SSL/TLS)

Create [`k8s/certificate.yaml`](k8s/certificate.yaml):

```yaml
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: safetyculture-cert
  namespace: safetyculture
spec:
  domains:
    - agent.yourdomain.com
    - gui.yourdomain.com
```

### Deploy to GKE

```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/certificate.yaml
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get pods -n safetyculture
kubectl get svc -n safetyculture
kubectl get ing -n safetyculture

# View logs
kubectl logs -f deployment/safetyculture-agent -n safetyculture

# Scale manually
kubectl scale deployment safetyculture-agent --replicas=5 -n safetyculture

# Rolling update
kubectl set image deployment/safetyculture-agent \
  agent=gcr.io/${PROJECT_ID}/safetyculture-agent:1.1.0 \
  -n safetyculture

# Rollback
kubectl rollout undo deployment/safetyculture-agent -n safetyculture
```

---

## Production Best Practices

### 1. Security Hardening

#### Use Secret Manager

```bash
# Never use environment variables for secrets in production
# Always use Secret Manager or equivalent

# Access secrets at runtime
from google.cloud import secretmanager

def get_secret(secret_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

#### Network Security

```bash
# Use VPC Service Controls
gcloud access-context-manager perimeters create safetyculture-perimeter \
  --title="SafetyCulture Agent Perimeter" \
  --resources=projects/${PROJECT_NUMBER} \
  --restricted-services=aiplatform.googleapis.com

# Enable Private Google Access
gcloud compute networks subnets update default \
  --region=${REGION} \
  --enable-private-ip-google-access
```

#### Identity and Access Management

```bash
# Use Workload Identity (GKE)
gcloud iam service-accounts add-iam-policy-binding ${SERVICE_ACCOUNT} \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[safetyculture/agent-sa]"

# Annotate Kubernetes service account
kubectl annotate serviceaccount agent-sa \
  -n safetyculture \
  iam.gke.io/gcp-service-account=${SERVICE_ACCOUNT}
```

### 2. Monitoring Setup

#### Cloud Monitoring Alerts

Create [`monitoring/alerts.yaml`](monitoring/alerts.yaml):

```yaml
# High error rate alert
displayName: "High Agent Error Rate"
conditions:
  - displayName: "Error rate > 5%"
    conditionThreshold:
      filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"'
      comparison: COMPARISON_GT
      thresholdValue: 0.05
      duration: 300s
      aggregations:
        - alignmentPeriod: 60s
          perSeriesAligner: ALIGN_RATE
notificationChannels:
  - projects/${PROJECT_ID}/notificationChannels/${CHANNEL_ID}
```

Deploy alerts:

```bash
gcloud alpha monitoring policies create --policy-from-file=monitoring/alerts.yaml
```

#### Custom Metrics

Add to agent code:

```python
from google.cloud import monitoring_v3
import time

def record_metric(metric_name: str, value: float):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"
    
    series = monitoring_v3.TimeSeries()
    series.metric.type = f"custom.googleapis.com/agent/{metric_name}"
    series.resource.type = "global"
    
    point = monitoring_v3.Point()
    point.value.double_value = value
    point.interval.end_time.seconds = int(time.time())
    
    series.points = [point]
    client.create_time_series(name=project_name, time_series=[series])

# Usage
record_metric("inspection_created", 1.0)
record_metric("template_match_confidence", 0.95)
```

### 3. Logging Strategy

#### Structured Logging

```python
import logging
import json
from google.cloud import logging as cloud_logging

# Configure Cloud Logging
logging_client = cloud_logging.Client()
logging_client.setup_logging()

# Use structured logs
logger = logging.getLogger(__name__)

def log_structured(severity: str, message: str, **kwargs):
    entry = {
        "message": message,
        "severity": severity,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }
    logger.log(getattr(logging, severity), json.dumps(entry))

# Usage
log_structured("INFO", "Inspection created", 
               inspection_id="INS-123", 
               asset_id="AST-456",
               duration_ms=1234)
```

#### Log-based Metrics

```bash
# Create log-based metric for tracking inspection creation
gcloud logging metrics create inspections_created \
  --description="Count of inspections created" \
  --log-filter='resource.type="cloud_run_revision"
    AND jsonPayload.message="Inspection created"'

# Create metric for error tracking
gcloud logging metrics create agent_errors \
  --description="Count of agent errors" \
  --log-filter='resource.type="cloud_run_revision"
    AND severity>=ERROR'
```

### 4. Backup Strategy

#### Database Backups

```bash
# Automated backup script
#!/bin/bash
# backup-database.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="gs://${PROJECT_ID}-backups/database/${TIMESTAMP}"

# Backup SQLite database
gsutil cp /app/data/asset_tracker.db ${BACKUP_PATH}/asset_tracker.db

# Backup memory storage
gsutil -m cp -r /app/.adk/memory ${BACKUP_PATH}/memory/

# Retention: Keep last 30 days
gsutil -m rm gs://${PROJECT_ID}-backups/database/$(date -d '30 days ago' +%Y%m%d)_*/
```

Schedule with Cloud Scheduler:

```bash
# Create Cloud Scheduler job
gcloud scheduler jobs create http backup-agent-data \
  --schedule="0 2 * * *" \
  --uri="https://safetyculture-agent-${REGION}-${PROJECT_ID}.run.app/backup" \
  --http-method=POST \
  --time-zone="America/Los_Angeles"
```

### 5. Performance Optimization

#### Caching Strategy

```python
from functools import lru_cache
import redis

# In-memory cache for templates
@lru_cache(maxsize=100)
def get_template_cached(template_id: str):
    return get_safetyculture_template_details(template_id)

# Redis cache for distributed systems
redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_asset_cached(asset_id: str):
    cache_key = f"asset:{asset_id}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    asset = get_safetyculture_asset_details(asset_id)
    redis_client.setex(cache_key, 3600, json.dumps(asset))
    return asset
```

#### Connection Pooling

```python
import aiohttp
from google.cloud import aiplatform

# Reuse HTTP sessions
class SafetyCultureClient:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        await self.session.close()
    
    async def get_asset(self, asset_id: str):
        async with self.session.get(f"{API_URL}/assets/{asset_id}") as resp:
            return await resp.json()
```

---

## Environment Configuration

### Production .env Template

Create [`.env.production`](.env.production):

```bash
# ============================================================================
# Production Environment Configuration
# ============================================================================
# WARNING: Never commit this file to version control
# Use Secret Manager for production deployments

# SafetyCulture API
SAFETYCULTURE_API_TOKEN=<from-secret-manager>

# Google Cloud Platform
GOOGLE_CLOUD_PROJECT=your-production-project-id
GOOGLE_CLOUD_REGION=us-central1

# Service Account (if not using Workload Identity)
# GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json

# Model Configuration
MODEL_PROVIDER=gemini
DEFAULT_MODEL_ALIAS=production

# Performance Tuning
ADK_MAX_RETRIES=3
ADK_TIMEOUT=300
ADK_CONCURRENCY=80

# Logging
ADK_LOG_LEVEL=INFO
ENABLE_CLOUD_LOGGING=true
ENABLE_STRUCTURED_LOGGING=true

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
ENABLE_TRACING=true

# Security
ENABLE_AUTH=true
CORS_ORIGINS=https://gui.yourdomain.com
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=100

# Database
DATABASE_PATH=/app/data/asset_tracker.db
DATABASE_POOL_SIZE=5
DATABASE_TIMEOUT=30

# Memory Service
MEMORY_BACKEND=gcs
MEMORY_BUCKET=${PROJECT_ID}-agent-memory
MEMORY_TTL=2592000  # 30 days
```

### Multi-Environment Setup

```bash
# Development
.env.development
.env.development.local

# Staging
.env.staging

# Production
.env.production

# Environment-specific overrides
if [ "$ENV" = "production" ]; then
    source .env.production
elif [ "$ENV" = "staging" ]; then
    source .env.staging
else
    source .env.development
fi
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

Create [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml):

```yaml
name: Deploy SafetyCulture Agent

on:
  push:
    branches:
      - main
    tags:
      - 'v*'
  pull_request:
    branches:
      - main

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  REGION: us-central1
  SERVICE_NAME: safetyculture-agent

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r safetyculture_agent/requirements.txt
        pip install pytest pytest-asyncio pylint
    
    - name: Lint with pylint
      run: |
        pylint safetyculture_agent --disable=C0111,R0913
    
    - name: Run tests
      run: |
        pytest tests/ -v --tb=short

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/'))
    
    permissions:
      contents: read
      id-token: write
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
        service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
    
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
    
    - name: Configure Docker
      run: |
        gcloud auth configure-docker gcr.io
    
    - name: Build and push backend
      run: |
        docker build -f Dockerfile.backend -t gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA .
        docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA
        
        # Tag as latest if main branch
        if [ "$GITHUB_REF" = "refs/heads/main" ]; then
          docker tag gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
          docker push gcr.io/$PROJECT_ID/$SERVICE_NAME:latest
        fi
    
    - name: Build and push frontend
      run: |
        docker build -f Dockerfile.frontend -t gcr.io/$PROJECT_ID/$SERVICE_NAME-gui:$GITHUB_SHA .
        docker push gcr.io/$PROJECT_ID/$SERVICE_NAME-gui:$GITHUB_SHA
        
        if [ "$GITHUB_REF" = "refs/heads/main" ]; then
          docker tag gcr.io/$PROJECT_ID/$SERVICE_NAME-gui:$GITHUB_SHA gcr.io/$PROJECT_ID/$SERVICE_NAME-gui:latest
          docker push gcr.io/$PROJECT_ID/$SERVICE_NAME-gui:latest
        fi

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
        service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
    
    - name: Deploy to Cloud Run (Staging)
      run: |
        gcloud run deploy $SERVICE_NAME-staging \
          --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA \
          --region $REGION \
          --platform managed \
          --service-account ${{ secrets.SERVICE_ACCOUNT }} \
          --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_REGION=$REGION,ENV=staging \
          --set-secrets SAFETYCULTURE_API_TOKEN=safetyculture-api-token:latest \
          --cpu 2 \
          --memory 4Gi \
          --timeout 300 \
          --no-allow-unauthenticated

  deploy-production:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    environment: production
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
        service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
    
    - name: Deploy to Cloud Run (Production)
      run: |
        gcloud run deploy $SERVICE_NAME \
          --image gcr.io/$PROJECT_ID/$SERVICE_NAME:$GITHUB_SHA \
          --region $REGION \
          --platform managed \
          --service-account ${{ secrets.SERVICE_ACCOUNT }} \
          --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_REGION=$REGION,ENV=production \
          --set-secrets SAFETYCULTURE_API_TOKEN=safetyculture-api-token:latest \
          --cpu 2 \
          --memory 4Gi \
          --timeout 300 \
          --min-instances 2 \
          --max-instances 10 \
          --cpu-boost \
          --no-allow-unauthenticated
    
    - name: Run smoke tests
      run: |
        SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
        curl -f ${SERVICE_URL}/health || exit 1
```

### Cloud Build Configuration

Create [`cloudbuild.yaml`](cloudbuild.yaml):

```yaml
steps:
  # Run tests
  - name: 'python:3.11'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r safetyculture_agent/requirements.txt
        pip install pytest
        pytest tests/ -v

  # Build backend
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-f'
      - 'Dockerfile.backend'
      - '-t'
      - 'gcr.io/$PROJECT_ID/safetyculture-agent:$SHORT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/safetyculture-agent:latest'
      - '.'

  # Build frontend
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-f'
      - 'Dockerfile.frontend'
      - '-t'
      - 'gcr.io/$PROJECT_ID/safetyculture-gui:$SHORT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/safetyculture-gui:latest'
      - '.'

  # Deploy backend
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'safetyculture-agent'
      - '--image'
      - 'gcr.io/$PROJECT_ID/safetyculture-agent:$SHORT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'

images:
  - 'gcr.io/$PROJECT_ID/safetyculture-agent:$SHORT_SHA'
  - 'gcr.io/$PROJECT_ID/safetyculture-agent:latest'
  - 'gcr.io/$PROJECT_ID/safetyculture-gui:$SHORT_SHA'
  - 'gcr.io/$PROJECT_ID/safetyculture-gui:latest'

options:
  machineType: 'N1_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY
```

Trigger builds:

```bash
# Manual trigger
gcloud builds submit --config=cloudbuild.yaml

# Automated trigger on git push
gcloud builds triggers create github \
  --repo-name=adk-python \
  --repo-owner=yourusername \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

---

## Monitoring & Observability

### Cloud Monitoring Dashboard

Create [`monitoring/dashboard.json`](monitoring/dashboard.json):

```json
{
  "displayName": "SafetyCulture Agent Dashboard",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Count",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"safetyculture-agent\" AND metric.type=\"run.googleapis.com/request_count\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        }
      },
      {
        "xPos": 6,
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Response Latency (p95)",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"safetyculture-agent\" AND metric.type=\"run.googleapis.com/request_latencies\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_DELTA",
                    "crossSeriesReducer": "REDUCE_PERCENTILE_95"
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}
```

Import dashboard:

```bash
gcloud monitoring dashboards create --config-from-file=monitoring/dashboard.json
```

### OpenTelemetry Integration

Add to agent code:

```python
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configure tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Export to Cloud Trace
cloud_trace_exporter = CloudTraceSpanExporter()
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)

# Use in code
@tracer.start_as_current_span("create_inspection")
def create_inspection(asset_id: str, template_id: str):
    span = trace.get_current_span()
    span.set_attribute("asset.id", asset_id)
    span.set_attribute("template.id", template_id)
    
    # Your logic here
    pass
```

### Health Check Endpoints

Add to [`safetyculture_agent/health.py`](safetyculture_agent/health.py):

```python
from fastapi import APIRouter, Response
from google.cloud import aiplatform
import aiosqlite

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "safetyculture-agent"}

@router.get("/health/ready")
async def readiness_check():
    """Readiness check - verifies dependencies."""
    checks = {
        "database": await check_database(),
        "vertex_ai": await check_vertex_ai(),
        "safetyculture_api": await check_safetyculture_api()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return Response(
        content=json.dumps({
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks
        }),
        status_code=status_code,
        media_type="application/json"
    )

@router.get("/health/live")
async def liveness_check():
    """Liveness check - verifies process is responsive."""
    return {"status": "alive"}

async def check_database():
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("SELECT 1")
        return True
    except Exception:
        return False

async def check_vertex_ai():
    try:
        # Simple check that credentials work
        aiplatform.init(project=PROJECT_ID, location=REGION)
        return True
    except Exception:
        return False

async def check_safetyculture_api():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{SC_API_URL}/assets",
                headers={"Authorization": f"Bearer {SC_TOKEN}"},
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                return resp.status == 200
    except Exception:
        return False
```

---

## Security Considerations

### 1. API Authentication

Implement OAuth2 for GUI access:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

@app.post("/agent/invoke")
async def invoke_agent(
    request: InvokeRequest,
    user: dict = Depends(verify_token)
):
    # Protected endpoint
    pass
```

### 2. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/agent/invoke")
@limiter.limit("10/minute")
async def invoke_agent(request: Request):
    pass
```

### 3. Input Validation

```python
from pydantic import BaseModel, validator, constr

class InvokeRequest(BaseModel):
    session_id: constr(regex=r'^[a-zA-Z0-9_-]{1,100}$')
    message: constr(min_length=1, max_length=10000)
    
    @validator('message')
    def sanitize_message(cls, v):
        # Remove potential injection attacks
        dangerous_patterns = ['<script', 'javascript:', 'onerror=']
        for pattern in dangerous_patterns:
            if pattern.lower() in v.lower():
                raise ValueError('Invalid message content')
        return v
```

### 4. Network Security

```bash
# Enable Cloud Armor
gcloud compute security-policies create agent-security-policy

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
  --security-policy agent-security-policy \
  --expression "true" \
  --action "rate-based-ban" \
  --rate-limit-threshold-count 100 \
  --rate-limit-threshold-interval-sec 60 \
  --ban-duration-sec 600

# Attach to backend service
gcloud compute backend-services update safetyculture-agent-backend \
  --security-policy agent-security-policy \
  --global
```

---

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

**Symptom:** `403 Forbidden` or `401 Unauthorized`

**Solutions:**
```bash
# Verify service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:${SERVICE_ACCOUNT}"

# Check secret access
gcloud secrets get-iam-policy safetyculture-api-token

# Test authentication
gcloud auth application-default print-access-token

# Verify Workload Identity (GKE)
kubectl describe serviceaccount agent-sa -n safetyculture
```

#### 2. Model Invocation Errors

**Symptom:** `Model not found` or timeout errors

**Solutions:**
```bash
# Verify Vertex AI API is enabled
gcloud services list --enabled | grep aiplatform

# Check model availability
gcloud ai models list --region=${REGION}

# Test model access
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/publishers/google/models/gemini-pro:predict" \
  -d '{"instances":[{"content":"Hello"}]}'
```

#### 3. Database Corruption

**Symptom:** SQLite database errors

**Solutions:**
```bash
# Check database integrity
sqlite3 asset_tracker.db "PRAGMA integrity_check;"

# Restore from backup
gsutil cp gs://${PROJECT_ID}-backups/database/latest/asset_tracker.db ./data/

# Rebuild database (last resort)
rm asset_tracker.db
# Restart agent to recreate
```

#### 4. Memory Issues

**Symptom:** OOM kills or high memory usage

**Solutions:**
```bash
# Check memory usage
kubectl top pods -n safetyculture

# Increase memory limits
kubectl set resources deployment/safetyculture-agent \
  -n safetyculture \
  --limits=memory=8Gi

# Enable memory profiling
export PYTHONMALLOC=malloc
python -m memory_profiler safetyculture_agent/agent.py
```

### Debug Mode

Enable verbose logging:

```bash
# Environment variable
export ADK_LOG_LEVEL=DEBUG
export LITELLM_LOG=DEBUG

# Python code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Support Resources

- **ADK Documentation:** https://github.com/google/adk-python
- **SafetyCulture API:** https://developer.safetyculture.com
- **Google Cloud Support:** https://cloud.google.com/support
- **GitHub Issues:** https://github.com/yourusername/adk-python/issues

---

## Cost Optimization

### Estimated Monthly Costs

**Small Deployment (Development):**
- Cloud Run: ~$10-30/month (min instances = 0)
- Vertex AI: ~$50-100/month (Gemini Flash)
- Storage: ~$5/month
- **Total: ~$65-135/month**

**Medium Deployment (Production):**
- Cloud Run: ~$100-200/month (min instances = 2)
- Vertex AI: ~$200-500/month
- Storage: ~$20/month
- Load Balancing: ~$20/month
- **Total: ~$340-740/month**

**Large Deployment (Enterprise):**
- GKE Cluster: ~$200-500/month
- Vertex AI: ~$1000-3000/month
- Storage: ~$100/month
- Networking: ~$100/month
- **Total: ~$1400-3700/month**

### Cost Reduction Strategies

```bash
# Use committed use discounts
gcloud compute commitments create \
  --resources=vcpu=8,memory=32GB \
  --plan=twelve-month

# Use preemptible nodes (GKE)
gcloud container node-pools create preemptible-pool \
  --cluster=safetyculture-cluster \
  --preemptible \
  --num-nodes=2

# Enable autoscaling to zero (development)
gcloud run services update safetyculture-agent \
  --min-instances=0 \
  --max-instances=3

# Use cheaper regions
# us-central1, us-east1 are typically cheapest

# Monitor costs
gcloud billing budgets create \
  --billing-account=${BILLING_ACCOUNT} \
  --display-name="SafetyCulture Agent Budget" \
  --budget-amount=500USD \
  --threshold-rules=percent=50,percent=90,percent=100
```

---

## Disaster Recovery

### Backup Strategy

```bash
# Automated daily backups
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
BACKUP_BUCKET="gs://${PROJECT_ID}-backups"

# Backup database
gsutil cp /app/data/asset_tracker.db ${BACKUP_BUCKET}/database/${DATE}/

# Backup memory
gsutil -m rsync -r /app/.adk/memory ${BACKUP_BUCKET}/memory/${DATE}/

# Backup configuration
gsutil cp /app/.env.production ${BACKUP_BUCKET}/config/${DATE}/

# Retention: 30 days
gsutil -m rm -r ${BACKUP_BUCKET}/database/$(date -d '30 days ago' +%Y%m%d)/
```

### Recovery Procedures

**Scenario 1: Service Failure**
```bash
# Rollback to previous version
gcloud run services update-traffic safetyculture-agent \
  --to-revisions=PREVIOUS_REVISION=100

# Or deploy known good version
gcloud run deploy safetyculture-agent \
  --image gcr.io/${PROJECT_ID}/safetyculture-agent:v1.0.0
```

**Scenario 2: Database Corruption**
```bash
# Stop service
gcloud run services update safetyculture-agent --min-instances=0

# Restore from backup
gsutil cp gs://${PROJECT_ID}-backups/database/latest/asset_tracker.db /app/data/

# Restart service
gcloud run services update safetyculture-agent --min-instances=2
```

**Scenario 3: Regional Failure**
```bash
# Deploy to backup region
export BACKUP_REGION=us-east1

gcloud run deploy safetyculture-agent \
  --image gcr.io/${PROJECT_ID}/safetyculture-agent:latest \
  --region ${BACKUP_REGION}

# Update DNS to point to backup region
```

### Testing Recovery

```bash
# Monthly DR drill
# 1. Create test backup
./backup.sh test

# 2. Deploy to staging with test backup
gcloud run deploy safetyculture-agent-dr-test \
  --image gcr.io/${PROJECT_ID}/safetyculture-agent:latest \
  --region us-east1

# 3. Restore test backup
# 4. Verify functionality
# 5. Document results
```

---

## Appendix

### Environment Variables Reference

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `SAFETYCULTURE_API_TOKEN` | Yes | SafetyCulture API authentication token | - |
| `GOOGLE_CLOUD_PROJECT` | Yes | GCP project ID | - |
| `GOOGLE_CLOUD_REGION` | Yes | GCP region for Vertex AI | `us-central1` |
| `GOOGLE_APPLICATION_CREDENTIALS` | No | Path to service account key | - |
| `MODEL_PROVIDER` | No | AI model provider | `gemini` |
| `ADK_LOG_LEVEL` | No | Logging level | `INFO` |
| `ADK_MAX_RETRIES` | No | Maximum retry attempts | `3` |
| `ADK_TIMEOUT` | No | Request timeout in seconds | `300` |

### Port Reference

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| Backend Agent | 8000 | HTTP | FastAPI server |
| Frontend GUI | 80/443 | HTTP/HTTPS | Nginx server |
| Metrics | 9090 | HTTP | Prometheus metrics |
| Health Check | 8000 | HTTP | `/health` endpoint |

### GCP Services Required

- **Vertex AI** - Model inference
- **Secret Manager** - Credential storage
- **Cloud Run** - Container hosting
- **Cloud Build** - CI/CD
- **Cloud Logging** - Log aggregation
- **Cloud Monitoring** - Metrics and alerts
- **Container Registry** - Image storage

---

## Summary

This deployment guide covered:

✅ **8 deployment strategies** from local development to enterprise GKE  
✅ **15+ configuration examples** with production-ready settings  
✅ **Complete CI/CD pipelines** for GitHub Actions and Cloud Build  
✅ **Comprehensive security** including IAM, secrets, and network policies  
✅ **Monitoring & observability** with Cloud Monitoring and OpenTelemetry  
✅ **Cost optimization** strategies and budget alerts  
✅ **Disaster recovery** procedures and backup automation  
✅ **Troubleshooting guide** for common production issues

**Key Security Highlights:**
- ⚠️ Never hard-code credentials
- ✅ Use Secret Manager for all sensitive data
- ✅ Implement least-privilege IAM roles
- ✅ Enable TLS/SSL everywhere
- ✅ Use Workload Identity for GKE
- ✅ Implement rate limiting and authentication

**Next Steps:**
1. Choose deployment strategy based on your requirements
2. Set up GCP project and enable required APIs
3. Configure Secret Manager with credentials
4. Deploy to staging environment
5. Run smoke tests and monitoring validation
6. Deploy to production with appropriate scaling
7. Set up alerts and monitoring dashboards
8. Schedule regular backups and DR drills

For questions or issues, refer to the troubleshooting section or open a GitHub issue.

---

**Document Version:** 1.0.0  
**Last Updated:** 2025-01-30  
**Maintained By:** DevOps Team  
**License:** Apache 2.0