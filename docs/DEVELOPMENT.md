# Development Guide

Guide for developers contributing to or extending the Python Super Heroes project.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Running Services Locally](#running-services-locally)
4. [Database Management](#database-management)
5. [Testing](#testing)
6. [Code Style](#code-style)
7. [Debugging](#debugging)
8. [Common Tasks](#common-tasks)

## Development Environment Setup

### Prerequisites

- **Python 3.13+**: Check with `python --version`
- **Docker**: Check with `docker --version`
- **Docker Compose**: Check with `docker-compose --version`
- **Git**: For version control

### Initial Setup

```bash
# Clone repository
git clone https://github.com/flyaruu/python-super-heroes.git
cd python-super-heroes

# Start all services
docker-compose up -d

# Verify services
docker-compose ps
```

### IDE Setup

#### VS Code

Recommended extensions:
- Python
- Docker
- REST Client
- Database Client

Create `.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

#### PyCharm

1. Configure Python interpreter (3.13+)
2. Enable Docker integration
3. Configure database connections
4. Set up run configurations for each service

## Project Structure

```
python-super-heroes/
├── .github/
│   ├── workflows/          # GitHub Actions workflows
│   └── copilot/           # Copilot instructions
├── database/              # Database initialization scripts
│   ├── heroes-db/
│   │   └── init/heroes.sql
│   ├── villains-db/
│   │   └── init/villains.sql
│   ├── locations-db/
│   │   └── init/initialize-tables.sql
│   └── fights-db/
│       └── initialize-database.js
├── services/              # Microservice implementations
│   ├── heroes/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── villains/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── locations/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   └── fights/
│       ├── Dockerfile
│       ├── main.py
│       └── requirements.txt
├── k6/                    # Load testing scripts
│   ├── randomFight.js
│   └── load.js
├── k6-image/             # Custom k6 Docker image
├── docs/                 # Documentation
├── compose.yml           # Docker Compose configuration
└── README.md
```

## Running Services Locally

### All Services with Docker Compose

```bash
# Start all services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Individual Service Development

For faster iteration during development:

#### Heroes Service

```bash
cd services/heroes

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgres://superman:superman@localhost:5432/heroes_database"

# Run service
uvicorn main:app --reload --port 8001
```

#### Villains Service

```bash
cd services/villains
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgres://superman:superman@localhost:5433/villains_database"
uvicorn main:app --reload --port 8002
```

#### Locations Service

```bash
cd services/locations
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export MYSQL_URL="mysql://locations:locations@localhost:3306/locations_database"
uvicorn main:app --reload --port 8003
```

#### Fights Service

```bash
cd services/fights
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# No database required
uvicorn main:app --reload --port 8004
```

### Hot Reload

When running with `--reload`, Uvicorn automatically restarts on code changes:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Database Management

### Access Databases

#### PostgreSQL (Heroes)

```bash
# Via Docker
docker-compose exec heroes-db psql -U superman -d heroes_database

# Via local psql
psql -h localhost -p 5432 -U superman -d heroes_database
# Password: superman
```

#### PostgreSQL (Villains)

```bash
# Via Docker
docker-compose exec villains-db psql -U superman -d villains_database

# Via local psql
psql -h localhost -p 5433 -U superman -d villains_database
```

#### MariaDB (Locations)

```bash
# Via Docker
docker-compose exec locations-db mysql -ulocations -plocations locations_database

# Via local mysql
mysql -h localhost -P 3306 -ulocations -plocations locations_database
```

#### MongoDB (Fights)

```bash
# Via Docker
docker-compose exec fights-db mongosh -u super -p super --authenticationDatabase admin

# Via local mongosh
mongosh "mongodb://super:super@localhost:27017/fights?authSource=admin"
```

### Reset Databases

```bash
# Stop and remove volumes
docker-compose down -v

# Restart (reinitializes databases)
docker-compose up -d
```

### Backup Data

```bash
# PostgreSQL backup
docker-compose exec heroes-db pg_dump -U superman heroes_database > backup.sql

# MariaDB backup
docker-compose exec locations-db mysqldump -ulocations -plocations locations_database > backup.sql

# MongoDB backup
docker-compose exec fights-db mongodump --uri="mongodb://super:super@localhost:27017/fights?authSource=admin" --out=/backup
```

## Testing

### Manual API Testing

#### Using cURL

```bash
# Test heroes service
curl http://localhost:8001/api/heroes
curl http://localhost:8001/api/heroes/1
curl http://localhost:8001/api/heroes/random_hero

# Test fights service
curl http://localhost:8004/api/fights/execute_fight
```

#### Using HTTPie

```bash
# Install httpie
pip install httpie

# Test endpoints
http GET http://localhost:8001/api/heroes
http GET http://localhost:8004/api/fights/execute_fight
```

### Load Testing

```bash
# Enter k6 container
docker-compose exec k6 bash

# Run load tests
k6 run /k6/randomFight.js
k6 run /k6/load.js

# Custom test
k6 run --vus 50 --duration 2m /k6/randomFight.js
```

### Unit Testing (Future)

Create `tests/` directory for each service:

```python
# services/heroes/tests/test_main.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_get_heroes():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/heroes")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
```

Run tests:
```bash
pytest services/heroes/tests/
```

## Code Style

### Python Standards

Follow PEP 8 with these tools:

```bash
# Install development tools
pip install black flake8 isort mypy

# Format code
black services/heroes/main.py

# Check style
flake8 services/heroes/main.py

# Sort imports
isort services/heroes/main.py

# Type checking
mypy services/heroes/main.py
```

### Configuration Files

Create `pyproject.toml` in project root:

```toml
[tool.black]
line-length = 100
target-version = ['py313']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
```

### Code Conventions

- Use async/await for all I/O operations
- Type hints for function signatures
- Docstrings for public functions
- Keep functions small and focused
- Use descriptive variable names

## Debugging

### Service Debugging

Add debug logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.get("/api/heroes")
async def get_heroes():
    logger.debug("Fetching heroes from database")
    # ... rest of code
```

### Database Query Debugging

```python
# PostgreSQL - asyncpg
async def get_hero(hero_id: int):
    query = "SELECT * FROM hero WHERE id = $1"
    print(f"Query: {query}, Params: {hero_id}")  # Debug
    result = await conn.fetchrow(query, hero_id)
    return result
```

### Using Python Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()
```

### Docker Debugging

```bash
# View service logs
docker-compose logs -f heroes

# Execute commands in container
docker-compose exec heroes bash

# Check environment variables
docker-compose exec heroes env
```

## Common Tasks

### Adding a New Endpoint

Example: Add endpoint to get heroes by level

```python
# services/heroes/main.py

@app.get("/api/heroes/by_level/{level}")
async def get_heroes_by_level(level: int):
    query = "SELECT * FROM hero WHERE level >= $1 ORDER BY level DESC"
    async with app.state.pool.acquire() as connection:
        rows = await connection.fetch(query, level)
        return [dict(row) for row in rows]
```

### Adding a New Service

1. Create service directory: `services/newservice/`
2. Create `Dockerfile`, `main.py`, `requirements.txt`
3. Add service to `compose.yml`
4. Create database initialization scripts if needed
5. Document in service README

### Modifying Database Schema

1. Edit initialization script in `database/*/init/`
2. Reset database:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

### Adding Dependencies

```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Rebuild container
docker-compose up -d --build heroes
```

### Performance Profiling

```python
# Add profiling
import cProfile
import pstats

def profile_handler():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.print_stats()
```

### Environment Variables

Create `.env` file (git-ignored):

```bash
# Database URLs
HEROES_DB_URL=postgres://superman:superman@localhost:5432/heroes_database
VILLAINS_DB_URL=postgres://superman:superman@localhost:5433/villains_database
LOCATIONS_DB_URL=mysql://locations:locations@localhost:3306/locations_database

# Service URLs
HEROES_SERVICE_URL=http://localhost:8001
VILLAINS_SERVICE_URL=http://localhost:8002
LOCATIONS_SERVICE_URL=http://localhost:8003
```

Load in Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("HEROES_DB_URL")
```

## Continuous Integration

GitHub Actions workflows in `.github/workflows/`:

- **agentics-maintenance.yml**: Automated maintenance
- **daily-perf-improver**: Performance testing
- **update-docs**: Documentation updates

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and test thoroughly
4. Commit with descriptive message
5. Push and create pull request

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Kill process or change port
uvicorn main:app --port 8005
```

### Database Connection Errors

```bash
# Check database is running
docker-compose ps

# Check connection
docker-compose exec heroes-db pg_isready -U superman

# View database logs
docker-compose logs heroes-db
```

### Import Errors

```bash
# Ensure virtual environment activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Starlette Documentation](https://www.starlette.io/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
