# API Documentation

Complete API reference for all Python Super Heroes microservices.

## Base URLs

When running locally with Docker Compose:

- **Heroes Service**: `http://localhost:8001`
- **Villains Service**: `http://localhost:8002`
- **Locations Service**: `http://localhost:8003`
- **Fights Service**: `http://localhost:8004`

## Authentication

Currently, no authentication is required (development only).

## Response Format

All endpoints return JSON responses with appropriate HTTP status codes.

### Success Responses
- `200 OK`: Request successful
- `201 Created`: Resource created

### Error Responses
- `404 Not Found`: Resource doesn't exist
- `500 Internal Server Error`: Server error

---

## Heroes Service API

### List All Heroes

Returns all available heroes.

**Request**:
```http
GET /api/heroes
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Superman",
    "othername": "Clark Kent",
    "picture": "https://example.com/superman.jpg",
    "level": 95,
    "powers": "flight, super strength, heat vision, x-ray vision"
  },
  {
    "id": 2,
    "name": "Batman",
    "othername": "Bruce Wayne",
    "picture": "https://example.com/batman.jpg",
    "level": 85,
    "powers": "martial arts, detective skills, technology"
  }
]
```

### Get Hero by ID

Returns a specific hero.

**Request**:
```http
GET /api/heroes/{id}
```

**Path Parameters**:
- `id` (integer, required): Hero ID

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Superman",
  "othername": "Clark Kent",
  "picture": "https://example.com/superman.jpg",
  "level": 95,
  "powers": "flight, super strength, heat vision"
}
```

**Response** (404 Not Found):
```json
{
  "detail": "Hero not found"
}
```

### Get Random Hero

Returns a randomly selected hero.

**Request**:
```http
GET /api/heroes/random_hero
```

**Response** (200 OK):
```json
{
  "id": 3,
  "name": "Wonder Woman",
  "othername": "Diana Prince",
  "picture": "https://example.com/wonderwoman.jpg",
  "level": 92,
  "powers": "super strength, flight, lasso of truth"
}
```

---

## Villains Service API

### List All Villains

Returns all available villains.

**Request**:
```http
GET /api/villains
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Lex Luthor",
    "othername": "Alexander Luthor",
    "picture": "https://example.com/lex.jpg",
    "level": 88,
    "powers": "genius intellect, power suit, wealth"
  },
  {
    "id": 2,
    "name": "Joker",
    "othername": "Unknown",
    "picture": "https://example.com/joker.jpg",
    "level": 82,
    "powers": "unpredictability, toxins, insanity"
  }
]
```

### Get Villain by ID

Returns a specific villain.

**Request**:
```http
GET /api/villains/{id}
```

**Path Parameters**:
- `id` (integer, required): Villain ID

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Lex Luthor",
  "othername": "Alexander Luthor",
  "picture": "https://example.com/lex.jpg",
  "level": 88,
  "powers": "genius intellect, power suit"
}
```

### Get Random Villain

Returns a randomly selected villain.

**Request**:
```http
GET /api/villains/random_villain
```

**Response** (200 OK):
```json
{
  "id": 4,
  "name": "Darkseid",
  "othername": "Uxas",
  "picture": "https://example.com/darkseid.jpg",
  "level": 97,
  "powers": "omega beams, super strength, immortality"
}
```

---

## Locations Service API

### List All Locations

Returns all available battle locations.

**Request**:
```http
GET /api/locations
```

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "name": "Metropolis",
    "description": "A bustling metropolis protected by Superman",
    "picture": "https://example.com/metropolis.jpg"
  },
  {
    "id": 2,
    "name": "Gotham City",
    "description": "A dark city watched over by Batman",
    "picture": "https://example.com/gotham.jpg"
  }
]
```

### Get Location by ID

Returns a specific location.

**Request**:
```http
GET /api/locations/{id}
```

**Path Parameters**:
- `id` (integer, required): Location ID

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "Metropolis",
  "description": "A bustling metropolis protected by Superman",
  "picture": "https://example.com/metropolis.jpg"
}
```

### Get Random Location

Returns a randomly selected location.

**Request**:
```http
GET /api/locations/random_location
```

**Response** (200 OK):
```json
{
  "id": 7,
  "name": "Themyscira",
  "description": "Paradise Island, home of the Amazons",
  "picture": "https://example.com/themyscira.jpg"
}
```

### Health Check

Simple health check endpoint.

**Request**:
```http
GET /thing
```

**Response** (200 OK):
```json
{
  "thing": "stuff"
}
```

---

## Fights Service API

### Get Random Fighters

Fetches a random hero and villain simultaneously.

**Request**:
```http
GET /api/fights/randomfighters
```

**Response** (200 OK):
```json
{
  "hero": {
    "id": 1,
    "name": "Superman",
    "level": 95,
    "powers": "flight, super strength"
  },
  "villain": {
    "id": 2,
    "name": "Lex Luthor",
    "level": 88,
    "powers": "genius intellect"
  }
}
```

**Service Calls**:
- Parallel requests to Heroes and Villains services

### Get Random Location

Fetches a random battle location.

