# API Reference

Complete API documentation for all microservices in the Python Super Heroes system.

## Heroes Service

**Base URL**: `http://localhost:8001`

### Endpoints

#### List All Heroes
``````http
GET /api/heroes
``````

Returns an array of all heroes in the database.

**Response**: `200 OK`
``````json
[
  {
    "id": 1,
    "name": "Superman",
    "otherName": "Clark Kent",
    "level": 95,
    "powers": "Flight, Super Strength, Heat Vision",
    "picture": "https://example.com/superman.jpg"
  },
  {
    "id": 2,
    "name": "Wonder Woman",
    "otherName": "Diana Prince",
    "level": 92,
    "powers": "Super Strength, Lasso of Truth",
    "picture": "https://example.com/wonderwoman.jpg"
  }
]
``````

#### Get Hero by ID
``````http
GET /api/heroes/{id}
``````

Retrieves a specific hero by ID.

**Parameters**:
- `id` (integer, path) - Hero identifier

**Response**: `200 OK`
``````json
{
  "id": 1,
  "name": "Superman",
  "otherName": "Clark Kent",
  "level": 95,
  "powers": "Flight, Super Strength, Heat Vision",
  "picture": "https://example.com/superman.jpg"
}
``````

**Error Response**: `404 Not Found`
``````json
{
  "detail": "Not found"
}
``````

#### Get Random Hero
``````http
GET /api/heroes/random_hero
``````

Returns a randomly selected hero from the database.

**Response**: `200 OK`
``````json
{
  "id": 3,
  "name": "Batman",
  "otherName": "Bruce Wayne",
  "level": 88,
  "powers": "Genius Intellect, Martial Arts, Technology",
  "picture": "https://example.com/batman.jpg"
}
``````

---

## Villains Service

**Base URL**: `http://localhost:8002`

### Endpoints

#### List All Villains
``````http
GET /api/villains
``````

Returns an array of all villains in the database.

**Response**: `200 OK`
``````json
[
  {
    "id": 1,
    "name": "Joker",
    "otherName": "Unknown",
    "level": 85,
    "powers": "Insanity, Chemical Expertise",
    "picture": "https://example.com/joker.jpg"
  }
]
``````

#### Get Villain by ID
``````http
GET /api/villains/{id}
``````

Retrieves a specific villain by ID.

**Parameters**:
- `id` (integer, path) - Villain identifier

**Response**: `200 OK`
``````json
{
  "id": 1,
  "name": "Joker",
  "otherName": "Unknown",
  "level": 85,
  "powers": "Insanity, Chemical Expertise",
  "picture": "https://example.com/joker.jpg"
}
``````

**Error Response**: `404 Not Found`
``````json
{
  "detail": "Not found"
}
``````

#### Get Random Villain
``````http
GET /api/villains/random_villain
``````

Returns a randomly selected villain from the database.

**Response**: `200 OK`
``````json
{
  "id": 2,
  "name": "Lex Luthor",
  "otherName": "Alexander Luthor",
  "level": 90,
  "powers": "Genius Intellect, Wealth, Technology",
  "picture": "https://example.com/lexluthor.jpg"
}
``````

---

## Locations Service

**Base URL**: `http://localhost:8003`

### Endpoints

#### List All Locations
``````http
GET /api/locations
``````

Returns an array of all battle locations.

**Response**: `200 OK`
``````json
[
  {
    "id": 1,
    "name": "Metropolis",
    "description": "The city of tomorrow",
    "picture": "https://example.com/metropolis.jpg"
  }
]
``````

#### Get Location by ID
``````http
GET /api/locations/{id}
``````

Retrieves a specific location by ID.

**Parameters**:
- `id` (integer, path) - Location identifier

**Response**: `200 OK`
``````json
{
  "id": 1,
  "name": "Metropolis",
  "description": "The city of tomorrow",
  "picture": "https://example.com/metropolis.jpg"
}
``````

**Error Response**: `404 Not Found`
``````json
{
  "detail": "Not found"
}
``````

#### Get Random Location
``````http
GET /api/locations/random_location
``````

Returns a randomly selected battle location.

