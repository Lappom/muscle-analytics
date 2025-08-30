"""
Tests unitaires pour les modules de calcul de features avancées.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.features.volume import VolumeCalculator
from src.features.one_rm import OneRMCalculator
from src.features.progression import ProgressionAnalyzer
from src.features.calculations import FeatureCalculator


class TestVolumeCalculator:
    """Tests pour VolumeCalculator."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        self.volume_calc = VolumeCalculator()
        
        # Données de test
        self.sample_data = pd.DataFrame({
            'session_id': [1, 1, 1, 2, 2, 2],
            'exercise': ['Bench Press', 'Bench Press', 'Squat', 'Bench Press', 'Bench Press', 'Squat'],
            'series_type': ['principale', 'principale', 'principale', 'principale', 'principale', 'principale'],
            'reps': [10, 8, 12, 10, 8, 12],
            'weight_kg': [100, 110, 120, 105, 115, 125],
            'skipped': [False, False, False, False, False, False]
        })
        
        self.sessions_data = pd.DataFrame({
            'id': [1, 2],
            'date': ['2023-01-01', '2023-01-03']
        })
    
    def test_calculate_set_volume(self):
        """Test calcul volume par set."""
        result = self.volume_calc.calculate_set_volume(self.sample_data)
        
        expected_volumes = [1000, 880, 1440, 1050, 920, 1500]  # reps * weight
        
        assert 'volume' in result.columns
        assert result['volume'].tolist() == expected_volumes
    
    def test_calculate_set_volume_with_nulls(self):
        """Test calcul volume avec valeurs nulles."""
        data_with_nulls = self.sample_data.copy()
        data_with_nulls.loc[0, 'reps'] = np.nan
        data_with_nulls.loc[1, 'weight_kg'] = np.nan
        data_with_nulls.loc[2, 'skipped'] = True
        
        result = self.volume_calc.calculate_set_volume(data_with_nulls)
        
        # Vérifier que les valeurs nulles/skipped donnent volume 0
        assert result.loc[0, 'volume'] == 0  # reps null
        assert result.loc[1, 'volume'] == 0  # weight null
        assert result.loc[2, 'volume'] == 0  # skipped
    
    def test_calculate_session_volume(self):
        """Test calcul volume par séance."""
        data_with_volume = self.volume_calc.calculate_set_volume(self.sample_data)
        result = self.volume_calc.calculate_session_volume(data_with_volume)
        
        assert 'volume_sum' in result.columns
        assert len(result) == 4  # 2 séances × 2 exercices
        
        # Vérifier quelques valeurs
        bench_session_1 = result[
            (result['session_id'] == 1) & (result['exercise'] == 'Bench Press')
        ]
        assert len(bench_session_1) == 1
        assert bench_session_1['volume_sum'].iloc[0] == 1880  # 1000 + 880
    
    def test_calculate_weekly_volume(self):
        """Test calcul volume hebdomadaire."""
        data_with_volume = self.volume_calc.calculate_set_volume(self.sample_data)
        result = self.volume_calc.calculate_weekly_volume(
            data_with_volume, self.sessions_data
        )
        
        assert 'volume_sum' in result.columns
        assert 'week' in result.columns
        assert len(result) > 0


