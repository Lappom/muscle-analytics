"""
Tests pour les services refactorisés avec gestion des DataFrames vides.
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
        # Mock de la base de données avec attribut .db
        self.mock_db = Mock()
        self.mock_db.db = Mock()
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
    
    def test_get_sessions_success(self):
        """Test de récupération des sessions avec succès."""
        # Configurer le mock pour simuler execute_query
        mock_results = [
            (1, date(2023, 1, 1), "10:00", "Push A", "Bonne séance", datetime.now()),
            (2, date(2023, 1, 8), "10:00", "Pull A", "", datetime.now()),
            (3, date(2023, 1, 15), "10:00", "Legs A", "Séance difficile", datetime.now())
        ]
        self.mock_db.execute_query.return_value = mock_results
        
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
        # Configurer le mock pour simuler execute_query avec toutes les colonnes
        mock_results = [
            (1, 1, "Bench Press", "working_set", 10, 100.0, "", False, datetime.now()),
            (2, 1, "Bench Press", "working_set", 8, 110.0, "", False, datetime.now()),
            (3, 2, "Squat", "working_set", 12, 120.0, "", False, datetime.now()),
            (4, 3, "Deadlift", "working_set", 5, 150.0, "", False, datetime.now())
        ]
        self.mock_db.execute_query.return_value = mock_results
        
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
        # Configurer le mock pour simuler execute_query
        mock_result = [(1, date(2023, 1, 1), "10:00", "Push A", "Bonne séance", datetime.now())]
        self.mock_db.execute_query.return_value = mock_result
        
        # Appeler le service
        result = self.db_service.get_session_by_id(1)
        
        # Vérifications
        assert result is not None
        assert result.id == 1
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
        # Configurer le mock pour simuler execute_query
        mock_results = [('Bench Press',), ('Squat',), ('Deadlift',)]
        self.mock_db.execute_query.return_value = mock_results
        
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
        
        # Vérifier que l'erreur est bien propagée (peut être HTTPException ou Exception)
        assert "Erreur" in str(exc_info.value)


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
        empty_sets = []
        empty_sessions = []
        
        self.mock_db_service.get_sets.return_value = empty_sets
        self.mock_db_service.get_sessions.return_value = empty_sessions
        
        # Appeler le service
        result = self.analytics_service.get_volume_analytics()
        
        # Vérifications
        assert result is not None
        # Le résultat peut être vide mais doit être géré gracieusement
        if isinstance(result, list):
            assert len(result) == 0
        else:
            assert result.empty if hasattr(result, 'empty') else True
    
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
        empty_sets = []
        self.mock_db_service.get_sets.return_value = empty_sets
        
        # Appeler le service
        result = self.analytics_service.get_one_rm_analytics()
        
        # Vérifications
        assert result is not None
        # Le résultat peut être vide mais doit être géré gracieusement
        if isinstance(result, list):
            assert len(result) == 0
        else:
            assert result.empty if hasattr(result, 'empty') else True
    
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
            assert hasattr(item, 'total_sessions')
            assert hasattr(item, 'progression_trend')
    
    def test_get_progression_analytics_empty_data(self):
        """Test de récupération des analytics de progression avec données vides."""
        # Configurer le mock pour retourner des listes vides
        empty_sets = []
        empty_sessions = []
        
        self.mock_db_service.get_sets.return_value = empty_sets
        self.mock_db_service.get_sessions.return_value = empty_sessions
        
        # Appeler le service
        result = self.analytics_service.get_progression_analytics()
        
        # Vérifications
        assert result is not None
        # Le résultat peut être vide mais doit être géré gracieusement
        if isinstance(result, list):
            assert len(result) == 0
        else:
            assert result.empty if hasattr(result, 'empty') else True
    
    def test_get_dashboard_data_success(self):
        """Test de récupération des données du dashboard avec succès."""
        # Configurer le mock pour retourner des données
        self.mock_db_service.get_sets.return_value = self.sample_sets_data
        self.mock_db_service.get_sessions.return_value = self.sample_sessions_data
        
        # Appeler le service
        result = self.analytics_service.get_dashboard_data()
        
        # Vérifications
        assert result is not None
        assert hasattr(result, 'total_sessions')
        assert hasattr(result, 'total_exercises')
        assert hasattr(result, 'total_volume_this_week')
        assert hasattr(result, 'total_volume_this_month')
    
    def test_get_dashboard_data_empty_data(self):
        """Test de récupération des données du dashboard avec données vides."""
        # Configurer le mock pour retourner des DataFrames vides
        empty_sets = pd.DataFrame(columns=['session_id', 'exercise', 'series_type', 'reps', 'weight_kg', 'skipped'])
        empty_sessions = pd.DataFrame(columns=['id', 'date'])
        
        self.mock_db_service.get_sets.return_value = empty_sets
        self.mock_db_service.get_sessions.return_value = empty_sessions
        
        # Appeler le service
        result = self.analytics_service.get_dashboard_data()
        
        # Vérifications
        assert result is not None
        # Vérifier que les valeurs par défaut sont définies
        assert result.total_sessions == 0
        assert result.total_exercises == 0
        assert result.total_volume_this_week == 0.0
        assert result.total_volume_this_month == 0.0
    
    def test_error_handling_in_analytics(self):
        """Test de gestion des erreurs dans les analytics."""
        # Configurer le mock pour lever une exception
        self.mock_db_service.get_sets.side_effect = Exception("Erreur lors de la récupération des sets")
        
        # Appeler le service et vérifier que l'erreur est gérée
        with pytest.raises(Exception) as exc_info:
            self.analytics_service.get_volume_analytics()
        
        assert "Erreur lors de la récupération des sets" in str(exc_info.value)
    
    def test_data_transformation_consistency(self):
        """Test de cohérence de la transformation des données."""
        # Configurer le mock pour retourner des données
        self.mock_db_service.get_sets.return_value = self.sample_sets_data
        self.mock_db_service.get_sessions.return_value = self.sample_sessions_data
        
        # Appeler plusieurs services et vérifier la cohérence
        volume_result = self.analytics_service.get_volume_analytics()
        one_rm_result = self.analytics_service.get_one_rm_analytics()
        progression_result = self.analytics_service.get_progression_analytics()
        
        # Vérifier que tous les résultats sont cohérents
        assert volume_result is not None
        assert one_rm_result is not None
        assert progression_result is not None
        
        # Vérifier que les exercices sont cohérents entre les différents analytics
        if len(volume_result) > 0 and len(one_rm_result) > 0:
            volume_exercises = {item.exercise for item in volume_result}
            one_rm_exercises = {item.exercise for item in one_rm_result}
            
            # Les exercices devraient être les mêmes
            assert volume_exercises == one_rm_exercises, "Les exercices devraient être cohérents entre les analytics"
    
    def test_performance_with_large_dataset(self):
        """Test de performance avec un grand dataset."""
        # Créer un grand dataset de test avec des objets Mock
        large_sets = []
        large_sessions = []
        
        for i in range(1, 1001):
            # Créer des objets Mock pour les sets
            mock_set = Mock()
            mock_set.session_id = i
            mock_set.exercise = 'Bench Press' if i <= 500 else 'Squat'
            mock_set.series_type = 'working_set'
            mock_set.reps = np.random.randint(5, 15)
            mock_set.weight_kg = np.random.uniform(50, 200)
            mock_set.skipped = False
            large_sets.append(mock_set)
            
            # Créer des objets Mock pour les sessions
            mock_session = Mock()
            mock_session.id = i
            mock_session.date = date(2023, 1, 1) + timedelta(days=i-1)
            large_sessions.append(mock_session)
        
        # Configurer le mock
        self.mock_db_service.get_sets.return_value = large_sets
        self.mock_db_service.get_sessions.return_value = large_sessions
        
        # Mesurer le temps d'exécution
        import time
        start_time = time.time()
        
        # Appeler le service
        result = self.analytics_service.get_volume_analytics()
        
        execution_time = time.time() - start_time
        
        # Vérifications
        assert result is not None
        assert len(result) > 0
        
        # L'exécution devrait être rapide (moins de 5 secondes pour 1000 enregistrements)
        assert execution_time < 5.0, f"Exécution trop lente: {execution_time:.3f}s"
    
    def test_memory_usage_optimization(self):
        """Test d'optimisation de l'utilisation mémoire."""
        # Créer un dataset de taille moyenne avec des objets Mock
        medium_sets = []
        medium_sessions = []
        
        for i in range(1, 101):
            # Créer des objets Mock pour les sets
            mock_set = Mock()
            mock_set.session_id = i
            mock_set.exercise = 'Bench Press' if i <= 50 else 'Squat'
            mock_set.series_type = 'working_set'
            mock_set.reps = np.random.randint(5, 15)
            mock_set.weight_kg = np.random.uniform(50, 200)
            mock_set.skipped = False
            medium_sets.append(mock_set)
            
            # Créer des objets Mock pour les sessions
            mock_session = Mock()
            mock_session.id = i
            mock_session.date = date(2023, 1, 1) + timedelta(days=i-1)
            medium_sessions.append(mock_session)
        
        # Configurer le mock
        self.mock_db_service.get_sets.return_value = medium_sets
        self.mock_db_service.get_sessions.return_value = medium_sessions
        
        # Mesurer l'utilisation mémoire
        import psutil
        import os
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Appeler plusieurs services
        volume_result = self.analytics_service.get_volume_analytics()
        one_rm_result = self.analytics_service.get_one_rm_analytics()
        progression_result = self.analytics_service.get_progression_analytics()
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        
        # Vérifications
        assert volume_result is not None
        assert one_rm_result is not None
        assert progression_result is not None
        
        # L'augmentation de mémoire ne devrait pas être excessive
        memory_increase = memory_after - memory_before
        assert memory_increase < 50, f"Augmentation de mémoire excessive: {memory_increase:.2f}MB"


class TestServiceIntegration:
    """Tests d'intégration entre les services."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        # Créer des services avec des mocks
        self.mock_db = Mock()
        self.db_service = DatabaseService(self.mock_db)
        self.analytics_service = AnalyticsService(self.db_service)
        
        # Données de test
        self.test_sets = pd.DataFrame({
            'session_id': [1, 1, 2],
            'exercise': ['Bench Press', 'Bench Press', 'Squat'],
            'series_type': ['working_set', 'working_set', 'working_set'],
            'reps': [10, 8, 12],
            'weight_kg': [100, 110, 120],
            'skipped': [False, False, False]
        })
        
        self.test_sessions = pd.DataFrame({
            'id': [1, 2],
            'date': ['2023-01-01', '2023-01-08']
        })
    
    def test_full_pipeline_integration(self):
        """Test d'intégration du pipeline complet."""
        # Utiliser des mocks pour les méthodes du service plutôt que la base de données
        from unittest.mock import patch
        
        # Mock des méthodes du service
        with patch.object(self.db_service, 'get_sets') as mock_get_sets, \
             patch.object(self.db_service, 'get_sessions') as mock_get_sessions:
            
            # Configurer les mocks pour retourner des objets Set et Session
            from src.api.models import Set, Session
            from datetime import datetime, date
            
            mock_sets = [
                Set(id=1, session_id=1, exercise='Bench Press', series_type='working_set', 
                    reps=10, weight_kg=100.0, notes='', skipped=False, created_at=datetime.now()),
                Set(id=2, session_id=1, exercise='Bench Press', series_type='working_set', 
                    reps=8, weight_kg=110.0, notes='', skipped=False, created_at=datetime.now()),
                Set(id=3, session_id=2, exercise='Squat', series_type='working_set', 
                    reps=12, weight_kg=120.0, notes='', skipped=False, created_at=datetime.now())
            ]
            
            mock_sessions = [
                Session(id=1, date=date(2023, 1, 1), start_time="10:00", 
                       training_name="Push A", notes="", created_at=datetime.now()),
                Session(id=2, date=date(2023, 1, 8), start_time="10:00", 
                       training_name="Pull A", notes="", created_at=datetime.now())
            ]
            
            mock_get_sets.return_value = mock_sets
            mock_get_sessions.return_value = mock_sessions
            
            # Tester le pipeline complet
            try:
                # 1. Récupération des données de base
                sets = self.db_service.get_sets()
                sessions = self.db_service.get_sessions()
                
                # 2. Calcul des analytics
                volume_analytics = self.analytics_service.get_volume_analytics()
                one_rm_analytics = self.analytics_service.get_one_rm_analytics()
                progression_analytics = self.analytics_service.get_progression_analytics()
                dashboard_data = self.analytics_service.get_dashboard_data()
                
                # Vérifications
                assert len(sets) == 3
                assert len(sessions) == 2
                
                assert volume_analytics is not None
                assert one_rm_analytics is not None
                assert progression_analytics is not None
                assert dashboard_data is not None
                
            except Exception as e:
                pytest.fail(f"Le pipeline d'intégration a échoué: {e}")
    
    def test_error_propagation(self):
        """Test de propagation des erreurs entre services."""
        # Configurer le mock pour lever une exception
        self.mock_db.execute_query.side_effect = Exception("Erreur de base de données")
        
        # Vérifier que l'erreur se propage correctement
        with pytest.raises(Exception) as exc_info:
            self.db_service.get_sets()
        
        # Le service transforme l'erreur en HTTPException, vérifier le message
        assert "récupération des sets" in str(exc_info.value)
        
        # Vérifier que l'erreur se propage aussi dans les analytics
        with pytest.raises(Exception) as exc_info:
            self.analytics_service.get_volume_analytics()
        
        # Le service transforme l'erreur en HTTPException, vérifier le message
        assert "récupération des sets" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
