#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script PowerShell pour automatiser les tâches du projet Muscle-Analytics

.DESCRIPTION
    Ce script fournit des raccourcis pour les tâches courantes de développement.

.PARAMETER Command
    Commande à exécuter

.EXAMPLE
    .\scripts.ps1 help
    .\scripts.ps1 dev
    .\scripts.ps1 test
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

# Variables
$ScriptsDir = "scripts"
$Python = "python"

# Fonction d'aide
function Show-Help {
    Write-Host "🏋️ Muscle-Analytics - Commandes disponibles:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📦 Installation et configuration:" -ForegroundColor Yellow
    Write-Host "  install    - Installe les dépendances"
    Write-Host "  setup-env  - Crée le fichier .env à partir du template"
    Write-Host "  config     - Affiche la configuration actuelle"
    Write-Host "  test-db    - Teste les connexions aux bases de données"
    Write-Host ""
    Write-Host "🚀 Développement:" -ForegroundColor Yellow
    Write-Host "  dev        - Démarre l'API en mode développement"
    Write-Host "  start      - Démarre l'API en mode production"
    Write-Host ""
    Write-Host "🧪 Tests:" -ForegroundColor Yellow
    Write-Host "  test       - Lance les tests unitaires"
    Write-Host "  test-cov   - Lance les tests avec couverture"
    Write-Host ""
    Write-Host "🐳 Docker:" -ForegroundColor Yellow
    Write-Host "  docker-build - Construit l'image Docker"
    Write-Host "  docker-up    - Démarre les services Docker"
    Write-Host "  docker-down  - Arrête les services Docker"
    Write-Host "  docker-test  - Teste l'API containerisée"
    Write-Host ""
    Write-Host "🧹 Maintenance:" -ForegroundColor Yellow
    Write-Host "  clean      - Nettoie les fichiers temporaires"
    Write-Host "  clean-dry  - Affiche ce qui serait nettoyé"
    Write-Host "  lint       - Vérifie le style du code"
    Write-Host "  format     - Formate le code"
    Write-Host ""
    Write-Host "📚 Documentation:" -ForegroundColor Yellow
    Write-Host "  docs       - Infos sur la documentation API"
}

# Exécution des commandes
switch ($Command.ToLower()) {
    "help" {
        Show-Help
    }
    "install" {
        Write-Host "📦 Installation des dépendances..." -ForegroundColor Green
        & $Python -m pip install -r requirements.txt
        & $Python -m pip install -r requirements-dev.txt
    }
    "setup-env" {
        Write-Host "📝 Création du fichier .env..." -ForegroundColor Green
        & $Python "$ScriptsDir/setup_databases.py" template
    }
    "config" {
        Write-Host "🔧 Configuration actuelle:" -ForegroundColor Green
        & $Python "$ScriptsDir/setup_databases.py" config
    }
    "test-db" {
        Write-Host "🔍 Test des connexions bases de données..." -ForegroundColor Green
        & $Python "$ScriptsDir/setup_databases.py" test
    }
    "dev" {
        Write-Host "🚀 Démarrage en mode développement..." -ForegroundColor Green
        & $Python "$ScriptsDir/run_api.py" --reload
    }
    "start" {
        Write-Host "🚀 Démarrage de l'API..." -ForegroundColor Green
        & $Python "$ScriptsDir/run_api.py"
    }
    "test" {
        Write-Host "🧪 Lancement des tests..." -ForegroundColor Green
        & $Python -m pytest tests/ -v
    }
    "test-cov" {
        Write-Host "🧪 Tests avec couverture..." -ForegroundColor Green
        & $Python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
    }
    "docker-build" {
        Write-Host "🐳 Construction de l'image Docker..." -ForegroundColor Green
        docker-compose build
    }
    "docker-up" {
        Write-Host "🐳 Démarrage des services Docker..." -ForegroundColor Green
        docker-compose up -d
    }
    "docker-down" {
        Write-Host "🐳 Arrêt des services Docker..." -ForegroundColor Green
        docker-compose down
    }
    "docker-test" {
        Write-Host "🐳 Test de l'API containerisée..." -ForegroundColor Green
        & $Python "$ScriptsDir/test_api_docker.py"
    }
    "clean" {
        Write-Host "🧹 Nettoyage des fichiers temporaires..." -ForegroundColor Green
        & $Python "$ScriptsDir/clean_project.py"
    }
    "clean-dry" {
        Write-Host "🧹 Aperçu du nettoyage..." -ForegroundColor Green
        & $Python "$ScriptsDir/clean_project.py" --dry-run
    }
    "lint" {
        Write-Host "🔍 Vérification du style..." -ForegroundColor Green
        & $Python -m flake8 src/ tests/
        & $Python -m black --check src/ tests/
    }
    "format" {
        Write-Host "✨ Formatage du code..." -ForegroundColor Green
        & $Python -m black src/ tests/
        & $Python -m isort src/ tests/
    }
    "docs" {
        Write-Host "📚 Documentation disponible:" -ForegroundColor Green
        Write-Host "  API: http://localhost:8000/docs" -ForegroundColor Cyan
        Write-Host "  Redoc: http://localhost:8000/redoc" -ForegroundColor Cyan
    }
    default {
        Write-Host "❌ Commande inconnue: $Command" -ForegroundColor Red
        Write-Host "💡 Utilisez 'help' pour voir les commandes disponibles" -ForegroundColor Yellow
        Show-Help
        exit 1
    }
}
