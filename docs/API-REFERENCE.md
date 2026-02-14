# API Reference

Complete API documentation for Python Super Heroes microservices.

## Table of Contents

- [Heroes Service API](#heroes-service-api)
- [Villains Service API](#villains-service-api)
- [Locations Service API](#locations-service-api)
- [Fights Service API](#fights-service-api)
- [Data Models](#data-models)
- [Error Handling](#error-handling)

## Heroes Service API

**Base URL**: `http://localhost:8001`

### List All Heroes

Retrieves all heroes from the database.

**Endpoint**: `GET /api/heroes`

**Response**: `200 OK`

``````json
[
  {
    "id": 1,
    "name": "Chewbacca",
    "otherName": "",
    "picture": "https://...",
    "powers": "Super Strength, Agility, Animal Attributes",
    "level": 30
  },
  {
    "id": 51,
    "name": "Yoda",
    "otherName": "",
    "picture": "https://...",
    "powers": "Force Manipulation, Telekinesis, Telepathy",
    "level": 286000
  }
]
``````

**Example**:
``````bash
curl http://localhost:8001/api/heroes
``````

### Get Hero by ID

Retrieves a specific hero by their unique identifier.

**Endpoint**: `GET /api/heroes/{id}`

**Path Parameters**:
- `id` (integer, required): The hero's unique identifier

**Response**: `200 OK` | `404 Not Found`

``````json
{
  "id": 1,
  "name": "Chewbacca",
  "otherName": "",
  "picture": "https://raw.githubusercontent.com/...",
  "powers": "Super Strength, Agility, Animal Attributes, Jaw Strength",
  "level": 30
}
``````

**Example**:
``````bash
curl http://localhost:8001/api/heroes/1
``````

### Get Random Hero

Returns a randomly selected hero for battle matchmaking. Uses energy-efficient selection algorithm.

**Endpoint**: `GET /api/heroes/random_hero`

**Response**: `200 OK` | `404 Not Found`

``````json
{
  "id": 51,
  "name": "Yoda",
  "otherName": "",
  "picture": "https://raw.githubusercontent.com/...",
  "powers": "Acrobatics, Agility, Force Manipulation",
  "level": 286000
}
``````

**Algorithm**: Uses `MAX(id)` to determine range, then random selection with `LIMIT 1` instead of `ORDER BY RANDOM()` for better performance.

**Example**:
``````bash
curl http://localhost:8001/api/heroes/random_hero
``````

---

## Villains Service API

**Base URL**: `http://localhost:8002`

### List All Villains

Retrieves all villains from the database.

**Endpoint**: `GET /api/villains`

**Response**: `200 OK`

``````json
[
  {
    "id": 1,
    "name": "Thanos",
    "otherName": "The Mad Titan",
    "picture": "https://...",
    "powers": "Super Strength, Reality Manipulation, Energy Projection",
    "level": 250000
  }
]
``````

**Example**:
``````bash
curl http://localhost:8002/api/villains
``````

### Get Villain by ID

Retrieves a specific villain by their unique identifier.

**Endpoint**: `GET /api/villains/{id}`

**Path Parameters**:
- `id` (integer, required): The villain's unique identifier

**Response**: `200 OK` | `404 Not Found`

``````json
{
  "id": 1,
  "name": "Thanos",
  "otherName": "The Mad Titan",
  "picture": "https://...",
  "powers": "Super Strength, Reality Manipulation",
  "level": 250000
}
``````

**Example**:
``````bash
curl http://localhost:8002/api/villains/1
``````

### Get Random Villain

Returns a randomly selected villain for battle matchmaking.

**Endpoint**: `GET /api/villains/random_villain`

**Response**: `200 OK` | `404 Not Found`

``````json
{
  "id": 1,
  "name": "Thanos",
  "otherName": "The Mad Titan",
  "picture": "https://...",
  "powers": "Super Strength, Reality Manipulation",
  "level": 250000
}
``````

**Example**:
``````bash
curl http://localhost:8002/api/villains/random_villain
``````

---

## Locations Service API

**Base URL**: `http://localhost:8003`

### List All Locations

Retrieves all battle locations from the database.

**Endpoint**: `GET /api/locations`

**Response**: `200 OK`

``````json
[
  {
    "id": 1,
    "name": "Gotham City",
    "description": "Dark urban environment",
    "picture": "https://..."
  }
]
``````

**Example**:
``````bash
curl http://localhost:8003/api/locations
``````

### Get Location by ID

Retrieves a specific location by its unique identifier.

**Endpoint**: `GET /api/locations/{id}`

**Path Parameters**:
- `id` (integer, required): The location's unique identifier

**Response**: `200 OK` | `404 Not Found`

``````json
{
  "id": 1,
  "name": "Gotham City",
  "description": "Dark urban environment",
  "picture": "https://..."
}
``````

**Example**:
``````bash
curl http://localhost:8003/api/locations/1
``````

### Get Random Location

Returns a randomly selected battle location.

**Endpoint**: `GET /api/locations/random_location`

**Response**: `200 OK` | `404 Not Found`

``````json
{
  "id": 1,
  "name": "Gotham City",
  "description": "Dark urban environment",
  "picture": "https://..."
}
``````

**Example**:
``````bash
curl http://localhost:8003/api/locations/random_location
``````

---

## Fights Service API

**Base URL**: `http://localhost:8004`

The Fights Service orchestrates battles and aggregates data from other services.

### Get Random Fighters

Fetches a random hero and villain in parallel.

**Endpoint**: `GET /api/fights/randomfighters`

**Response**: `200 OK`

``````json
{
  "hero": {
    "id": 51,
    "name": "Yoda",
    "otherName": "",
    "powers": "Force Manipulation",
    "level": 286000
  },
  "villain": {
    "id": 1,
    "name": "Thanos",
    "otherName": "The Mad Titan",
    "powers": "Reality Manipulation",
    "level": 250000
  }
}
``````

**Performance**: Uses `asyncio.gather()` to fetch both combatants concurrently, reducing total request time.

**Example**:
``````bash
curl http://localhost:8004/api/fights/randomfighters
``````

### Get Random Location

Fetches a random battle location.

**Endpoint**: `GET /api/fights/randomlocation`

**Response**: `200 OK`

``````json
{
  "id": 1,
  "name": "Gotham City",
  "description": "Dark urban environment",
  "picture": "https://..."
}
``````

**Example**:
``````bash
curl http://localhost:8004/api/fights/randomlocation
``````

### Execute Fight

Simulates a battle with provided hero, villain, and location.

**Endpoint**: `POST /api/fights`

**Request Body**:
``````json
{
  "hero": {
    "id": 51,
    "name": "Yoda",
    "level": 286000,
    "powers": "Force Manipulation",
    "picture": "https://..."
  },
  "villain": {
    "id": 1,
    "name": "Thanos",
    "level": 250000,
    "powers": "Reality Manipulation",
    "picture": "https://..."
  },
  "location": {
    "id": 1,
    "name": "Gotham City"
  }
}
``````

**Response**: `200 OK`

``````json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "fight_date": "2023-10-01T12:00:00Z",
  "winner_name": "Yoda",
  "winner_level": 286000,
  "winner_powers": "Force Manipulation",
  "winner_picture": "https://...",
  "winner_team": "heroes",
  "loser_name": "Thanos",
  "loser_level": 250000,
  "loser_powers": "Reality Manipulation",
  "loser_picture": "https://...",
  "loser_team": "villains",
  "hero": { /* original hero object */ },
  "villain": { /* original villain object */ },
  "location": { /* original location object */ }
}
``````

**Battle Logic**: Winner determined by comparing `level` values. Higher level wins.

**Example**:
``````bash
curl -X POST http://localhost:8004/api/fights \
  -H "Content-Type: application/json" \
  -d '{
    "hero": {"id": 1, "name": "Yoda", "level": 286000, "powers": "Force", "picture": ""},
    "villain": {"id": 1, "name": "Thanos", "level": 250000, "powers": "Reality", "picture": ""},
    "location": {"id": 1, "name": "Gotham"}
  }'
``````

### Execute Random Fight

Fetches random hero, villain, and location, then executes the battle. All data fetched in parallel.

**Endpoint**: `GET /api/fights/execute_fight`

**Response**: `200 OK`

``````json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "fight_date": "2023-10-01T12:00:00Z",
  "winner_name": "Yoda",
  "winner_level": 286000,
  "winner_powers": "Force Manipulation, Telekinesis",
  "winner_picture": "https://...",
  "winner_team": "heroes",
  "loser_name": "Thanos",
  "loser_level": 250000,
  "loser_powers": "Reality Manipulation",
  "loser_picture": "https://...",
  "loser_team": "villains",
  "hero": {
    "id": 51,
    "name": "Yoda",
    "level": 286000
  },
  "villain": {
    "id": 1,
    "name": "Thanos",
    "level": 250000
  },
  "location": {
    "id": 1,
    "name": "Gotham City"
  }
}
``````

**Performance**: Uses `asyncio.gather()` to fetch hero, villain, and location concurrently.

**Example**:
``````bash
curl http://localhost:8004/api/fights/execute_fight
``````

---

## Data Models

### Hero Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | Unique identifier |
| name | string | Yes | Hero name (max 50 chars) |
| otherName | string | No | Alias or alternate identity (max 255 chars) |
| picture | string | No | URL to hero image (max 255 chars) |
| powers | text | No | Comma-separated list of abilities |
| level | integer | Yes | Power level for battle calculations |

### Villain Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | Unique identifier |
| name | string | Yes | Villain name (max 50 chars) |
| otherName | string | No | Alias or alternate identity (max 255 chars) |
| picture | string | No | URL to villain image (max 255 chars) |
| powers | text | No | Comma-separated list of abilities |
| level | integer | Yes | Power level for battle calculations |

### Location Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | Unique identifier |
| name | string | Yes | Location name |
| description | string | No | Location description |
| picture | string | No | URL to location image |

### Fight Result Model

| Field | Type | Description |
|-------|------|-------------|
| id | string (UUID) | Unique fight identifier |
| fight_date | string (ISO 8601) | Timestamp of the battle |
| winner_name | string | Name of the victor |
| winner_level | integer | Winner's power level |
| winner_powers | string | Winner's abilities |
| winner_picture | string | Winner's image URL |
| winner_team | string | "heroes" or "villains" |
| loser_name | string | Name of the defeated |
| loser_level | integer | Loser's power level |
| loser_powers | string | Loser's abilities |
| loser_picture | string | Loser's image URL |
| loser_team | string | "heroes" or "villains" |
| hero | object | Complete hero data |
| villain | object | Complete villain data |
| location | object | Complete location data |

---

## Error Handling

### Standard Error Responses

All services return consistent error formats.

#### 404 Not Found

Returned when requested resource doesn't exist.

``````json
{
  "detail": "Not found"
}
``````

#### 502 Bad Gateway

Returned by Fights Service when upstream service is unavailable.

``````json
{
  "detail": "Error connecting to external service: Connection refused"
}
``````

### HTTP Client Timeouts

The Fights Service implements aggressive timeouts:
- **Connect**: 2 seconds
- **Read**: 5 seconds
- **Write**: 2 seconds
- **Pool**: 2 seconds

If external services don't respond within these limits, requests will fail with timeout errors.

### Database Connection Errors

Services retry database connections for 10-30 seconds on startup. If databases aren't available within this window, services will fail to start.

---

## Rate Limiting

No rate limiting is currently implemented. For production deployments, consider adding:
- API gateway with rate limiting
- Per-IP request throttling
- Authenticated API keys with quotas

## CORS

CORS is not configured. To enable cross-origin requests, add middleware to each service.

## Interactive Documentation

The Fights Service (FastAPI) provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8004/docs
- **ReDoc**: http://localhost:8004/redoc

Heroes, Villains, and Locations services (Starlette) do not include built-in documentation endpoints.
