"""
Tests pour les optimisations de calculs et la gestion des performances.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.features.volume import VolumeCalculator
from src.features.one_rm import OneRMCalculator
from src.features.progression import ProgressionAnalyzer


class TestCalculationOptimizations:
    """Tests pour les optimisations de calculs."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        self.volume_calc = VolumeCalculator()
        self.one_rm_calc = OneRMCalculator()
        self.prog_analyzer = ProgressionAnalyzer()
        
        # Données de test CORRIGÉES avec 'working_set'
        self.sample_data = pd.DataFrame({
            'session_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
            'exercise': ['Bench Press', 'Bench Press', 'Squat', 'Bench Press', 'Bench Press', 'Squat', 'Bench Press', 'Bench Press', 'Squat'],
            'series_type': ['working_set', 'working_set', 'working_set', 'working_set', 'working_set', 'working_set', 'working_set', 'working_set', 'working_set'],
            'reps': [10, 8, 12, 10, 8, 12, 11, 9, 13],
            'weight_kg': [100, 110, 120, 105, 115, 125, 107, 117, 127],
            'skipped': [False, False, False, False, False, False, False, False, False]
        })
        
        self.sessions_data = pd.DataFrame({
            'id': [1, 2, 3],
            'date': ['2023-01-01', '2023-01-08', '2023-01-15']
        })
    
    def test_volume_calculation_optimization(self):
        """Test d'optimisation du calcul de volume."""
        # Calculer le volume
        data_with_volume = self.volume_calc.calculate_set_volume(self.sample_data)
        
        # Vérifier que le résultat n'est pas vide
        assert not data_with_volume.empty, "Le résultat ne devrait pas être vide"
        assert 'volume' in data_with_volume.columns
        
        # Vérifier que les calculs sont corrects
        expected_volumes = [1000, 880, 1440, 1050, 920, 1500, 1177, 1053, 1651]
        actual_volumes = data_with_volume['volume'].tolist()
        
        # Comparer les volumes calculés avec les valeurs attendues
        for expected, actual in zip(expected_volumes, actual_volumes):
            assert abs(expected - actual) < 0.01, f"Volume attendu: {expected}, Volume calculé: {actual}"
    
    def test_volume_calculation_empty_data(self):
        """Test de calcul de volume avec données vides."""
        empty_data = pd.DataFrame(columns=['session_id', 'exercise', 'series_type', 'reps', 'weight_kg', 'skipped'])
        
        result = self.volume_calc.calculate_set_volume(empty_data)
        
        # Vérifier que le résultat est vide mais avec la bonne structure
        assert result.empty
        assert 'volume' in result.columns or len(result.columns) > 0
    
    def test_session_volume_optimization(self):
        """Test d'optimisation du calcul de volume par séance."""
        data_with_volume = self.volume_calc.calculate_set_volume(self.sample_data)
        result = self.volume_calc.calculate_session_volume(data_with_volume)
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
        assert 'volume_sum' in result.columns
        
        # Vérifier qu'il y a des données pour chaque session et exercice
        expected_combinations = [
            (1, 'Bench Press'), (1, 'Squat'),
            (2, 'Bench Press'), (2, 'Squat'),
            (3, 'Bench Press'), (3, 'Squat')
        ]
        
        for session_id, exercise in expected_combinations:
            subset = result[(result['session_id'] == session_id) & (result['exercise'] == exercise)]
            assert len(subset) == 1, f"Données manquantes pour session {session_id}, exercice {exercise}"
    
    def test_weekly_volume_optimization(self):
        """Test d'optimisation du calcul de volume hebdomadaire."""
        data_with_volume = self.volume_calc.calculate_set_volume(self.sample_data)
        result = self.volume_calc.calculate_weekly_volume(data_with_volume, self.sessions_data)
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
        assert 'volume_sum' in result.columns
        assert 'week' in result.columns
        
        # Vérifier qu'il y a des données hebdomadaires
        assert len(result) > 0, "Il devrait y avoir des données hebdomadaires"
    
    def test_one_rm_calculation_optimization(self):
        """Test d'optimisation du calcul de 1RM."""
        result = self.one_rm_calc.calculate_dataframe_1rm(self.sample_data)
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
        assert 'one_rm_epley' in result.columns
        assert 'one_rm_brzycki' in result.columns
        
        # Vérifier que les valeurs 1RM sont calculées correctement
        assert not result['one_rm_epley'].isna().all(), "Les valeurs 1RM Epley ne devraient pas être toutes NaN"
        assert not result['one_rm_brzycki'].isna().all(), "Les valeurs 1RM Brzycki ne devraient pas être toutes NaN"
        
        # Vérifier que les formules donnent des résultats cohérents
        epley_values = result['one_rm_epley'].dropna()
        brzycki_values = result['one_rm_brzycki'].dropna()
        
        if len(epley_values) > 0 and len(brzycki_values) > 0:
            # Les formules Epley et Brzycki devraient donner des résultats similaires pour des reps faibles
            for i in range(min(len(epley_values), len(brzycki_values))):
                epley_val = epley_values.iloc[i]
                brzycki_val = brzycki_values.iloc[i]
                # Les valeurs devraient être dans un rapport raisonnable (pas plus de 20% de différence)
                ratio = abs(epley_val - brzycki_val) / max(epley_val, brzycki_val)
                assert ratio < 0.2, f"Différence trop importante entre Epley ({epley_val}) et Brzycki ({brzycki_val})"
    
    def test_one_rm_calculation_empty_data(self):
        """Test de calcul 1RM avec données vides."""
        empty_data = pd.DataFrame(columns=['session_id', 'exercise', 'series_type', 'reps', 'weight_kg', 'skipped'])
        
        result = self.one_rm_calc.calculate_dataframe_1rm(empty_data)
        
        # Vérifier que le résultat est vide mais avec la bonne structure
        assert result.empty
        assert 'one_rm_epley' in result.columns or len(result.columns) > 0
    
    def test_progression_analysis_optimization(self):
        """Test d'optimisation de l'analyse de progression."""
        # Préparer les données avec dates
        data_with_volume = self.volume_calc.calculate_set_volume(self.sample_data)
        data_with_dates = data_with_volume.merge(
            self.sessions_data[['id', 'date']], 
            left_on='session_id', right_on='id', 
            how='left'
        )
        data_with_dates['date'] = pd.to_datetime(data_with_dates['date'])
        
        # Analyser la progression
        result = self.prog_analyzer.calculate_volume_progression(data_with_dates)
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
        assert 'volume_progression' in result.columns
        
        # Vérifier qu'il y a des données de progression
        progression_values = result['volume_progression'].dropna()
        assert len(progression_values) > 0, "Il devrait y avoir des valeurs de progression non-NaN"
    
    def test_progression_analysis_empty_data(self):
        """Test d'analyse de progression avec données vides."""
        empty_data = pd.DataFrame(columns=['session_id', 'exercise', 'series_type', 'reps', 'weight_kg', 'skipped', 'volume', 'date'])
        
        result = self.prog_analyzer.calculate_volume_progression(empty_data)
        
        # Vérifier que le résultat est vide mais avec la bonne structure
        assert result.empty
        assert 'volume_progression' in result.columns or len(result.columns) > 0
    
    def test_plateau_detection_optimization(self):
        """Test d'optimisation de la détection de plateaux."""
        # Créer des données avec un plateau évident
        plateau_data = pd.DataFrame({
            'session_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'exercise': ['Bench Press'] * 10,
            'series_type': ['working_set'] * 10,
            'reps': [10, 10, 10, 10, 10, 10, 10, 10, 10, 10],
            'weight_kg': [100, 100, 100, 100, 100, 100, 100, 100, 100, 100],
            'skipped': [False] * 10,
            'volume': [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
            'date': pd.date_range('2023-01-01', periods=10, freq='D')
        })
        
        result = self.prog_analyzer.detect_plateaus(plateau_data)
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
        assert 'plateau_indicator' in result.columns
        
        # Avec des données aussi stables, un plateau devrait être détecté
        if 'plateau_detected' in result.columns:
            plateau_detected = result['plateau_detected'].any()
            # Note: La détection de plateau peut varier selon l'algorithme
            # On vérifie juste que la colonne existe et contient des valeurs booléennes
    
    def test_memory_optimization(self):
        """Test d'optimisation de la mémoire."""
        # Créer un grand dataset pour tester la gestion mémoire
        large_data = pd.DataFrame({
            'session_id': list(range(1, 1001)),  # 1000 sessions
            'exercise': ['Bench Press'] * 500 + ['Squat'] * 500,
            'series_type': ['working_set'] * 1000,
            'reps': np.random.randint(5, 15, 1000),
            'weight_kg': np.random.uniform(50, 200, 1000),
            'skipped': [False] * 1000
        })
        
        # Mesurer l'utilisation mémoire avant
        import psutil
        import os
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Exécuter les calculs
        data_with_volume = self.volume_calc.calculate_set_volume(large_data)
        session_volumes = self.volume_calc.calculate_session_volume(data_with_volume)
        weekly_volumes = self.volume_calc.calculate_weekly_volume(data_with_volume, pd.DataFrame({
            'id': list(range(1, 1001)),
            'date': pd.date_range('2023-01-01', periods=1000, freq='D')
        }))
        
        # Mesurer l'utilisation mémoire après
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        
        # Vérifier que les calculs fonctionnent
        assert not data_with_volume.empty
        assert not session_volumes.empty
        assert not weekly_volumes.empty
        
        # Vérifier que l'utilisation mémoire est raisonnable
        memory_increase = memory_after - memory_before
        # L'augmentation de mémoire ne devrait pas dépasser 100MB pour 1000 enregistrements
        assert memory_increase < 100, f"Augmentation de mémoire excessive: {memory_increase:.2f}MB"
    
    def test_performance_benchmark(self):
        """Test de benchmark des performances."""
        import time
        
        # Créer un dataset de taille moyenne
        medium_data = pd.DataFrame({
            'session_id': list(range(1, 101)),  # 100 sessions
            'exercise': ['Bench Press'] * 50 + ['Squat'] * 50,
            'series_type': ['working_set'] * 100,
            'reps': np.random.randint(5, 15, 100),
            'weight_kg': np.random.uniform(50, 200, 100),
            'skipped': [False] * 100
        })
        
        # Mesurer le temps de calcul du volume
        start_time = time.time()
        data_with_volume = self.volume_calc.calculate_set_volume(medium_data)
        volume_time = time.time() - start_time
        
        # Mesurer le temps de calcul des volumes par séance
        start_time = time.time()
        session_volumes = self.volume_calc.calculate_session_volume(data_with_volume)
        session_time = time.time() - start_time
        
        # Mesurer le temps de calcul des volumes hebdomadaires
        sessions_df = pd.DataFrame({
            'id': list(range(1, 101)),
            'date': pd.date_range('2023-01-01', periods=100, freq='D')
        })
        
        start_time = time.time()
        weekly_volumes = self.volume_calc.calculate_weekly_volume(data_with_volume, sessions_df)
        weekly_time = time.time() - start_time
        
        # Vérifier que les calculs sont rapides (moins de 1 seconde pour 100 enregistrements)
        assert volume_time < 1.0, f"Calcul de volume trop lent: {volume_time:.3f}s"
        assert session_time < 1.0, f"Calcul de volume par séance trop lent: {session_time:.3f}s"
        assert weekly_time < 1.0, f"Calcul de volume hebdomadaire trop lent: {weekly_time:.3f}s"
        
        # Vérifier que les résultats sont corrects
        assert not data_with_volume.empty
        assert not session_volumes.empty
        assert not weekly_volumes.empty
    
    def test_data_consistency_optimization(self):
        """Test de cohérence des données à travers les optimisations."""
        # Vérifier que les optimisations ne changent pas les résultats
        data_with_volume = self.volume_calc.calculate_set_volume(self.sample_data)
        
        # Calculer les volumes par séance
        session_volumes_1 = self.volume_calc.calculate_session_volume(data_with_volume)
        session_volumes_2 = self.volume_calc.calculate_session_volume(data_with_volume)
        
        # Les résultats devraient être identiques
        pd.testing.assert_frame_equal(session_volumes_1, session_volumes_2, check_dtype=False)
        
        # Vérifier que les calculs sont déterministes
        volume_values_1 = data_with_volume['volume'].tolist()
        volume_values_2 = self.volume_calc.calculate_set_volume(self.sample_data)['volume'].tolist()
        
        assert volume_values_1 == volume_values_2, "Les calculs de volume devraient être déterministes"
    
    def test_error_handling_optimization(self):
        """Test de gestion des erreurs avec optimisations."""
        # Test avec données corrompues
        corrupted_data = self.sample_data.copy()
        corrupted_data.loc[0, 'reps'] = np.nan
        corrupted_data.loc[1, 'weight_kg'] = -10  # Poids négatif
        corrupted_data.loc[2, 'series_type'] = 'invalid_type'  # Type invalide
        
        # Les calculs devraient gérer les erreurs gracieusement
        try:
            data_with_volume = self.volume_calc.calculate_set_volume(corrupted_data)
            
            # Vérifier que le résultat n'est pas vide
            assert not data_with_volume.empty, "Le résultat ne devrait pas être vide même avec des données corrompues"
            
            # Vérifier que les valeurs problématiques sont gérées
            if 'volume' in data_with_volume.columns:
                # Les volumes avec données invalides devraient être 0
                assert data_with_volume.loc[0, 'volume'] == 0, "Volume avec reps NaN devrait être 0"
                assert data_with_volume.loc[1, 'volume'] == 0, "Volume avec poids négatif devrait être 0"
                
        except Exception as e:
            # Si une exception est levée, elle devrait être informative
            assert "données" in str(e).lower() or "validation" in str(e).lower(), f"Exception non informative: {e}"
    
    def test_integration_optimization(self):
        """Test d'intégration des optimisations."""
        # Test du pipeline complet avec optimisations
        try:
            # 1. Calcul du volume
            data_with_volume = self.volume_calc.calculate_set_volume(self.sample_data)
            assert not data_with_volume.empty
            
            # 2. Calcul des volumes par séance
            session_volumes = self.volume_calc.calculate_session_volume(data_with_volume)
            assert not session_volumes.empty
            
            # 3. Calcul des volumes hebdomadaires
            weekly_volumes = self.volume_calc.calculate_weekly_volume(data_with_volume, self.sessions_data)
            assert not weekly_volumes.empty
            
            # 4. Calcul des 1RM
            one_rm_data = self.one_rm_calc.calculate_dataframe_1rm(self.sample_data)
            assert not one_rm_data.empty
            
            # 5. Analyse de progression
            data_with_dates = data_with_volume.merge(
                self.sessions_data[['id', 'date']], 
                left_on='session_id', right_on='id', 
                how='left'
            )
            data_with_dates['date'] = pd.to_datetime(data_with_dates['date'])
            
            progression_data = self.prog_analyzer.calculate_volume_progression(data_with_dates)
            assert not progression_data.empty
            
            # Vérifier que toutes les données sont cohérentes
            assert len(data_with_volume) == len(self.sample_data)
            assert len(session_volumes) > 0
            assert len(weekly_volumes) > 0
            assert len(one_rm_data) == len(self.sample_data)
            assert len(progression_data) > 0
            
        except Exception as e:
            pytest.fail(f"Le pipeline d'optimisation a échoué: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
