# Deployment Guide

Production deployment guide for Python Super Heroes.

## Deployment Options

### Docker Compose (Simple)

Best for: Development, testing, small-scale deployments

**Pros**: Simple, portable, minimal setup
**Cons**: Single-host limitation, manual scaling

### Kubernetes

Best for: Production, high availability, auto-scaling

**Pros**: Orchestration, scaling, self-healing
**Cons**: Complexity, infrastructure requirements

### Cloud Platforms

Best for: Managed infrastructure, rapid deployment

Options:
- **AWS ECS/Fargate**: Container orchestration
- **Google Cloud Run**: Serverless containers
- **Azure Container Apps**: Managed containers

## Docker Compose Deployment

### Production Configuration

Create `compose.prod.yml`:

``````yaml
services:
  heroes:
    image: ghcr.io/flyaruu/python-super-heroes/heroes:latest
    environment:
      DATABASE_URL: ${HEROES_DB_URL}
    restart: unless-stopped
    
  # Add health checks, resource limits, etc.
``````

### Security Hardening

1. **Use Secrets**:
   ``````yaml
   services:
     heroes-db:
       environment:
         POSTGRES_PASSWORD_FILE: /run/secrets/db_password
       secrets:
         - db_password
   
   secrets:
     db_password:
       external: true
   ``````

2. **Non-root Users**:
   ``````dockerfile
   FROM python:3.11-slim
   RUN useradd -m appuser
   USER appuser
   ``````

3. **Read-only Filesystems**:
   ``````yaml
   services:
     heroes:
       read_only: true
       tmpfs:
         - /tmp
   ``````

### Environment Variables

Create `.env.prod`:

``````env
# Database URLs
HEROES_DB_URL=postgres://user:pass@heroes-db:5432/heroes_database
VILLAINS_DB_URL=postgres://user:pass@villains-db:5432/villains_database
LOCATIONS_DB_URL=mysql://user:pass@locations-db:3306/locations_database

# Service URLs
HEROES_SERVICE_URL=http://heroes:8000
VILLAINS_SERVICE_URL=http://villains:8000
LOCATIONS_SERVICE_URL=http://locations:8000
``````

### Deployment Steps

``````bash
# Build images
docker compose -f compose.prod.yml build

# Pull latest images
docker compose -f compose.prod.yml pull

# Start services
docker compose -f compose.prod.yml up -d

# Check health
docker compose -f compose.prod.yml ps
``````

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (GKE, EKS, AKS, or self-hosted)
- kubectl configured
- Helm (optional)

### Architecture

``````
┌─────────────────────────────────────────┐
│             Ingress/Load Balancer        │
└─────────────┬───────────────────────────┘
              │
      ┌───────┴────────┐
      │   Kubernetes   │
      │    Cluster     │
      └───────┬────────┘
              │
    ┌─────────┼─────────┬─────────┐
    │         │         │         │
┌───▼────┬────▼───┬────▼───┬────▼────┐
│ Heroes │Villains│Location│ Fights  │
│  Pods  │  Pods  │  Pods  │  Pods   │
└───┬────┴────┬───┴────┬───┴────┬────┘
    │         │        │        │
┌───▼────┬────▼───┬────▼───┬────▼────┐
│Heroes  │Villains│Location│ Fights  │
│  DB    │   DB   │   DB   │   DB    │
└────────┴────────┴────────┴─────────┘
``````

### Kubernetes Manifests

**Deployment** (`k8s/heroes-deployment.yaml`):

``````yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: heroes
spec:
  replicas: 3
  selector:
    matchLabels:
      app: heroes
  template:
    metadata:
      labels:
        app: heroes
    spec:
      containers:
      - name: heroes
        image: ghcr.io/flyaruu/python-super-heroes/heroes:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: heroes-db-secret
              key: url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/heroes
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/heroes
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
``````

**Service** (`k8s/heroes-service.yaml`):

``````yaml
apiVersion: v1
kind: Service
metadata:
  name: heroes
spec:
  selector:
    app: heroes
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
``````

**Secret** (`k8s/heroes-secret.yaml`):

``````yaml
apiVersion: v1
kind: Secret
metadata:
  name: heroes-db-secret
type: Opaque
stringData:
  url: postgres://superman:superman@heroes-db:5432/heroes_database
``````

### Helm Chart (Optional)

Create `helm/super-heroes/values.yaml`:

``````yaml
heroes:
  replicaCount: 3
  image:
    repository: ghcr.io/flyaruu/python-super-heroes/heroes
    tag: latest
  database:
    host: heroes-db
    port: 5432
    name: heroes_database
``````

Deploy with Helm:

``````bash
helm install super-heroes ./helm/super-heroes
``````

### Database Management

