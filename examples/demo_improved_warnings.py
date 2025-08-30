#!/usr/bin/env python3
"""
Démonstration du système d'avertissements amélioré pour les calculs de 1RM.

Ce script montre comment le nouveau système de logging évite les avertissements
excessifs tout en conservant l'information importante pour les développeurs.
"""

import sys
import os
import logging

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.features.one_rm import OneRMCalculator


def setup_logging():
    """Configure le logging pour voir les avertissements."""
    logging.basicConfig(
        level=logging.WARNING,
        format='%(levelname)s - %(name)s - %(message)s'
    )


def demo_old_vs_new_warnings():
    """Démontre la différence entre l'ancien et le nouveau système."""
    print("=== Démonstration du système d'avertissements amélioré ===\n")
    
    setup_logging()
    
    # Calculateur avec warnings activés
    calc_with_warnings = OneRMCalculator(enable_warnings=True)
    
    # Calculateur avec warnings désactivés (pour la production)
    calc_no_warnings = OneRMCalculator(enable_warnings=False)
    
    print("1. Test avec un nombre de répétitions très élevé (40 reps)")
    print("   Ancien système: générait un warning à chaque appel")
    print("   Nouveau système: un seul warning par type de problème\n")
    
    # Premier appel - devrait logger un warning
    print("Premier appel avec Brzycki (40 reps):")
    result1 = calc_with_warnings.calculate_1rm(100, 40, 'brzycki')
    print(f"Résultat: {result1}kg (fallback vers Epley)\n")
    
    # Deuxième appel - ne devrait pas re-logger le même warning
    print("Deuxième appel avec Brzycki (40 reps):")
    result2 = calc_with_warnings.calculate_1rm(100, 40, 'brzycki')
    print(f"Résultat: {result2}kg (pas de warning répété)\n")
    
    # Test avec différent nombre de reps - devrait logger car c'est un cas différent
    print("Appel avec Brzycki (50 reps):")
    result3 = calc_with_warnings.calculate_1rm(100, 50, 'brzycki')
    print(f"Résultat: {result3}kg\n")
    
    print("2. Test avec warnings désactivés (mode production)")
    print("Calculateur avec enable_warnings=False:")
    result4 = calc_no_warnings.calculate_1rm(100, 40, 'brzycki')
    print(f"Résultat: {result4}kg (aucun warning émis)\n")
    
    print("3. Test avec différentes formules et cas limites")
    test_cases = [
        (100, 38, 'lander'),   # Limite pour Lander
        (100, 39, 'lander'),   # Au-dessus de la limite
        (100, 37, 'brzycki'),  # Limite pour Brzycki
        (100, 0, 'epley'),     # Cas spécial: 0 reps
    ]
    
    for weight, reps, formula in test_cases:
        result = calc_with_warnings.calculate_1rm(weight, reps, formula)
        print(f"{formula.capitalize()}: {weight}kg x {reps} reps = {result}kg")
    
    print("\n=== Avantages du nouveau système ===")
    print("✓ Évite le spam de warnings en production")
    print("✓ Conserve l'information importante pour le debugging")
    print("✓ Permet de désactiver complètement les warnings si nécessaire")
    print("✓ Utilise le système de logging standard de Python")
    print("✓ Différencie les premiers avertissements des répétitions")


def demo_production_usage():
    """Montre l'utilisation recommandée en production."""
    print("\n=== Utilisation recommandée en production ===\n")
    
    # Configuration pour la production
    calc_production = OneRMCalculator(enable_warnings=False)
    
    # Simuler des données d'entraînement avec beaucoup de calculs
    training_data = [
        (100, 40),  # Cas limite
        (120, 35),  # Cas limite
        (80, 45),   # Cas limite
        (100, 10),  # Cas normal
        (90, 8),    # Cas normal
    ]
    
    print("Calculs en mode production (warnings désactivés):")
    for weight, reps in training_data:
        result_epley = calc_production.calculate_1rm(weight, reps, 'epley')
        result_brzycki = calc_production.calculate_1rm(weight, reps, 'brzycki')
        print(f"{weight}kg x {reps} reps - Epley: {result_epley}kg, Brzycki: {result_brzycki}kg")
    
    print("\nAucun warning émis, même avec des cas limites répétés.")


if __name__ == '__main__':
    demo_old_vs_new_warnings()
    demo_production_usage()
