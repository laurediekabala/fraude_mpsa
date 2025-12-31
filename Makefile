.PHONY: help build up down logs restart clean test prod-up prod-down

# Couleurs pour l'output
BLUE := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# ═══════════════════════════════════════════════════════════════
# HELP
# ═══════════════════════════════════════════════════════════════

help:
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Fraude Detection System - Docker Management$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  $(YELLOW)make build$(NC)           - Build les images Docker"
	@echo "  $(YELLOW)make up$(NC)              - Démarrer tous les services"
	@echo "  $(YELLOW)make down$(NC)            - Arrêter tous les services"
	@echo "  $(YELLOW)make restart$(NC)         - Redémarrer tous les services"
	@echo "  $(YELLOW)make logs$(NC)            - Voir les logs (suivi en direct)"
	@echo "  $(YELLOW)make logs-api$(NC)        - Logs de l'API uniquement"
	@echo "  $(YELLOW)make logs-web$(NC)        - Logs de Streamlit uniquement"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  $(YELLOW)make test$(NC)            - Tester la connexion API"
	@echo "  $(YELLOW)make status$(NC)          - Voir le statut des services"
	@echo "  $(YELLOW)make health$(NC)          - Vérifier la santé des services"
	@echo ""
	@echo "$(GREEN)Database & Cleanup:$(NC)"
	@echo "  $(YELLOW)make clean$(NC)           - Nettoyer les ressources Docker"
	@echo "  $(YELLOW)make clean-volumes$(NC)   - Supprimer les volumes (⚠️ perte de données)"
	@echo "  $(YELLOW)make reset$(NC)           - Reset complet (images, volumes, conteneurs)"
	@echo ""
	@echo "$(GREEN)Production:$(NC)"
	@echo "  $(YELLOW)make prod-up$(NC)         - Démarrer mode production"
	@echo "  $(YELLOW)make prod-down$(NC)       - Arrêter mode production"
	@echo ""
	@echo "$(GREEN)Admin:$(NC)"
	@echo "  $(YELLOW)make shell-api$(NC)       - Shell du conteneur API"
	@echo "  $(YELLOW)make shell-web$(NC)       - Shell du conteneur Streamlit"
	@echo "  $(YELLOW)make inspect$(NC)         - Détails des conteneurs"
	@echo "  $(YELLOW)make prune$(NC)           - Nettoyer les ressources orphelines"
	@echo ""

# ═══════════════════════════════════════════════════════════════
# BUILD & DEPLOYMENT
# ═══════════════════════════════════════════════════════════════

build:
	@echo "$(YELLOW)🔨 Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✅ Build completed!$(NC)"

up: build
	@echo "$(YELLOW)🚀 Starting services...$(NC)"
	docker-compose up -d
	@echo "$(YELLOW)⏳ Waiting for health checks (30 seconds)...$(NC)"
	@sleep 30
	@echo "$(GREEN)✅ Services started!$(NC)"
	@echo "$(BLUE)📊 API:        http://localhost:5000$(NC)"
	@echo "$(BLUE)🎨 Streamlit:  http://localhost:8501$(NC)"

down:
	@echo "$(YELLOW)🛑 Stopping services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✅ Services stopped!$(NC)"

restart:
	@echo "$(YELLOW)🔄 Restarting services...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✅ Services restarted!$(NC)"

# ═══════════════════════════════════════════════════════════════
# LOGS & MONITORING
# ═══════════════════════════════════════════════════════════════

logs:
	@echo "$(YELLOW)📋 Showing logs (Ctrl+C to stop)...$(NC)"
	docker-compose logs -f

logs-api:
	@echo "$(YELLOW)📋 API logs (Ctrl+C to stop)...$(NC)"
	docker-compose logs -f api

logs-web:
	@echo "$(YELLOW)📋 Streamlit logs (Ctrl+C to stop)...$(NC)"
	docker-compose logs -f streamlit

status:
	@echo "$(BLUE)📊 Service Status:$(NC)"
	@docker-compose ps

health:
	@echo "$(BLUE)💚 Health Check:$(NC)"
	@echo "  API:       $$(curl -s http://localhost:5000/health | grep -o 'success' || echo '❌ Down')"
	@echo "  Streamlit: $$(curl -s http://localhost:8501/_stcore/health | grep -o 'ok' || echo '❌ Down')"

# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

test: up
	@echo "$(YELLOW)🧪 Testing API...$(NC)"
	@curl -X GET http://localhost:5000/health -v
	@echo ""
	@echo "$(GREEN)✅ Test completed!$(NC)"

test-predict:
	@echo "$(YELLOW)🧪 Testing prediction endpoint...$(NC)"
	@curl -X POST http://localhost:5000/predict \
		-H "Content-Type: application/json" \
		-d '{"amount": 5000, "type": "TRANSFER"}' -v

# ═══════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════

clean:
	@echo "$(YELLOW)🧹 Cleaning up Docker resources...$(NC)"
	docker-compose down
	docker image prune -f
	docker container prune -f
	@echo "$(GREEN)✅ Cleanup completed!$(NC)"

clean-volumes:
	@echo "$(RED)⚠️  WARNING: This will delete all volumes and data!$(NC)"
	@read -p "Continue? (y/n) " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "$(GREEN)✅ Volumes deleted!$(NC)"; \
	fi

reset: clean clean-volumes
	@echo "$(YELLOW)🔄 Resetting Docker environment...$(NC)"
	docker system prune -a -f
	@echo "$(GREEN)✅ Full reset completed!$(NC)"

# ═══════════════════════════════════════════════════════════════
# PRODUCTION
# ═══════════════════════════════════════════════════════════════

prod-up:
	@echo "$(YELLOW)🚀 Starting PRODUCTION services...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✅ Production services started!$(NC)"

prod-down:
	@echo "$(YELLOW)🛑 Stopping PRODUCTION services...$(NC)"
	docker-compose -f docker-compose.prod.yml down
	@echo "$(GREEN)✅ Production services stopped!$(NC)"

# ═══════════════════════════════════════════════════════════════
# ADMIN
# ═══════════════════════════════════════════════════════════════

shell-api:
	@echo "$(YELLOW)🐚 Opening API container shell...$(NC)"
	docker exec -it fraude_api bash

shell-web:
	@echo "$(YELLOW)🐚 Opening Streamlit container shell...$(NC)"
	docker exec -it fraude_streamlit bash

inspect:
	@echo "$(BLUE)📊 Container Details:$(NC)"
	@docker inspect fraude_api | grep -E 'Id|State|Ports'
	@docker inspect fraude_streamlit | grep -E 'Id|State|Ports'

prune:
	@echo "$(YELLOW)🧹 Pruning Docker system...$(NC)"
	docker system prune -f
	@echo "$(GREEN)✅ Prune completed!$(NC)"

# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════

stats:
	@echo "$(BLUE)📊 Docker Container Stats:$(NC)"
	docker stats --no-stream

backup-baseline:
	@echo "$(YELLOW)💾 Backing up baseline...$(NC)"
	@docker cp fraude_api:/app/api_flask/drift_baseline.json ./drift_baseline.backup.json 2>/dev/null || echo "$(YELLOW)Baseline not found$(NC)"
	@echo "$(GREEN)✅ Backup completed!$(NC)"

version:
	@echo "$(BLUE)Docker version:$(NC)"
	@docker --version
	@echo "$(BLUE)Docker Compose version:$(NC)"
	@docker-compose --version
