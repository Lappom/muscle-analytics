"""
Tests unitaires corrigés pour les modules de calcul de features avancées.
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
        
        # Données de test CORRIGÉES - utiliser 'working_set' au lieu de 'principale'
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
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
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
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
        assert 'volume_sum' in result.columns
        assert 'week' in result.columns
        assert len(result) > 0


class TestOneRMCalculator:
    """Tests pour OneRMCalculator."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        self.one_rm_calc = OneRMCalculator()
        
        # Données de test CORRIGÉES
        self.sample_data = pd.DataFrame({
            'session_id': [1, 1, 2, 2],
            'exercise': ['Bench Press', 'Bench Press', 'Squat', 'Squat'],
            'series_type': ['working_set', 'working_set', 'working_set', 'working_set'],
            'reps': [5, 3, 8, 6],
            'weight_kg': [100, 110, 120, 125],
            'skipped': [False, False, False, False]
        })
    
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
        # Test avec la formule Epley (qui existe)
        result = self.one_rm_calc.calculate_1rm(100, 5, 'epley')
        expected = 100 * (1 + 5/30)  # ≈ 116.67
        assert abs(result - expected) < 0.01
        
        # Test avec la formule Brzycki
        result = self.one_rm_calc.calculate_1rm(100, 5, 'brzycki')
        expected = 100 / (1.0278 - 0.0278 * 5)  # ≈ 113.64
        assert abs(result - expected) < 0.01
        
        # Test avec la formule Lander
        result = self.one_rm_calc.calculate_1rm(100, 5, 'lander')
        expected = 100 / (1.013 - 0.0267123 * 5)  # ≈ 115.38
        assert abs(result - expected) < 0.01
        
        # Test avec la formule O'Connor
        result = self.one_rm_calc.calculate_1rm(100, 5, 'oconner')
        expected = 100 * (1 + 0.025 * 5)  # ≈ 112.5
        assert abs(result - expected) < 0.01
    
    def test_calculate_dataframe_1rm(self):
        """Test calcul 1RM sur DataFrame."""
        result = self.one_rm_calc.calculate_dataframe_1rm(self.sample_data)
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
        assert 'one_rm_epley' in result.columns
        assert 'one_rm_brzycki' in result.columns
        
        # Vérifier que les valeurs 1RM sont calculées correctement
        assert not result['one_rm_epley'].isna().all(), "Les valeurs 1RM Epley ne devraient pas être toutes NaN"
        assert not result['one_rm_brzycki'].isna().all(), "Les valeurs 1RM Brzycki ne devraient pas être toutes NaN"
    
    def test_get_max_1rm_by_exercise(self):
        """Test obtention du 1RM maximum par exercice."""
        # D'abord calculer les 1RM
        data_with_1rm = self.one_rm_calc.calculate_dataframe_1rm(self.sample_data)
        result = self.one_rm_calc.get_max_1rm_by_exercise(data_with_1rm)
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
        assert 'exercise' in result.columns
        assert 'one_rm_epley' in result.columns
        assert 'one_rm_brzycki' in result.columns
        
        # Vérifier qu'il y a des valeurs non-NaN
        assert not result['one_rm_epley'].isna().all(), "Les valeurs 1RM Epley ne devraient pas être toutes NaN"


class TestProgressionAnalyzer:
    """Tests pour ProgressionAnalyzer."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        self.prog_analyzer = ProgressionAnalyzer()
        
        # Données de test CORRIGÉES avec dates
        self.sample_data = pd.DataFrame({
            'session_id': [1, 1, 2, 2, 3, 3],
            'exercise': ['Bench Press', 'Bench Press', 'Bench Press', 'Bench Press', 'Bench Press', 'Bench Press'],
            'series_type': ['working_set', 'working_set', 'working_set', 'working_set', 'working_set', 'working_set'],
            'reps': [10, 8, 10, 8, 10, 8],
            'weight_kg': [100, 110, 105, 115, 110, 120],
            'skipped': [False, False, False, False, False, False],
            'volume': [1000, 880, 1050, 920, 1100, 960]
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
    
    def test_performance_metrics(self):
        """Test calcul métriques de performance."""
        result = self.prog_analyzer.calculate_performance_metrics(
            self.sample_data, self.sessions_data
        )
        
        assert 'global_metrics' in result
        assert 'exercise_metrics' in result
        assert result['global_metrics']['total_exercises'] == 1  # Un seul exercice dans nos données


class TestFeatureCalculator:
    """Tests pour FeatureCalculator."""
    
    def setup_method(self):
        """Setup avant chaque test."""
        self.feature_calc = FeatureCalculator()
        
        # Données de test CORRIGÉES
        self.sample_data = pd.DataFrame({
            'session_id': [1, 1, 2, 2],
            'exercise': ['Bench Press', 'Bench Press', 'Squat', 'Squat'],
            'series_type': ['working_set', 'working_set', 'working_set', 'working_set'],
            'reps': [10, 8, 12, 10],
            'weight_kg': [100, 110, 120, 125],
            'skipped': [False, False, False, False]
        })
        
        self.sessions_data = pd.DataFrame({
            'id': [1, 2],
            'date': ['2023-01-01', '2023-01-08']
        })
    
    def test_calculate_all_features(self):
        """Test calcul de toutes les features."""
        result = self.feature_calc.calculate_all_features(
            self.sample_data, 
            self.sessions_data
        )
        
        # Vérifier que le résultat n'est pas vide
        assert not result.empty, "Le résultat ne devrait pas être vide"
        
        # Vérifier que les colonnes principales sont présentes
        expected_columns = ['session_id', 'exercise', 'volume', 'one_rm_epley']
        for col in expected_columns:
            assert col in result.columns, f"La colonne {col} devrait être présente"
    
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
