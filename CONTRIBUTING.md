# Contributing to Python Super Heroes

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/python-super-heroes.git
   cd python-super-heroes
   ```
3. **Set up development environment**:
   ```bash
   docker-compose up -d
   ```
4. **Create a branch**:
   ```bash
   git checkout -b feature/my-contribution
   ```

## Types of Contributions

### Bug Reports

Report bugs by creating a GitHub issue:

- **Title**: Clear, descriptive summary
- **Description**: Steps to reproduce, expected vs actual behavior
- **Environment**: OS, Docker version, Python version
- **Logs**: Relevant error messages or stack traces

### Feature Requests

Suggest features via GitHub issues:

- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Other approaches considered

### Code Contributions

#### Areas for Contribution

- **New Features**: Additional endpoints, services, or functionality
- **Performance**: Optimization and efficiency improvements
- **Testing**: Unit tests, integration tests, load tests
- **Documentation**: Improvements, corrections, translations
- **Bug Fixes**: Addressing reported issues

## Development Process

### 1. Set Up Development Environment

See [Development Guide](docs/DEVELOPMENT.md) for detailed setup instructions.

### 2. Make Your Changes

- **Keep changes focused**: One feature or fix per pull request
- **Follow code style**: Use Black, Flake8, isort
- **Add tests**: Cover new functionality
- **Update documentation**: Keep docs in sync with code

### 3. Test Your Changes

```bash
# Start services
docker-compose up -d

# Test manually
curl http://localhost:8001/api/heroes
curl http://localhost:8004/api/fights/execute_fight

# Run load tests
docker-compose exec k6 k6 run /k6/randomFight.js

# Check logs for errors
docker-compose logs -f
```

### 4. Commit Your Changes

Follow commit message conventions:

```bash
# Format: <type>(<scope>): <subject>

# Examples:
git commit -m "feat(heroes): add endpoint to filter by power level"
git commit -m "fix(fights): correct winner determination logic"
git commit -m "docs(api): update endpoint descriptions"
git commit -m "perf(locations): optimize database queries"
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/my-contribution
```

Create pull request on GitHub with:

- **Clear title**: Summarize the change
- **Description**: What changed and why
- **Testing**: How you tested the changes
- **Related issues**: Link to related issues

## Code Style Guidelines

### Python

- **PEP 8**: Follow Python style guide
- **Black**: Use for code formatting (line length 100)
- **Type hints**: Add to function signatures
- **Async/await**: Use for I/O operations
- **Docstrings**: Document public functions

Example:

```python
from typing import List, Optional

async def get_heroes_by_level(min_level: int) -> List[dict]:
    """
    Fetch heroes with level greater than or equal to min_level.
    
    Args:
        min_level: Minimum level threshold
        
    Returns:
        List of hero dictionaries
    """
    query = "SELECT * FROM hero WHERE level >= $1"
    async with app.state.pool.acquire() as conn:
        rows = await conn.fetch(query, min_level)
        return [dict(row) for row in rows]
```

### Documentation

- **Markdown**: Use standard Markdown syntax
- **Clear headings**: Use hierarchical structure
- **Code blocks**: Specify language for syntax highlighting
- **Examples**: Include practical examples
- **Links**: Use relative links for internal docs

## Testing Guidelines

### Manual Testing

Test all affected endpoints:

```bash
# Test the specific service
curl -X GET http://localhost:8001/api/heroes
curl -X GET http://localhost:8001/api/heroes/1
curl -X GET http://localhost:8001/api/heroes/random_hero
```

### Load Testing

Verify performance isn't degraded:

```bash
docker-compose exec k6 k6 run /k6/randomFight.js
```

Check that:
- Response times remain acceptable
- Error rate is 0%
- No memory leaks or resource issues

### Unit Tests (Future)

When adding unit tests:

```python
# services/heroes/tests/test_heroes.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_get_heroes():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/heroes")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
```

## Pull Request Process

1. **Ensure CI passes**: All automated checks must pass
2. **Update documentation**: Keep docs synchronized
3. **Request review**: Tag maintainers if needed
4. **Address feedback**: Respond to review comments
5. **Squash commits** (if requested): Clean up commit history

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Changes are tested and working
- [ ] Documentation updated (if applicable)
- [ ] Commit messages follow convention
- [ ] No merge conflicts with main branch
- [ ] All services start successfully
- [ ] Load tests pass (if applicable)

## Documentation Contributions

Documentation improvements are always welcome!

### Documentation Structure

```
docs/
├── ARCHITECTURE.md    # System design and architecture
├── API.md            # Complete API reference
├── DEVELOPMENT.md    # Developer setup and workflow
├── LOAD_TESTING.md   # Performance testing guide
└── CONTRIBUTING.md   # This file
```

### Documentation Standards

- **Clarity**: Write for diverse skill levels
- **Completeness**: Include all necessary information
- **Accuracy**: Test all code examples
- **Consistency**: Follow existing style and format
- **Progressive disclosure**: High-level first, details later

### Example Documentation Contribution

```markdown
# New Feature: Hero Search

## Endpoint

GET /api/heroes/search?name={query}

## Parameters

- `name` (string): Search query for hero names

## Example

```bash
curl "http://localhost:8001/api/heroes/search?name=super"
```

## Response

Returns heroes matching the search query.
```

## Reporting Security Issues

**Do not** open public issues for security vulnerabilities.

Instead, email security concerns to: [maintainer email]

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Community

- **GitHub Discussions**: Ask questions, share ideas
- **GitHub Issues**: Report bugs, request features
- **Pull Requests**: Contribute code

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Recognition

Contributors are recognized in:
- GitHub contributor list
- Release notes (for significant contributions)
- Project documentation (for major features)

## Questions?

- Check [Development Guide](docs/DEVELOPMENT.md)
- Check [Architecture Documentation](docs/ARCHITECTURE.md)
- Open a GitHub Discussion
- Review existing issues and pull requests

## Getting Help

If you're stuck:

1. **Documentation**: Check docs/ directory
2. **Issues**: Search existing GitHub issues
3. **Discussions**: Start a conversation
4. **Code**: Review similar implementations in the codebase

## Review Process

Pull requests are reviewed for:

- **Functionality**: Does it work as intended?
- **Code quality**: Is it maintainable and readable?
- **Testing**: Is it adequately tested?
- **Documentation**: Are changes documented?
- **Performance**: Does it impact system performance?
- **Security**: Are there security concerns?

Reviews typically take 2-5 business days.

## Continuous Improvement

We continuously improve:

- **Architecture**: Better design patterns
- **Performance**: Faster response times
- **Developer experience**: Better tools and docs
- **Test coverage**: More comprehensive testing
- **Documentation**: Clearer, more complete docs

Your contributions help make this project better!

---

Thank you for contributing to Python Super Heroes! 🦸‍♂️🦹‍♀️
