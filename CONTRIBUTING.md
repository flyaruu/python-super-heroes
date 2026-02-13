# Contributing to Python Super Heroes

Thank you for your interest in contributing to Python Super Heroes! This document provides guidelines and standards for contributing to the project.

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone, regardless of background or identity.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or insulting comments
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates.

**When filing a bug report, include**:

- **Clear title**: Brief description of the issue
- **Steps to reproduce**: Detailed steps to recreate the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Docker version, Python version
- **Logs**: Relevant error messages or stack traces
- **Screenshots**: If applicable

**Example bug report**:

``````markdown
**Title**: Fights service returns 502 when heroes service is slow

**Steps to Reproduce**:
1. Start all services with `docker-compose up`
2. Add 2-second delay to heroes service
3. Call `GET /api/fights/execute_fight`

**Expected**: Should return fight result after delay
**Actual**: Returns 502 Bad Gateway immediately

**Environment**:
- OS: Ubuntu 22.04
- Docker: 24.0.5
- Python: 3.13

**Logs**:
```
fights-1 | ERROR - Error connecting to external service: timeout
```
``````

### Suggesting Enhancements

We welcome enhancement suggestions! Please provide:

- **Use case**: Why is this enhancement needed?
- **Proposed solution**: How should it work?
- **Alternatives**: Other approaches considered
- **Impact**: Who benefits from this change?

**Example enhancement**:

``````markdown
**Title**: Add caching layer for random hero/villain queries

**Use Case**: 
Under load, database queries for random heroes/villains become a bottleneck.

**Proposed Solution**:
Add Redis cache with 60-second TTL for random selections.

**Benefits**:
- Reduced database load
- Improved p95 latency
- Better scalability

**Trade-offs**:
- Added complexity
- Slightly stale data
- Redis dependency
``````

### Pull Requests

#### Before Submitting

1. ✅ Search existing PRs to avoid duplicates
2. ✅ Create an issue first for significant changes
3. ✅ Fork the repository
4. ✅ Create a feature branch
5. ✅ Make your changes following coding standards
6. ✅ Add tests for new functionality
7. ✅ Update documentation
8. ✅ Ensure all tests pass
9. ✅ Format code with Black

#### PR Guidelines

**Good PRs**:
- ✅ Single, focused change
- ✅ Clear, descriptive title
- ✅ Detailed description
- ✅ Tests included
- ✅ Documentation updated
- ✅ Small, reviewable size

**Avoid**:
- ❌ Multiple unrelated changes
- ❌ Massive PRs (>500 lines)
- ❌ Breaking changes without discussion
- ❌ Missing tests
- ❌ Outdated documentation

#### PR Template

``````markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
How was this tested?

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing performed
- [ ] Load tests pass (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review performed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added for new functionality
- [ ] All tests pass locally

## Related Issues
Fixes #(issue number)

## Screenshots (if applicable)
``````

#### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

**Format**: `<type>(<scope>): <description>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples**:
``````
feat(heroes): add search by power endpoint
fix(fights): handle service timeout gracefully
docs(api): add examples for all endpoints
refactor(database): extract connection pool logic
test(villains): add integration tests
chore(deps): update FastAPI to 0.110.0
perf(fights): cache random fighter selections
``````

### Development Workflow

1. **Fork and Clone**:
   ``````bash
   git clone https://github.com/YOUR_USERNAME/python-super-heroes.git
   cd python-super-heroes
   ``````

2. **Create Branch**:
   ``````bash
   git checkout -b feature/your-feature-name
   ``````

3. **Make Changes**:
   - Follow [Development Guide](docs/development.md)
   - Follow coding standards
   - Add tests

4. **Test Locally**:
   ``````bash
   # Format code
   black services/
   
   # Run tests
   pytest
   
   # Test with Docker
   docker-compose up -d
   curl http://localhost:8001/api/heroes
   ``````

5. **Commit**:
   ``````bash
   git add .
   git commit -m "feat(heroes): add search functionality"
   ``````

6. **Push**:
   ``````bash
   git push origin feature/your-feature-name
   ``````

7. **Create PR** on GitHub

### Code Review Process

1. **Automated Checks**: CI runs tests, linting, formatting checks
2. **Maintainer Review**: Project maintainer reviews code
3. **Feedback**: Address review comments
4. **Approval**: Once approved, PR will be merged
5. **Cleanup**: Delete your branch after merge

**Expected Timeline**:
- Initial review: 2-3 business days
- Feedback cycles: 1-2 days per cycle
- Merge: After approval

## Coding Standards

### Python

- **Style**: PEP 8
- **Line Length**: 120 characters
- **Formatter**: Black
- **Type Hints**: Required for all functions
- **Docstrings**: Google style for all public functions

### Documentation

- **Format**: Markdown
- **Style**: Developer-friendly, concise
- **Structure**: Progressive disclosure (overview → details)
- **Examples**: Include code examples for all features

### Testing

- **Coverage**: Aim for >80% code coverage
- **Test Types**: Unit, integration, load tests
- **Naming**: `test_<function>_<scenario>`
- **Assertions**: Use descriptive assertion messages

### Git

- **Commits**: Atomic, focused commits
- **Messages**: Conventional Commits format
- **Branches**: Feature branches from main
- **History**: Keep clean history (squash if needed)

## Project Structure

``````
python-super-heroes/
├── services/          # Each service is independent
│   ├── fights/       # Fight orchestration
│   ├── heroes/       # Heroes CRUD
│   ├── villains/     # Villains CRUD
│   └── locations/    # Locations CRUD
├── database/         # DB initialization scripts
├── k6/              # Load tests
├── docs/            # Documentation
└── compose.yml      # Docker orchestration
``````

## Communication

### Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Pull Requests**: Code contributions, reviews

### Response Times

- **Issues**: 2-3 business days for initial response
- **PRs**: 2-3 business days for initial review
- **Questions**: 1-2 business days

### Asking for Help

**Good Questions**:
- ✅ Include context and what you've tried
- ✅ Show relevant code or error messages
- ✅ Specify environment details
- ✅ Be specific about expected vs actual behavior

**Example**:
``````markdown
**Question**: How do I add a new field to the Hero schema?

**Context**: I want to add a `team` field to track which team each hero belongs to.

**What I've tried**:
1. Added field to PostgreSQL schema
2. Updated the data model

**Issue**: The API doesn't return the new field

**Environment**:
- Running locally with Docker Compose
- Modified `database/heroes-db/init/heroes.sql`
``````

## Recognition

Contributors are recognized in:

- **README.md**: Contributors section (coming soon)
- **Release Notes**: Credited in changelog
- **GitHub**: Contributor statistics

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (to be specified).

## Additional Resources

- [Development Guide](docs/development.md)
- [API Reference](docs/api-reference.md)
- [Architecture Guide](docs/architecture.md)
- [Load Testing Guide](docs/load-testing.md)

## Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search GitHub Issues/Discussions
3. Create a new Discussion
4. Contact maintainers

Thank you for contributing to Python Super Heroes! 🦸‍♂️🦹‍♀️
