# Database Performance Guide

## Understanding This Stack

**Databases:**
- Heroes/Villains: PostgreSQL 16 with asyncpg (async connection pool)
- Locations: MariaDB 11.5 with aiomysql (async MySQL driver)
- Fights: MongoDB 7.0 (document store)

**Common issue:** Random selection uses `ORDER BY RANDOM()` / `RAND()` - this is slow!

## Optimizing Random Queries

**Current slow approach:**
```sql
-- PostgreSQL (heroes, villains)
SELECT * FROM heroes ORDER BY RANDOM() LIMIT 1;

-- MariaDB (locations)
SELECT * FROM locations ORDER BY RAND() LIMIT 1;
```

**Problem:** Full table scan + sort every time. Not cacheable. Slow with >1000 rows.

**Fast alternative 1: Random ID selection**
```python
# Get max ID once (can cache for minutes)
max_id = await conn.fetchval("SELECT MAX(id) FROM heroes")

# Pick random ID, find nearest row
random_id = random.randint(1, max_id)
hero = await conn.fetchrow(
    "SELECT * FROM heroes WHERE id >= $1 LIMIT 1", 
    random_id
)
# Uses primary key index - 10-50x faster
```

**Fast alternative 2: Pre-cached random sample**
```python
# On startup or every 5 minutes
RANDOM_SAMPLE = await conn.fetch("SELECT * FROM heroes ORDER BY RANDOM() LIMIT 100")

# On each request
return random.choice(RANDOM_SAMPLE)
# Near-zero database load
```

## Connection Pool Configuration

**Current settings (services/heroes/main.py):**
```python
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=10,
    max_size=50
)
```

**How to tune:**
1. **Measure actual concurrency:** Add logging in endpoints
   ```python
   logger.info(f"Pool: {pool.get_size()}/{pool.get_max_size()}")
   ```
2. **Watch for pool exhaustion:** If `get_size() == max_size` often, increase pool
3. **Database limits:** Check `max_connections` setting
   ```sql
   SHOW max_connections;  -- PostgreSQL/MariaDB
   ```

**Guidelines:**
- Min size: Expected baseline concurrency (10-20 for this app)
- Max size: Peak concurrent requests × 1.2
- Never exceed database `max_connections / number_of_service_instances`

## Index Optimization

**Check if indexes are being used:**
```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT * FROM heroes WHERE id >= 42 LIMIT 1;

-- Look for "Index Scan" vs "Seq Scan"
-- Seq Scan = bad (full table scan)
-- Index Scan = good (using index)
```

**This app's schema:** Primary keys are indexed by default. No additional indexes needed unless adding filters.

## Query Performance Monitoring

**Enable slow query logging (PostgreSQL):**
```bash
docker compose exec heroes-db psql -U superman -d heroes_database
ALTER DATABASE heroes_database SET log_min_duration_statement = 100;
-- Logs queries >100ms
```

**View slow queries:**
```bash
docker compose logs heroes-db | grep "duration:"
```

## Database-Specific Tips

**PostgreSQL (asyncpg):**
- Connection pool is excellent, uses binary protocol
- `EXPLAIN ANALYZE` for query planning
- Consider `pg_stat_statements` extension for production

**MariaDB (aiomysql):**
- Pool configuration: `pool_recycle=3600` (reconnect hourly)
- Watch for connection timeouts under low load
- `SHOW PROCESSLIST` to see active queries

**MongoDB (fights):**
- Document-based storage, no random query issue
- Default connection handling is fine for this use case
- Use indexes on frequently queried fields
