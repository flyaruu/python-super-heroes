# API Reference

Complete API documentation for all microservices in the Python Super Heroes system.

## Heroes Service

**Base URL**: `http://localhost:8001`

### GET /api/heroes

List all heroes.

**Response**: `200 OK`
``````json
[
  {
    "id": 1,
    "name": "Spider-Man",
    "otherName": "Peter Parker",
    "level": 93,
    "picture": "https://example.com/spiderman.jpg",
    "powers": "Web-slinging, Wall-crawling, Spider-sense"
  }
]
``````

### GET /api/heroes/random_hero

Get a random hero.

**Response**: `200 OK`
``````json
{
  "id": 42,
  "name": "Yoda",
  "otherName": "",
  "level": 286000,
  "picture": "https://example.com/yoda.jpg",
  "powers": "The Force, Master Tactician, Telekinesis"
}
``````

**Response**: `404 Not Found` (if no heroes exist)
``````json
{
  "detail": "Not found"
}
``````

### GET /api/heroes/{id}

Get a specific hero by ID.

**Parameters:**
- `id` (integer, path) - Hero ID

**Response**: `200 OK`
``````json
{
  "id": 1,
  "name": "Chewbacca",
  "otherName": "",
  "level": 30,
  "picture": "https://example.com/chewie.jpg",
  "powers": "Super Strength, Agility, Longevity"
}
``````

**Response**: `404 Not Found`
``````json
{
  "detail": "Not found"
}
``````

---

## Villains Service

**Base URL**: `http://localhost:8002`

### GET /api/villains

List all villains.

**Response**: `200 OK`
``````json
[
  {
    "id": 1,
    "name": "Thanos",
    "otherName": "The Mad Titan",
    "level": 1000000,
    "picture": "https://example.com/thanos.jpg",
    "powers": "Super Strength, Durability, Intelligence"
  }
]
``````

### GET /api/villains/random_villain

Get a random villain.

**Response**: `200 OK`
``````json
{
  "id": 23,
  "name": "Joker",
  "otherName": "",
  "level": 150,
  "picture": "https://example.com/joker.jpg",
  "powers": "Intelligence, Master Tactician, Insanity"
}
``````

**Response**: `404 Not Found`
``````json
{
  "detail": "Not found"
}
``````

### GET /api/villains/{id}

Get a specific villain by ID.

**Parameters:**
- `id` (integer, path) - Villain ID

**Response**: `200 OK`
``````json
{
  "id": 5,
  "name": "Darth Vader",
  "otherName": "Anakin Skywalker",
  "level": 500000,
  "picture": "https://example.com/vader.jpg",
  "powers": "The Force, Lightsaber Combat, Force Choke"
}
``````

**Response**: `404 Not Found`
``````json
{
  "detail": "Not found"
}
``````

---

## Locations Service

**Base URL**: `http://localhost:8003`

### GET /api/locations

List all locations.

**Response**: `200 OK`
``````json
[
  {
    "id": 1,
    "name": "Gotham City",
    "description": "Dark metropolis",
    "picture": "https://example.com/gotham.jpg"
  }
]
``````

### GET /api/locations/random_location

Get a random location.

**Response**: `200 OK`
``````json
{
  "id": 15,
  "name": "Asgard",
  "description": "Realm of the Norse gods",
  "picture": "https://example.com/asgard.jpg"
}
``````

**Response**: `404 Not Found`
``````json
{
  "detail": "Not found"
}
``````

### GET /api/locations/{id}

Get a specific location by ID.

**Parameters:**
- `id` (integer, path) - Location ID

**Response**: `200 OK`
``````json
{
  "id": 7,
  "name": "Wakanda",
  "description": "Advanced African nation",
  "picture": "https://example.com/wakanda.jpg"
}
``````

**Response**: `404 Not Found`
``````json
{
  "detail": "Not found"
}
``````

### GET /thing

Test endpoint.

**Response**: `200 OK`
``````json
{
  "message": "This is a thing"
}
``````

---

## Fights Service

**Base URL**: `http://localhost:8004`

### GET /api/fights/randomfighters

Get a random hero and villain for a fight.

**Response**: `200 OK`
``````json
{
  "hero": {
    "id": 10,
    "name": "Spider-Man",
    "otherName": "Peter Parker",
    "level": 93,
    "picture": "https://example.com/spiderman.jpg",
    "powers": "Web-slinging, Wall-crawling"
  },
  "villain": {
    "id": 23,
    "name": "Green Goblin",
    "otherName": "Norman Osborn",
    "level": 85,
    "picture": "https://example.com/goblin.jpg",
    "powers": "Super Strength, Glider, Pumpkin Bombs"
  }
}
``````

**Response**: `502 Bad Gateway` (if upstream service unavailable)
``````json
{
  "detail": "Error connecting to external service: ..."
}
``````

### GET /api/fights/randomlocation

Get a random fight location.

**Response**: `200 OK`
``````json
{
  "id": 5,
  "name": "New York City",
  "description": "Urban battleground",
  "picture": "https://example.com/nyc.jpg"
}
``````

**Response**: `502 Bad Gateway`
``````json
{
  "detail": "Error connecting to external service: ..."
}
``````

### POST /api/fights

Execute a fight between a hero and villain at a location.