**Response**: `200 OK`
``````json
{
  "id": 3,
  "name": "Gotham City",
  "description": "Dark urban landscape",
  "picture": "https://example.com/gotham.jpg"
}
``````

---

## Fights Service

**Base URL**: `http://localhost:8004`

### Endpoints

#### Get Random Fighters
``````http
GET /api/fights/randomfighters
``````

Returns a random hero and villain for a potential fight.

**Response**: `200 OK`
``````json
{
  "hero": {
    "id": 1,
    "name": "Superman",
    "otherName": "Clark Kent",
    "level": 95,
    "powers": "Flight, Super Strength, Heat Vision",
    "picture": "https://example.com/superman.jpg"
  },
  "villain": {
    "id": 2,
    "name": "Lex Luthor",
    "otherName": "Alexander Luthor",
    "level": 90,
    "powers": "Genius Intellect, Wealth, Technology",
    "picture": "https://example.com/lexluthor.jpg"
  }
}
``````

#### Get Random Location
``````http
GET /api/fights/randomlocation
``````

Returns a random location for a fight.

**Response**: `200 OK`
``````json
{
  "id": 1,
  "name": "Metropolis",
  "description": "The city of tomorrow",
  "picture": "https://example.com/metropolis.jpg"
}
``````

#### Execute Random Fight
``````http
GET /api/fights/execute_fight
``````

Executes a complete fight with random hero, villain, and location. Winner is determined by level comparison.

**Response**: `200 OK`
``````json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "fight_date": "2023-10-01T12:00:00Z",
  "winner_name": "Superman",
  "winner_level": 95,
  "winner_powers": "Flight, Super Strength, Heat Vision",
  "winner_picture": "https://example.com/superman.jpg",
  "loser_name": "Lex Luthor",
  "loser_level": 90,
  "loser_powers": "Genius Intellect, Wealth, Technology",
  "loser_picture": "https://example.com/lexluthor.jpg",
  "winner_team": "heroes",
  "loser_team": "villains",
  "hero": {
    "id": 1,
    "name": "Superman",
    "otherName": "Clark Kent",
    "level": 95,
    "powers": "Flight, Super Strength, Heat Vision",
    "picture": "https://example.com/superman.jpg"
  },
  "villain": {
    "id": 2,
    "name": "Lex Luthor",
    "otherName": "Alexander Luthor",
    "level": 90,
    "powers": "Genius Intellect, Wealth, Technology",
    "picture": "https://example.com/lexluthor.jpg"
  },
  "location": {
    "id": 1,
    "name": "Metropolis",
    "description": "The city of tomorrow",
    "picture": "https://example.com/metropolis.jpg"
  }
}
``````

#### Create Custom Fight
``````http
POST /api/fights
``````

Creates a fight with specific hero, villain, and location.

**Request Body**:
``````json
{
  "hero": {
    "id": 1,
    "name": "Superman",
    "level": 95,
    "powers": "Flight, Super Strength, Heat Vision"
  },
  "villain": {
    "id": 2,
    "name": "Lex Luthor",
    "level": 90,
    "powers": "Genius Intellect, Wealth, Technology"
  },
  "location": {
    "id": 1,
    "name": "Metropolis"
  }
}
``````

**Response**: `200 OK`
``````json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "fight_date": "2023-10-01T12:00:00Z",
  "winner_name": "Superman",
  "winner_level": 95,
  "winner_team": "heroes",
  "loser_name": "Lex Luthor",
  "loser_level": 90,
  "loser_team": "villains",
  "hero": { ... },
  "villain": { ... },
  "location": { ... }
}
``````

---

## Error Codes

All services use standard HTTP status codes:

| Code | Description |
|------|-------------|
| 200 | Success - Request completed successfully |
| 404 | Not Found - Requested resource does not exist |
| 502 | Bad Gateway - External service connection failed |

## Fight Logic

The fight winner is determined by comparing the `level` attribute:
- Higher level wins
- If levels are equal, hero wins
- Result includes complete winner/loser details and original fighters

## CORS

Services do not currently implement CORS headers. Add appropriate middleware for browser-based clients.

## Rate Limiting

No rate limiting is currently implemented. Consider adding in production environments.
