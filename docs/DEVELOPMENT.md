# Development Guide

Complete guide for local development, debugging, and extending the Python Super Heroes application.

## Prerequisites

### Required Software

- **Docker**: 20.10 or later
- **Docker Compose**: 2.0 or later
- **Python**: 3.11+ (for local development without Docker)
- **Git**: 2.30+

### Optional Tools

- **curl**: For API testing
- **jq**: For JSON parsing
- **httpie**: Alternative to curl
- **Postman**: API testing GUI

## Initial Setup

### 1. Clone Repository

``````bash
git clone https://github.com/flyaruu/python-super-heroes.git
cd python-super-heroes
``````

### 2. Start Services

``````bash
# Start all services in background
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f heroes
``````

### 3. Verify Services

``````bash
# Check service health
docker-compose ps

# Test heroes service
curl http://localhost:8001/api/heroes/random_hero

# Test villains service
curl http://localhost:8002/api/villains/random_villain

# Test locations service
curl http://localhost:8003/api/locations/random_location

# Test fights service
curl http://localhost:8004/api/fights/execute_fight
``````

## Development Workflow

### Running Individual Services

Each service can be run independently for development:

**Heroes Service:**
``````bash
cd services/heroes

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgres://superman:superman@localhost:5432/heroes_database"

# Run service
python main.py
``````

**Villains Service:**
``````bash
cd services/villains
pip install -r requirements.txt
export DATABASE_URL="postgres://superman:superman@localhost:5433/villains_database"
python main.py
``````

**Locations Service:**
``````bash
cd services/locations
pip install -r requirements.txt
export MYSQL_URL="mysql://locations:locations@localhost:3306/locations_database"
python main.py
``````

**Fights Service:**
``````bash
cd services/fights
pip install -r requirements.txt
python main.py
``````

### Hot Reload Development

Mount your local code into containers for live updates:

``````yaml
# Add to docker-compose.yml
services:
  heroes:
    volumes:
      - ./services/heroes:/app
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--reload"]
``````

Then:
``````bash
docker-compose up heroes
``````

Now code changes automatically reload the service.

### Database Management

#### Access PostgreSQL (Heroes/Villains)

``````bash
# Heroes database
docker-compose exec heroes-db psql -U superman -d heroes_database

# Villains database
docker-compose exec villains-db psql -U superman -d villains_database

# Example queries
SELECT COUNT(*) FROM Hero;
SELECT name, level FROM Hero ORDER BY level DESC LIMIT 10;
``````

#### Access MariaDB (Locations)

``````bash
# Locations database
docker-compose exec locations-db mysql -u locations -plocations locations_database

# Example queries
SELECT COUNT(*) FROM Location;
SELECT name FROM Location LIMIT 10;
``````

#### Access MongoDB (Fights)

``````bash
# MongoDB shell
docker-compose exec fights-db mongosh -u super -p super fights

# Example queries
db.fights.find().limit(5)
db.fights.countDocuments()
``````

#### Reset Databases

``````bash
# Stop all services
docker-compose down

# Remove volumes (deletes data)
docker-compose down -v

# Restart (re-initializes databases)
docker-compose up -d
``````

### Adding New Heroes/Villains/Locations

Edit the initialization SQL files:

**Heroes:**
``````bash
vim database/heroes-db/init/heroes.sql
``````

Add INSERT statements:
``````sql
INSERT INTO hero(id, name, otherName, picture, powers, level)
VALUES (nextval('hero_seq'), 'New Hero', 'Alias', 'url', 'Powers', 100);
``````

**Villains:**
``````bash
vim database/villains-db/init/villains.sql
``````

**Locations:**
``````bash
vim database/locations-db/init/initialize-tables.sql
``````

Then reset databases to apply changes.

## Debugging

### Service Logs

``````bash
# All services
docker-compose logs -f

# Specific service with timestamps
docker-compose logs -f --timestamps fights

# Last 100 lines
docker-compose logs --tail=100 heroes
``````

### Python Debugging

Add breakpoints with pdb:

``````python
# In service code
import pdb; pdb.set_trace()
``````

Run service in foreground:
``````bash
docker-compose run --service-ports heroes
``````

### Network Debugging

``````bash
# Inspect network
docker network inspect python-super-heroes_default

# Check service connectivity
docker-compose exec fights ping heroes
docker-compose exec fights curl http://heroes:8000/api/heroes/random_hero
``````

### Database Connection Issues

**Check database is ready:**
``````bash
# PostgreSQL
docker-compose exec heroes-db pg_isready -U superman

# MariaDB
docker-compose exec locations-db mysqladmin ping -u locations -plocations

# MongoDB
docker-compose exec fights-db mongosh --eval "db.adminCommand('ping')" -u super -p super
``````

**Connection pool issues:**

Increase pool size in service code:
``````python
# services/heroes/main.py
pool = await asyncpg.create_pool(
    DATABASE_URL, 
    min_size=20,  # Increase from 10
    max_size=100  # Increase from 50
)
``````

## Adding New Features

### Add New Endpoint

**1. Define route in service:**
``````python
# services/heroes/main.py

