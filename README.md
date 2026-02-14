# Python Super Heroes

A high-performance microservices application for simulating superhero battles, built with Python async frameworks and optimized for energy efficiency.

## Overview

Python Super Heroes is a cloud-native demonstration application showcasing modern Python microservices architecture with asynchronous operations, database integration, and load testing capabilities. The system orchestrates battles between heroes and villains at randomly selected locations, demonstrating RESTful API design and inter-service communication.

## Architecture

The application consists of four microservices, each with dedicated database backends:

```
┌─────────────┐      ┌──────────────┐      ┌───────────────┐
│   Heroes    │      │   Villains   │      │   Locations   │
│  Service    │      │   Service    │      │    Service    │
│ (Starlette) │      │ (Starlette)  │      │  (Starlette)  │
└──────┬──────┘      └──────┬───────┘      └───────┬───────┘
       │                    │                      │
       │ PostgreSQL         │ PostgreSQL           │ MySQL
       │                    │                      │
       └────────────────────┼──────────────────────┘
                            │
                    ┌───────▼────────┐
                    │     Fights     │
                    │    Service     │
                    │   (FastAPI)    │
                    └────────┬───────┘
                             │
                             │ MongoDB
                             │
```

### Services

#### Heroes Service
- **Framework**: Starlette
- **Database**: PostgreSQL
- **Port**: 8001
- **Purpose**: Manages superhero data and provides random hero selection

**Endpoints**:
- `GET /api/heroes` - List all heroes
- `GET /api/heroes/{id}` - Get specific hero
- `GET /api/heroes/random_hero` - Get random hero for battles

#### Villains Service
- **Framework**: Starlette
- **Database**: PostgreSQL
- **Port**: 8002
- **Purpose**: Manages villain data and provides random villain selection

**Endpoints**:
- `GET /api/villains` - List all villains
- `GET /api/villains/{id}` - Get specific villain
- `GET /api/villains/random_villain` - Get random villain for battles

#### Locations Service
- **Framework**: Starlette
- **Database**: MySQL (MariaDB)
- **Port**: 8003
- **Purpose**: Manages battle locations and provides random location selection

**Endpoints**:
- `GET /api/locations` - List all locations
- `GET /api/locations/{id}` - Get specific location
- `GET /api/locations/random_location` - Get random battle location

#### Fights Service
- **Framework**: FastAPI
- **Database**: MongoDB
- **Port**: 8004
- **Purpose**: Orchestrates battles between heroes and villains

**Endpoints**:
- `GET /api/fights/randomfighters` - Get random hero and villain (parallel fetching)
- `GET /api/fights/randomlocation` - Get random battle location
- `POST /api/fights` - Execute a fight with provided combatants
- `GET /api/fights/execute_fight` - Execute complete random fight (parallel data fetching)

## Performance Optimizations

This application implements several energy-efficiency and performance optimizations:

### Parallel Request Processing
- **Fights Service**: Uses `asyncio.gather()` to fetch heroes, villains, and locations concurrently
- Reduces total request time by executing independent operations in parallel

### Database Query Optimization
- **Random Selection**: Uses efficient `MAX(id)` approach instead of `ORDER BY RANDOM()`
- **Connection Pooling**: Configured pools for optimal resource utilization
  - Heroes/Villains: 10-50 connections
  - Locations: 1-10 connections

### HTTP Client Configuration
- **Connection Pooling**: 100 max connections, 20 keepalive
- **Aggressive Timeouts**: Connect (2s), Read (5s), Write (2s)
- **Reduced Logging**: WARNING level to minimize I/O overhead

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.13+ (for local development)
- 4GB+ RAM recommended

### Running with Docker Compose

1. **Clone the repository**:
   ``````bash
   git clone https://github.com/flyaruu/python-super-heroes.git
   cd python-super-heroes
   ``````

2. **Start all services**:
   ``````bash
   docker compose up -d
   ``````

3. **Verify services are running**:
   ``````bash
   docker compose ps
   ``````

4. **Execute a random fight**:
   ``````bash
   curl http://localhost:8004/api/fights/execute_fight
   ``````

### Sample Response

``````json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "fight_date": "2023-10-01T12:00:00Z",
  "winner_name": "Yoda",
  "winner_level": 286000,
  "winner_powers": "Acrobatics, Force Manipulation...",
  "winner_team": "heroes",
  "loser_name": "Thanos",
  "loser_level": 250000,
  "loser_team": "villains",
  "location": {
    "id": 42,
    "name": "Gotham City",
    "description": "Dark urban environment"
  }
}
``````

## Load Testing

The application includes k6-based load testing infrastructure.

### Running Load Tests

1. **Access k6 container**:
   ``````bash
   docker compose exec k6 bash
   ``````

