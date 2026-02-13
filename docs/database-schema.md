# Database Schema Reference

This document provides comprehensive documentation of all database schemas used in the Python Super Heroes system.

## Overview

The system uses **polyglot persistence** with three different database technologies:

- **PostgreSQL 16**: Heroes and Villains data (relational)
- **MariaDB 11.5**: Locations data (relational)
- **MongoDB 7.0**: Fight results (document)

## Heroes Database (PostgreSQL)

### Connection Details

- **Host**: `localhost:5432` (or `heroes-db:5432` in Docker)
- **Database**: `heroes_database`
- **User**: `superman`
- **Driver**: `asyncpg`

### Schema

``````sql
CREATE SEQUENCE hero_seq START 1 INCREMENT 50;

CREATE TABLE Hero (
  id int8 NOT NULL,
  level int4 NOT NULL,
  name VARCHAR(50) NOT NULL,
  otherName VARCHAR(255),
  picture VARCHAR(255),
  powers TEXT,
  PRIMARY KEY (id)
);
``````

### Field Descriptions

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | bigint | No | Unique identifier (auto-generated from sequence) |
| `name` | varchar(50) | No | Hero's primary name |
| `otherName` | varchar(255) | Yes | Alternate identity/civilian name |
| `level` | integer | No | Power level (1-286000) for fight comparisons |
| `picture` | varchar(255) | Yes | URL to hero image |
| `powers` | text | Yes | Comma-separated list of superpowers |

### Sample Data

``````sql
INSERT INTO hero(id, name, otherName, picture, powers, level)
VALUES (
  nextval('hero_seq'),
  'Yoda',
  '',
  'https://raw.githubusercontent.com/quarkusio/.../yoda.jpg',
  'Acrobatics, Agility, Telekinesis, The Force, ...',
  286000
);
``````

### Indexes

- Primary key index on `id`
- Consider adding indexes on:
  - `level` for performance queries
  - `name` for search functionality

### Data Statistics

- **Record Count**: 100 heroes
- **Level Range**: 22 - 286,000
- **Average Powers**: 10-30 per hero

## Villains Database (PostgreSQL)

### Connection Details

- **Host**: `localhost:5433` (or `villains-db:5432` in Docker)
- **Database**: `villains_database`
- **User**: `lex_luthor`
- **Driver**: `asyncpg`

### Schema

``````sql
CREATE SEQUENCE villain_seq START 1 INCREMENT 50;

CREATE TABLE Villain (
  id int8 NOT NULL,
  level int4 NOT NULL,
  name VARCHAR(50) NOT NULL,
  otherName VARCHAR(255),
  picture VARCHAR(255),
  powers TEXT,
  PRIMARY KEY (id)
);
``````

### Field Descriptions

Identical structure to Heroes table:

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | bigint | No | Unique identifier (auto-generated from sequence) |
| `name` | varchar(50) | No | Villain's primary name |
| `otherName` | varchar(255) | Yes | Alternate identity/civilian name |
| `level` | integer | No | Power level (1-286000) for fight comparisons |
| `picture` | varchar(255) | Yes | URL to villain image |
| `powers` | text | Yes | Comma-separated list of powers |

### Data Statistics

- **Record Count**: 100 villains
- **Level Range**: Similar to heroes
- **Data Source**: quarkus-super-heroes character database

## Locations Database (MariaDB)

### Connection Details

- **Host**: `localhost:3306` (or `locations-db:3306` in Docker)
- **Database**: `locations_database`
- **User**: `location_master`
- **Driver**: `aiomysql`

### Schema

``````sql
CREATE TABLE locations (
  id bigint NOT NULL AUTO_INCREMENT,
  name VARCHAR(50) NOT NULL,
  description TEXT,
  picture VARCHAR(255),
  type ENUM('CITY', 'PLANET', 'PLACE', 'ISLAND', 'COUNTRY', 'MOON') NOT NULL,
  PRIMARY KEY (id),
  CONSTRAINT UK_name UNIQUE (name)
) ENGINE=InnoDB;
``````

