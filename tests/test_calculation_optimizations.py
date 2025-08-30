"""
Tests unitaires pour les optimisations de performance dans calculations.py
"""

import pytest
import pandas as pd
import numpy as np
from src.features.calculations import FeatureCalculator


class TestCalculationOptimizations:
    """Tests pour les optimisations de performance dans les calculs."""
    
    def setup_method(self):
        """Configuration pour chaque test."""
        self.calculator = FeatureCalculator()
    
    def test_calculate_estimated_set_duration_vectorized(self):
        """Test que la fonction vectorisée fonctionne correctement."""
        # Test avec Series pandas
        reps_series = pd.Series([10, 5, 15, 0, -1], name='reps')
        
        result = self.calculator.calculate_estimated_set_duration(reps_series)
        
        assert isinstance(result, pd.Series)
        assert len(result) == len(reps_series)
        
        # Vérifier que les valeurs valides sont calculées
        expected_10 = 10 * self.calculator.seconds_per_rep + self.calculator.set_rest_time
        expected_5 = 5 * self.calculator.seconds_per_rep + self.calculator.set_rest_time
        expected_15 = 15 * self.calculator.seconds_per_rep + self.calculator.set_rest_time
        
        assert result.iloc[0] == expected_10
        assert result.iloc[1] == expected_5
        assert result.iloc[2] == expected_15
        
        # Vérifier que les valeurs invalides sont NaN
        assert pd.isna(result.iloc[3])  # 0 reps
        assert pd.isna(result.iloc[4])  # -1 reps
    
    def test_calculate_estimated_set_duration_scalar(self):
        """Test que la fonction scalaire fonctionne toujours."""
        # Valeurs valides
        assert self.calculator.calculate_estimated_set_duration(10) == 10 * 4 + 60
        assert self.calculator.calculate_estimated_set_duration(5.5) == 5.5 * 4 + 60
        
        # Valeurs invalides
        assert pd.isna(self.calculator.calculate_estimated_set_duration(0))
        assert pd.isna(self.calculator.calculate_estimated_set_duration(-1))
        assert pd.isna(self.calculator.calculate_estimated_set_duration(np.nan))
    
    def test_validate_numeric_columns(self):
        """Test de la validation des colonnes numériques."""
        # Données avec types mixtes et valeurs invalides
        test_df = pd.DataFrame({
            'reps': ['10', '5', 'invalid', '-1', '0'],
            'weight_kg': [50.5, '100', 'text', -10, 0],
            'other_col': ['a', 'b', 'c', 'd', 'e']
        })
        
        result = self.calculator._validate_numeric_columns(
            test_df, ['reps', 'weight_kg']
        )
        
        # Vérifier que les colonnes sont numériques
        assert pd.api.types.is_numeric_dtype(result['reps'])
        assert pd.api.types.is_numeric_dtype(result['weight_kg'])
        
        # Vérifier les conversions
        assert result['reps'].iloc[0] == 10.0
        assert result['reps'].iloc[1] == 5.0
        assert pd.isna(result['reps'].iloc[2])  # 'invalid' → NaN
        assert pd.isna(result['reps'].iloc[3])  # '-1' → NaN (valeur négative)
        assert pd.isna(result['reps'].iloc[4])  # '0' → NaN (valeur nulle)
        
        assert result['weight_kg'].iloc[0] == 50.5
        assert result['weight_kg'].iloc[1] == 100.0
        assert pd.isna(result['weight_kg'].iloc[2])  # 'text' → NaN
        assert pd.isna(result['weight_kg'].iloc[3])  # -10 → NaN (valeur négative)
        assert pd.isna(result['weight_kg'].iloc[4])  # 0 → NaN (valeur nulle)
        
        # Vérifier que les autres colonnes ne sont pas affectées
        assert result['other_col'].equals(test_df['other_col'])
    
    def test_calculate_all_features_with_validation(self):
        """Test que les features sont calculées avec validation optimisée."""
        test_df = pd.DataFrame({
            'session_id': [1, 1, 2, 2],
            'exercise': ['squat', 'squat', 'bench', 'bench'],
            'reps': [10, 8, 12, 6],
            'weight_kg': [100, 110, 80, 85],
            'series_type': 'normal',
            'skipped': False
        })
        
        result = self.calculator.calculate_all_features(test_df, include_1rm=False)
        
        # Vérifier que les features de durée sont ajoutées
        assert 'estimated_duration_seconds' in result.columns
        assert 'estimated_duration_minutes' in result.columns
        
        # Vérifier que les calculs sont corrects
        expected_durations = [
            10 * 4 + 60,  # 10 reps
            8 * 4 + 60,   # 8 reps
            12 * 4 + 60,  # 12 reps
            6 * 4 + 60    # 6 reps
        ]
        
        for i, expected in enumerate(expected_durations):
            assert result['estimated_duration_seconds'].iloc[i] == expected
            assert result['estimated_duration_minutes'].iloc[i] == expected / 60
    
    def test_performance_with_large_dataset(self):
        """Test de performance avec un dataset plus large."""
        import time
        
        # Créer un dataset de taille moyenne
        n_rows = 5000
        large_df = pd.DataFrame({
            'session_id': np.random.randint(1, 100, n_rows),
            'exercise': np.random.choice(['squat', 'bench', 'deadlift'], n_rows),
            'reps': np.random.randint(1, 20, n_rows),
            'weight_kg': np.random.uniform(20, 150, n_rows),
            'series_type': 'normal',
            'skipped': False
        })
        
        start_time = time.time()
        result = self.calculator.calculate_all_features(large_df, include_1rm=False)
        execution_time = time.time() - start_time
        
        # Vérifier que l'exécution est rapide (moins de 1 seconde pour 5000 lignes)
        assert execution_time < 1.0, f"Execution too slow: {execution_time:.3f}s"
        
        # Vérifier que les résultats sont cohérents
        assert len(result) == n_rows
        assert 'estimated_duration_seconds' in result.columns
        assert result['estimated_duration_seconds'].notna().sum() == n_rows
    
    def test_custom_timing_parameters(self):
        """Test avec des paramètres de timing personnalisés."""
        custom_calculator = FeatureCalculator(seconds_per_rep=3.0, set_rest_time=45.0)
        
        reps_series = pd.Series([10, 5])
        result = custom_calculator.calculate_estimated_set_duration(reps_series)
        
        assert result.iloc[0] == 10 * 3.0 + 45.0  # 75 secondes
        assert result.iloc[1] == 5 * 3.0 + 45.0   # 60 secondes
