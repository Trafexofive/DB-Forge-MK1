# 🗡️ DB-Forge MK1 - Database Management Platform

**Forged by Gemini for Absolute Data Sovereignty**

DB-Forge MK1 is a modern, containerized Database-as-a-Service (DBaaS) platform that provides complete control over isolated database instances. Built with a focus on developer experience, it offers both powerful APIs and an intuitive web interface for managing your database infrastructure.

## 🌟 Project Vision

Empower developers and automated systems with a self-hosted, highly flexible, and transparent data persistence layer. Reduce the friction of managing multiple database environments while maintaining absolute data sovereignty and control.

## ✨ Key Features

### 🚀 **Core Platform**
- **Dynamic Database Provisioning**: Spin up or tear down isolated database environments with simple API calls
- **Absolute Data Sovereignty**: Your data stays on your filesystem with full ownership and persistence
- **RESTful API**: Comprehensive HTTP API for all database operations and management
- **Isolated Instances**: Every database runs in its own dedicated Docker container for security and separation

### 🎨 **Modern Web Interface**
- **Next.js Admin Dashboard**: Professional, responsive web UI built with modern React
- **Real-time Monitoring**: Live database status, connections, and health metrics  
- **Mobile-First Design**: Clean, accessible interface that works on all devices
- **shadcn/ui Components**: Beautiful, accessible UI components with Radix primitives

### 🔧 **Developer Experience**
- **Comprehensive Makefile**: 25+ commands for development, testing, and deployment
- **Multiple Client Libraries**: Python, C++, and TUI clients with full API coverage
- **Docker-First**: Fully containerized with optimized builds and easy deployment
- **Type-Safe APIs**: Full TypeScript support with comprehensive error handling

