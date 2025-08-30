"""
Tests unitaires pour l'API Muscle-Analytics

Ce module teste tous les endpoints de l'API en utilisant des mocks et fixtures.
Les données de test sont créées via des factories dans conftest.py.
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
os.environ['APP_ENV'] = 'test'

from src.api.main import app


class TestAPIEndpoints:
    """Tests des endpoints de base de l'API"""
    
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
    
    def test_get_sessions(self, mock_db_service):
        """Test de récupération des sessions"""
        from src.api.services import get_database_service
        
        # Override de la dépendance
        app.dependency_overrides[get_database_service] = lambda: mock_db_service
        
        try:
            client = TestClient(app)
            response = client.get("/sessions")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["training_name"] == "Push A"
        finally:
            # Nettoyer l'override
            app.dependency_overrides.clear()
    
    def test_get_sessions_with_date_filter(self, mock_db_service):
        """Test de récupération des sessions avec filtre de date"""
        from src.api.services import get_database_service
        
        app.dependency_overrides[get_database_service] = lambda: mock_db_service
        
        try:
            client = TestClient(app)
            today = date.today()
            response = client.get(f"/sessions?start_date={today}&end_date={today}")
            assert response.status_code == 200
            
            # Vérifier que le service a été appelé avec les bons paramètres
            mock_db_service.get_sessions.assert_called_with(start_date=today, end_date=today)
        finally:
            app.dependency_overrides.clear()
    
    def test_get_session_details(self, mock_db_service):
        """Test de récupération des détails d'une session"""
        from src.api.services import get_database_service
        
        app.dependency_overrides[get_database_service] = lambda: mock_db_service
        
        try:
            client = TestClient(app)
            response = client.get("/sessions/1")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert "sets" in data
        finally:
            app.dependency_overrides.clear()
    
    def test_get_session_not_found(self, mock_db_service, sample_sessions):
        """Test de récupération d'une session inexistante"""
        from src.api.services import get_database_service
        
        # Mock pour retourner les sessions existantes, mais pas la session 999
        mock_db_service.get_sessions.return_value = sample_sessions
        
        app.dependency_overrides[get_database_service] = lambda: mock_db_service
        
        try:
            client = TestClient(app)
            response = client.get("/sessions/999")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()
    
    def test_get_sets(self, mock_db_service):
        """Test de récupération des sets"""
        from src.api.services import get_database_service
        
        app.dependency_overrides[get_database_service] = lambda: mock_db_service
        
        try:
            client = TestClient(app)
            response = client.get("/sets")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["exercise"] == "Développé couché"
        finally:
            app.dependency_overrides.clear()
    
    def test_get_sets_with_filters(self, mock_db_service):
        """Test de récupération des sets avec filtres"""
        from src.api.services import get_database_service
        
        app.dependency_overrides[get_database_service] = lambda: mock_db_service
        
        try:
            client = TestClient(app)
            response = client.get("/sets?exercise=Développé couché&session_id=1")
            assert response.status_code == 200
            
            # Vérifier que le service a été appelé avec les bons paramètres
            mock_db_service.get_sets.assert_called_with(
                session_id=1,
                exercise="Développé couché",
                start_date=None,
                end_date=None
            )
        finally:
            app.dependency_overrides.clear()
    
    def test_get_exercises(self, mock_db_service):
        """Test de récupération du catalogue d'exercices"""
        from src.api.services import get_database_service
        
        app.dependency_overrides[get_database_service] = lambda: mock_db_service
        
        try:
            client = TestClient(app)
            response = client.get("/exercises")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["name"] == "Développé couché"
        finally:
            app.dependency_overrides.clear()
    
    def test_get_practiced_exercises(self, mock_db_service):
        """Test de récupération des exercices pratiqués"""
        from src.api.services import get_database_service
        
        app.dependency_overrides[get_database_service] = lambda: mock_db_service
        
        try:
            client = TestClient(app)
            response = client.get("/exercises/practiced")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert "Développé couché" in data
            assert "Tractions" in data
        finally:
            app.dependency_overrides.clear()


