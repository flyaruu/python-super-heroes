# Python Super Heroes

A microservices-based superhero fighting simulation system built with FastAPI, featuring multiple databases and load testing capabilities.

## Overview

Python Super Heroes is a distributed system that simulates epic battles between heroes and villains across various locations. The system consists of four independent microservices, each managing different aspects of the fight simulation, backed by different database technologies to demonstrate polyglot persistence patterns.

## Architecture

The system uses a microservices architecture with the following services:

```
┌─────────────────┐
│  Fights Service │ (Orchestrator)
│   Port: 8004    │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┬─────────────┐
    │          │          │             │
┌───▼───┐  ┌──▼────┐  ┌──▼────┐  ┌────▼─────┐
│Heroes │  │Villains│ │Locations│ │Fights DB │
│  8001 │  │  8002  │ │  8003   │ │ MongoDB  │
└───┬───┘  └───┬────┘ └───┬─────┘ └──────────┘
    │          │          │
┌───▼───┐  ┌───▼────┐ ┌──▼──────┐
│Postgres│ │Postgres│ │ MariaDB │
│  5432  │ │  5433  │ │  3306   │
└────────┘ └────────┘ └─────────┘
```

### Services

- **Fights Service** (`/api/fights`): Orchestrates battles by fetching heroes, villains, and locations, then determining winners
- **Heroes Service** (`/api/heroes`): Manages superhero data including names, powers, and stats
- **Villains Service** (`/api/villains`): Manages villain data with similar structure to heroes
- **Locations Service** (`/api/locations`): Manages fight locations (cities, planets, islands, etc.)

## Technology Stack

- **Framework**: FastAPI + Uvicorn
- **Languages**: Python 3.13
- **Databases**: 
  - PostgreSQL 16 (Heroes & Villains)
  - MariaDB 11.5 (Locations)
  - MongoDB 7.0 (Fight Results)
- **Orchestration**: Docker Compose
- **Load Testing**: k6
- **HTTP Client**: httpx (async)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- (Optional) Python 3.13+ for local development

### Running the System

1. **Clone the repository**:
   ``````bash
   git clone https://github.com/flyaruu/python-super-heroes.git
   cd python-super-heroes
   ``````

2. **Start all services**:
   ``````bash
   docker-compose up -d
   ``````

3. **Verify services are running**:
   ``````bash
   # Check all containers
   docker-compose ps
   
   # Test heroes service
   curl http://localhost:8001/api/heroes
   
   # Test a random fight
   curl http://localhost:8004/api/fights/execute_fight
   ``````

4. **Stop the system**:
   ``````bash
   docker-compose down
   ``````

## API Endpoints

### Heroes Service (Port 8001)

- `GET /api/heroes` - List all heroes
- `GET /api/heroes/{id}` - Get hero by ID
- `GET /api/heroes/random_hero` - Get a random hero

### Villains Service (Port 8002)

- `GET /api/villains` - List all villains
- `GET /api/villains/{id}` - Get villain by ID
- `GET /api/villains/random_villain` - Get a random villain

### Locations Service (Port 8003)

- `GET /api/locations` - List all locations
- `GET /api/locations/{id}` - Get location by ID
- `GET /api/locations/random_location` - Get a random location

### Fights Service (Port 8004)

- `GET /api/fights/randomfighters` - Get random hero and villain
- `GET /api/fights/randomlocation` - Get random fight location
- `POST /api/fights` - Execute a fight with provided fighters
- `GET /api/fights/execute_fight` - Execute a complete random fight

## Load Testing

The project includes k6 load testing configuration to simulate realistic traffic patterns.

### Running Load Tests

``````bash
# Start the load test
docker-compose up k6

# View results
ls -l k6/results/
``````

### Load Test Configuration

- **Target**: 500 requests/second at peak
- **Duration**: 30 seconds total (5s ramp-up, 20s sustained, 5s ramp-down)
- **Performance Thresholds**:
  - 95th percentile latency < 500ms
  - Error rate < 0.1%
  - No dropped iterations

See [docs/load-testing.md](docs/load-testing.md) for detailed information.

## Development

### Local Development Setup

Each service can be run locally for development:

``````bash
# Example: Running heroes service locally
cd services/heroes
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
``````

### Project Structure

``````
python-super-heroes/
├── services/           # Microservices
│   ├── fights/        # Fight orchestration service
│   ├── heroes/        # Heroes CRUD service
│   ├── villains/      # Villains CRUD service
│   └── locations/     # Locations CRUD service
├── database/          # Database initialization scripts
│   ├── fights-db/     # MongoDB init
│   ├── heroes-db/     # PostgreSQL heroes schema
│   ├── villains-db/   # PostgreSQL villains schema
│   └── locations-db/  # MariaDB locations schema
├── k6/                # Load testing scripts
│   ├── load.js        # Load test configuration
│   └── randomFight.js # Fight simulation scenario
├── k6-image/          # Custom k6 Docker image
├── compose.yml        # Docker Compose configuration
└── docs/              # Documentation
``````

## Documentation

- [API Reference](docs/api-reference.md) - Complete API documentation
- [Architecture Guide](docs/architecture.md) - System design and patterns
- [Database Schema](docs/database-schema.md) - Database structures
- [Load Testing Guide](docs/load-testing.md) - Performance testing
- [Development Guide](docs/development.md) - Contributing and development workflow

## Performance Characteristics

- **Latency**: p95 < 500ms under 500 req/s load
- **Throughput**: Designed for 500+ requests/second
- **Availability**: Health checks on all database connections
- **Reliability**: Automatic retries with exponential backoff

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[Add your license here]

## Contact

- **Repository**: [flyaruu/python-super-heroes](https://github.com/flyaruu/python-super-heroes)
- **Issues**: [GitHub Issues](https://github.com/flyaruu/python-super-heroes/issues)
