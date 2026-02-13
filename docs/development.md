# Development Guide

Guide for developers contributing to the Python Super Heroes project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Making Changes](#making-changes)
- [Submitting Contributions](#submitting-contributions)

## Getting Started

### Prerequisites

- **Docker** & **Docker Compose**: For running the full stack
- **Python 3.13+**: For local development
- **Git**: For version control
- **(Optional) k6**: For load testing

### Initial Setup

1. **Fork and clone the repository**:
   ``````bash
   git clone https://github.com/YOUR_USERNAME/python-super-heroes.git
   cd python-super-heroes
   ``````

2. **Start the complete system**:
   ``````bash
   docker-compose up -d
   ``````

3. **Verify all services are running**:
   ``````bash
   docker-compose ps
   
   # Expected output: All services should show "Up" status
   ``````

4. **Test the API**:
   ``````bash
   # Test heroes service
   curl http://localhost:8001/api/heroes | jq
   
   # Execute a random fight
   curl http://localhost:8004/api/fights/execute_fight | jq
   ``````

## Development Environment

### Local Development (Without Docker)

For faster iteration during development, run services locally:

#### Heroes Service

``````bash
cd services/heroes

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL (using Docker)
docker-compose up -d heroes-db

# Run service
uvicorn main:app --reload --port 8001
``````

#### Villains Service

``````bash
cd services/villains
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

docker-compose up -d villains-db

uvicorn main:app --reload --port 8002
``````

#### Locations Service

``````bash
cd services/locations
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

docker-compose up -d locations-db

uvicorn main:app --reload --port 8003
``````

#### Fights Service

``````bash
cd services/fights
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ensure other services are running
docker-compose up -d heroes villains locations fights-db

# Or run other services locally in separate terminals

uvicorn main:app --reload --port 8004
``````

### Environment Variables

Each service supports configuration via environment variables:

``````bash
# Database connection
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Service URLs (for Fights service)
HEROES_URL=http://localhost:8001
VILLAINS_URL=http://localhost:8002
LOCATIONS_URL=http://localhost:8003

# Logging
LOG_LEVEL=INFO
``````

### IDE Setup

#### VS Code

Recommended extensions:
- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **Docker** (Microsoft)
- **REST Client** (Huachao Mao)

``````json
// .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "120"],
  "editor.formatOnSave": true,
  "[python]": {
    "editor.rulers": [120]
  }
}
``````

#### PyCharm

1. Open project
2. Configure Python interpreter (Python 3.13+)
3. Enable Docker plugin
4. Set line length to 120 in Code Style

## Project Structure

``````
python-super-heroes/
├── .github/               # GitHub workflows and configurations
│   └── workflows/        # CI/CD pipelines
├── services/             # Microservices
│   ├── fights/          # Fight orchestration service
│   │   ├── main.py      # FastAPI application
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── heroes/          # Heroes CRUD service
│   ├── villains/        # Villains CRUD service
│   └── locations/       # Locations CRUD service
├── database/            # Database initialization scripts
│   ├── fights-db/       # MongoDB initialization
│   ├── heroes-db/       # PostgreSQL heroes schema + data
│   ├── villains-db/     # PostgreSQL villains schema + data
│   └── locations-db/    # MariaDB locations schema + data
├── k6/                  # Load testing
│   ├── load.js          # Load test configuration
│   └── randomFight.js   # Fight scenario
├── k6-image/            # Custom k6 Docker image
├── docs/                # Documentation
├── compose.yml          # Docker Compose configuration
└── README.md           # Project overview
``````

## Coding Standards

### Python Style Guide

Follow **PEP 8** with these specifications:

- **Line Length**: 120 characters
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Grouped and sorted (standard library, third-party, local)

### Code Formatting

Use **Black** for automatic formatting:

``````bash
# Install black
pip install black

# Format a file
black services/heroes/main.py

# Format entire service
black services/heroes/

# Check without modifying
black --check services/
``````

### Import Organization

``````python
# Standard library
import os
import logging
from typing import Optional

# Third-party
from fastapi import FastAPI, HTTPException
import httpx
import uvicorn

# Local
from .models import Hero
from .database import get_pool
``````

### Naming Conventions

- **Functions/Methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private variables**: `_leading_underscore`

### Type Hints

Always use type hints:

``````python
async def get_hero(hero_id: int) -> dict:
    """Fetch hero by ID from database."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM hero WHERE id = $1", hero_id)
    return dict(row) if row else None
``````

### Docstrings

Use Google-style docstrings:

``````python
def execute_fight(hero: dict, villain: dict) -> dict:
    """
    Execute a fight between hero and villain.
    
    Args:
        hero: Dictionary containing hero data with 'level' key
        villain: Dictionary containing villain data with 'level' key
        
    Returns:
        Dictionary with fight result including winner information
        
    Raises:
        ValueError: If hero or villain data is invalid
    """
    if hero["level"] > villain["level"]:
        return {"winner": "hero", "winnerName": hero["name"]}
    return {"winner": "villain", "winnerName": villain["name"]}
``````

### Error Handling

Use appropriate exception handling:

``````python
try:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()
except httpx.RequestError as exc:
    logger.error(f"Connection error: {exc}")
    raise HTTPException(status_code=502, detail=f"Service unavailable: {exc}")
except httpx.HTTPStatusError as exc:
    logger.error(f"HTTP error: {exc.response.status_code}")
    raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
``````

### Logging

Use structured logging:

``````python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Usage
logger.info("Fetching hero with id=%s", hero_id)
logger.warning("Database connection slow, latency=%dms", latency)
logger.error("Failed to fetch hero: %s", str(exc))
``````

## Testing

### Unit Tests

Create unit tests using `pytest`:

``````python
# tests/test_fights.py
import pytest
from main import determine_winner

def test_hero_wins_when_higher_level():
    hero = {"id": 1, "name": "Superman", "level": 95}
    villain = {"id": 2, "name": "Lex", "level": 85}
    
    result = determine_winner(hero, villain)
    
    assert result["winner"] == "hero"
    assert result["winnerName"] == "Superman"

def test_villain_wins_when_higher_level():
    hero = {"id": 1, "name": "Batman", "level": 75}
    villain = {"id": 2, "name": "Joker", "level": 85}
    
    result = determine_winner(hero, villain)
    
    assert result["winner"] == "villain"
``````

Run tests:
``````bash
# Install pytest
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with coverage
pip install pytest-cov
pytest --cov=services --cov-report=html
``````

### Integration Tests

Test API endpoints:

``````python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_list_heroes():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/heroes")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_random_hero():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/heroes/random_hero")
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "level" in data
``````

### Load Testing

See [Load Testing Guide](load-testing.md) for detailed instructions.

Quick test:
``````bash
docker-compose up -d
docker-compose run k6
``````

## Making Changes

### Branching Strategy

Use feature branches:

``````bash
# Create feature branch
git checkout -b feature/add-hero-search

# Create bugfix branch
git checkout -b fix/database-connection-leak

# Create documentation branch
git checkout -b docs/api-examples
``````

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

``````
feat: add search endpoint to heroes service
fix: resolve database connection pool exhaustion
docs: update API reference with new endpoints
refactor: extract fight logic into separate module
test: add integration tests for fights service
chore: update dependencies to latest versions
``````

Examples:
``````bash
git commit -m "feat: add pagination to heroes list endpoint"
git commit -m "fix: handle null values in villain powers field"
git commit -m "docs: add architecture diagram to README"
``````

### Making Code Changes

1. **Create a branch**:
   ``````bash
   git checkout -b feature/my-feature
   ``````

2. **Make changes** following coding standards

3. **Test locally**:
   ``````bash
   # Run unit tests
   pytest
   
   # Start services
   docker-compose up -d
   
   # Manual testing
   curl http://localhost:8001/api/heroes
   ``````

4. **Format code**:
   ``````bash
   black services/
   ``````

5. **Commit changes**:
   ``````bash
   git add .
   git commit -m "feat: description of changes"
   ``````

6. **Push to GitHub**:
   ``````bash
   git push origin feature/my-feature
   ``````

## Submitting Contributions

### Pull Request Process

1. **Update documentation** if needed
2. **Ensure tests pass**
3. **Update CHANGELOG.md** (if exists)
4. **Create Pull Request** on GitHub
5. **Fill PR template** with:
   - Description of changes
   - Testing performed
   - Related issues
   - Screenshots (if UI changes)

### PR Title Format

``````
feat: Add search functionality to heroes service
fix: Resolve connection pool leak in villains service
docs: Update API reference with new endpoints
``````

### Code Review

All contributions require code review:

- **Self-review** first
- **Address feedback** constructively
- **Keep PRs focused** (one feature/fix per PR)
- **Update based on comments**

### Continuous Integration

PRs trigger automated checks:

- ✅ Code formatting (Black)
- ✅ Unit tests (pytest)
- ✅ Integration tests
- ✅ Load tests (optional)
- ✅ Docker build

## Common Development Tasks

### Adding a New Endpoint

``````python
# services/heroes/main.py

@heroes_router.get("/api/heroes/by-power/{power}")
async def get_heroes_by_power(power: str):
    """Get heroes with specific power."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM hero WHERE powers ILIKE $1",
            f"%{power}%"
        )
    return [dict(row) for row in rows]
