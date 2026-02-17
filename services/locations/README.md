# Locations Service

RESTful API service for managing battle location data.

## Technology

- **Framework**: Starlette (async Python web framework)
- **Database**: MariaDB 11.5 with aiomysql driver
- **Server**: Uvicorn ASGI server
- **Port**: 8003

## API Endpoints

### GET /api/locations

Returns a list of all battle locations.

**Response**: Array of location objects

```json
[
  {
    "id": 1,
    "name": "Metropolis",
    "description": "A bustling city protected by Superman",
    "picture": "https://..."
  }
]
```

### GET /api/locations/{id}

Returns a specific location by ID.

**Parameters**:
- `id` (path) - Location ID (integer)

**Response**: Location object or 404

### GET /api/locations/random_location

Returns a randomly selected location from the database.

**Response**: Single location object

### GET /thing

Health check endpoint that returns a simple response.

**Response**: `{"thing": "stuff"}`

## Database Schema

The service connects to MariaDB with approximately 35 pre-loaded locations including:
- Cities (Metropolis, Gotham City)
- Planets (Krypton, Apokolips)
- Islands and special locations
- Each with descriptions and images

```sql
Location table:
- id: integer (primary key)
- name: varchar
- description: text
- picture: varchar
```

## Environment Variables

- `MYSQL_URL`: MariaDB/MySQL connection string
  - Format: `mysql://user:password@host/database`
  - Example: `mysql://locations:locations@locations-db/locations_database`

## Running Locally

```bash
cd services/locations

# Install dependencies
pip install -r requirements.txt

# Set database connection
export MYSQL_URL="mysql://locations:locations@localhost:3306/locations_database"

# Run the service
uvicorn main:app --reload --port 8003
```

## Docker

```bash
# Build
docker build -t locations-service services/locations

# Run
docker run -p 8003:8000 \
  -e MYSQL_URL="mysql://locations:locations@host.docker.internal:3306/locations_database" \
  locations-service
```

## Dependencies

```
starlette==0.41.3
uvicorn==0.34.0
aiomysql==0.2.0
pymysql==1.1.1
cryptography==44.0.0
```

## Health Check

Use the `/thing` endpoint for basic health checks, or any `/api/locations` endpoint to verify database connectivity.
