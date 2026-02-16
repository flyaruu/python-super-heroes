# Troubleshooting

This guide helps you diagnose and fix common issues with the Python Super Heroes application.

## Common Issues

### Services Won't Start

#### Symptom
Services exit immediately or show "Exited" status.

#### Diagnosis
``````bash
docker compose ps
docker compose logs servicename
``````

#### Solutions

**1. Port Already in Use**
``````bash
# Find process using the port
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Stop the conflicting process or change the port in compose.yml
``````

**2. Database Not Ready**
Wait for health checks to pass:
``````bash
docker compose ps
# Wait until STATUS shows "healthy" for databases
``````

**3. Build Errors**
Rebuild from scratch:
``````bash
docker compose down
docker compose build --no-cache
docker compose up -d
``````

### Database Connection Failures

#### Symptom
Service logs show "Could not connect to database" or connection timeout errors.

#### Diagnosis
``````bash
# Check if database container is running
docker compose ps

# Check database logs
docker compose logs heroes-db

# Test database connectivity
docker compose exec heroes-db pg_isready -U superman
``````

#### Solutions

**1. Database Not Initialized**
``````bash
# Restart with fresh databases
docker compose down -v
docker compose up -d
``````

**2. Wrong Credentials**
Verify environment variables in `compose.yml` match the service configuration.

**3. Network Issues**
``````bash
# Recreate networks
docker compose down
docker compose up -d
``````

### API Returns 502 Bad Gateway

#### Symptom
Fights Service returns 502 when calling other services.

#### Diagnosis
``````bash
# Check if all services are running
docker compose ps

# Test each service individually
curl http://localhost:8001/api/heroes
curl http://localhost:8002/api/villains
curl http://localhost:8003/api/locations
``````

#### Solutions

**1. Downstream Service Down**
Start the failed service:
``````bash
docker compose up -d heroes
``````

**2. Service Not Responding**
Check service logs for errors:
``````bash
docker compose logs heroes
``````

Restart the service:
``````bash
docker compose restart heroes
``````

### Empty API Responses

#### Symptom
API returns `[]` or `{"detail": "Not found"}`.

#### Diagnosis
``````bash
# Check if database has data
docker compose exec heroes-db psql -U superman -d heroes_database -c "SELECT COUNT(*) FROM Hero;"
``````

#### Solutions

**1. Database Not Initialized**
``````bash
docker compose down -v
docker compose up -d
# Wait 30 seconds for initialization
``````

**2. Initialization Script Failed**
``````bash
# Check database logs for errors
docker compose logs heroes-db

# Manually verify init script
docker compose exec heroes-db cat /docker-entrypoint-initdb.d/init.sql
``````

### Load Tests Failing

#### Symptom
k6 tests report threshold violations or high error rates.

#### Diagnosis
``````bash
# Check service resource usage
docker stats

# Review service logs during test
docker compose logs -f fights
``````

#### Solutions

**1. System Overloaded**
- Reduce `RAMPING_RATE`
- Increase `maxVUs` in k6 config
- Allocate more resources to Docker

**2. Database Connection Pool Exhausted**
Edit service code to increase pool size:
``````python
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=20,    # Increase
    max_size=100    # Increase
)
``````

**3. Slow Queries**
Check database performance:
``````bash
docker compose exec heroes-db psql -U superman -d heroes_database -c "SELECT * FROM Hero ORDER BY random() LIMIT 1;"
``````

### Docker Compose Commands Hanging

#### Symptom
`docker compose up` or other commands hang indefinitely.

#### Diagnosis
``````bash
# Check Docker daemon status
docker ps

# Check Docker disk space
docker system df
``````

#### Solutions

**1. Docker Daemon Issues**
Restart Docker:
``````bash
# macOS/Windows: Restart Docker Desktop
# Linux:
sudo systemctl restart docker
``````

**2. Disk Space Full**
Clean up Docker resources:
``````bash
docker system prune -a
docker volume prune
``````

### Permission Denied Errors

#### Symptom
"Permission denied" when accessing database initialization scripts.

#### Diagnosis
``````bash
ls -la database/heroes-db/init/
``````

#### Solutions

**1. File Permissions**
``````bash
chmod 644 database/heroes-db/init/heroes.sql
``````

**2. SELinux Context (Linux)**
``````bash
chcon -Rt svirt_sandbox_file_t database/
``````

### Service Crashes Under Load

#### Symptom
Services exit or restart during load testing.

