"""
Tests unitaires pour le module de normalisation.
"""

import pytest
import pandas as pd
from datetime import datetime
from src.etl.normalization import DataNormalizer, NormalizationError


class TestDataNormalizer:
    """Tests pour la classe DataNormalizer"""
    
    @pytest.fixture
    def normalizer(self):
        return DataNormalizer()
    
    @pytest.fixture
    def sample_raw_dataframe(self):
        return pd.DataFrame({
            'date': ['29/08/2025', '30/08/2025'],
            'training': ['Pecs Dos 2', 'Upper Body'],
            'time': ['16:05', '09:00'],
            'exercise': ['Traction à la Barre Fixe', 'Développé couché'],
            'region': ['Dos', 'Pectoraux'],
            'muscles_primary': ['Trapèzes, Dorsaux', 'Pectoraux'],
            'muscles_secondary': ['Biceps', 'Triceps'],
            'series_type': ['Série', 'Principale'],
            'reps': ['13 répétitions', '8'],
            'weight': ['0,00 kg', '75,5 kg'],
            'notes': ['RAS', 'Forme parfaite'],
            'skipped': ['Non', 'Non']
        })
    
    def test_normalize_dataframe_complete(self, normalizer, sample_raw_dataframe):
        """Test normalisation complète"""
        df_norm = normalizer.normalize_dataframe(sample_raw_dataframe)
        
        assert not df_norm.empty
        assert len(df_norm) == 2
        assert 'volume' in df_norm.columns
        assert 'estimated_1rm' in df_norm.columns
        assert df_norm['date'].iloc[0] == '2025-08-29'
        assert df_norm['exercise'].iloc[0] == 'pull-up'
    
    def test_normalize_date(self, normalizer):
        """Test normalisation des dates"""
        assert normalizer._normalize_date('29/08/2025') == '2025-08-29'
        assert normalizer._normalize_date('01-12-2024') == '2024-12-01'
        assert normalizer._normalize_date(datetime(2025, 8, 29)) == '2025-08-29'
        assert normalizer._normalize_date('') is None
        assert normalizer._normalize_date(None) is None
    
    def test_normalize_exercise(self, normalizer):
        """Test normalisation des exercices"""
        assert normalizer._normalize_exercise('Traction à la Barre Fixe') == 'pull-up'
        assert normalizer._normalize_exercise('Développé couché') == 'bench-press'
        assert normalizer._normalize_exercise('Squat') == 'squat'
        assert normalizer._normalize_exercise('') == 'unknown'
    
    def test_normalize_weight(self, normalizer):
        """Test normalisation des poids"""
        assert normalizer._normalize_weight('75,5 kg') == 75.5
        assert normalizer._normalize_weight('0,00 kg') == 0.0
        assert normalizer._normalize_weight(80) == 80.0
        assert normalizer._normalize_weight('') == 0.0
    
    def test_calculate_1rm(self, normalizer):
        """Test calcul 1RM"""
        row = pd.Series({'reps': 8, 'weight_kg': 80.0, 'skipped': False})
        expected = 80.0 * (1 + 8/30)
        assert abs(normalizer._calculate_1rm(row) - expected) < 0.01
        
        row_skipped = pd.Series({'reps': 8, 'weight_kg': 80.0, 'skipped': True})
        assert normalizer._calculate_1rm(row_skipped) == 0.0