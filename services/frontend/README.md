# DB-Forge Frontend

A modern, clean admin web UI for the DB-Forge database management platform. Built with Next.js, TypeScript, Tailwind CSS, shadcn/ui, and Lucide icons.

## Features

- ✨ **Modern Tech Stack**: Next.js 15, TypeScript, Tailwind CSS
- 🎨 **Clean UI**: shadcn/ui components with Radix primitives
- 📱 **Responsive Design**: Mobile-first responsive layout
- 🔧 **Admin Interface**: Database monitoring and management
- 🚀 **Production Ready**: Dockerized with optimized builds

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React
- **Build**: Docker with standalone output

## Development

### Prerequisites

- Node.js 20+
- npm or yarn

### Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

### Environment Variables

Copy `.env.example` to `.env.local` and configure:

```env
NEXT_PUBLIC_API_URL=http://db.localhost:8081
NEXT_PUBLIC_API_TIMEOUT=30000
NEXT_PUBLIC_APP_NAME="DB-Forge Admin"
NEXT_PUBLIC_APP_DESCRIPTION="Database Management Platform"
```

## Docker

### Build Image

```bash
docker build -t db-forge-frontend .
```

### Run Container

```bash
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://db.localhost:8081 \
  db-forge-frontend
```

## Architecture

```
src/
├── app/                 # Next.js App Router pages
│   ├── globals.css      # Global styles with Tailwind + shadcn/ui
│   ├── layout.tsx       # Root layout
│   └── page.tsx         # Home page
├── components/
│   ├── ui/              # shadcn/ui components
│   └── dashboard/       # Custom dashboard components
│       ├── dashboard-shell.tsx
│       └── database-overview.tsx
└── lib/
    ├── api.ts           # API client
    └── utils.ts         # Utilities (cn function, etc.)
```

## Features Overview

### Dashboard Shell
- Responsive sidebar navigation
- Mobile-friendly hamburger menu
- System status indicator
- Clean, professional layout

### Database Overview
- Statistics cards for key metrics
- Database instance monitoring
- Connection tracking
- Health status indicators

### API Integration
- Type-safe API client
- Error handling and timeouts
- Environment-based configuration

## Integration

The frontend integrates with the DB-Forge stack via:

- **API**: Communicates with `db-gateway` service
- **Routing**: Traefik handles routing via `frontend.db.localhost`
- **Docker**: Runs as part of the complete stack

## Development Workflow

1. **Local Development**: Run `npm run dev` for hot reloading
2. **API Integration**: Configure API URL to point to running db-gateway
3. **Building**: Use `npm run build` to create production build
4. **Docker**: Use provided Dockerfile for containerization

## Contributing

1. Follow TypeScript best practices
2. Use shadcn/ui components when possible
3. Maintain responsive design principles
4. Add proper error handling for API calls
5. Keep components small and focused