``````

### Adding Database Migration

``````sql
-- database/heroes-db/migrations/V2__add_team_field.sql

ALTER TABLE hero ADD COLUMN team VARCHAR(100);

UPDATE hero SET team = 'Justice League' 
WHERE name IN ('Superman', 'Batman', 'Wonder Woman');
``````

### Adding New Service

1. Create service directory: `services/newservice/`
2. Add `main.py`, `requirements.txt`, `Dockerfile`
3. Add database in `database/newservice-db/`
4. Update `compose.yml`
5. Add documentation

## Debugging

### Docker Logs

``````bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f heroes

# View last 100 lines
docker-compose logs --tail=100 fights
``````

### Database Access

``````bash
# PostgreSQL (Heroes)
docker-compose exec heroes-db psql -U superman heroes_database

# PostgreSQL (Villains)
docker-compose exec villains-db psql -U lex_luthor villains_database

# MariaDB (Locations)
docker-compose exec locations-db mysql -u location_master -p locations_database

# MongoDB (Fights)
docker-compose exec fights-db mongosh -u super -p super fights
``````

### Interactive Python Shell

``````bash
docker-compose exec heroes python

>>> import asyncpg
>>> # Test database queries
``````

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [k6 Load Testing](https://k6.io/docs/)

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/flyaruu/python-super-heroes/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flyaruu/python-super-heroes/discussions)
- **Documentation**: Check `docs/` directory

## License

See [LICENSE](../LICENSE) file for details.
