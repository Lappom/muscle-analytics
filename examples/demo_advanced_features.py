"""
Script de démonstration des calculs de features avancées.

Ce script montre comment utiliser les nouveaux modules de calcul :
- Volume d'entraînement
- 1RM estimé
- Progression et tendances
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta

# Ajouter le chemin src pour les imports
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(project_root)

from src.features.calculations import FeatureCalculator
from src.features.volume import VolumeCalculator
from src.features.one_rm import OneRMCalculator
from src.features.progression import ProgressionAnalyzer


def create_sample_data():
    """Crée des données d'exemple pour la démonstration."""
    # Données d'entraînement simulées sur 6 semaines
    data = []
    session_id = 1
    
    # Progression réaliste sur 6 semaines
    exercises = {
        'Bench Press': {'start_weight': 80, 'progression': 2.5},
        'Squat': {'start_weight': 100, 'progression': 5},
        'Deadlift': {'start_weight': 120, 'progression': 5},
        'Overhead Press': {'start_weight': 50, 'progression': 1.25}
    }
    
    for week in range(6):
        for session in range(2):  # 2 séances par semaine
            for exercise, params in exercises.items():
                # Progression du poids
                current_weight = params['start_weight'] + (week * params['progression'])
                
                # 3 sets par exercice avec variation
                for set_num in range(3):
                    if set_num == 0:  # Premier set - plus de reps
                        reps = np.random.randint(10, 12)
                        weight = current_weight * 0.9
                    elif set_num == 1:  # Deuxième set - poids max
                        reps = np.random.randint(8, 10)
                        weight = current_weight
                    else:  # Troisième set - fatigue
                        reps = np.random.randint(6, 9)
                        weight = current_weight * 0.95
                    
                    data.append({
                        'session_id': session_id,
                        'exercise': exercise,
                        'series_type': 'principale',
                        'reps': reps,
                        'weight_kg': round(weight, 1),
                        'skipped': False,
                        'notes': f'Set {set_num + 1}'
                    })
            
            session_id += 1
    
    # Ajouter quelques sets d'échauffement
    warmup_data = []
    for i in range(0, session_id, 3):  # Échauffement toutes les 3 séances
        warmup_data.append({
            'session_id': i + 1,
            'exercise': 'Bench Press',
            'series_type': 'échauffement',
            'reps': 15,
            'weight_kg': 40,
            'skipped': False,
            'notes': 'Échauffement'
        })
    
    data.extend(warmup_data)
    
    return pd.DataFrame(data)


def create_sessions_data(num_sessions):
    """Crée les données de séances."""
    sessions = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(num_sessions):
        # 2 séances par semaine (lundi et jeudi)
        week = i // 2
        session_in_week = i % 2
        
        if session_in_week == 0:
            # Lundi
            session_date = start_date + timedelta(weeks=week)
        else:
            # Jeudi
            session_date = start_date + timedelta(weeks=week, days=3)
        
        sessions.append({
            'id': i + 1,
            'date': session_date.date(),
            'training_name': f'Session {i + 1}',
            'notes': f'Semaine {week + 1}, Séance {session_in_week + 1}'
        })
    
    return pd.DataFrame(sessions)


def demo_volume_calculations():
    """Démonstration des calculs de volume."""
    print("=== 📊 DÉMONSTRATION DES CALCULS DE VOLUME ===\n")
    
    # Créer données d'exemple
    df = create_sample_data()
    sessions_df = create_sessions_data(df['session_id'].nunique())
    
    # Initialiser calculateur
    volume_calc = VolumeCalculator()
    
    # 1. Volume par set
    print("1. Calcul du volume par set (reps × poids):")
    df_with_volume = volume_calc.calculate_set_volume(df)
    sample_sets = df_with_volume.head(5)[['exercise', 'reps', 'weight_kg', 'volume']]
    print(sample_sets.to_string(index=False))
    print()
    
    # 2. Volume par séance
    print("2. Volume par séance et par exercice:")
    session_volumes = volume_calc.calculate_session_volume(df_with_volume)
    print(session_volumes.head(10)[['session_id', 'exercise', 'volume_sum', 'volume_count']].to_string(index=False))
    print()
    
    # 3. Volume hebdomadaire
    print("3. Volume hebdomadaire:")
    weekly_volumes = volume_calc.calculate_weekly_volume(df_with_volume, sessions_df)
    print(weekly_volumes.head(8)[['week', 'exercise', 'volume_sum', 'sessions_count']].to_string(index=False))
    print()
    
    # 4. Résumé complet
    print("4. Résumé des volumes:")
    volume_summary = volume_calc.get_volume_summary(df_with_volume, sessions_df)
    print(f"Volume total: {volume_summary['total_volume']:.0f} kg")
    print(f"Sets totaux: {volume_summary['total_sets']}")
    print(f"Volume moyen par set: {volume_summary['avg_volume_per_set']:.1f} kg")
    print(f"Volume moyen par séance: {volume_summary['avg_volume_per_session']:.1f} kg")
    print()