### Field Descriptions

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | bigint | No | Auto-incrementing unique identifier |
| `name` | varchar(50) | No | Location name (unique) |
| `description` | text | Yes | Detailed description of location |
| `picture` | varchar(255) | Yes | URL to location image |
| `type` | enum | No | Location category |

### Location Types

| Type | Description | Examples |
|------|-------------|----------|
| `CITY` | Urban locations | Gotham City, Metropolis |
| `PLANET` | Planetary bodies | Earth, Krypton, Sakaar |
| `PLACE` | General locations | Asgard, The Savage Land |
| `ISLAND` | Island locations | Themyscira, Genosha |
| `COUNTRY` | Country-level areas | Wakanda, Latveria |
| `MOON` | Lunar/satellite locations | (Future expansion) |

### Sample Data

``````sql
INSERT INTO locations(name, description, picture, type)
VALUES (
  'Gotham City',
  'An American city rife with corruption and crime, the home of its iconic protector Batman.',
  'https://raw.githubusercontent.com/.../gotham_city.jpg',
  'CITY'
);
``````

### Constraints

- **UK_name**: Unique constraint on `name` field
- **PRIMARY KEY**: Auto-increment on `id`
- **ENGINE**: InnoDB for transaction support

### Data Statistics

- **Record Count**: 20+ locations
- **Type Distribution**:
  - CITY: ~40%
  - PLANET: ~30%
  - PLACE: ~25%
  - Other: ~5%

## Fights Database (MongoDB)

### Connection Details

- **Host**: `localhost:27017` (or `fights-db:27017` in Docker)
- **Database**: `fights`
- **User**: `super`
- **Collection**: `fight_results`

### Document Schema

``````json
{
  "_id": ObjectId("..."),
  "fightId": "550e8400-e29b-41d4-a716-446655440000",
  "hero": {
    "id": 1,
    "name": "Superman",
    "level": 95
  },
  "villain": {
    "id": 2,
    "name": "Lex Luthor",
    "level": 85
  },
  "location": {
    "id": 1,
    "name": "Metropolis",
    "type": "CITY"
  },
  "winner": "hero",
  "winnerName": "Superman",
  "fightDate": ISODate("2026-02-13T13:38:00Z")
}
``````

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Yes | MongoDB auto-generated ID |
| `fightId` | String (UUID) | Yes | Unique fight identifier |
| `hero` | Object | Yes | Hero participant details |
| `hero.id` | Integer | Yes | Hero database ID |
| `hero.name` | String | Yes | Hero name |
| `hero.level` | Integer | Yes | Hero power level |
| `villain` | Object | Yes | Villain participant details |
| `villain.id` | Integer | Yes | Villain database ID |
| `villain.name` | String | Yes | Villain name |
| `villain.level` | Integer | Yes | Villain power level |
| `location` | Object | Yes | Fight location details |
| `location.id` | Integer | Yes | Location database ID |
| `location.name` | String | Yes | Location name |
| `location.type` | String | Yes | Location type enum value |
| `winner` | String | Yes | "hero" or "villain" |
| `winnerName` | String | Yes | Name of winning character |
| `fightDate` | ISODate | Yes | Timestamp of fight execution |

### Indexes (Recommended)

``````javascript
// Index for querying by fight date
db.fight_results.createIndex({ "fightDate": -1 })

// Index for winner analysis
db.fight_results.createIndex({ "winner": 1 })

// Compound index for hero/villain stats
db.fight_results.createIndex({ "hero.id": 1, "villain.id": 1 })

// Unique index on fightId
db.fight_results.createIndex({ "fightId": 1 }, { unique: true })
``````

### Example Queries

**Find all fights won by a specific hero**:
``````javascript
db.fight_results.find({ "winner": "hero", "hero.id": 1 })
``````

**Get fight statistics**:
``````javascript
db.fight_results.aggregate([
  {
    $group: {
      _id: "$winner",
      count: { $sum: 1 }
    }
  }
])
``````

**Recent fights**:
``````javascript
db.fight_results.find()
  .sort({ "fightDate": -1 })
  .limit(10)
``````

## Database Initialization

### Heroes Database

Initialization script: `database/heroes-db/init/heroes.sql`

