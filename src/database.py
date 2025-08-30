"""
Module unifié de gestion de base de données pour Muscle-Analytics.

Ce module combine :
1. Configuration multi-environnements (DatabaseConfig)  
2. Gestionnaire de base de données (DatabaseManager)
3. Utilitaires de connexion

Usage simple :
    from src.database import get_database, DatabaseEnvironment
    
    # Automatique selon l'environnement
    db = get_database()
    
    # Spécifique
    test_db = get_database(DatabaseEnvironment.TEST)
"""

import psycopg2
import pandas as pd
import os
from typing import Optional, List, Dict, Tuple, Any
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime, date
from contextlib import contextmanager

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

class DatabaseEnvironment(Enum):
    """Types d'environnements de base de données"""
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"
    DOCKER = "docker"


class DatabaseConfig:
    """Gestionnaire de configuration de base de données"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.env_file = self.project_root / '.env'
        self.load_env_file()
    
    def _find_project_root(self) -> Path:
        """Trouve la racine du projet (où se trouve .env)"""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / '.env').exists() or (current / 'pyproject.toml').exists():
                return current
            current = current.parent
        return Path(__file__).parent.parent  # Fallback
    
    def load_env_file(self):
        """Charge le fichier .env s'il existe"""
        if self.env_file.exists():
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key, value)
    
    def get_config(self, environment: DatabaseEnvironment) -> Dict[str, Any]:
        """Récupère la configuration pour un environnement spécifique"""
        if environment == DatabaseEnvironment.DEVELOPMENT:
            return self._get_dev_config()
        elif environment == DatabaseEnvironment.TEST:
            return self._get_test_config()
        elif environment == DatabaseEnvironment.PRODUCTION:
            return self._get_prod_config()
        elif environment == DatabaseEnvironment.DOCKER:
            return self._get_docker_config()
        else:
            raise ValueError(f"Environnement non supporté: {environment}")
    
    def _get_dev_config(self) -> Dict[str, Any]:
        """Configuration pour le développement local"""
        return {
            'host': os.getenv('DEV_DB_HOST', 'localhost'),
            'port': int(os.getenv('DEV_DB_PORT', '5432')),
            'database': os.getenv('DEV_DB_NAME', 'muscle_analytics_dev'),
            'user': os.getenv('DEV_DB_USER', 'dev_user'),
            'password': os.getenv('DEV_DB_PASSWORD', 'dev_password_change_me')
        }
    
    def _get_test_config(self) -> Dict[str, Any]:
        """Configuration pour les tests"""
        return {
            'host': os.getenv('TEST_DB_HOST', 'localhost'),
            'port': int(os.getenv('TEST_DB_PORT', '5433')),
            'database': os.getenv('TEST_DB_NAME', 'muscle_analytics_test'),
            'user': os.getenv('TEST_DB_USER', 'test_user'),
            'password': os.getenv('TEST_DB_PASSWORD', 'test_password_change_me')
        }
    
    def _get_prod_config(self) -> Dict[str, Any]:
        """Configuration pour la production"""
        required_vars = ['PROD_DB_HOST', 'PROD_DB_NAME', 'PROD_DB_USER', 'PROD_DB_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Variables de production manquantes: {missing_vars}")
        
        return {
            'host': os.getenv('PROD_DB_HOST'),
            'port': int(os.getenv('PROD_DB_PORT', '5432')),
            'database': os.getenv('PROD_DB_NAME'),
            'user': os.getenv('PROD_DB_USER'),
            'password': os.getenv('PROD_DB_PASSWORD')
        }
    
    def _get_docker_config(self) -> Dict[str, Any]:
        """Configuration pour Docker"""
        return {
            'host': os.getenv('DB_HOST', 'postgres'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'muscle_analytics'),
            'user': os.getenv('DB_USER', 'dev'),
            'password': os.getenv('DB_PASSWORD', 'devpass')
        }
    
    def get_current_environment(self) -> DatabaseEnvironment:
        """Détermine l'environnement actuel"""
        env = os.getenv('APP_ENV', '').lower()
        
        if env == 'production':
            return DatabaseEnvironment.PRODUCTION
        elif env == 'test':
            return DatabaseEnvironment.TEST
        elif env == 'docker':
            return DatabaseEnvironment.DOCKER
        else:
            return DatabaseEnvironment.DEVELOPMENT


# =============================================================================
# GESTIONNAIRE DE BASE DE DONNÉES
# =============================================================================

class DatabaseError(Exception):
    """Exception spécifique aux opérations de base de données"""
    pass


class DatabaseManager:
    """Gestionnaire de base de données pour Muscle-Analytics"""
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 5432,
                 database: str = "muscle_analytics",
                 user: str = "postgres", 
                 password: str = "password"):
        """
        Initialise le gestionnaire de base de données.
        
        Args:
            host: Hôte PostgreSQL
            port: Port PostgreSQL
            database: Nom de la base de données
            user: Utilisateur
            password: Mot de passe
        """
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        
        logger.info(f"DatabaseManager configuré pour {user}@{host}:{port}/{database}")
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'DatabaseManager':
        """Crée un DatabaseManager à partir d'une configuration"""
        return cls(**config)
    
    @classmethod
    def from_environment(cls, environment: DatabaseEnvironment) -> 'DatabaseManager':
        """Crée un DatabaseManager pour un environnement spécifique"""
        config_manager = DatabaseConfig()
        config = config_manager.get_config(environment)
        return cls.from_config(config)
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à la base de données.
        
        Returns:
            True si la connexion réussit, False sinon
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Échec de la connexion à la base de données: {e}")
            return False
    
    @contextmanager
    def get_connection(self):
        """
        Context manager pour obtenir une connexion à la base de données.
        
        Yields:
            Connexion psycopg2
            
        Raises:
            DatabaseError: Si la connexion échoue
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Erreur de base de données: {e}")
        except Exception as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Erreur inattendue: {e}")
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """
        Exécute une requête SELECT et retourne les résultats.
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
            
        Returns:
            Liste des résultats
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Exécute une requête UPDATE/INSERT/DELETE.
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
            
        Returns:
            Nombre de lignes affectées
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

