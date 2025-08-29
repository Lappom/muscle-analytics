# 💪 Muscle-Analytics

> Plateforme d'analyse et de prédiction intelligente pour l'entraînement de force

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
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

- **Python 3.8+** : Pandas, Scikit-learn, NumPy
- **FastAPI** : API REST performante et auto-documentée
- **Prophet/ARIMA** : modèles de forecasting
- **SQLAlchemy** : ORM pour la base de données

### Frontend

- **React** : dashboard moderne et responsive
- **Streamlit** : alternative rapide pour MVP
- **Plotly/D3.js** : visualisations interactives

### Infrastructure

- **PostgreSQL** : base de données robuste
- **SQLite** : alternative pour prototype
- **Docker & Docker Compose** : containerisation
- **Redis** : cache et sessions (optionnel)

### Qualité & CI/CD

- **pytest** : tests unitaires et d'intégration
- **GitHub Actions** : CI/CD automatisé
- **Black, isort, flake8** : qualité du code
- **Coverage** : métriques de tests

---

## 📁 Formats de données supportés

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

## 🚀 Installation rapide

### Prérequis

- Docker et Docker Compose
- Git

### Démarrage

```bash
# 1. Cloner le repository
git clone https://github.com/Lappom/muscle-analytics.git
cd muscle-analytics

# 2. Configurer l'environnement
cp .env.example .env
# Éditer .env avec vos paramètres DB

# 3. Lancer l'application
docker compose up --build

# 4. Accéder à l'application
# Dashboard : http://localhost:3000
# API : http://localhost:8000/docs
```

**Alternative rapide (prototype) :**

```bash
pip install -r requirements.txt
streamlit run app/main.py
```

---

## 🧪 Développement

### Structure du projet

```
muscle-analytics/
├── app/                    # Application principale
│   ├── api/               # Endpoints FastAPI
│   ├── core/              # Configuration et utilitaires
│   ├── etl/               # Pipeline ETL
│   ├── ml/                # Modèles ML
│   └── ui/                # Interface utilisateur
├── notebooks/             # EDA et expérimentations
├── tests/                 # Tests unitaires et d'intégration
├── docker/                # Configuration Docker
└── docs/                  # Documentation
```

### Workflow Git

- **`main`** : version stable
- **`dev`** : intégration continue
- **`feat/xxx`** : nouvelles fonctionnalités

### Standards de code

```bash
# Tests
pytest tests/ --cov=app --cov-report=html

# Qualité du code
black app/ tests/
isort app/ tests/
flake8 app/ tests/
```

---

## 📋 Livrables

- ✅ **Repository GitHub** avec README et Roadmap
- 📊 **Notebooks EDA** et modèles ML
- 🖥️ **Dashboard fonctionnel** + API REST
- 🎥 **Vidéo démo** (1-2 min) et rapport technique
- 📚 **Documentation complète** et guide utilisateur

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

**Lappom** - Développeur Data Science & ML

- 🐙 **GitHub** : [@Lappom]

---

## 🙏 Remerciements

- Communauté open source Python
- Outils de visualisation (Plotly, D3.js)
- Bibliothèques ML (Scikit-learn, Prophet)

---

<div align="center">

**⭐ Si ce projet vous plaît, n'oubliez pas de le star !**

[![GitHub stars](https://img.shields.io/github/stars/votre-username/muscle-analytics?style=social)](https://github.com/votre-username/muscle-analytics)

</div>
