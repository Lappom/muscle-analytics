#!/usr/bin/env python3
"""
Exemple d'utilisation de la configuration de test sécurisée.

Ce script démontre comment utiliser la nouvelle configuration
de test sans exposer de mots de passe.
"""

import sys
from pathlib import Path

# Ajouter les chemins pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from test_config import (
    setup_test_environment, 
    get_mock_db_config, 
    create_test_env_template,
    save_test_config_template
)

def demo_secure_test_config():
    """Démonstration de configuration de test sécurisée"""
    
    print("=== Configuration de Test Sécurisée ===\n")
    
    print("🔐 PROBLÈME RÉSOLU :")
    print("   ❌ Avant : Mots de passe codés en dur")
    print("   ✅ Après : Configuration externalisée et sécurisée\n")
    
    # 1. Configuration automatique
    print("1️⃣  Configuration automatique (recommandée)")
    config = setup_test_environment()
    
    # Masquer le mot de passe pour l'affichage
    display_config = config.copy()
    if display_config.get('password'):
        display_config['password'] = '*' * 8 + f" ({len(config['password'])} caractères)"
    
    print("   Configuration chargée :")
    for key, value in display_config.items():
        print(f"     {key}: {value}")
    print()
    
    # 2. Configuration mock
    print("2️⃣  Configuration mock (pour tests sans DB)")
    mock_config = get_mock_db_config()
    print("   Configuration mock :")
    for key, value in mock_config.items():
        print(f"     {key}: {value}")
    print()
    
    # 3. Variables d'environnement
    print("3️⃣  Variables d'environnement disponibles :")
    env_vars = [
        'TEST_DB_HOST', 'TEST_DB_PORT', 'TEST_DB_NAME',
        'TEST_DB_USER', 'TEST_DB_PASSWORD'
    ]
    
    import os
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var:
                value = '*' * len(value)
            print(f"     {var}: {value}")
        else:
            print(f"     {var}: (non définie)")
    print()
    
    # 4. Exemples d'utilisation
    print("4️⃣  Exemples d'utilisation :")
    print("""
    # Dans vos tests
    from test_config import setup_test_environment
    from etl.database import DatabaseManager
    
    def setUp(self):
        db_config = setup_test_environment()
        self.db_manager = DatabaseManager(**db_config)
    
    # Pour des tests mock
    from test_config import get_mock_db_config
    
    def test_without_real_db(self):
        mock_config = get_mock_db_config()
        # ... utiliser la config mock
    """)
    
    # 5. Configuration recommandée
    print("5️⃣  Configuration recommandée pour votre environnement :")
    
    # Créer le template si nécessaire
    template_file = Path(__file__).parent / '.env.test.template'
    if not template_file.exists():
        save_test_config_template()
    
    print(f"   📄 Template créé : {template_file}")
    print("   📋 Pour configurer :")
    print("      1. Copiez .env.test.template vers .env.test")
    print("      2. Éditez .env.test avec vos valeurs")
    print("      3. Le fichier .env.test est automatiquement ignoré par git")
    print()
    
    print("🔒 SÉCURITÉ :")
    print("   ✅ Mots de passe externalisés")
    print("   ✅ Configuration par environnement")
    print("   ✅ Fallback intelligent") 
    print("   ✅ Compatible CI/CD")
    print("   ✅ Tests reproductibles")


def demo_different_environments():
    """Démonstration de configuration pour différents environnements"""
    
    print("\n=== Configuration Multi-Environnements ===\n")
    
    environments = {
        'development': {
            'description': 'Développement local',
            'setup': 'Fichier .env.test local',
            'security': 'Mot de passe simple OK'
        },
        'ci_cd': {
            'description': 'Intégration continue',
            'setup': 'Variables d\'environnement',
            'security': 'Secrets GitHub/Azure'
        },
        'docker': {
            'description': 'Conteneur Docker',
            'setup': 'Docker secrets',
            'security': 'Fichiers secrets montés'
        }
    }
    
    for env_name, env_info in environments.items():
        print(f"🌍 {env_name.upper()}")
        print(f"   Description: {env_info['description']}")
        print(f"   Configuration: {env_info['setup']}")
        print(f"   Sécurité: {env_info['security']}")
        print()


if __name__ == "__main__":
    demo_secure_test_config()
    demo_different_environments()
    
    print("\n💡 Pour plus d'informations, consultez README_SECURITY.md")
