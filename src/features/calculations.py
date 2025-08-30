"""
Module principal de calcul des features avancées pour l'analyse de musculation.

Ce module combine tous les calculateurs spécialisés pour produire
un ensemble complet de features d'entraînement.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

from .volume import VolumeCalculator
from .one_rm import OneRMCalculator
from .progression import ProgressionAnalyzer

# Configuration du logger
logger = logging.getLogger(__name__)


class FeatureCalculator:
    """Calculateur principal pour toutes les features avancées."""
    
    # Valeurs par défaut pour l'estimation de durée
    DEFAULT_SECONDS_PER_REP = 4  # Temps moyen par répétition en secondes
    DEFAULT_SET_REST_TIME = 60   # Temps de récupération moyen entre séries
    
    def __init__(self, seconds_per_rep: float = DEFAULT_SECONDS_PER_REP, 
                 set_rest_time: float = DEFAULT_SET_REST_TIME):
        """
        Initialise les calculateurs spécialisés.
        
        Args:
            seconds_per_rep: Temps moyen par répétition en secondes (défaut: 4)
            set_rest_time: Temps de récupération moyen entre séries en secondes (défaut: 60)
        
        Examples:
            # Utilisation avec valeurs par défaut
            calc = FeatureCalculator()
            
            # Personnalisation pour un entraînement plus rapide
            calc_fast = FeatureCalculator(seconds_per_rep=3.0, set_rest_time=45.0)
        """
        self.volume_calculator = VolumeCalculator()
        self.one_rm_calculator = OneRMCalculator()
        self.progression_analyzer = ProgressionAnalyzer()
        
        # Configuration des paramètres de timing
        self.seconds_per_rep = seconds_per_rep
        self.set_rest_time = set_rest_time
    
    def calculate_estimated_set_duration(self, reps: Union[int, float]) -> float:
        """
        Calcule la durée estimée d'un set.
        
        Args:
            reps: Nombre de répétitions
            
        Returns:
            Durée estimée en secondes
        """
        # Validation que reps est un nombre positif valide
        if pd.isna(reps) or not isinstance(reps, (int, float)) or reps <= 0:
            return np.nan
        
        return reps * self.seconds_per_rep + self.set_rest_time
    
    def calculate_all_features(self, 
                             df: pd.DataFrame,
                             sessions_df: Optional[pd.DataFrame] = None,
                             include_1rm: bool = True,
                             one_rm_formulas: List[str] = ['epley', 'brzycki']) -> pd.DataFrame:
        """
        Calcule toutes les features pour un DataFrame.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des séances avec dates
            include_1rm: Inclure calculs 1RM
            one_rm_formulas: Formules 1RM à utiliser
            
        Returns:
            DataFrame enrichi avec toutes les features
        """
        # Copie pour éviter modifications accidentelles
        result_df = df.copy()
        
        # Validation des données d'entrée
        if result_df.empty:
            return result_df
        
        # === CALCULS VOLUME ===
        try:
            result_df = self.volume_calculator.calculate_set_volume(result_df)
        except Exception as e:
            logger.error(f"Erreur lors du calcul de volume: {e}", exc_info=True)
        
        # === CALCULS 1RM ===
        if include_1rm:
            try:
                result_df = self.one_rm_calculator.calculate_dataframe_1rm(
                    result_df, formulas=one_rm_formulas
                )
            except Exception as e:
                logger.error(f"Erreur lors du calcul 1RM: {e}", exc_info=True)
        
        # === CALCULS DE PROGRESSION ===
        # Note: Les calculs de progression retournent des DataFrames agrégés
        # On les stocke séparément pour éviter d'écraser result_df
        progression_data = {}
        try:
            volume_progression = self.progression_analyzer.calculate_volume_progression(result_df, sessions_df)
            progression_data['volume_progression'] = volume_progression
            
            intensity_progression = self.progression_analyzer.calculate_intensity_progression(result_df, sessions_df)
            progression_data['intensity_progression'] = intensity_progression
            
            # Détection de plateaux (nécessite des données de progression temporelles)
            # Skip si pas assez de données temporelles
            if sessions_df is not None and len(result_df) > 6:
                plateau_data = self.progression_analyzer.detect_plateaus(result_df, 'volume')
                progression_data['plateau_data'] = plateau_data
        except Exception as e:
            logger.error(f"Erreur lors du calcul de progression: {e}", exc_info=True)
        
        # === FEATURES DÉRIVÉES ===
        result_df = self._add_derived_features(result_df)
        
        # Optionnel: Stocker les données de progression dans les métadonnées
        if hasattr(result_df, 'attrs'):
            result_df.attrs['progression_data'] = progression_data
        
        return result_df
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajoute des features dérivées calculées à partir des features de base.
        
        Args:
            df: DataFrame avec features de base
            
        Returns:
            DataFrame avec features dérivées ajoutées
        """
        result_df = df.copy()
        
        # === INTENSITÉ ===
        if 'weight_kg' in result_df.columns and 'reps' in result_df.columns:
            # Intensité relative (ratio poids/reps)
            result_df['intensity_ratio'] = result_df['weight_kg'] / (result_df['reps'] + 1)
            result_df['intensity_relative'] = result_df['intensity_ratio']  # Alias pour compatibilité
            
            # Charge de travail par répétition
            result_df['workload_per_rep'] = result_df['weight_kg'] * result_df['reps']
        
        # === DURÉE ESTIMÉE ===
        if 'reps' in result_df.columns:
            result_df['estimated_duration_seconds'] = result_df['reps'].apply(
                self.calculate_estimated_set_duration
            )
            result_df['estimated_duration_minutes'] = result_df['estimated_duration_seconds'] / 60
        
        # === MÉTRIQUES DE QUALITÉ ===
        # Densité de volume (volume par minute estimée)
        if 'volume' in result_df.columns and 'estimated_duration_minutes' in result_df.columns:
            result_df['volume_density'] = result_df['volume'] / result_df['estimated_duration_minutes']
        
        # === CLASSIFICATION DES SÉRIES ===
        # Intensité relative par rapport au max de l'exercice
        for exercise in result_df['exercise'].unique():
            if pd.isna(exercise):
                continue
                
            exercise_data = result_df[result_df['exercise'] == exercise]
            
            if 'weight_kg' in exercise_data.columns:
                max_weight = exercise_data['weight_kg'].max()
                if max_weight > 0:
                    result_df.loc[result_df['exercise'] == exercise, 'weight_percentage_of_max'] = \
                        (result_df.loc[result_df['exercise'] == exercise, 'weight_kg'] / max_weight) * 100
        
        # === INDICATEURS DE PERFORMANCE ===
        # Évolution du volume par session
        if 'session_id' in result_df.columns and 'volume' in result_df.columns:
            session_volumes = result_df.groupby('session_id')['volume'].sum().reset_index()
            session_volumes['session_volume_ma3'] = session_volumes['volume'].rolling(
                window=3, min_periods=1
            ).mean()
            
            result_df = result_df.merge(
                session_volumes[['session_id', 'session_volume_ma3']], 
                on='session_id', how='left'
            )
        
        return result_df
    
    def generate_session_summary(self, df: pd.DataFrame,
                                session_id: Optional[int] = None,
                                sessions_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Génère un résumé des métriques pour une session.
        
        Args:
            df: DataFrame avec features calculées
            session_id: ID de session spécifique (optionnel)
            sessions_df: DataFrame des sessions avec données supplémentaires
            
        Returns:
            Dictionnaire avec métriques de session
        """
        if session_id:
            session_data = df[df['session_id'] == session_id]
        else:
            session_data = df
        
        if session_data.empty:
            return {}
        
        # Calcul des volumes si pas déjà fait
        if 'volume' not in session_data.columns:
            session_data = self.volume_calculator.calculate_set_volume(session_data)
        
        summary = {
            'session_id': session_id,
            'total_sets': len(session_data),
            'unique_exercises': session_data['exercise'].nunique(),
            'total_volume': session_data.get('volume', pd.Series()).sum(),
            'avg_weight': session_data.get('weight_kg', pd.Series()).mean(),
            'total_reps': session_data.get('reps', pd.Series()).sum(),
            'estimated_duration_minutes': session_data.get('estimated_duration_minutes', pd.Series()).sum(),
        }
        
        # Ajout des métriques avancées si disponibles
        if '1rm_average' in session_data.columns:
            summary['max_1rm_session'] = session_data['1rm_average'].max()
            summary['avg_1rm_session'] = session_data['1rm_average'].mean()
        
        if 'volume_density' in session_data.columns:
            summary['avg_volume_density'] = session_data['volume_density'].mean()
        
        # Exercices avec leur contribution au volume
        volume_by_exercise = session_data.groupby('exercise')['volume'].sum().to_dict() \
            if 'volume' in session_data.columns else {}
        summary['volume_by_exercise'] = volume_by_exercise
        summary['exercise_breakdown'] = volume_by_exercise  # Alias pour compatibilité
        summary['exercises'] = list(session_data['exercise'].unique())
        
        return summary
    
    def generate_complete_analysis(self, df: pd.DataFrame,
                                 sessions_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Génère une analyse complète des données d'entraînement.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des sessions
            
        Returns:
            Dictionnaire avec analyse complète
        """
        # Calcul de toutes les features
        features_df = self.calculate_all_features(df, sessions_df)
        
        analysis = {
            'analysis_metadata': {
                'total_sessions': features_df['session_id'].nunique() if 'session_id' in features_df.columns else 0,
                'total_sets': len(features_df),
                'unique_exercises': features_df['exercise'].nunique(),
                'date_range': {
                    'start': features_df['date'].min() if 'date' in features_df.columns else None,
                    'end': features_df['date'].max() if 'date' in features_df.columns else None
                }
            },
            'global_statistics': {
                'total_sessions': features_df['session_id'].nunique() if 'session_id' in features_df.columns else 0,
                'total_sets': len(features_df),
                'total_exercises': features_df['exercise'].nunique(),
                'date_range': {
                    'start': features_df['date'].min() if 'date' in features_df.columns else None,
                    'end': features_df['date'].max() if 'date' in features_df.columns else None
                }
            },
            'volume_analysis': self.volume_calculator.get_volume_summary(df, sessions_df),
            'strength_analysis': {},
            'progression_analysis': {},
            'raw_data_with_features': features_df  # Ajout des données avec features
        }
        
        # Analyse de force (1RM)
        if any(col.startswith('one_rm_') for col in features_df.columns):
            analysis['one_rm_analysis'] = self.one_rm_calculator.get_1rm_summary(features_df)
        else:
            analysis['one_rm_analysis'] = {}
        
        # Analyse de progression
        if 'progression_trend' in features_df.columns:
            analysis['progression_analysis'] = self.progression_analyzer.generate_progression_report(
                features_df, sessions_df
            )
        
        return analysis
    
    def export_features_to_csv(self, df: pd.DataFrame,
                             sessions_df: Optional[pd.DataFrame] = None,
                             output_path: str = 'features_export.csv') -> str:
        """
        Exporte les features calculées vers un fichier CSV.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des sessions
            output_path: Chemin de sortie du fichier CSV
            
        Returns:
            Chemin du fichier exporté
        """
        # Calcul des features
        df_with_features = self.calculate_all_features(df, sessions_df)
        
        # Ajout des données de session si disponibles
        if sessions_df is not None and not sessions_df.empty:
            df_export = df_with_features.merge(
                sessions_df[['id', 'date', 'training_name']], 
                left_on='session_id', right_on='id', 
                how='left'
            ).drop('id', axis=1)
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
