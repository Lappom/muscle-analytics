"""
Module principal de calcul des features avancées.

Ce module orchestre tous les calculs de features :
- Volume d'entraînement
- 1RM estimé
- Progression et tendances
- Métriques de performance
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime

from .volume import VolumeCalculator
from .one_rm import OneRMCalculator
from .progression import ProgressionAnalyzer


class FeatureCalculator:
    """Calculateur principal pour toutes les features avancées."""
    
    # Constantes pour estimation de durée des sets
    SECONDS_PER_REP = 2.5      # Temps estimé par répétition (secondes)
    SET_REST_TIME = 60         # Temps de repos estimé entre les sets (secondes)
    
    def __init__(self):
        """Initialise le calculateur de features."""
        self.volume_calc = VolumeCalculator()
        self.one_rm_calc = OneRMCalculator()
        self.progression_analyzer = ProgressionAnalyzer()
    
    def calculate_estimated_set_duration(self, reps: Union[int, float]) -> float:
        """
        Calcule la durée estimée d'un set.
        
        Args:
            reps: Nombre de répétitions
            
        Returns:
            Durée estimée en secondes
        """
        if pd.isna(reps) or reps <= 0:
            return np.nan
        
        return reps * self.SECONDS_PER_REP + self.SET_REST_TIME
    
    def calculate_all_features(self, df: pd.DataFrame,
                             sessions_df: Optional[pd.DataFrame] = None,
                             include_1rm: bool = True,
                             include_progression: bool = True,
                             one_rm_formulas: List[str] = ['epley', 'brzycki']) -> pd.DataFrame:
        """
        Calcule toutes les features pour un DataFrame.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des séances avec dates
            include_1rm: Inclure calculs 1RM
            include_progression: Inclure analyse progression
            one_rm_formulas: Formules 1RM à utiliser
            
        Returns:
            DataFrame enrichi avec toutes les features
        """
        # Copie pour éviter modifications accidentelles
        result_df = df.copy()
        
        # 1. Calcul du volume
        result_df = self.volume_calc.calculate_set_volume(result_df)
        
        # 2. Calcul 1RM si demandé
        if include_1rm:
            result_df = self.one_rm_calc.calculate_dataframe_1rm(
                result_df, 
                formulas=one_rm_formulas
            )
        
        # 3. Ajout d'autres métriques calculées
        result_df = self._add_derived_features(result_df)
        
        return result_df
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajoute des features dérivées calculées.
        
        Args:
            df: DataFrame avec features de base
            
        Returns:
            DataFrame avec features supplémentaires
        """
        df = df.copy()
        
        # Filtrer les sets principaux pour les calculs
        main_sets_mask = (df['series_type'] == 'principale') & (df['skipped'] != True)
        
        # Intensité relative (poids / poids corporel si disponible)
        # Pour l'instant, normalisation par l'exercice
        exercise_max_weights = (df[main_sets_mask]
                              .groupby('exercise')['weight_kg']
                              .max())
        
        df['intensity_relative'] = df.apply(
            lambda row: (row['weight_kg'] / exercise_max_weights.get(row['exercise'], 1)
                        if pd.notna(row['weight_kg']) and exercise_max_weights.get(row['exercise'], 0) > 0
                        else np.nan),
            axis=1
        )
        
        # Densité du set (volume / temps estimé)
        # Utilisation de la méthode dédiée pour calculer la durée
        df['estimated_set_duration'] = df['reps'].apply(self.calculate_estimated_set_duration)
        df['volume_density'] = np.where(
            df['estimated_set_duration'] > 0,
            df['volume'] / df['estimated_set_duration'] * 60,  # volume par minute
            np.nan
        )
        
        # Fatigue index (différence entre premier et dernier set de la séance)
        session_exercise_groups = df[main_sets_mask].groupby(['session_id', 'exercise'])
        
        fatigue_data = []
        for (session_id, exercise), group in session_exercise_groups:
            if len(group) > 1:
                first_weight = group.iloc[0]['weight_kg']
                last_weight = group.iloc[-1]['weight_kg']
                first_reps = group.iloc[0]['reps']
                last_reps = group.iloc[-1]['reps']
                
                if pd.notna(first_weight) and pd.notna(last_weight) and first_weight > 0:
                    weight_fatigue = (last_weight - first_weight) / first_weight * 100
                else:
                    weight_fatigue = np.nan
                
                if pd.notna(first_reps) and pd.notna(last_reps) and first_reps > 0:
                    reps_fatigue = (last_reps - first_reps) / first_reps * 100
                else:
                    reps_fatigue = np.nan
                
                fatigue_data.append({
                    'session_id': session_id,
                    'exercise': exercise,
                    'weight_fatigue_pct': weight_fatigue,
                    'reps_fatigue_pct': reps_fatigue
                })
        
        if fatigue_data:
            fatigue_df = pd.DataFrame(fatigue_data)
            df = df.merge(fatigue_df, on=['session_id', 'exercise'], how='left')
        else:
            df['weight_fatigue_pct'] = np.nan
            df['reps_fatigue_pct'] = np.nan
        
        return df
    
    def generate_session_summary(self, df: pd.DataFrame,
                               session_id: int,
                               sessions_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Génère un résumé complet pour une séance.
        
        Args:
            df: DataFrame avec toutes les features
            session_id: ID de la séance à analyser
            sessions_df: DataFrame des séances
            
        Returns:
            Dictionnaire avec résumé de la séance
        """
        session_data = df[df['session_id'] == session_id].copy()
        
        if len(session_data) == 0:
            return {'error': f'Aucune donnée trouvée pour la séance {session_id}'}
        
        # S'assurer que les features sont calculées
        session_data = self.calculate_all_features(session_data, sessions_df)
        
        # Volume de la séance
        volume_summary = self.volume_calc.get_volume_summary(session_data, sessions_df)
        
        # 1RM de la séance
        one_rm_summary = self.one_rm_calc.get_1rm_summary(session_data, sessions_df)
        
        # Informations de base
        main_sets = session_data[
            (session_data['series_type'] == 'principale') & 
            (session_data['skipped'] != True)
        ]
        
        # Date de la séance
        session_date = None
        if sessions_df is not None:
            session_info = sessions_df[sessions_df['id'] == session_id]
            if len(session_info) > 0:
                session_date = session_info.iloc[0]['date']
        
        summary = {
            'session_id': session_id,
            'date': session_date,
            'exercises': list(main_sets['exercise'].unique()),
            'total_sets': len(main_sets),
            'total_volume': main_sets['volume'].sum(),
            'avg_intensity': main_sets['weight_kg'].mean(),
            'max_weight': main_sets['weight_kg'].max(),
            'total_reps': main_sets['reps'].sum(),
            'exercise_breakdown': {},
            'volume_metrics': volume_summary,
            'one_rm_metrics': one_rm_summary
        }
        
        # Détail par exercice
        for exercise in main_sets['exercise'].unique():
            exercise_data = main_sets[main_sets['exercise'] == exercise]
            
            exercise_summary = {
                'sets_count': len(exercise_data),
                'total_volume': exercise_data['volume'].sum(),
                'max_weight': exercise_data['weight_kg'].max(),
                'avg_weight': exercise_data['weight_kg'].mean(),
                'total_reps': exercise_data['reps'].sum(),
                'avg_reps': exercise_data['reps'].mean(),
                'max_1rm_epley': exercise_data['one_rm_epley'].max() if 'one_rm_epley' in exercise_data.columns else None,
                'avg_intensity_relative': exercise_data['intensity_relative'].mean() if 'intensity_relative' in exercise_data.columns else None,
                'fatigue_weight': exercise_data['weight_fatigue_pct'].iloc[0] if 'weight_fatigue_pct' in exercise_data.columns and not exercise_data['weight_fatigue_pct'].isna().all() else None,
                'fatigue_reps': exercise_data['reps_fatigue_pct'].iloc[0] if 'reps_fatigue_pct' in exercise_data.columns and not exercise_data['reps_fatigue_pct'].isna().all() else None
            }
            
            summary['exercise_breakdown'][exercise] = exercise_summary
        
        return summary
    
    def generate_complete_analysis(self, df: pd.DataFrame,
                                 sessions_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Génère une analyse complète de tous les données.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des séances
            
        Returns:
            Dictionnaire avec analyse complète
        """
        # Calculer toutes les features
        df_with_features = self.calculate_all_features(df, sessions_df)
        
        # Résumés par module
        volume_summary = self.volume_calc.get_volume_summary(df_with_features, sessions_df)
        one_rm_summary = self.one_rm_calc.get_1rm_summary(df_with_features, sessions_df)
        progression_report = self.progression_analyzer.generate_progression_report(
            df_with_features, sessions_df
        )
        
        # Statistiques globales
        main_sets = df_with_features[
            (df_with_features['series_type'] == 'principale') & 
            (df_with_features['skipped'] != True)
        ]
        
        global_stats = {
            'total_sessions': df_with_features['session_id'].nunique(),
            'total_exercises': df_with_features['exercise'].nunique(),
            'total_sets': len(main_sets),
            'total_volume': main_sets['volume'].sum(),
            'avg_session_volume': volume_summary['avg_volume_per_session'],
            'date_range': {
                'start': sessions_df['date'].min() if sessions_df is not None else 'N/A',
                'end': sessions_df['date'].max() if sessions_df is not None else 'N/A',
                'duration_days': (pd.to_datetime(sessions_df['date'].max()) - 
                                pd.to_datetime(sessions_df['date'].min())).days if sessions_df is not None else 0
            }
        }
        
        # Compilation finale
        complete_analysis = {
            'analysis_metadata': {
                'generated_at': datetime.now().isoformat(),
                'data_version': '1.0',
                'feature_calculator_version': '1.0'
            },
            'global_statistics': global_stats,
            'volume_analysis': volume_summary,
            'one_rm_analysis': one_rm_summary,
            'progression_analysis': progression_report,
            'raw_data_with_features': df_with_features
        }
        
        return complete_analysis
    
    def export_features_to_csv(self, df: pd.DataFrame,
                             sessions_df: Optional[pd.DataFrame] = None,
                             output_path: str = 'features_export.csv') -> str:
        """
        Exporte les données avec features calculées vers CSV.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des séances
            output_path: Chemin du fichier de sortie
            
        Returns:
            Chemin du fichier créé
        """
        # Calculer toutes les features
        df_with_features = self.calculate_all_features(df, sessions_df)
        
        # Joindre avec informations des séances si disponible
        if sessions_df is not None:
            df_export = df_with_features.merge(
                sessions_df[['id', 'date', 'training_name']], 
                left_on='session_id', 
                right_on='id', 
                how='left'
            )
            df_export = df_export.drop('id', axis=1)
        else:
            df_export = df_with_features
        
        # Réorganiser les colonnes pour plus de clarté
        base_cols = ['session_id', 'date', 'training_name', 'exercise', 'series_type', 
                    'reps', 'weight_kg', 'skipped']
        feature_cols = [col for col in df_export.columns if col not in base_cols]
        
        ordered_cols = []
        for col in base_cols:
            if col in df_export.columns:
                ordered_cols.append(col)
        ordered_cols.extend(feature_cols)
        
        df_export = df_export[ordered_cols]
        
        # Export
        df_export.to_csv(output_path, index=False)
        
        return output_path
