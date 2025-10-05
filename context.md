# 🚀 DB-Forge MK1 - LLM Context Guide

## Project Overview
**DB-Forge MK1** is a modern, containerized Database-as-a-Service (DBaaS) platform with a full-stack web interface. It provides on-demand SQLite database instances through a REST API with a professional React/Next.js admin dashboard.

## 🏗️ Architecture

### **Core Stack**
- **Backend**: FastAPI (Python) - REST API service
- **Frontend**: Next.js 15 (React 19) - Admin dashboard
- **Database Workers**: SQLite containers (Alpine Linux)
- **Proxy**: Traefik - HTTP routing and load balancing
- **Container Platform**: Docker Compose

### **Service Architecture**
```
┌─────────────────────────────────────────────────────────┐
│                    Traefik Proxy                        │
│              (http://db.localhost:8081)                 │
└─────────────────┬───────────────┬───────────────────────┘
                  │               │
        ┌─────────▼─────────┐   ┌─▼─────────────┐
        │   DB Gateway      │◄──┤   Frontend    │
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

## 📁 Directory Structure

```
DB-Forge-MK1/
├── services/                    # Core application services
│   ├── db-gateway/             # Backend API service
│   │   ├── app/
│   │   │   ├── auth/           # Authentication system
│   │   │   ├── routes/         # API endpoints
│   │   │   ├── services/       # Business logic
│   │   │   ├── models/         # Data models
│   │   │   └── main.py         # FastAPI entry point
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── frontend/               # Next.js web interface
│       ├── src/
│       │   ├── app/            # Next.js 15 App Router pages
│       │   │   ├── databases/  # Database management page
│       │   │   ├── connections/# Connection monitoring
│       │   │   ├── users/      # User management
│       │   │   ├── security/   # Security dashboard
│       │   │   ├── logs/       # System logs
│       │   │   └── settings/   # Configuration
│       │   ├── components/     # React components
│       │   │   ├── dashboard/  # Dashboard shell & navigation
│       │   │   ├── ui/         # shadcn/ui components
│       │   │   └── [pages]/    # Page-specific components
│       │   └── lib/            # Utilities and API client
│       ├── Dockerfile
│       └── package.json
├── infra/                      # Infrastructure configuration
│   ├── docker-compose.yml     # Production compose file
│   ├── docker-compose.dev.yml # Development overrides
│   ├── .env                   # Environment variables
│   ├── traefik/               # Reverse proxy config
│   └── db-worker-base/        # Database worker image
├── scripts/                   # Automation scripts
├── docs/                      # Documentation
├── Makefile                   # Development commands
└── context.md                 # This file
```

## 🔧 Development Setup

### **Prerequisites**
- Docker & Docker Compose
- Make (for commands)
- Git

### **Quick Start Commands**
```bash
# Start the entire stack
make up

# Stop services
make down

# Rebuild and restart
make restart

# View logs
make logs

# Build frontend only
make frontend-build

# Access shells
make shell-frontend    # Frontend container shell
make shell-gateway     # Backend container shell
```

### **Environment Configuration**
- Main config: `infra/.env`
- Frontend env: `services/frontend/.env.local`
- Development API key: `development-api-key-12345`

## 🌐 Access Points

### **Web Interfaces**
- **Frontend Dashboard**: http://frontend.db.localhost:8081
- **API Documentation**: http://db.localhost:8081/docs  
- **Traefik Dashboard**: http://localhost:8080/dashboard/

### **API Authentication**
- **Header**: `X-API-Key: development-api-key-12345`
- **Base URL**: http://db.localhost:8081 (through Traefik)
- **Direct Backend**: http://localhost:8000 (development only)

## 📚 API Endpoints

### **Database Management**
- `GET /admin/databases` - List all database instances
- `POST /admin/databases/spawn/{db_name}` - Create database
- `POST /admin/databases/prune/{db_name}` - Delete database
- `GET /admin/gateway/stats` - System statistics

### **Data Operations**
- `POST /api/db/{db_name}/query` - Execute SQL queries
- `POST /api/db/{db_name}/tables` - Create tables
- `POST /api/db/{db_name}/tables/{table}/rows` - Insert data

## 🎨 Frontend Stack

### **Technology**
- **Framework**: Next.js 15 with App Router
- **UI Library**: shadcn/ui + Radix UI primitives
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Forms**: React Hook Form + Zod validation
- **HTTP Client**: Native fetch with custom API wrapper

### **Page Structure**
1. **Overview** (`/`) - Dashboard with system stats
2. **Databases** (`/databases`) - Database management interface
3. **Connections** (`/connections`) - Connection monitoring
4. **Users** (`/users`) - User management (planned)
5. **Security** (`/security`) - Security monitoring
6. **Logs** (`/logs`) - System logs viewer
7. **Settings** (`/settings`) - Configuration panel

### **Key Components**
- `DashboardShell` - Main layout with navigation
- `DatabasesView` - Database management with SQL console
- `DatabaseOverview` - Real-time dashboard stats
- API Client (`src/lib/api.ts`) - Centralized API communication

## 🔐 Authentication System

### **Current Implementation**
- **Method**: Fixed API key for development
- **Key**: `development-api-key-12345`
- **Storage**: Environment variables
- **Headers**: `X-API-Key` header required for all API calls

### **Planned Features**
- JWT token authentication
- Role-based access control (Admin, User, Viewer)
- Multi-factor authentication
- Session management

## 🐳 Container Architecture

### **Services**
1. **traefik-db-forge** - HTTP router and load balancer
2. **db-gateway** - FastAPI backend service  
3. **db-forge-frontend** - Next.js web interface
4. **Dynamic DB Workers** - On-demand SQLite containers

### **Networking**
- **Network**: `db-forge-net` (bridge)
- **External Ports**: 8080-8081 (Traefik), 3000 (Frontend dev)
- **Internal Communication**: Service discovery via Docker DNS

### **Data Persistence**
- Database files: Container volumes (ephemeral)
- Configuration: `infra/.env` and secrets/
- Logs: Container stdout/stderr

## 🛠️ Development Workflow

### **Making Changes**

#### **Backend Changes** (`services/db-gateway/`)
```bash
# Edit Python files
# Rebuild and restart
make restart

