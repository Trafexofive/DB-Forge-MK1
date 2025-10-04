# ======================================================================================
#                        PRAETORIAN DB-FORGE - ORCHESTRATOR
# ======================================================================================
#  The Unified Master Control Program for the DB-Forge Stack.
# ======================================================================================
SHELL := /bin/bash
.SHELLFLAGS := -o pipefail -c

# DB-Forge specific compose configuration
COMPOSE := docker-compose -f infra/docker-compose.yml --env-file infra/.env
COMPOSE_DEV := docker-compose -f infra/docker-compose.yml -f infra/docker-compose.dev.yml --env-file infra/.env

# Universal compose configuration (for generic rules)
COMPOSE_FILE ?= infra/docker-compose.yml
COMPOSE_UNIVERSAL := docker compose -f $(COMPOSE_FILE) --env-file infra/.env
PROJECT_NAME ?= db-forge

# --- Cosmetics ---
GREEN   := \033[0;32m
YELLOW  := \033[0;33m
PURPLE  := \033[0;35m
CYAN    := \033[0;36m
RED     := \033[0;31m
BLUE    := \033[0;34m
NC      := \033[0m

.DEFAULT_GOAL := help

help:
	@echo -e "${PURPLE}Praetorian DB-Forge - Master Control Program${NC}"
	@echo -e "${YELLOW}Usage:${NC} make [target] [service=SERVICE_NAME] [args=\"ARGS\"]\n"
	@echo -e "${GREEN}Core Stack Management:${NC}"
	@echo -e "  ${CYAN}up${NC}        - Builds and ignites the entire DB-Forge stack."
	@echo -e "  ${CYAN}down${NC}      - Shuts down the stack and removes containers."
	@echo -e "  ${CYAN}re${NC}        - ${YELLOW}Obliterates and completely rebuilds the stack from scratch.${NC}"
	@echo -e "  ${CYAN}restart${NC}   - Restarts all services."
	@echo -e "  ${CYAN}pull${NC}      - Pulls latest images for services."
	@echo -e "  ${CYAN}stop${NC}      - Stop services without removing containers."
	@echo -e "\n${GREEN}Development:${NC}"
	@echo -e "  ${CYAN}dev${NC}       - Start stack in development mode with live reload."
	@echo -e "  ${CYAN}build${NC}     - Build all service images."
	@echo -e "  ${CYAN}rebuild${NC}   - Force rebuild all images (no cache)."
	@echo -e "\n${GREEN}Frontend Development:${NC}"
	@echo -e "  ${CYAN}frontend-dev${NC}  - Run frontend in development mode (localhost:3000)."
	@echo -e "  ${CYAN}frontend-build${NC} - Build frontend for production."
	@echo -e "  ${CYAN}frontend-install${NC} - Install frontend dependencies."
	@echo -e "  ${CYAN}frontend-lint${NC} - Lint frontend code.
	@echo -e "\n${GREEN}Diagnostics & Universal Tools:${NC}"
	@echo -e "  ${CYAN}status${NC}    - Displays the status of all services (alias: ps)."
	@echo -e "  ${CYAN}logs${NC}      - Taps into the data stream of the db-gateway."
	@echo -e "  ${CYAN}logs-all${NC}  - Shows logs for all services."
	@echo -e "  ${CYAN}ssh${NC}       - Establishes a shell into the db-gateway (alias: it)."
	@echo -e "  ${CYAN}exec${NC}      - Execute command in service: make exec service=NAME args=\"command\""
	@echo -e "  ${CYAN}inspect${NC}   - Inspect a running service container."
	@echo -e "  ${CYAN}health${NC}    - Check health status of all services."
	@echo -e "  ${CYAN}config${NC}    - Validate and show effective compose configuration."
	@echo -e "\n${GREEN}Testing:${NC}"
	@echo -e "  ${CYAN}test${NC}      - Runs the full test suite."
	@echo -e "\n${GREEN}Sanitization:${NC}"
	@echo -e "  ${CYAN}clean${NC}     - ${RED}DANGER:${NC} Obliterates all stack containers, networks, and data volumes."
	@echo -e "  ${CYAN}fclean${NC}    - ${RED}EXTREME DANGER:${NC} Deep clean including volumes and images."
	@echo -e "  ${CYAN}prune${NC}     - Removes unused Docker resources system-wide."

# --- CORE STACK MANAGEMENT ---
up: build
	@echo -e "${GREEN}Igniting the DB-Forge stack...${NC}"
	@mkdir -p ./db-data
	@$(COMPOSE) up -d --remove-orphans

down:
	@echo -e "${RED}Shutting down the DB-Forge stack...${NC}"
	@$(COMPOSE) down --remove-orphans

restart:
	@echo -e "${YELLOW}Restarting the DB-Forge stack...${NC}"
	@$(COMPOSE) restart

pull:
	@echo -e "${CYAN}Pulling latest images...${NC}"
	@$(COMPOSE) pull

re: clean up
	@echo -e "${GREEN}Stack has been reforged and reignited from a clean slate.${NC}"

# --- DEVELOPMENT ---
dev: build
	@echo -e "${GREEN}Starting DB-Forge in development mode...${NC}"
	@mkdir -p ./db-data
	@$(COMPOSE_DEV) up -d --remove-orphans

# --- BUILDING ---
build:
	@echo -e "${CYAN}Building base image for DB workers...${NC}"
	@docker build -t db-worker-base:latest -f infra/db-worker-base/Dockerfile .
	@echo -e "${CYAN}Building all service images...${NC}"
	@$(COMPOSE) build

rebuild:
	@echo -e "${CYAN}Force rebuilding all images...${NC}"
	@docker build --no-cache -t db-worker-base:latest -f infra/db-worker-base/Dockerfile .
	@$(COMPOSE) build --no-cache

# --- DIAGNOSTICS ---
status:
	@$(COMPOSE) ps

logs:
	@$(COMPOSE) logs -f db-gateway

logs-all:
	@$(COMPOSE) logs -f

ssh:
	@$(COMPOSE) exec db-gateway /bin/bash

# --- TESTING ---
test:
	@echo -e "${CYAN}Ensuring all services are down before cleanup...${NC}"
	@$(COMPOSE) down
	@$(MAKE) clean-test-dbs
	@echo -e "${CYAN}Bringing services back up for testing...${NC}"
	@$(COMPOSE) up -d
	@echo -e "${CYAN}Running API tests...${NC}"
	@./scripts/test.sh

clean-test-dbs:
	@echo -e "${RED}Cleaning up test databases...${NC}"
	# Stop and remove all db-worker containers
	-@for id in $(docker ps -a -q --filter "label=db-worker"); do docker stop $id && docker rm -f $id; done
	# Remove the persistent data directory
	sleep 1 # Give Docker a moment to release file locks
	@rm -rf ./db-data

# --- SANITIZATION ---
clean:
	@echo -e "${RED}DANGER: Obliterating all stack containers, networks, and data volumes...${NC}"
	@$(COMPOSE) down -v --remove-orphans
	-@for id in $$(docker ps -a -q --filter "label=db-worker"); do docker stop $$id && docker rm -f $$id; done
	@rm -rf ./db-data

prune:
	@echo -e "${YELLOW}Removing unused Docker resources...${NC}"
	@docker system prune -f
	@docker volume prune -f

# ======================================================================================
# UNIVERSAL COMPOSE UTILITIES (from universal makefile)
# ======================================================================================

# --- Additional aliases for compatibility ---
start: up ## Alias for up
ps: status ## Alias for status
it: ssh ## Alias for ssh
rere: clean rebuild up ## Rebuild without cache and restart

# --- Validation utilities ---
validate-compose: ## Validate compose file syntax
	@echo -e "${BLUE}Validating compose configuration...${NC}"
	@$(COMPOSE_UNIVERSAL) config --quiet && echo -e "${GREEN}✓ Compose file is valid${NC}" || (echo -e "${RED}✗ Compose file validation failed${NC}" && exit 1)

check-running: ## Check which services are currently running
	@echo -e "${BLUE}Checking running services for DB-Forge...${NC}"
	@_running=$$($(COMPOSE) ps --services --filter "status=running" 2>/dev/null); \
	if [ -z "$$_running" ]; then \
		echo -e "${YELLOW}No services currently running.${NC}"; \
	else \
		echo -e "${GREEN}Running services:${NC}"; \
		echo "$$_running" | sed 's/^/  - /'; \
	fi

# --- Enhanced stop command ---
stop: ## Stop all services without removing them
	@echo -e "${YELLOW}Stopping services...${NC}"
	@$(COMPOSE) stop $(service)
	@echo -e "${GREEN}✓ Services stopped (containers preserved).${NC}"

# --- Enhanced exec command ---
exec: ## Execute a command in a running service container
	@if [ -z "$(service)" ] || [ -z "$(args)" ]; then \
		echo -e "${RED}Error: Service name and command required. Usage: make exec service=<service_name> args=\"<command>\"${NC}"; \
		exit 1; \
	fi
	@echo -e "${GREEN}Executing in $(service): $(args)${NC}"
	@$(COMPOSE) exec $(service) $(args)

# --- Inspect command ---
inspect: ## Inspect a running service container
	@if [ -z "$(service)" ]; then \
		echo -e "${RED}Error: Service name required. Usage: make inspect service=<service_name>${NC}"; \
		exit 1; \
	fi
	@echo -e "${BLUE}Inspecting $(service)...${NC}"
	@_container_id=$$($(COMPOSE) ps -q $(service) | head -n 1); \
	if [ -z "$$_container_id" ]; then \
		echo -e "${RED}Service $(service) not found or not running.${NC}"; \
		exit 1; \
	fi; \
	docker inspect $$_container_id

# --- Health check ---
health: ## Check health status of services
	@echo -e "${BLUE}Health check for services:${NC}"
	@for service in $$($(COMPOSE) ps --services 2>/dev/null); do \
		_health=$$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no healthcheck{{end}}' "$$($(COMPOSE) ps -q $$service 2>/dev/null)" 2>/dev/null); \
		if [ "$$_health" = "healthy" ]; then \
			echo -e "  ${GREEN}✓${NC} $$service: $$_health"; \
		elif [ "$$_health" = "unhealthy" ]; then \
			echo -e "  ${RED}✗${NC} $$service: $$_health"; \
		else \
			echo -e "  ${YELLOW}○${NC} $$service: $$_health"; \
		fi \
	done

# --- Configuration display ---
config: validate-compose ## Validate and display effective Docker Compose configuration
	@echo -e "${BLUE}Effective Configuration:${NC}"
	@$(COMPOSE) config

# --- Volume and network listing ---
project-volumes: ## List volumes for this project only
	@echo -e "${BLUE}Volumes for DB-Forge project:${NC}"
	@docker volume ls --filter label=com.docker.compose.project=$(PROJECT_NAME) --format "table {{.Driver}}\t{{.Name}}" || echo "No project volumes found"

project-networks: ## List networks for this project only
	@echo -e "${BLUE}Networks for DB-Forge project:${NC}"
	@docker network ls --filter label=com.docker.compose.project=$(PROJECT_NAME) --format "table {{.Driver}}\t{{.Name}}\t{{.Scope}}" || echo "No project networks found"

list-volumes: ## List all Docker volumes
	@echo -e "${BLUE}All Docker Volumes:${NC}"
	@docker volume ls

list-networks: ## List all Docker networks
	@echo -e "${BLUE}All Docker Networks:${NC}"
	@docker network ls

# --- Enhanced cleaning ---
fclean: ## Remove containers, networks, volumes, and images
	@echo -e "${RED}Deep cleaning: containers, networks, volumes, and images...${NC}"
	@read -p "This will remove ALL project data including volumes. Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(COMPOSE) down --volumes --remove-orphans --rmi local; \
		-@for id in $$(docker ps -a -q --filter "label=db-worker"); do docker stop $$id && docker rm -f $$id; done; \
		@rm -rf ./db-data; \
		echo -e "${GREEN}✓ Deep clean complete.${NC}"; \
	else \
		echo -e "${YELLOW}Aborted.${NC}"; \
	fi

# --- FRONTEND DEVELOPMENT ---
frontend-install: ## Install frontend dependencies
	@echo -e "${CYAN}Installing frontend dependencies...${NC}"
	@cd services/frontend && npm install

frontend-dev: ## Run frontend in development mode
	@echo -e "${GREEN}Starting frontend development server...${NC}"
	@cd services/frontend && npm run dev

frontend-build: ## Build frontend for production
	@echo -e "${CYAN}Building frontend for production...${NC}"
	@cd services/frontend && npm run build

frontend-lint: ## Lint frontend code
	@echo -e "${CYAN}Linting frontend code...${NC}"
	@cd services/frontend && npm run lint

frontend-clean: ## Clean frontend build artifacts
	@echo -e "${RED}Cleaning frontend build artifacts...${NC}"
	@cd services/frontend && rm -rf .next && rm -rf node_modules/.cache

# Phony targets
.PHONY: help up down restart pull re dev build rebuild status logs logs-all ssh clean test clean-test-dbs prune \
        stop start ps exec inspect list-volumes list-networks validate-compose check-running \
        project-volumes project-networks health config rere fclean it \
        frontend-install frontend-dev frontend-build frontend-lint frontend-clean
