# Python Super Heroes

A microservices-based application for managing superhero battles, built with Python and designed for performance optimization experiments.

## Overview

This project consists of four microservices:
- **Heroes Service**: Manages hero data (PostgreSQL)
- **Villains Service**: Manages villain data (PostgreSQL)
- **Locations Service**: Manages fight locations (MariaDB)
- **Fights Service**: Orchestrates battles between heroes and villains

## Quick Start

```bash
# Start all services
docker compose up -d

# Check service health
docker compose ps

# Run a load test
docker compose exec k6 k6 run /k6/load.js
```

## Performance Feedback Loop

This project implements a complete performance feedback loop for data-driven optimization. See [docs/PERFORMANCE_FEEDBACK_LOOP.md](docs/PERFORMANCE_FEEDBACK_LOOP.md) for details.

### Quick Performance Test

```bash
# Install Python dependencies
pip install requests

# Collect baseline performance data
python scripts/collect_performance_data.py \
  --rps 50 \
  --output k6/results/baseline.json \
  --report k6/results/baseline_report.md

# View the report
cat k6/results/baseline_report.md
```

### Making Data-Driven Optimizations

1. Collect baseline performance data
2. Identify bottlenecks from the metrics
3. Make targeted changes
4. Measure impact with comparison to baseline
5. Include performance data in PRs

See [.github/copilot/instructions/data-driven-optimization.md](.github/copilot/instructions/data-driven-optimization.md) for detailed guidance.

## Service Architecture

### Heroes Service (Port 8001)
- Endpoint: `/api/heroes`, `/api/heroes/{id}`, `/api/heroes/random_hero`
- Database: PostgreSQL
- Metrics: `/metrics` (Prometheus format)

### Villains Service (Port 8002)
- Endpoint: `/api/villains`, `/api/villains/{id}`, `/api/villains/random_villain`
- Database: PostgreSQL

### Locations Service (Port 8003)
- Endpoint: `/api/locations`, `/api/locations/{id}`, `/api/locations/random_location`
- Database: MariaDB

### Fights Service (Port 8004)
- Endpoint: `/api/fights/randomfighters`, `/api/fights/randomlocation`, `/api/fights/execute_fight`
- Orchestrates calls to heroes, villains, and locations services
- Metrics: `/metrics` (Prometheus format)

## Performance Instrumentation

Services are instrumented with Prometheus metrics:

```bash
# View heroes service metrics
curl http://localhost:8001/metrics

# View fights service metrics
curl http://localhost:8004/metrics
```

Available metrics:
- `http_requests_total`: Request count by method, endpoint, status
- `http_request_duration_seconds`: Request latency histogram
- `db_query_duration_seconds`: Database query timing
- `external_request_duration_seconds`: External service call timing

## Load Testing

k6 load tests are available at various RPS levels:

```bash
# Test at 10 RPS
docker compose exec k6 k6 run -e RAMPING_RATE=10 /k6/load.js

# Test at 50 RPS
docker compose exec k6 k6 run -e RAMPING_RATE=50 /k6/load.js

# Test at 100 RPS
docker compose exec k6 k6 run -e RAMPING_RATE=100 /k6/load.js
```

## GitHub Workflows

### Daily Performance Improver

An agentic workflow that:
1. Analyzes performance metrics
2. Identifies optimization opportunities
3. Makes data-driven improvements
4. Validates changes with before/after measurements

See [.github/workflows/daily-perf-improver.md](.github/workflows/daily-perf-improver.md) for details.

## Development

### Building Services

```bash
# Rebuild all services
docker compose up -d --build

# Rebuild specific service
docker compose up -d --build heroes
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f heroes
```

### Testing Services

```bash
# Manual API test
curl http://localhost:8004/api/fights/randomfighters

# Run k6 load test
docker compose exec k6 k6 run /k6/load.js
```

## Contributing

When making performance optimizations:

1. **Always measure first**: Establish baseline before making changes
2. **Use data to guide decisions**: Review metrics to identify actual bottlenecks
3. **Validate improvements**: Compare before/after performance data
4. **Document methodology**: Include measurement approach in PRs
5. **Watch for regressions**: Ensure other metrics don't degrade

See [.github/copilot/instructions/data-driven-optimization.md](.github/copilot/instructions/data-driven-optimization.md) for detailed guidance.

## Performance Guides

- [Performance Feedback Loop](docs/PERFORMANCE_FEEDBACK_LOOP.md)
- [Data-Driven Optimization](.github/copilot/instructions/data-driven-optimization.md)
- [Load Testing Best Practices](.github/copilot/instructions/load-testing.md)
- [API Performance](.github/copilot/instructions/api-performance.md)
- [Database Performance](.github/copilot/instructions/database-performance.md)
- [Microservices Performance](.github/copilot/instructions/microservices-performance.md)
- [Profiling Python](.github/copilot/instructions/profiling-python.md)

## License

MIT
