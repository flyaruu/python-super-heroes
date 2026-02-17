# Fights Service

Orchestration service that simulates superhero battles by aggregating data from Heroes, Villains, and Locations services.

## Technology

- **Framework**: FastAPI (with automatic OpenAPI documentation)
- **HTTP Client**: httpx for async service-to-service communication
- **Server**: Uvicorn ASGI server
- **Port**: 8004
- **Architecture**: Stateless orchestrator (no persistent database)

## API Endpoints

### GET /api/fights/randomfighters

Fetches a random hero and random villain in parallel.

**Response**:
```json
{
  "hero": { "id": 1, "name": "Superman", ... },
  "villain": { "id": 2, "name": "Lex Luthor", ... }
}
```

**Service Calls**:
- `GET http://heroes:8000/api/heroes/random_hero`
- `GET http://villains:8000/api/villains/random_villain`

### GET /api/fights/randomlocation

Fetches a random battle location.

**Response**:
```json
{
  "id": 5,
  "name": "Metropolis",
  "description": "...",
  "picture": "..."
}
```

**Service Calls**:
- `GET http://locations:8000/api/locations/random_location`

### POST /api/fights

Creates a fight scenario with provided fighters and location.

**Request Body**:
```json
{
  "hero": { "id": 1, "name": "Superman", "level": 95 },
  "villain": { "id": 2, "name": "Lex Luthor", "level": 85 },
  "location": { "id": 3, "name": "Metropolis" }
}
```

**Response**:
```json
{
  "fight": {
    "hero": { ... },
    "villain": { ... },
    "location": { ... },
    "winner": "hero",
    "loser": "villain"
  }
}
```

**Logic**: Compares hero and villain levels to determine winner.

### GET /api/fights/execute_fight

Executes a complete random fight by:
1. Fetching random hero and villain (parallel)
2. Fetching random location
3. Determining winner based on level comparison

**Response**: Complete fight result with winner/loser designation

**Service Calls**:
- Parallel: Heroes and Villains services
- Sequential: Locations service

## Service Dependencies

The Fights service relies on three other microservices:

- **Heroes Service** (http://heroes:8000)
- **Villains Service** (http://villains:8000)
- **Locations Service** (http://locations:8000)

## Running Locally

```bash
cd services/fights

# Install dependencies
pip install -r requirements.txt

# Ensure dependent services are accessible
# Default: heroes:8000, villains:8000, locations:8000

# Run the service
uvicorn main:app --reload --port 8004
```

## Docker

```bash
# Build
docker build -t fights-service services/fights

# Run (requires network access to other services)
docker run -p 8004:8000 fights-service
```

## Dependencies

```
fastapi==0.115.6
uvicorn==0.34.0
httpx==0.28.1
```

## OpenAPI Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8004/docs
- **ReDoc**: http://localhost:8004/redoc
- **OpenAPI JSON**: http://localhost:8004/openapi.json

## Architecture Notes

- **Stateless Design**: No database persistence; acts as API gateway
- **Async HTTP**: Uses httpx for non-blocking service calls
- **Parallel Requests**: Fetches hero and villain simultaneously using `asyncio.gather()`
- **Error Handling**: Propagates errors from downstream services

## Performance Considerations

This service is designed for high throughput:
- Async request handling
- Parallel service calls where possible
- No database I/O overhead
- Suitable for load testing and benchmarking

See `/k6` directory for load testing scripts.
