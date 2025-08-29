#!/usr/bin/env python3
"""
Démonstration du pipeline ETL Muscle-Analytics.

Script d'exemple montrant l'utilisation complète du pipeline.
"""

import sys
from pathlib import Path

# Ajout du chemin src pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from etl.pipeline import ETLPipeline
import logging

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Fonction principale de démonstration"""
    print("🚀 DÉMONSTRATION ETL MUSCLE-ANALYTICS")
    print("=" * 50)
    
    # Initialisation du pipeline
    pipeline = ETLPipeline()
    
    # Chemins vers les fichiers d'exemple
    current_dir = Path(__file__).parent
    csv_file = current_dir / 'sample_data.csv'
    xml_file = current_dir / 'sample_data.xml'
    
    print(f"\n📁 Fichiers de test:")
    print(f"- CSV: {csv_file}")
    print(f"- XML: {xml_file}")
    
    # Test 1: Traitement du fichier CSV
    print(f"\n🔄 Test 1: Traitement CSV")
    print("-" * 30)
    
    try:
        df_csv = pipeline.process_file(csv_file)
        print(f"✅ CSV traité avec succès: {len(df_csv)} lignes")
        
        # Affichage des premières lignes
        print("\n📊 Aperçu des données CSV normalisées:")
        print(df_csv[['date', 'exercise', 'reps', 'weight_kg', 'volume']].head())
        
    except Exception as e:
        print(f"❌ Erreur CSV: {e}")
    
    # Test 2: Traitement du fichier XML
    print(f"\n🔄 Test 2: Traitement XML")
    print("-" * 30)
    
    try:
        df_xml = pipeline.process_file(xml_file)
        print(f"✅ XML traité avec succès: {len(df_xml)} lignes")
        
        # Affichage des premières lignes
        print("\n📊 Aperçu des données XML normalisées:")
        print(df_xml[['date', 'exercise', 'reps', 'weight_kg', 'volume']].head())
        
    except Exception as e:
        print(f"❌ Erreur XML: {e}")
    
    # Test 3: Traitement multiple
    print(f"\n🔄 Test 3: Traitement multiple")
    print("-" * 30)
    
    try:
        df_combined = pipeline.process_multiple_files([csv_file, xml_file])
        print(f"✅ Traitement multiple réussi: {len(df_combined)} lignes totales")
        
        # Rapport de qualité
        quality = pipeline.validate_data_quality(df_combined)
        print(f"\n📈 Qualité des données: {quality['quality_percentage']:.1f}%")
        print(f"   - Séries valides: {quality['valid_sets']}/{quality['total_rows']}")
        print(f"   - Séries sautées: {quality['skipped_sets']}")
        
        # Statistiques par exercice
        print(f"\n💪 Répartition par exercice:")
        exercise_counts = df_combined['exercise'].value_counts()
        for exercise, count in exercise_counts.head().items():
            print(f"   - {exercise}: {count} séries")
        
        # Volume total par entraînement
        if 'training' in df_combined.columns and 'volume' in df_combined.columns:
            print(f"\n🏋️ Volume par entraînement:")
            volume_by_training = df_combined.groupby('training')['volume'].sum().sort_values(ascending=False)
            for training, volume in volume_by_training.head().items():
                print(f"   - {training}: {volume:.1f} kg")
        
    except Exception as e:
        print(f"❌ Erreur traitement multiple: {e}")
    
    # Test 4: Rapport de synthèse
    print(f"\n📋 Rapport de synthèse complet:")
    print("-" * 30)
    
    try:
        report = pipeline.generate_summary_report(df_combined)
        print(report)
        
    except Exception as e:
        print(f"❌ Erreur génération rapport: {e}")
    
    print(f"\n✨ Démonstration terminée!")


if __name__ == '__main__':
    main()

