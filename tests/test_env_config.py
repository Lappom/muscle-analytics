"""
Configuration de test standardisée pour éviter les erreurs de rôles PostgreSQL

Ce module force la configuration de test à utiliser des valeurs standardisées
et empêche l'utilisation de valeurs par défaut problématiques comme 'root'.
Utilise 'test_user' pour la compatibilité CI/CD.
"""

import os
import logging

logger = logging.getLogger(__name__)

def ensure_test_environment():
    """
    S'assure que l'environnement de test est correctement configuré.
    
    Cette fonction doit être appelée au début des tests pour éviter
    l'erreur 'role root does not exist'. Elle standardise l'utilisation
    de 'test_user' comme utilisateur de base de données pour tous les tests,
    assurant ainsi la cohérence entre les environnements locaux et CI/CD.
    """
    # Configuration standardisée pour les tests - compatible avec CI/CD
    test_env_vars = {
        'APP_ENV': 'test',
        'TEST_DB_HOST': 'localhost',
        'TEST_DB_PORT': '5432',
        'TEST_DB_NAME': 'muscle_analytics_test',
        'TEST_DB_USER': 'test_user',  # Standardisé pour CI/CD - évite les conflits avec 'postgres'
        'TEST_DB_PASSWORD': 'test_password',  # Standardisé pour CI/CD
        'DB_USER': 'test_user',  # Cohérence avec TEST_DB_USER
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
        'user': os.getenv('TEST_DB_USER', 'test_user'),  # Standardisé pour CI/CD
        'password': os.getenv('TEST_DB_PASSWORD', 'test_password')  # Standardisé pour CI/CD
    }


# Configuration automatique à l'import
ensure_test_environment()
