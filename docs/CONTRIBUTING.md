# 🤝 DB-Forge MK1: Contributing Guidelines

Welcome to the DB-Forge MK1 project! We're excited to have you contribute to building the ultimate database management platform. This guide will help you get started with contributing code, documentation, and ideas.

## 🌟 Ways to Contribute

### 🐛 Bug Reports
- Report issues via [GitHub Issues](https://github.com/your-org/db-forge/issues)
- Include steps to reproduce, expected vs actual behavior
- Provide system information and log outputs when relevant

### 💡 Feature Requests  
- Propose new features through [GitHub Discussions](https://github.com/your-org/db-forge/discussions)
- Check the [Roadmap](../TODO.md) to see planned features
- Provide use cases and implementation ideas

### 📝 Documentation
- Improve API documentation, tutorials, and guides
- Fix typos, clarify instructions, add examples
- Translate documentation to other languages

### 🔧 Code Contributions
- Bug fixes and performance improvements
- New features from the roadmap
- Client library enhancements
- Test coverage improvements

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:
- **Docker** & **Docker Compose** (latest versions)
- **Node.js 20+** (for frontend development)
- **Python 3.11+** (for backend development)
- **Git** (for version control)
- **Make** (for automation commands)

### 1. Fork & Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/db-forge-mk1.git
cd db-forge-mk1

# Add upstream remote for staying up-to-date
git remote add upstream https://github.com/original-org/db-forge-mk1.git
```

### 2. Development Setup

```bash
# Copy environment configuration
cp infra/.env.example infra/.env

# Build and start development environment
make dev

# Install frontend dependencies (if working on UI)
make frontend-install

# Verify everything works
make test
```

### 3. Development Workflow

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes...

# Test your changes
make test
make frontend-lint  # If working on frontend

# Commit with clear messages
git add .
git commit -m "feat: add database backup functionality"

# Push to your fork
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
```

## 📋 Development Guidelines

### 🏗️ Project Structure

```
DB-Forge-MK1/
├── services/
│   ├── db-gateway/          # FastAPI backend service
│   │   ├── app/            # Application code
│   │   ├── tests/          # Backend tests
│   │   └── Dockerfile      # Container definition
│   └── frontend/           # Next.js admin interface  
│       ├── src/            # Source code
│       ├── tests/          # Frontend tests
│       └── Dockerfile      # Container definition
├── infra/                  # Infrastructure & deployment
│   ├── docker-compose.yml  # Service orchestration
│   ├── traefik/           # Reverse proxy config
│   └── db-worker-base/    # Database worker image
├── clients/               # Client libraries
│   ├── python/           # Python SDK
│   ├── cpp/              # C++ SDK
│   └── tui/              # Terminal UI client
├── docs/                 # Documentation
├── testing/              # Integration tests
└── Makefile             # Development automation
```

### 🐍 Backend Development (FastAPI)

#### Code Style
- Follow **PEP 8** style guidelines
- Use **type hints** for all function parameters and returns
- Write **docstrings** for all public functions and classes
- Maximum line length: **88 characters** (Black formatter)

#### Example Code Style:
```python
from typing import List, Optional
from pydantic import BaseModel

class DatabaseInfo(BaseModel):
    """Model representing database instance information."""
    name: str
    status: str
    created_at: datetime
    size_bytes: int

async def get_database_info(
    db_name: str, 
    include_stats: bool = False
) -> Optional[DatabaseInfo]:
    """
    Retrieve information about a database instance.
    
    Args:
        db_name: Name of the database to query
        include_stats: Whether to include detailed statistics
        
    Returns:
        DatabaseInfo object if found, None otherwise
        
    Raises:
        DatabaseNotFound: If the database doesn't exist
    """
    # Implementation here...
    pass
```

#### Testing Requirements
```python
# Use pytest for testing
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_database():
    """Test database creation endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/admin/databases/spawn/test-db")
        assert response.status_code == 201
        assert response.json()["database"]["name"] == "test-db"
```

### ⚛️ Frontend Development (Next.js)

#### Code Style
- Use **TypeScript** for all new code
- Follow **React** best practices and hooks patterns
- Use **Tailwind CSS** for styling (no custom CSS unless necessary)
- Prefer **shadcn/ui** components over custom implementations

#### Component Structure:
```typescript
"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface DatabaseListProps {
  onDatabaseSelect?: (dbName: string) => void
}

export function DatabaseList({ onDatabaseSelect }: DatabaseListProps) {
  const [databases, setDatabases] = useState<Database[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Load databases...
  }, [])

  if (isLoading) {
    return <div>Loading databases...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Database Instances</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Component content */}
      </CardContent>
    </Card>
  )
}
```

#### API Integration:
```typescript
// Use the centralized API client
import { apiClient } from '@/lib/api'

export async function useDatabases() {
  const [databases, setDatabases] = useState<Database[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDatabases = async () => {
      try {
        const result = await apiClient.getDatabases()
        setDatabases(result)
      } catch (err) {
        setError(err.message)
      }
    }
    fetchDatabases()
  }, [])

  return { databases, error }
}
```

### 🧪 Testing Standards

#### Test Coverage Requirements
- **Backend**: Minimum 90% test coverage
- **Frontend**: Minimum 80% test coverage for utility functions
- **Integration**: All API endpoints must have integration tests

#### Test Organization:
```bash
# Backend tests
services/db-gateway/tests/
├── unit/                    # Unit tests for individual functions
├── integration/            # API endpoint tests
└── conftest.py            # Pytest configuration

# Frontend tests  
services/frontend/tests/
├── components/            # Component unit tests
├── utils/                 # Utility function tests
└── integration/          # E2E tests
```

#### Running Tests:
```bash
# Run all tests
make test

# Run specific test suites
cd services/db-gateway && python -m pytest tests/unit/
cd services/frontend && npm run test

# Run with coverage
cd services/db-gateway && python -m pytest --cov=app tests/
cd services/frontend && npm run test:coverage
```

## 🔄 Pull Request Process

### 1. Before Submitting

- [ ] **Tests pass**: All existing and new tests pass
- [ ] **Code quality**: Linting passes without warnings
- [ ] **Documentation**: Update relevant documentation
- [ ] **Breaking changes**: Note any breaking changes in description
- [ ] **Commit messages**: Follow conventional commit format

### 2. Commit Message Format

We use [Conventional Commits](https://conventionalcommits.org/) for clear history:

```
type(scope): brief description

More detailed explanation if needed.

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix  
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(api): add database backup endpoint
fix(frontend): resolve table pagination issue  
docs(readme): update installation instructions
test(api): add integration tests for query endpoint
```

### 3. Pull Request Template

When creating a PR, include:

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated  
- [ ] Manual testing completed

## Screenshots (if applicable)
Include screenshots for UI changes.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for hard-to-understand areas
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### 4. Review Process

1. **Automated Checks**: CI pipeline runs tests and linting
2. **Code Review**: At least one maintainer reviews the code
3. **Testing**: Reviewer tests the changes locally if needed
4. **Approval**: Once approved, maintainers will merge

## 🏗️ Architecture Decisions

### When Adding New Features

1. **Check the Roadmap**: Ensure feature aligns with project direction
2. **Design Discussion**: For major features, create a GitHub Discussion
3. **API Design**: Follow existing API patterns and conventions
4. **Database Changes**: Consider backward compatibility
5. **Security**: Ensure new features don't introduce vulnerabilities

### Code Organization Principles

- **Separation of Concerns**: Keep business logic separate from API routes
- **Dependency Injection**: Use dependency injection for testability
- **Error Handling**: Consistent error handling across all components
- **Configuration**: Use environment variables for all configuration
- **Logging**: Add appropriate logging for debugging and monitoring

## 🛠️ Development Tools

### Recommended IDE Setup

#### Visual Studio Code Extensions:
- **Python**: Python extension pack
- **TypeScript**: Official TypeScript extension
- **Tailwind CSS**: IntelliSense for Tailwind
- **Docker**: Docker extension
- **Prettier**: Code formatting
- **ESLint**: JavaScript linting

#### Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "./services/db-gateway/.venv/bin/python",
  "typescript.preferences.includePackageJsonAutoImports": "auto",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

### Debugging

#### Backend Debugging:
```bash
# Run with debugger
cd services/db-gateway
python -m debugpy --listen 5678 --wait-for-client -m uvicorn app.main:app --reload
```

#### Frontend Debugging:
```bash
# Run with Next.js debugging
cd services/frontend  
NODE_OPTIONS='--inspect' npm run dev
```

## 📚 Resources

### Learning Resources
- **FastAPI**: [Official Documentation](https://fastapi.tiangolo.com/)
- **Next.js**: [Official Documentation](https://nextjs.org/docs)
- **shadcn/ui**: [Component Library](https://ui.shadcn.com/)
- **Docker**: [Best Practices](https://docs.docker.com/develop/best-practices/)

### Project Resources
- **API Documentation**: http://db.localhost:8081/docs
- **Architecture Guide**: [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **Roadmap**: [TODO.md](../TODO.md)
- **Issue Tracker**: [GitHub Issues](https://github.com/your-org/db-forge/issues)

## 🏆 Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub** contributor graphs and statistics
- **Project documentation** acknowledgments

## 🆘 Getting Help

- **GitHub Discussions**: For general questions and ideas
- **GitHub Issues**: For specific bugs and feature requests  
- **Discord Community**: (Coming soon) Real-time chat support
- **Email**: maintainers@db-forge.dev (for sensitive issues)

## 📄 License

By contributing to DB-Forge MK1, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to DB-Forge MK1!** 🚀

*Together, we're building the future of database management.*
*   Any relevant error messages or logs.

## Feature Requests

We're always open to new ideas! If you have a feature request, please open an issue on GitHub to discuss it.

Thank you for contributing to Praetorian DB-Forge!
