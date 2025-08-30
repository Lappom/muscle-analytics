"""
Tests unitaires pour l'API Muscle-Analytics
"""

import pytest
import sys
import os
from datetime import date, timedelta
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configuration d'environnement de test
os.environ['APP_ENV'] = 'development'

from src.api.main import app
from src.api.models import Session, Set, Exercise
from src.api.services import DatabaseService, AnalyticsService


class TestAPIEndpoints:
    """Tests des endpoints de l'API"""
    
    @pytest.fixture
    def client(self):
        """Client de test FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_db_service(self):
        """Mock du service de base de données"""
        mock_service = Mock(spec=DatabaseService)
        
        # Mock des sessions
        mock_sessions = [
            Session(
                id=1,
                date=date.today(),
                start_time="10:00",
                training_name="Push A",
                notes="Bonne séance",
                created_at=date.today()
            ),
            Session(
                id=2,
                date=date.today() - timedelta(days=1),
                start_time="18:00",
                training_name="Pull A",
                notes="",
                created_at=date.today() - timedelta(days=1)
            )
        ]
        mock_service.get_sessions.return_value = mock_sessions
        
        # Mock des sets
        mock_sets = [
            Set(
                id=1,
                session_id=1,
                exercise="Développé couché",
                series_type="principale",
                reps=10,
                weight_kg=80.0,
                notes="",
                skipped=False,
                created_at=date.today()
            ),
            Set(
                id=2,
                session_id=1,
                exercise="Développé couché",
                series_type="principale",
                reps=8,
                weight_kg=85.0,
                notes="",
                skipped=False,
                created_at=date.today()
            )
        ]
        mock_service.get_sets.return_value = mock_sets
        
        # Mock des exercices
        mock_exercises = [
            Exercise(
                name="Développé couché",
                main_region="Pectoraux",
                muscles_primary=["Pectoraux", "Triceps"],
                muscles_secondary=["Deltoïdes antérieurs"],
                created_at=date.today()
            )
        ]
        mock_service.get_exercises.return_value = mock_exercises
        mock_service.get_unique_exercises_from_sets.return_value = ["Développé couché", "Tractions"]
        
        return mock_service
    
    def test_root_endpoint(self, client):
        """Test du endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """Test du endpoint de santé"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @patch('src.api.services.get_database_service')
    def test_get_sessions(self, mock_get_db_service, client, mock_db_service):
        """Test de récupération des sessions"""
        mock_get_db_service.return_value = mock_db_service
        
        response = client.get("/sessions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["training_name"] == "Push A"
    
    @patch('src.api.services.get_database_service')
    def test_get_sessions_with_date_filter(self, mock_get_db_service, client, mock_db_service):
        """Test de récupération des sessions avec filtre de date"""
        mock_get_db_service.return_value = mock_db_service
        
        today = date.today()
        response = client.get(f"/sessions?start_date={today}&end_date={today}")
        assert response.status_code == 200
        
        # Vérifier que le service a été appelé avec les bons paramètres
        mock_db_service.get_sessions.assert_called_with(start_date=today, end_date=today)
    
    @patch('src.api.services.get_database_service')
    def test_get_session_details(self, mock_get_db_service, client, mock_db_service):
        """Test de récupération des détails d'une session"""
        mock_get_db_service.return_value = mock_db_service
        
        response = client.get("/sessions/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert "sets" in data
    
    @patch('src.api.services.get_database_service')
    def test_get_session_not_found(self, mock_get_db_service, client, mock_db_service):
        """Test de récupération d'une session inexistante"""
        mock_get_db_service.return_value = mock_db_service
        
        response = client.get("/sessions/999")
        assert response.status_code == 404
    
    @patch('src.api.services.get_database_service')
    def test_get_sets(self, mock_get_db_service, client, mock_db_service):
        """Test de récupération des sets"""
        mock_get_db_service.return_value = mock_db_service
        
        response = client.get("/sets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["exercise"] == "Développé couché"
    
    @patch('src.api.services.get_database_service')
    def test_get_sets_with_filters(self, mock_get_db_service, client, mock_db_service):
        """Test de récupération des sets avec filtres"""
        mock_get_db_service.return_value = mock_db_service
        
        response = client.get("/sets?exercise=Développé couché&session_id=1")
        assert response.status_code == 200
        
        # Vérifier que le service a été appelé avec les bons paramètres
        mock_db_service.get_sets.assert_called_with(
            session_id=1,
            exercise="Développé couché",
            start_date=None,
            end_date=None
        )
    
    @patch('src.api.services.get_database_service')
    def test_get_exercises(self, mock_get_db_service, client, mock_db_service):
        """Test de récupération du catalogue d'exercices"""
        mock_get_db_service.return_value = mock_db_service
        
        response = client.get("/exercises")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Développé couché"
    
    @patch('src.api.services.get_database_service')
    def test_get_practiced_exercises(self, mock_get_db_service, client, mock_db_service):
        """Test de récupération des exercices pratiqués"""
        mock_get_db_service.return_value = mock_db_service
        
        response = client.get("/exercises/practiced")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert "Développé couché" in data
        assert "Tractions" in data


class TestAnalyticsEndpoints:
    """Tests des endpoints d'analytics"""
    
    @pytest.fixture
    def client(self):
        """Client de test FastAPI"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_analytics_service(self):
        """Mock du service d'analytics"""
        mock_service = Mock(spec=AnalyticsService)
        
        # Mock des analytics de volume
        from src.api.models import VolumeStats, OneRMStats, ProgressionStats, DashboardData
        
        mock_volume_stats = [
            VolumeStats(
                exercise="Développé couché",
                total_volume=1650.0,
                avg_volume_per_set=82.5,
                avg_volume_per_session=330.0,
                weekly_volume=660.0,
                monthly_volume=1650.0
            )
        ]
        mock_service.get_volume_analytics.return_value = mock_volume_stats
        
        # Mock des analytics de 1RM
        mock_one_rm_stats = [
            OneRMStats(
                exercise="Développé couché",
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
        ]
        mock_service.get_one_rm_analytics.return_value = mock_one_rm_stats
        
        # Mock des analytics de progression
        mock_progression_stats = [
            ProgressionStats(
                exercise="Développé couché",
                total_sessions=5,
                progression_trend="Stable",
                volume_trend_7d=2.5,
                volume_trend_30d=8.0,
                plateau_detected=False,
                days_since_last_pr=7
            )
        ]
        mock_service.get_progression_analytics.return_value = mock_progression_stats
        
        # Mock du dashboard
        mock_dashboard = DashboardData(
            total_sessions=10,
            total_exercises=5,
            total_volume_this_week=1200.0,
            total_volume_this_month=3500.0,
            recent_sessions=[],
            top_exercises_by_volume=mock_volume_stats,
            exercises_with_plateau=[]
        )
        mock_service.get_dashboard_data.return_value = mock_dashboard
        
        return mock_service
    
    @patch('src.api.services.get_analytics_service')
    def test_get_volume_analytics(self, mock_get_analytics_service, client, mock_analytics_service):
        """Test des analytics de volume"""
        mock_get_analytics_service.return_value = mock_analytics_service
        
        response = client.get("/analytics/volume")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["exercise"] == "Développé couché"
        assert data[0]["total_volume"] == 1650.0
    
    @patch('src.api.services.get_analytics_service')
    def test_get_one_rm_analytics(self, mock_get_analytics_service, client, mock_analytics_service):
        """Test des analytics de 1RM"""
        mock_get_analytics_service.return_value = mock_analytics_service
        
        response = client.get("/analytics/one-rm")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["exercise"] == "Développé couché"
        assert data[0]["best_1rm_average"] == 108.5
    
    @patch('src.api.services.get_analytics_service')
    def test_get_progression_analytics(self, mock_get_analytics_service, client, mock_analytics_service):
        """Test des analytics de progression"""
        mock_get_analytics_service.return_value = mock_analytics_service
        
        response = client.get("/analytics/progression")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["exercise"] == "Développé couché"
        assert data[0]["plateau_detected"] == False
    
    @patch('src.api.services.get_analytics_service')
    def test_get_exercise_analytics(self, mock_get_analytics_service, client, mock_analytics_service):
        """Test des analytics pour un exercice spécifique"""
        mock_get_analytics_service.return_value = mock_analytics_service
        
        response = client.get("/analytics/exercise/Développé couché")
        assert response.status_code == 200
        data = response.json()
        assert data["exercise"] == "Développé couché"
        assert "volume_stats" in data
        assert "one_rm_stats" in data
        assert "progression_stats" in data
    
    @patch('src.api.services.get_analytics_service')
    def test_get_dashboard_analytics(self, mock_get_analytics_service, client, mock_analytics_service):
        """Test du dashboard"""
        mock_get_analytics_service.return_value = mock_analytics_service
        
        response = client.get("/analytics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["total_sessions"] == 10
        assert data["total_exercises"] == 5
        assert data["total_volume_this_week"] == 1200.0
    
    @patch('src.api.services.get_analytics_service')
    def test_analytics_with_date_filters(self, mock_get_analytics_service, client, mock_analytics_service):
        """Test des analytics avec filtres de date"""
        mock_get_analytics_service.return_value = mock_analytics_service
        
        today = date.today()
        last_week = today - timedelta(days=7)
        
        response = client.get(f"/analytics/volume?start_date={last_week}&end_date={today}")
        assert response.status_code == 200
        
        # Vérifier que le service a été appelé avec les bons paramètres
        mock_analytics_service.get_volume_analytics.assert_called_with(
            exercise=None,
            start_date=last_week,
            end_date=today
        )


class TestStatusEndpoint:
    """Tests du endpoint de statut"""
    
    @pytest.fixture
    def client(self):
        """Client de test FastAPI"""
        return TestClient(app)
    
    @patch('src.api.services.get_database_service')
    def test_get_status_healthy(self, mock_get_db_service, client):
        """Test du statut avec base de données connectée"""
        mock_db_service = Mock()
        mock_db_service.db.test_connection.return_value = True
        mock_db_service.get_sessions.return_value = [Mock(date=date.today())]
        mock_db_service.get_unique_exercises_from_sets.return_value = ["Exercise1", "Exercise2"]
        mock_get_db_service.return_value = mock_db_service
        
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["api_status"] == "healthy"
        assert data["database_connected"] == True
        assert data["total_sessions"] == 1
        assert data["total_exercises"] == 2
    
    @patch('src.api.services.get_database_service')
    def test_get_status_degraded(self, mock_get_db_service, client):
        """Test du statut avec erreur de base de données"""
        mock_db_service = Mock()
        mock_db_service.db.test_connection.side_effect = Exception("DB Error")
        mock_get_db_service.return_value = mock_db_service
        
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["api_status"] == "degraded"
        assert data["database_connected"] == False
        assert "error" in data


if __name__ == "__main__":
    # Pour exécuter les tests directement
    pytest.main([__file__, "-v"])
