# Villains Service

RESTful API service for managing villain data.

## Technology

- **Framework**: Starlette (async Python web framework)
- **Database**: PostgreSQL 16 with asyncpg driver
- **Server**: Uvicorn ASGI server
- **Port**: 8002

## API Endpoints

### GET /api/villains

Returns a list of all villains.

**Response**: Array of villain objects

```json
[
  {
    "id": 1,
    "name": "Lex Luthor",
    "othername": "Alexander Luthor",
    "picture": "https://...",
    "level": 90,
    "powers": "genius intellect, power suit"
  }
]
```

### GET /api/villains/{id}

Returns a specific villain by ID.

**Parameters**:
- `id` (path) - Villain ID (integer)

**Response**: Villain object or 404

### GET /api/villains/random_villain

Returns a randomly selected villain from the database.

**Response**: Single villain object

## Database Schema

The service connects to PostgreSQL with the following schema:

```sql
Villain table (23 columns):
- id: integer (primary key)
- name: varchar
- othername: varchar
- picture: varchar
- level: integer
- powers: text
- ... (additional attributes)
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
  - Format: `postgres://user:password@host:port/database`
  - Example: `postgres://superman:superman@villains-db:5432/villains_database`

## Running Locally

```bash
cd services/villains

# Install dependencies
pip install -r requirements.txt

# Set database connection
export DATABASE_URL="postgres://superman:superman@localhost:5433/villains_database"

# Run the service
uvicorn main:app --reload --port 8002
```

## Docker

```bash
# Build
docker build -t villains-service services/villains

# Run
docker run -p 8002:8000 \
  -e DATABASE_URL="postgres://superman:superman@host.docker.internal:5433/villains_database" \
  villains-service
```

## Dependencies

```
starlette==0.41.3
uvicorn==0.34.0
asyncpg==0.30.0
```

## Health Check

The service automatically initializes the database connection pool on startup and closes it on shutdown. Check service health by querying any endpoint.
