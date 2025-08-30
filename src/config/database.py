"""
Configuration centralisée pour toutes les bases de données du projet.

Ce module gère la configuration pour :
- Base de données de développement
- Base de données de test
- Base de données de production
- Base de données Docker
"""

import os
from typing import Dict, Any, Optional
from enum import Enum
from pathlib import Path


class DatabaseEnvironment(Enum):
    """Types d'environnements de base de données"""
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"
    DOCKER = "docker"


class DatabaseConfig:
    """Gestionnaire de configuration de base de données"""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent
        self.env_file = self.config_dir / '.env'
        self.load_env_file()
    
    def load_env_file(self):
        """Charge le fichier .env s'il existe"""
        if self.env_file.exists():
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key, value)
    
    def get_database_config(self, environment: DatabaseEnvironment) -> Dict[str, Any]:
        """
        Récupère la configuration pour un environnement spécifique.
        
        Args:
            environment: Type d'environnement
            
        Returns:
            Configuration de base de données
        """
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
            'port': int(os.getenv('TEST_DB_PORT', '5433')),  # Port différent
            'database': os.getenv('TEST_DB_NAME', 'muscle_analytics_test'),
            'user': os.getenv('TEST_DB_USER', 'test_user'),
            'password': os.getenv('TEST_DB_PASSWORD', 'test_password_change_me')
        }
    
    def _get_prod_config(self) -> Dict[str, Any]:
        """Configuration pour la production"""
        # En production, TOUTES les variables doivent être définies
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
        """Configuration pour Docker (utilise les variables d'environnement du conteneur)"""
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
    
    def get_auto_config(self) -> Dict[str, Any]:
        """Récupère automatiquement la config selon l'environnement actuel"""
        current_env = self.get_current_environment()
        return self.get_database_config(current_env)
    
    def create_env_template(self) -> str:
        """Crée un template de fichier .env"""
        template = """# Configuration des bases de données Muscle-Analytics
# Copiez ce fichier vers .env et modifiez les valeurs

# Environnement actuel (development, test, production, docker)
APP_ENV=development

# === BASE DE DONNÉES DE DÉVELOPPEMENT ===
DEV_DB_HOST=localhost
DEV_DB_PORT=5432
DEV_DB_NAME=muscle_analytics_dev
DEV_DB_USER=dev_user
DEV_DB_PASSWORD=votre_mdp_dev_ici

# === BASE DE DONNÉES DE TEST ===
TEST_DB_HOST=localhost
TEST_DB_PORT=5433
TEST_DB_NAME=muscle_analytics_test
TEST_DB_USER=test_user
TEST_DB_PASSWORD=votre_mdp_test_ici

# === BASE DE DONNÉES DE PRODUCTION ===
# ⚠️ À configurer uniquement en production !
# PROD_DB_HOST=
# PROD_DB_PORT=5432
# PROD_DB_NAME=
# PROD_DB_USER=
# PROD_DB_PASSWORD=

# === DOCKER (utilisé par docker-compose) ===
DB_HOST=postgres
DB_PORT=5432
DB_NAME=muscle_analytics
DB_USER=dev
DB_PASSWORD=docker_dev_password

# === AUTRES CONFIGURATIONS ===
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
"""
        return template
    
    def save_env_template(self):
        """Sauvegarde le template .env"""
        template_file = self.config_dir / '.env.template'
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(self.create_env_template())
        print(f"📝 Template créé: {template_file}")
        print("💡 Copiez-le vers .env et modifiez les valeurs")


# Instance globale
db_config = DatabaseConfig()


def get_db_config(environment: Optional[DatabaseEnvironment] = None) -> Dict[str, Any]:
    """
    Fonction utilitaire pour obtenir la configuration de base de données.
    
    Args:
        environment: Environnement spécifique ou None pour auto-détection
        
    Returns:
        Configuration de base de données
    """
    if environment:
        return db_config.get_database_config(environment)
    else:
        return db_config.get_auto_config()


def setup_database_environment(environment: DatabaseEnvironment) -> Dict[str, Any]:
    """
    Configure l'environnement de base de données.
    
    Args:
        environment: Type d'environnement à configurer
        
    Returns:
        Configuration appliquée
    """
    config = db_config.get_database_config(environment)
    
    print(f"🔧 Configuration de l'environnement: {environment.value}")
    print(f"   Hôte: {config['host']}:{config['port']}")
    print(f"   Base: {config['database']}")
    print(f"   Utilisateur: {config['user']}")
    print(f"   Mot de passe: {'*' * len(config['password'])}")
    
    return config


if __name__ == "__main__":
    # Créer le template
    db_config.save_env_template()
    
    # Afficher la configuration actuelle
    print("\n🔧 Configuration actuelle:")
    current_config = get_db_config()
    
    # Masquer le mot de passe
    display_config = current_config.copy()
    display_config['password'] = '*' * len(current_config['password'])
    
    for key, value in display_config.items():
        print(f"   {key}: {value}")
    
    print(f"\n🌍 Environnement détecté: {db_config.get_current_environment().value}")
