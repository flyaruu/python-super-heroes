# Development Guide

A comprehensive guide for developers working on Python Super Heroes.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Organization](#code-organization)
- [Database Management](#database-management)
- [Testing](#testing)
- [Performance Optimization](#performance-optimization)
- [Debugging](#debugging)
- [Contributing](#contributing)

## Getting Started

### Prerequisites

- **Python**: 3.13+ (uses latest async features)
- **Docker**: 24.0+ and Docker Compose V2
- **Git**: For version control
- **curl** or **httpie**: For API testing

### Initial Setup

1. **Clone and navigate**:
   ``````bash
   git clone https://github.com/flyaruu/python-super-heroes.git
   cd python-super-heroes
   ``````

2. **Start all services**:
   ``````bash
   docker compose up -d
   ``````

3. **Verify startup**:
   ``````bash
   docker compose logs -f
   # Press Ctrl+C when all services are ready
   ``````

4. **Test the application**:
   ``````bash
   curl http://localhost:8004/api/fights/execute_fight
   ``````

## Development Environment

### Local Development (Without Docker)

For faster iteration, run services locally while databases run in containers.

#### 1. Start Databases Only

``````bash
docker compose up -d heroes-db villains-db locations-db fights-db
``````

#### 2. Set Up Python Environment

**Heroes Service**:
``````bash
cd services/heroes
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL="postgres://superman:superman@localhost:5432/heroes_database"
python main.py
``````

**Villains Service**:
``````bash
cd services/villains
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="postgres://superman:superman@localhost:5433/villains_database"
python main.py
``````

**Locations Service**:
``````bash
cd services/locations
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export MYSQL_URL="mysql://locations:locations@localhost:3306/locations_database"
python main.py
``````

**Fights Service**:
``````bash
cd services/fights
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# No database required - uses hardcoded service URLs
python main.py
``````

### IDE Configuration

#### VS Code

Recommended extensions:
- Python (Microsoft)
- Pylance
- Docker
- REST Client

**settings.json**:
``````json
{
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
``````

#### PyCharm

1. Open project root directory
2. Configure Python interpreters for each service
3. Add run configurations for each service
4. Enable Docker integration

## Code Organization

### Project Structure

``````
python-super-heroes/
├── services/              # Microservices
│   ├── heroes/
│   │   ├── main.py       # Heroes service implementation
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── villains/
│   │   ├── main.py       # Villains service implementation
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── locations/
│   │   ├── main.py       # Locations service implementation
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── fights/
│       ├── main.py       # Fights orchestration service
│       ├── requirements.txt
│       └── Dockerfile
├── database/              # Database initialization
│   ├── heroes-db/init/
│   ├── villains-db/init/
│   ├── locations-db/init/
│   └── fights-db/
├── k6/                    # Load testing scripts
│   ├── load.js
│   ├── randomFight.js
│   └── results/
├── k6-image/              # Custom k6 Docker image
├── docs/                  # Documentation
├── compose.yml            # Docker Compose configuration
└── usage_scenario.yml     # Load test scenarios
``````

### Service Architecture

All services follow a similar pattern:

1. **Startup**: Database connection with retry logic
2. **Route Definition**: RESTful endpoints
3. **Request Handlers**: Async functions for each endpoint
4. **Shutdown**: Graceful database connection cleanup

**Example Service Structure**:
``````python
import asyncpg
from starlette.applications import Starlette
from starlette.routing import Route

# 1. Startup
async def startup():
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)

# 2. Shutdown
async def shutdown():
    await app.state.pool.close()

# 3. Route Handlers
async def list_items(request):
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM items")
    return JSONResponse([dict(r) for r in rows])

# 4. Route Definition
routes = [
    Route("/api/items", list_items, methods=["GET"]),
]

# 5. Application
app = Starlette(
    routes=routes,
    on_startup=[startup],
    on_shutdown=[shutdown]
)
``````

## Database Management

### Database Schemas

#### Heroes Database (PostgreSQL)

``````sql
CREATE TABLE Hero (
  id int8 PRIMARY KEY,
  level int4 NOT NULL,
  name VARCHAR(50) NOT NULL,
  otherName VARCHAR(255),
  picture VARCHAR(255),
  powers TEXT
);
``````

#### Villains Database (PostgreSQL)

``````sql
CREATE TABLE Villain (
  id int8 PRIMARY KEY,
  level int4 NOT NULL,
  name VARCHAR(50) NOT NULL,
  otherName VARCHAR(255),
  picture VARCHAR(255),
  powers TEXT
);
``````

#### Locations Database (MySQL)

``````sql
CREATE TABLE Location (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  picture VARCHAR(255)
);
``````

### Accessing Databases

**PostgreSQL (Heroes)**:
``````bash
docker compose exec heroes-db psql -U superman -d heroes_database
``````

**PostgreSQL (Villains)**:
``````bash
docker compose exec villains-db psql -U superman -d villains_database
``````

**MySQL (Locations)**:
``````bash
docker compose exec locations-db mysql -u locations -plocations locations_database
``````

**MongoDB (Fights)**:
``````bash
docker compose exec fights-db mongosh -u super -p super --authenticationDatabase admin
``````

### Modifying Database Schema

1. **Update initialization script** in `database/{service}-db/init/`
2. **Rebuild database containers**:
   ``````bash
   docker compose down -v  # WARNING: Deletes all data
   docker compose up -d
   ``````

### Adding Test Data

Edit the SQL/JS files in `database/*/init/` and rebuild containers.

## Testing

### Manual API Testing

**Using curl**:
``````bash
# Get all heroes
curl http://localhost:8001/api/heroes

# Get random hero
curl http://localhost:8001/api/heroes/random_hero

# Execute random fight
curl http://localhost:8004/api/fights/execute_fight

# Execute custom fight
curl -X POST http://localhost:8004/api/fights \
  -H "Content-Type: application/json" \
  -d '{
    "hero": {"id": 1, "name": "Yoda", "level": 286000, "powers": "Force", "picture": ""},
    "villain": {"id": 1, "name": "Thanos", "level": 250000, "powers": "Reality", "picture": ""},
    "location": {"id": 1, "name": "Gotham"}
  }'
``````

**Using httpie**:
``````bash
http localhost:8001/api/heroes
http localhost:8004/api/fights/execute_fight
``````

### Load Testing

#### Run Single Load Test

``````bash
docker compose exec k6 k6 run -e RAMPING_RATE=10 /k6/load.js
``````

#### Customize Load Test

Edit `k6/load.js` to adjust:
- **Duration**: Change `stages` array
- **Thresholds**: Modify `thresholds` object
- **VUs**: Adjust `preAllocatedVUs` and `maxVUs`

#### Analyze Results

Results are saved to `k6/results/`:
``````bash
cat k6/results/summary_10.json | jq '.metrics'
``````

### Unit Testing

No unit tests currently exist. To add:

1. **Install pytest**:
   ``````bash
   pip install pytest pytest-asyncio httpx
   ``````

2. **Create test file** (e.g., `services/heroes/test_main.py`):
   ``````python
   import pytest
   from httpx import AsyncClient
   from main import app

   @pytest.mark.asyncio
   async def test_list_heroes():
       async with AsyncClient(app=app, base_url="http://test") as client:
           response = await client.get("/api/heroes")
       assert response.status_code == 200
       assert isinstance(response.json(), list)
   ``````

3. **Run tests**:
   ``````bash
   pytest
   ``````

## Performance Optimization

### Key Optimizations Implemented

1. **Parallel Requests** (`asyncio.gather()`):
   ``````python
   # Fetch hero, villain, location concurrently
   location, hero, villain = await asyncio.gather(
       get_location(),
       get_hero(),
       get_villain()
   )
   ``````

2. **Efficient Random Selection**:
   ``````python
   # Instead of ORDER BY RANDOM() (slow)
   max_id = await conn.fetchval("SELECT MAX(id) FROM Hero")
   random_id = random.randint(1, max_id)
   row = await conn.fetchrow("SELECT * FROM Hero WHERE id >= $1 LIMIT 1", random_id)
   ``````

3. **Connection Pooling**:
   ``````python
   # Reuse database connections
   pool = await asyncpg.create_pool(
       DATABASE_URL,
       min_size=10,
       max_size=50
   )
   ``````

4. **HTTP Client Pooling**:
   ``````python
   client = httpx.AsyncClient(
       limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
   )
   ``````

5. **Reduced Logging**:
   ``````python
   logging.basicConfig(level=logging.WARNING)
   ``````

### Profiling

#### Profile a Service

``````bash
python -m cProfile -o profile.stats main.py
``````

#### Analyze Profile

``````python
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(20)
``````

#### Memory Profiling

``````bash
pip install memory_profiler
python -m memory_profiler main.py
``````

## Debugging

### View Logs

**All services**:
``````bash
docker compose logs -f
``````

**Specific service**:
``````bash
docker compose logs -f heroes
``````

**Last 100 lines**:
``````bash
docker compose logs --tail=100 fights
``````

### Attach Debugger

1. **Add breakpoint** in code:
   ``````python
   import pdb; pdb.set_trace()
   ``````

2. **Run service interactively**:
   ``````bash
   docker compose run --rm --service-ports heroes python -m pdb main.py
   ``````

### Common Issues

#### Service won't start

**Check database health**:
``````bash
docker compose ps
# Wait until databases show "healthy"
``````

**Check logs**:
``````bash
docker compose logs heroes-db
``````

#### Connection refused errors

- Ensure service dependencies are running
- Check `depends_on` in `compose.yml`
- Verify service URLs in code match container names

#### Database connection errors

- Check credentials match environment variables
- Verify database initialization completed
- Check network connectivity between containers

## Contributing

### Code Style

- **Formatting**: Use `black` for Python code
- **Linting**: Follow `flake8` recommendations
- **Imports**: Organize with `isort`
- **Docstrings**: Use Google-style docstrings

### Commit Guidelines

- Use conventional commits: `feat:`, `fix:`, `docs:`, `perf:`
- Keep commits focused and atomic
- Write descriptive commit messages

### Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feat/your-feature`
3. Make targeted changes
4. Test locally
5. Commit with descriptive message
6. Push and create pull request
7. Respond to review feedback

### Testing Checklist

Before submitting PR:
- [ ] All services build successfully
- [ ] All services start without errors
- [ ] API endpoints return expected responses
- [ ] No regressions in existing functionality
- [ ] Load tests pass with acceptable performance

## Additional Resources

- **Starlette Documentation**: https://www.starlette.io/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **asyncpg Documentation**: https://magicstack.github.io/asyncpg/
- **k6 Documentation**: https://k6.io/docs/
- **Docker Compose Documentation**: https://docs.docker.com/compose/
