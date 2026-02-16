# Development Guide

Guide for developers working on the Python Super Heroes microservices application.

## Getting Started

### Prerequisites

- **Docker** 20.10 or later
- **Docker Compose** 2.0 or later
- **Python** 3.11+ (for local development without Docker)
- **Git**

### Initial Setup

1. **Clone the repository:**

   ``````bash
   git clone https://github.com/flyaruu/python-super-heroes.git
   cd python-super-heroes
   ``````

2. **Start all services:**

   ``````bash
   docker compose up --build
   ``````

3. **Verify services are running:**

   ``````bash
   # Check Docker containers
   docker compose ps

   # Test each service
   curl http://localhost:8001/api/heroes
   curl http://localhost:8002/api/villains/random_villain
   curl http://localhost:8003/api/locations/random_location
   curl http://localhost:8004/api/fights/execute_fight
   ``````

## Project Structure

``````
python-super-heroes/
├── services/
│   ├── heroes/
│   │   ├── main.py              # Starlette application
│   │   ├── requirements.txt     # Python dependencies
│   │   └── Dockerfile          # Container build
│   ├── villains/               # Same structure as heroes
│   ├── locations/              # Same structure, uses MariaDB
│   └── fights/                 # FastAPI orchestrator
├── database/
│   ├── heroes-db/init/         # PostgreSQL schema
│   ├── villains-db/init/       # PostgreSQL schema
│   ├── locations-db/init/      # MariaDB schema
│   └── fights-db/              # MongoDB initialization
├── k6/
│   ├── load.js                 # Load test configuration
│   └── randomFight.js          # Fight simulation
└── compose.yml                 # Docker orchestration
``````

## Service Architecture

### Heroes Service (Starlette + PostgreSQL)

**File:** `services/heroes/main.py`

Key components:
- **Framework:** Starlette (lightweight ASGI)
- **Database Driver:** asyncpg
- **Connection Pool:** min_size=10, max_size=50
- **Startup Logic:** Automatic retry with 10-second timeout

**Database Schema:**
``````sql
CREATE TABLE Hero (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    othername TEXT,
    picture TEXT,
    powers TEXT,
    level INTEGER
);
``````

**Endpoints:**
- `GET /api/heroes` - List all heroes
- `GET /api/heroes/random_hero` - Random hero
- `GET /api/heroes/{id}` - Get by ID

### Villains Service (Starlette + PostgreSQL)

**File:** `services/villains/main.py`

Identical structure to Heroes service, different data table.

**Database Schema:**
``````sql
CREATE TABLE Villain (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    othername TEXT,
    picture TEXT,
    powers TEXT,
    level INTEGER
);
``````

### Locations Service (Starlette + MariaDB)

**File:** `services/locations/main.py`

**Differences from Heroes/Villains:**
- Uses `aiomysql` instead of `asyncpg`
- MariaDB connection parsing from URL
- Different retry timeout (20 seconds)

**Database Schema:**
``````sql
CREATE TABLE Location (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    picture TEXT
);
``````

### Fights Service (FastAPI + MongoDB)

**File:** `services/fights/main.py`

**Framework:** FastAPI (full-featured async framework)

**Service Orchestration:**
The Fights service coordinates multiple HTTP calls:

``````python
async def get_hero():
    response = await client.get("http://heroes:8000/api/heroes/random_hero")
    return response.json()

async def get_villain():
    response = await client.get("http://villains:8000/api/villains/random_villain")
    return response.json()

async def get_location():
    response = await client.get("http://locations:8000/api/locations/random_location")
    return response.json()
``````

**Performance Note:** Currently uses sequential calls. Can be optimized with parallel execution using `asyncio.gather()`.

## Local Development

### Running Individual Services

**Without Docker (requires local databases):**

1. **Install dependencies:**

   ``````bash
   cd services/heroes
   pip install -r requirements.txt
   ``````

2. **Set environment variables:**

   ``````bash
   export DATABASE_URL="postgres://superman:superman@localhost:5432/heroes_database"
   ``````

3. **Run the service:**

   ``````bash
   python main.py
   # Service runs on http://localhost:8000
   ``````

### Database Access

**PostgreSQL (Heroes):**
``````bash
docker compose exec heroes-db psql -U superman -d heroes_database
``````

**PostgreSQL (Villains):**
``````bash
docker compose exec villains-db psql -U superman -d villains_database
``````

**MariaDB (Locations):**
``````bash
docker compose exec locations-db mysql -u locations -plocations locations_database
``````

**MongoDB (Fights):**
``````bash
docker compose exec fights-db mongosh -u super -p super --authenticationDatabase admin fights
``````

### Database Credentials

| Service | Type | Host | Port | Database | Username | Password |
|---------|------|------|------|----------|----------|----------|
| Heroes | PostgreSQL | localhost | 5432 | heroes_database | superman | superman |
| Villains | PostgreSQL | localhost | 5433 | villains_database | superman | superman |
| Locations | MariaDB | localhost | 3306 | locations_database | locations | locations |
| Fights | MongoDB | localhost | 27017 | fights | super | super |

## Testing

### Load Testing with k6

The project includes comprehensive k6 load tests.

**Run a specific load test:**

``````bash
# Start services
docker compose up -d