**Request**:
```http
GET /api/fights/randomlocation
```

**Response** (200 OK):
```json
{
  "id": 3,
  "name": "Metropolis",
  "description": "Superman's city"
}
```

### Create Fight

Creates a fight with provided fighters and location.

**Request**:
```http
POST /api/fights
Content-Type: application/json

{
  "hero": {
    "id": 1,
    "name": "Superman",
    "level": 95
  },
  "villain": {
    "id": 2,
    "name": "Lex Luthor",
    "level": 88
  },
  "location": {
    "id": 3,
    "name": "Metropolis"
  }
}
```

**Response** (200 OK):
```json
{
  "fight": {
    "hero": {
      "id": 1,
      "name": "Superman",
      "level": 95
    },
    "villain": {
      "id": 2,
      "name": "Lex Luthor",
      "level": 88
    },
    "location": {
      "id": 3,
      "name": "Metropolis"
    },
    "winner": "hero",
    "loser": "villain"
  }
}
```

**Fight Logic**:
- Winner determined by comparing `hero.level` vs `villain.level`
- Higher level wins
- If equal, hero wins (hero advantage)

### Execute Random Fight

Executes a complete fight with random hero, villain, and location.

**Request**:
```http
GET /api/fights/execute_fight
```

**Response** (200 OK):
```json
{
  "fight": {
    "hero": {
      "id": 5,
      "name": "Flash",
      "othername": "Barry Allen",
      "level": 89,
      "powers": "super speed"
    },
    "villain": {
      "id": 8,
      "name": "Reverse Flash",
      "othername": "Eobard Thawne",
      "level": 87,
      "powers": "super speed, time manipulation"
    },
    "location": {
      "id": 12,
      "name": "Central City",
      "description": "Home of the Flash"
    },
    "winner": "hero",
    "loser": "villain"
  }
}
```

**Service Call Sequence**:
1. **Parallel**: Fetch random hero AND random villain
2. **Sequential**: Fetch random location
3. **Calculate**: Determine winner by level comparison

---

## Interactive API Documentation

The Fights service (FastAPI) provides automatic interactive documentation:

### Swagger UI
```
http://localhost:8004/docs
```

Features:
- Try out API endpoints directly in browser
- See request/response schemas
- Authentication (when implemented)

### ReDoc
```
http://localhost:8004/redoc
```

Features:
- Clean, readable API documentation
- Searchable
- Code samples in multiple languages

### OpenAPI JSON
```
http://localhost:8004/openapi.json
```

Raw OpenAPI 3.0 specification for programmatic access.

---

## Rate Limiting

Currently not implemented. Consider adding rate limiting for production deployments.

## CORS

All services allow cross-origin requests for development. Configure CORS properly for production.

## Pagination

Currently not implemented. All list endpoints return complete results.

**Future Enhancement**:
```http
GET /api/heroes?page=1&limit=50
```

## Filtering and Sorting

Currently not implemented.

**Future Enhancement**:
```http
GET /api/heroes?level_min=80&sort=level_desc
```

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Status Code | Meaning | Example |
|-------------|---------|---------|
| 400 | Bad Request | Invalid JSON body |
| 404 | Not Found | Resource with ID doesn't exist |
| 500 | Internal Server Error | Database connection failed |
| 503 | Service Unavailable | Dependent service unreachable |

---

## Code Examples

### cURL

```bash
# Get all heroes
curl http://localhost:8001/api/heroes

# Get specific hero
curl http://localhost:8001/api/heroes/1

# Execute random fight
curl http://localhost:8004/api/fights/execute_fight

# Create custom fight
curl -X POST http://localhost:8004/api/fights \
  -H "Content-Type: application/json" \
  -d '{
    "hero": {"id": 1, "name": "Superman", "level": 95},
    "villain": {"id": 2, "name": "Lex Luthor", "level": 88},
    "location": {"id": 3, "name": "Metropolis"}
  }'
```

### Python

```python
import requests

# Get random hero
hero_response = requests.get('http://localhost:8001/api/heroes/random_hero')
hero = hero_response.json()

# Get random villain
villain_response = requests.get('http://localhost:8002/api/villains/random_villain')
villain = villain_response.json()

# Execute fight
fight_response = requests.get('http://localhost:8004/api/fights/execute_fight')
fight = fight_response.json()
print(f"Winner: {fight['fight']['winner']}")
```

### JavaScript

```javascript
// Fetch random fighters
fetch('http://localhost:8004/api/fights/randomfighters')
  .then(response => response.json())
  .then(data => {
    console.log('Hero:', data.hero.name);
    console.log('Villain:', data.villain.name);
  });

// Execute fight
async function executeFight() {
  const response = await fetch('http://localhost:8004/api/fights/execute_fight');
  const result = await response.json();
  return result.fight;
}
```

---

## Versioning

Current version: v1 (implicit in URLs)

Future versions may use explicit versioning:
```
/api/v2/heroes
```

## Deprecation Policy

Breaking changes will be announced with:
1. Minimum 90-day notice
2. Migration guide
3. Parallel version support during transition