- Creates sequence and table
- Inserts 100 hero records
- Automatically runs on container startup

### Villains Database

Initialization script: `database/villains-db/init/villains.sql`

- Creates sequence and table
- Inserts 100 villain records
- Automatically runs on container startup

### Locations Database

Initialization script: `database/locations-db/init/initialize-tables.sql`

- Creates table with constraints
- Inserts 20+ location records
- Automatically runs on container startup

### Fights Database

Initialization script: `database/fights-db/initialize-database.js`

- Creates database
- Creates collection (on first insert)
- No pre-populated data

## Connection Pooling

All services use connection pooling for optimal performance:

### PostgreSQL (Heroes/Villains)

``````python
pool = await asyncpg.create_pool(
    dsn=DATABASE_URL,
    min_size=10,  # Minimum connections
    max_size=50   # Maximum connections
)
``````

### MariaDB (Locations)

``````python
pool = await aiomysql.create_pool(
    host='locations-db',
    port=3306,
    user='location_master',
    password='location_master',
    db='locations_database',
    minsize=1,
    maxsize=10
)
``````

## Backup and Recovery

### PostgreSQL Backup

``````bash
# Backup heroes database
docker exec heroes-db pg_dump -U superman heroes_database > heroes_backup.sql

# Restore
docker exec -i heroes-db psql -U superman heroes_database < heroes_backup.sql
``````

### MariaDB Backup

``````bash
# Backup locations database
docker exec locations-db mysqldump -u location_master -plocation_master locations_database > locations_backup.sql

# Restore
docker exec -i locations-db mysql -u location_master -plocation_master locations_database < locations_backup.sql
``````

### MongoDB Backup

``````bash
# Backup fights database
docker exec fights-db mongodump --db fights --out /backup

# Restore
docker exec fights-db mongorestore --db fights /backup/fights
``````

## Migration Strategy

For schema changes, implement versioned migration scripts:

``````
database/
├── heroes-db/
│   └── migrations/
│       ├── V1__initial_schema.sql
│       ├── V2__add_team_field.sql
│       └── V3__add_indexes.sql
``````

Consider using migration tools:
- **Alembic** for PostgreSQL (Python)
- **Flyway** or **Liquibase** for cross-database migrations

## Performance Tuning

### PostgreSQL

``````sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM hero WHERE level > 5000;

-- Update statistics
ANALYZE hero;

-- Create indexes
CREATE INDEX idx_hero_level ON hero(level);
``````

### MariaDB

``````sql
-- Check slow queries
SHOW FULL PROCESSLIST;

-- Optimize table
OPTIMIZE TABLE locations;

-- Add index
CREATE INDEX idx_location_type ON locations(type);
``````

### MongoDB

``````javascript
// Check index usage
db.fight_results.explain("executionStats").find({ winner: "hero" })

// Create compound index
db.fight_results.createIndex({ "hero.level": 1, "villain.level": 1 })
``````

## Security Considerations

### Development vs Production

**Current (Development)**:
- Default passwords
- No SSL/TLS
- Root access enabled

**Production Recommendations**:
- Strong passwords (secrets management)
- SSL/TLS encryption for connections
- Least-privilege user accounts
- Network isolation
- Regular security updates

### Credential Management

Use environment variables or secrets managers:

``````bash
# Development
export DB_PASSWORD="superman"

# Production (Kubernetes)
kubectl create secret generic db-credentials \
  --from-literal=username=superman \
  --from-literal=password=<strong-password>
``````

## Monitoring

### Health Checks

All databases have health checks configured in `compose.yml`:

``````yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U superman"]
  interval: 10s
  timeout: 5s
  retries: 20
``````

### Monitoring Queries

**PostgreSQL Connections**:
``````sql
SELECT count(*) FROM pg_stat_activity;
``````

**MariaDB Connections**:
``````sql
SHOW STATUS LIKE 'Threads_connected';
``````

**MongoDB Status**:
``````javascript
db.serverStatus()
``````

## Data Source Attribution

Character data sourced from the [Quarkus Super Heroes](https://github.com/quarkusio/quarkus-super-heroes) project character database.
