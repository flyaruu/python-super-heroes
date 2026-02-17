# Python Super Heroes

A microservices-based application demonstrating superhero battles with load testing capabilities. Built with Python async frameworks and multiple database technologies.

## Overview

This project implements a distributed system for simulating superhero vs villain battles. It consists of four microservices that manage heroes, villains, locations, and fight orchestration, backed by three different database technologies.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Fights Service                       │
│                   (FastAPI + httpx)                      │
│                     Port: 8004                           │
└───────────┬──────────────┬─────────────┬────────────────┘
            │              │             │
    ┌───────▼──────┐  ┌───▼────────┐  ┌─▼──────────────┐
    │   Heroes     │  │  Villains  │  │   Locations    │
    │  (Starlette) │  │ (Starlette)│  │  (Starlette)   │
    │   Port: 8001 │  │ Port: 8002 │  │  Port: 8003    │
    └──────┬───────┘  └─────┬──────┘  └────────┬────────┘
           │                │                   │
    ┌──────▼─────┐   ┌─────▼──────┐    ┌──────▼────────┐
    │ PostgreSQL │   │ PostgreSQL │    │   MariaDB     │
    │   Port:    │   │   Port:    │    │   Port: 3306  │
    │   5432     │   │   5433     │    │               │
    └────────────┘   └────────────┘    └───────────────┘
```

### Services

- **Heroes Service**: Manages superhero data with PostgreSQL backend
- **Villains Service**: Manages villain data with PostgreSQL backend  
- **Locations Service**: Manages battle locations with MariaDB backend
- **Fights Service**: Orchestrates battles by calling other services

### Technology Stack

- **Web Frameworks**: FastAPI, Starlette, Uvicorn
- **Databases**: PostgreSQL 16, MariaDB 11.5, MongoDB 7.0
- **Async Libraries**: asyncpg, aiomysql, httpx
- **Load Testing**: k6
- **Orchestration**: Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.13+ (for local development)

### Running the Application

1. **Start all services**:
   ```bash
   docker-compose up -d
   ```

2. **Verify services are running**:
   ```bash
   docker-compose ps
   ```

3. **Execute a random fight**:
   ```bash
   curl http://localhost:8004/api/fights/execute_fight
   ```

### API Endpoints

#### Heroes Service (Port 8001)
- `GET /api/heroes` - List all heroes
- `GET /api/heroes/{id}` - Get specific hero
- `GET /api/heroes/random_hero` - Get random hero

#### Villains Service (Port 8002)
- `GET /api/villains` - List all villains
- `GET /api/villains/{id}` - Get specific villain
- `GET /api/villains/random_villain` - Get random villain

#### Locations Service (Port 8003)
- `GET /api/locations` - List all locations
- `GET /api/locations/{id}` - Get specific location
- `GET /api/locations/random_location` - Get random location

#### Fights Service (Port 8004)
- `GET /api/fights/randomfighters` - Get random hero and villain
- `GET /api/fights/randomlocation` - Get random location
- `POST /api/fights` - Create custom fight scenario
- `GET /api/fights/execute_fight` - Execute complete random fight

## Load Testing

The project includes k6 for load testing the microservices.

### Run Load Tests

```bash
# Enter k6 container
docker-compose exec k6 bash

# Run random fight load test
k6 run /k6/randomFight.js

# Run general load test
k6 run /k6/load.js
```

Test results are saved to `./k6/results/`.

## Development

### Local Development Setup

Each service can be run independently for development:

```bash
# Heroes service example
cd services/heroes
pip install -r requirements.txt
export DATABASE_URL="postgres://superman:superman@localhost:5432/heroes_database"
uvicorn main:app --reload --port 8001
```

### Database Access

- **Heroes DB**: `postgresql://superman:superman@localhost:5432/heroes_database`
- **Villains DB**: `postgresql://superman:superman@localhost:5433/villains_database`
- **Locations DB**: `mysql://locations:locations@localhost:3306/locations_database`
- **Fights DB**: `mongodb://super:super@localhost:27017/fights`

### Project Structure

```
.
├── services/           # Microservice implementations
│   ├── heroes/        # Heroes service (Starlette + PostgreSQL)
│   ├── villains/      # Villains service (Starlette + PostgreSQL)
│   ├── locations/     # Locations service (Starlette + MariaDB)
│   └── fights/        # Fights orchestrator (FastAPI)
├── database/          # Database initialization scripts
│   ├── heroes-db/
│   ├── villains-db/
│   ├── locations-db/
│   └── fights-db/
├── k6/                # Load testing scripts
├── k6-image/          # Custom k6 Docker image
└── compose.yml        # Docker Compose configuration
```

## Monitoring and Performance

The repository includes GitHub Actions workflows for:

- **Continuous Performance Improvement**: Automated performance profiling and optimization
- **Documentation Updates**: Automatic documentation synchronization
- **Load Testing**: Regular performance regression testing

See `.github/workflows/` for workflow configurations.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure services start correctly
5. Submit a pull request

## License

[Specify license here]

## Additional Resources

- [Architecture Documentation](docs/ARCHITECTURE.md) _(coming soon)_
- [API Documentation](docs/API.md) _(coming soon)_
- [Performance Tuning Guide](docs/PERFORMANCE.md) _(coming soon)_
- [Load Testing Guide](docs/LOAD_TESTING.md) _(coming soon)_
