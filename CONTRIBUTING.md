# Contributing to MarketingIQ Google Ads Platform

## Development Workflow

### 1. Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/your-org/marketingiq-google-ads.git
cd marketingiq-google-ads

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r api/requirements.txt
```

### 2. Branch Naming Convention

- `feature/` - New features (e.g., `feature/add-conversion-tracking`)
- `bugfix/` - Bug fixes (e.g., `bugfix/fix-keyword-metrics`)
- `hotfix/` - Urgent production fixes
- `refactor/` - Code refactoring
- `docs/` - Documentation updates

### 3. Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Example:
```
feat(api): add pagination to keywords endpoint

- Implemented limit/offset pagination
- Added has_more flag for UI
- Updated documentation

Closes #123
```

### 4. Testing

Before submitting PR:

```bash
# Run ETL pipeline tests
python -m pytest tests/

# Test API endpoints
cd api
python -m pytest tests/

# Check code formatting
black . --check
flake8 .
```

### 5. Pull Request Process

1. Update documentation for any API changes
2. Add tests for new features
3. Ensure all tests pass
4. Update README.md if needed
5. Request review from team leads

## Code Standards

### Python Style

- Follow PEP 8
- Use type hints where possible
- Document all functions with docstrings
- Keep functions under 50 lines
- Use meaningful variable names

### API Design

- RESTful conventions
- Consistent error responses
- Pagination for list endpoints
- Clear schema documentation
- Version API endpoints

### Database

- Maintain normalized structure
- Add indexes for queried fields
- Document schema changes
- Use migrations for updates

## Security Guidelines

1. **Never commit credentials**
   - Use `.env` files
   - Add to `.gitignore`

2. **Validate input data**
   - Sanitize SQL queries
   - Validate API parameters

3. **Rate limiting**
   - Implement for production
   - Document limits

## Documentation

- Update API docs for endpoint changes
- Keep README current
- Document breaking changes
- Add inline code comments for complex logic

## Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No credentials committed
- [ ] PR description clear
- [ ] Breaking changes documented

## Getting Help

- Create an issue for bugs
- Use discussions for questions
- Tag team leads for urgent items
- Check existing issues first

## Team Contacts

- **ETL Pipeline**: @data-team
- **API Development**: @api-team
- **Frontend**: @manya @mayeera
- **DevOps**: @infrastructure