# Heroes Service

The Heroes Service manages superhero data and provides API endpoints for retrieving hero information.

## Technical Details

- **Framework**: Starlette (async ASGI framework)
- **Database**: PostgreSQL
- **Port**: 8000 (container) / 8001 (host)
- **Language**: Python 3.13

## Database Schema

The service uses a PostgreSQL database with the following schema:

``````sql
CREATE TABLE Hero (
  id int8 NOT NULL PRIMARY KEY,
  level int4 NOT NULL,
  name VARCHAR(50) NOT NULL,
  otherName VARCHAR(255),
  picture VARCHAR(255),
  powers TEXT
);
``````

### Fields

- `id`: Unique identifier for the hero
- `level`: Power level (determines fight outcomes)
- `name`: Hero's primary name
- `otherName`: Alternate identity or alias
- `picture`: URL to hero's image
- `powers`: Comma-separated list of superpowers

## API Endpoints

### GET /api/heroes

Returns a list of all heroes.

**Response**:
``````json
[
  {
    "id": 1,
    "name": "Chewbacca",
    "otherName": "",
    "picture": "https://...",
    "powers": "Super Strength, Agility, ...",
    "level": 30
  }
]
``````

### GET /api/heroes/random_hero

Returns a randomly selected hero.

**Response**:
``````json
{
  "id": 51,
  "name": "Yoda",
  "otherName": "",
  "picture": "https://...",
  "powers": "Acrobatics, Agility, ...",
  "level": 286000
}
``````

### GET /api/heroes/{id}

Returns a specific hero by ID.

**Parameters**:
- `id` (path): Hero ID

**Response**:
``````json
{
  "id": 1,
  "name": "Chewbacca",
  "otherName": "",
  "picture": "https://...",
  "powers": "Super Strength, Agility, ...",
  "level": 30
}
``````

**Error Response** (404):
``````json
{
  "detail": "Not found"
}
``````

## Configuration

The service uses the following environment variables:

- `DATABASE_URL`: PostgreSQL connection string
  - Default: `postgres://superman:superman@heroes-db:5432/heroes_database`

## Database Connection

The service implements connection retry logic with the following parameters:

- **Retry Timeout**: 10 seconds
- **Retry Interval**: 0.5 seconds

Connection pooling is configured with:
- **Min Pool Size**: 10
- **Max Pool Size**: 50

## Implementation Details

### Startup Behavior

On startup, the service:
1. Attempts to connect to PostgreSQL
2. Retries connection for up to 10 seconds
3. Creates connection pool
4. Verifies database connectivity

### Field Name Mapping

The service automatically maps database field names to API field names:
- Database: `othername` → API: `otherName`

This ensures consistent camelCase naming in API responses.

## Running Locally

Using Docker Compose:
``````bash
docker compose up heroes
``````

Standalone (requires PostgreSQL running):
``````bash
cd services/heroes
pip install -r requirements.txt
DATABASE_URL=postgres://user:pass@localhost:5432/heroes_database python main.py
``````

## Dependencies

See `requirements.txt`:
- `starlette` - ASGI framework
- `asyncpg` - PostgreSQL async driver
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variable management

## Data Source

Hero data is sourced from the [Quarkus Super Heroes](https://github.com/quarkusio/quarkus-super-heroes) project, containing 100 randomly sampled heroes from their character database.
