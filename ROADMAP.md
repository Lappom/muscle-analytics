# 🚀 Roadmap — Muscle-Analytics

> Plan de développement structuré et progressif pour l'application d'analyse de musculation

## 📋 Vue d'ensemble

Cette roadmap présente un plan de développement en 6 phases, conçu pour un développeur solo avec une disponibilité modérée. Chaque phase est autonome et produit des livrables fonctionnels.

**Durée totale estimée :** 6-12 semaines  
**Approche :** Développement itératif avec livrables fonctionnels à chaque phase

---

## 🎯 Phase 0 — Setup initial du repo & infrastructure (1-3 jours)

### Objectif

Mise en place d'un repository propre avec infrastructure de développement et conventions définies.

### Tâches détaillées

- [x] Créer repository GitHub avec README initial
- [x] Configurer `.gitignore`, `.editorconfig`, `.gitattributes` et `LICENSE`
- [ ] Créer branches : `main`, `dev`, `feature/*`
- [x] Ajouter `docker-compose.yml` minimal (DB + API skeleton)
- [ ] Configurer CI basique via GitHub Actions (lint + tests skeleton)
- [x] Définir conventions de code et structure du projet

### Critères d'acceptation

- [x] `docker compose up` démarre DB + API stub
- [x] CI pipeline passe (lint + tests stubs)
- [x] Structure de projet claire et documentée

### Livrable

- [x] Repository initial avec infrastructure de base fonctionnelle.

---

## 🔄 Phase 1 — Ingestion & ETL baseline (1-2 semaines)

### Objectif

Parser fiable pour CSV/XML → DB avec normalisation des données et tests.

### Tâches détaillées

- [x] Implémenter parser CSV robuste
  - Gestion des virgules et espaces insécables
  - Validation des données d'entrée
- [x] Implémenter parser XML (structure fournie)
- [x] Normalisation des données
  - Dates : DD/MM/YYYY → ISO 8601
  - Poids : virgules → points, suppression des unités
  - Répétitions : conversion en entiers
- [x] Heuristiques pour détecter séries d'échauffement vs principales
- [x] Mapping initial des exercices (table `exercises` simple)
- [ ] Scripts ETL pour insertion en DB et import incrémental
- [x] Tests unitaires pour parse + conversions

### Critères d'acceptation

- [x] Import d'un fichier CSV et XML d'exemple avec résultat correct dans DB
- [x] Tests unitaires couvrant les cas edge (valeurs nulles, formats différents)
- [x] Gestion des erreurs et logging approprié

### Livrable

- [x] Pipeline ETL fonctionnel avec tests et documentation.

---

## 📊 Phase 2 — EDA & features de base (1-2 semaines)

### Objectif

Explorer les données, créer des features clés et développer des dashboards prototypes.

### Tâches détaillées

- [ ] Notebooks EDA (Jupyter/Colab)
  - Distributions et outliers
  - Mapping muscles/exercices
  - Analyse temporelle des données
- [ ] Calculs de features avancées
  - Volume par set et par séance
  - 1RM estimé (formules Epley/Brzycki)
  - Rolling sums et windows
  - Indicateurs de progression
- [ ] Endpoints API de base pour exposer agrégations
- [ ] MVP frontend (Streamlit ou React minimal)
  - Volume hebdomadaire
  - Progression par exercice
  - Calendrier heatmap
  - Graphiques de tendance

### Critères d'acceptation

- [ ] Dashboards affichant KPIs et courbes par exercice
- [ ] Endpoints API retournant JSON testables
- [ ] Interface utilisateur intuitive et responsive

### Livrable

Notebooks EDA + MVP dashboard fonctionnel.

---

## 🤖 Phase 3 — Modèles ML simples (2-3 semaines)

### Objectif

Implémenter des modèles de forecasting et de régression basiques.

### Tâches détaillées

