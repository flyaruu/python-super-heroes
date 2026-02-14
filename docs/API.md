# API Reference

Complete API documentation for the Python Super Heroes microservices.

## Overview

The Python Super Heroes application exposes RESTful HTTP APIs across four microservices. All endpoints return JSON responses.

## Base URLs

When running locally with Docker Compose:

- **Fights Service**: `http://localhost:8004`
- **Heroes Service**: `http://localhost:8001`
- **Villains Service**: `http://localhost:8002`
- **Locations Service**: `http://localhost:8003`

## Fights Service

The Fights service orchestrates battles by coordinating calls to the Heroes, Villains, and Locations services.

### Get Random Fighters

Fetch a random hero and villain for a battle.

**Endpoint:** `GET /api/fights/randomfighters`

**Response:**
``````json
{
  "hero": {
    "id": 1,
    "name": "Superman",
    "otherName": "Clark Kent",
    "picture": "https://example.com/superman.jpg",
    "powers": "Flight, Super Strength, Heat Vision",
    "level": 15
  },
  "villain": {
    "id": 5,
    "name": "Lex Luthor",
    "otherName": "Alexander Luthor",
    "picture": "https://example.com/lex.jpg",
    "powers": "Genius Intellect, Wealth",
    "level": 12
  }
}
``````

**Example:**
``````bash
curl http://localhost:8004/api/fights/randomfighters
``````

### Get Random Location

Fetch a random location for a battle.

**Endpoint:** `GET /api/fights/randomlocation`

**Response:**
``````json
{
  "id": 3,
  "name": "Metropolis",
  "description": "Home city of Superman",
  "picture": "https://example.com/metropolis.jpg"
}
``````

**Example:**
``````bash
curl http://localhost:8004/api/fights/randomlocation
``````

### Execute Random Fight

Execute a complete random fight by fetching a hero, villain, and location, then determining the winner.

**Endpoint:** `GET /api/fights/execute_fight`

**Response:**
``````json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "fight_date": "2023-10-01T12:00:00Z",
  "winner_name": "Superman",
  "winner_level": 15,
  "winner_powers": "Flight, Super Strength, Heat Vision",
  "winner_picture": "https://example.com/superman.jpg",
  "loser_name": "Lex Luthor",
  "loser_level": 12,
  "loser_powers": "Genius Intellect, Wealth",
  "loser_picture": "https://example.com/lex.jpg",
  "winner_team": "heroes",
  "loser_team": "villains",
  "hero": { ... },
  "villain": { ... },
  "location": { ... }
}
``````

**Fight Logic:**
- Winner is determined by comparing `level` values
- Higher level wins the battle
- Response includes complete hero, villain, and location details

**Example:**
``````bash
curl http://localhost:8004/api/fights/execute_fight
``````

### Create Custom Fight

Create a fight with specific hero, villain, and location.

**Endpoint:** `POST /api/fights`

**Request Body:**
``````json
{
  "hero": {
    "id": 1,
    "name": "Superman",
    "otherName": "Clark Kent",
    "level": 15,
    "powers": "Flight, Super Strength",
    "picture": "https://example.com/superman.jpg"
  },
  "villain": {
    "id": 5,
    "name": "Lex Luthor",
    "otherName": "Alexander Luthor",
    "level": 12,
    "powers": "Genius Intellect",
    "picture": "https://example.com/lex.jpg"
  },
  "location": {
    "id": 3,
    "name": "Metropolis",
    "description": "Home city of Superman",
    "picture": "https://example.com/metropolis.jpg"
  }
}
``````

**Response:**
Same format as Execute Random Fight endpoint.

**Example:**
``````bash
curl -X POST http://localhost:8004/api/fights \
  -H "Content-Type: application/json" \
  -d '{
    "hero": {"id": 1, "name": "Superman", "level": 15, "powers": "Flight", "picture": ""},
    "villain": {"id": 5, "name": "Lex Luthor", "level": 12, "powers": "Intellect", "picture": ""},
    "location": {"id": 3, "name": "Metropolis", "description": "City", "picture": ""}
  }'
