"""
Tests unitaires pour les méthodes d'extraction refactorisées dans services.py
"""

import pytest
import pandas as pd
import numpy as np
from src.api.services import AnalyticsService, DatabaseService
from unittest.mock import Mock


class TestSafeExtractionMethods:
    """Tests pour les méthodes d'extraction sécurisées refactorisées."""
    
    def setup_method(self):
        """Configuration pour chaque test."""
        # Mock du DatabaseService pour les tests
        mock_db_service = Mock(spec=DatabaseService)
        self.analytics_service = AnalyticsService(mock_db_service)
    
    def test_safe_extract_value_generic(self):
        """Test de la méthode générique _safe_extract_value."""
        # DataFrame de test avec différents types de données
        test_df = pd.DataFrame({
            'float_col': [1.5, 2.7, 3.9],
            'int_col': [10, 20, 30],
            'bool_col': [True, False, True],
            'str_col': ['a', 'b', 'c'],
            'mixed_col': [1, 'text', 3.5],
            'nan_col': [1.0, np.nan, 3.0]
        })
        
        # Test extraction float (dernière valeur)
        result = self.analytics_service._safe_extract_value(
            test_df, 'float_col', float, use_max=False, default=None
        )
        assert result == 3.9
        
        # Test extraction float (valeur max)
        result = self.analytics_service._safe_extract_value(
            test_df, 'float_col', float, use_max=True, default=None
        )
        assert result == 3.9
        
        # Test extraction int
        result = self.analytics_service._safe_extract_value(
            test_df, 'int_col', int, use_max=False, default=None
        )
        assert result == 30
        
        # Test extraction bool
        result = self.analytics_service._safe_extract_value(
            test_df, 'bool_col', bool, use_max=False, default=False
        )
        assert result is True
        
        # Test extraction string
        result = self.analytics_service._safe_extract_value(
            test_df, 'str_col', str, use_max=False, default=None
        )
        assert result == 'c'
        
        # Test colonne inexistante
        result = self.analytics_service._safe_extract_value(
            test_df, 'nonexistent', float, use_max=False, default=999.0
        )
        assert result == 999.0
        
        # Test DataFrame vide
        empty_df = pd.DataFrame()
        result = self.analytics_service._safe_extract_value(
            empty_df, 'any_col', float, use_max=False, default=555.0
        )
        assert result == 555.0
        
        # Test valeur NaN (nan_col a comme dernière valeur 3.0, pas NaN)
        result = self.analytics_service._safe_extract_value(
            test_df, 'nan_col', float, use_max=False, default=111.0
        )
        assert result == 3.0  # Dernière valeur est 3.0
        
        # Créons un test spécifique pour NaN en dernière position
        nan_test_df = pd.DataFrame({'test_col': [1.0, 2.0, np.nan]})
        result = self.analytics_service._safe_extract_value(
            nan_test_df, 'test_col', float, use_max=False, default=111.0
        )
        assert result == 111.0
    
    def test_safe_extract_float(self):
        """Test de la méthode _safe_extract_float refactorisée."""
        test_df = pd.DataFrame({
            'values': [1.5, 2.7, 3.9, 2.1]
        })
        
        # DataFrame séparé avec NaN pour éviter les problèmes de taille
        nan_df = pd.DataFrame({
            'with_nan': [1.0, np.nan, 3.0]
        })
        
        # Test extraction normale (dernière valeur)
        result = self.analytics_service._safe_extract_float(test_df, 'values')
        assert result == 2.1
        
        # Test extraction max
        result = self.analytics_service._safe_extract_float(test_df, 'values', use_max=True)
        assert result == 3.9
        
        # Test colonne inexistante
        result = self.analytics_service._safe_extract_float(test_df, 'nonexistent')
        assert result is None
        
        # Test avec NaN en dernière position
        test_nan_df = pd.DataFrame({'test': [1.0, 2.0, np.nan]})
        result = self.analytics_service._safe_extract_float(test_nan_df, 'test')
        assert result is None
    
    def test_safe_extract_int(self):
        """Test de la méthode _safe_extract_int refactorisée."""
        test_df = pd.DataFrame({
            'integers': [10, 20, 30],
            'floats_convertible': [1.0, 2.0, 3.0]
        })
        
        # Test extraction int normale
        result = self.analytics_service._safe_extract_int(test_df, 'integers')
        assert result == 30
        assert isinstance(result, int)
        
        # Test conversion float vers int
        result = self.analytics_service._safe_extract_int(test_df, 'floats_convertible')
        assert result == 3
        assert isinstance(result, int)
        
        # Test colonne inexistante
        result = self.analytics_service._safe_extract_int(test_df, 'nonexistent')
        assert result is None
    
    def test_safe_extract_bool(self):
        """Test de la méthode _safe_extract_bool refactorisée."""
        test_df = pd.DataFrame({
            'booleans': [True, False, True],
            'integers': [0, 1, 0],
            'strings': ['false', 'true', 'yes']
        })
        
        # Test extraction bool normale
        result = self.analytics_service._safe_extract_bool(test_df, 'booleans')
        assert result is True
        
        # Test conversion int vers bool
        result = self.analytics_service._safe_extract_bool(test_df, 'integers')
        assert result is False  # 0 → False
        
        # Test avec valeur par défaut
        result = self.analytics_service._safe_extract_bool(test_df, 'nonexistent', default=True)
        assert result is True
        
        # Test conversion string vers bool
        result = self.analytics_service._safe_extract_bool(test_df, 'strings')
        assert result is True  # 'yes' → True (non-empty string)
    
    def test_safe_extract_str(self):
        """Test de la méthode _safe_extract_str refactorisée."""
        test_df = pd.DataFrame({
            'strings': ['hello', 'world', 'test'],
            'numbers': [123, 456, 789],
            'mixed': [1, 'text', 3.14]
        })
        
        # Test extraction string normale
        result = self.analytics_service._safe_extract_str(test_df, 'strings')
        assert result == 'test'
        assert isinstance(result, str)
        
        # Test conversion number vers string
        result = self.analytics_service._safe_extract_str(test_df, 'numbers')
        assert result == '789'
        assert isinstance(result, str)
        
        # Test conversion valeur mixte vers string
        result = self.analytics_service._safe_extract_str(test_df, 'mixed')
        assert result == '3.14'
        
        # Test colonne inexistante
        result = self.analytics_service._safe_extract_str(test_df, 'nonexistent')
        assert result is None
    
    def test_error_handling(self):
        """Test de la gestion d'erreurs lors des conversions."""
        # DataFrame avec des valeurs problématiques
        test_df = pd.DataFrame({
            'problematic': ['not_a_number', 'still_not_a_number', 'nope']
        })
        
        # Test conversion impossible vers float
        result = self.analytics_service._safe_extract_float(test_df, 'problematic')
        assert result is None
        
        # Test conversion impossible vers int  
        result = self.analytics_service._safe_extract_int(test_df, 'problematic')
        assert result is None
        
        # Test avec valeur par défaut personnalisée
        result = self.analytics_service._safe_extract_value(
            test_df, 'problematic', float, use_max=False, default=999.0
        )
        assert result == 999.0
    
    def test_consistency_with_original_behavior(self):
        """Test que le comportement est identique à l'ancienne implémentation."""
        test_df = pd.DataFrame({
            'test_col': [1.1, 2.2, 3.3]
        })
        
        # Les méthodes spécialisées doivent donner les mêmes résultats
        # que la méthode générique avec les bons paramètres
        
        generic_float = self.analytics_service._safe_extract_value(
            test_df, 'test_col', float, use_max=False, default=None
        )
        specialized_float = self.analytics_service._safe_extract_float(test_df, 'test_col')
        assert generic_float == specialized_float
        
        generic_int = self.analytics_service._safe_extract_value(
            test_df, 'test_col', int, use_max=False, default=None
        )
        specialized_int = self.analytics_service._safe_extract_int(test_df, 'test_col')
        assert generic_int == specialized_int
        
        generic_str = self.analytics_service._safe_extract_value(
            test_df, 'test_col', str, use_max=False, default=None
        )
        specialized_str = self.analytics_service._safe_extract_str(test_df, 'test_col')
        assert generic_str == specialized_str
