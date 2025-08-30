# 🚀 API Muscle-Analytics

API REST complète pour l'analyse d'entraînements de musculation, développée avec FastAPI.

## 📖 Vue d'ensemble

Cette API expose toutes les fonctionnalités d'analyse développées dans la Phase 2 :
- **Données de base** : Sessions, sets, exercices
- **Analytics de volume** : Calculs de volume par exercice, session, période
- **Analytics de 1RM** : Estimations de force maximale avec 4 formules
- **Analytics de progression** : Tendances, détection de plateaux
- **Dashboard** : Vue d'ensemble avec métriques clés

## 🏗️ Architecture

```
src/api/
├── main.py         # Application FastAPI principale + endpoints
├── models.py       # Modèles Pydantic pour requêtes/réponses
└── services.py     # Services pour base de données et analytics
```

## 🚀 Démarrage rapide

### 1. Prérequis
- Base de données PostgreSQL en cours d'exécution
- Python avec les dépendances installées

### 2. Démarrage de l'API
```bash
# Méthode recommandée
python run_api.py --port 8000 --host localhost

# Ou directement avec uvicorn
python -m uvicorn src.api.main:app --host localhost --port 8000 --reload
```

### 3. Accès à la documentation
- **API Documentation** : http://localhost:8000/docs
- **Alternative Redoc** : http://localhost:8000/redoc
- **OpenAPI Schema** : http://localhost:8000/openapi.json

## 📊 Endpoints disponibles

### 🏠 Endpoints de base
| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Informations générales et endpoints disponibles |
| `/health` | GET | Vérification de santé de l'API |
| `/status` | GET | Statut détaillé (API + base de données) |

### 📝 Données d'entraînement
| Endpoint | Méthode | Description | Paramètres |
|----------|---------|-------------|------------|
| `/sessions` | GET | Liste des sessions | `start_date`, `end_date` |
| `/sessions/{id}` | GET | Détails d'une session avec sets | - |
| `/sets` | GET | Liste des sets | `session_id`, `exercise`, `start_date`, `end_date` |
| `/exercises` | GET | Catalogue des exercices | - |
| `/exercises/practiced` | GET | Liste des exercices pratiqués | - |

### 📈 Analytics
| Endpoint | Méthode | Description | Paramètres |
|----------|---------|-------------|------------|
| `/analytics/volume` | GET | Analytics de volume | `exercise`, `start_date`, `end_date` |
| `/analytics/one-rm` | GET | Analytics de 1RM | `exercise`, `start_date`, `end_date` |
| `/analytics/progression` | GET | Analytics de progression | `exercise`, `start_date`, `end_date` |
| `/analytics/exercise/{name}` | GET | Analytics complètes pour un exercice | `start_date`, `end_date` |
| `/analytics/dashboard` | GET | Données du dashboard principal | - |

## 🔧 Exemples d'utilisation

### Récupérer toutes les sessions
```bash
curl http://localhost:8000/sessions
```

### Sessions de la dernière semaine
```bash
curl "http://localhost:8000/sessions?start_date=2025-08-23&end_date=2025-08-30"
```

### Analytics de volume pour un exercice
```bash
curl "http://localhost:8000/analytics/volume?exercise=Développé couché"
```

### Dashboard complet
```bash
curl http://localhost:8000/analytics/dashboard
```

## 📋 Format des réponses

### Session
```json
{
  "id": 1,
  "date": "2025-08-30",
  "start_time": "10:00",
  "training_name": "Push A",
  "notes": "Bonne séance",
  "created_at": "2025-08-30T10:00:00"
}
```

### Set
```json
{
  "id": 1,
  "session_id": 1,
  "exercise": "Développé couché",
  "series_type": "principale",
  "reps": 10,
  "weight_kg": 80.0,
  "notes": "",
  "skipped": false,
  "created_at": "2025-08-30T10:05:00"
}
```

### Analytics de Volume
```json
{
  "exercise": "Développé couché",
  "total_volume": 1650.0,
  "avg_volume_per_set": 82.5,
  "avg_volume_per_session": 330.0,
  "weekly_volume": 660.0,
  "monthly_volume": 1650.0
}
```

### Analytics de 1RM
```json
{
  "exercise": "Développé couché",
  "best_1rm_epley": 110.0,
  "best_1rm_brzycki": 108.0,
  "best_1rm_lander": 107.0,
  "best_1rm_oconner": 109.0,
  "best_1rm_average": 108.5,
  "current_1rm_epley": 105.0,
  "current_1rm_brzycki": 103.0,
  "current_1rm_lander": 102.0,
  "current_1rm_oconner": 104.0,
  "current_1rm_average": 103.5
}
```

