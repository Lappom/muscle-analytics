"""
Module utilitaire pour générer des données de démonstration déterministes.

Ce module propose différentes stratégies pour créer des données d'entraînement
reproductibles pour les démonstrations et tests.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class DeterministicDataGenerator:
    """
    Générateur de données d'entraînement déterministes.
    
    Utilise des patterns mathématiques pour simuler des progressions réalistes
    sans recourir à l'aléatoire pur.
    """
    
    def __init__(self, seed: Optional[int] = 42):
        """
        Initialise le générateur.
        
        Args:
            seed: Graine pour la reproductibilité (optionnel)
        """
        if seed is not None:
            np.random.seed(seed)
        self.seed = seed
    
    def create_exercise_progression(
        self, 
        exercise_name: str,
        base_weight: float,
        weekly_progression: float,
        weeks: int = 6
    ) -> Dict[str, float]:
        """
        Crée une progression déterministe pour un exercice.
        
        Args:
            exercise_name: Nom de l'exercice
            base_weight: Poids de base
            weekly_progression: Progression hebdomadaire
            weeks: Nombre de semaines
            
        Returns:
            Dictionnaire avec les poids par semaine
        """
        progression = {}
        for week in range(weeks):
            # Progression linéaire avec petites variations
            base_increase = week * weekly_progression
            # Variation basée sur le hash du nom pour la cohérence
            name_variation = (hash(exercise_name) % 10) / 10.0
            week_weight = base_weight + base_increase + name_variation
            progression[f'week_{week}'] = round(week_weight, 1)
        
        return progression
    
    def generate_set_pattern(
        self, 
        exercise_index: int, 
        week: int, 
        session: int, 
        set_num: int
    ) -> Tuple[int, float]:
        """
        Génère un pattern déterministe pour les répétitions et l'intensité.
        
        Args:
            exercise_index: Index de l'exercice (pour variation)
            week: Semaine d'entraînement
            session: Numéro de session dans la semaine
            set_num: Numéro de série (0-2)
            
        Returns:
            Tuple (répétitions, multiplicateur d'intensité)
        """
        # Créer un "hash" déterministe à partir des paramètres
        pattern_seed = (exercise_index * 1000) + (week * 100) + (session * 10) + set_num
        
        # Patterns de répétitions par série
        rep_patterns = {
            0: [10, 11, 12, 10, 11],  # Premier set: volume élevé
            1: [8, 9, 10, 8, 9],      # Deuxième set: intensité élevée
            2: [6, 7, 8, 9, 6]       # Troisième set: fatigue
        }
        
        # Patterns d'intensité par série
        intensity_patterns = {
            0: 0.90,  # Premier set: 90% du poids de travail
            1: 1.00,  # Deuxième set: 100% du poids de travail
            2: 0.95   # Troisième set: 95% du poids de travail
        }
        
        # Sélectionner les répétitions de façon déterministe
        reps = rep_patterns[set_num][pattern_seed % len(rep_patterns[set_num])]
        intensity = intensity_patterns[set_num]
        
        return reps, intensity
    
    def create_training_data(
        self,
        exercises_config: Dict[str, Dict],
        weeks: int = 6,
        sessions_per_week: int = 2
    ) -> pd.DataFrame:
        """
        Crée un dataset d'entraînement complet de façon déterministe.
        
        Args:
            exercises_config: Configuration des exercices
                Format: {
                    'nom_exercice': {
                        'base_weight': float,
                        'weekly_progression': float
                    }
                }
            weeks: Nombre de semaines
            sessions_per_week: Sessions par semaine
            
        Returns:
            DataFrame avec les données d'entraînement
        """
        data = []
        session_id = 1
        
        for week in range(weeks):
            for session in range(sessions_per_week):
                for exercise_idx, (exercise_name, config) in enumerate(exercises_config.items()):
                    # Calculer le poids de travail pour cette semaine
                    base_weight = config['base_weight']
                    progression = config['weekly_progression']
                    current_weight = base_weight + (week * progression)
                    
                    # Générer 3 sets par exercice
                    for set_num in range(3):
                        reps, intensity_mult = self.generate_set_pattern(
                            exercise_idx, week, session, set_num
                        )
                        
                        weight = round(current_weight * intensity_mult, 1)
                        
                        data.append({
                            'session_id': session_id,
                            'exercise': exercise_name,
                            'series_type': 'principale',
                            'reps': reps,
                            'weight_kg': weight,
                            'skipped': False,
                            'notes': f'S{week+1}-Session{session+1}-Set{set_num+1}',
                            'week': week + 1,
                            'session_in_week': session + 1,
                            'set_number': set_num + 1
                        })
                
                session_id += 1
        
        return pd.DataFrame(data)
    
    def add_warmup_sets(
        self, 
        df: pd.DataFrame, 
        warmup_frequency: int = 3
    ) -> pd.DataFrame:
        """
        Ajoute des sets d'échauffement de façon déterministe.
        
        Args:
            df: DataFrame de base
            warmup_frequency: Fréquence d'échauffement (toutes les N séances)
            
        Returns:
            DataFrame avec échauffements ajoutés
        """
        warmup_data = []
        unique_sessions = df['session_id'].unique()
        
        for session_id in unique_sessions[::warmup_frequency]:
            # Exercices principaux pour cette session
            session_exercises = df[df['session_id'] == session_id]['exercise'].unique()
            
            for exercise in session_exercises[:2]:  # Échauffement pour 2 exercices max
                warmup_data.append({
                    'session_id': session_id,
                    'exercise': exercise,
                    'series_type': 'échauffement',
                    'reps': 15,
                    'weight_kg': 40.0,  # Poids fixe d'échauffement
                    'skipped': False,
                    'notes': 'Échauffement',
                    'week': df[df['session_id'] == session_id]['week'].iloc[0],
                    'session_in_week': df[df['session_id'] == session_id]['session_in_week'].iloc[0],
                    'set_number': 0  # Set 0 pour échauffement
                })
        
        return pd.concat([df, pd.DataFrame(warmup_data)], ignore_index=True)
    
    def create_sessions_dataframe(
        self, 
        num_sessions: int, 
        start_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Crée un DataFrame des sessions avec dates déterministes.
        
        Args:
            num_sessions: Nombre total de sessions
            start_date: Date de début (par défaut: 1er janvier 2023)
            
        Returns:
            DataFrame des sessions
        """
        if start_date is None:
            start_date = datetime(2023, 1, 1)
        
        sessions = []
        
        for i in range(num_sessions):
            week = i // 2
            session_in_week = i % 2
            
            # Lundi et jeudi pour chaque semaine
            if session_in_week == 0:
                session_date = start_date + timedelta(weeks=week)
            else:
                session_date = start_date + timedelta(weeks=week, days=3)
            
            sessions.append({
                'id': i + 1,
                'date': session_date.date(),
                'training_name': f'Session {i + 1}',
                'notes': f'Semaine {week + 1}, Séance {session_in_week + 1}',
                'week': week + 1,
                'session_in_week': session_in_week + 1
            })
        
        return pd.DataFrame(sessions)


# Configuration par défaut pour les démonstrations
DEFAULT_EXERCISES_CONFIG = {
    'Bench Press': {
        'base_weight': 80.0,
        'weekly_progression': 2.5
    },
    'Squat': {
        'base_weight': 100.0,
        'weekly_progression': 5.0
    },
    'Deadlift': {
        'base_weight': 120.0,
        'weekly_progression': 5.0
    },
    'Overhead Press': {
        'base_weight': 50.0,
        'weekly_progression': 1.25
    }
}


def create_demo_dataset(
    exercises_config: Optional[Dict] = None,
    weeks: int = 6,
    sessions_per_week: int = 2,
    include_warmup: bool = True,
    seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fonction utilitaire pour créer rapidement un dataset de démonstration.
    
    Args:
        exercises_config: Configuration des exercices (utilise la config par défaut si None)
        weeks: Nombre de semaines
        sessions_per_week: Sessions par semaine
        include_warmup: Inclure les échauffements
        seed: Graine pour reproductibilité
        
    Returns:
        Tuple (DataFrame d'entraînement, DataFrame des sessions)
    """
    if exercises_config is None:
        exercises_config = DEFAULT_EXERCISES_CONFIG
    
    generator = DeterministicDataGenerator(seed=seed)
    
    # Créer les données d'entraînement
    training_df = generator.create_training_data(
        exercises_config, weeks, sessions_per_week
    )
    
    # Ajouter les échauffements si demandé
    if include_warmup:
        training_df = generator.add_warmup_sets(training_df)
    
    # Créer le DataFrame des sessions
    num_sessions = training_df['session_id'].nunique()
    sessions_df = generator.create_sessions_dataframe(num_sessions)
    
    return training_df, sessions_df


if __name__ == '__main__':
    # Démonstration du générateur
    print("=== Démonstration du générateur de données déterministes ===\n")
    
    # Créer un dataset de démonstration
    training_data, sessions_data = create_demo_dataset()
    
    print(f"Dataset créé avec {len(training_data)} enregistrements sur {len(sessions_data)} sessions")
    print(f"Exercices: {', '.join(training_data['exercise'].unique())}")
    print(f"Types de séries: {', '.join(training_data['series_type'].unique())}")
    
    print("\nAperçu des données d'entraînement:")
    print(training_data.head(10)[['session_id', 'exercise', 'reps', 'weight_kg', 'series_type']].to_string(index=False))
    
    print("\nAperçu des sessions:")
    print(sessions_data.head()[['id', 'date', 'training_name', 'week']].to_string(index=False))
    
    # Test de reproductibilité
    print("\n=== Test de reproductibilité ===")
    data1, _ = create_demo_dataset(seed=42)
    data2, _ = create_demo_dataset(seed=42)
    
    print(f"Les deux datasets sont identiques: {data1.equals(data2)}")
