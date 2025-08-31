"""
Module de calcul du volume d'entraînement.

Ce module fournit des fonctions pour calculer différentes métriques de volume :
- Volume par set (répétitions × poids)
- Volume par séance
- Volume par semaine/mois
- Moyennes mobiles de volume
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class VolumeCalculator:
    """Calculateur de volumes d'entraînement."""
    
    def __init__(self, week_start_day: str = 'MON'):
        """
        Initialise le calculateur de volume.
        
        Args:
            week_start_day: Jour de début de semaine ('MON', 'SUN', 'TUE', etc.)
                          Par défaut 'MON' (lundi)
        """
        # Valider le jour de début de semaine
        valid_days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
        if week_start_day not in valid_days:
            raise ValueError(f"week_start_day doit être l'un de: {valid_days}")
        
        self.week_start_day = week_start_day
    
    def calculate_set_volume(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcule le volume par set (répétitions × poids).
        
        Args:
            df: DataFrame avec colonnes 'reps' et 'weight_kg'
            
        Returns:
            DataFrame avec colonne 'volume' ajoutée
        """
        df = df.copy()
        
        # Validation des données avant calcul
        # Remplacer les valeurs invalides par 0
        valid_reps = df['reps'].fillna(0)
        valid_weight = df['weight_kg'].fillna(0)
        
        # Valider que les poids et reps sont positifs
        valid_reps = valid_reps.where(valid_reps > 0, 0)
        valid_weight = valid_weight.where(valid_weight > 0, 0)
        
        # Calcul du volume (reps × poids) avec données validées
        df['volume'] = valid_reps * valid_weight
        
        # Volume à 0 pour les sets skipped ou sans données valides
        df.loc[df['skipped'] == True, 'volume'] = 0
        df.loc[(df['reps'].isna()) | (df['weight_kg'].isna()), 'volume'] = 0
        
        return df
    
    def calculate_session_volume(self, df: pd.DataFrame, 
                               group_by_exercise: bool = True) -> pd.DataFrame:
        """
        Calcule le volume par séance.
        
        Args:
            df: DataFrame avec volumes calculés et session_id
            group_by_exercise: Si True, groupe par exercice et séance
            
        Returns:
            DataFrame avec volumes par séance
        """
        # S'assurer que le volume est calculé
        if 'volume' not in df.columns:
            df = self.calculate_set_volume(df)
        
        # Filtrer les sets non-skipped et de type 'working_set'
        mask = (df['skipped'] != True) & (df['series_type'] == 'working_set')
        working_sets = df[mask].copy()
        
        # Si aucun set working_set, retourner un DataFrame vide avec la bonne structure
        if working_sets.empty:
            if group_by_exercise:
                return pd.DataFrame(columns=['session_id', 'exercise', 'volume_sum', 'volume_count', 
                                           'volume_mean', 'reps_sum', 'reps_mean', 'weight_kg_max', 'weight_kg_mean'])
            else:
                return pd.DataFrame(columns=['session_id', 'volume_sum', 'volume_count', 
                                           'volume_mean', 'exercise_count'])
        
        if group_by_exercise:
            # Volume par exercice et par séance
            session_volumes = (working_sets
                             .groupby(['session_id', 'exercise'])
                             .agg({
                                 'volume': ['sum', 'count', 'mean'],
                                 'reps': ['sum', 'mean'],
                                 'weight_kg': ['max', 'mean']
                             })
                             .round(2))
            
            # Aplatir les colonnes multi-niveau
            session_volumes.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] 
                                     for col in session_volumes.columns]
            session_volumes = session_volumes.reset_index()
            
        else:
            # Volume total par séance (tous exercices confondus)
            session_stats = working_sets.groupby('session_id').agg({
                'volume': ['sum', 'count', 'mean'],
                'exercise': 'nunique'  # Nombre d'exercices différents
            })
            session_volumes = session_stats.round(2)
            
            session_volumes.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] 
                                     for col in session_volumes.columns]
            session_volumes = session_volumes.reset_index()
            session_volumes.rename(columns={'exercise_nunique': 'exercise_count'}, 
                                 inplace=True)
        
        return session_volumes
    
    def calculate_weekly_volume(self, df: pd.DataFrame, 
                              sessions_df: Optional[pd.DataFrame] = None,
                              week_start_day: Optional[str] = None) -> pd.DataFrame:
        """
        Calcule le volume hebdomadaire.
        
        Args:
            df: DataFrame avec volumes calculés
            sessions_df: DataFrame des séances avec dates (optionnel)
            week_start_day: Jour de début de semaine (optionnel, utilise la config de l'instance par défaut)
            
        Returns:
            DataFrame avec volumes hebdomadaires
        """
        # S'assurer que le volume est calculé
        if 'volume' not in df.columns:
            df = self.calculate_set_volume(df)
        
        # Joindre avec les dates des séances si fourni
        if sessions_df is not None:
            df_with_dates = df.merge(sessions_df[['id', 'date']], 
                                   left_on='session_id', right_on='id', 
                                   how='left')
            df_with_dates['date'] = pd.to_datetime(df_with_dates['date'])
        else:
            # Assumer que df contient déjà une colonne date
            df_with_dates = df.copy()
            df_with_dates['date'] = pd.to_datetime(df_with_dates['date'])
        
        # Déterminer le jour de début de semaine à utiliser
        start_day = week_start_day if week_start_day is not None else self.week_start_day
        
        # Calculer la semaine avec le jour de début configuré
        df_with_dates['week'] = df_with_dates['date'].dt.to_period(f'W-{start_day}')
        
        # Filtrer les sets principaux
        mask = (df_with_dates['skipped'] != True) & (df_with_dates['series_type'] == 'working_set')
        working_sets = df_with_dates[mask].copy()
        
        # Si aucun set working_set, retourner un DataFrame vide avec la bonne structure
        if working_sets.empty:
            return pd.DataFrame(columns=['week', 'exercise', 'volume_sum', 'volume_count', 'sessions_count'])
        
        # Volume par semaine et par exercice
        weekly_stats = working_sets.groupby(['week', 'exercise']).agg({
            'volume': ['sum', 'count'],
            'session_id': 'nunique'  # Nombre de séances
        })
        weekly_volumes = weekly_stats.round(2)
        
        weekly_volumes.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] 
                                for col in weekly_volumes.columns]
        weekly_volumes = weekly_volumes.reset_index()
        weekly_volumes.rename(columns={'session_id_nunique': 'sessions_count'}, 
                            inplace=True)
        
        return weekly_volumes
    
    def calculate_rolling_volume(self, df: pd.DataFrame, 
                               window_days: int = 7,
                               sessions_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Calcule les moyennes mobiles de volume.
        
        Args:
            df: DataFrame avec volumes calculés
            window_days: Taille de la fenêtre en jours
            sessions_df: DataFrame des séances avec dates
            
        Returns:
            DataFrame avec moyennes mobiles
        """
        # S'assurer que le volume est calculé
        if 'volume' not in df.columns:
            df = self.calculate_set_volume(df)
        
        # Joindre avec les dates des séances
        if sessions_df is not None:
            df_with_dates = df.merge(sessions_df[['id', 'date']], 
                                   left_on='session_id', right_on='id', 
                                   how='left')
        else:
            df_with_dates = df.copy()
        
        df_with_dates['date'] = pd.to_datetime(df_with_dates['date'])
        
        # Filtrer les sets principaux
        mask = (df_with_dates['skipped'] != True) & (df_with_dates['series_type'] == 'working_set')
        working_sets = df_with_dates[mask].copy()
        
        # Volume quotidien par exercice
        daily_volume = (working_sets
                       .groupby(['date', 'exercise'])
                       .agg({'volume': 'sum'})
                       .reset_index())
        
        # Calculer les moyennes mobiles par exercice
        rolling_data = []
        for exercise in daily_volume['exercise'].unique():
            exercise_data = daily_volume[daily_volume['exercise'] == exercise].copy()
            exercise_data = exercise_data.sort_values('date')
            
            # Moyenne mobile
            exercise_data[f'volume_ma_{window_days}d'] = (
                exercise_data['volume']
                .rolling(window=window_days, min_periods=1)
                .mean()
                .round(2)
            )
            
            rolling_data.append(exercise_data)
        
        rolling_volumes = pd.concat(rolling_data, ignore_index=True)
        return rolling_volumes
    
    def get_volume_summary(self, df: pd.DataFrame,
                          sessions_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Génère un résumé complet des volumes.
        
        Args:
            df: DataFrame avec les sets
            sessions_df: DataFrame des séances
            
        Returns:
            Dictionnaire avec statistiques de volume
        """
        # Calculer les volumes
        df_with_volume = self.calculate_set_volume(df)
        session_volumes = self.calculate_session_volume(df_with_volume)
        
        # Initialiser les variables pour les volumes avancés
        weekly_volumes = None
        rolling_volumes = None
        
        if sessions_df is not None:
            weekly_volumes = self.calculate_weekly_volume(df_with_volume, sessions_df)
            rolling_volumes = self.calculate_rolling_volume(df_with_volume, 
                                                          window_days=7, 
                                                          sessions_df=sessions_df)
        
        # Statistiques générales
        mask = (df_with_volume['skipped'] != True) & (df_with_volume['series_type'] == 'working_set')
        working_sets = df_with_volume[mask]
        
        summary = {
            'total_volume': working_sets['volume'].sum(),
            'total_sets': len(working_sets),
            'avg_volume_per_set': working_sets['volume'].mean(),
            'avg_volume_per_session': session_volumes['volume_sum'].mean(),
            'exercises_count': df_with_volume['exercise'].nunique(),
            'sessions_count': df_with_volume['session_id'].nunique(),
            'volume_distribution': {
                'min': working_sets['volume'].min(),
                'q25': working_sets['volume'].quantile(0.25),
                'median': working_sets['volume'].median(),
                'q75': working_sets['volume'].quantile(0.75),
                'max': working_sets['volume'].max(),
                'std': working_sets['volume'].std()
            }
        }
        
        # Ajouter les données détaillées
        summary['session_volumes'] = session_volumes
        if weekly_volumes is not None:
            summary['weekly_volumes'] = weekly_volumes
        if rolling_volumes is not None:
            summary['rolling_volumes'] = rolling_volumes
        
        return summary
