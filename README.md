# 💪 Muscle-Analytics

> Plateforme d'analyse et de prédiction intelligente pour l'entraînement de force

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Security](https://img.shields.io/badge/Security-Enhanced-green.svg)](README.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Un projet **Data Science & IA** qui transforme vos logs d'entraînements (CSV/XML) en **insights actionnables** : dashboards interactifs, métriques de progression, estimations 1RM et prédictions pour optimiser votre entraînement.

## 🚀 Démarrage avec Docker (Recommandé)

Le moyen le plus simple de démarrer est d'utiliser Docker et Docker Compose.

```bash
# 1. Cloner le projet
git clone https://github.com/Lappom/muscle-analytics.git
cd muscle-analytics

# 2. Lancer l'environnement complet
docker-compose up

# 3. C'est prêt !
# 🌐 API : http://localhost:8000
# 📚 Documentation interactive : http://localhost:8000/docs
```

Une fois l'application lancée, vous pouvez tester les points d'accès de l'API :

```bash
# Test rapide de l'API
python examples/demo_api_complete.py

# Ou voir les données de démo
curl http://localhost:8000/analytics/dashboard
```

## 🎯 Objectif

Convertir vos logs de musculation en **insights actionnables** :

- 📊 **Volume et progression** par exercice
- 🎯 **Estimation 1RM** avec formules validées
- 📈 **Détection de plateaux** et anomalies
- 🔮 **Forecasting** du volume hebdomadaire
- 💡 **Recommandations** personnalisées

## ✨ Fonctionnalités principales

- **🔄 Ingestion & ETL** : Parsers robustes pour CSV/XML, normalisation et import intelligent.
- **📊 API REST Complète** : Endpoints FastAPI modernes pour les sessions, exercices et analyses.
- **🧮 Calculs de Features Avancés** : Volume, 1RM, tendances de progression, et moyennes mobiles.
- **🤖 Intelligence Artificielle (Prévu)** : Forecasting, détection d'anomalies et recommandations.

## 🛠️ Tech Stack

- **Backend & ML** : Python 3.9+, FastAPI, Pandas, Scikit-learn, SQLAlchemy.
- **Infrastructure** : PostgreSQL, Docker & Docker Compose.
- **Qualité & CI/CD** : pytest, GitHub Actions, Black, isort, flake8.

---

<details>
<summary>👨‍💻 Pour les développeurs : Développement local et configuration avancée</summary>

### 🔧 Développement Local (Sans Docker)

Si vous préférez travailler sans Docker, vous pouvez configurer un environnement local.

```bash
# 1. Créer un environnement virtuel et l'activer
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements-dev.txt

# 3. Configurer les bases de données (dev et test)
# Ce script crée les BDD si elles n'existent pas
python scripts/setup_databases.py

# 4. Lancer les tests pour valider la configuration
pytest

# 5. Démarrer l'API en mode développement
uvicorn src.api.main:app --reload
```

### 🔒 Gestion des environnements

Le projet est conçu pour fonctionner dans différents environnements (`dev`, `test`, `docker`). La configuration est gérée via des variables d'environnement.

1.  **Copiez le fichier d'exemple** : `cp .env.example .env`
2.  **Modifiez `.env`** : Adaptez les variables à votre configuration locale (ports, mots de passe, etc.).

Le module `src/config/database.py` lit ce fichier `.env` pour configurer la connexion à la base de données appropriée en fonction du contexte.

### 🧪 Tests

Lancez les tests pour vous assurer que tout fonctionne comme prévu.

```bash
# Lancer tous les tests avec la couverture de code
pytest --cov=src --cov-report=html

# Lancer un fichier de test spécifique
pytest tests/test_api_endpoints.py -v
```

### 🗂️ Structure du projet

```
muscle-analytics/
├── src/                    # Code source principal
│   ├── api/                # API FastAPI
│   ├── config/             # Configuration (gestion des environnements)
│   ├── database.py         # Module de connexion DB
│   ├── etl/                # Pipeline ETL
│   └── features/           # Calculs de features
├── tests/                  # Tests unitaires et d'intégration
├── examples/               # Scripts de démonstration
├── notebooks/              # Analyses EDA
├── docker-compose.yml      # Environnement Docker
└── .env.example            # Template de configuration
```

</details>

---

## 🗺️ Roadmap & Contribution

Consultez [ROADMAP.md](ROADMAP.md) pour le plan de développement détaillé. Les contributions sont les bienvenues !

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE).

**⭐ Si ce projet vous plaît, n'oubliez pas de lui donner une étoile !**
