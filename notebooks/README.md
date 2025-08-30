# 📊 Notebooks d'Analyse Exploratoire (EDA)

Ce dossier contient les notebooks Jupyter pour l'analyse exploratoire des données d'entraînement de musculation, conformément à la **Phase 2** du roadmap.

## 📋 Structure des notebooks

### 1. **01_EDA_general.ipynb** - Vue d'ensemble
- **Objectif** : Analyse exploratoire générale des données
- **Contenu** :
  - Chargement et nettoyage des données CSV/PostgreSQL
  - Statistiques descriptives globales
  - Analyse des distributions (poids, répétitions, volume)
  - Détection d'outliers avec méthode IQR
  - Visualisations des métriques principales
  - Analyse par type de série (échauffement vs principales)

### 2. **02_EDA_muscles_exercices.ipynb** - Mapping musculaire
- **Objectif** : Analyse des exercices et groupes musculaires
- **Contenu** :
  - Mapping exercices ↔ muscles (primaires/secondaires)
  - Répartition par région musculaire (Pectoraux, Dos, Jambes)
  - Analyse de l'équilibre musculaire
  - Détection des déséquilibres (muscles sous/sur-développés)
  - Fréquence d'entraînement par groupe musculaire
  - Recommandations d'optimisation

### 3. **03_EDA_temporel.ipynb** - Analyse temporelle
- **Objectif** : Patterns temporels et progression
- **Contenu** :
  - Évolution du volume d'entraînement dans le temps
  - Progression par exercice (régression linéaire)
  - Patterns hebdomadaires (jour optimal d'entraînement)
  - Analyse de la régularité (intervalles entre sessions)
  - Features temporelles pour ML (rolling windows, momentum)
  - Matrice de corrélation des nouvelles features

### 4. **04_features_engineering.ipynb** - Engineering avancé
- **Objectif** : Création de features ML-ready
- **Contenu** :
  - **Calcul 1RM** : Formules Epley, Brzycki, Lombardi
  - **Features progression** : Max personnels, pourcentages, tendances
  - **Features performance** : Intensité relative, fatigue index, efficacité
  - **Features temporelles** : Cycliques, cumuls, momentum
  - **Analyse d'importance** : Information mutuelle pour prédiction
  - **Dataset enrichi** : Prêt pour modélisation ML

## 🚀 Utilisation

### Prérequis
```bash
# Installation des dépendances
pip install jupyter matplotlib seaborn plotly scikit-learn numpy pandas

# Lancement de Jupyter
jupyter notebook
```

### Ordre d'exécution recommandé
1. **01_EDA_general.ipynb** - Base obligatoire
2. **02_EDA_muscles_exercices.ipynb** - Analyse spécialisée
3. **03_EDA_temporel.ipynb** - Progression temporelle
4. **04_features_engineering.ipynb** - Préparation ML

### Sources de données
- **CSV** : `../examples/sample_data.csv` (toujours disponible)
- **PostgreSQL** : `localhost:5432/muscle_analytics` (si Docker lancé)
- **Génération** : Chaque notebook enrichit le dataset pour le suivant

## 📊 Outputs et résultats

### Métriques générées
- **Volume total** : 2040kg (exemple avec données de démo)
- **Exercices analysés** : 3 exercices principaux
- **Période couverte** : 3 jours d'entraînement
- **Features créées** : 40+ nouvelles variables

### Insights clés identifiés
- **Équilibre musculaire** : Analyse comparative par région
- **Progression** : Tendances par exercice avec significativité
- **Régularité** : Classification automatique de la constance
- **Performance** : Zones d'intensité et patterns optimaux

### Visualisations produites
- Histogrammes de distribution avec outliers
- Graphiques temporels avec tendances
- Heatmaps de corrélation
- Pie charts de répartition musculaire
- Barplots de progression par exercice

## 🎯 Transition vers Phase 3 (ML)

Les notebooks génèrent un **dataset enrichi** contenant :
- **Features temporelles** : Rolling windows, momentum, cycliques
- **Features de progression** : 1RM, max personnels, pourcentages
- **Features de performance** : Intensité, fatigue, efficacité
- **Target variables** : Progression binaire, classe d'intensité

Compatible pour :
- **Modèles de régression** : Prédiction de charge optimale
- **Modèles de classification** : Détection de plateaux
- **Séries temporelles** : Forecasting avec Prophet/ARIMA
- **Clustering** : Profils d'entraînement

## ⚠️ Notes importantes

### Gestion des données manquantes
- **Tractions (0kg)** : Gérées comme poids de corps
- **Sets sautés** : Flaggés et exclus des calculs de progression
- **Répétitions manquantes** : Imputées ou exclues selon le contexte

### Limitations actuelles
- **Échantillon restreint** : 3 jours de données de démo
- **1RM estimé** : Formules théoriques (non testées)
- **Poids corporel** : Simulé à 80kg
- **Durée des sets** : Estimée aléatoirement

### Extensions futures
- **Données réelles** : Intégration de vrais historiques d'entraînement
- **Capteurs** : Heart rate, GPS, accéléromètres
- **Nutritions** : Corrélation avec apports caloriques
- **Récupération** : Qualité de sommeil, stress

---

## 🔗 Liens utiles

- **Roadmap principal** : `../ROADMAP.md`
- **Documentation API** : `../src/api/`
- **Tests unitaires** : `../tests/`
- **Données d'exemple** : `../examples/`

**Status Phase 2** : ✅ **TERMINÉE** - Notebooks EDA complets et fonctionnels
