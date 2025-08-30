#!/usr/bin/env python3
"""
Script de débogage pour identifier la source de l'erreur 'role root does not exist'
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def debug_environment():
    """Debug des variables d'environnement"""
    print("=== VARIABLES D'ENVIRONNEMENT ===")
    db_vars = [
        'APP_ENV', 'USER', 'USERNAME', 'LOGNAME',
        'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
        'TEST_DB_HOST', 'TEST_DB_PORT', 'TEST_DB_NAME', 'TEST_DB_USER', 'TEST_DB_PASSWORD',
        'DATABASE_URL', 'POSTGRES_USER', 'POSTGRES_PASSWORD'
    ]
    
    for var in db_vars:
        value = os.getenv(var, '[NON DÉFINIE]')
        if 'PASSWORD' in var:
            value = '*' * len(value) if value != '[NON DÉFINIE]' else '[NON DÉFINIE]'
        print(f"{var}: {value}")
    
    print("\n=== TOUTES LES VARIABLES CONTENANT 'DB' ===")
    for key, value in os.environ.items():
        if 'DB' in key.upper():
            if 'PASSWORD' in key.upper():
                value = '*' * len(value)
            print(f"{key}: {value}")

def debug_database_config():
    """Debug de la configuration de base de données"""
    print("\n=== CONFIGURATION DATABASE ===")
    
    try:
        from src.database import DatabaseConfig, DatabaseEnvironment, get_database_config
        
        # Test de chaque environnement
        environments = [
            DatabaseEnvironment.DEVELOPMENT,
            DatabaseEnvironment.TEST, 
            DatabaseEnvironment.DOCKER,
        ]
        
        config_manager = DatabaseConfig()
        current_env = config_manager.get_current_environment()
        print(f"Environnement détecté: {current_env.value}")
        
        for env in environments:
            print(f"\n--- {env.value.upper()} ---")
            try:
                config = get_database_config(env)
                safe_config = config.copy()
                safe_config['password'] = '*' * len(config['password'])
                for key, value in safe_config.items():
                    print(f"  {key}: {value}")
            except Exception as e:
                print(f"  ERREUR: {e}")
        
        # Configuration automatique
        print(f"\n--- CONFIGURATION AUTO (pour {current_env.value}) ---")
        try:
            auto_config = get_database_config()
            safe_auto_config = auto_config.copy()
            safe_auto_config['password'] = '*' * len(auto_config['password'])
            for key, value in safe_auto_config.items():
                print(f"  {key}: {value}")
        except Exception as e:
            print(f"  ERREUR: {e}")
            
    except Exception as e:
        print(f"ERREUR lors de l'import: {e}")

def debug_psycopg2_defaults():
    """Debug des paramètres par défaut de psycopg2"""
    print("\n=== PSYCOPG2 DEFAULTS ===")
    
    try:
        import psycopg2
        
        # Test de connexion avec paramètres minimaux pour voir les defaults
        print("Test de connexion psycopg2 avec paramètres par défaut...")
        
        # Paramètres minimum (devrait échouer mais nous montrer les defaults utilisés)
        try:
            conn = psycopg2.connect(
                host='localhost',
                port=5432,
                database='nonexistent'
            )
        except psycopg2.Error as e:
            error_msg = str(e)
            print(f"Erreur psycopg2 (normale): {error_msg}")
            
            # Chercher des indices sur l'utilisateur par défaut
            if 'role' in error_msg and 'root' in error_msg:
                print("🚨 TROUVÉ: L'erreur contient 'root' - psycopg2 utilise 'root' par défaut !")
            elif 'role' in error_msg:
                print(f"ℹ️  Utilisateur par défaut dans l'erreur: {error_msg}")
                
    except ImportError:
        print("psycopg2 non disponible")
    except Exception as e:
        print(f"Erreur inattendue: {e}")

def debug_system_user():
    """Debug de l'utilisateur système"""
    print("\n=== UTILISATEUR SYSTÈME ===")
    
    import getpass
    
    try:
        system_user = getpass.getuser()
        print(f"getpass.getuser(): {system_user}")
    except Exception as e:
        print(f"Erreur getpass.getuser(): {e}")
    
    # Sur Linux/Unix seulement
    try:
        import pwd
        if hasattr(os, 'getuid') and hasattr(pwd, 'getpwuid'):
            pwd_user = pwd.getpwuid(os.getuid()).pw_name
            print(f"pwd.getpwuid(): {pwd_user}")
        else:
            print("pwd.getpwuid non disponible sur cette plateforme")
    except ImportError as e:
        print(f"Module pwd non disponible (probablement Windows): {e}")
    except Exception as e:
        print(f"Erreur pwd.getpwuid(): {e}")

def main():
    """Fonction principale de débogage"""
    print("🔍 DÉBOGAGE CONFIGURATION DATABASE - MUSCLE ANALYTICS")
    print("=" * 60)
    
    debug_environment()
    debug_database_config()
    debug_psycopg2_defaults()
    
    try:
        debug_system_user()
    except ImportError:
        print("\n=== UTILISATEUR SYSTÈME (pwd non disponible) ===")
        print("Module pwd non disponible (probablement Windows)")

if __name__ == "__main__":
    main()
