# Architecture Guide

This document provides an in-depth look at the Python Super Heroes system architecture, design patterns, and technical decisions.

## System Overview

Python Super Heroes is a microservices-based application demonstrating modern distributed system patterns including:

- **Polyglot Persistence**: Multiple database technologies for different data models
- **Service Orchestration**: Composition pattern for complex business operations
- **Asynchronous Communication**: Non-blocking HTTP calls using httpx
- **Container Orchestration**: Docker Compose for local development
- **Performance Testing**: Integrated load testing with k6

## Architecture Diagram

``````
┌─────────────────────────────────────────────────────────────┐
│                      External Clients                        │
│                   (Browser, k6, curl)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Fights Service (8004)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI Application (Orchestrator Layer)            │   │
│  │  - Fetches random fighters (hero/villain)            │   │
│  │  - Fetches random location                           │   │
│  │  - Executes fight logic (level comparison)           │   │
│  │  - Stores results (MongoDB)                          │   │
│  └──────────────────────────────────────────────────────┘   │
└──┬────────────────┬────────────────┬────────────────────┬───┘
   │                │                │                    │
   │ httpx          │ httpx          │ httpx              │ mongo
   ▼                ▼                ▼                    ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐  ┌────────────────┐
│ Heroes   │  │ Villains │  │  Locations   │  │  Fights DB     │
│ Service  │  │ Service  │  │  Service     │  │  (MongoDB 7.0) │
│  :8001   │  │  :8002   │  │   :8003      │  │  :27017        │
│          │  │          │  │              │  │                │
│ FastAPI  │  │ FastAPI  │  │  FastAPI     │  │ - fight_id     │
│ CRUD     │  │ CRUD     │  │  CRUD        │  │ - hero         │
│          │  │          │  │              │  │ - villain      │
│          │  │          │  │              │  │ - location     │
│          │  │          │  │              │  │ - winner       │
│          │  │          │  │              │  │ - timestamp    │
└────┬─────┘  └────┬─────┘  └──────┬───────┘  └────────────────┘
     │             │               │
     │ asyncpg     │ asyncpg       │ aiomysql
     ▼             ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│Heroes DB │  │Villains  │  │ Locations DB │
│PostgreSQL│  │   DB     │  │   MariaDB    │
│  :5432   │  │PostgreSQL│  │    :3306     │
│          │  │  :5433   │  │              │
│ - id     │  │          │  │ - id         │
│ - name   │  │ - id     │  │ - name       │
│ - other  │  │ - name   │  │ - description│
│ - level  │  │ - other  │  │ - picture    │
│ - picture│  │ - level  │  │ - type       │
│ - powers │  │ - picture│  │              │
│          │  │ - powers │  │              │
└──────────┘  └──────────┘  └──────────────┘
``````

## Design Patterns

### 1. Microservices Pattern

Each service is independently deployable and manages its own data:

- **Heroes Service**: Manages superhero data
- **Villains Service**: Manages villain data
- **Locations Service**: Manages location data
- **Fights Service**: Orchestrates fights and stores results

**Benefits**:
- Independent scaling
- Technology diversity
- Fault isolation
- Team autonomy

**Trade-offs**:
- Increased complexity
- Network latency
- Distributed transactions challenges

### 2. API Composition Pattern

The Fights service implements the **API Composition** pattern, aggregating data from multiple services:

``````python
async def execute_fight():
    # Fetch from multiple services
    hero = await get_hero()
    villain = await get_villain()
    location = await get_location()
    
    # Execute business logic
    winner = determine_winner(hero, villain)
    
    # Store result
    return fight_result
``````

**Benefits**:
- Simple to implement
- Real-time data aggregation
- No data duplication

**Trade-offs**:
- Multiple network calls increase latency
- Reduced availability (depends on all services)
- No distributed transactions

### 3. Database per Service Pattern

Each service has its own database with appropriate technology:

- **PostgreSQL** for Heroes/Villains: Relational data with ACID guarantees
- **MariaDB** for Locations: Geographic/structured data
- **MongoDB** for Fights: Document-oriented fight records

**Benefits**:
- Service autonomy
- Optimized data models
- Independent scaling

**Trade-offs**:
- No joins across services
- Distributed data management
- Eventual consistency

### 4. Strangler Fig Pattern (Future)

The architecture allows gradual migration or replacement of services without system-wide changes.

## Communication Patterns

### Synchronous HTTP/REST

All inter-service communication uses REST over HTTP:

``````python
async def get_hero():
    response = await client.get("http://heroes:8000/api/heroes/random_hero")
    return response.json()
``````

**Characteristics**:
- Request-response model
- Blocking (with async/await)
- Simple error handling
- Direct dependencies

### Asynchronous I/O

All services use FastAPI with `async/await` for non-blocking I/O:

``````python
@app.get("/api/heroes")
async def list_heroes():
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM heroes")
    return rows
``````

**Benefits**:
- High concurrency
- Efficient resource usage
- Better throughput

## Data Models

