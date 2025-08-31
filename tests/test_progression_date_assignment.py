#!/usr/bin/env python3
"""
Tests pour la fonction d'assignation de dates par défaut dans ProgressionAnalyzer

Ces tests vérifient que la logique d'assignation de dates par défaut
fonctionne correctement quand les vraies dates ne sont pas disponibles.
"""

import unittest
import unittest.mock
import pandas as pd
import sys
from pathlib import Path

# Ajouter les chemins pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from features.progression import ProgressionAnalyzer, DEFAULT_START_DATE, DEFAULT_DATE_SPACING


class TestProgressionDateAssignment(unittest.TestCase):
    """Tests pour l'assignation de dates par défaut"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.analyzer = ProgressionAnalyzer()
        
        # Données de test avec session_id
        self.test_data_with_sessions = pd.DataFrame({
            'session_id': [3, 1, 2, 4, 1, 3, 2],
            'exercise': ['Squat', 'Squat', 'Squat', 'Squat', 'Bench', 'Bench', 'Bench'],
            'weight_kg': [100, 80, 90, 110, 60, 65, 70],
            'reps': [5, 5, 5, 5, 5, 5, 5]
        })
        
        # Données de test sans session_id
        self.test_data_without_sessions = pd.DataFrame({
            'exercise': ['Squat', 'Bench', 'Deadlift'],
            'weight_kg': [100, 80, 120],
            'reps': [5, 5, 5]
        })

    def test_assign_proxy_dates_with_session_id(self):
        """Test que les dates par défaut sont assignées correctement avec session_id"""
        result = self.analyzer._assign_proxy_dates(self.test_data_with_sessions)
        
        # Vérifier que la colonne date a été ajoutée
        self.assertIn('date', result.columns)
        
        # Vérifier que toutes les lignes ont une date
        self.assertFalse(result['date'].isna().any())
        
        # Vérifier que les dates sont des timestamps pandas
        self.assertTrue(all(isinstance(date, pd.Timestamp) for date in result['date']))
        
        # Vérifier que les sessions ont des dates consécutives
        unique_sessions = sorted(self.test_data_with_sessions['session_id'].unique())
        expected_dates = [
            DEFAULT_START_DATE + (i * DEFAULT_DATE_SPACING)
            for i in range(len(unique_sessions))
        ]
        
        for session_id, expected_date in zip(unique_sessions, expected_dates):
            session_data = result[result['session_id'] == session_id]
            self.assertTrue(all(session_data['date'] == expected_date))

    def test_assign_proxy_dates_without_session_id(self):
        """Test que la date actuelle est assignée quand pas de session_id"""
        # Mock de pd.Timestamp.now() pour un test déterministe
        with unittest.mock.patch('pandas.Timestamp.now') as mock_now:
            mock_now.return_value = pd.Timestamp('2023-01-01 12:00:00')
            
            result = self.analyzer._assign_proxy_dates(self.test_data_without_sessions)
            
            # Vérifier que la colonne date a été ajoutée
            self.assertIn('date', result.columns)
            
            # Vérifier que toutes les lignes ont la même date (date actuelle)
            unique_dates = result['date'].unique()
            self.assertEqual(len(unique_dates), 1)
            
            # Vérifier que la date est celle du mock
            expected_date = pd.Timestamp('2023-01-01 12:00:00')
            self.assertEqual(unique_dates[0], expected_date)

    def test_assign_proxy_dates_maintains_order(self):
        """Test que l'ordre temporel relatif est maintenu"""
        # Créer des données avec des sessions dans un ordre spécifique
        ordered_data = pd.DataFrame({
            'session_id': [10, 5, 20, 1],
            'exercise': ['Squat'] * 4,
            'weight_kg': [100, 90, 110, 80],
            'reps': [5] * 4
        })
        
        result = self.analyzer._assign_proxy_dates(ordered_data)
        
        # Vérifier que les sessions sont triées par session_id
        session_dates = {}
        for session_id in ordered_data['session_id']:
            session_data = result[result['session_id'] == session_id]
            session_dates[session_id] = session_data['date'].iloc[0]
        
        # Vérifier que les dates sont dans l'ordre croissant
        sorted_sessions = sorted(ordered_data['session_id'])
        sorted_dates = [session_dates[sid] for sid in sorted_sessions]
        
        for i in range(1, len(sorted_dates)):
            self.assertGreater(sorted_dates[i], sorted_dates[i-1])

    def test_assign_proxy_dates_empty_dataframe(self):
        """Test avec un DataFrame vide"""
        empty_df = pd.DataFrame()
        result = self.analyzer._assign_proxy_dates(empty_df)
        
        # Vérifier que le résultat est un DataFrame vide
        self.assertTrue(result.empty)
        # Vérifier que la colonne date est présente
        self.assertIn('date', result.columns)

    def test_assign_proxy_dates_single_session(self):
        """Test avec une seule session"""
        single_session_data = pd.DataFrame({
            'session_id': [1],
            'exercise': ['Squat'],
            'weight_kg': [100],
            'reps': [5]
        })
        
        result = self.analyzer._assign_proxy_dates(single_session_data)
        
        # Vérifier que la date assignée est DEFAULT_START_DATE
        expected_date = DEFAULT_START_DATE
        self.assertEqual(result['date'].iloc[0], expected_date)

    def test_assign_proxy_dates_duplicate_sessions(self):
        """Test avec des sessions dupliquées"""
        duplicate_data = pd.DataFrame({
            'session_id': [1, 1, 2, 2, 1],
            'exercise': ['Squat'] * 5,
            'weight_kg': [100, 105, 110, 115, 120],
            'reps': [5] * 5
        })
        
        result = self.analyzer._assign_proxy_dates(duplicate_data)
        
        # Vérifier que toutes les lignes d'une même session ont la même date
        session_1_data = result[result['session_id'] == 1]
        session_2_data = result[result['session_id'] == 2]
        
        self.assertTrue(all(session_1_data['date'] == session_1_data['date'].iloc[0]))
        self.assertTrue(all(session_2_data['date'] == session_2_data['date'].iloc[0]))
        
        # Vérifier que les dates sont différentes entre sessions
        self.assertNotEqual(session_1_data['date'].iloc[0], session_2_data['date'].iloc[0])

    def test_constants_are_defined(self):
        """Test que les constantes sont définies correctement"""
        # Vérifier que DEFAULT_START_DATE est un Timestamp
        self.assertIsInstance(DEFAULT_START_DATE, pd.Timestamp)
        
        # Vérifier que DEFAULT_DATE_SPACING est un Timedelta
        self.assertIsInstance(DEFAULT_DATE_SPACING, pd.Timedelta)
        
        # Vérifier que DEFAULT_DATE_SPACING est de 1 jour
        self.assertEqual(DEFAULT_DATE_SPACING, pd.Timedelta(days=1))
        
        # Vérifier que DEFAULT_START_DATE est le 1er janvier 2024
        expected_date = pd.Timestamp('2024-01-01')
        self.assertEqual(DEFAULT_START_DATE, expected_date)


if __name__ == '__main__':
    # Configuration des tests
    unittest.main(verbosity=2)