Use StatefulSets for databases or managed services:

``````yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: heroes-db
spec:
  serviceName: heroes-db
  replicas: 1
  selector:
    matchLabels:
      app: heroes-db
  template:
    metadata:
      labels:
        app: heroes-db
    spec:
      containers:
      - name: postgres
        image: postgres:16
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
``````

Or use managed databases:
- **AWS RDS** (PostgreSQL)
- **Google Cloud SQL**
- **Azure Database for PostgreSQL**
- **MongoDB Atlas**

## Cloud Platform Deployment

### AWS ECS/Fargate

1. **Create ECR repositories**:
   ``````bash
   aws ecr create-repository --repository-name super-heroes/heroes
   ``````

2. **Push images**:
   ``````bash
   docker tag heroes:latest ${AWS_ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/super-heroes/heroes:latest
   docker push ${AWS_ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/super-heroes/heroes:latest
   ``````

3. **Create task definitions** and **ECS services**

### Google Cloud Run

``````bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/${PROJECT_ID}/heroes services/heroes

# Deploy
gcloud run deploy heroes \
  --image gcr.io/${PROJECT_ID}/heroes \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=${DB_URL}
``````

### Azure Container Apps

``````bash
# Create container app
az containerapp create \
  --name heroes \
  --resource-group super-heroes \
  --image ghcr.io/flyaruu/python-super-heroes/heroes:latest \
  --target-port 8000 \
  --env-vars DATABASE_URL=${DB_URL} \
  --ingress external
``````

## CI/CD Pipeline

### GitHub Actions

`.github/workflows/deploy.yml`:

``````yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker compose build
      
      - name: Push to registry
        run: |
          echo ${{ secrets.GHCR_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          docker compose push
      
      - name: Deploy to production
        run: |
          # SSH to server and pull latest images
          ssh deploy@server 'cd /app && docker compose pull && docker compose up -d'
``````

## Monitoring & Logging

### Prometheus Metrics

Add metrics endpoint to services:

``````python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.route('/metrics')
async def metrics(request):
    return Response(generate_latest(), media_type='text/plain')
``````

### Logging

Use structured logging with JSON output:

``````python
import json
import logging

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            'timestamp': record.created,
            'level': record.levelname,
            'message': record.getMessage(),
            'service': 'heroes'
        })

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.root.addHandler(handler)
``````

Ship logs to:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Grafana Loki**
- **Cloud logging** (CloudWatch, Stackdriver, Azure Monitor)

## Backup & Recovery

### Database Backups

**PostgreSQL**:
``````bash
pg_dump -h heroes-db -U superman heroes_database > backup.sql
``````

**MongoDB**:
``````bash
mongodump --uri="mongodb://super:super@fights-db/fights"
``````

**MariaDB**:
``````bash
mysqldump -h locations-db -u locations -p locations_database > backup.sql
``````

### Automated Backups

Schedule with cron or Kubernetes CronJob:

``````yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:16
            command: ["/bin/sh"]
            args: ["-c", "pg_dump ... | aws s3 cp - s3://backups/$(date +%Y%m%d).sql"]
``````

## Performance Tuning

### Connection Pooling

Tune based on expected load:

``````python
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=10,
    max_size=100,
    max_inactive_connection_lifetime=300
)
``````

### Resource Limits

Set appropriate limits:

``````yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
``````

### Horizontal Pod Autoscaling

``````yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: heroes
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: heroes
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
``````

## Security Checklist

- [ ] Use secrets management (not environment variables)
- [ ] Enable TLS/SSL for all services
- [ ] Implement authentication and authorization
- [ ] Use network policies to restrict traffic
- [ ] Run containers as non-root users
- [ ] Scan images for vulnerabilities
- [ ] Enable audit logging
- [ ] Implement rate limiting
- [ ] Use read-only filesystems where possible
- [ ] Regularly update dependencies

## Troubleshooting

### Service Not Starting

Check logs:
``````bash
kubectl logs deployment/heroes
docker compose logs heroes
``````

### Database Connection Issues

Verify connectivity:
``````bash
kubectl exec -it heroes-pod -- ping heroes-db
docker compose exec heroes ping heroes-db
``````

### High Latency

Check metrics and resource usage:
``````bash
kubectl top pods
docker stats
``````

## Rollback Strategy

### Kubernetes

``````bash
# Rollback to previous version
kubectl rollout undo deployment/heroes

# Rollback to specific revision
kubectl rollout undo deployment/heroes --to-revision=2
``````

### Docker Compose

``````bash
# Keep previous version tagged
docker tag heroes:latest heroes:v1.0.0

# Rollback by changing image tag
docker compose down
docker compose up -d
``````

## Further Resources

- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [12-Factor App](https://12factor.net/)