### Heroes/Villains Schema

``````sql
CREATE TABLE heroes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    other_name VARCHAR(100),
    level INTEGER NOT NULL,
    picture TEXT,
    powers TEXT
);
``````

### Locations Schema

``````sql
CREATE TABLE locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    picture TEXT,
    type ENUM('CITY', 'PLANET', 'PLACE', 'ISLAND', 'COUNTRY', 'MOON')
);
``````

### Fights Schema (MongoDB)

``````json
{
  "_id": ObjectId,
  "fightId": "uuid",
  "hero": {
    "id": 1,
    "name": "Superman",
    "level": 95
  },
  "villain": {
    "id": 2,
    "name": "Lex Luthor",
    "level": 85
  },
  "location": {
    "id": 1,
    "name": "Metropolis"
  },
  "winner": "hero",
  "fightDate": ISODate("2026-02-13T13:38:00Z")
}
``````

## Resilience Patterns

### Health Checks

All databases have health checks configured:

``````yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U superman"]
  interval: 10s
  timeout: 5s
  retries: 20
``````

### Connection Pooling

Services use connection pools for efficient resource management:

``````python
pool = await asyncpg.create_pool(
    dsn=DATABASE_URL,
    min_size=10,
    max_size=50
)
``````

### Retry Logic

Services implement startup retry logic:

``````python
import time

max_retries = 20
for attempt in range(max_retries):
    try:
        pool = await create_pool()
        break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(10)
        else:
            raise
``````

### Error Handling

Services use FastAPI exception handling:

``````python
try:
    response = await client.get(url)
    response.raise_for_status()
except httpx.RequestError as exc:
    raise HTTPException(status_code=502, detail=f"Error: {exc}")
``````

## Performance Considerations

### Async/Await

Non-blocking I/O allows handling thousands of concurrent requests:

- Database queries: `await conn.fetch()`
- HTTP calls: `await client.get()`
- No thread blocking

### Connection Pooling

Reusing database connections reduces overhead:

- Minimum pool size: 10
- Maximum pool size: 50
- Automatic connection management

### Horizontal Scaling

Services can scale independently:

``````yaml
services:
  heroes:
    deploy:
      replicas: 3
``````

## Security Considerations

### Current State (Development)

- No authentication/authorization
- No CORS restrictions
- No rate limiting
- No input validation beyond FastAPI schemas

### Production Recommendations

1. **Authentication**: Implement JWT or OAuth2
2. **Authorization**: Role-based access control (RBAC)
3. **CORS**: Configure allowed origins
4. **Rate Limiting**: Implement per-IP limits
5. **Input Validation**: Strengthen validation rules
6. **Database Security**: Use secrets management
7. **Network Security**: Service mesh (Istio) or API gateway

## Deployment Architecture

### Development (Current)

Docker Compose orchestrates all services:

``````
docker-compose up -d
``````

### Production (Recommended)

**Kubernetes Deployment**:

``````yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: heroes-service
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
        image: heroes:latest
        ports:
        - containerPort: 8000
``````

**Service Mesh**: Istio for traffic management, security, observability

**Managed Databases**: Use cloud-managed PostgreSQL, MongoDB

## Observability

### Current State

Basic logging to stdout:

``````python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting service")
``````

### Recommended Improvements

1. **Distributed Tracing**: OpenTelemetry + Jaeger
2. **Metrics**: Prometheus + Grafana
3. **Centralized Logging**: ELK Stack or Loki
4. **APM**: DataDog, New Relic, or Elastic APM

## Future Enhancements

### Event-Driven Architecture

Replace synchronous calls with message queues:

``````
Fights Service → [RabbitMQ/Kafka] → Heroes/Villains/Locations
``````

### CQRS Pattern

Separate read and write models for better performance:

- **Write Model**: Transactional operations
- **Read Model**: Optimized queries, caching

### Saga Pattern

Implement distributed transactions for complex operations:

``````
Start Fight → Reserve Hero → Reserve Villain → Reserve Location → Execute
``````

### API Gateway

Add Kong, Traefik, or AWS API Gateway for:

- Authentication
- Rate limiting
- Request routing
- Load balancing

## Technology Choices

### Why FastAPI?

- **Performance**: Comparable to Node.js and Go
- **Async Support**: Native async/await
- **Type Safety**: Pydantic models
- **Documentation**: Auto-generated OpenAPI docs
- **Developer Experience**: Minimal boilerplate

### Why Different Databases?

Demonstrates **polyglot persistence**:

- **PostgreSQL**: ACID transactions for critical data
- **MariaDB**: Alternative relational database
- **MongoDB**: Flexible schema for event logs

### Why k6?

- **Performance**: Written in Go, low overhead
- **JavaScript DSL**: Familiar syntax
- **Thresholds**: Built-in SLA validation
- **Scalability**: Cloud execution support

## Conclusion

This architecture balances simplicity with modern microservices patterns, providing a foundation for scalable, maintainable systems while demonstrating key distributed system concepts.
