# Fights Service

The Fights Service orchestrates battles between heroes and villains at random locations. It acts as the main aggregation service, calling the Heroes, Villains, and Locations services.

## Technical Details

- **Framework**: FastAPI
- **Database**: MongoDB 7.0
- **Port**: 8000 (container) / 8004 (host)
- **Language**: Python 3.13

## Architecture

The Fights Service is an **aggregator service** that:
1. Fetches random heroes from the Heroes Service
2. Fetches random villains from the Villains Service
3. Fetches random locations from the Locations Service
4. Executes fight logic based on character levels
5. Returns fight results

## API Endpoints

### GET /api/fights/randomfighters

Fetches a random hero and villain for a potential fight.

**Response**:
``````json
{
  "hero": {
    "id": 1,
    "name": "Yoda",
    "level": 286000,
    "powers": "...",
    "picture": "https://..."
  },
  "villain": {
    "id": 42,
    "name": "Thanos",
    "level": 95000,
    "powers": "...",
    "picture": "https://..."
  }
}
``````

### GET /api/fights/randomlocation

Fetches a random fight location.

**Response**:
``````json
{
  "id": 15,
  "name": "Metropolis",
  "description": "A shining city of tomorrow",
  "picture": "https://..."
}
``````

### GET /api/fights/execute_fight

Executes a random fight between a hero and villain at a random location.

**Response**:
``````json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "fight_date": "2023-10-01T12:00:00Z",
  "winner_name": "Yoda",
  "winner_level": 286000,
  "winner_powers": "Acrobatics, Agility, ...",
  "winner_picture": "https://...",
  "winner_team": "heroes",
  "loser_name": "Thanos",
  "loser_level": 95000,
  "loser_powers": "Super Strength, ...",
  "loser_picture": "https://...",
  "loser_team": "villains",
  "hero": { ... },
  "villain": { ... },
  "location": { ... }
}
``````

### POST /api/fights

Creates a custom fight with specified hero, villain, and location.

**Request Body**:
``````json
{
  "hero": {
    "id": 1,
    "name": "Superman",
    "level": 100000,
    "powers": "...",
    "picture": "https://..."
  },
  "villain": {
    "id": 2,
    "name": "Lex Luthor",
    "level": 5000,
    "powers": "...",
    "picture": "https://..."
  },
  "location": {
    "id": 3,
    "name": "Metropolis",
    "description": "...",
    "picture": "https://..."
  }
}
``````

**Response**: Same as `/api/fights/execute_fight`

## Fight Logic

The winner is determined by comparing character levels:
- **Winner**: Character with higher level
- **Draw**: If levels are equal (uses hero as tiebreaker)

The response includes:
- Unique fight ID (UUID)
- Winner and loser details
- Complete hero, villain, and location information
- Team affiliation (heroes/villains)

## Service Dependencies

The Fights Service makes HTTP calls to:
- `http://heroes:8000/api/heroes/random_hero`
- `http://villains:8000/api/villains/random_villain`
- `http://locations:8000/api/locations/random_location`

## Configuration

The service uses hardcoded internal service URLs for Docker Compose networking:
- Heroes Service: `http://heroes:8000`
- Villains Service: `http://villains:8000`
- Locations Service: `http://locations:8000`

## HTTP Client

Uses `httpx.AsyncClient` for non-blocking HTTP requests with:
- Automatic connection pooling
- Proper lifecycle management (startup/shutdown)
- Comprehensive error handling

### Error Handling

The service handles two types of errors:

1. **Connection Errors** (`httpx.RequestError`):
   - Returns 502 Bad Gateway
   - Indicates downstream service is unreachable

2. **HTTP Status Errors** (`httpx.HTTPStatusError`):
   - Returns the original status code
   - Passes through error details from downstream service

## Logging

Structured logging is configured for all operations:
- Service startup/shutdown
- Each API endpoint call
- Fight executions with participant details

**Log Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

## Running Locally

Using Docker Compose:
``````bash
docker compose up fights
``````

Standalone (requires other services running):
``````bash
cd services/fights
pip install -r requirements.txt
python main.py
``````

## Dependencies

See `requirements.txt`:
- `fastapi` - Modern web framework
- `httpx` - Async HTTP client
- `uvicorn` - ASGI server
- Python 3.13 standard library

## Database Usage

Currently, the service connects to MongoDB but doesn't persist fight results. This could be extended to:
- Store fight history
- Track win/loss statistics
- Enable fight replay functionality
- Implement leaderboards

## Design Patterns

This service demonstrates several microservices patterns:
- **API Gateway/Aggregator**: Combines multiple service calls
- **Service Mesh**: Inter-service communication
- **Resilience**: Error handling and graceful degradation
- **Async I/O**: Non-blocking concurrent requests