``````

## Heroes Service

Manages hero data stored in PostgreSQL.

### List All Heroes

Retrieve all heroes from the database.

**Endpoint:** `GET /api/heroes`

**Response:**
``````json
[
  {
    "id": 1,
    "name": "Superman",
    "otherName": "Clark Kent",
    "picture": "https://example.com/superman.jpg",
    "powers": "Flight, Super Strength, Heat Vision",
    "level": 15
  },
  {
    "id": 2,
    "name": "Batman",
    "otherName": "Bruce Wayne",
    "picture": "https://example.com/batman.jpg",
    "powers": "Intelligence, Martial Arts, Gadgets",
    "level": 12
  }
]
``````

**Example:**
``````bash
curl http://localhost:8001/api/heroes
``````

### Get Random Hero

Retrieve a single random hero.

**Endpoint:** `GET /api/heroes/random_hero`

**Response:**
``````json
{
  "id": 1,
  "name": "Superman",
  "otherName": "Clark Kent",
  "picture": "https://example.com/superman.jpg",
  "powers": "Flight, Super Strength, Heat Vision",
  "level": 15
}
``````

**Example:**
``````bash
curl http://localhost:8001/api/heroes/random_hero
``````

### Get Hero by ID

Retrieve a specific hero by their ID.

**Endpoint:** `GET /api/heroes/{id}`

**Path Parameters:**
- `id` (integer) - Hero ID

**Response:**
``````json
{
  "id": 1,
  "name": "Superman",
  "otherName": "Clark Kent",
  "picture": "https://example.com/superman.jpg",
  "powers": "Flight, Super Strength, Heat Vision",
  "level": 15
}
``````

**Error Response (404):**
``````json
{
  "detail": "Not found"
}
``````

**Example:**
``````bash
curl http://localhost:8001/api/heroes/1
``````

## Villains Service

Manages villain data stored in PostgreSQL.

### List All Villains

Retrieve all villains from the database.

**Endpoint:** `GET /api/villains`

**Response:**
``````json
[
  {
    "id": 1,
    "name": "Lex Luthor",
    "otherName": "Alexander Luthor",
    "picture": "https://example.com/lex.jpg",
    "powers": "Genius Intellect, Wealth",
    "level": 12
  }
]
``````

**Example:**
``````bash
curl http://localhost:8002/api/villains
``````

### Get Random Villain

Retrieve a single random villain.

**Endpoint:** `GET /api/villains/random_villain`

**Response:**
``````json
{
  "id": 1,
  "name": "Lex Luthor",
  "otherName": "Alexander Luthor",
  "picture": "https://example.com/lex.jpg",
  "powers": "Genius Intellect, Wealth",
  "level": 12
}
``````

**Example:**
``````bash
curl http://localhost:8002/api/villains/random_villain
``````

### Get Villain by ID

Retrieve a specific villain by their ID.

**Endpoint:** `GET /api/villains/{id}`

**Path Parameters:**
- `id` (integer) - Villain ID

**Response:**
``````json
{
  "id": 1,
  "name": "Lex Luthor",
  "otherName": "Alexander Luthor",
  "picture": "https://example.com/lex.jpg",
  "powers": "Genius Intellect, Wealth",
  "level": 12
}
``````

**Error Response (404):**
``````json
{
  "detail": "Not found"
}
``````

**Example:**
``````bash
curl http://localhost:8002/api/villains/1
``````

## Locations Service

Manages fight location data stored in MariaDB.

### List All Locations

Retrieve all locations from the database.

**Endpoint:** `GET /api/locations`

**Response:**
``````json
[
  {
    "id": 1,
    "name": "Metropolis",
    "description": "Home city of Superman",
    "picture": "https://example.com/metropolis.jpg"
  },
  {
    "id": 2,
    "name": "Gotham City",
    "description": "Dark city protected by Batman",
    "picture": "https://example.com/gotham.jpg"
  }
]
``````

**Example:**
``````bash
curl http://localhost:8003/api/locations
``````

### Get Random Location

Retrieve a single random location.

