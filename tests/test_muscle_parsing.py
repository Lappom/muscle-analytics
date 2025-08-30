#!/usr/bin/env python3
"""
Test rapide pour valider la nouvelle méthode _parse_muscle_list
"""

import pandas as pd

from src.database import DatabaseManager

def test_parse_muscle_list():
    """Test de la méthode _parse_muscle_list"""
    
    # Créer une instance (sans vraie connexion DB)
    db = DatabaseManager()
    
    # Tests avec différentes valeurs
    test_cases = [
        ("biceps, triceps, deltoid", ["biceps", "triceps", "deltoid"]),
        ("quadriceps", ["quadriceps"]),
        ("", []),
        (None, []),
        (pd.NA, []),
        (float('nan'), []),
        (123, []),
        ("  ", ["  "]),  # String avec espaces seulement
    ]
    
    print("Test de la méthode _parse_muscle_list:")
    print("=" * 50)
    
    for i, (input_val, expected) in enumerate(test_cases, 1):
        try:
            result = db._parse_muscle_list(input_val)
            status = "✓ PASS" if result == expected else "✗ FAIL"
            print(f"Test {i}: {status}")
            print(f"  Input: {repr(input_val)}")
            print(f"  Expected: {expected}")
            print(f"  Got: {result}")
            print()
        except Exception as e:
            print(f"Test {i}: ✗ ERROR - {e}")
            print(f"  Input: {repr(input_val)}")
            print()

if __name__ == "__main__":
    test_parse_muscle_list()
