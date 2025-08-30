"""
Configuration de test explicite pour éviter l'erreur 'role root does not exist'

Ce module force la configuration de test à utiliser l'utilisateur 'postgres'
et empêche l'utilisation de valeurs par défaut problématiques.
"""

import os
import logging

logger = logging.getLogger(__name__)

def ensure_test_environment():
    """
    S'assure que l'environnement de test est correctement configuré.
    
    Cette fonction doit être appelée au début des tests pour éviter
    l'erreur 'role root does not exist'.
    """
    # Configuration forcée pour les tests - compatible avec CI
    test_env_vars = {
        'APP_ENV': 'test',
        'TEST_DB_HOST': 'localhost',
        'TEST_DB_PORT': '5432',
        'TEST_DB_NAME': 'muscle_analytics_test',
        'TEST_DB_USER': 'test_user',  # Changé de 'postgres' à 'test_user' pour CI
        'TEST_DB_PASSWORD': 'test_password',  # Changé de 'password' à 'test_password' pour CI
        'DB_USER': 'test_user',  # Pour éviter la confusion
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'muscle_analytics_test',
        'DB_PASSWORD': 'test_password'
    }
    
    logger.info("Configuration de l'environnement de test...")
    
    for key, value in test_env_vars.items():
        current_value = os.getenv(key)
        if current_value != value:
            logger.info(f"Définition de {key}: {value} (était: {current_value})")
            os.environ[key] = value
        else:
            logger.debug(f"{key} déjà défini correctement: {value}")
    
    # Vérifications supplémentaires
    problematic_vars = ['USER', 'LOGNAME', 'USERNAME']
    for var in problematic_vars:
        value = os.getenv(var)
        if value == 'root':
            logger.warning(f"Variable système {var}=root détectée - pourrait causer des problèmes")
    
    logger.info("Environnement de test configuré avec succès")


def get_safe_test_config():
    """
    Retourne une configuration de test sûre.
    
    Returns:
        Dict avec les paramètres de connexion de test
    """
    ensure_test_environment()
    
    return {
        'host': os.getenv('TEST_DB_HOST', 'localhost'),
        'port': int(os.getenv('TEST_DB_PORT', '5432')),
        'database': os.getenv('TEST_DB_NAME', 'muscle_analytics_test'),
        'user': os.getenv('TEST_DB_USER', 'test_user'),  # Changé de 'postgres' à 'test_user'
        'password': os.getenv('TEST_DB_PASSWORD', 'test_password')  # Changé de 'password' à 'test_password'
    }


# Configuration automatique à l'import
ensure_test_environment()
