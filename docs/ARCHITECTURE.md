# Architecture Documentation

## System Overview

Python Super Heroes is a microservices-based application demonstrating distributed system patterns, async Python programming, and multi-database architecture.

## Design Principles

1. **Microservices Architecture**: Each service has a single responsibility
2. **Database per Service**: Each service owns its data and schema
3. **Async-First**: All I/O operations use async/await patterns
4. **API Gateway Pattern**: Fights service orchestrates calls to other services
5. **Polyglot Persistence**: Different databases for different data models

## System Components

### Service Layer

```
┌──────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│                    (HTTP/REST Clients)                       │
└────────────────┬─────────────────────────────────────────────┘
                 │
         ┌───────▼────────┐
         │ Fights Service │  ◄── Orchestrator/API Gateway
         │   (FastAPI)    │
         └────┬─────┬─────┘
              │     │
     ┌────────┼─────┼────────┐
     │        │     │        │
┌────▼───┐ ┌─▼──┐ ┌▼──────┐ │
│ Heroes │ │Vill│ │Locati-│ │ ◄── Domain Services
│        │ │ains│ │ons    │ │
└────┬───┘ └─┬──┘ └┬──────┘ │
     │       │     │        │
┌────▼───┐ ┌─▼──┐ ┌▼──────┐ │
│Postgres│ │Post│ │MariaDB│ │ ◄── Data Layer
│  :5432 │ │:543│ │ :3306 │ │
└────────┘ └─3──┘ └───────┘ │
                             │
                    ┌────────▼──┐
                    │  MongoDB  │ ◄── Reserved (not used)
                    │   :27017  │
                    └───────────┘
```

### Service Descriptions

#### Heroes Service
- **Responsibility**: CRUD operations for superhero data
- **Technology**: Starlette + asyncpg
- **Database**: PostgreSQL (heroes_database)
- **Port**: 8001
- **Key Features**:
  - List all heroes
  - Get hero by ID
  - Random hero selection

#### Villains Service
- **Responsibility**: CRUD operations for villain data
- **Technology**: Starlette + asyncpg
- **Database**: PostgreSQL (villains_database)
- **Port**: 8002
- **Key Features**:
  - List all villains
  - Get villain by ID
  - Random villain selection

#### Locations Service
- **Responsibility**: CRUD operations for battle locations
- **Technology**: Starlette + aiomysql
- **Database**: MariaDB (locations_database)
- **Port**: 8003
- **Key Features**:
  - List all locations
  - Get location by ID
  - Random location selection
  - Health check endpoint

#### Fights Service
- **Responsibility**: Battle orchestration and service aggregation
- **Technology**: FastAPI + httpx
- **Database**: None (stateless)
- **Port**: 8004
- **Key Features**:
  - Aggregate data from multiple services
  - Parallel service calls
  - Fight outcome calculation
  - OpenAPI/Swagger documentation

## Data Flow

### Execute Fight Flow

```
Client Request
    │
    ▼
GET /api/fights/execute_fight
    │
    ├──[Parallel]──┬─► GET heroes:8000/api/heroes/random_hero
    │              └─► GET villains:8000/api/villains/random_villain
    │
    ├──[Sequential]─► GET locations:8000/api/locations/random_location
    │
    ├──[Business Logic]─► Compare hero.level vs villain.level
    │
    └─► Return fight result
```

### Key Characteristics:

1. **Parallel Requests**: Hero and villain fetched simultaneously using `asyncio.gather()`
2. **Sequential Requests**: Location fetched after fighters
3. **No Persistence**: Fight results not stored (stateless)
4. **Deterministic Logic**: Winner determined by level comparison

## Database Architecture

### PostgreSQL (Heroes & Villains)

**Schema Similarity**: Both services use identical 23-column schema

```sql
CREATE TABLE hero/villain (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    othername VARCHAR,
    picture VARCHAR,
    level INTEGER,
    powers TEXT,
    -- ... 18 more columns
);
```

**Why PostgreSQL?**
- ACID compliance for character data
- Rich querying capabilities
- Excellent JSON support
- Mature async drivers (asyncpg)

### MariaDB (Locations)

