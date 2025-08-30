"""
Module de calcul des features avancées pour l'analyse de musculation.
"""

from .calculations import FeatureCalculator
from .one_rm import OneRMCalculator
from .progression import ProgressionAnalyzer
from .volume import VolumeCalculator

__all__ = [
    'FeatureCalculator',
    'OneRMCalculator', 
    'ProgressionAnalyzer',
    'VolumeCalculator'
]
