"""
Script pour démarrer l'API Muscle-Analytics

Usage:
    python run_api.py [--port 8000] [--host localhost] [--reload]
"""

import uvicorn
import argparse
import sys
import os
from pathlib import Path


def main():
    """Lance l'API FastAPI"""
    parser = argparse.ArgumentParser(description="Démarre l'API Muscle-Analytics")
    parser.add_argument("--host", default="localhost", help="Hôte (défaut: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="Port (défaut: 8000)")
    parser.add_argument("--reload", action="store_true", help="Mode reload automatique")
    parser.add_argument("--log-level", default="info", help="Niveau de log (défaut: info)")
    
    args = parser.parse_args()
    
    # Définition du répertoire racine du projet (nécessaire pour uvicorn)
    project_root = Path(__file__).parent.parent
    
    print(f"🚀 Démarrage de l'API Muscle-Analytics")
    print(f"🌐 URL: http://{args.host}:{args.port}")
    print(f"📚 Documentation: http://{args.host}:{args.port}/docs")
    print(f"🔄 Reload: {'Activé' if args.reload else 'Désactivé'}")
    print("-" * 50)
    
    # Configuration d'environnement
    os.environ.setdefault("APP_ENV", "development")
    
    try:
        uvicorn.run(
            "src.api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            app_dir=str(project_root)
        )
    except KeyboardInterrupt:
        print("\n👋 Arrêt de l'API")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
