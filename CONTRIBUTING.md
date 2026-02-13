# Contributing to Python Super Heroes

Thank you for considering contributing to Python Super Heroes! This document provides guidelines and workflows for contributing.

## Getting Started

### Prerequisites

Before you begin, ensure you have:
- Docker 20.10+ and Docker Compose 2.0+
- Git 2.30+
- Python 3.11+ (for local development)
- A GitHub account

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork:
   ``````bash
   git clone https://github.com/YOUR-USERNAME/python-super-heroes.git
   cd python-super-heroes
   ``````
3. Add upstream remote:
   ``````bash
   git remote add upstream https://github.com/flyaruu/python-super-heroes.git
   ``````

### Development Setup

``````bash
# Start all services
docker-compose up -d

# Verify everything works
curl http://localhost:8004/api/fights/execute_fight
``````

## Development Workflow

### 1. Create a Branch

``````bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
``````

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

### 2. Make Changes

Follow the project's code standards (see below) and make your changes.

### 3. Test Your Changes

``````bash
# Test manually
docker-compose restart service-name
curl http://localhost:PORT/api/endpoint

# Run load tests
docker-compose run k6 k6 run -e RAMPING_RATE=10 /k6/load.js
``````

### 4. Commit Changes

Use clear, descriptive commit messages following the Conventional Commits format:

``````bash
git add .
git commit -m "feat: add hero search by name endpoint"
``````

**Commit types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style (formatting, no logic change)
- `refactor:` Code refactoring
- `perf:` Performance improvement
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

**Examples:**
``````bash
git commit -m "feat: add pagination to heroes list endpoint"
git commit -m "fix: resolve database connection timeout issue"
git commit -m "docs: update API documentation for fights service"
git commit -m "refactor: extract database connection logic"
``````

### 5. Push and Create Pull Request

``````bash
# Push to your fork
git push origin feature/your-feature-name
``````

Then create a Pull Request on GitHub:
1. Go to your fork on GitHub
2. Click "Pull Request"
3. Select your branch
4. Fill in the PR template
5. Submit

## Code Standards

### Python Style Guide

We follow PEP 8 with these specifications:

**Formatting:**
- Line length: 100 characters maximum
- Indentation: 4 spaces (no tabs)
- Imports: Grouped and sorted (stdlib → third-party → local)
- String quotes: Double quotes preferred

**Example:**
``````python
import asyncio
import os
from typing import Dict, List

from starlette.applications import Starlette
from starlette.responses import JSONResponse

from local_module import helper


async def get_heroes() -> List[Dict[str, str]]:
    """Fetch all heroes from the database.
    
    Returns:
        List of hero dictionaries with id, name, and level.
    """
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM Hero")
        return [dict(row) for row in rows]
``````

### Linting

Before submitting, run linters:

``````bash
# Install linting tools
pip install black flake8 mypy isort

# Format code
black services/heroes/main.py

# Sort imports
isort services/heroes/main.py

# Check style
flake8 services/heroes/main.py

# Type check
mypy services/heroes/main.py
``````

**Configuration** (add to project root if needed):

``.flake8``
``````ini
[flake8]
max-line-length = 100
exclude = __pycache__,venv,.git
``````

``pyproject.toml``
``````toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100
``````

### Docstrings

Use Google-style docstrings:

``````python
async def calculate_fight_winner(hero: Dict, villain: Dict) -> str:
    """Determine the winner of a fight based on levels.
    
    Args:
        hero: Hero dictionary with 'name' and 'level' keys
        villain: Villain dictionary with 'name' and 'level' keys
    
    Returns:
        Name of the winner
    
    Raises:
        ValueError: If hero or villain missing required fields
    
    Example:
        >>> winner = await calculate_fight_winner(
        ...     {"name": "Spider-Man", "level": 93},
        ...     {"name": "Joker", "level": 150}
        ... )
        >>> print(winner)
        'Joker'
    """
    if hero["level"] > villain["level"]:
        return hero["name"]
    return villain["name"]
``````

### Type Hints

Add type hints for function parameters and return values:

``````python
from typing import Dict, List, Optional

async def get_hero_by_id(hero_id: int) -> Optional[Dict[str, str]]:
    """Get hero by ID."""
    ...

async def list_heroes(limit: int = 100) -> List[Dict[str, str]]:
    """List heroes."""
    ...
``````

## Pull Request Guidelines

### PR Title

Use the same format as commit messages:

``````
feat: add hero search endpoint
fix: resolve database timeout in villains service
docs: update architecture documentation
``````

### PR Description

Include:

``````markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- Change 1
- Change 2

## Testing
How to test these changes

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
``````

### Review Process

1. **Automated checks** run on your PR (if CI/CD configured)
2. **Code review** by maintainer(s)
3. **Address feedback** with new commits
4. **Approval** and merge by maintainer

## Types of Contributions

### Bug Fixes

1. Create an issue describing the bug (if not already exists)
2. Reference the issue in your PR: "Fixes #123"
3. Include reproduction steps in PR description
4. Add tests to prevent regression

### New Features

1. Discuss feature in an issue first
2. Ensure feature aligns with project goals
3. Keep PRs focused (one feature per PR)
4. Update documentation
5. Add tests for new functionality

### Documentation

1. Check for spelling and grammar
2. Test code examples
3. Ensure markdown formatting is correct
4. Update table of contents if needed

### Performance Improvements

1. Include benchmark results in PR
2. Run K6 tests before and after changes
3. Document performance gains
4. Ensure no regressions in functionality

## Testing

### Manual Testing

``````bash
# Test your changes
docker-compose up -d
curl http://localhost:PORT/api/your-endpoint

# Check logs
docker-compose logs -f service-name
``````

### Load Testing

``````bash
# Run baseline test
docker-compose run k6 k6 run -e RAMPING_RATE=10 /k6/load.js

# Ensure tests pass
``````

### Unit Tests

Add tests for new functionality:

``````python
# services/heroes/test_main.py
import pytest
from starlette.testclient import TestClient
from main import app

def test_get_hero_by_name():
    client = TestClient(app)
    response = client.get("/api/heroes/search/spider")
    assert response.status_code == 200
    assert "Spider-Man" in response.json()["name"]
``````

## Documentation

### When to Update Documentation

Update documentation when:
- Adding new endpoints
- Changing existing behavior
- Adding configuration options
- Modifying architecture
- Adding dependencies

### Documentation Files

- **README.md**: Overview and quick start
- **docs/API.md**: API reference
- **docs/ARCHITECTURE.md**: System design
- **docs/DEVELOPMENT.md**: Development setup
- **docs/TESTING.md**: Testing guide
- **CONTRIBUTING.md**: This file

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

### Communication

- Use GitHub issues for bugs and feature requests
- Use pull requests for code discussions
- Be clear and concise
- Provide context and examples

### Response Times

- Bug fixes: Reviewed within 3 days
- Features: Reviewed within 7 days
- Documentation: Reviewed within 3 days

## Questions?

If you have questions:
1. Check existing documentation
2. Search closed issues
3. Create a new issue with the "question" label
4. Contact maintainers

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Python Super Heroes! 🦸‍♂️🦹‍♀️