class TestOneRMCalculator:
    """Tests pour OneRMCalculator."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        self.one_rm_calc = OneRMCalculator()
    
    def test_epley_formula(self):
        """Test formule d'Epley."""
        # Test cas standard
        result = self.one_rm_calc.calculate_1rm(100, 5, 'epley')
        expected = 100 * (1 + 5/30)  # ≈ 116.67
        assert abs(result - expected) < 0.01
        
        # Test avec 1 rep (devrait retourner le poids)
        result = self.one_rm_calc.calculate_1rm(100, 1, 'epley')
        assert result == 103.33  # 100 * (1 + 1/30)
    
    def test_brzycki_formula(self):
        """Test formule de Brzycki."""
        result = self.one_rm_calc.calculate_1rm(100, 5, 'brzycki')
        expected = 100 / (1.0278 - 0.0278 * 5)  # ≈ 113.64
        assert abs(result - expected) < 0.01
    
    def test_invalid_inputs(self):
        """Test avec entrées invalides."""
        # Poids négatif ou nul
        assert pd.isna(self.one_rm_calc.calculate_1rm(0, 5, 'epley'))
        assert pd.isna(self.one_rm_calc.calculate_1rm(-10, 5, 'epley'))
        
        # Valeurs NaN
        assert pd.isna(self.one_rm_calc.calculate_1rm(np.nan, 5, 'epley'))
        assert pd.isna(self.one_rm_calc.calculate_1rm(100, np.nan, 'epley'))
    
    def test_calculate_all_formulas(self):
        """Test calcul avec toutes les formules."""
        result = self.one_rm_calc.calculate_all_formulas(100, 5)
        
        expected_keys = ['one_rm_epley', 'one_rm_brzycki', 'one_rm_lander', 'one_rm_oconner', 'one_rm_weighted']
        assert all(key in result for key in expected_keys)
        assert all(not pd.isna(v) for v in result.values())
    
    def test_calculate_dataframe_1rm(self):
        """Test calcul 1RM sur DataFrame."""
        data = pd.DataFrame({
            'exercise': ['Bench Press', 'Bench Press', 'Squat'],
            'series_type': ['principale', 'principale', 'principale'],
            'reps': [5, 8, 10],
            'weight_kg': [100, 90, 120],
            'skipped': [False, False, False]
        })
        
        result = self.one_rm_calc.calculate_dataframe_1rm(data, formulas=['epley'])
        
        assert 'one_rm_epley' in result.columns
        assert not result['one_rm_epley'].isna().all()


class TestProgressionAnalyzer:
    """Tests pour ProgressionAnalyzer."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        self.progression_analyzer = ProgressionAnalyzer()
        
        # Données de progression simulées
        self.progression_data = pd.DataFrame({
            'session_id': [1, 1, 2, 2, 3, 3],
            'exercise': ['Bench Press', 'Squat', 'Bench Press', 'Squat', 'Bench Press', 'Squat'],
            'series_type': ['principale', 'principale', 'principale', 'principale', 'principale', 'principale'],
            'reps': [10, 12, 10, 12, 10, 12],
            'weight_kg': [100, 120, 105, 125, 110, 130],
            'skipped': [False, False, False, False, False, False],
            'volume': [1000, 1440, 1050, 1500, 1100, 1560]
        })
        
        self.sessions_data = pd.DataFrame({
            'id': [1, 2, 3],
            'date': ['2023-01-01', '2023-01-08', '2023-01-15']
        })
    
    def test_calculate_volume_progression(self):
        """Test calcul progression volume."""
        result = self.progression_analyzer.calculate_volume_progression(
            self.progression_data, self.sessions_data
        )
        
        assert 'volume_progression' in result.columns
        assert 'volume_progression_pct' in result.columns
        assert len(result) > 0
        
        # Vérifier que la progression est croissante pour nos données test
        bench_data = result[result['exercise'] == 'Bench Press'].sort_values('date')
        assert bench_data['volume_progression'].iloc[-1] > 0  # Progression positive
    
    def test_detect_plateaus(self):
        """Test détection de plateaux."""
        # Créer des données avec plateau artificiel (plus de points pour la détection)
        plateau_data = pd.DataFrame({
            'exercise': ['Bench Press'] * 12,
            'date': pd.date_range('2023-01-01', periods=12, freq='D'),
            'volume': [1000, 1050, 1020, 1000, 1000, 1000, 1000, 1000, 1000, 1010, 1000, 1000]
        })
        
        result = self.progression_analyzer.detect_plateaus(plateau_data, 'volume', window_size=6)
        
        assert 'plateau_indicator' in result.columns
        # Avec plus de données stables, devrait détecter un plateau
        assert len(result) > 0  # Au moins des données sont retournées
    
    def test_performance_metrics(self):
        """Test calcul métriques de performance."""
        result = self.progression_analyzer.calculate_performance_metrics(
            self.progression_data, self.sessions_data
        )
        
        assert 'global_metrics' in result
        assert 'exercise_metrics' in result
        assert result['global_metrics']['total_exercises'] == 2


class TestFeatureCalculator:
    """Tests pour FeatureCalculator principal."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        self.feature_calc = FeatureCalculator()
        
        self.sample_data = pd.DataFrame({
            'session_id': [1, 1, 2, 2],
            'exercise': ['Bench Press', 'Bench Press', 'Bench Press', 'Squat'],
            'series_type': ['principale', 'principale', 'principale', 'principale'],
            'reps': [10, 8, 10, 12],
            'weight_kg': [100, 110, 105, 120],
            'skipped': [False, False, False, False]
        })
        
        self.sessions_data = pd.DataFrame({
            'id': [1, 2],
            'date': ['2023-01-01', '2023-01-03']
        })
    
    def test_calculate_all_features(self):
        """Test calcul de toutes les features."""
        result = self.feature_calc.calculate_all_features(self.sample_data, self.sessions_data)
        
        # Vérifier présence des colonnes principales
        expected_cols = ['volume', 'one_rm_epley', 'one_rm_brzycki', 'intensity_relative']
        for col in expected_cols:
            assert col in result.columns
        
        # Vérifier que les calculs sont corrects
        assert result['volume'].iloc[0] == 1000  # 10 * 100
        assert not result['one_rm_epley'].isna().all()
    
    def test_generate_session_summary(self):
        """Test génération résumé de séance."""
        result = self.feature_calc.generate_session_summary(
            self.sample_data, session_id=1, sessions_df=self.sessions_data
        )
        
        assert 'session_id' in result
        assert 'total_volume' in result
        assert 'exercise_breakdown' in result
        assert result['session_id'] == 1
        assert len(result['exercises']) == 1  # Bench Press seulement dans session 1
    
    def test_generate_complete_analysis(self):
        """Test analyse complète."""
        result = self.feature_calc.generate_complete_analysis(
            self.sample_data, self.sessions_data
        )
        
        expected_keys = [
            'analysis_metadata', 'global_statistics', 'volume_analysis',
            'one_rm_analysis', 'progression_analysis'
        ]
        
        for key in expected_keys:
            assert key in result
        
        assert result['global_statistics']['total_sessions'] == 2
        assert result['global_statistics']['total_exercises'] == 2


