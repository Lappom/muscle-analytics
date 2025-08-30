# Scripts Utilitaires

Ce dossier contient les scripts d'administration et utilitaires pour le projet Muscle-Analytics.

## Scripts disponibles

### `run_api.py`
Script pour démarrer l'API FastAPI en mode développement.

```bash
# Démarrage simple
python scripts/run_api.py

# Avec options
python scripts/run_api.py --host 0.0.0.0 --port 8080 --reload

# Aide
python scripts/run_api.py --help
```

**Options :**
- `--host` : Adresse d'écoute (défaut: localhost)
- `--port` : Port d'écoute (défaut: 8000)
- `--reload` : Mode rechargement automatique
- `--log-level` : Niveau de log (défaut: info)

### `setup_databases.py`
Script de configuration et test des bases de données.

```bash
# Démonstration complète
python scripts/setup_databases.py demo

# Afficher la configuration
python scripts/setup_databases.py config

# Créer le template .env
python scripts/setup_databases.py template

# Tester les connexions
python scripts/setup_databases.py test
```

### `test_api_docker.py`
Test rapide de l'API containerisée.

```bash
# Test de l'API en container
python scripts/test_api_docker.py
```

### `clean_project.py`
Script de nettoyage automatique de l'arborescence.

```bash
# Voir ce qui serait nettoyé
python scripts/clean_project.py --dry-run

# Nettoyer réellement
python scripts/clean_project.py
```

**Supprime automatiquement :**
- Dossiers `__pycache__/` (sauf dans .venv)
- Fichiers `.pyc`, `.pyo`, `.pyd`
- Fichiers de log (`.log`)
- Fichiers temporaires (`.DS_Store`, `Thumbs.db`)
- Fichiers de couverture (`.coverage`, `htmlcov/`, `.pytest_cache/`)

## Usage recommandé

1. **Configuration initiale :**
   ```bash
   python scripts/setup_databases.py template
   cp .env.template .env
   # Éditer .env avec vos mots de passe
   ```

2. **Test de la configuration :**
   ```bash
   python scripts/setup_databases.py test
   ```

3. **Démarrage en développement :**
   ```bash
   python scripts/run_api.py --reload
   ```

4. **Test container :**
   ```bash
   docker-compose up -d
   python scripts/test_api_docker.py
   ```