async def get_hero_by_name(request: Request) -> JSONResponse:
    name = request.path_params["name"]
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM Hero WHERE name ILIKE $1",
            f"%{name}%"
        )
    if not row:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return JSONResponse(dict(row))

# Add to routes list
routes = [
    # ... existing routes
    Route("/api/heroes/search/{name}", get_hero_by_name, methods=["GET"]),
]
``````

**2. Test endpoint:**
``````bash
curl http://localhost:8001/api/heroes/search/spider
``````

**3. Document in API.md**

### Add New Service

**1. Create service directory:**
``````bash
mkdir -p services/new-service
cd services/new-service
``````

**2. Create main.py:**
``````python
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import uvicorn

async def hello(request):
    return JSONResponse({"message": "Hello from new service"})

routes = [Route("/", hello, methods=["GET"])]
app = Starlette(debug=False, routes=routes)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
``````

**3. Create requirements.txt:**
``````
starlette==0.35.1
uvicorn==0.25.0
``````

**4. Create Dockerfile:**
``````dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
``````

**5. Add to docker-compose.yml:**
``````yaml
services:
  new-service:
    build:
      context: services/new-service
    ports:
      - "8005:8000"
``````

**6. Test:**
``````bash
docker-compose up new-service
curl http://localhost:8005/
``````

## Code Standards

### Python Style

Follow PEP 8 with these guidelines:

- **Line length**: 100 characters
- **Imports**: Grouped (stdlib, third-party, local)
- **Docstrings**: Google style
- **Type hints**: Encouraged for function signatures

### Linting

``````bash
# Install tools
pip install black flake8 mypy

# Format code
black services/heroes/main.py

# Check style
flake8 services/heroes/main.py

# Type check
mypy services/heroes/main.py
``````

### Git Workflow

``````bash
# Create feature branch
git checkout -b feature/new-endpoint

# Make changes, commit
git add .
git commit -m "feat: add hero search endpoint"

# Push and create PR
git push origin feature/new-endpoint
``````

**Commit message format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code refactoring
- `test:` Tests
- `chore:` Maintenance

## Performance Optimization

### Database Query Optimization

**Use indexes:**
``````sql
CREATE INDEX idx_hero_name ON Hero(name);
CREATE INDEX idx_hero_level ON Hero(level);
``````

**Limit result sets:**
``````python
# Bad
rows = await conn.fetch("SELECT * FROM Hero")

# Good
rows = await conn.fetch("SELECT * FROM Hero LIMIT 100")
``````

### Connection Pool Tuning

Monitor pool usage:
``````python
import logging
logging.basicConfig(level=logging.DEBUG)
``````

Adjust based on load:
``````python
# Low traffic
pool = await asyncpg.create_pool(min_size=5, max_size=20)

# High traffic
pool = await asyncpg.create_pool(min_size=20, max_size=100)
``````

### Caching

Add Redis for caching:

``````yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
``````

``````python
# In service
import aioredis

redis = await aioredis.create_redis_pool('redis://redis:6379')

# Cache random hero
cached = await redis.get('random_hero')
if cached:
    return JSONResponse(json.loads(cached))

# ... fetch from DB
await redis.setex('random_hero', 60, json.dumps(hero))
``````

## Testing

### Unit Tests

``````python
# services/heroes/test_main.py
import pytest
from starlette.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_hero(client):
    response = client.get("/api/heroes/1")
    assert response.status_code == 200
    assert "name" in response.json()
``````

Run tests:
``````bash
pip install pytest pytest-asyncio
pytest services/heroes/test_main.py
``````

### Integration Tests

``````bash
# Start services
docker-compose up -d

# Run integration tests
python tests/integration_test.py
``````

### Load Testing

See [TESTING.md](TESTING.md) for comprehensive load testing guide.

## Troubleshooting

### Service Won't Start

**Check logs:**
``````bash
docker-compose logs heroes
``````

**Common issues:**
- Database not ready → Increase `RETRY_TIMEOUT`
- Port already in use → Change port in `compose.yml`
- Import error → Check `requirements.txt`

### Database Connection Errors

**PostgreSQL connection refused:**
``````bash
# Check database is running
docker-compose ps heroes-db

# Check connectivity
docker-compose exec heroes ping heroes-db
``````

**Connection pool exhausted:**
- Increase `max_size` in pool configuration
- Check for connection leaks (missing `pool.close()`)

### Performance Issues

**High latency:**
- Check database query performance
- Review connection pool settings
- Monitor service logs for errors

**Memory issues:**
- Reduce pool sizes
- Check for memory leaks
- Monitor with `docker stats`

## Environment Variables

### Heroes Service
- `DATABASE_URL`: PostgreSQL connection string (default: `postgres://superman:superman@heroes-db:5432/heroes_database`)

### Villains Service
- `DATABASE_URL`: PostgreSQL connection string (default: `postgres://superman:superman@villains-db:5432/villains_database`)

### Locations Service
- `MYSQL_URL`: MySQL connection string (default: `mysql://locations:locations@locations-db/locations_database`)

### Fights Service
- `K6_HOST`: Used by K6 tests (default: `http://fights:8000`)

## Resources

- [Starlette Documentation](https://www.starlette.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [aiomysql Documentation](https://aiomysql.readthedocs.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
