# ======================================================================================
#                        PRAETORIAN DB-FORGE - ORCHESTRATOR
# ======================================================================================
#  The Unified Master Control Program for the DB-Forge Stack.
# ======================================================================================
SHELL := /bin/bash
COMPOSE := docker-compose

# --- Cosmetics ---
GREEN   := \033[0;32m
YELLOW  := \033[0;33m
PURPLE  := \033[0;35m
CYAN    := \033[0;36m
RED     := \033[0;31m
NC      := \033[0m

.DEFAULT_GOAL := help

help:
	@echo -e "${PURPLE}Praetorian DB-Forge - Master Control Program${NC}"
	@echo -e "${YELLOW}Usage:${NC} make [target]\n"
	@echo -e "${GREEN}Core Stack Management:${NC}"
	@echo -e "  ${CYAN}up${NC}        - Builds and ignites the entire DB-Forge stack."
	@echo -e "  ${CYAN}down${NC}      - Shuts down the stack and removes containers."
	@echo -e "  ${CYAN}re${NC}        - ${YELLOW}Obliterates and completely rebuilds the stack from scratch.${NC}"
	@echo -e "\n${GREEN}Diagnostics:${NC}"
	@echo -e "  ${CYAN}status${NC}    - Displays the status of all services."
	@echo -e "  ${CYAN}logs${NC}      - Taps into the data stream of the db-gateway."
	@echo -e "  ${CYAN}ssh${NC}       - Establishes a shell into the db-gateway."
	@echo -e "\n${GREEN}Sanitization:${NC}"
	@echo -e "  ${CYAN}clean${NC}     - ${RED}DANGER:${NC} Obliterates all stack containers, networks, and data volumes."

# --- CORE STACK MANAGEMENT ---
up: build
	@echo -e "${GREEN}Igniting the DB-Forge stack...${NC}"
	@mkdir -p ./db-data
	@$(COMPOSE) up -d --remove-orphans

down:
	@echo -e "${RED}Shutting down the DB-Forge stack...${NC}"
	@$(COMPOSE) down --remove-orphans

re: clean up
	@echo -e "${GREEN}Stack has been reforged and reignited from a clean slate.${NC}"

# --- BUILDING ---
build:
	@echo -e "${CYAN}Building base image for DB workers...${NC}"
	@docker build -t db-worker-base:latest -f infra/db-worker-base/Dockerfile .
	@echo -e "${CYAN}Building all service images...${NC}"
	@$(COMPOSE) build

# --- DIAGNOSTICS ---
status:
	@$(COMPOSE) ps

logs:
	@$(COMPOSE) logs -f db-gateway

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

.PHONY: help up down re build status logs ssh clean test clean-test-dbs