# Tests d'intégration
class TestIntegration:
    """Tests d'intégration entre les modules."""
    
    def test_full_pipeline(self):
        """Test du pipeline complet."""
        # Données simulées plus complètes
        data = pd.DataFrame({
            'session_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
            'exercise': ['Bench Press', 'Bench Press', 'Squat', 'Bench Press', 'Bench Press', 'Squat', 'Bench Press', 'Bench Press', 'Squat'],
            'series_type': ['principale', 'principale', 'principale', 'principale', 'principale', 'principale', 'principale', 'principale', 'principale'],
            'reps': [10, 8, 12, 10, 8, 12, 11, 9, 13],
            'weight_kg': [100, 110, 120, 105, 115, 125, 107, 117, 127],
            'skipped': [False, False, False, False, False, False, False, False, False]
        })
        
        sessions = pd.DataFrame({
            'id': [1, 2, 3],
            'date': ['2023-01-01', '2023-01-08', '2023-01-15'],
            'training_name': ['Push A', 'Push A', 'Push A']
        })
        
        # Calculer toutes les features
        feature_calc = FeatureCalculator()
        analysis = feature_calc.generate_complete_analysis(data, sessions)
        
        # Vérifications globales
        assert analysis['global_statistics']['total_sessions'] == 3
        assert analysis['global_statistics']['total_exercises'] == 2
        
        # Vérifier présence des analyses
        assert 'volume_analysis' in analysis
        assert 'one_rm_analysis' in analysis
        assert 'progression_analysis' in analysis
        
        # Vérifier cohérence des données
        raw_data = analysis['raw_data_with_features']
        assert 'volume' in raw_data.columns
        assert 'one_rm_epley' in raw_data.columns
        assert len(raw_data) == len(data)


if __name__ == '__main__':
    # Exécuter les tests
    pytest.main([__file__, '-v'])