- [ ] Baseline forecasting
  - Modèle Prophet ou ARIMA pour volume hebdomadaire
  - Validation des prédictions
- [ ] Modèle de régression
  - Estimation de charge probable sur X répétitions
  - Split train/test approprié
  - Feature engineering
- [ ] Validation et évaluation
  - Backtesting sur données historiques
  - Métriques RMSE/MAE
  - Analyse des erreurs
- [ ] Sauvegarde et déploiement
  - Sauvegarde modèle (pickle/ONNX)
  - Endpoint de prédiction
  - Monitoring des performances

### Critères d'acceptation

- [ ] Modèle forecasting avec score documenté
- [ ] Endpoint de prédiction répondant correctement
- [ ] Documentation des performances et limitations

### Livrable

Modèles entraînés + endpoints associés + documentation.

---

## ⚠️ Phase 4 — Analyses avancées & alerting (1-2 semaines)

### Objectif

Ajouter détection de plateaux/anomalies et système d'alertes intelligent.

### Tâches détaillées

- [ ] Détection de plateaux
  - Règles métier + tests statistiques
  - Rolling windows pour analyse
  - Seuils configurables
- [ ] Anomaly detection
  - Isolation Forest ou approche rule-based
  - Détection des performances anormales
- [ ] Mécanisme d'alerte
  - Interface utilisateur pour alertes
  - Notifications (emails ou logs)
  - Historique des alertes
- [ ] Suggestions heuristiques
  - Recommandations d'augmentation de poids
  - Conseils d'adaptation d'entraînement

### Critères d'acceptation

- [ ] Alertes déclenchées sur cas synthétiques
- [ ] UI affiche alertes et recommandations
- [ ] Système de notification fonctionnel

### Livrable

Module alerting complet + UI intégrée.

---

## ✨ Phase 5 — UX/polish & déploiement (1-2 semaines)

### Objectif

Rendre le produit utilisable, stable et déployable en production.

### Tâches détaillées

- [ ] Amélioration UI/UX
  - Filtres avancés
  - Exports PDF/Excel
  - Responsive design
- [ ] Authentification simple (optionnel)
- [ ] Tests et qualité
  - Tests d'intégration
  - QA manuelle
  - Performance testing
- [ ] Déploiement
  - Dockerisation complète
  - Scripts de déploiement
  - Configuration production
- [ ] Documentation finale
  - README complet
  - Notebooks nettoyés
  - Vidéo démo

### Critères d'acceptation

- [ ] Déploiement réussi sur VM/container
- [ ] Documentation complète et claire
- [ ] Démo fonctionnelle

### Livrable

Version déployée et documentée en production.

---

## 🔮 Phase 6 — Extensions (optionnel)

### Fonctionnalités avancées

- [ ] Fine-tune d'un petit LLM pour conseils personnalisés (NLP)
- [ ] Optimisation de planification d'entraînements (solver)
- [ ] Intégration de capteurs (HR, GPS)
- [ ] Multi-utilisateur et partage sécurisé
- [ ] API publique pour intégrations tierces

---

## 📝 Checklist & bonnes pratiques

### Qualité du code

- [ ] Tests unitaires pour parsers et calculs
- [ ] Code coverage > 80%
- [ ] Linting et formatting automatique

### Gestion de projet

- [ ] Commits atomiques + PRs sur dev
- [ ] Documentation des choix techniques
- [ ] Backups réguliers de la DB

### Reproducibilité

- [ ] Notebooks reproductibles avec requirements.txt
- [ ] Environnements Dockerisés
- [ ] Seeds pour données de test

---

## 🎯 Métriques de succès

- **Phase 1-2 :** Pipeline ETL stable avec données de test
- **Phase 3 :** Modèles ML avec métriques de performance
- **Phase 4-5 :** Application utilisable en production
- **Phase 6 :** Fonctionnalités avancées validées

---

_Dernière mise à jour : $(date)_  
_Version : 2.0_
