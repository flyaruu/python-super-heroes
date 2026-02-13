# Development Guide

Guide for developers working on Python Super Heroes.

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- Git
- A code editor (VS Code, PyCharm, etc.)

## Setting Up Development Environment

### 1. Clone the Repository

``````bash
git clone https://github.com/flyaruu/python-super-heroes.git
cd python-super-heroes
``````

### 2. Start Database Services

Start only the databases for local development:

``````bash
docker compose up -d heroes-db villains-db locations-db fights-db
``````

### 3. Set Up Python Environment

Create a virtual environment for each service:

``````bash
# Heroes service
cd services/heroes
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
``````

Repeat for other services as needed.

### 4. Configure Environment Variables

Create a `.env` file in each service directory:

**Heroes Service** (`services/heroes/.env`):
``````env
DATABASE_URL=postgres://superman:superman@localhost:5432/heroes_database
``````

**Villains Service** (`services/villains/.env`):
``````env
DATABASE_URL=postgres://superman:superman@localhost:5433/villains_database
``````

**Locations Service** (`services/locations/.env`):
``````env
MYSQL_URL=mysql://locations:locations@localhost:3306/locations_database
``````

## Running Services Locally

### Individual Service

``````bash
cd services/heroes
source venv/bin/activate
python main.py
``````

The service will start on `http://localhost:8000`.

### Multiple Services

To run services on different ports simultaneously:

``````bash
# Terminal 1 - Heroes
cd services/heroes && python main.py

# Terminal 2 - Villains  
cd services/villains && python main.py

# Terminal 3 - Locations
cd services/locations && python main.py

# Terminal 4 - Fights
cd services/fights && python main.py
``````

Note: Modify port bindings in code if running multiple services locally.

## Project Structure

### Service Structure

Each service follows this pattern:

``````
services/heroes/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container build instructions
└── .env                # Local environment variables (not committed)
``````

### Main Components

**main.py** - Core application file containing:
- Database connection setup
- API route definitions
- Request handlers
- Startup/shutdown logic

## Code Style

### Async/Await Patterns

All database operations use async/await:

``````python
async def get_hero(request: Request) -> JSONResponse:
    async with app.state.pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM Hero WHERE id=$1", hero_id)
    return JSONResponse(dict(row))
``````

### Error Handling

Implement proper error handling:

``````python
try:
    response = await client.get(url)
    response.raise_for_status()
except httpx.RequestError as exc:
    raise HTTPException(status_code=502, detail=f"Connection error: {exc}")
except httpx.HTTPStatusError as exc:
    raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
``````

### Logging

Use structured logging:

``````python
import logging

logger = logging.getLogger(__name__)
logger.info(f"Fetching hero {hero_id}")
``````

## Database Migrations

### PostgreSQL (Heroes/Villains)

Initialization scripts are in `database/heroes-db/init/` and `database/villains-db/init/`.

To modify schema:
1. Update SQL files in init directory
2. Rebuild database: `docker compose down -v && docker compose up -d heroes-db`

### MariaDB (Locations)

Initialization in `database/locations-db/init/initialize-tables.sql`.

### MongoDB (Fights)

Initialization in `database/fights-db/initialize-database.js`.

## Testing

### Manual API Testing

Use curl or httpie:

``````bash
# Get all heroes
curl http://localhost:8001/api/heroes

# Get random hero
curl http://localhost:8001/api/heroes/random_hero

# Execute a fight
curl http://localhost:8004/api/fights/execute_fight
``````

### Load Testing

Run k6 tests:

``````bash
# Start all services
docker compose up -d

# Run load test
docker compose exec k6 k6 run -e RAMPING_RATE=10 /k6/load.js
``````

## Debugging

### Enable Debug Mode

Modify service code to enable debug logging:

``````python
logging.basicConfig(level=logging.DEBUG)
app = Starlette(debug=True, routes=routes)
``````

### Database Connection Issues

Check database is ready:

``````bash
# PostgreSQL
docker compose exec heroes-db pg_isready -U superman

# MariaDB
docker compose exec locations-db mysql -u locations -plocations -e "SELECT 1"

# MongoDB
docker compose exec fights-db mongosh --eval "db.runCommand({ ping: 1 })"
``````

### View Logs

``````bash
# Service logs
docker compose logs -f heroes

# Database logs  
docker compose logs -f heroes-db
``````

## Adding New Endpoints

1. Define route handler:

``````python
async def create_hero(request: Request) -> JSONResponse:
    data = await request.json()
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO Hero (name, level) VALUES ($1, $2)",
            data['name'], data['level']
        )
    return JSONResponse({"status": "created"}, status_code=201)
``````

2. Add route:

``````python
routes = [
    Route("/api/heroes", create_hero, methods=["POST"]),
    # ... existing routes
]
``````

## Performance Optimization

### Connection Pooling

Tune pool sizes based on load:

``````python
app.state.pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=5,   # Minimum connections
    max_size=20   # Maximum connections
)
``````

### Query Optimization

Use appropriate indexes and limit result sets:

``````sql
CREATE INDEX idx_hero_level ON Hero(level);
SELECT * FROM Hero WHERE level > 90 LIMIT 100;
``````

## Common Issues

### Port Already in Use

Change port in `main.py`:

``````python
uvicorn.run(app, host="0.0.0.0", port=8005)  # Use different port
``````

### Database Connection Timeout

Increase retry timeout in service code:

``````python
RETRY_TIMEOUT = 30  # Increase from 10 seconds
``````

### Module Not Found

Ensure virtual environment is activated and dependencies installed:

``````bash
source venv/bin/activate
pip install -r requirements.txt
``````

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes following code style guidelines
3. Test locally with Docker Compose
4. Commit with descriptive messages
5. Push and create Pull Request

## Useful Commands

``````bash
# Rebuild a service
docker compose build heroes

# Restart a service
docker compose restart heroes

# View service status
docker compose ps

# Clean up everything
docker compose down -v

# View database data
docker compose exec heroes-db psql -U superman -d heroes_database -c "SELECT * FROM Hero LIMIT 5"
``````
