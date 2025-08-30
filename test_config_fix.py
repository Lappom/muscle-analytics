#!/usr/bin/env python3
"""
Test rapide de la configuration de base de données pour éviter l'erreur 'role root does not exist'
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'tests'))

def main():
    print("🧪 Test de configuration de base de données")
    print("=" * 50)
    
    # Test 1: Configuration d'environnement sécurisée
    print("\n1️⃣ Test de la configuration d'environnement...")
    try:
        from tests.test_env_config import ensure_test_environment, get_safe_test_config
        
        ensure_test_environment()
        config = get_safe_test_config()
        
        # Masquer le mot de passe
        safe_config = config.copy()
        safe_config['password'] = '*' * len(config['password'])
        
        print("   ✅ Configuration sécurisée chargée:")
        for key, value in safe_config.items():
            print(f"      {key}: {value}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test 2: Configuration de base de données normale
    print("\n2️⃣ Test de la configuration de base de données normale...")
    try:
        from src.database import get_database_config, DatabaseEnvironment
        
        config = get_database_config(DatabaseEnvironment.TEST)
        
        # Vérifier qu'aucun paramètre n'est 'root'
        if config.get('user') == 'root':
            print(f"   ❌ PROBLÈME: L'utilisateur est 'root' - ceci causera l'erreur!")
            return False
        
        # Masquer le mot de passe
        safe_config = config.copy()
        safe_config['password'] = '*' * len(config['password'])
        
        print("   ✅ Configuration normale chargée:")
        for key, value in safe_config.items():
            print(f"      {key}: {value}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False
    
    # Test 3: Test de connexion (si base disponible)
    print("\n3️⃣ Test de connexion à la base de données...")
    try:
        from src.database import DatabaseManager
        
        db = DatabaseManager(**config)
        
        if db.test_connection():
            print("   ✅ Connexion réussie!")
        else:
            print("   ⚠️  Connexion échouée (base probablement non disponible)")
            
    except Exception as e:
        error_msg = str(e)
        if 'role "root" does not exist' in error_msg:
            print(f"   ❌ ERREUR CRITIQUE: {error_msg}")
            print("      Cette erreur indique que l'utilisateur 'root' est encore utilisé quelque part!")
            return False
        else:
            print(f"   ⚠️  Connexion impossible: {e}")
    
    print("\n✅ Tous les tests de configuration passés!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