**Endpoint:** `GET /api/locations/random_location`

**Response:**
``````json
{
  "id": 1,
  "name": "Metropolis",
  "description": "Home city of Superman",
  "picture": "https://example.com/metropolis.jpg"
}
``````

**Example:**
``````bash
curl http://localhost:8003/api/locations/random_location
``````

### Get Location by ID

Retrieve a specific location by its ID.

**Endpoint:** `GET /api/locations/{id}`

**Path Parameters:**
- `id` (integer) - Location ID

**Response:**
``````json
{
  "id": 1,
  "name": "Metropolis",
  "description": "Home city of Superman",
  "picture": "https://example.com/metropolis.jpg"
}
``````

**Error Response (404):**
``````json
{
  "detail": "Not found"
}
``````

**Example:**
``````bash
curl http://localhost:8003/api/locations/1
``````

## Error Handling

### Standard Error Responses

All services follow consistent error response patterns:

**404 Not Found:**
``````json
{
  "detail": "Not found"
}
``````

**502 Bad Gateway (Fights Service):**
When the Fights service cannot reach dependent services:
``````json
{
  "detail": "Error connecting to external service: <error details>"
}
``````

### HTTP Status Codes

- `200 OK` - Request successful
- `404 Not Found` - Resource not found
- `502 Bad Gateway` - Upstream service unavailable (Fights service only)

## Data Models

### Hero/Villain Schema

``````json
{
  "id": "integer",
  "name": "string",
  "otherName": "string",
  "picture": "string (URL)",
  "powers": "string",
  "level": "integer"
}
``````

**Note:** The database stores `othername` (lowercase), but the API returns `otherName` (camelCase).

### Location Schema

``````json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "picture": "string (URL)"
}
``````

### Fight Result Schema

``````json
{
  "id": "string (UUID)",
  "fight_date": "string (ISO 8601 timestamp)",
  "winner_name": "string",
  "winner_level": "integer",
  "winner_powers": "string",
  "winner_picture": "string (URL)",
  "loser_name": "string",
  "loser_level": "integer",
  "loser_powers": "string",
  "loser_picture": "string (URL)",
  "winner_team": "string ('heroes' or 'villains')",
  "loser_team": "string ('heroes' or 'villains')",
  "hero": "Hero object",
  "villain": "Villain object",
  "location": "Location object"
}
``````

## Performance Considerations

### Connection Pooling

All services use database connection pools:
- **Min connections:** 10
- **Max connections:** 50 (PostgreSQL services), 10 (Locations service)

### Async I/O

All services leverage async/await patterns:
- **Heroes/Villains:** asyncpg (async PostgreSQL driver)
- **Locations:** aiomysql (async MySQL driver)
- **Fights:** httpx (async HTTP client)

### Service Communication

The Fights service makes HTTP calls to dependent services. For optimal performance:
- Calls can be parallelized using `asyncio.gather()` instead of sequential awaits
- Connection pooling reduces overhead for service-to-service communication

## Testing with curl

### Complete Fight Flow

``````bash
# 1. Get random fighters
curl http://localhost:8004/api/fights/randomfighters

# 2. Get random location
curl http://localhost:8004/api/fights/randomlocation

# 3. Execute complete fight
curl http://localhost:8004/api/fights/execute_fight

# 4. Direct service access
curl http://localhost:8001/api/heroes/random_hero
curl http://localhost:8002/api/villains/random_villain
curl http://localhost:8003/api/locations/random_location
``````

## Integration Notes

### Database Initialization

Services automatically create tables if they don't exist during startup. Initial data is loaded from SQL/JavaScript scripts in the `database/` directory.

### Retry Logic

Services include connection retry logic with configurable timeouts:
- **PostgreSQL services:** 10-second timeout with 0.5-second retry intervals
- **Locations service:** 20-second timeout with 0.5-second retry intervals

### Health Checks

Database containers include health checks in `compose.yml`:
- PostgreSQL: `pg_isready` command
- MariaDB: `healthcheck.sh --connect --innodb_initialized`
- Services wait for database readiness before starting
