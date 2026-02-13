# Architecture Overview

## System Design

Python Super Heroes implements a microservices architecture pattern where each service is independently deployable and manages its own data store.

## Architectural Principles

### Separation of Concerns

Each microservice has a single, well-defined responsibility:

- **Heroes Service**: Hero entity management
- **Villains Service**: Villain entity management
- **Locations Service**: Battle location management
- **Fights Service**: Battle orchestration and coordination

### Database per Service

Each microservice uses a database technology appropriate for its domain:

- **Heroes/Villains**: PostgreSQL (relational data with strong consistency)
- **Locations**: MariaDB (alternative relational database demonstration)
- **Fights**: MongoDB (flexible schema for fight records)

This pattern ensures:
- Service independence
- Technology flexibility
- Data isolation
- Scalability options

## Service Communication

### Synchronous HTTP/REST

The Fights service coordinates with other services via HTTP:

``````python
# Example: Fetching a random hero
response = await client.get("http://heroes:8000/api/heroes/random_hero")
hero = response.json()
``````

Services communicate using:
- Docker internal networking
- Service discovery via Docker DNS
- RESTful JSON APIs

## Data Flow

### Fight Execution Sequence

1. Client requests a fight via `GET /api/fights/execute_fight`
2. Fights service fetches random hero from Heroes service
3. Fights service fetches random villain from Villains service
4. Fights service fetches random location from Locations service
5. Fight logic determines winner based on level comparison
6. Fights service returns complete fight result

``````
┌─────────┐
│ Client  │
└────┬────┘
     │
     ▼
┌─────────────┐      ┌─────────────┐
│   Fights    │─────▶│   Heroes    │
│   Service   │      │   Service   │
│  (Port 8004)│      │  (Port 8001)│
└──────┬──────┘      └─────────────┘
       │
       │             ┌─────────────┐
       ├────────────▶│  Villains   │
       │             │   Service   │
       │             │  (Port 8002)│
       │             └─────────────┘
       │
       │             ┌─────────────┐
       └────────────▶│  Locations  │
                     │   Service   │
                     │  (Port 8003)│
                     └─────────────┘
``````

## Connection Pooling

All services implement database connection pooling for performance:

### PostgreSQL (Heroes/Villains)
``````python
app.state.pool = await asyncpg.create_pool(
    DATABASE_URL, 
    min_size=10, 
    max_size=50
)
``````

### MariaDB (Locations)
``````python
pool = await aiomysql.create_pool(
    host=host,
    port=port,
    user=user,
    password=password,
    db=database,
    minsize=1,
    maxsize=10
)
``````

## Resilience Patterns

### Retry Logic

Services implement startup retry logic to handle database initialization delays:

``````python
RETRY_TIMEOUT = 10  # seconds
RETRY_INTERVAL = 0.5  # seconds between attempts

while time.monotonic() < deadline:
    try:
        pool = await connect_to_database()
        return
    except Exception as e:
        await asyncio.sleep(RETRY_INTERVAL)
``````

### Health Checks

Databases include health checks in Docker Compose:

``````yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U superman"]
  interval: 10s
  timeout: 5s
  retries: 20
``````

### Error Handling

Services return appropriate HTTP status codes:
- `404` - Resource not found
- `502` - External service connection error

## Scalability Considerations

### Horizontal Scaling

Services can be scaled independently:
``````bash
docker compose up -d --scale heroes=3
``````

### Load Balancing

In production, add a load balancer (nginx, HAProxy) in front of services.

### Database Scaling

- **PostgreSQL/MariaDB**: Read replicas, connection pooling
- **MongoDB**: Replica sets, sharding

## Deployment

### Container Orchestration

Current: Docker Compose (development/testing)

Production options:
- Kubernetes with Helm charts
- Docker Swarm
- Cloud-native services (AWS ECS, Google Cloud Run)

### Configuration Management

Environment variables configure database connections:
- `DATABASE_URL` - PostgreSQL connection string
- `MYSQL_URL` - MariaDB connection string
- MongoDB connection configured in Fights service

## Monitoring & Observability

### Logging

Services use structured logging:
``````python
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
``````

### Performance Testing

k6 load testing suite measures:
- Request throughput (RPS)
- Response latency
- Error rates
- System behavior under load

## Security Considerations

### Current State (Development)

- Hardcoded credentials in compose.yml
- No authentication/authorization
- Internal network only

### Production Recommendations

- Use secrets management (Docker secrets, HashiCorp Vault)
- Implement API authentication (JWT, OAuth 2.0)
- Enable TLS/SSL for all communications
- Network policies and service mesh (Istio, Linkerd)
- Rate limiting and API gateways