# Instance globale de configuration
_config_manager = DatabaseConfig()


def get_database_config(environment: Optional[DatabaseEnvironment] = None) -> Dict[str, Any]:
    """
    Récupère la configuration de base de données.
    
    Args:
        environment: Environnement spécifique ou None pour auto-détection
        
    Returns:
        Configuration de base de données
    """
    if environment is None:
        environment = _config_manager.get_current_environment()
    
    return _config_manager.get_config(environment)


def get_database(environment: Optional[DatabaseEnvironment] = None) -> DatabaseManager:
    """
    Crée un DatabaseManager configuré automatiquement.
    
    Args:
        environment: Environnement spécifique ou None pour auto-détection
        
    Returns:
        Instance de DatabaseManager configurée
        
    Examples:
        # Configuration automatique
        db = get_database()
        
        # Configuration spécifique
        test_db = get_database(DatabaseEnvironment.TEST)
        prod_db = get_database(DatabaseEnvironment.PRODUCTION)
    """
    config = get_database_config(environment)
    return DatabaseManager.from_config(config)


def setup_test_database() -> DatabaseManager:
    """Utilitaire pour configurer rapidement une base de test"""
    return get_database(DatabaseEnvironment.TEST)


def setup_development_database() -> DatabaseManager:
    """Utilitaire pour configurer rapidement une base de développement"""
    return get_database(DatabaseEnvironment.DEVELOPMENT)


# =============================================================================
# COMPATIBILITÉ AVEC L'ANCIEN CODE
# =============================================================================

# Pour compatibilité avec l'ancien code
def get_db_config(environment: Optional[DatabaseEnvironment] = None) -> Dict[str, Any]:
    """Alias pour get_database_config (compatibilité)"""
    return get_database_config(environment)


# Export des classes principales
__all__ = [
    'DatabaseManager', 'DatabaseConfig', 'DatabaseEnvironment', 'DatabaseError',
    'get_database', 'get_database_config', 'setup_test_database', 'setup_development_database'
]


if __name__ == "__main__":
    # Test rapide
    print("🔧 Configuration de base de données")
    
    current_env = _config_manager.get_current_environment()
    print(f"🌍 Environnement: {current_env.value}")
    
    config = get_database_config()
    print(f"📊 Configuration: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
    
    # Test de connexion
    try:
        db = get_database()
        if db.test_connection():
            print("✅ Connexion réussie")
        else:
            print("❌ Connexion échouée")
    except Exception as e:
        print(f"❌ Erreur: {e}")
