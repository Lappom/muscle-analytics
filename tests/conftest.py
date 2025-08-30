"""
Configuration et fixtures globales pour les tests de l'API Muscle-Analytics
"""

import pytest
import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from unittest.mock import Mock

# Configuration d'environnement de test sécurisée
from .test_env_config import ensure_test_environment, get_safe_test_config

from src.api.main import app
from src.api.models import Session, Set, Exercise, VolumeStats, OneRMStats, ProgressionStats, DashboardData
from src.api.services import DatabaseService, AnalyticsService


# =============================================================================
# FACTORY POUR LES DONNÉES DE TEST
# =============================================================================

class TestDataFactory:
    """Factory pour créer des données de test cohérentes"""
    
    @staticmethod
    def create_session(id=1, session_date=None, training_name="Push A", notes="Bonne séance"):
        """Crée une session de test"""
        session_date = session_date or date.today()
        return Session(
            id=id,
            date=session_date,
            start_time="10:00",
            training_name=training_name,
            notes=notes,
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_set(id=1, session_id=1, exercise="Développé couché", reps=10, weight_kg=80.0):
        """Crée un set de test"""
        return Set(
            id=id,
            session_id=session_id,
            exercise=exercise,
            series_type="principale",
            reps=reps,
            weight_kg=Decimal(str(weight_kg)),
            notes="",
            skipped=False,
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_exercise(name="Développé couché", main_region="Pectoraux"):
        """Crée un exercice de test"""
        return Exercise(
            name=name,
            main_region=main_region,
            muscles_primary=["Pectoraux", "Triceps"],
            muscles_secondary=["Deltoïdes antérieurs"],
            created_at=datetime.now()
        )
    
    @staticmethod
    def create_volume_stats(exercise="Développé couché", total_volume=1650.0):
        """Crée des statistiques de volume de test"""
        return VolumeStats(
            exercise=exercise,
            total_volume=total_volume,
            avg_volume_per_set=82.5,
            avg_volume_per_session=330.0,
            weekly_volume=660.0,
            monthly_volume=total_volume
        )
    
    @staticmethod
    def create_one_rm_stats(exercise="Développé couché"):
        """Crée des statistiques de 1RM de test"""
        return OneRMStats(
            exercise=exercise,
            best_1rm_epley=110.0,
            best_1rm_brzycki=108.0,
            best_1rm_lander=107.0,
            best_1rm_oconner=109.0,
            best_1rm_average=108.5,
            current_1rm_epley=105.0,
            current_1rm_brzycki=103.0,
            current_1rm_lander=102.0,
            current_1rm_oconner=104.0,
            current_1rm_average=103.5
        )
    
    @staticmethod
    def create_progression_stats(exercise="Développé couché"):
        """Crée des statistiques de progression de test"""
        return ProgressionStats(
            exercise=exercise,
            total_sessions=5,
            progression_trend="Stable",
            volume_trend_7d=2.5,
            volume_trend_30d=8.0,
            plateau_detected=False,
            days_since_last_pr=7
        )


# =============================================================================
# FIXTURES GLOBALES
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """
    Configure l'environnement de test une seule fois par session de test.
    Cette fixture s'exécute automatiquement avant tous les tests.
    """
    ensure_test_environment()


@pytest.fixture
def safe_test_config():
    """
    Fixture pour obtenir une configuration de test sécurisée.
    Utilisez cette fixture dans vos tests qui ont besoin de la config DB.
    """
    return get_safe_test_config()


@pytest.fixture
def client():
    """Client de test FastAPI basique - pas utilisé dans les tests avec override"""
    # Note: ce client ne doit pas être utilisé directement dans les tests API
    # car il ne configure pas les overrides de dépendances
    return TestClient(app)


@pytest.fixture
def app_with_overrides():
    """
    Fixture pour l'application FastAPI avec support des overrides.
    Nettoie automatiquement les overrides après chaque test.
    """
    yield app
    # Nettoyage automatique des overrides après chaque test
    app.dependency_overrides.clear()


@pytest.fixture
def data_factory():
    """Factory pour créer des données de test"""
    return TestDataFactory


@pytest.fixture
def sample_sessions(data_factory):
    """Sessions de test standard"""
    return [
        data_factory.create_session(
            id=1, 
            session_date=date.today(),
            training_name="Push A",
            notes="Bonne séance"
        ),
        data_factory.create_session(
            id=2,
            session_date=date.today() - timedelta(days=1),
            training_name="Pull A",
            notes=""
        )
    ]


@pytest.fixture
def sample_sets(data_factory):
    """Sets de test standard"""
    return [
        data_factory.create_set(id=1, session_id=1, reps=10, weight_kg=80.0),
        data_factory.create_set(id=2, session_id=1, reps=8, weight_kg=85.0)
    ]


@pytest.fixture
def sample_exercises(data_factory):
    """Exercices de test standard"""
    return [
        data_factory.create_exercise("Développé couché", "Pectoraux")
    ]


@pytest.fixture
def sample_volume_stats(data_factory):
    """Statistiques de volume de test"""
    return [data_factory.create_volume_stats()]


@pytest.fixture
def sample_one_rm_stats(data_factory):
    """Statistiques de 1RM de test"""
    return [data_factory.create_one_rm_stats()]


@pytest.fixture
def sample_progression_stats(data_factory):
    """Statistiques de progression de test"""
    return [data_factory.create_progression_stats()]


@pytest.fixture
def mock_db_service(sample_sessions, sample_sets, sample_exercises):
    """Mock du service de base de données configuré avec des données de test"""
    mock_service = Mock(spec=DatabaseService)
    
    mock_service.get_sessions.return_value = sample_sessions
    mock_service.get_sets.return_value = sample_sets
    mock_service.get_exercises.return_value = sample_exercises
    mock_service.get_unique_exercises_from_sets.return_value = ["Développé couché", "Tractions"]
    
    # Ajout du mock pour get_session_by_id
    def mock_get_session_by_id(session_id):
        for session in sample_sessions:
            if session.id == session_id:
                return session
        return None
    
    mock_service.get_session_by_id.side_effect = mock_get_session_by_id
    
    return mock_service


@pytest.fixture
def mock_analytics_service(sample_volume_stats, sample_one_rm_stats, sample_progression_stats):
    """Mock du service d'analytics configuré avec des données de test"""
    # Ne pas utiliser spec=AnalyticsService pour permettre l'ajout d'attributs dynamiques
    mock_service = Mock()
    
    mock_service.get_volume_analytics.return_value = sample_volume_stats
    mock_service.get_one_rm_analytics.return_value = sample_one_rm_stats
    mock_service.get_progression_analytics.return_value = sample_progression_stats
    
    # Mock du dashboard
    mock_dashboard = DashboardData(
        total_sessions=10,
        total_exercises=5,
        total_volume_this_week=1200.0,
        total_volume_this_month=3500.0,
        recent_sessions=[],
        top_exercises_by_volume=sample_volume_stats,
        exercises_with_plateau=[]
    )
    mock_service.get_dashboard_data.return_value = mock_dashboard
    
    return mock_service