def demo_one_rm_calculations():
    """Démonstration des calculs de 1RM."""
    print("=== 💪 DÉMONSTRATION DES CALCULS DE 1RM ===\n")
    
    # Créer données d'exemple
    df = create_sample_data()
    sessions_df = create_sessions_data(df['session_id'].nunique())
    
    # Initialiser calculateur
    one_rm_calc = OneRMCalculator()
    
    # 1. Calculs individuels
    print("1. Exemples de calculs 1RM pour différentes formules:")
    test_cases = [(100, 5), (80, 10), (120, 3)]
    
    for weight, reps in test_cases:
        results = one_rm_calc.calculate_all_formulas(weight, reps)
        print(f"Poids: {weight}kg, Reps: {reps}")
        for formula, value in results.items():
            print(f"  {formula}: {value:.1f}kg")
        print()
    
    # 2. Calcul sur DataFrame
    print("2. 1RM calculé sur les données d'entraînement:")
    df_with_1rm = one_rm_calc.calculate_dataframe_1rm(df, formulas=['epley', 'brzycki'])
    
    # Afficher quelques exemples
    sample_1rm = df_with_1rm[df_with_1rm['one_rm_epley'].notna()].head(5)
    print(sample_1rm[['exercise', 'reps', 'weight_kg', 'one_rm_epley', 'one_rm_brzycki']].to_string(index=False))
    print()
    
    # 3. 1RM maximum par exercice
    print("3. 1RM maximum par exercice:")
    max_1rm = one_rm_calc.get_max_1rm_by_exercise(df_with_1rm)
    print(max_1rm[['exercise', 'one_rm_epley', 'one_rm_brzycki', 'weight_kg_max']].to_string(index=False))
    print()
    
    # 4. Progression 1RM
    print("4. Progression du 1RM au fil du temps:")
    progression_1rm = one_rm_calc.calculate_1rm_progression(df_with_1rm, sessions_df)
    
    # Afficher progression pour Bench Press
    bench_progression = progression_1rm[progression_1rm['exercise'] == 'Bench Press'].tail(5)
    if not bench_progression.empty:
        print("Progression Bench Press (5 dernières séances):")
        print(bench_progression[['date', 'one_rm_epley', 'one_rm_epley_progression', 'one_rm_epley_progression_pct']].to_string(index=False))
    print()


def demo_progression_analysis():
    """Démonstration de l'analyse de progression."""
    print("=== 📈 DÉMONSTRATION DE L'ANALYSE DE PROGRESSION ===\n")
    
    # Créer données d'exemple
    df = create_sample_data()
    sessions_df = create_sessions_data(df['session_id'].nunique())
    
    # Initialiser analyseur
    progression_analyzer = ProgressionAnalyzer()
    
    # 1. Progression du volume
    print("1. Progression du volume par exercice:")
    volume_progression = progression_analyzer.calculate_volume_progression(df, sessions_df)
    
    # Afficher progression pour un exercice
    squat_progression = volume_progression[volume_progression['exercise'] == 'Squat'].tail(5)
    if not squat_progression.empty:
        print("Progression Squat (5 dernières séances):")
        print(squat_progression[['date', 'volume', 'volume_progression', 'volume_progression_pct']].to_string(index=False))
    print()
    
    # 2. Métriques de performance
    print("2. Métriques de performance globales:")
    performance_metrics = progression_analyzer.calculate_performance_metrics(df, sessions_df)
    
    global_metrics = performance_metrics['global_metrics']
    print(f"Total exercices: {global_metrics['total_exercises']}")
    print(f"Exercices en progression: {global_metrics['exercises_in_progression']}")
    print(f"Exercices en plateau: {global_metrics['exercises_in_plateau']}")
    print(f"Progression moyenne: {global_metrics['avg_volume_progression']:.1f}%")
    print()
    
    # 3. Métriques par exercice
    print("3. Métriques détaillées par exercice:")
    exercise_metrics = performance_metrics['exercise_metrics']
    
    for exercise, metrics in exercise_metrics.items():
        print(f"{exercise}:")
        print(f"  Séances: {metrics['sessions_count']}")
        print(f"  Progression volume: {metrics['volume_progression_total_pct']:.1f}%")
        print(f"  En plateau: {'Oui' if metrics['current_plateau'] else 'Non'}")
        print()
    
    # 4. Rapport complet avec recommandations
    print("4. Recommandations basées sur la progression:")
    report = progression_analyzer.generate_progression_report(df, sessions_df)
    
    recommendations = report['recommendations']
    for i, rec in enumerate(recommendations[:5], 1):  # Limiter à 5 recommandations
        print(f"{i}. {rec}")
    print()


