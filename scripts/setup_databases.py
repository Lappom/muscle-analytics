#!/usr/bin/env python3
"""
Script de test et configuration des bases de données.

Usage: python setup_databases.py [action]

Actions:
- config : Affiche la configuration actuelle
- template : Crée le template .env
- test : Teste les connexions
- demo : Démonstration complète
"""

import sys
import os
from pathlib import Path

# Import direct depuis le package installé
try:
    from config.database import (
        DatabaseConfig, DatabaseEnvironment, 
        get_db_config, setup_database_environment
    )
    from etl.database import DatabaseManager
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("💡 Assurez-vous que le package muscle-analytics est installé:")
    print("   pip install -e .")
    print("💡 Et que vous êtes dans l'environnement virtuel approprié")
    sys.exit(1)


def show_config():
    """Affiche la configuration actuelle"""
    print("🔧 Configuration des Bases de Données")
    print("=" * 50)
    
    db_config_manager = DatabaseConfig()
    current_env = db_config_manager.get_current_environment()
    
    print(f"🌍 Environnement actuel: {current_env.value}")
    print()
    
    environments = [
        DatabaseEnvironment.DEVELOPMENT,
        DatabaseEnvironment.TEST,
        DatabaseEnvironment.DOCKER,
    ]
    
    for env in environments:
        print(f"📊 {env.value.upper()}")
        try:
            config = get_db_config(env)
            # Masquer le mot de passe
            display_config = config.copy()
            display_config['password'] = '*' * len(config['password'])
            
            for key, value in display_config.items():
                print(f"   {key}: {value}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
        print()


def create_template():
    """Crée le template de configuration"""
    print("📝 Création du template de configuration...")
    
    db_config_manager = DatabaseConfig()
    db_config_manager.save_env_template()
    
    # Créer aussi à la racine pour faciliter l'usage
    root_template = Path(".env.template")
    src_template = Path("src/config/.env.template")
    
    if src_template.exists():
        try:
            content = src_template.read_text(encoding='utf-8')
            root_template.write_text(content, encoding='utf-8')
            print(f"📄 Template copié vers: {root_template.absolute()}")
        except UnicodeDecodeError:
            # Fallback si problème d'encodage
            content = src_template.read_bytes()
            root_template.write_bytes(content)
            print(f"📄 Template copié vers: {root_template.absolute()}")
    
    print()
    print("🚀 Prochaines étapes:")
    print("1. cp .env.template .env")
    print("2. Éditez .env avec vos mots de passe")
    print("3. Redémarrez pour appliquer la configuration")


def test_connections():
    """Teste les connexions aux bases de données"""
    print("🔍 Test des connexions aux bases de données")
    print("=" * 50)
    
    environments = [
        (DatabaseEnvironment.DEVELOPMENT, "Base de développement"),
        (DatabaseEnvironment.TEST, "Base de test"),
        (DatabaseEnvironment.DOCKER, "Base Docker"),
    ]
    
    for env, description in environments:
        print(f"\n🧪 {description}")
        try:
            config = get_db_config(env)
            db_manager = DatabaseManager(**config)
            
            if db_manager.test_connection():
                print(f"   ✅ Connexion réussie")
                print(f"   📍 {config['host']}:{config['port']}/{config['database']}")
            else:
                print(f"   ❌ Connexion échouée")
                print(f"   📍 {config['host']}:{config['port']}/{config['database']}")
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print("\n💡 Si des connexions échouent:")
    print("   - Vérifiez que PostgreSQL est démarré")
    print("   - Vérifiez les mots de passe dans .env")
    print("   - Pour Docker: docker-compose up postgres")


def demo():
    """Démonstration complète"""
    print("🎯 Démonstration de Configuration Multi-Bases")
    print("=" * 60)
    print()
    
    # 1. Configuration actuelle
    print("1️⃣ Configuration actuelle")
    print("-" * 30)
    show_config()
    
    # 2. Test des connexions
    print("2️⃣ Test des connexions")
    print("-" * 30)
    test_connections()
    
    # 3. Exemple d'utilisation
    print("\n3️⃣ Exemple d'utilisation dans le code")
    print("-" * 30)
    print("""
# Utilisation simple
from src.config.database import get_db_config, DatabaseEnvironment
from src.etl.database import DatabaseManager

# Configuration automatique
config = get_db_config()
db = DatabaseManager(**config)

# Configuration spécifique
test_config = get_db_config(DatabaseEnvironment.TEST)
test_db = DatabaseManager(**test_config)

# Dans les tests
def setUp(self):
    config = get_db_config(DatabaseEnvironment.TEST)
    self.db = DatabaseManager(**config)
""")
    
    # 4. Commandes Docker
    print("4️⃣ Commandes Docker utiles")
    print("-" * 30)
    print("""
# Démarrer la base de développement
docker-compose up postgres

# Démarrer la base de test
docker-compose up postgres-test --profile test

# Démarrer avec variables d'environnement
DB_PASSWORD=mon_mdp docker-compose up

# Utiliser le docker-compose sécurisé
docker-compose -f docker-compose.secure.yml up
""")


def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        action = "demo"
    else:
        action = sys.argv[1].lower()
    
    if action == "config":
        show_config()
    elif action == "template":
        create_template()
    elif action == "test":
        test_connections()
    elif action == "demo":
        demo()
    elif action == "help":
        print(__doc__)
    else:
        print(f"❌ Action inconnue: {action}")
        print("💡 Actions disponibles: config, template, test, demo, help")
        sys.exit(1)


if __name__ == "__main__":
    main()
