# Locations Service

The Locations Service manages battle location data and provides API endpoints for retrieving location information.

## Technical Details

- **Framework**: Starlette (async ASGI framework)
- **Database**: MariaDB 11.5
- **Port**: 8000 (container) / 8003 (host)
- **Language**: Python 3.13

## Database Schema

The service uses a MariaDB database with the following schema:

``````sql
CREATE TABLE Location (
  id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  picture VARCHAR(255)
);
``````

### Fields

- `id`: Unique identifier for the location
- `name`: Location name
- `description`: Detailed description of the location
- `picture`: URL to location's image

## API Endpoints

### GET /api/locations

Returns a list of all locations.

**Response**:
``````json
[
  {
    "id": 1,
    "name": "Gotham City",
    "description": "A dark and crime-ridden metropolis",
    "picture": "https://..."
  }
]
``````

### GET /api/locations/random_location

Returns a randomly selected location.

**Response**:
``````json
{
  "id": 42,
  "name": "Metropolis",
  "description": "A shining city of tomorrow",
  "picture": "https://..."
}
``````

### GET /api/locations/{id}

Returns a specific location by ID.

**Parameters**:
- `id` (path): Location ID

**Response**:
``````json
{
  "id": 1,
  "name": "Gotham City",
  "description": "A dark and crime-ridden metropolis",
  "picture": "https://..."
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

- `MYSQL_URL`: MySQL/MariaDB connection string
  - Default: `mysql://locations:locations@localhost/locations_database`
  - Format: `mysql://username:password@host:port/database`

## Database Connection

The service implements robust connection retry logic:

- **Retry Timeout**: 20 seconds
- **Retry Interval**: 0.5 seconds

Connection pooling is configured with:
- **Min Pool Size**: 1
- **Max Pool Size**: 10

## Implementation Details

### Startup Behavior

On startup, the service:
1. Parses the MYSQL_URL environment variable
2. Attempts to connect to MariaDB
3. Retries connection for up to 20 seconds
4. Creates connection pool
5. Verifies table exists

### URL Parsing

The service uses `urllib.parse.urlparse` to extract connection parameters from the MYSQL_URL:
- Host, port, username, password, and database name are all extracted automatically
- URL encoding/decoding is handled for special characters in credentials

## Running Locally

Using Docker Compose:
``````bash
docker compose up locations
``````

Standalone (requires MariaDB running):
``````bash
cd services/locations
pip install -r requirements.txt
MYSQL_URL=mysql://user:pass@localhost:3306/locations_database python main.py
``````

## Dependencies

See `requirements.txt`:
- `starlette` - ASGI framework
- `aiomysql` - MySQL/MariaDB async driver
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variable management

## Database Notes

This service demonstrates polyglot persistence by using MariaDB instead of PostgreSQL, showing how microservices can use different database technologies based on their specific requirements.

The MariaDB instance is configured with:
- User: `locations`
- Password: `locations`
- Database: `locations_database`
- Root password: `locations`
- Test database creation is skipped for security

## Health Check

The MariaDB container includes a health check that verifies:
- Database connectivity
- InnoDB engine initialization

This ensures the service doesn't start before the database is fully ready.
