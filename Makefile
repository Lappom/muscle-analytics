# Commandes utiles pour le projet Muscle-Analytics

.DEFAULT_GOAL := help

## Variables
PYTHON := python
SCRIPTS_DIR := scripts

## Aide
help: ## Affiche cette aide
	@echo "🏋️ Muscle-Analytics - Commandes disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

## Installation et configuration
install: ## Installe les dépendances
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -r requirements-dev.txt

setup-env: ## Crée le fichier .env à partir du template
	$(PYTHON) $(SCRIPTS_DIR)/setup_databases.py template

config: ## Affiche la configuration actuelle
	$(PYTHON) $(SCRIPTS_DIR)/setup_databases.py config

test-db: ## Teste les connexions aux bases de données
	$(PYTHON) $(SCRIPTS_DIR)/setup_databases.py test

## Développement
dev: ## Démarre l'API en mode développement
	$(PYTHON) $(SCRIPTS_DIR)/run_api.py --reload

start: ## Démarre l'API en mode production
	$(PYTHON) $(SCRIPTS_DIR)/run_api.py

## Tests
test: ## Lance les tests unitaires
	$(PYTHON) -m pytest tests/ -v

test-cov: ## Lance les tests avec couverture
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

## Docker
docker-build: ## Construit l'image Docker
	docker-compose build

docker-up: ## Démarre les services Docker
	docker-compose up -d

docker-down: ## Arrête les services Docker
	docker-compose down

docker-test: ## Teste l'API containerisée
	$(PYTHON) $(SCRIPTS_DIR)/test_api_docker.py

## Maintenance
clean: ## Nettoie le projet (fichiers temporaires, cache, etc.)
	$(PYTHON) $(SCRIPTS_DIR)/clean_project.py

clean-all: ## Nettoyage complet avec suppression des fichiers de démonstration
	@echo "🧹 Nettoyage complet du projet..."
	$(PYTHON) $(SCRIPTS_DIR)/clean_project.py
	@echo "✅ Nettoyage terminé !"

lint: ## Vérifie le style du code
	$(PYTHON) -m flake8 src/ tests/
	$(PYTHON) -m black --check src/ tests/

format: ## Formate le code
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m isort src/ tests/

## Documentation
docs: ## Génère la documentation API
	@echo "📚 Documentation disponible:"
	@echo "  API: http://localhost:8000/docs"
	@echo "  Redoc: http://localhost:8000/redoc"

.PHONY: help install setup-env config test-db dev start test test-cov docker-build docker-up docker-down docker-test clean clean-all lint format docs