**Request Body:**
``````json
{
  "hero": {
    "id": 10,
    "name": "Spider-Man",
    "level": 93,
    "powers": "Web-slinging",
    "picture": "https://example.com/spiderman.jpg"
  },
  "villain": {
    "id": 23,
    "name": "Green Goblin",
    "level": 85,
    "powers": "Glider",
    "picture": "https://example.com/goblin.jpg"
  },
  "location": {
    "id": 5,
    "name": "New York City",
    "picture": "https://example.com/nyc.jpg"
  }
}
``````

**Response**: `200 OK`
``````json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "fight_date": "2023-10-01T12:00:00Z",
  "winner_name": "Spider-Man",
  "winner_level": 93,
  "winner_powers": "Web-slinging",
  "winner_picture": "https://example.com/spiderman.jpg",
  "winner_team": "heroes",
  "loser_name": "Green Goblin",
  "loser_level": 85,
  "loser_powers": "Glider",
  "loser_picture": "https://example.com/goblin.jpg",
  "loser_team": "villains",
  "hero": { ... },
  "villain": { ... },
  "location": { ... }
}
``````

### GET /api/fights/execute_fight

Execute a random fight (convenience endpoint).

Combines `randomfighters` + `randomlocation` + `POST /api/fights` in one call.

**Response**: `200 OK`
``````json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "fight_date": "2023-10-01T12:00:00Z",
  "winner_name": "Yoda",
  "winner_level": 286000,
  "winner_powers": "The Force, Telekinesis",
  "winner_picture": "https://example.com/yoda.jpg",
  "winner_team": "heroes",
  "loser_name": "Darth Vader",
  "loser_level": 500000,
  "loser_powers": "The Force, Lightsaber",
  "loser_picture": "https://example.com/vader.jpg",
  "loser_team": "villains",
  "hero": {
    "id": 42,
    "name": "Yoda",
    "level": 286000,
    "powers": "The Force",
    "picture": "https://example.com/yoda.jpg"
  },
  "villain": {
    "id": 67,
    "name": "Darth Vader",
    "level": 500000,
    "powers": "The Force",
    "picture": "https://example.com/vader.jpg"
  },
  "location": {
    "id": 12,
    "name": "Death Star",
    "picture": "https://example.com/deathstar.jpg"
  }
}
``````

---

## Common Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 404 | Not Found | Resource doesn't exist |
| 502 | Bad Gateway | Upstream service unavailable |

## Error Response Format

All errors follow this structure:

``````json
{
  "detail": "Human-readable error message"
}
``````

## Rate Limiting

Currently no rate limiting is implemented. See [ARCHITECTURE.md](ARCHITECTURE.md#security-considerations) for production recommendations.

## Authentication

Currently no authentication is required. All endpoints are publicly accessible.

## CORS

CORS is not currently configured. Add CORS middleware if frontend access is needed:

``````python
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
``````

## Content-Type

All requests and responses use `application/json`.

## Character Encoding

UTF-8 encoding is used throughout.

## API Versioning

Current API version is implicit (v1). Endpoints are prefixed with `/api/` for future versioning capability.

Future versions could use:
- Path versioning: `/api/v2/heroes`
- Header versioning: `Accept: application/vnd.superheroes.v2+json`
- Query parameter: `/api/heroes?version=2`

## Examples

### cURL Examples

**Get random fight:**
``````bash
curl http://localhost:8004/api/fights/execute_fight
``````

**Get specific hero:**
``````bash
curl http://localhost:8001/api/heroes/42
``````

**Execute custom fight:**
``````bash
curl -X POST http://localhost:8004/api/fights \
  -H "Content-Type: application/json" \
  -d '{
    "hero": {"id": 1, "name": "Hero", "level": 100, "powers": "Flight", "picture": ""},
    "villain": {"id": 2, "name": "Villain", "level": 90, "powers": "Strength", "picture": ""},
    "location": {"id": 3, "name": "City", "picture": ""}
  }'
``````

### Python Examples

**Using requests:**
``````python
import requests

# Get random hero
response = requests.get("http://localhost:8001/api/heroes/random_hero")
hero = response.json()
print(f"Hero: {hero['name']} (Level {hero['level']})")

# Execute fight
fight_response = requests.get("http://localhost:8004/api/fights/execute_fight")
fight = fight_response.json()
print(f"Winner: {fight['winner_name']} from {fight['winner_team']}")
``````

**Using httpx (async):**
``````python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8004/api/fights/execute_fight")
        fight = response.json()
        print(f"Fight at {fight['location']['name']}")
        print(f"{fight['hero']['name']} vs {fight['villain']['name']}")
        print(f"Winner: {fight['winner_name']}")

asyncio.run(main())
``````

### JavaScript Examples

**Using fetch:**
``````javascript
// Get random fighters
fetch('http://localhost:8004/api/fights/randomfighters')
  .then(response => response.json())
  .then(data => {
    console.log(`Hero: ${data.hero.name} (${data.hero.level})`);
    console.log(`Villain: ${data.villain.name} (${data.villain.level})`);
  });

// Execute fight
fetch('http://localhost:8004/api/fights/execute_fight')
  .then(response => response.json())
  .then(fight => {
    console.log(`Winner: ${fight.winner_name}`);
  });
``````
