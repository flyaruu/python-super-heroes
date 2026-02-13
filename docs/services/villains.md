# Villains Service

The Villains Service manages villain data and provides API endpoints for retrieving villain information.

## Technical Details

- **Framework**: Starlette (async ASGI framework)
- **Database**: PostgreSQL
- **Port**: 8000 (container) / 8002 (host)
- **Language**: Python 3.13

## Database Schema

The service uses a PostgreSQL database with the following schema:

``````sql
CREATE TABLE Villain (
  id int8 NOT NULL PRIMARY KEY,
  level int4 NOT NULL,
  name VARCHAR(50) NOT NULL,
  otherName VARCHAR(255),
  picture VARCHAR(255),
  powers TEXT
);
``````

### Fields

- `id`: Unique identifier for the villain
- `level`: Power level (determines fight outcomes)
- `name`: Villain's primary name
- `otherName`: Alternate identity or alias
- `picture`: URL to villain's image
- `powers`: Comma-separated list of superpowers

## API Endpoints

### GET /api/villains

Returns a list of all villains.

**Response**:
``````json
[
  {
    "id": 1,
    "name": "Thanos",
    "otherName": "The Mad Titan",
    "picture": "https://...",
    "powers": "Super Strength, Durability, ...",
    "level": 95000
  }
]
``````

### GET /api/villains/random_villain

Returns a randomly selected villain.

**Response**:
``````json
{
  "id": 42,
  "name": "Magneto",
  "otherName": "Erik Lehnsherr",
  "picture": "https://...",
  "powers": "Magnetism, Flight, ...",
  "level": 8500
}
``````

### GET /api/villains/{id}

Returns a specific villain by ID.

**Parameters**:
- `id` (path): Villain ID

**Response**:
``````json
{
  "id": 1,
  "name": "Thanos",
  "otherName": "The Mad Titan",
  "picture": "https://...",
  "powers": "Super Strength, Durability, ...",
  "level": 95000
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
  - Default: `postgres://superman:superman@villains-db:5432/villains_database`

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
docker compose up villains
``````

Standalone (requires PostgreSQL running):
``````bash
cd services/villains
pip install -r requirements.txt
DATABASE_URL=postgres://user:pass@localhost:5432/villains_database python main.py
``````

## Dependencies

See `requirements.txt`:
- `starlette` - ASGI framework
- `asyncpg` - PostgreSQL async driver
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variable management

## Database Notes

The villains database runs on a separate PostgreSQL instance (port 5433 on the host) to demonstrate microservices isolation and independent data management.

## Data Source

Villain data is sourced from the [Quarkus Super Heroes](https://github.com/quarkusio/quarkus-super-heroes) project, containing 100 randomly sampled villains from their character database.
