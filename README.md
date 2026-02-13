# Python Super Heroes

A microservices-based superhero battle simulation system built with Python, featuring multiple databases and RESTful APIs.

## Overview

Python Super Heroes is a distributed application demonstrating microservices architecture patterns. It simulates battles between heroes and villains at various locations, leveraging different database technologies for each service.

## Architecture

The system consists of four core microservices:

- **Heroes Service** - Manages superhero data (PostgreSQL)
- **Villains Service** - Manages villain data (PostgreSQL)
- **Locations Service** - Manages battle locations (MariaDB)
- **Fights Service** - Orchestrates battles between heroes and villains (MongoDB)

### Technology Stack

- **Runtime**: Python 3.x with async/await
- **Web Frameworks**: Starlette, FastAPI
- **Databases**: PostgreSQL 16, MongoDB 7.0, MariaDB 11.5
- **Database Drivers**: asyncpg, aiomysql, Motor
- **Deployment**: Docker Compose
- **Load Testing**: k6

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)
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

3. Verify services are running:
   ``````bash
   docker compose ps
   ``````

### Service Endpoints

Once running, the following endpoints are available:

- **Heroes Service**: http://localhost:8001
- **Villains Service**: http://localhost:8002
- **Locations Service**: http://localhost:8003
- **Fights Service**: http://localhost:8004

## API Documentation

### Heroes Service (Port 8001)

- `GET /api/heroes` - List all heroes
- `GET /api/heroes/{id}` - Get a specific hero
- `GET /api/heroes/random_hero` - Get a random hero

### Villains Service (Port 8002)

- `GET /api/villains` - List all villains
- `GET /api/villains/{id}` - Get a specific villain
- `GET /api/villains/random_villain` - Get a random villain

### Locations Service (Port 8003)

- `GET /api/locations` - List all locations
- `GET /api/locations/{id}` - Get a specific location
- `GET /api/locations/random_location` - Get a random location

### Fights Service (Port 8004)

- `GET /api/fights/randomfighters` - Get random hero and villain
- `GET /api/fights/randomlocation` - Get random battle location
- `GET /api/fights/execute_fight` - Execute a random battle
- `POST /api/fights` - Create a custom fight

## Load Testing

The project includes k6 load testing scenarios at various request rates (1, 10, 50, 75, 100 RPS).

Run load tests:
``````bash
docker compose exec k6 k6 run -e RAMPING_RATE=10 /k6/load.js
``````

## Project Structure

``````
.
├── services/
│   ├── heroes/         # Heroes microservice
│   ├── villains/       # Villains microservice
│   ├── locations/      # Locations microservice
│   └── fights/         # Fights orchestration service
├── database/
│   ├── heroes-db/      # PostgreSQL initialization
│   ├── villains-db/    # PostgreSQL initialization
│   ├── locations-db/   # MariaDB initialization
│   └── fights-db/      # MongoDB initialization
├── k6/                 # Load testing scripts
├── k6-image/           # k6 Docker image
├── compose.yml         # Docker Compose configuration
└── usage_scenario.yml  # Load testing scenarios
``````

## Development

### Local Development Setup

1. Install dependencies for a specific service:
   ``````bash
   cd services/heroes
   pip install -r requirements.txt
   ``````

2. Set environment variables:
   ``````bash
   export DATABASE_URL="postgres://superman:superman@localhost:5432/heroes_database"
   ``````

3. Run the service locally:
   ``````bash
   python main.py
   ``````

## Database Schemas

### Heroes & Villains (PostgreSQL)

- Table: `Hero` / `Villain`
- Fields: `id`, `name`, `otherName`, `level`, `powers`, `picture`

### Locations (MariaDB)

- Table: `Location`
- Fields: `id`, `name`, `description`, `picture`

### Fights (MongoDB)

- Collection: `fights`
- Documents contain fight results with winner/loser details

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is available for educational and demonstration purposes.

## Author

Frank Lyaruu
