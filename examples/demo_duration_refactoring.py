#!/usr/bin/env python3
"""
Démonstration des améliorations de la méthode calculate_estimated_set_duration.

Ce script montre comment la refactorisation améliore la testabilité et la réutilisabilité
du calcul de durée des sets.
"""

import sys
import os
import pandas as pd
import numpy as np

# Ajouter le chemin src pour les imports
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(project_root)

from src.features.calculations import FeatureCalculator


def demo_refactored_duration_calculation():
    """Démontre les avantages de la méthode refactorisée."""
    print("=== Démonstration de la refactorisation du calcul de durée ===\n")
    
    # Créer le calculateur
    feature_calc = FeatureCalculator()
    
    print("1. Test de la méthode isolée (facilite le debugging)")
    print("   Constantes utilisées:")
    print(f"   - SECONDS_PER_REP: {feature_calc.SECONDS_PER_REP} secondes")
    print(f"   - SET_REST_TIME: {feature_calc.SET_REST_TIME} secondes")
    print()
    
    # Test avec différentes valeurs
    test_reps = [5, 8, 10, 12, 15]
    print("   Tests unitaires de la méthode:")
    for reps in test_reps:
        duration = feature_calc.calculate_estimated_set_duration(reps)
        print(f"   {reps} reps → {duration} secondes ({duration/60:.1f} minutes)")
    
    print()
    
    # Test des cas limites
    print("2. Gestion des cas limites (valeurs invalides)")
    edge_cases = [0, -5, np.nan, None]
    for case in edge_cases:
        try:
            duration = feature_calc.calculate_estimated_set_duration(case)
            status = "NaN" if pd.isna(duration) else f"{duration} sec"
            print(f"   {case} reps → {status}")
        except Exception as e:
            print(f"   {case} reps → Erreur: {e}")
    
    print()
    
    print("3. Utilisation dans le calcul des features (réutilisabilité)")
    
    # Créer des données d'exemple
    sample_data = pd.DataFrame({
        'session_id': [1, 1, 1, 1],
        'exercise': ['Bench Press', 'Bench Press', 'Squat', 'Squat'],
        'series_type': ['principale', 'principale', 'principale', 'principale'],
        'reps': [10, 8, 12, 6],
        'weight_kg': [100, 110, 120, 130],
        'skipped': [False, False, False, False]
    })
    
    # Calculer les features (qui utilise maintenant la méthode refactorisée)
    df_with_features = feature_calc.calculate_all_features(sample_data)
    
    print("   Données avec durées calculées:")
    result_cols = ['exercise', 'reps', 'estimated_set_duration', 'volume_density']
    print(df_with_features[result_cols].to_string(index=False))
    print()
    
    print("4. Avantages de la refactorisation:")
    print("   ✓ Méthode testable indépendamment")
    print("   ✓ Logique de calcul centralisée")
    print("   ✓ Gestion cohérente des cas limites")
    print("   ✓ Réutilisable dans d'autres contextes")
    print("   ✓ Facilite la modification des paramètres")
    print()


def demo_custom_duration_calculation():
    """Montre comment personnaliser le calcul de durée."""
    print("=== Personnalisation du calcul de durée ===\n")
    
    class CustomFeatureCalculator(FeatureCalculator):
        """Calculateur avec paramètres de durée personnalisés."""
        
        # Paramètres pour un entraînement plus intensif
        SECONDS_PER_REP = 2.0     # Répétitions plus rapides
        SET_REST_TIME = 45        # Repos plus court
    
    # Comparaison entre calculateurs standard et personnalisé
    standard_calc = FeatureCalculator()
    custom_calc = CustomFeatureCalculator()
    
    print("Comparaison des durées calculées:")
    print("Reps | Standard | Personnalisé | Différence")
    print("-" * 45)
    
    for reps in [8, 10, 12]:
        duration_std = standard_calc.calculate_estimated_set_duration(reps)
        duration_custom = custom_calc.calculate_estimated_set_duration(reps)
        diff = duration_std - duration_custom
        
        print(f"{reps:4d} | {duration_std:8.1f} | {duration_custom:12.1f} | {diff:+9.1f}")
    
    print("\nAvantage: paramètres facilement modifiables pour différents styles d'entraînement")
    print()


def demo_testing_advantages():
    """Démontre les avantages pour les tests unitaires."""
    print("=== Avantages pour les tests unitaires ===\n")
    
    feature_calc = FeatureCalculator()
    
    print("Tests simples et ciblés possibles:")
    print()
    
    # Exemple de tests unitaires
    test_cases = [
        {"reps": 10, "expected": 10 * 2.5 + 60, "description": "Cas normal"},
        {"reps": 0, "expected": np.nan, "description": "Zéro répétitions"},
        {"reps": -5, "expected": np.nan, "description": "Répétitions négatives"},
        {"reps": np.nan, "expected": np.nan, "description": "Valeur NaN"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        result = feature_calc.calculate_estimated_set_duration(test["reps"])
        
        if pd.isna(test["expected"]):
            success = pd.isna(result)
            expected_str = "NaN"
            result_str = "NaN" if pd.isna(result) else str(result)
        else:
            success = abs(result - test["expected"]) < 0.001
            expected_str = f"{test['expected']}"
            result_str = f"{result}"
        
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{i}. {test['description']}")
        print(f"   Attendu: {expected_str}")
        print(f"   Obtenu:  {result_str}")
        print(f"   {status}")
        print()
    
    print("Avec la méthode extraite, ces tests sont rapides et fiables !")


def main():
    """Fonction principale pour exécuter toutes les démonstrations."""
    print("🔧 DÉMONSTRATION DE LA REFACTORISATION - CALCUL DE DURÉE")
    print("=" * 65)
    print()
    
    try:
        demo_refactored_duration_calculation()
        demo_custom_duration_calculation()
        demo_testing_advantages()
        
        print("✅ Toutes les démonstrations ont été exécutées avec succès!")
        print("\n" + "=" * 65)
        print("RÉSUMÉ DES AMÉLIORATIONS:")
        print("• Extraction de la logique de calcul dans une méthode dédiée")
        print("• Amélioration de la testabilité et du debugging")
        print("• Centralisation de la gestion des cas limites")
        print("• Facilitation de la personnalisation des paramètres")
        print("• Code plus maintenable et réutilisable")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
