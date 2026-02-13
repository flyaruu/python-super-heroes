# Configuration

This document describes all configuration options for the Python Super Heroes application.

## Environment Variables

### Heroes Service

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://superman:superman@heroes-db:5432/heroes_database` |

**Format**: `postgres://username:password@host:port/database`

### Villains Service

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://superman:superman@villains-db:5432/villains_database` |

**Format**: `postgres://username:password@host:port/database`

### Locations Service

| Variable | Description | Default |
|----------|-------------|---------|
| `MYSQL_URL` | MariaDB connection string | `mysql://locations:locations@localhost/locations_database` |

**Format**: `mysql://username:password@host:port/database`

### Fights Service

The Fights Service uses hardcoded service URLs for Docker Compose networking:
- Heroes: `http://heroes:8000`
- Villains: `http://villains:8000`
- Locations: `http://locations:8000`

### k6 Load Testing

| Variable | Description | Default |
|----------|-------------|---------|
| `K6_HOST` | Base URL for Fights Service | `http://fights:8000` |
| `RAMPING_RATE` | Target requests per second | Varies by test |

## Docker Compose Configuration

### Port Mappings

| Service | Container Port | Host Port |
|---------|---------------|-----------|
| Heroes Service | 8000 | 8001 |
| Villains Service | 8000 | 8002 |
| Locations Service | 8000 | 8003 |
| Fights Service | 8000 | 8004 |
| Heroes DB (PostgreSQL) | 5432 | 5432 |
| Villains DB (PostgreSQL) | 5432 | 5433 |
| Locations DB (MariaDB) | 3306 | 3306 |
| Fights DB (MongoDB) | 27017 | 27017 |

### Database Credentials

#### Heroes Database (PostgreSQL)

- **User**: `superman`
- **Password**: `superman`
- **Database**: `heroes_database`
- **Port**: 5432

#### Villains Database (PostgreSQL)

- **User**: `superman`
- **Password**: `superman`
- **Database**: `villains_database`
- **Port**: 5433 (host) / 5432 (container)

#### Locations Database (MariaDB)

- **User**: `locations`
- **Password**: `locations`
- **Root Password**: `locations`
- **Database**: `locations_database`
- **Port**: 3306

#### Fights Database (MongoDB)

- **User**: `super`
- **Password**: `super`
- **Database**: `fights`
- **Port**: 27017

## Database Initialization

### Heroes Database

Initialized with SQL script: `database/heroes-db/init/heroes.sql`
- Creates `Hero` table
- Inserts 100 sample heroes

### Villains Database

Initialized with SQL script: `database/villains-db/init/villains.sql`
- Creates `Villain` table
- Inserts 100 sample villains

### Locations Database

Initialized with SQL script: `database/locations-db/init/initialize-tables.sql`
- Creates `Location` table
- Inserts sample locations

### Fights Database

Initialized with JavaScript: `database/fights-db/initialize-database.js`
- Creates necessary collections
- Sets up indexes

## Service Dependencies

Docker Compose manages service startup order with health checks:

``````yaml
heroes:
  depends_on:
    heroes-db:
      condition: service_healthy

villains:
  depends_on:
    villains-db:
      condition: service_healthy

locations:
  depends_on:
    locations-db:
      condition: service_healthy

fights:
  depends_on:
    - fights-db
``````

## Health Checks

### PostgreSQL (Heroes & Villains)

``````yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U superman"]
  interval: 10s
  timeout: 5s
  retries: 20
``````

### MariaDB (Locations)

``````yaml
healthcheck:
  test: ["CMD", "healthcheck.sh", "--connect", "--innodb_initialized"]
  interval: 10s
  timeout: 5s
  retries: 20
``````

## Connection Pooling

### PostgreSQL Services (Heroes, Villains)

``````python
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=10,
    max_size=50
)
``````

### MariaDB Service (Locations)

``````python
pool = await aiomysql.create_pool(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    db=DB_NAME,
    minsize=1,
    maxsize=10
)
``````

## Connection Retry Logic

### Heroes & Villains Services

- **Timeout**: 10 seconds
- **Interval**: 0.5 seconds

### Locations Service

- **Timeout**: 20 seconds
- **Interval**: 0.5 seconds

## Volumes

### Database Data Persistence

By default, database data is **not persisted** across container restarts. To enable persistence, add volume mounts:

``````yaml
services:
  heroes-db:
    volumes:
      - heroes-data:/var/lib/postgresql/data
      - ./database/heroes-db/init/heroes.sql:/docker-entrypoint-initdb.d/init.sql:ro

volumes:
  heroes-data:
``````

### Load Test Results

``````yaml
k6:
  volumes:
    - ./k6:/k6:ro
    - ./k6/results:/results
``````

Results are written to `k6/results/` on the host machine.

## Network Configuration

All services use the default Docker Compose network, allowing services to communicate using service names as hostnames:
- `heroes:8000`
- `villains:8000`
- `locations:8000`
- `fights:8000`

## Security Considerations

⚠️ **Warning**: This configuration uses default credentials and is intended for **development only**.

For production deployments:
1. Use strong, unique passwords
2. Store credentials in environment files or secrets management
3. Enable TLS/SSL for database connections
4. Implement authentication for service APIs
5. Use network policies to restrict service communication
6. Enable audit logging

## Customizing Configuration

### Using .env Files

Create a `.env` file in the project root:

``````env
# Heroes Service
HEROES_DB_PASSWORD=my-secure-password

# Villains Service
VILLAINS_DB_PASSWORD=another-secure-password

# Locations Service
LOCATIONS_DB_PASSWORD=yet-another-password
``````

Update `compose.yml` to use these variables:

``````yaml
services:
  heroes-db:
    environment:
      POSTGRES_PASSWORD: ${HEROES_DB_PASSWORD}
``````

### Override Files

Create `compose.override.yml` for local customizations:

``````yaml
services:
  heroes:
    environment:
      DATABASE_URL: "postgres://myuser:mypass@heroes-db:5432/heroes_database"
``````

Docker Compose automatically merges this with `compose.yml`.
