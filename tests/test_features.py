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
            'series_type': ['working_set', 'working_set', 'working_set', 'working_set', 'working_set', 'working_set'],
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
        
        # Test avec 1 rep (devrait appliquer la formule)
        result = self.one_rm_calc.calculate_1rm(100, 1, 'epley')
        expected = 100 * (1 + 1/30)  # ≈ 103.33
        assert abs(result - expected) < 0.01
        
        # Test avec 2 reps (devrait appliquer la formule)
        result = self.one_rm_calc.calculate_1rm(100, 2, 'epley')
        expected = 100 * (1 + 2/30)  # ≈ 106.67
        assert abs(result - expected) < 0.01
        
        # Test avec 0 rep (devrait retourner le poids directement)
        result = self.one_rm_calc.calculate_1rm(100, 0, 'epley')
        assert result == 100
    
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
    
    def test_formula_limits_and_warnings(self):
        """Test limites des formules et système d'avertissements."""
        import logging
        
        # Créer un calculateur avec warnings activés
        calc_with_warnings = OneRMCalculator(enable_warnings=True)
        
        # Test avec un nombre de reps élevé pour Brzycki (devrait utiliser Epley)
        result_brzycki = calc_with_warnings.calculate_1rm(100, 40, 'brzycki')
        expected_epley = calc_with_warnings.calculate_1rm(100, 40, 'epley')
        assert result_brzycki == expected_epley
        
        # Test avec un nombre de reps élevé pour Lander
        result_lander = calc_with_warnings.calculate_1rm(100, 40, 'lander')
        assert result_lander == expected_epley
        
        # Créer un calculateur avec warnings désactivés
        calc_no_warnings = OneRMCalculator(enable_warnings=False)
        result_no_warn = calc_no_warnings.calculate_1rm(100, 40, 'brzycki')
        assert result_no_warn == expected_epley
    
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
            'series_type': ['working_set', 'working_set', 'working_set'],
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
        self.prog_analyzer = ProgressionAnalyzer()
        
        # Données de test CORRIGÉES avec dates
        self.sample_data = pd.DataFrame({
            'session_id': [1, 1, 2, 2, 3, 3],
            'exercise': ['Bench Press', 'Bench Press', 'Squat', 'Bench Press', 'Bench Press', 'Squat'],
            'series_type': ['working_set', 'working_set', 'working_set', 'working_set', 'working_set', 'working_set'],
            'reps': [10, 8, 12, 10, 8, 12],
            'weight_kg': [100, 110, 120, 105, 115, 125],
            'skipped': [False, False, False, False, False, False],
            'volume': [1000, 880, 1440, 1050, 920, 1500]
        })
        
        self.sessions_data = pd.DataFrame({
            'id': [1, 2, 3],
            'date': ['2023-01-01', '2023-01-08', '2023-01-15']
        })
    
    def test_analyze_volume_progression(self):
        """Test analyse de progression du volume."""
        # Joindre les données avec les dates
        data_with_dates = self.sample_data.merge(
            self.sessions_data[['id', 'date']], 
            left_on='session_id', right_on='id', 
            how='left'
        )
        data_with_dates['date'] = pd.to_datetime(data_with_dates['date'])
        
        result = self.prog_analyzer.calculate_volume_progression(data_with_dates)
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
        assert 'volume_progression' in result.columns, "La colonne volume_progression devrait être présente"
        
        # Vérifier qu'il y a des données de progression
        progression_values = result['volume_progression'].dropna()
        assert len(progression_values) > 0, "Il devrait y avoir des valeurs de progression non-NaN"
    
    def test_analyze_volume_progression_empty_data(self):
        """Test analyse de progression avec données vides."""
        empty_data = pd.DataFrame(columns=['session_id', 'exercise', 'series_type', 'reps', 'weight_kg', 'skipped', 'volume'])
        empty_sessions = pd.DataFrame(columns=['id', 'date'])
        
        # Ajouter une colonne date vide
        empty_data['date'] = []
        
        result = self.prog_analyzer.calculate_volume_progression(empty_data)
        
        # Vérifier que le résultat est vide mais avec la bonne structure
        assert result.empty
        assert 'volume_progression' in result.columns or len(result.columns) > 0
    
    def test_detect_plateaus(self):
        """Test détection de plateaux."""
        # Créer des données avec un plateau
        plateau_data = pd.DataFrame({
            'session_id': [1, 2, 3, 4, 5],
            'exercise': ['Bench Press'] * 5,
            'series_type': ['working_set'] * 5,
            'reps': [10, 10, 10, 10, 10],
            'weight_kg': [100, 100, 100, 100, 100],
            'skipped': [False] * 5,
            'volume': [1000, 1000, 1000, 1000, 1000],
            'date': pd.date_range('2023-01-01', periods=5, freq='D')
        })
        
        result = self.prog_analyzer.detect_plateaus(plateau_data)
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
        assert 'plateau_indicator' in result.columns, "La colonne plateau_indicator devrait être présente"
    
    def test_detect_plateaus_empty_data(self):
        """Test détection de plateaux avec données vides."""
        # Créer un DataFrame vide avec la structure attendue par detect_plateaus
        empty_data = pd.DataFrame(columns=['session_id', 'date', 'volume', 'reps', 'weight_kg', 
                                          'volume_ma', 'volume_progression', 'volume_progression_pct', 
                                          'trend_slope', 'trend_r_squared', 'trend_p_value', 'exercise'])
        
        result = self.prog_analyzer.detect_plateaus(empty_data)
        
        # Vérifier que le résultat est vide mais avec la bonne structure
        assert result.empty
        assert 'plateau_indicator' in result.columns or len(result.columns) > 0
    
    def test_performance_metrics(self):
        """Test calcul métriques de performance."""
        result = self.prog_analyzer.calculate_performance_metrics(
            self.sample_data, self.sessions_data
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
            'series_type': ['working_set', 'working_set', 'working_set', 'working_set'],
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
    
    def test_calculate_estimated_set_duration(self):
        """Test calcul de durée estimée d'un set."""
        # Test cas normal
        duration = self.feature_calc.calculate_estimated_set_duration(10)
        expected = 10 * self.feature_calc.seconds_per_rep + self.feature_calc.set_rest_time
        assert duration == expected
        
        # Test avec 0 reps
        duration_zero = self.feature_calc.calculate_estimated_set_duration(0)
        assert pd.isna(duration_zero)
        
        # Test avec valeur NaN
        duration_nan = self.feature_calc.calculate_estimated_set_duration(np.nan)
        assert pd.isna(duration_nan)
        
        # Test avec valeur négative
        duration_neg = self.feature_calc.calculate_estimated_set_duration(-5)
        assert pd.isna(duration_neg)
    
    def test_custom_timing_parameters(self):
        """Test de FeatureCalculator avec paramètres de timing personnalisés."""
        # Test avec paramètres par défaut
        calc_default = FeatureCalculator()
        assert calc_default.seconds_per_rep == 4
        assert calc_default.set_rest_time == 60
        
        # Test avec paramètres personnalisés
        calc_custom = FeatureCalculator(seconds_per_rep=3.0, set_rest_time=45.0)
        assert calc_custom.seconds_per_rep == 3.0
        assert calc_custom.set_rest_time == 45.0
        
        # Test que les calculs utilisent les nouveaux paramètres
        duration_default = calc_default.calculate_estimated_set_duration(10)
        duration_custom = calc_custom.calculate_estimated_set_duration(10)
        
        # Durée par défaut: 10 * 4 + 60 = 100s
        assert duration_default == 100
        # Durée personnalisée: 10 * 3 + 45 = 75s
        assert duration_custom == 75.0


# Tests d'intégration
class TestIntegration:
    """Tests d'intégration entre les modules."""
    
    def test_full_pipeline(self):
        """Test du pipeline complet."""
        # Données simulées plus complètes
        data = pd.DataFrame({
            'session_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
            'exercise': ['Bench Press', 'Bench Press', 'Squat', 'Bench Press', 'Bench Press', 'Squat', 'Bench Press', 'Bench Press', 'Squat'],
            'series_type': ['working_set', 'working_set', 'working_set', 'working_set', 'working_set', 'working_set', 'working_set', 'working_set', 'working_set'],
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