# Or rebuild just backend
docker-compose -f infra/docker-compose.yml build db-gateway
docker-compose -f infra/docker-compose.yml up -d db-gateway
```

#### **Frontend Changes** (`services/frontend/`)
```bash
# Edit React/Next.js files
# Rebuild frontend
make frontend-build

# Or for development with hot reload
cd services/frontend && npm run dev
```

#### **Infrastructure Changes** (`infra/`)
```bash
# Edit docker-compose.yml, Traefik config, etc.
make rebuild  # Full rebuild
make up       # Start services
```

### **Testing Approach**
```bash
# Test API directly
curl -H "X-API-Key: development-api-key-12345" \
     -H "Host: db.localhost" \
     http://localhost:8081/admin/databases

# Test frontend integration
# Navigate to http://frontend.db.localhost:8081

# Test database operations
curl -X POST -H "X-API-Key: development-api-key-12345" \
     -H "Host: db.localhost" \
     http://localhost:8081/admin/databases/spawn/test-db
```

## 🚨 Common Issues & Solutions

### **"API Key Invalid" Errors**
- Check API key: `development-api-key-12345`
- Ensure `X-API-Key` header is set
- Verify backend is running: `docker logs db-gateway`

### **Frontend Can't Connect to Backend**
- Check Traefik routing: http://localhost:8080/dashboard/
- Verify environment: `services/frontend/.env.local`
- Check network connectivity between containers

### **Database Creation Fails**
- Check Docker socket access in containers
- Verify `db-worker-base` image exists: `docker images`
- Check container logs: `make logs`

### **Port Conflicts**
- Default ports: 8080-8081 (Traefik), 3000 (Frontend dev)
- Change ports in `infra/docker-compose.yml` if needed

## 📝 Code Patterns

### **API Client Usage** (Frontend)
```typescript
import { apiClient } from '@/lib/api'

// Get databases
const databases = await apiClient.getDatabases()

// Create database
await apiClient.createDatabase('my-db')

// Execute query
const result = await apiClient.executeQuery('my-db', 'SELECT * FROM users')
```

### **Adding New API Endpoints** (Backend)
```python
# In services/db-gateway/app/routes/
from fastapi import APIRouter, Depends
from app.auth.auth import verify_api_key_header

router = APIRouter(dependencies=[Depends(verify_api_key_header)])

@router.get("/my-endpoint")
async def my_endpoint():
    return {"message": "Hello World"}
```

### **Adding New Frontend Pages**
```typescript
// Create: services/frontend/src/app/my-page/page.tsx
import { DashboardShell } from "@/components/dashboard/dashboard-shell"

export default function MyPage() {
  return (
    <DashboardShell>
      <h1>My Page</h1>
    </DashboardShell>
  )
}

// Update navigation in: src/components/dashboard/dashboard-shell.tsx
```

## 🔄 Deployment Status

### **Current State**: Development Ready
- ✅ Complete frontend-backend integration
- ✅ All dashboard pages implemented
- ✅ Docker containerization working
- ✅ API authentication functional
- ✅ Real-time data updates

### **Production Considerations**
- [ ] Replace fixed API key with proper auth
- [ ] Add HTTPS/TLS termination
- [ ] Implement persistent database storage
- [ ] Add monitoring and alerting
- [ ] Set up backup strategies
- [ ] Add rate limiting and security headers

## 📊 Project Statistics

- **Backend**: ~2,000 lines Python (FastAPI)
- **Frontend**: ~15,000 lines TypeScript/React
- **Docker Images**: 4 services + dynamic workers
- **Pages**: 7 complete dashboard pages
- **Components**: 50+ UI components
- **API Endpoints**: 15+ REST endpoints

## 🎯 Working with This Codebase

### **As an LLM Assistant, I can help with:**

1. **Adding new features** to existing pages
2. **Creating new API endpoints** and integrating them
3. **Building new dashboard pages** following existing patterns
4. **Debugging issues** with Docker, API, or frontend
5. **Refactoring components** for better reusability
6. **Adding new database types** beyond SQLite
7. **Implementing authentication** improvements
8. **Performance optimizations** and code improvements

### **Key Files to Understand:**
- `services/db-gateway/app/main.py` - Backend entry point
- `services/frontend/src/lib/api.ts` - API client
- `services/frontend/src/components/dashboard/dashboard-shell.tsx` - Navigation
- `infra/docker-compose.yml` - Service orchestration
- `Makefile` - Development commands

### **Development Philosophy:**
- **Container-first**: Everything runs in Docker
- **API-driven**: Frontend consumes REST APIs
- **Component-based**: Reusable UI components
- **Type-safe**: TypeScript throughout frontend
- **Production-ready**: Professional coding standards

---

**This context should give you everything needed to immediately start working productively with the DB-Forge codebase!** 🚀