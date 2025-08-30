#!/usr/bin/env python3
"""
Exemple d'utilisation de l'import ETL avec date de référence configurable.

Ce script démontre comment rendre les imports déterministes en injectant
une date de référence, particulièrement utile pour les tests et l'environnement
de développement.
"""

import sys
from pathlib import Path
from datetime import date

# Ajouter le dossier src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from etl.import_scripts import ETLImporter

def demo_deterministic_import():
    """Démonstration d'import avec date de référence configurable"""
    
    print("=== Démonstration d'Import ETL Déterministe ===\n")
    
    # Initialiser l'importateur
    importer = ETLImporter()
    
    # Date de référence fixe pour la démonstration
    reference_date = date(2024, 8, 31)
    
    print(f"📅 Date de référence configurée: {reference_date}")
    print("🎯 Avantages:")
    print("   - Import déterministe (reproductible)")
    print("   - Tests fiables et cohérents")
    print("   - Simulations avec dates spécifiques")
    print()
    
    # Exemple d'utilisation avec date de référence
    file_path = Path("examples/sample_data.csv")
    
    if file_path.exists():
        print(f"📂 Import incrémental de: {file_path}")
        
        # Import avec date de référence (déterministe)
        result = importer.incremental_import(
            file_path, 
            days_threshold=30,
            reference_date=reference_date  # Date configurable !
        )
        
        if result['success']:
            print("✅ Import réussi!")
            stats = result.get('stats', {})
            print(f"   - Nouvelles données trouvées: {stats.get('new_data_found', False)}")
            print(f"   - Lignes originales: {stats.get('original_rows', 0)}")
            print(f"   - Nouvelles lignes: {stats.get('new_rows', 0)}")
        else:
            print(f"❌ Échec de l'import: {result.get('message', 'Erreur inconnue')}")
            
    else:
        print(f"⚠️  Fichier non trouvé: {file_path}")
        print("   Créez d'abord un fichier de test avec demo_etl.py")
    
    print("\n🔧 Utilisation dans les tests:")
    print("""
    # Test déterministe
    from datetime import date
    
    def test_import_with_specific_date():
        importer = ETLImporter()
        test_date = date(2024, 8, 31)
        
        result = importer.incremental_import(
            "data.csv",
            days_threshold=7,
            reference_date=test_date  # Toujours la même date !
        )
        
        # Le test sera reproductible
        assert result['success']
    """)
    
    print("\n🚀 Utilisation en production:")
    print("""
    # Import avec date actuelle (comportement par défaut)
    result = importer.incremental_import("data.csv")
    
    # Import avec date spécifique (pour simulations)
    from datetime import date
    simulation_date = date(2024, 12, 1)
    result = importer.incremental_import(
        "data.csv", 
        reference_date=simulation_date
    )
    """)

if __name__ == "__main__":
    demo_deterministic_import()