# Run 10 RPS test
docker compose exec k6 k6 run -e RAMPING_RATE=10 \
  --summary-export=/results/summary_10.json \
  /k6/load.js

# View results
docker compose exec k6 cat /results/summary_10.json
``````

**Load test stages:**
- Ramp up to target RPS over 5 seconds
- Maintain target RPS for 20 seconds
- Ramp down over 5 seconds

**Performance thresholds:**
- 95th percentile response time: <500ms
- Error rate: <0.1%
- Dropped iterations: 0

### Manual Testing

**Test individual endpoints:**

``````bash
# Heroes
curl http://localhost:8001/api/heroes | jq
curl http://localhost:8001/api/heroes/random_hero | jq

# Villains
curl http://localhost:8002/api/villains | jq
curl http://localhost:8002/api/villains/random_villain | jq

# Locations
curl http://localhost:8003/api/locations | jq
curl http://localhost:8003/api/locations/random_location | jq

# Fights
curl http://localhost:8004/api/fights/randomfighters | jq
curl http://localhost:8004/api/fights/randomlocation | jq
curl http://localhost:8004/api/fights/execute_fight | jq
``````

## Performance Optimization

### Connection Pooling

All services use connection pools to reduce database connection overhead:

**PostgreSQL (asyncpg):**
``````python
pool = await asyncpg.create_pool(
    DATABASE_URL, 
    min_size=10,  # Minimum idle connections
    max_size=50   # Maximum total connections
)
``````

**MariaDB (aiomysql):**
``````python
pool = await aiomysql.create_pool(
    minsize=1,
    maxsize=10,
    **conn_kwargs
)
``````

### Async I/O Patterns

**Sequential (current implementation):**
``````python
hero = await get_hero()
villain = await get_villain()
location = await get_location()
``````

**Parallel (optimized):**
``````python
import asyncio

hero, villain, location = await asyncio.gather(
    get_hero(),
    get_villain(),
    get_location()
)
``````

**Performance Impact:** Parallel execution can reduce total latency from ~300ms to ~100ms (assuming each call takes ~100ms).

### Database Query Optimization

**Use indexes for random selection:**
``````sql
-- Instead of: ORDER BY random()
-- Use: Indexed column with random offset
SELECT * FROM Hero OFFSET floor(random() * (SELECT count(*) FROM Hero)) LIMIT 1;
``````

**Note:** Current implementation uses `ORDER BY random()` for simplicity.

## Adding New Features

### Adding a New Endpoint

**Example: Add health check to Heroes service**

1. **Define the route handler:**

   ``````python
   async def health_check(request: Request) -> JSONResponse:
       return JSONResponse({"status": "healthy"})
   ``````

2. **Add route to routes list:**

   ``````python
   routes = [
       Route("/api/heroes", list_all, methods=["GET"]),
       Route("/health", health_check, methods=["GET"]),
       # ... other routes
   ]
   ``````

3. **Test the endpoint:**

   ``````bash
   curl http://localhost:8001/health
   ``````

### Adding a New Service

1. **Create service directory:**

   ``````bash
   mkdir -p services/new-service
   ``````

2. **Create main.py, requirements.txt, Dockerfile**

3. **Add database to compose.yml**

4. **Add service to compose.yml**

5. **Create database initialization scripts in database/new-service/**

## Troubleshooting

### Services Not Starting

**Check logs:**
``````bash
docker compose logs heroes
docker compose logs villains
docker compose logs locations
docker compose logs fights
``````

**Common issues:**
- Database not ready: Services have retry logic, wait 10-30 seconds
- Port conflicts: Check if ports 8001-8004, 5432, 5433, 3306, 27017 are available
- Build failures: Run `docker compose build --no-cache`

### Database Connection Errors

**Verify database health:**
``````bash
docker compose ps
# All databases should show "healthy" status
``````

**Reset databases:**
``````bash
docker compose down -v  # WARNING: Deletes all data
docker compose up --build
``````

### Performance Issues

**Check resource usage:**
``````bash
docker stats
``````

**Adjust connection pool sizes in service code if needed.**

## Code Style

### Python Conventions

- Follow **PEP 8** style guide
- Use **async/await** for all I/O operations
- Use **type hints** where beneficial
- Keep functions focused and single-purpose

### Example Code Style

``````python
async def get_random_item(request: Request) -> JSONResponse:
    """Fetch a random hero from the database."""
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "select * from Hero order by random() limit 1"
        )
    if not row:
        return JSONResponse({"detail": "Not found"}, status_code=404)
    return JSONResponse(dict(row))
``````

## Contributing

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/my-feature`
3. **Make changes and test thoroughly**
4. **Commit with clear messages:** `git commit -m "Add: new endpoint for hero search"`
5. **Push to your fork:** `git push origin feature/my-feature`
6. **Create a Pull Request**

## Continuous Integration

The project includes GitHub Actions workflows:

- **daily-perf-improver** - Automated performance optimization
- **update-docs** - Documentation synchronization

See `.github/workflows/` for workflow definitions.

## Resources

- **Starlette Documentation:** https://www.starlette.io/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **asyncpg Documentation:** https://magicstack.github.io/asyncpg/
- **k6 Load Testing:** https://k6.io/docs/

## Support

For questions or issues:
- Open a GitHub Issue
- Check existing GitHub Discussions
- Review documentation in the `docs/` directory
