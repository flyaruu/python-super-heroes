# Architecture

## Overview

Python Super Heroes implements a microservices architecture pattern where each service is independently deployable, scalable, and maintains its own database. This design demonstrates polyglot persistence, service orchestration, and asynchronous communication patterns.

## Design Principles

### 1. Single Responsibility
Each service handles one domain:
- **Heroes Service**: Hero character management
- **Villains Service**: Villain character management  
- **Locations Service**: Fight location management
- **Fights Service**: Battle orchestration and result calculation

### 2. Polyglot Persistence
Different databases chosen based on data characteristics:

| Service | Database | Rationale |
|---------|----------|-----------|
| Heroes | PostgreSQL | Relational data with ACID guarantees |
| Villains | PostgreSQL | Consistent schema, joins with heroes |
| Locations | MariaDB | Geographic data, MySQL compatibility |
| Fights | MongoDB | Flexible schema for fight results |

### 3. Asynchronous Communication
All services use async/await patterns for non-blocking I/O:
- Database connection pools (10-50 connections)
- Async HTTP clients (httpx)
- Event loop optimization

## Service Details

### Heroes Service

**Technology**: Starlette + asyncpg  
**Database**: PostgreSQL  
**Port**: 8001

**Schema:**
``````sql
CREATE TABLE Hero (
  id SERIAL PRIMARY KEY,
  level INTEGER NOT NULL,
  name VARCHAR(50) NOT NULL,
  otherName VARCHAR(255),
  picture VARCHAR(255),
  powers TEXT
);
``````

**Key Features:**
- Connection retry logic (10s timeout)
- Database connection pooling
- Field name transformation (snake_case ↔ camelCase)

### Villains Service

**Technology**: Starlette + asyncpg  
**Database**: PostgreSQL (separate instance)  
**Port**: 8002

**Schema:**
``````sql
CREATE TABLE Villain (
  id SERIAL PRIMARY KEY,
  level INTEGER NOT NULL,
  name VARCHAR(50) NOT NULL,
  otherName VARCHAR(255),
  picture VARCHAR(255),
  powers TEXT
);
``````

**Design Notes:**
- Mirror of Heroes service for symmetry
- Separate database prevents cross-contamination
- Identical API contract for consistency

### Locations Service

**Technology**: Starlette + aiomysql  
**Database**: MariaDB  
**Port**: 8003

**Schema:**
``````sql
CREATE TABLE Location (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  picture VARCHAR(255)
);
``````

**Key Features:**
- URL parsing for connection string
- Enhanced logging for debugging
- DictCursor for JSON serialization

### Fights Service

**Technology**: FastAPI + httpx  
**Database**: MongoDB  
**Port**: 8004

**Responsibilities:**
1. Fetch random hero from Heroes service
2. Fetch random villain from Villains service
3. Fetch random location from Locations service
4. Calculate fight winner based on levels
5. Return comprehensive fight result

**Fight Logic:**
``````python
winner = hero if hero.level > villain.level else villain
loser = villain if hero.level > villain.level else hero
``````

**Response Schema:**
``````json
{
  "id": "uuid",
  "fight_date": "ISO 8601 timestamp",
  "winner_name": "string",
  "winner_level": "integer",
  "winner_powers": "string",
  "winner_picture": "url",
  "winner_team": "heroes|villains",
  "loser_name": "string",
  "loser_level": "integer",
  "loser_powers": "string",
  "loser_picture": "url",
  "loser_team": "heroes|villains",
  "hero": {...},
  "villain": {...},
  "location": {...}
}
``````

## Communication Patterns

### Service-to-Service Communication

The Fights service acts as an orchestrator using HTTP requests:

``````
Fights Service
    ├─> GET http://heroes:8000/api/heroes/random_hero
    ├─> GET http://villains:8000/api/villains/random_villain
    └─> GET http://locations:8000/api/locations/random_location
``````