def demo_complete_analysis():
    """Démonstration de l'analyse complète."""
    print("=== 🎯 ANALYSE COMPLÈTE AVEC FEATURE CALCULATOR ===\n")
    
    # Créer données d'exemple
    df = create_sample_data()
    sessions_df = create_sessions_data(df['session_id'].nunique())
    
    # Initialiser calculateur principal
    feature_calc = FeatureCalculator()
    
    # 1. Calcul de toutes les features
    print("1. Calcul de toutes les features avancées:")
    df_with_features = feature_calc.calculate_all_features(df, sessions_df)
    
    feature_cols = ['volume', 'one_rm_epley', 'one_rm_brzycki', 'intensity_relative', 'volume_density']
    sample_features = df_with_features[df_with_features['series_type'] == 'principale'].head(5)
    print("Exemple de features calculées:")
    print(sample_features[['exercise', 'reps', 'weight_kg'] + feature_cols].to_string(index=False))
    print()
    
    # 2. Résumé d'une séance
    print("2. Résumé détaillé d'une séance:")
    session_summary = feature_calc.generate_session_summary(df_with_features, session_id=5, sessions_df=sessions_df)
    
    print(f"Séance {session_summary['session_id']} du {session_summary['date']}")
    print(f"Exercices: {', '.join(session_summary['exercises'])}")
    print(f"Sets totaux: {session_summary['total_sets']}")
    print(f"Volume total: {session_summary['total_volume']:.0f} kg")
    print(f"Intensité moyenne: {session_summary['avg_intensity']:.1f} kg")
    print()
    
    print("Détail par exercice:")
    for exercise, details in session_summary['exercise_breakdown'].items():
        print(f"  {exercise}:")
        print(f"    Sets: {details['sets_count']}")
        print(f"    Volume: {details['total_volume']:.0f} kg")
        print(f"    Poids max: {details['max_weight']:.1f} kg")
        print(f"    1RM estimé: {details['max_1rm_epley']:.1f} kg" if details['max_1rm_epley'] else "")
    print()
    
    # 3. Analyse complète
    print("3. Statistiques globales de l'analyse:")
    complete_analysis = feature_calc.generate_complete_analysis(df_with_features, sessions_df)
    
    global_stats = complete_analysis['global_statistics']
    print(f"Période analysée: {global_stats['date_range']['start']} à {global_stats['date_range']['end']}")
    print(f"Durée: {global_stats['date_range']['duration_days']} jours")
    print(f"Séances totales: {global_stats['total_sessions']}")
    print(f"Exercices différents: {global_stats['total_exercises']}")
    print(f"Sets totaux: {global_stats['total_sets']}")
    print(f"Volume total: {global_stats['total_volume']:.0f} kg")
    print(f"Volume moyen par séance: {global_stats['avg_session_volume']:.0f} kg")
    print()
    
    # 4. Export des données
    print("4. Export des données avec features:")
    # Construire le chemin d'export relatif au script et s'assurer que le dossier existe
    export_dir = os.path.dirname(__file__)  # Dossier du script courant (examples)
    export_path = os.path.join(export_dir, 'demo_features_export.csv')
    output_file = feature_calc.export_features_to_csv(df, sessions_df, export_path)
    print(f"Données exportées vers: {output_file}")
    print()


def main():
    """Fonction principale pour exécuter toutes les démonstrations."""
    print("🚀 DÉMONSTRATION DES FEATURES AVANCÉES - MUSCLE ANALYTICS")
    print("=" * 60)
    print()
    
    try:
        # Exécuter toutes les démonstrations
        demo_volume_calculations()
        demo_one_rm_calculations()
        demo_progression_analysis()
        demo_complete_analysis()
        
        print("✅ Toutes les démonstrations ont été exécutées avec succès!")
        print("\nLes nouveaux modules de features avancées sont prêts à être utilisés:")
        print("- 📊 VolumeCalculator: Calculs de volume d'entraînement")
        print("- 💪 OneRMCalculator: Estimation du 1RM avec plusieurs formules")
        print("- 📈 ProgressionAnalyzer: Analyse de progression et détection de plateaux")
        print("- 🎯 FeatureCalculator: Orchestration de tous les calculs")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
