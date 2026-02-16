# Development Guide

This guide covers development workflows, best practices, and contribution guidelines for the Python Super Heroes project.

## Development Setup

### Prerequisites

- Python 3.13 or later
- Docker and Docker Compose
- Git
- A code editor (VS Code, PyCharm, etc.)

### Local Development Environment

1. Clone the repository:
   ``````bash
   git clone https://github.com/flyaruu/python-super-heroes.git
   cd python-super-heroes
   ``````

2. Start the databases:
   ``````bash
   docker compose up -d heroes-db villains-db locations-db fights-db
   ``````

3. Set up Python virtual environment:
   ``````bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ``````

4. Install dependencies for a specific service:
   ``````bash
   cd services/heroes
   pip install -r requirements.txt
   ``````

5. Run the service locally:
   ``````bash
   DATABASE_URL=postgres://superman:superman@localhost:5432/heroes_database python main.py
   ``````

## Project Structure

``````
python-super-heroes/
├── .github/
│   └── workflows/         # GitHub Actions workflows
├── compose.yml           # Docker Compose configuration
├── database/            # Database initialization scripts
│   ├── fights-db/      # MongoDB init
│   ├── heroes-db/      # PostgreSQL heroes
│   ├── villains-db/    # PostgreSQL villains
│   └── locations-db/   # MariaDB locations
├── docs/               # Documentation
│   └── services/       # Service-specific docs
├── k6/                # Load testing scripts
│   ├── load.js       # Main load test
│   ├── randomFight.js # Fight test module
│   └── results/      # Test results output
├── k6-image/         # Custom k6 Docker image
└── services/         # Microservices
    ├── fights/      # Fights orchestration service
    ├── heroes/      # Heroes data service
    ├── villains/    # Villains data service
    └── locations/   # Locations data service
``````

## Code Style and Standards

### Python Style Guide

This project follows [PEP 8](https://pep8.org/) with the following specifics:

- **Line Length**: 120 characters maximum
- **Imports**: Grouped and sorted (standard library, third-party, local)
- **Type Hints**: Recommended but not required
- **Docstrings**: Use for public functions and classes

### Formatting

Use `black` for consistent formatting:
``````bash
pip install black
black services/heroes/main.py
``````

### Linting

Use `ruff` for fast linting:
``````bash
pip install ruff
ruff check services/heroes/
``````

## Testing

### Manual Testing

Use curl or httpie to test endpoints:

``````bash
# Get all heroes
curl http://localhost:8001/api/heroes

# Get random hero
curl http://localhost:8001/api/heroes/random_hero

# Get specific hero
curl http://localhost:8001/api/heroes/1
``````

### Load Testing

Run k6 tests during development:
``````bash
docker compose exec k6 k6 run -e RAMPING_RATE=1 /k6/load.js
``````

## Making Changes

### Adding a New Endpoint

1. Edit the service file (e.g., `services/heroes/main.py`)
2. Add the route handler:
   ``````python
   async def new_endpoint(request: Request) -> JSONResponse:
       # Implementation
       return JSONResponse({"result": "data"})
   ``````

3. Register the route:
   ``````python
   routes = [
       # ... existing routes
       Route("/api/heroes/new_endpoint", new_endpoint, methods=["GET"]),
   ]
   ``````

4. Test locally
5. Update documentation in `docs/services/`
6. Create a pull request

### Modifying Database Schema

⚠️ **Warning**: Schema changes require coordination across services.

1. Update initialization script (e.g., `database/heroes-db/init/heroes.sql`)
2. Update service code to handle new fields
3. Test with fresh database:
   ``````bash
   docker compose down -v  # Removes volumes
   docker compose up -d
   ``````

4. Document schema changes in service documentation

### Adding Dependencies

1. Add to `requirements.txt`:
   ``````bash
   echo "new-package==1.2.3" >> services/heroes/requirements.txt
   ``````

2. Rebuild Docker image:
   ``````bash
   docker compose build heroes
   ``````

3. Test the updated service

## Debugging

### Service Logs

View logs for a specific service:
``````bash
docker compose logs -f heroes
``````

View logs for all services:
``````bash
docker compose logs -f
``````

### Database Access

Connect to databases for debugging:

**PostgreSQL (Heroes)**:
``````bash
docker compose exec heroes-db psql -U superman -d heroes_database
``````

**PostgreSQL (Villains)**:
``````bash
docker compose exec villains-db psql -U superman -d villains_database
``````

**MariaDB (Locations)**:
``````bash
docker compose exec locations-db mysql -u locations -plocations locations_database
``````

**MongoDB (Fights)**:
``````bash
docker compose exec fights-db mongosh -u super -p super fights
``````

### Python Debugger

Add breakpoints using `pdb`:
``````python
import pdb; pdb.set_trace()
``````

Or use your IDE's debugger by running the service outside Docker.

## Common Development Tasks

### Reset All Databases

``````bash
docker compose down -v
docker compose up -d
``````

### Rebuild All Services

``````bash
docker compose build
docker compose up -d
``````

### Update a Single Service

``````bash
docker compose up -d --build heroes
``````

### Check Service Health

``````bash
docker compose ps
curl http://localhost:8001/api/heroes
``````

## Git Workflow

### Branch Naming

- Features: `feature/description`
- Bug fixes: `fix/description`
- Documentation: `docs/description`
- Refactoring: `refactor/description`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

``````
feat: add new endpoint for hero search
fix: correct database connection retry logic
docs: update API documentation
refactor: simplify fight logic
``````

### Pull Request Process

1. Create feature branch from `main`
2. Make changes and commit
3. Push to GitHub
4. Create pull request with clear description
5. Wait for review and CI checks
6. Address feedback
7. Merge when approved

## Performance Optimization

### Database Queries

- Use connection pooling (already configured)
- Index frequently queried fields
- Avoid N+1 queries
- Use `EXPLAIN` to analyze query performance

### Service Response Times

- Use async/await consistently
- Minimize external service calls
- Implement caching where appropriate
- Monitor response times with k6

### Resource Usage

Monitor container resources:
``````bash
docker stats
``````

## Troubleshooting Development Issues

### Service Won't Start

1. Check logs: `docker compose logs servicename`
2. Verify database is healthy: `docker compose ps`
3. Check port conflicts: `netstat -tulpn | grep PORT`
4. Rebuild image: `docker compose build servicename`

### Database Connection Errors

1. Verify database is running: `docker compose ps`
2. Check connection string format
3. Test direct database connection
4. Check network connectivity: `docker compose exec heroes ping heroes-db`

### Import Errors

1. Verify dependencies: `pip list`
2. Reinstall requirements: `pip install -r requirements.txt`
3. Check Python version: `python --version`

## Contributing

### Code Review Checklist

- [ ] Code follows PEP 8 style guide
- [ ] All endpoints are documented
- [ ] Manual testing completed
- [ ] Load tests pass
- [ ] No sensitive data in code
- [ ] Commit messages are clear
- [ ] Documentation updated

### Getting Help

- Check existing documentation
- Review GitHub issues
- Ask in pull request comments
- Contact maintainers

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Starlette Documentation](https://www.starlette.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [k6 Documentation](https://k6.io/docs/)
- [AsyncPG Documentation](https://magicstack.github.io/asyncpg/)
