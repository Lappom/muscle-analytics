"""
Muscle-Analytics - Analyse d'entraînements de musculation.

Ce package fournit des outils pour l'analyse et le suivi
des données d'entraînement de musculation.
"""

__version__ = "0.1.0"
__author__ = "Lappom"

# Imports principaux pour faciliter l'usage
from .database import get_database, DatabaseEnvironment, DatabaseManager
from .features import FeatureCalculator

__all__ = [
    'get_database', 
    'DatabaseEnvironment', 
    'DatabaseManager',
    'FeatureCalculator'
]