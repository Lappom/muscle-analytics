"""
Tests corrigés pour les services refactorisés avec gestion des DataFrames vides.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api.services import DatabaseService, AnalyticsService
from src.features.volume import VolumeCalculator
from src.features.one_rm import OneRMCalculator
from src.features.progression import ProgressionAnalyzer


class TestDatabaseServiceRefactoring:
    """Tests pour le service de base de données refactorisé."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        # Mock de la base de données
        self.mock_db = Mock()
        self.db_service = DatabaseService(self.mock_db)
        
        # Données de test CORRIGÉES
        self.sample_sessions = [
            Mock(id=1, date=date(2023, 1, 1), training_name="Push A", notes="Bonne séance"),
            Mock(id=2, date=date(2023, 1, 8), training_name="Pull A", notes=""),
            Mock(id=3, date=date(2023, 1, 15), training_name="Legs A", notes="Séance difficile")
        ]
        
        self.sample_sets = [
            Mock(id=1, session_id=1, exercise="Bench Press", reps=10, weight_kg=100.0, skipped=False),
            Mock(id=2, session_id=1, exercise="Bench Press", reps=8, weight_kg=110.0, skipped=False),
            Mock(id=3, session_id=2, exercise="Squat", reps=12, weight_kg=120.0, skipped=False),
            Mock(id=4, session_id=3, exercise="Deadlift", reps=5, weight_kg=150.0, skipped=False)
        ]
        
        # Mock des résultats de base de données (tuples)
        self.sample_sessions_db = [
            (1, date(2023, 1, 1), "09:00:00", "Push A", "Bonne séance", datetime.now()),
            (2, date(2023, 1, 8), "09:00:00", "Pull A", "", datetime.now()),
            (3, date(2023, 1, 15), "09:00:00", "Legs A", "Séance difficile", datetime.now())
        ]
        
        self.sample_sets_db = [
            (1, 1, "Bench Press", "working_set", 10, 100.0, "Notes", False, datetime.now()),
            (2, 1, "Bench Press", "working_set", 8, 110.0, "Notes", False, datetime.now()),
            (3, 2, "Squat", "working_set", 12, 120.0, "Notes", False, datetime.now()),
            (4, 3, "Deadlift", "working_set", 5, 150.0, "Notes", False, datetime.now())
        ]
        
        self.sample_exercises_db = [("Bench Press",), ("Squat",), ("Deadlift",)]
    
    def test_get_sessions_success(self):
        """Test de récupération des sessions avec succès."""
        # Configurer le mock pour execute_query
        self.mock_db.execute_query.return_value = self.sample_sessions_db
        
        # Appeler le service
        result = self.db_service.get_sessions()
        
        # Vérifications
        assert len(result) == 3
        assert result[0].training_name == "Push A"
        self.mock_db.execute_query.assert_called_once()
    
    def test_get_sessions_empty_result(self):
        """Test de récupération des sessions avec résultat vide."""
        # Configurer le mock pour retourner une liste vide
        self.mock_db.execute_query.return_value = []
        
        # Appeler le service
        result = self.db_service.get_sessions()
        
        # Vérifications
        assert result == []
        assert len(result) == 0
        self.mock_db.execute_query.assert_called_once()
    
    def test_get_sets_success(self):
        """Test de récupération des sets avec succès."""
        # Configurer le mock pour execute_query
        self.mock_db.execute_query.return_value = self.sample_sets_db
        
        # Appeler le service
        result = self.db_service.get_sets()
        
        # Vérifications
        assert len(result) == 4
        assert result[0].exercise == "Bench Press"
        self.mock_db.execute_query.assert_called_once()
    
    def test_get_sets_empty_result(self):
        """Test de récupération des sets avec résultat vide."""
        # Configurer le mock pour retourner une liste vide
        self.mock_db.execute_query.return_value = []
        
        # Appeler le service
        result = self.db_service.get_sets()
        
        # Vérifications
        assert result == []
        assert len(result) == 0
        self.mock_db.execute_query.assert_called_once()
    
    def test_get_session_by_id_success(self):
        """Test de récupération d'une session par ID avec succès."""
        target_session_db = self.sample_sessions_db[0]
        self.mock_db.execute_query.return_value = [target_session_db]
        
        # Appeler le service
        result = self.db_service.get_session_by_id(1)
        
        # Vérifications
        assert result is not None
        assert result.training_name == "Push A"
        self.mock_db.execute_query.assert_called_once()
    
    def test_get_session_by_id_not_found(self):
        """Test de récupération d'une session par ID non trouvée."""
        # Configurer le mock pour retourner une liste vide
        self.mock_db.execute_query.return_value = []
        
        # Appeler le service
        result = self.db_service.get_session_by_id(999)
        
        # Vérifications
        assert result is None
        self.mock_db.execute_query.assert_called_once()
    
    def test_get_unique_exercises_success(self):
        """Test de récupération des exercices uniques avec succès."""
        expected_exercises = ["Bench Press", "Squat", "Deadlift"]
        self.mock_db.execute_query.return_value = self.sample_exercises_db
        
        # Appeler le service
        result = self.db_service.get_unique_exercises_from_sets()
        
        # Vérifications
        assert result == expected_exercises
        self.mock_db.execute_query.assert_called_once()
    
    def test_get_unique_exercises_empty_result(self):
        """Test de récupération des exercices uniques avec résultat vide."""
        # Configurer le mock pour retourner une liste vide
        self.mock_db.execute_query.return_value = []
        
        # Appeler le service
        result = self.db_service.get_unique_exercises_from_sets()
        
        # Vérifications
        assert result == []
        assert len(result) == 0
        self.mock_db.execute_query.assert_called_once()
    
    def test_database_error_handling(self):
        """Test de gestion des erreurs de base de données."""
        # Configurer le mock pour lever une exception
        self.mock_db.execute_query.side_effect = Exception("Erreur de base de données")
        
        # Appeler le service et vérifier que l'erreur est propagée
        with pytest.raises(Exception) as exc_info:
            self.db_service.get_sessions()
        
        # Vérifier que l'erreur contient le message original dans le détail
        error_str = str(exc_info.value)
        assert "Erreur de base de données" in error_str or "récupération des sessions" in error_str