### Analytics de Progression
```json
{
  "exercise": "Développé couché",
  "total_sessions": 15,
  "progression_trend": "Progression",
  "volume_trend_7d": 5.2,
  "volume_trend_30d": 12.8,
  "plateau_detected": false,
  "days_since_last_pr": 7
}
```

## 🧪 Tests

### Tests automatisés
```bash
# Tests unitaires de l'API
python -m pytest tests/test_api_endpoints.py -v

# Test complet avec l'API en cours d'exécution
python examples/test_api_endpoints.py
```

### Tests manuels avec l'API en cours
```bash
# Test de santé
python examples/test_api_endpoints.py http://localhost:8000

# Démonstration complète
python examples/demo_api_complete.py http://localhost:8000
```

## ⚙️ Configuration

### Variables d'environnement
```bash
# Environnement
APP_ENV=development  # development, test, production, docker

# Base de données de développement
DEV_DB_HOST=localhost
DEV_DB_PORT=5432
DEV_DB_NAME=muscle_analytics
DEV_DB_USER=dev
DEV_DB_PASSWORD=devpass
```

### Fichier .env
Le fichier `.env` est automatiquement chargé au démarrage pour configurer la base de données.

## 🔧 Développement

### Structure des services

#### DatabaseService
- Gestion des connexions à la base de données
- Requêtes pour sessions, sets, exercices
- Gestion des filtres (dates, exercices)

#### AnalyticsService
- Calculs de features avec `FeatureCalculator`
- Conversion des données en modèles Pydantic
- Agrégation et formatage des résultats

### Ajout d'un nouvel endpoint

1. **Modèle Pydantic** dans `models.py`
```python
class NewModel(BaseModel):
    field1: str
    field2: int
```

2. **Logique métier** dans `services.py`
```python
def get_new_data(self) -> List[NewModel]:
    # Logique de calcul
    return results
```

3. **Endpoint** dans `main.py`
```python
@app.get("/new-endpoint", response_model=List[NewModel])
async def get_new_endpoint(service: AnalyticsService = Depends(get_analytics_service)):
    return service.get_new_data()
```

## 🐛 Dépannage

### Problèmes courants

#### Erreur de connexion à la base
```
DatabaseError: connection to server failed
```
- Vérifier que PostgreSQL est démarré : `docker-compose ps`
- Vérifier la configuration dans `.env`
- Tester la connexion : `python -c "from src.database import get_database; get_database().test_connection()"`

#### Module non trouvé
```
ModuleNotFoundError: No module named 'src'
```
- Exécuter depuis la racine du projet
- Vérifier que `PYTHONPATH` inclut le répertoire `src`

#### Dépendances manquantes
```
ModuleNotFoundError: No module named 'scipy'
```
- Installer les dépendances : `pip install -r requirements.txt`
- Ou spécifiquement : `pip install scipy fastapi uvicorn`

### Logs et debugging

#### Logs de l'API
L'API utilise le système de logging standard de Python. Pour plus de détails :
```bash
python -m uvicorn src.api.main:app --log-level debug
```

#### Validation des données
FastAPI valide automatiquement les données avec Pydantic. Les erreurs de validation sont retournées avec des détails précis.

## 🚀 Prochaines étapes

### Phase 3 - Améliorations prévues
- [ ] Authentification et autorisation
- [ ] Endpoints pour créer/modifier des données
- [ ] Cache Redis pour les analytics coûteux
- [ ] Rate limiting et monitoring
- [ ] Versioning de l'API (v2)

### Performance
- [ ] Optimisation des requêtes SQL
- [ ] Pagination pour les grandes listes
- [ ] Compression des réponses
- [ ] Background tasks pour calculs longs

## 📚 Ressources

- **FastAPI Documentation** : https://fastapi.tiangolo.com/
- **Pydantic Models** : https://pydantic.dev/
- **OpenAPI Specification** : https://swagger.io/specification/

---

✅ **Statut Phase 2 - Tâche 3** : **TERMINÉE**
- [x] Endpoints API complets pour toutes les données
- [x] Analytics intégrées (volume, 1RM, progression)
- [x] Documentation interactive automatique
- [x] Tests unitaires et scripts de validation
- [x] Configuration multi-environnements
