# Python Super Heroes

A microservices-based demonstration application that simulates superheroes fighting villains at various locations. This project showcases distributed systems architecture with performance testing and optimization capabilities using k6 load testing.

## Overview

Python Super Heroes is a learning-oriented microservices application built to demonstrate:

- **Asynchronous Python microservices** using FastAPI and Starlette
- **Service orchestration patterns** with sequential and parallel HTTP calls
- **Performance testing** at scale using k6
- **Multi-database architecture** (PostgreSQL, MariaDB, MongoDB)
- **Docker Compose** for local development and testing

## Architecture

The application consists of four microservices communicating via HTTP REST APIs:

```
┌──────────────┐
│    Fights    │ ◄─── Orchestrator Service (Port 8004)
│   (FastAPI)  │
└──────┬───────┘
       │
       ├─────► Heroes Service (Port 8001) ──► PostgreSQL
       ├─────► Villains Service (Port 8002) ──► PostgreSQL  
       └─────► Locations Service (Port 8003) ──► MariaDB
```

### Services

| Service | Framework | Database | Port | Purpose |
|---------|-----------|----------|------|---------|
| **Fights** | FastAPI | MongoDB | 8004 | Orchestrates battles by fetching heroes, villains, and locations |
| **Heroes** | Starlette | PostgreSQL | 8001 | Manages hero data and provides random hero selection |
| **Villains** | Starlette | PostgreSQL | 8002 | Manages villain data and provides random villain selection |
| **Locations** | Starlette | MariaDB | 8003 | Manages fight locations and provides random location selection |

### Key Endpoints

#### Fights Service
- `GET /api/fights/randomfighters` - Fetch a random hero and villain
- `GET /api/fights/randomlocation` - Fetch a random fight location
- `GET /api/fights/execute_fight` - Execute a random fight (fetches hero, villain, location)
- `POST /api/fights` - Create a custom fight

#### Heroes Service
- `GET /api/heroes` - List all heroes
- `GET /api/heroes/random_hero` - Get a random hero
- `GET /api/heroes/{id}` - Get a specific hero by ID

#### Villains Service
- `GET /api/villains/random_villain` - Get a random villain

#### Locations Service
- `GET /api/locations/random_location` - Get a random location

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) k6 for load testing

### Running the Application

1. **Start all services:**

   ``````bash
   docker compose up --build
   ``````

2. **Verify services are running:**

   ``````bash
   # Check heroes service
   curl http://localhost:8001/api/heroes

   # Check villains service
   curl http://localhost:8002/api/villains/random_villain

   # Check locations service
   curl http://localhost:8003/api/locations/random_location

   # Execute a fight
   curl http://localhost:8004/api/fights/execute_fight
   ``````

3. **Stop all services:**

   ``````bash
   docker compose down
   ``````

## Load Testing

The project includes comprehensive k6 load testing scenarios to measure performance at different request rates.

### Running Load Tests

The `usage_scenario.yml` defines automated load tests at 1, 10, 50, 75, and 100 requests per second (RPS).

**Manual k6 execution:**

``````bash
# Run load test at 10 RPS
docker compose exec k6 k6 run -e RAMPING_RATE=10 \
  --summary-export=/results/summary_10.json \
  /k6/load.js

# View results
docker compose exec k6 cat /results/summary_10.json
``````

### Load Test Scenarios

| Scenario | RPS | Description |
|----------|-----|-------------|
| Baseline | 1 | Single request per second for baseline metrics |
| Low Load | 10 | Low concurrency scenario |
| Medium Load | 50 | Medium traffic simulation |
| High Load | 75 | High traffic stress test |
| Peak Load | 100 | Maximum load scenario |

## Project Structure

``````
python-super-heroes/
├── compose.yml                 # Docker Compose orchestration
├── services/                   # Microservices directory
│   ├── fights/                # Fights orchestrator service
│   │   ├── main.py           # FastAPI application
│   │   ├── requirements.txt  # Python dependencies
│   │   └── Dockerfile        # Container configuration
│   ├── heroes/               # Heroes service
│   ├── villains/             # Villains service
│   └── locations/            # Locations service
├── database/                  # Database initialization scripts
│   ├── fights-db/            # MongoDB initialization
│   ├── heroes-db/            # PostgreSQL heroes schema
│   ├── villains-db/          # PostgreSQL villains schema
│   └── locations-db/         # MariaDB locations schema
├── k6/                        # Load testing scripts
│   ├── load.js               # k6 load test configuration
│   └── results/              # Test results output
├── k6-image/                  # Custom k6 Docker image
└── usage_scenario.yml         # Automated test orchestration
``````

## Technology Stack

### Backend Services
- **Python 3.x** - Programming language
- **FastAPI** - Modern async web framework (Fights service)
- **Starlette** - Lightweight ASGI framework (Heroes, Villains, Locations)
- **Uvicorn** - ASGI web server
- **httpx** - Async HTTP client for service-to-service communication

### Databases
- **PostgreSQL 16** - Heroes and Villains data
- **MariaDB 11.5** - Locations data
- **MongoDB 7.0** - Fights data

### Database Drivers
- **asyncpg** - PostgreSQL async driver
- **aiomysql** - MariaDB/MySQL async driver
- **Motor** - MongoDB async driver

### Testing & DevOps
- **k6** - Load testing and performance measurement
- **Docker & Docker Compose** - Containerization and orchestration
- **python-dotenv** - Environment configuration management

## Development

### Service Development

Each service follows a similar structure:

1. **main.py** - Application entry point
2. **requirements.txt** - Python dependencies
3. **Dockerfile** - Container build configuration

### Environment Variables

Services use environment variables for database connections:

- `DATABASE_URL` - PostgreSQL connection string (Heroes, Villains)
- `MYSQL_URL` - MariaDB connection string (Locations)
- MongoDB connection configured in Fights service

### Database Initialization

Database schemas are automatically initialized on first startup using initialization scripts in the `database/` directory.

## Performance Optimization

This project is designed to explore microservice performance patterns, particularly:

- **Sequential vs. Parallel Service Calls** - The Fights service can orchestrate calls sequentially or in parallel
- **Connection Pooling** - Services use connection pools (min: 10, max: 50 connections)
- **Async I/O** - All services leverage async/await for non-blocking operations
- **Database Query Optimization** - Using indexes and optimized queries

### GitHub Actions Workflows

Automated workflows enhance the development experience:

- **daily-perf-improver** - Identifies performance bottlenecks and creates optimization PRs
- **update-docs** - Ensures documentation stays synchronized with code changes

## Contributing

When contributing to this project:

1. Ensure all services start successfully with `docker compose up`
2. Run load tests to verify performance isn't degraded
3. Update documentation for any API or architectural changes
4. Follow the existing code style and patterns

## License

This project is a demonstration/educational application. Check with the repository owner for licensing details.

## Support

For issues, questions, or contributions, please use the GitHub Issues or Discussions features.
