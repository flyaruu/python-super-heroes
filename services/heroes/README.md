# Heroes Service

RESTful API service for managing superhero data.

## Technology

- **Framework**: Starlette (async Python web framework)
- **Database**: PostgreSQL 16 with asyncpg driver
- **Server**: Uvicorn ASGI server
- **Port**: 8001

## API Endpoints

### GET /api/heroes

Returns a list of all heroes.

**Response**: Array of hero objects

```json
[
  {
    "id": 1,
    "name": "Superman",
    "othername": "Clark Kent",
    "picture": "https://...",
    "level": 95,
    "powers": "flight, super strength, heat vision"
  }
]
```

### GET /api/heroes/{id}

Returns a specific hero by ID.

**Parameters**:
- `id` (path) - Hero ID (integer)

**Response**: Hero object or 404

### GET /api/heroes/random_hero

Returns a randomly selected hero from the database.

**Response**: Single hero object

## Database Schema

The service connects to PostgreSQL with the following schema:

```sql
Hero table (23 columns):
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
  - Example: `postgres://superman:superman@heroes-db:5432/heroes_database`

## Running Locally

```bash
cd services/heroes

# Install dependencies
pip install -r requirements.txt

# Set database connection
export DATABASE_URL="postgres://superman:superman@localhost:5432/heroes_database"

# Run the service
uvicorn main:app --reload --port 8001
```

## Docker

```bash
# Build
docker build -t heroes-service services/heroes

# Run
docker run -p 8001:8000 \
  -e DATABASE_URL="postgres://superman:superman@host.docker.internal:5432/heroes_database" \
  heroes-service
```

## Dependencies

```
starlette==0.41.3
uvicorn==0.34.0
asyncpg==0.30.0
```

## Health Check

The service automatically initializes the database connection pool on startup and closes it on shutdown. Check service health by querying any endpoint.
