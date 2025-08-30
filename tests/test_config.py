"""
Configuration pour les tests - Gestion sécurisée des paramètres de test.

Ce module fournit des utilitaires pour configurer les tests de manière sécurisée
sans exposer de mots de passe en dur dans le code.
"""

import os
import secrets
import string
from typing import Dict, Any, Optional
from pathlib import Path


def get_test_db_config() -> Dict[str, Any]:
    """
    Récupère la configuration de base de données pour les tests.
    
    Utilise des variables d'environnement avec des valeurs par défaut appropriées.
    
    Variables d'environnement supportées:
    - TEST_DB_HOST: Hôte de la base de données (défaut: localhost)
    - TEST_DB_PORT: Port de la base de données (défaut: 5432)
    - TEST_DB_NAME: Nom de la base de données (défaut: muscle_analytics_test)
    - TEST_DB_USER: Utilisateur de la base de données (défaut: postgres)
    - TEST_DB_PASSWORD: Mot de passe (défaut: généré aléatoirement)
    
    Returns:
        Dict contenant la configuration de la base de données de test
    """
    # Génération d'un mot de passe aléatoire si non fourni
    default_password = _generate_test_password()
    
    config = {
        'host': os.getenv('TEST_DB_HOST', 'localhost'),
        'port': int(os.getenv('TEST_DB_PORT', '5432')),
        'database': os.getenv('TEST_DB_NAME', 'muscle_analytics_test'),
        'user': os.getenv('TEST_DB_USER', 'postgres'),
        'password': os.getenv('TEST_DB_PASSWORD', default_password)
    }
    
    return config


def get_test_db_config_from_file() -> Optional[Dict[str, Any]]:
    """
    Charge la configuration depuis un fichier de test (optionnel).
    
    Recherche un fichier .env.test ou test_config.ini dans le dossier tests.
    
    Returns:
        Dict avec la configuration ou None si aucun fichier trouvé
    """
    test_dir = Path(__file__).parent
    
    # Essayer de charger un fichier .env.test
    env_test_file = test_dir / '.env.test'
    if env_test_file.exists():
        return _load_env_file(env_test_file)
    
    # Essayer de charger un fichier test_config.ini
    ini_test_file = test_dir / 'test_config.ini'
    if ini_test_file.exists():
        return _load_ini_file(ini_test_file)
    
    return None


def get_mock_db_config() -> Dict[str, Any]:
    """
    Configuration pour les tests avec base de données mockée.
    
    Returns:
        Dict avec configuration de test minimal
    """
    return {
        'host': 'mock',
        'port': 0,
        'database': 'test_mock',
        'user': 'mock_user',
        'password': 'mock_password'
    }


def create_test_env_template() -> str:
    """
    Crée un template de fichier .env.test pour la configuration.
    
    Returns:
        Contenu du template comme chaîne
    """
    template = """# Configuration de base de données pour les tests
# Copiez ce fichier vers .env.test et ajustez les valeurs

# Paramètres de connexion PostgreSQL
TEST_DB_HOST=localhost
TEST_DB_PORT=5432
TEST_DB_NAME=muscle_analytics_test
TEST_DB_USER=postgres
TEST_DB_PASSWORD=your_secure_test_password_here

# Remarques:
# - Utilisez toujours une base de données dédiée aux tests
# - Ne commitez jamais le fichier .env.test avec de vrais mots de passe
# - Pour les tests CI/CD, utilisez des variables d'environnement
"""
    return template


def _generate_test_password(length: int = 16) -> str:
    """
    Génère un mot de passe aléatoire pour les tests.
    
    Args:
        length: Longueur du mot de passe
        
    Returns:
        Mot de passe généré aléatoirement
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _load_env_file(file_path: Path) -> Dict[str, Any]:
    """Charge un fichier .env simple"""
    config = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Convertir les clés d'environnement en clés de config
                    if key.startswith('TEST_DB_'):
                        config_key = key.replace('TEST_DB_', '').lower()
                        if config_key == 'name':
                            config_key = 'database'
                        
                        # Conversion de type pour le port
                        if config_key == 'port':
                            config[config_key] = int(value)
                        else:
                            config[config_key] = value
    except Exception as e:
        print(f"⚠️  Erreur lors du chargement de {file_path}: {e}")
        return {}
    
    return config


def _load_ini_file(file_path: Path) -> Dict[str, Any]:
    """Charge un fichier INI simple"""
    try:
        import configparser
        
        config_parser = configparser.ConfigParser()
        config_parser.read(file_path)
        
        if 'database' in config_parser:
            db_section = config_parser['database']
            return {
                'host': db_section.get('host', 'localhost'),
                'port': int(db_section.get('port', '5432')),
                'database': db_section.get('name', 'muscle_analytics_test'),
                'user': db_section.get('user', 'test_user'),
                'password': db_section.get('password', _generate_test_password())
            }
    except Exception as e:
        print(f"⚠️  Erreur lors du chargement de {file_path}: {e}")
    
    return {}


def setup_test_environment() -> Dict[str, Any]:
    """
    Configure l'environnement de test avec la meilleure configuration disponible.
    
    Ordre de priorité:
    1. Variables d'environnement
    2. Fichier de configuration local
    3. Configuration par défaut avec mot de passe généré
    
    Returns:
        Configuration de base de données optimale pour les tests
    """
    # Essayer de charger depuis un fichier local d'abord
    file_config = get_test_db_config_from_file()
    if file_config:
        print("📄 Configuration chargée depuis fichier local")
        return file_config
    
    # Utiliser les variables d'environnement ou les valeurs par défaut
    env_config = get_test_db_config()
    
    # Avertir si on utilise des valeurs par défaut
    if os.getenv('TEST_DB_PASSWORD') is None:
        print("🔐 Mot de passe de test généré automatiquement")
        print("💡 Conseil: Définissez TEST_DB_PASSWORD pour un contrôle précis")
    
    return env_config


def save_test_config_template():
    """
    Sauvegarde un template de configuration dans le dossier tests.
    """
    test_dir = Path(__file__).parent
    template_file = test_dir / '.env.test.template'
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(create_test_env_template())
    
    print(f"📝 Template de configuration créé: {template_file}")
    print("💡 Copiez-le vers .env.test et ajustez les valeurs")


if __name__ == "__main__":
    # Utilitaire pour créer le template
    save_test_config_template()
    
    # Afficher la configuration actuelle
    print("\n🔧 Configuration de test actuelle:")
    config = setup_test_environment()
    
    # Masquer le mot de passe pour l'affichage
    display_config = config.copy()
    if display_config.get('password'):
        display_config['password'] = '*' * len(display_config['password'])
    
    for key, value in display_config.items():
        print(f"   {key}: {value}")