class TestAnalyticsEndpoints:
    """Tests des endpoints d'analytics"""
    
    def test_get_volume_analytics(self, client, mock_analytics_service):
        """Test des analytics de volume"""
        from src.api.main import app
        from src.api.services import get_analytics_service
        
        # Override les dépendances FastAPI
        app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
        
        try:
            response = client.get("/analytics/volume")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["exercise"] == "Développé couché"
            assert data[0]["total_volume"] == 1650.0
        finally:
            # Nettoyer les overrides
            app.dependency_overrides.clear()
    
    def test_get_one_rm_analytics(self, client, mock_analytics_service):
        """Test des analytics de 1RM"""
        from src.api.main import app
        from src.api.services import get_analytics_service
        
        # Override les dépendances FastAPI
        app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
        
        try:
            response = client.get("/analytics/one-rm")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["exercise"] == "Développé couché"
            assert data[0]["best_1rm_average"] == 108.5
        finally:
            # Nettoyer les overrides
            app.dependency_overrides.clear()
    
    def test_get_progression_analytics(self, client, mock_analytics_service):
        """Test des analytics de progression"""
        from src.api.main import app
        from src.api.services import get_analytics_service
        
        # Override les dépendances FastAPI
        app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
        
        try:
            response = client.get("/analytics/progression")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["exercise"] == "Développé couché"
            assert data[0]["plateau_detected"] == False
        finally:
            # Nettoyer les overrides
            app.dependency_overrides.clear()
    
    def test_get_exercise_analytics(self, client, mock_analytics_service, mock_db_service):
        """Test des analytics pour un exercice spécifique"""
        from src.api.main import app
        from src.api.services import get_analytics_service, get_database_service
        
        # Override les dépendances FastAPI
        app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
        app.dependency_overrides[get_database_service] = lambda: mock_db_service
        
        try:
            response = client.get("/analytics/exercise/Développé couché")
            assert response.status_code == 200
            data = response.json()
            assert data["exercise"] == "Développé couché"
            assert "volume_stats" in data
            assert "one_rm_stats" in data
            assert "progression_stats" in data
            
            # Vérifier que les méthodes individuelles ont été appelées
            mock_analytics_service.get_volume_analytics.assert_called_with(
                exercise="Développé couché", start_date=None, end_date=None
            )
            mock_analytics_service.get_one_rm_analytics.assert_called_with(
                exercise="Développé couché", start_date=None, end_date=None
            )
            mock_analytics_service.get_progression_analytics.assert_called_with(
                exercise="Développé couché", start_date=None, end_date=None
            )
        finally:
            # Nettoyer les overrides
            app.dependency_overrides.clear()
    
    def test_get_dashboard_analytics(self, client, mock_analytics_service):
        """Test du dashboard"""
        from src.api.main import app
        from src.api.services import get_analytics_service
        
        # Override les dépendances FastAPI
        app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
        
        try:
            response = client.get("/analytics/dashboard")
            assert response.status_code == 200
            data = response.json()
            assert data["total_sessions"] == 10
            assert data["total_exercises"] == 5
            assert data["total_volume_this_week"] == 1200.0
        finally:
            # Nettoyer les overrides
            app.dependency_overrides.clear()
    
    def test_analytics_with_date_filters(self, client, mock_analytics_service):
        """Test des analytics avec filtres de date"""
        from src.api.main import app
        from src.api.services import get_analytics_service
        
        # Override les dépendances FastAPI
        app.dependency_overrides[get_analytics_service] = lambda: mock_analytics_service
        
        try:
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
        finally:
            # Nettoyer les overrides
            app.dependency_overrides.clear()


class TestStatusEndpoint:
    """Tests du endpoint de statut"""
    
    def test_get_status_healthy(self):
        """Test du statut avec base de données connectée"""
        from src.api.services import get_database_service
        
        mock_db_service = Mock()
        mock_db_service.db.test_connection.return_value = True
        mock_db_service.get_sessions.return_value = [Mock(date=date.today())]
        mock_db_service.get_unique_exercises_from_sets.return_value = ["Exercise1", "Exercise2"]
        
        app.dependency_overrides[get_database_service] = lambda: mock_db_service
        
        try:
            client = TestClient(app)
            response = client.get("/status")
            assert response.status_code == 200
            data = response.json()
            assert data["api_status"] == "healthy"
            assert data["database_connected"] == True
            assert data["total_sessions"] == 1
            assert data["total_exercises"] == 2
        finally:
            app.dependency_overrides.clear()
    
    def test_get_status_degraded(self):
        """Test du statut avec erreur de base de données"""
        from src.api.services import get_database_service
        
        mock_db_service = Mock()
        mock_db_service.db.test_connection.side_effect = Exception("DB Error")
        
        app.dependency_overrides[get_database_service] = lambda: mock_db_service
        
        try:
            client = TestClient(app)
            response = client.get("/status")
            assert response.status_code == 200
            data = response.json()
            assert data["api_status"] == "degraded"
            assert data["database_connected"] == False
            assert "error" in data
        finally:
            app.dependency_overrides.clear()


if __name__ == "__main__":
    # Pour exécuter les tests directement
    pytest.main([__file__, "-v"])
