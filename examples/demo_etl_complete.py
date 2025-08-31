#!/usr/bin/env python3
"""
Script de démonstration pour le pipeline ETL complet.

Ce script démontre l'utilisation du pipeline ETL de bout en bout :
- Traitement des fichiers CSV/XML
- Insertion en base de données
- Import incrémental
- Génération de rapports
"""

import logging
import sys
from pathlib import Path

# Ajout du chemin src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from etl.pipeline import ETLPipeline
from src.database import DatabaseManager
from etl.import_scripts import ETLImporter
from config.database import get_db_config

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('etl_demo.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def test_database_connection():
    """Test la connexion à la base de données"""
    logger.info("=== TEST DE CONNEXION À LA BASE DE DONNÉES ===")
    
    # Utilisation de la configuration automatique (détecte l'environnement)
    db_config = get_db_config()
    db_manager = DatabaseManager(**db_config)
    
    if db_manager.test_connection():
        logger.info("CONNEXION RÉUSSIE à la base de données")
        
        # Affichage des statistiques
        try:
            stats = db_manager.get_database_stats()
            logger.info(f"Statistiques actuelles:")
            logger.info(f"   - Sessions: {stats['total_sessions']}")
            logger.info(f"   - Séries: {stats['total_sets']}")
            logger.info(f"   - Exercices uniques: {stats['unique_exercises']}")
            logger.info(f"   - Exercices catalogués: {stats['catalogued_exercises']}")
            
            if stats['date_range']['start'] and stats['date_range']['end']:
                logger.info(f"   - Période: {stats['date_range']['start']} à {stats['date_range']['end']}")
        except Exception as e:
            logger.warning(f"Impossible de récupérer les statistiques: {e}")
        
        return True
    else:
        logger.error("ÉCHEC de la connexion à la base de données")
        logger.error("Vérifiez que PostgreSQL est démarré et que la base existe")
        return False


def test_pipeline_processing():
    """Test le traitement des fichiers d'exemple"""
    logger.info("=== TEST DU PIPELINE DE TRAITEMENT ===")
    
    pipeline = ETLPipeline()
    examples_dir = Path(__file__).parent
    
    # Test du fichier CSV
    csv_file = examples_dir / 'sample_data.csv'
    if csv_file.exists():
        logger.info(f"Traitement du fichier CSV: {csv_file.name}")
        try:
            df_csv = pipeline.process_file(csv_file)
            logger.info(f"CSV traité AVEC SUCCÈS: {len(df_csv)} lignes normalisées")
            
            # Validation de la qualité
            quality = pipeline.validate_data_quality(df_csv)
            logger.info(f"Qualité: {quality['quality_percentage']:.1f}% ({quality['valid_sets']}/{quality['total_rows']} séries valides)")
            
        except Exception as e:
            logger.error(f"ERREUR CSV: {e}")
    else:
        logger.warning(f"Fichier CSV non trouvé: {csv_file}")
    
    # Test du fichier XML
    xml_file = examples_dir / 'sample_data.xml'
    if xml_file.exists():
        logger.info(f"Traitement du fichier XML: {xml_file.name}")
        try:
            df_xml = pipeline.process_file(xml_file)
            logger.info(f"XML traité AVEC SUCCÈS: {len(df_xml)} lignes normalisées")
            
            # Validation de la qualité
            quality = pipeline.validate_data_quality(df_xml)
            logger.info(f"Qualité: {quality['quality_percentage']:.1f}% ({quality['valid_sets']}/{quality['total_rows']} séries valides)")
            
        except Exception as e:
            logger.error(f"ERREUR XML: {e}")
    else:
        logger.warning(f"Fichier XML non trouvé: {xml_file}")


def test_database_import():
    """Test l'import en base de données"""
    logger.info("=== TEST D'IMPORT EN BASE DE DONNÉES ===")
    
    # Utilisation de la configuration automatique
    db_config = get_db_config()
    db_manager = DatabaseManager(**db_config)
    importer = ETLImporter(db_manager)
    examples_dir = Path(__file__).parent
    
    # Test d'import d'un fichier
    csv_file = examples_dir / 'sample_data.csv'
    if csv_file.exists():
        logger.info(f"Import du fichier: {csv_file.name}")
        try:
            result = importer.import_file(csv_file, force_import=True)
            
            if result['success']:
                logger.info(f"Import RÉUSSI: {result['message']}")
                logger.info(f"Statistiques: {result['stats']}")
            else:
                logger.error(f"ÉCHEC d'import: {result['message']}")
            
            # Génération du rapport
            report = importer.generate_import_report(result)
            logger.info(f"Rapport d'import:\n{report}")
            
        except Exception as e:
            logger.error(f"ERREUR d'import: {e}")
    
    # Test d'import de répertoire
    if examples_dir.exists():
        logger.info(f"Import du répertoire: {examples_dir}")
        try:
            result = importer.import_directory(examples_dir, force_import=False)
            
            if result['success']:
                logger.info(f"✅ Import répertoire réussi: {result['message']}")
            else:
                logger.info(f"ℹ️  Import répertoire: {result['message']}")
            
            # Génération du rapport
            report = importer.generate_import_report(result)
            logger.info(f"📄 Rapport d'import répertoire:\n{report}")
            
        except Exception as e:
            logger.error(f"❌ Erreur d'import répertoire: {e}")


def test_incremental_import():
    """Test l'import incrémental"""
    logger.info("=== TEST D'IMPORT INCRÉMENTAL ===")
    
    # Utilisation de la configuration automatique
    db_config = get_db_config()
    db_manager = DatabaseManager(**db_config)
    importer = ETLImporter(db_manager)
    examples_dir = Path(__file__).parent
    
    if examples_dir.exists():
        logger.info(f"Import incrémental du répertoire: {examples_dir}")
        try:
            result = importer.incremental_import(examples_dir, days_threshold=30)
            
            if result['success']:
                logger.info(f"✅ Import incrémental réussi: {result['message']}")
            else:
                logger.info(f"ℹ️  Import incrémental: {result['message']}")
            
            logger.info(f"📊 Statistiques: {result['stats']}")
            
        except Exception as e:
            logger.error(f"❌ Erreur d'import incrémental: {e}")


def generate_demo_report():
    """Génère un rapport de démonstration complet"""
    logger.info("=== GÉNÉRATION DU RAPPORT DE DÉMONSTRATION ===")
    
    try:
        pipeline = ETLPipeline()
        # Utilisation de la configuration automatique
        db_config = get_db_config()
        db_manager = DatabaseManager(**db_config)
        
        # Statistiques finales de la base
        if db_manager.test_connection():
            stats = db_manager.get_database_stats()
            
            logger.info("📊 RAPPORT FINAL:")
            logger.info(f"   - Sessions totales: {stats['total_sessions']}")
            logger.info(f"   - Séries totales: {stats['total_sets']}")
            logger.info(f"   - Exercices uniques: {stats['unique_exercises']}")
            logger.info(f"   - Exercices catalogués: {stats['catalogued_exercises']}")
            
            if stats['date_range']['start'] and stats['date_range']['end']:
                logger.info(f"   - Période couverte: {stats['date_range']['start']} à {stats['date_range']['end']}")
        
        # Test de génération de rapport de synthèse
        examples_dir = Path(__file__).parent
        csv_file = examples_dir / 'sample_data.csv'
        
        if csv_file.exists():
            df = pipeline.process_file(csv_file)
            if not df.empty:
                summary_report = pipeline.generate_summary_report(df)
                logger.info(f"📄 RAPPORT DE SYNTHÈSE DES DONNÉES:\n{summary_report}")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la génération du rapport: {e}")


def main():
    """Fonction principale de démonstration"""
    logger.info("DÉMONSTRATION DU PIPELINE ETL - MUSCLE ANALYTICS")
    logger.info("=" * 60)
    
    try:
        # 1. Test de connexion
        if not test_database_connection():
            logger.error("ARRÊT de la démonstration - problème de base de données")
            return
        
        logger.info('')  # Ligne vide pour la lisibilité
        
        # 2. Test du pipeline
        test_pipeline_processing()
        logger.info('')
        
        # 3. Test d'import
        test_database_import()
        logger.info('')
        
        # 4. Test d'import incrémental
        test_incremental_import()
        logger.info('')
        
        # 5. Rapport final
        generate_demo_report()
        
        logger.info("DÉMONSTRATION TERMINÉE AVEC SUCCÈS")
        
    except KeyboardInterrupt:
        logger.info("Démonstration interrompue par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        raise


if __name__ == "__main__":
    main()