**Error Handling:**
- HTTP 502: Service unavailable
- HTTP 404: Resource not found
- Retry logic in upstream clients (K6 tests)

### Database Connection Management

All services implement connection pooling:

**PostgreSQL (asyncpg):**
``````python
pool = await asyncpg.create_pool(
    DATABASE_URL, 
    min_size=10, 
    max_size=50
)
``````

**MariaDB (aiomysql):**
``````python
pool = await aiomysql.create_pool(
    host=...,
    minsize=1,
    maxsize=10
)
``````

**Benefits:**
- Connection reuse reduces overhead
- Configurable pool sizes for scaling
- Automatic connection health checks

## Resilience Patterns

### 1. Retry Logic
Services retry database connections on startup:

``````python
RETRY_TIMEOUT = 10  # seconds
RETRY_INTERVAL = 0.5  # seconds

while time_elapsed < RETRY_TIMEOUT:
    try:
        connect()
        break
    except ConnectionError:
        await asyncio.sleep(RETRY_INTERVAL)
``````

### 2. Health Checks
Docker Compose health checks ensure dependencies:

``````yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U superman"]
  interval: 10s
  timeout: 5s
  retries: 20
``````

### 3. Graceful Shutdown
All services implement cleanup:

``````python
async def shutdown():
    await app.state.pool.close()
``````

## Scalability Considerations

### Horizontal Scaling
Each service can scale independently:

``````bash
docker-compose up --scale heroes=3 --scale villains=3
``````

**Requirements:**
- Load balancer (nginx/traefik)
- Shared database instances
- Session-less design (current implementation ✓)

### Vertical Scaling
Database connection pools can be tuned:

- **Light load**: min=5, max=20
- **Medium load**: min=10, max=50 (current)
- **Heavy load**: min=20, max=100

### Performance Characteristics

Based on K6 testing:

| RPS | p95 Latency | Error Rate | Notes |
|-----|-------------|------------|-------|
| 1 | <50ms | <0.1% | Baseline |
| 10 | <100ms | <0.1% | Comfortable |
| 50 | <200ms | <0.5% | Scaling required |
| 100 | <500ms | <1% | Database tuning needed |

## Security Considerations

**Current Implementation:**
- No authentication/authorization
- Hardcoded credentials (development only)
- No HTTPS/TLS

**Production Recommendations:**
1. Add API gateway with authentication
2. Use secrets management (Vault, AWS Secrets Manager)
3. Enable TLS between services
4. Implement rate limiting
5. Add input validation and sanitization
6. Use database user permissions properly

## Deployment

### Docker Compose
Current deployment uses Docker Compose for orchestration:

**Advantages:**
- Simple local development
- Service dependency management
- Integrated networking

**Limitations:**
- Single host only
- Manual scaling
- No auto-healing

### Production Deployment

**Kubernetes Recommendation:**
``````yaml
Services → Deployments
Databases → StatefulSets
Networking → Services + Ingress
Configuration → ConfigMaps + Secrets
``````

**Benefits:**
- Auto-scaling
- Self-healing
- Rolling updates
- Multi-host deployment
- Built-in service discovery

## Monitoring and Observability

**Recommended Additions:**
1. **Structured Logging**: JSON logs with correlation IDs
2. **Metrics**: Prometheus exporters for each service
3. **Tracing**: OpenTelemetry for distributed tracing
4. **Health Endpoints**: `/health` and `/ready` for each service
5. **APM**: Application Performance Monitoring (DataDog, New Relic)

## Future Enhancements

1. **Event-Driven Architecture**: Use message queue (RabbitMQ/Kafka) instead of synchronous HTTP
2. **CQRS**: Separate read/write models for fights
3. **Event Sourcing**: Store all fight events for replay
4. **GraphQL Gateway**: Single API endpoint for clients
5. **Service Mesh**: Istio for advanced networking
6. **Feature Flags**: LaunchDarkly for progressive rollouts
