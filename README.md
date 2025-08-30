# 💪 Muscle-Analytics

> Plateforme d'analyse et de prédiction intelligente pour l'entraînement de force

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Security](https://img.shields.io/badge/Security-Enhanced-green.svg)](README.md)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Un projet **Data Science & IA** qui transforme vos logs d'entraînements (CSV/XML) en **insights actionnables** : dashboards interactifs, métriques de progression, estimations 1RM et prédictions pour optimiser votre entraînement.

## 🎯 Objectif

Convertir vos logs de musculation en **insights actionnables** :

- 📊 **Volume et progression** par exercice
- 🎯 **Estimation 1RM** avec formules validées
- 📈 **Détection de plateaux** et anomalies
- 🔮 **Forecasting** du volume hebdomadaire
- 💡 **Recommandations** personnalisées

## 👥 Utilisateurs cibles

- **Vous** (usage personnel)
- **Sportifs étudiants** en sciences du sport
- **Recruteurs** (portfolio technique)

---

## ✨ Fonctionnalités principales

### 🔄 Ingestion & ETL

- **Parsers robustes** CSV/XML avec gestion des formats français
- **Normalisation automatique** : virgules décimales → points, dates → ISO
- **Mapping intelligent** des exercices et groupes musculaires
- **Import incrémental** avec détection de doublons
- **🔐 Configuration sécurisée** : Variables d'environnement pour toutes les connexions DB
- **Tests déterministes** : Configuration par environnement (dev/test/prod)

### 📊 Dashboard interactif

- **Vues globales** : progression générale, volume total
- **Détail par exercice** : courbes de progression, 1RM estimé
- **Calendrier heatmap** : fréquence et intensité des entraînements
- **Comparaisons** : périodes, exercices, groupes musculaires

### 🤖 Intelligence artificielle

- **EDA avancée** avec notebooks Jupyter
- **Forecasting** du volume hebdomadaire (Prophet/ARIMA)
- **Estimation de charge** probable sur X répétitions
- **Détection de plateaux** et anomalies (Isolation Forest)

### ⚠️ Alertes & suggestions

- **Notifications** de plateaux et surentraînement
- **Conseils personnalisés** d'augmentation de charge
- **Recommandations** d'adaptation d'entraînement

---

## 🛠️ Tech Stack

### Backend & ML

- **Python 3.9+** : Pandas, Scikit-learn, NumPy
- **FastAPI** : API REST performante et auto-documentée
- **Prophet/ARIMA** : modèles de forecasting
- **SQLAlchemy** : ORM pour la base de données
- **🔒 Configuration sécurisée** : Gestion multi-environnements

### Frontend

- **React** : dashboard moderne et responsive
- **Streamlit** : alternative rapide pour MVP
- **Plotly/D3.js** : visualisations interactives

### Infrastructure

- **PostgreSQL 13+** : Base de données relationnelle robuste
- **🔒 Multi-environnements** : Configuration sécurisée pour dev/test/prod
- **Docker & Docker Compose** : Déploiement containerisé
- **SQLite** : Alternative pour prototype
- **Redis** : Cache et sessions (optionnel)

### Qualité & CI/CD

- **pytest** : tests unitaires et d'intégration
- **GitHub Actions** : CI/CD automatisé
- **Black, isort, flake8** : qualité du code
- **Coverage** : métriques de tests

---

## 📁 Formats de données supportés (**GymBook** app)

### CSV

```csv
Date,Entraînement,Heure,Exercice,Région,Groupes musculaires (Primaires),Groupes musculaires (Secondaires),Série / Série d'échauffement / Série de récupération,Répétitions / Temps,Poids / Distance,Notes,Sautée
29/08/2025,Upper Body,09:00,Développé couché,Pectoraux,Pectoraux,Triceps,Principale,8,80,Forme parfaite,Non
```

### XML

```xml
<logs>
  <log>
    <date>29/08/2025</date>
    <workout>Upper Body</workout>
    <exercise>Développé couché</exercise>
    <reps>8</reps>
    <weight>80</weight>
  </log>
</logs>
```

**Note :** Le parser est **tolérant aux variantes** (alias d'exercices, décimales avec virgule, espaces insécables) et produit un format canonique avant insertion en DB.

---

## 🗄️ Schéma de base de données

```sql
-- Sessions d'entraînement
sessions (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  start_time TIME,
  training_name VARCHAR(100),
  notes TEXT
);

-- Séries d'exercices
sets (
  id SERIAL PRIMARY KEY,
  session_id INTEGER REFERENCES sessions(id),
  exercise VARCHAR(100) NOT NULL,
  series_type VARCHAR(50), -- 'échauffement', 'principale', 'récupération'
  reps INTEGER,
  weight_kg DECIMAL(5,2),
  notes TEXT,
  skipped BOOLEAN DEFAULT FALSE
);

-- Catalogue d'exercices
exercises (
  name VARCHAR(100) PRIMARY KEY,
  main_region VARCHAR(50),
  muscles_primary TEXT[],
  muscles_secondary TEXT[]
);
```

---

## 🚀 Installation et Configuration

### Prérequis

- **Docker et Docker Compose**
- **Git**
- **Python 3.9+** (pour développement local)

### 🔒 Configuration Sécurisée

```bash
# 1. Cloner le repository
git clone https://github.com/Lappom/muscle-analytics.git
cd muscle-analytics

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres sécurisés
# DB_HOST=localhost
# DB_NAME=muscle_analytics_dev
# DB_USER=muscle_user
# DB_PASSWORD=votre_mot_de_passe_securise
# DB_TEST_NAME=muscle_analytics_test

# 3. Configuration multi-environnements
python setup_databases.py  # Configurer dev/test/prod

# 4. Lancer avec Docker sécurisé
docker compose -f docker-compose.secure.yml up --build

# 5. Accéder à l'application
# Dashboard : http://localhost:3000
# API : http://localhost:8000/docs
```

### 🔧 Développement Local

```bash
# Installation Python (environnement virtuel recommandé)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

pip install -r requirements-dev.txt

# Tests avec configuration sécurisée
pytest tests/ -v

# Lancement API locale
cd src/api && python main.py
```

**Alternative rapide (prototype) :**

```bash
pip install -r requirements.txt
streamlit run app/main.py
```

---

## 🧪 Développement et Architecture

### 🗂️ Structure du projet

```text
muscle-analytics/
├── src/                    # Code source principal
│   ├── api/               # API FastAPI
│   ├── database.py        # Module unifié de gestion DB
│   ├── etl/               # Pipeline ETL sécurisé
│   │   ├── csv_parser.py
│   │   ├── xml_parser.py
│   │   ├── import_scripts.py  # Tests déterministes
│   │   └── pipeline.py
│   └── features/          # Fonctionnalités ML
├── tests/                 # Tests avec config sécurisée
│   ├── test_etl_integration.py
│   └── test_config.py
├── docker-compose.secure.yml  # Docker sécurisé
├── setup_databases.py     # Gestionnaire de configuration
└── .env.example           # Template de configuration
```

### 🔒 Sécurité et Configuration

#### Multi-environnements

- **dev** : PostgreSQL local (port 5432)
- **test** : PostgreSQL séparé (port 5433)
- **docker** : Conteneur avec variables d'environnement
- **prod** : Configuration cloud sécurisée

#### Variables d'environnement

```bash
# Base de données principale
DB_HOST=localhost
DB_NAME=muscle_analytics_dev
DB_USER=muscle_user
DB_PASSWORD=***sécurisé***

# Base de test séparée
DB_TEST_HOST=localhost
DB_TEST_NAME=muscle_analytics_test
DB_TEST_USER=test_user
DB_TEST_PASSWORD=***sécurisé***
```

### 🧪 Tests et Qualité

```bash
# Tests avec configuration sécurisée
pytest tests/ --cov=src --cov-report=html

# Tests spécifiques
pytest tests/test_etl_integration.py -v
pytest tests/test_config.py -v

# Qualité du code
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

### 🔄 Workflow Git

- **`main`** : version stable
- **`dev`** : intégration continue
- **`feat/xxx`** : nouvelles fonctionnalités

---

## 📋 Fonctionnalités Réalisées

- ✅ **Pipeline ETL sécurisé** avec tests déterministes
- ✅ **Configuration multi-environnements** (dev/test/docker/prod)
- ✅ **Gestion unifiée des bases de données** avec variables d'environnement
- ✅ **Tests d'intégration** avec configuration sécurisée
- ✅ **Parsing CSV/XML** pour données GymBook
- ✅ **Architecture modulaire** et extensible
- 📊 **Notebooks EDA** et modèles ML (en cours)
- 🖥️ **Dashboard fonctionnel** + API REST (en cours)
- 🎥 **Vidéo démo** (1-2 min) et rapport technique (prévu)
- 📚 **Documentation complète** et guide utilisateur (en cours)

---

## 🗺️ Roadmap & contribution

Consultez [ROADMAP.md](ROADMAP.md) pour le plan de développement détaillé, les milestones et la checklist par phase.

**Phases principales :**

1. 🎯 **Setup** : Infrastructure et conventions
2. 🔄 **ETL** : Ingestion et normalisation des données
3. 📊 **EDA** : Exploration et features de base
4. 🤖 **ML** : Modèles de prédiction
5. ⚠️ **Alerting** : Détection d'anomalies
6. ✨ **Production** : Déploiement et polish

---

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE) - libre d'utilisation pour des projets personnels et commerciaux.

---

## 👨‍💻 Auteur

## 👨‍💻 Développeur

**Lappom** - Développeur Data Science & ML

- 🐙 **GitHub** : [@Lappom]

---

## 🙏 Remerciements

- Communauté open source Python
- Outils de visualisation (Plotly, D3.js)
- Bibliothèques ML (Scikit-learn, Prophet)

---

**Muscle Analytics** - Optimisez vos entraînements avec l'intelligence artificielle ! 🚀

**⭐ Si ce projet vous plaît, n'oubliez pas de le star !**

[![GitHub stars](https://img.shields.io/github/stars/votre-username/muscle-analytics?style=social)](https://github.com/votre-username/muscle-analytics)

</div>
