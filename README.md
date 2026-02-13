# Python Super Heroes

A microservices-based superhero fighting game with load testing capabilities. Watch heroes and villains battle it out across epic locations!

## Overview

Python Super Heroes is a distributed application demonstrating microservices architecture, polyglot persistence, and performance testing with K6. The system orchestrates random fights between heroes and villains at various locations, with results determined by character power levels.

### Architecture

``````
┌─────────────────────────────────────────────────────────────────┐
│                        Fights Service (Port 8004)               │
│                         FastAPI + MongoDB                       │
└──────────┬─────────────────────┬─────────────────┬──────────────┘
           │                     │                 │
           ▼                     ▼                 ▼
    ┌─────────────┐      ┌─────────────┐   ┌─────────────┐
    │   Heroes    │      │  Villains   │   │  Locations  │
    │  Port 8001  │      │  Port 8002  │   │  Port 8003  │
    │  Starlette  │      │  Starlette  │   │  Starlette  │
    └──────┬──────┘      └──────┬──────┘   └──────┬──────┘
           │                    │                  │
           ▼                    ▼                  ▼
    ┌─────────────┐      ┌─────────────┐   ┌─────────────┐
    │ PostgreSQL  │      │ PostgreSQL  │   │   MariaDB   │
    │  Port 5432  │      │  Port 5433  │   │  Port 3306  │
    └─────────────┘      └─────────────┘   └─────────────┘
``````

### Features

- **Microservices Architecture**: Four independent services with dedicated databases
- **Polyglot Persistence**: PostgreSQL, MariaDB, and MongoDB
- **RESTful APIs**: JSON-based communication between services
- **Load Testing**: K6 scenarios with ramping request rates (1-100 RPS)
- **Docker Compose**: Complete orchestration with health checks
- **Database Initialization**: Pre-populated with 100 heroes, villains, and locations

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum

### Running the Application

1. **Clone the repository**
   ``````bash
   git clone https://github.com/flyaruu/python-super-heroes.git
   cd python-super-heroes
   ``````

2. **Start all services**
   ``````bash
   docker-compose up -d
   ``````

3. **Verify services are running**
   ``````bash
   docker-compose ps
   ``````

4. **Execute a random fight**
   ``````bash
   curl http://localhost:8004/api/fights/execute_fight
   ``````

### Testing the APIs

**Get a random hero:**
``````bash
curl http://localhost:8001/api/heroes/random_hero
``````

**Get a random villain:**
``````bash
curl http://localhost:8002/api/villains/random_villain
``````

**Get a random location:**
``````bash
curl http://localhost:8003/api/locations/random_location
``````

**Get random fighters:**
``````bash
curl http://localhost:8004/api/fights/randomfighters
``````

## Services

| Service | Port | Framework | Database | Purpose |
|---------|------|-----------|----------|---------|
| Heroes | 8001 | Starlette | PostgreSQL (5432) | Manage hero characters |
| Villains | 8002 | Starlette | PostgreSQL (5433) | Manage villain characters |
| Locations | 8003 | Starlette | MariaDB (3306) | Manage fight locations |
| Fights | 8004 | FastAPI | MongoDB (27017) | Orchestrate battles |

## Load Testing

The project includes K6 load testing scenarios:

``````bash
# Run K6 container
docker-compose run k6 k6 run -e RAMPING_RATE=10 /k6/load.js
``````

Available scenarios:
- **1 RPS**: Baseline performance
- **10 RPS**: Light load
- **50 RPS**: Medium load
- **75 RPS**: Heavy load
- **100 RPS**: Stress test

Results are saved to `k6/results/` directory.

## Documentation

- [Architecture Details](docs/ARCHITECTURE.md) - System design and patterns
- [API Reference](docs/API.md) - Complete endpoint documentation
- [Development Guide](docs/DEVELOPMENT.md) - Setup and debugging
- [Testing Guide](docs/TESTING.md) - Load testing and benchmarks
- [Contributing](CONTRIBUTING.md) - Development workflow

## Technology Stack

**Languages & Frameworks:**
- Python 3.11+
- FastAPI (Fights service)
- Starlette (Heroes, Villains, Locations)
- asyncpg (PostgreSQL async client)
- aiomysql (MySQL async client)

**Databases:**
- PostgreSQL 16
- MariaDB 11.5
- MongoDB 7.0

**Testing:**
- K6 (load testing)

**Deployment:**
- Docker
- Docker Compose

## Project Structure

``````
.
├── services/
│   ├── fights/          # Fights orchestration service
│   ├── heroes/          # Heroes service
│   ├── villains/        # Villains service
│   └── locations/       # Locations service
├── database/
│   ├── fights-db/       # MongoDB initialization
│   ├── heroes-db/       # PostgreSQL heroes schema
│   ├── villains-db/     # PostgreSQL villains schema
│   └── locations-db/    # MariaDB locations schema
├── k6/
│   ├── load.js          # Load test configuration
│   ├── randomFight.js   # Fight simulation script
│   └── results/         # Test results output
├── compose.yml          # Docker orchestration
└── usage_scenario.yml   # K6 test scenarios
``````

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

This project is available for educational and demonstration purposes.

## Author

Frank Lyaruu

## Acknowledgments

- Hero/villain data sourced from [Quarkus Super Heroes](https://github.com/quarkusio/quarkus-super-heroes)