### 📊 **Enterprise Ready**
- **Traefik Integration**: Intelligent reverse proxy with automatic service discovery
- **Health Monitoring**: Built-in health checks and status reporting
- **Production Builds**: Optimized Docker images with standalone outputs
- **Extensible Architecture**: Plugin-ready design for multiple database backends

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Traefik Proxy                        │
│              (http://db.localhost:8081)                 │
└─────────────────┬───────────────┬───────────────────────┘
                  │               │
        ┌─────────▼─────────┐   ┌─▼─────────────┐
        │   DB Gateway      │   │   Frontend    │
        │   (FastAPI)       │   │   (Next.js)   │
        │   Port: 8000      │   │   Port: 3000  │
        └─────────┬─────────┘   └───────────────┘
                  │
        ┌─────────▼─────────┐
        │  Database Workers │
        │   (SQLite/etc)    │
        │  Isolated Containers │
        └───────────────────┘
```

### Core Components

1. **DB Gateway**: FastAPI service managing database lifecycles and operations
2. **Frontend**: Next.js admin interface for monitoring and management  
3. **Database Workers**: Isolated containers running individual database instances
4. **Traefik Proxy**: Intelligent routing and load balancing
5. **Client Libraries**: Multi-language SDKs for programmatic access

## 🚀 Quick Start

### Prerequisites

- **Docker** & **Docker Compose**
- **Node.js 20+** (for frontend development)
- **Make** (for automation)

### 1. Clone & Setup

```bash
git clone <repository-url>
cd DB-Forge-MK1

# Copy and customize environment
cp infra/.env.example infra/.env
```

### 2. Start the Platform

```bash
# Build and start all services
make up

# Or start in development mode with live reload
make dev
```

### 3. Access the Platform

- **Admin Dashboard**: http://frontend.db.localhost:8081
- **API Documentation**: http://db.localhost:8081/docs  
- **Traefik Dashboard**: http://localhost:8080/dashboard/

## 📚 Development

### Frontend Development

```bash
# Install dependencies
make frontend-install

# Start development server (hot reload)
make frontend-dev

# Build for production
make frontend-build

# Lint code
make frontend-lint
```

### API Development

```bash
# View API logs
make logs

# Access gateway shell
make ssh

# Run tests
make test

# Check service status
make status
```

### Complete Command Reference

```bash
# Core Stack Management
make up          # Build and start all services
make down        # Stop and remove containers  
make restart     # Restart all services
make re          # Clean rebuild from scratch

# Development
make dev         # Development mode with live reload
make build       # Build all service images
make rebuild     # Force rebuild (no cache)

# Frontend
make frontend-dev      # Next.js dev server
make frontend-build    # Production build
make frontend-install  # Install dependencies
make frontend-lint     # Lint code
make frontend-clean    # Clean build artifacts

# Diagnostics
make status      # Service status
make logs        # Gateway logs
make logs-all    # All service logs
make health      # Health checks
make ssh         # Gateway shell

# Testing & Cleanup
make test        # Run test suite
make clean       # Remove containers/data ⚠️
make fclean      # Deep clean with volumes ⚠️
make prune       # Clean unused Docker resources
```

## 🧪 Client Libraries

### 🐍 Python Client
```python
from dbforge_client import DBForgeClient

client = DBForgeClient("http://db.localhost:8081")
await client.spawn_database("my-app")
result = await client.execute_query("my-app", "SELECT * FROM users")
```

### 🔧 C++ Client  
```cpp
#include <dbforge/dbforge.hpp>

dbforge::Client client("http://db.localhost:8081");
client.spawn_database("my-app");
auto result = client.execute_query("my-app", "SELECT * FROM users");
```

### 🖥️ TUI Client (Interactive Terminal)
```bash
cd clients/tui && make run
# Features: Real-time dashboard, SQL editor, table browser
```

**Features:**
- 🔒 Exception-safe error handling
- ⚡ Async/await support (Python)
- 🧵 Thread-safe operations (C++)
- 📱 Interactive TUI with vim bindings
- 📖 Comprehensive documentation

## 🧪 Testing

```bash
# Run comprehensive test suite
make test

# Test specific components
cd testing && python -m pytest tests/
```

The test suite covers:
- API endpoint validation
- Database lifecycle management
- Error handling scenarios
- Client library functionality
- Integration testing

## 📖 Documentation

### Core Documentation
- [API Specification](docs/API.md) - Complete REST API reference
- [Architecture Deep Dive](docs/ARCHITECTURE.md) - System design and components
- [Contributing Guidelines](docs/CONTRIBUTING.md) - How to contribute
- [Project Roadmap](TODO.md) - Future features and improvements

### Component Documentation
- [Frontend README](services/frontend/README.md) - Next.js admin interface
- [Client Libraries](clients/README.md) - Multi-language SDK documentation
- [Testing Guide](testing/README.md) - Test suite and validation

## 🔄 Roadmap & Future Features

### ✅ Current (MK1)
- SQLite backend with container isolation
- RESTful API with FastAPI
- Next.js admin dashboard
- Python/C++/TUI clients
- Docker containerization
- Traefik reverse proxy

### 🚧 Phase II (MK2) - Enhanced Experience  
- Multi-backend support (PostgreSQL, MySQL, Redis)
- Authentication & authorization
- Advanced monitoring & metrics
- Backup & restore functionality
- WebSocket real-time updates

### 🌟 Phase III (MK3) - AI Integration
- Agent SDKs for AI systems
- Semantic query layer (natural language → SQL)
- Autonomous database management
- Knowledge graph integration
- Advanced analytics dashboard

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/CONTRIBUTING.md) for:

- Development setup and workflow
- Code style and conventions  
- Testing requirements
- Documentation standards
- Pull request process

## 📄 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

## 🔗 Links & Resources

- **Live Demo**: (Coming Soon)
- **Documentation**: Full docs in `/docs` directory
- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for community support

---

**Built with ❤️ by the DB-Forge Team**  
*Empowering developers with sovereign data infrastructure*