#### Diagnosis
``````bash
# Check for OOM kills
docker compose logs heroes | grep -i "killed"

# Monitor resource usage
docker stats
``````

#### Solutions

**1. Memory Limit Reached**
Increase memory limits in `compose.yml`:
``````yaml
services:
  heroes:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
``````

**2. Too Many Connections**
Reduce connection pool size or implement rate limiting.

## Database-Specific Issues

### PostgreSQL: Too Many Connections

#### Symptom
`FATAL: sorry, too many clients already`

#### Solutions
``````bash
# Reduce pool size in service code
# Or increase max_connections in PostgreSQL

docker compose exec heroes-db psql -U superman -d heroes_database -c "ALTER SYSTEM SET max_connections = 200;"
docker compose restart heroes-db
``````

### MariaDB: Can't Connect to MySQL Server

#### Symptom
`ERROR 2002 (HY000): Can't connect to MySQL server`

#### Solutions
``````bash
# Wait for MariaDB to fully initialize
docker compose logs locations-db

# Check health status
docker compose ps locations-db

# Restart if stuck
docker compose restart locations-db
``````

### MongoDB: Authentication Failed

#### Symptom
`MongoServerError: Authentication failed`

#### Solutions
Verify credentials in `compose.yml`:
``````yaml
fights-db:
  environment:
    MONGO_INITDB_ROOT_USERNAME: super
    MONGO_INITDB_ROOT_PASSWORD: super
``````

## Performance Issues

### Slow Response Times

#### Diagnosis
``````bash
# Test individual services
time curl http://localhost:8001/api/heroes/random_hero
time curl http://localhost:8004/api/fights/execute_fight
``````

#### Solutions

**1. Database Query Optimization**
Add indexes to frequently queried columns.

**2. Connection Pooling**
Ensure connection pools are properly configured.

**3. Service Resource Limits**
Remove or increase resource limits.

### High CPU Usage

#### Diagnosis
``````bash
docker stats
``````

#### Solutions

**1. Reduce Load**
Lower k6 `RAMPING_RATE`.

**2. Scale Services**
Run multiple instances:
``````bash
docker compose up -d --scale heroes=3
``````

**3. Optimize Code**
Profile code to find bottlenecks.

## Networking Issues

### Services Can't Communicate

#### Symptom
`httpx.RequestError: [Errno -2] Name or service not known`

#### Solutions

**1. Verify Network**
``````bash
docker compose exec fights ping heroes
``````

**2. Recreate Network**
``````bash
docker compose down
docker compose up -d
``````

**3. Check Service Names**
Ensure service URLs match service names in `compose.yml`.

## Development Environment Issues

### Changes Not Reflected

#### Symptom
Code changes don't appear in running service.

#### Solutions

**1. Rebuild Image**
``````bash
docker compose up -d --build heroes
``````

**2. Volume Caching**
Add volume mounts for live reload (not recommended for production):
``````yaml
heroes:
  volumes:
    - ./services/heroes:/app
``````

### Import Errors

#### Symptom
`ModuleNotFoundError: No module named 'fastapi'`

#### Solutions

**1. Rebuild Container**
``````bash
docker compose build heroes
``````

**2. Verify requirements.txt**
Check that all dependencies are listed.

**3. Check Python Version**
Ensure Dockerfile uses correct Python version.

## Getting More Help

### Enable Debug Logging

Edit service code to increase log level:
``````python
logging.basicConfig(level=logging.DEBUG)
``````

### Collect Diagnostic Information

``````bash
# System information
docker version
docker compose version
uname -a  # Linux/macOS
systeminfo  # Windows

# Service status
docker compose ps -a

# Logs
docker compose logs > debug.log

# Resource usage
docker stats --no-stream > stats.txt
``````

### Report Issues

When reporting issues, include:
1. Error messages and stack traces
2. Service logs
3. Steps to reproduce
4. Environment details (OS, Docker version)
5. `docker compose ps` output

## Quick Fixes Checklist

When things go wrong, try these in order:

1. ☐ Check logs: `docker compose logs`
2. ☐ Verify all services running: `docker compose ps`
3. ☐ Restart services: `docker compose restart`
4. ☐ Rebuild images: `docker compose build`
5. ☐ Remove volumes and restart: `docker compose down -v && docker compose up -d`
6. ☐ Clean Docker system: `docker system prune`
7. ☐ Restart Docker daemon
8. ☐ Check GitHub issues for similar problems
