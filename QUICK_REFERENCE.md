# 🚀 DB-Forge Quick Reference

## Instant Commands

### **Start/Stop**
```bash
make up          # Start all services
make down        # Stop all services  
make restart     # Restart everything
make rebuild     # Force rebuild + start
```

### **Development**
```bash
make logs                    # View all logs
make shell-frontend          # Frontend container shell
make shell-gateway          # Backend container shell
make frontend-build         # Rebuild frontend only
```

### **Access Points**
- **Dashboard**: http://frontend.db.localhost:8081
- **API Docs**: http://db.localhost:8081/docs
- **Traefik**: http://localhost:8080/dashboard/

## API Testing

### **Quick Test**
```bash
# Test backend health
curl -H "X-API-Key: development-api-key-12345" \
     -H "Host: db.localhost" \
     http://localhost:8081/admin/gateway/stats

# List databases  
curl -H "X-API-Key: development-api-key-12345" \
     -H "Host: db.localhost" \
     http://localhost:8081/admin/databases

# Create database
curl -X POST -H "X-API-Key: development-api-key-12345" \
     -H "Host: db.localhost" \
     http://localhost:8081/admin/databases/spawn/test-db
```

### **Authentication**
- **API Key**: `development-api-key-12345`
- **Header**: `X-API-Key: development-api-key-12345`
- **Required for**: All `/admin` and `/api` endpoints

## File Locations

### **Key Files**
```
services/db-gateway/app/main.py           # Backend entry point
services/frontend/src/lib/api.ts          # API client
services/frontend/src/app/*/page.tsx      # Dashboard pages
infra/docker-compose.yml                  # Service config
Makefile                                  # Commands
context.md                                # Full context guide
```

### **Add New Page**
1. Create `services/frontend/src/app/my-page/page.tsx`
2. Add to navigation in `dashboard-shell.tsx`
3. Create component in `services/frontend/src/components/my-page/`

### **Add New API Endpoint**
1. Add route in `services/db-gateway/app/routes/`
2. Update `services/frontend/src/lib/api.ts`
3. Use in frontend components

## Troubleshooting

### **Common Fixes**
```bash
# Container issues
docker system prune -f

# Port conflicts  
make down && sleep 5 && make up

# Build issues
make rebuild

# Permission issues
sudo chown -R $USER:$USER .
```

### **Check Status**
```bash
docker ps                    # Running containers
docker logs db-gateway       # Backend logs
docker logs db-forge-frontend # Frontend logs
docker logs traefik-db-forge # Proxy logs
```

---
**💡 Tip: Always check `context.md` for complete details!**