**Schema**:
```sql
CREATE TABLE Location (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    description TEXT,
    picture VARCHAR(500)
);
```

**Why MariaDB?**
- Demonstrates polyglot persistence
- Good text search for location descriptions
- Lightweight for simple data model

### MongoDB (Fights - Reserved)

Currently configured but not utilized. Potential future use:
- Store fight history
- Analytics data
- Event sourcing

## Communication Patterns

### Synchronous REST
- All inter-service communication uses HTTP/REST
- JSON payload format
- Standard HTTP status codes

### Request/Response Flow
```
Client ─HTTP─► Fights ─HTTP─► Heroes
                      ─HTTP─► Villains
                      ─HTTP─► Locations
```

### Error Propagation
- Services return HTTP error codes
- Fights service propagates downstream errors
- No circuit breakers or retry logic (intentionally simple)

## Deployment Architecture

### Docker Compose Orchestration

```yaml
Services:
  - fights-db (MongoDB)      # Port 27017
  - heroes-db (PostgreSQL)   # Port 5432
  - villains-db (PostgreSQL) # Port 5433
  - locations-db (MariaDB)   # Port 3306
  - heroes                   # Port 8001
  - villains                 # Port 8002
  - locations                # Port 8003
  - fights                   # Port 8004
  - k6 (load testing)        # On-demand
```

### Dependency Graph

```
fights ─depends_on─► heroes-db (healthy)
heroes ─depends_on─► villains-db (healthy)
villains ─depends_on─► locations-db (healthy)
locations ─depends_on─► fights-db
k6 (no dependencies, runs independently)
```

### Health Checks

**Database Health Checks**:
- PostgreSQL: `pg_isready -U superman`
- MariaDB: `healthcheck.sh --connect --innodb_initialized`
- MongoDB: No health check (not critical)

## Scalability Considerations

### Horizontal Scaling
- All services are stateless (except databases)
- Can run multiple instances behind load balancer
- No shared state between service instances

### Bottlenecks
1. **Database Connections**: Each service uses connection pooling
2. **Network Latency**: Service-to-service HTTP calls
3. **Sequential Requests**: Location fetch after fighters

### Optimization Opportunities
1. Implement caching layer (Redis)
2. Add circuit breakers and retries
3. Use gRPC instead of HTTP/REST
4. Implement event-driven architecture
5. Add API gateway (Kong, Traefik)

## Security Considerations

**Current State** (Development):
- Hardcoded database credentials
- No authentication/authorization
- No HTTPS/TLS
- Direct database exposure on host ports

**Production Recommendations**:
1. Use secrets management (Vault, AWS Secrets Manager)
2. Implement API authentication (JWT, OAuth2)
3. Enable TLS for all communication
4. Use internal Docker networks
5. Add rate limiting and DDoS protection

## Monitoring and Observability

### Current Tools
- **k6**: Load testing and performance metrics
- **Docker logs**: Basic application logging

### Recommended Additions
1. **Distributed Tracing**: Jaeger, Zipkin
2. **Metrics**: Prometheus + Grafana
3. **Logging**: ELK stack or Loki
4. **APM**: New Relic, Datadog
5. **Health Checks**: Dedicated endpoint per service

## Technology Choices

### Why Async Python?
- High concurrency with single-threaded event loop
- Efficient I/O handling for database and HTTP
- Modern Python best practices
- Excellent library ecosystem

### Why Multiple Frameworks?
- **FastAPI**: Rich features, automatic docs, validation
- **Starlette**: Lightweight, minimal overhead, flexibility
- Demonstrates framework diversity and interoperability

### Why Multiple Databases?
- **Educational**: Shows polyglot persistence patterns
- **Real-world**: Different databases for different needs
- **Benchmarking**: Compare performance across databases

## Future Architecture Enhancements

1. **Message Queue**: Add RabbitMQ/Kafka for async processing
2. **Caching**: Redis for frequently accessed data
3. **Service Mesh**: Istio or Linkerd for advanced networking
4. **API Gateway**: Centralized routing and authentication
5. **Event Sourcing**: Store fight history in MongoDB
6. **GraphQL**: Alternative to REST for flexible querying
7. **gRPC**: High-performance inter-service communication