class TestAnalyticsServiceRefactoring:
    """Tests pour le service d'analytics refactorisé."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        # Mock du service de base de données
        self.mock_db_service = Mock(spec=DatabaseService)
        
        # Créer le service d'analytics
        self.analytics_service = AnalyticsService(self.mock_db_service)
        
        # Données de test CORRIGÉES - objets Mock au lieu de DataFrames
        self.sample_sets_data = [
            Mock(id=1, session_id=1, exercise="Bench Press", series_type="working_set", reps=10, weight_kg=100.0, skipped=False),
            Mock(id=2, session_id=1, exercise="Bench Press", series_type="working_set", reps=8, weight_kg=110.0, skipped=False),
            Mock(id=3, session_id=1, exercise="Squat", series_type="working_set", reps=12, weight_kg=120.0, skipped=False),
            Mock(id=4, session_id=2, exercise="Bench Press", series_type="working_set", reps=10, weight_kg=105.0, skipped=False),
            Mock(id=5, session_id=2, exercise="Bench Press", series_type="working_set", reps=8, weight_kg=115.0, skipped=False),
            Mock(id=6, session_id=2, exercise="Squat", series_type="working_set", reps=12, weight_kg=125.0, skipped=False),
            Mock(id=7, session_id=3, exercise="Bench Press", series_type="working_set", reps=11, weight_kg=107.0, skipped=False),
            Mock(id=8, session_id=3, exercise="Bench Press", series_type="working_set", reps=9, weight_kg=117.0, skipped=False),
            Mock(id=9, session_id=3, exercise="Squat", series_type="working_set", reps=13, weight_kg=127.0, skipped=False)
        ]
        
        self.sample_sessions_data = [
            Mock(id=1, date=date(2023, 1, 1)),
            Mock(id=2, date=date(2023, 1, 8)),
            Mock(id=3, date=date(2023, 1, 15))
        ]
    
    def test_get_volume_analytics_success(self):
        """Test de récupération des analytics de volume avec succès."""
        # Configurer le mock pour retourner des données
        self.mock_db_service.get_sets.return_value = self.sample_sets_data
        self.mock_db_service.get_sessions.return_value = self.sample_sessions_data
        
        # Appeler le service
        result = self.analytics_service.get_volume_analytics()
        
        # Vérifications
        assert result is not None
        assert len(result) > 0, "Le résultat ne devrait pas être vide"
        
        # Vérifier la structure des données
        for item in result:
            assert hasattr(item, 'exercise')
            assert hasattr(item, 'total_volume')
            assert hasattr(item, 'avg_volume_per_set')
    
    def test_get_volume_analytics_empty_data(self):
        """Test de récupération des analytics de volume avec données vides."""
        # Configurer le mock pour retourner des listes vides
        self.mock_db_service.get_sets.return_value = []
        self.mock_db_service.get_sessions.return_value = []
        
        # Appeler le service
        result = self.analytics_service.get_volume_analytics()
        
        # Vérifications
        assert result == []
    
    def test_get_one_rm_analytics_success(self):
        """Test de récupération des analytics de 1RM avec succès."""
        # Configurer le mock pour retourner des données
        self.mock_db_service.get_sets.return_value = self.sample_sets_data
        self.mock_db_service.get_sessions.return_value = self.sample_sessions_data
        
        # Appeler le service
        result = self.analytics_service.get_one_rm_analytics()
        
        # Vérifications
        assert result is not None
        assert len(result) > 0, "Le résultat ne devrait pas être vide"
        
        # Vérifier la structure des données
        for item in result:
            assert hasattr(item, 'exercise')
            assert hasattr(item, 'best_1rm_epley')
            assert hasattr(item, 'best_1rm_brzycki')
    
    def test_get_one_rm_analytics_empty_data(self):
        """Test de récupération des analytics de 1RM avec données vides."""
        # Configurer le mock pour retourner une liste vide
        self.mock_db_service.get_sets.return_value = []
        
        # Appeler le service
        result = self.analytics_service.get_one_rm_analytics()
        
        # Vérifications
        assert result == []
    
    def test_get_progression_analytics_success(self):
        """Test de récupération des analytics de progression avec succès."""
        # Configurer le mock pour retourner des données
        self.mock_db_service.get_sets.return_value = self.sample_sets_data
        self.mock_db_service.get_sessions.return_value = self.sample_sessions_data
        
        # Appeler le service
        result = self.analytics_service.get_progression_analytics()
        
        # Vérifications
        assert result is not None
        assert len(result) > 0, "Le résultat ne devrait pas être vide"
        
        # Vérifier la structure des données
        for item in result:
            assert hasattr(item, 'exercise')
    
    def test_get_progression_analytics_empty_data(self):
        """Test de récupération des analytics de progression avec données vides."""
        # Configurer le mock pour retourner des listes vides
        self.mock_db_service.get_sets.return_value = []
        self.mock_db_service.get_sessions.return_value = []
        
        # Appeler le service
        result = self.analytics_service.get_progression_analytics()
        
        # Vérifications
        assert result == []
    
    def test_get_dashboard_data_success(self):
        """Test de récupération des données du dashboard avec succès."""
        # Configurer le mock pour retourner des données
        self.mock_db_service.get_sets.return_value = self.sample_sets_data
        self.mock_db_service.get_sessions.return_value = self.sample_sessions_data
        self.mock_db_service.get_unique_exercises_from_sets.return_value = ["Bench Press", "Squat"]
        
        # Appeler le service
        result = self.analytics_service.get_dashboard_data()
        
        # Vérifications
        assert result is not None
        assert result.total_sessions == 3
        assert result.total_exercises == 2
    
    def test_get_dashboard_data_empty_data(self):
        """Test de récupération des données du dashboard avec données vides."""
        # Configurer le mock pour retourner des listes vides
        self.mock_db_service.get_sets.return_value = []
        self.mock_db_service.get_sessions.return_value = []
        self.mock_db_service.get_unique_exercises_from_sets.return_value = []
        
        # Appeler le service
        result = self.analytics_service.get_dashboard_data()
        
        # Vérifications
        assert result is not None
        assert result.total_sessions == 0
        assert result.total_exercises == 0
    
    def test_error_handling_in_analytics(self):
        """Test de gestion des erreurs dans les analytics."""
        # Configurer le mock pour lever une exception
        self.mock_db_service.get_sets.side_effect = Exception("Erreur de base de données")
        
        # Vérifier que l'erreur se propage correctement
        with pytest.raises(Exception):
            self.analytics_service.get_volume_analytics()
    
    def test_data_transformation_consistency(self):
        """Test de cohérence de la transformation des données."""
        # Configurer le mock pour retourner des données
        self.mock_db_service.get_sets.return_value = self.sample_sets_data
        self.mock_db_service.get_sessions.return_value = self.sample_sessions_data
        
        # Appeler plusieurs services et vérifier la cohérence
        volume_result = self.analytics_service.get_volume_analytics()
        one_rm_result = self.analytics_service.get_one_rm_analytics()
        progression_result = self.analytics_service.get_progression_analytics()
        
        # Vérifications
        assert volume_result is not None
        assert one_rm_result is not None
        assert progression_result is not None
        
        # Vérifier que les données sont cohérentes
        assert len(volume_result) > 0
        assert len(one_rm_result) > 0
        assert len(progression_result) > 0


class TestServiceIntegration:
    """Tests d'intégration entre les services."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        # Créer des services avec des mocks
        self.mock_db = Mock()
        self.db_service = DatabaseService(self.mock_db)
        self.analytics_service = AnalyticsService(self.db_service)
        
        # Données de test pour la base de données (tuples)
        self.test_sets_db = [
            (1, 1, "Bench Press", "working_set", 10, 100.0, "Notes", False, datetime.now()),
            (2, 1, "Bench Press", "working_set", 8, 110.0, "Notes", False, datetime.now()),
            (3, 2, "Squat", "working_set", 12, 120.0, "Notes", False, datetime.now())
        ]
        
        self.test_sessions_db = [
            (1, date(2023, 1, 1), "09:00:00", "Push A", "Notes", datetime.now()),
            (2, date(2023, 1, 8), "09:00:00", "Pull A", "Notes", datetime.now())
        ]
        
        self.test_exercises_db = [("Bench Press",), ("Squat",)]
    
    def test_full_pipeline_integration(self):
        """Test d'intégration du pipeline complet."""
        # Configurer les mocks pour execute_query
        self.mock_db.execute_query.return_value = self.test_sets_db
        
        # Tester le pipeline complet
        try:
            # 1. Récupération des données de base
            sets = self.db_service.get_sets()
            sessions = self.db_service.get_sessions()
            exercises = self.db_service.get_unique_exercises_from_sets()
            
            # 2. Calcul des analytics
            volume_analytics = self.analytics_service.get_volume_analytics()
            one_rm_analytics = self.analytics_service.get_one_rm_analytics()
            progression_analytics = self.analytics_service.get_progression_analytics()
            dashboard_data = self.analytics_service.get_dashboard_data()
            
            # Vérifications
            assert len(sets) == 3
            assert len(sessions) == 2
            assert len(exercises) == 2
            
            assert volume_analytics is not None
            assert one_rm_analytics is not None
            assert progression_analytics is not None
            assert dashboard_data is not None
            
            # Vérifier la cohérence des données
            assert dashboard_data.total_sessions == 2
            assert dashboard_data.total_exercises == 2
            
        except Exception as e:
            pytest.fail(f"Le pipeline d'intégration a échoué: {e}")
    
    def test_error_propagation(self):
        """Test de propagation des erreurs entre services."""
        # Configurer le mock pour lever une exception
        self.mock_db.execute_query.side_effect = Exception("Erreur de base de données")
        
        # Vérifier que l'erreur se propage correctement
        with pytest.raises(Exception) as exc_info:
            self.db_service.get_sets()
        
        # Vérifier que l'erreur contient le message original dans le détail
        error_str = str(exc_info.value)
        assert "Erreur de base de données" in error_str or "récupération des sets" in error_str
        
        # Vérifier que l'erreur se propage aussi dans les analytics
        with pytest.raises(Exception) as exc_info:
            self.analytics_service.get_volume_analytics()
        
        # Vérifier que l'erreur contient le message original dans le détail
        error_str = str(exc_info.value)
        assert "Erreur de base de données" in error_str or "récupération des sets" in error_str


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
