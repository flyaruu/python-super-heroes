# Python Super Heroes

A microservices-based superhero battle simulation system built with Python, featuring multiple database backends and load testing capabilities.

## Overview

Python Super Heroes is a distributed application that simulates battles between heroes and villains at random locations. The system demonstrates modern microservices architecture patterns, including:

- Multiple Python web frameworks (FastAPI, Starlette)
- Polyglot persistence (PostgreSQL, MySQL/MariaDB, MongoDB)
- Docker Compose orchestration
- Load testing with k6
- Asynchronous Python programming

## Architecture

The application consists of four main microservices:

- **Heroes Service** - Manages superhero data (PostgreSQL)
- **Villains Service** - Manages villain data (PostgreSQL)
- **Locations Service** - Manages battle location data (MariaDB)
- **Fights Service** - Orchestrates battles between heroes and villains (MongoDB)

### System Diagram

```
┌──────────────┐
│  k6 Load     │
│  Testing     │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│       Fights Service (FastAPI)       │
│         Port: 8004                   │
└──┬────────────┬────────────┬─────────┘
   │            │            │
   ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────────┐
│ Heroes │  │Villains│  │ Locations  │
│(8001)  │  │(8002)  │  │  (8003)    │
└───┬────┘  └───┬────┘  └─────┬──────┘
    │           │              │
    ▼           ▼              ▼
┌─────────┐ ┌─────────┐ ┌───────────┐
│PostgreSQL│ │PostgreSQL│ │  MariaDB  │
│  5432   │ │  5433   │ │   3306    │
└─────────┘ └─────────┘ └───────────┘

Fights Service also uses:
┌──────────┐
│ MongoDB  │
│  27017   │
└──────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Running the Application

1. Clone the repository:
   ``````bash
   git clone https://github.com/flyaruu/python-super-heroes.git
   cd python-super-heroes
   ``````

2. Start all services:
   ``````bash
   docker compose up -d
   ``````

3. Wait for services to initialize (approximately 30 seconds)

4. Verify services are running:
   ``````bash
   docker compose ps
   ``````

### Testing the API

Get a random hero:
``````bash
curl http://localhost:8001/api/heroes/random_hero
``````

Get a random villain:
``````bash
curl http://localhost:8002/api/villains/random_villain
``````

Get a random location:
``````bash
curl http://localhost:8003/api/locations/random_location
``````

Execute a random fight:
``````bash
curl http://localhost:8004/api/fights/execute_fight
``````

## Services Documentation

### Heroes Service

- **Port**: 8001
- **Framework**: Starlette
- **Database**: PostgreSQL (port 5432)
- **Documentation**: [docs/services/heroes.md](docs/services/heroes.md)

**API Endpoints**:
- `GET /api/heroes` - List all heroes
- `GET /api/heroes/random_hero` - Get a random hero
- `GET /api/heroes/{id}` - Get hero by ID

### Villains Service

- **Port**: 8002
- **Framework**: Starlette
- **Database**: PostgreSQL (port 5433)
- **Documentation**: [docs/services/villains.md](docs/services/villains.md)

**API Endpoints**:
- `GET /api/villains` - List all villains
- `GET /api/villains/random_villain` - Get a random villain
- `GET /api/villains/{id}` - Get villain by ID

### Locations Service

- **Port**: 8003
- **Framework**: Starlette
- **Database**: MariaDB (port 3306)
- **Documentation**: [docs/services/locations.md](docs/services/locations.md)

**API Endpoints**:
- `GET /api/locations` - List all locations
- `GET /api/locations/random_location` - Get a random location
- `GET /api/locations/{id}` - Get location by ID

### Fights Service

- **Port**: 8004
- **Framework**: FastAPI
- **Database**: MongoDB (port 27017)
- **Documentation**: [docs/services/fights.md](docs/services/fights.md)

**API Endpoints**:
- `GET /api/fights/randomfighters` - Get random hero and villain
- `GET /api/fights/randomlocation` - Get random fight location
- `GET /api/fights/execute_fight` - Execute a random fight
- `POST /api/fights` - Create a custom fight

## Load Testing

The project includes k6 load testing configuration. See [docs/load-testing.md](docs/load-testing.md) for details.

### Running Load Tests

Execute a load test:
``````bash
docker compose exec k6 k6 run -e RAMPING_RATE=10 /k6/load.js
``````

## Development

### Project Structure

``````
python-super-heroes/
├── compose.yml              # Docker Compose configuration
├── database/               # Database initialization scripts
│   ├── fights-db/         # MongoDB init
│   ├── heroes-db/         # PostgreSQL heroes init
│   ├── villains-db/       # PostgreSQL villains init
│   └── locations-db/      # MariaDB locations init
├── services/              # Microservices
│   ├── fights/           # Fights service
│   ├── heroes/           # Heroes service
│   ├── villains/         # Villains service
│   └── locations/        # Locations service
├── k6/                   # Load testing scripts
└── k6-image/            # Custom k6 Docker image
``````

### Adding New Features

See [docs/development.md](docs/development.md) for development guidelines.

## Configuration

All services use environment variables for configuration. See [docs/configuration.md](docs/configuration.md) for details.

## Troubleshooting

Common issues and solutions can be found in [docs/troubleshooting.md](docs/troubleshooting.md).

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

This project is open source. Please check the repository for license information.

## Credits

Hero and villain data is sourced from the [Quarkus Super Heroes](https://github.com/quarkusio/quarkus-super-heroes) project.