2. **Execute load test**:
   ``````bash
   k6 run -e RAMPING_RATE=10 /k6/load.js
   ``````

3. **View results**:
   ``````bash
   cat /results/summary_10.json
   ``````

### Performance Thresholds

- **Response Time**: p95 < 500ms
- **Error Rate**: < 0.1%
- **Dropped Iterations**: 0

### Load Test Scenarios

The `usage_scenario.yml` defines automated test scenarios at various request rates:
- 1 RPS (baseline)
- 10 RPS (light load)
- 50 RPS (moderate load)
- 75 RPS (heavy load)
- 100 RPS (stress test)

## Development

### Local Development Setup

1. **Start databases only**:
   ``````bash
   docker compose up -d heroes-db villains-db locations-db fights-db
   ``````

2. **Install dependencies** (per service):
   ``````bash
   cd services/heroes
   pip install -r requirements.txt
   ``````

3. **Set environment variables**:
   ``````bash
   export DATABASE_URL="postgres://superman:superman@localhost:5432/heroes_database"
   ``````

4. **Run service**:
   ``````bash
   python main.py
   ``````

### Project Structure

``````
python-super-heroes/
├── services/
│   ├── heroes/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── villains/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── locations/
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── fights/
│       ├── main.py
│       ├── requirements.txt
│       └── Dockerfile
├── database/
│   ├── heroes-db/init/heroes.sql
│   ├── villains-db/init/villains.sql
│   ├── locations-db/init/initialize-tables.sql
│   └── fights-db/initialize-database.js
├── k6/
│   ├── load.js
│   └── randomFight.js
├── k6-image/
│   ├── Dockerfile
│   └── entrypoint.sh
├── compose.yml
└── usage_scenario.yml
``````

## Dependencies

### Core Frameworks
- **Starlette**: Lightweight ASGI framework for high performance
- **FastAPI**: Modern web framework with automatic API documentation
- **Uvicorn**: Lightning-fast ASGI server

### Database Drivers
- **asyncpg**: High-performance PostgreSQL driver
- **aiomysql**: Async MySQL/MariaDB driver
- **motor**: Async MongoDB driver (via pymongo)

### HTTP Client
- **httpx**: Async HTTP client with connection pooling

### Database Systems
- **PostgreSQL 16**: Heroes and Villains data
- **MariaDB 11.5**: Locations data
- **MongoDB 7.0**: Fights history

## Configuration

### Environment Variables

#### Heroes Service
- `DATABASE_URL`: PostgreSQL connection string (default: `postgres://superman:superman@heroes-db:5432/heroes_database`)

#### Villains Service
- `DATABASE_URL`: PostgreSQL connection string (default: `postgres://superman:superman@villains-db:5432/villains_database`)

#### Locations Service
- `MYSQL_URL`: MySQL connection string (default: `mysql://locations:locations@locations-db/locations_database`)

#### Fights Service
- No database configuration required (uses hardcoded service URLs)

### Database Retry Logic

All services implement robust connection retry logic:
- **Timeout**: 10-30 seconds depending on database type
- **Retry Interval**: 0.5 seconds
- **Behavior**: Services wait for database availability on startup

## Monitoring and Observability

### Health Checks

Database containers include health checks:
- **PostgreSQL**: `pg_isready` every 10s
- **MariaDB**: Built-in healthcheck every 10s
- **MongoDB**: No health check configured

### Logging

- **Level**: WARNING (production)
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- Minimized for performance and energy efficiency

## API Documentation

When running locally, FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8004/docs
- **ReDoc**: http://localhost:8004/redoc

## Troubleshooting

### Services not starting

1. **Check database health**:
   ``````bash
   docker compose logs heroes-db
   ``````

2. **Verify port availability**:
   ``````bash
   lsof -i :8001-8004
   ``````

3. **Review service logs**:
   ``````bash
   docker compose logs heroes
   ``````

### Connection timeouts

- Ensure all services are running: `docker compose ps`
- Check network connectivity: `docker network inspect python-super-heroes_default`
- Verify database initialization completed

### Load test failures

- Increase `maxVUs` in `k6/load.js` if hitting VU limits
- Adjust `http_req_duration` threshold for slower environments
- Check `dropped_iterations` metric for resource exhaustion

## CI/CD

The repository includes GitHub Actions workflows:

- **Agentic Maintenance**: Automated daily performance improvements
- **Documentation Updates**: Automatic documentation synchronization

See `.github/workflows/` for workflow definitions.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make targeted, minimal changes
4. Ensure all services build and run
5. Submit a pull request

## License

[Specify license here]

## Credits

Hero and villain data sourced from [Quarkus Super Heroes](https://github.com/quarkusio/quarkus-super-heroes).

## Contact

Maintained by Frank Lyaruu (flyaruu@gmail.com)
