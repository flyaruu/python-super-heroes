# API Reference

Complete API documentation for all Python Super Heroes microservices.

## Table of Contents

- [Heroes Service](#heroes-service)
- [Villains Service](#villains-service)
- [Locations Service](#locations-service)
- [Fights Service](#fights-service)
- [Common Response Formats](#common-response-formats)
- [Error Handling](#error-handling)

---

## Heroes Service

**Base URL**: `http://localhost:8001`

### List All Heroes

Retrieves all heroes from the database.

**Endpoint**: `GET /api/heroes`

**Response**: `200 OK`

``````json
[
  {
    "id": 1,
    "name": "Superman",
    "otherName": "Clark Kent",
    "level": 95,
    "picture": "https://example.com/superman.jpg",
    "powers": "Flight, Super Strength, Heat Vision"
  },
  {
    "id": 2,
    "name": "Wonder Woman",
    "otherName": "Diana Prince",
    "level": 92,
    "picture": "https://example.com/wonderwoman.jpg",
    "powers": "Super Strength, Lasso of Truth, Flight"
  }
]
``````

### Get Hero by ID

Retrieves a specific hero by their ID.

**Endpoint**: `GET /api/heroes/{id}`

**Path Parameters**:
- `id` (integer, required) - The hero ID

**Response**: `200 OK`

``````json
{
  "id": 1,
  "name": "Superman",
  "otherName": "Clark Kent",
  "level": 95,
  "picture": "https://example.com/superman.jpg",
  "powers": "Flight, Super Strength, Heat Vision"
}
``````

**Error Response**: `404 Not Found`

``````json
{
  "detail": "Hero not found"
}
``````

### Get Random Hero

Retrieves a random hero from the database.

**Endpoint**: `GET /api/heroes/random_hero`

**Response**: `200 OK`

``````json
{
  "id": 42,
  "name": "Spider-Man",
  "otherName": "Peter Parker",
  "level": 88,
  "picture": "https://example.com/spiderman.jpg",
  "powers": "Wall Crawling, Spider Sense, Web Slinging"
}
``````

---

## Villains Service

**Base URL**: `http://localhost:8002`

### List All Villains

Retrieves all villains from the database.

**Endpoint**: `GET /api/villains`

**Response**: `200 OK`

``````json
[
  {
    "id": 1,
    "name": "Lex Luthor",
    "otherName": "Alexander Luthor",
    "level": 85,
    "picture": "https://example.com/lexluthor.jpg",
    "powers": "Genius Intellect, Powered Armor"
  }
]
``````

### Get Villain by ID

Retrieves a specific villain by their ID.

**Endpoint**: `GET /api/villains/{id}`

**Path Parameters**:
- `id` (integer, required) - The villain ID

**Response**: `200 OK`

``````json
{
  "id": 1,
  "name": "Lex Luthor",
  "otherName": "Alexander Luthor",
  "level": 85,
  "picture": "https://example.com/lexluthor.jpg",
  "powers": "Genius Intellect, Powered Armor"
}
``````

### Get Random Villain

Retrieves a random villain from the database.

**Endpoint**: `GET /api/villains/random_villain`

**Response**: `200 OK`

``````json
{
  "id": 23,
  "name": "The Joker",
  "otherName": "Unknown",
  "level": 82,
  "picture": "https://example.com/joker.jpg",
  "powers": "Genius Intellect, Chemical Expertise"
}
``````

---

## Locations Service

**Base URL**: `http://localhost:8003`

### List All Locations

Retrieves all fight locations from the database.

**Endpoint**: `GET /api/locations`

**Response**: `200 OK`

``````json
[
  {
    "id": 1,
    "name": "Metropolis",
    "description": "A bustling metropolis with towering skyscrapers",
    "picture": "https://example.com/metropolis.jpg",
    "type": "CITY"
  },
  {
    "id": 2,
    "name": "Themyscira",
    "description": "Hidden island home of the Amazons",
    "picture": "https://example.com/themyscira.jpg",
    "type": "ISLAND"
  }
]
``````

### Location Types

- `CITY` - Urban locations
- `PLANET` - Planetary locations
- `PLACE` - Generic places
- `ISLAND` - Island locations
- `COUNTRY` - Country-level locations
- `MOON` - Lunar/satellite locations

### Get Location by ID

Retrieves a specific location by its ID.

**Endpoint**: `GET /api/locations/{id}`

**Path Parameters**:
- `id` (integer, required) - The location ID

**Response**: `200 OK`

``````json
{
  "id": 1,
  "name": "Metropolis",
  "description": "A bustling metropolis with towering skyscrapers",
  "picture": "https://example.com/metropolis.jpg",
  "type": "CITY"
}
``````

### Get Random Location

Retrieves a random location from the database.

**Endpoint**: `GET /api/locations/random_location`

**Response**: `200 OK`

``````json
{
  "id": 7,
  "name": "Gotham City",
  "description": "A dark, crime-ridden city",
  "picture": "https://example.com/gotham.jpg",
  "type": "CITY"
}
``````

---

## Fights Service

**Base URL**: `http://localhost:8004`

The Fights service orchestrates battles between heroes and villains at various locations.

### Get Random Fighters

Retrieves a random hero and villain for a potential fight.

**Endpoint**: `GET /api/fights/randomfighters`

**Response**: `200 OK`

``````json
{
  "hero": {
    "id": 12,
    "name": "The Flash",
    "otherName": "Barry Allen",
    "level": 90,
    "picture": "https://example.com/flash.jpg",
    "powers": "Super Speed, Time Travel"
  },
  "villain": {
    "id": 8,
    "name": "Reverse Flash",
    "otherName": "Eobard Thawne",
    "level": 89,
    "picture": "https://example.com/reverseflash.jpg",
    "powers": "Super Speed, Negative Speed Force"
  }
}
``````

### Get Random Location

Retrieves a random location for a fight.

**Endpoint**: `GET /api/fights/randomlocation`

**Response**: `200 OK`

``````json
{
  "id": 5,
  "name": "Central City",
  "description": "Home of the Flash",
  "picture": "https://example.com/centralcity.jpg",
  "type": "CITY"
}
``````

### Execute Fight

Executes a fight between a hero and villain at a specified location.

**Endpoint**: `POST /api/fights`

**Request Body**:

``````json
{
  "hero": {
    "id": 1,
    "name": "Superman",
    "level": 95,
    "powers": "Flight, Super Strength"
  },
  "villain": {
    "id": 1,
    "name": "Lex Luthor",
    "level": 85,
    "powers": "Genius Intellect"
  },
  "location": {
    "id": 1,
    "name": "Metropolis",
    "type": "CITY"
  }
}
``````

**Response**: `200 OK`

``````json
{
  "fightId": "550e8400-e29b-41d4-a716-446655440000",
  "winner": {
    "id": 1,
    "name": "Superman",
    "level": 95
  },
  "loser": {
    "id": 1,
    "name": "Lex Luthor",
    "level": 85
  },
  "location": {
    "id": 1,
    "name": "Metropolis"
  },
  "fightDate": "2026-02-13T13:38:00Z"
}
``````

**Fight Logic**: The winner is determined by comparing the `level` attribute. The fighter with the higher level wins.

### Execute Random Fight

Automatically fetches random fighters and location, then executes the fight.

**Endpoint**: `GET /api/fights/execute_fight`

**Response**: `200 OK`

``````json
{
  "fightId": "660e8400-e29b-41d4-a716-446655440000",
  "hero": {
    "id": 5,
    "name": "Batman",
    "level": 87
  },
  "villain": {
    "id": 3,
    "name": "The Penguin",
    "level": 65
  },
  "location": {
    "id": 4,
    "name": "Gotham City"
  },
  "winner": "hero",
  "winnerName": "Batman",
  "fightDate": "2026-02-13T13:38:00Z"
}
``````

---

## Common Response Formats

### Success Response

All successful API calls return HTTP 200 with JSON data.

### Pagination

Currently, the API does not support pagination. All `GET /api/{resource}` endpoints return complete lists.

---

## Error Handling

### Error Response Format

``````json
{
  "detail": "Error message describing what went wrong"
}
``````

### HTTP Status Codes

- `200 OK` - Request successful
- `404 Not Found` - Resource not found
- `502 Bad Gateway` - Error connecting to external service (Fights service)
- `500 Internal Server Error` - Server error

### Common Errors

**Service Unavailable**

If a dependent service is down, the Fights service returns:

``````json
{
  "detail": "Error connecting to external service: Connection refused"
}
``````

**Resource Not Found**

``````json
{
  "detail": "Hero not found"
}
``````

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting at the API gateway level.

## CORS

All services are configured to accept requests from any origin during development. Configure appropriate CORS policies for production.

## Authentication

The current implementation does not include authentication. All endpoints are publicly accessible.
