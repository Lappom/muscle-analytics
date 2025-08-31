"""
Module de calcul du 1RM (1 Repetition Maximum) estimé.

Ce module implémente plusieurs formules pour estimer le 1RM :
- Formule d'Epley
- Formule de Brzycki  
- Formule de Lander
- Formule de O'Conner
- Moyennes pondérées
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
import logging


class OneRMCalculator:
    """Calculateur de 1RM estimé avec différentes formules."""
    
    # Constantes pour les limites des formules
    BRZYCKI_MAX_REPS = 37  # Limite mathématique où 1.0278 - 0.0278 * reps = 0
    LANDER_MAX_REPS = 38   # Limite mathématique où 101.3 - 2.67123 * reps = 0
    
    def __init__(self, enable_warnings: bool = True):
        """
        Initialise le calculateur de 1RM.
        
        Args:
            enable_warnings: Active ou désactive les avertissements pour les limites de formules
        """
        self.formulas = {
            'epley': self._epley_formula,
            'brzycki': self._brzycki_formula,
            'lander': self._lander_formula,
            'oconner': self._oconner_formula
        }
        self.enable_warnings = enable_warnings
        self.logger = logging.getLogger(__name__)
        
        # Cache pour éviter les avertissements répétés
        self._warned_formulas = set()
    
    def _log_formula_fallback(self, formula_name: str, reps: Union[int, float], 
                             reason: str = "limite de répétitions dépassée"):
        """
        Log un avertissement pour le fallback de formule de manière contrôlée.
        
        Args:
            formula_name: Nom de la formule originale
            reps: Nombre de répétitions problématique
            reason: Raison du fallback
        """
        warning_key = f"{formula_name}_{reason}"
        
        if self.enable_warnings and warning_key not in self._warned_formulas:
            self.logger.warning(
                f"Formule {formula_name}: {reason} (reps={reps}), "
                f"utilisation d'Epley comme fallback"
            )
            self._warned_formulas.add(warning_key)
        elif self.enable_warnings:
            # Log seulement en debug pour éviter le spam
            self.logger.debug(
                f"Formule {formula_name}: fallback vers Epley (reps={reps})"
            )
    
    def _epley_formula(self, weight: float, reps: Union[int, float]) -> float:
        """
        Formule d'Epley : 1RM = weight * (1 + reps/30)
        
        Args:
            weight: Poids soulevé (kg)
            reps: Nombre de répétitions
            
        Returns:
            1RM estimé
        """
        if reps <= 0:
            return weight
        return weight * (1 + reps / 30)
    
    def _brzycki_formula(self, weight: float, reps: Union[int, float]) -> float:
        """
        Formule de Brzycki : 1RM = weight / (1.0278 - 0.0278 * reps)
        
        Args:
            weight: Poids soulevé (kg)
            reps: Nombre de répétitions
            
        Returns:
            1RM estimé
        """
        if reps <= 0:
            return weight
        if reps >= self.BRZYCKI_MAX_REPS:  # Éviter division par zéro ou valeurs négatives
            self._log_formula_fallback('brzycki', reps, 'nombre de répétitions trop élevé')
            return self._epley_formula(weight, reps)
        
        denominator = 1.0278 - 0.0278 * reps
        if denominator <= 0:
            self._log_formula_fallback('brzycki', reps, 'dénominateur négatif ou nul')
            return self._epley_formula(weight, reps)
        
        return weight / denominator
    
    def _lander_formula(self, weight: float, reps: Union[int, float]) -> float:
        """
        Formule de Lander : 1RM = (100 * weight) / (101.3 - 2.67123 * reps)
        
        Args:
            weight: Poids soulevé (kg)
            reps: Nombre de répétitions
            
        Returns:
            1RM estimé
        """
        if reps <= 0:
            return weight
        if reps >= self.LANDER_MAX_REPS:  # Éviter valeurs négatives
            self._log_formula_fallback('lander', reps, 'nombre de répétitions trop élevé')
            return self._epley_formula(weight, reps)
        
        denominator = 101.3 - 2.67123 * reps
        if denominator <= 0:
            self._log_formula_fallback('lander', reps, 'dénominateur négatif ou nul')
            return self._epley_formula(weight, reps)
        
        return (100 * weight) / denominator
    
    def _oconner_formula(self, weight: float, reps: Union[int, float]) -> float:
        """
        Formule d'O'Conner : 1RM = weight * (1 + 0.025 * reps)
        
        Args:
            weight: Poids soulevé (kg)
            reps: Nombre de répétitions
            
        Returns:
            1RM estimé
        """
        if reps <= 0:
            return weight
        return weight * (1 + 0.025 * reps)
    
    def calculate_1rm(self, weight: float, reps: Union[int, float], 
                     formula: str = 'epley') -> float:
        """
        Calcule le 1RM avec la formule spécifiée.
        
        Args:
            weight: Poids soulevé (kg)
            reps: Nombre de répétitions
            formula: Formule à utiliser ('epley', 'brzycki', 'lander', 'oconner')
            
        Returns:
            1RM estimé
        """
        if pd.isna(weight) or pd.isna(reps) or weight <= 0:
            return np.nan
        
        if reps <= 0:
            return weight
        
        if formula not in self.formulas:
            raise ValueError(f"Formule inconnue: {formula}. "
                           f"Formules disponibles: {list(self.formulas.keys())}")
        
        return round(self.formulas[formula](weight, reps), 2)
    
    def calculate_all_formulas(self, weight: float, reps: Union[int, float]) -> Dict[str, float]:
        """
        Calcule le 1RM avec toutes les formules disponibles.
        
        Args:
            weight: Poids soulevé (kg)
            reps: Nombre de répétitions
            
        Returns:
            Dictionnaire avec les 1RM pour chaque formule
        """
        results = {}
        for formula_name in self.formulas.keys():
            results[f'one_rm_{formula_name}'] = self.calculate_1rm(weight, reps, formula_name)
        
        # Ajouter une moyenne pondérée (Epley et Brzycki plus fiables)
        if all(not pd.isna(v) for v in results.values()):
            epley_weight = 0.4
            brzycki_weight = 0.4
            others_weight = 0.2
            
            weighted_avg = (
                epley_weight * results['one_rm_epley'] +
                brzycki_weight * results['one_rm_brzycki'] +
                others_weight * (results['one_rm_lander'] + results['one_rm_oconner']) / 2
            )
            results['one_rm_weighted'] = round(weighted_avg, 2)
        
        return results
    
    def calculate_dataframe_1rm(self, df: pd.DataFrame, 
                              weight_col: str = 'weight_kg',
                              reps_col: str = 'reps',
                              formulas: List[str] = ['epley', 'brzycki']) -> pd.DataFrame:
        """
        Calcule le 1RM pour un DataFrame entier.
        
        Args:
            df: DataFrame avec données d'entraînement
            weight_col: Nom de la colonne poids
            reps_col: Nom de la colonne répétitions
            formulas: Liste des formules à calculer
            
        Returns:
            DataFrame avec colonnes 1RM ajoutées
        """
        df_result = df.copy()
        
        # Filtrer les sets principaux avec données valides
        mask = (
            (df_result['series_type'] == 'working_set') &
            (df_result['skipped'] != True) &
            (df_result[weight_col].notna()) &
            (df_result[reps_col].notna()) &
            (df_result[weight_col] > 0) &
            (df_result[reps_col] > 0)
        )
        
        valid_data = df_result[mask].copy()
        
        # Calculer 1RM pour chaque formule demandée
        for formula in formulas:
            col_name = f'one_rm_{formula}'
            df_result[col_name] = np.nan
            
            if len(valid_data) > 0:
                one_rm_values = valid_data.apply(
                    lambda row: self.calculate_1rm(
                        row[weight_col], 
                        row[reps_col], 
                        formula
                    ),
                    axis=1
                )
                df_result.loc[mask, col_name] = one_rm_values
        
        return df_result
    
    def get_max_1rm_by_exercise(self, df: pd.DataFrame,
                              formulas: List[str] = ['epley', 'brzycki']) -> pd.DataFrame:
        """
        Obtient le 1RM maximum par exercice.
        
        Args:
            df: DataFrame avec 1RM calculés
            formulas: Formules à analyser
            
        Returns:
            DataFrame avec 1RM max par exercice
        """
        # S'assurer que les 1RM sont calculés
        df_with_1rm = self.calculate_dataframe_1rm(df, formulas=formulas)
        
        # Colonnes 1RM à analyser
        one_rm_cols = [f'one_rm_{formula}' for formula in formulas]
        existing_cols = [col for col in one_rm_cols if col in df_with_1rm.columns]
        
        if not existing_cols:
            raise ValueError("Aucune colonne 1RM trouvée dans le DataFrame")
        
        # Grouper par exercice et prendre le maximum
        result = (df_with_1rm
                 .groupby('exercise')[existing_cols]
                 .max()
                 .reset_index())
        
        # Ajouter des informations supplémentaires
        additional_info = (df_with_1rm
                          .groupby('exercise')
                          .agg({
                              'weight_kg': ['max', 'mean'],
                              'reps': ['min', 'max', 'mean'],
                              'session_id': 'nunique'
                          }))
        
        additional_info.columns = [f"{col[0]}_{col[1]}" for col in additional_info.columns]
        additional_info = additional_info.reset_index()
        
        result = result.merge(additional_info, on='exercise', how='left')
        
        return result
    
    def calculate_1rm_progression(self, df: pd.DataFrame,
                                sessions_df: Optional[pd.DataFrame] = None,
                                formula: str = 'epley',
                                window_sessions: int = 5) -> pd.DataFrame:
        """
        Calcule la progression du 1RM au fil du temps.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des séances avec dates
            formula: Formule 1RM à utiliser
            window_sessions: Fenêtre pour moyenne mobile
            
        Returns:
            DataFrame avec progression 1RM par exercice
        """
        # Calculer 1RM
        df_with_1rm = self.calculate_dataframe_1rm(df, formulas=[formula])
        one_rm_col = f'one_rm_{formula}'
        
        # Joindre avec les dates si disponibles
        if sessions_df is not None:
            df_with_dates = df_with_1rm.merge(
                sessions_df[['id', 'date']], 
                left_on='session_id', 
                right_on='id', 
                how='left'
            )
            df_with_dates['date'] = pd.to_datetime(df_with_dates['date'])
        else:
            df_with_dates = df_with_1rm.copy()
            # Assumer que session_id peut être utilisé comme proxy temporel
            df_with_dates['date'] = df_with_dates['session_id']
        
        # Filtrer les données valides
        valid_mask = df_with_dates[one_rm_col].notna()
        df_valid = df_with_dates[valid_mask].copy()
        
        # Progression par exercice
        progression_data = []
        
        for exercise in df_valid['exercise'].unique():
            exercise_data = df_valid[df_valid['exercise'] == exercise].copy()
            exercise_data = exercise_data.sort_values('date')
            
            # 1RM maximum par séance
            session_max = (exercise_data
                          .groupby('session_id')[one_rm_col]
                          .max()
                          .reset_index())
            
            # Ajouter les dates
            if sessions_df is not None:
                session_max = session_max.merge(
                    sessions_df[['id', 'date']], 
                    left_on='session_id', 
                    right_on='id',
                    how='left'
                )
                session_max['date'] = pd.to_datetime(session_max['date'])
                session_max = session_max.sort_values('date')
            
            # Calculer moyennes mobiles et tendances
            session_max['exercise'] = exercise
            session_max[f'{one_rm_col}_ma'] = (
                session_max[one_rm_col]
                .rolling(window=window_sessions, min_periods=1)
                .mean()
                .round(2)
            )
            
            # Progression absolue et relative
            session_max[f'{one_rm_col}_progression'] = (
                session_max[one_rm_col] - session_max[one_rm_col].iloc[0]
            )
            session_max[f'{one_rm_col}_progression_pct'] = (
                (session_max[one_rm_col] / session_max[one_rm_col].iloc[0] - 1) * 100
            ).round(2)
            
            progression_data.append(session_max)
        
        result = pd.concat(progression_data, ignore_index=True)
        return result
    
    def get_1rm_summary(self, df: pd.DataFrame,
                       sessions_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Génère un résumé complet des 1RM.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des séances
            
        Returns:
            Dictionnaire avec statistiques 1RM
        """
        # Calculer 1RM avec toutes les formules
        df_with_1rm = self.calculate_dataframe_1rm(df, formulas=['epley', 'brzycki', 'lander'])
        
        # 1RM max par exercice
        max_1rm = self.get_max_1rm_by_exercise(df_with_1rm, formulas=['epley', 'brzycki'])
        
        # Progression si dates disponibles
        progression = None
        if sessions_df is not None:
            progression = self.calculate_1rm_progression(df_with_1rm, sessions_df)
        
        # Statistiques générales
        valid_mask = df_with_1rm['one_rm_epley'].notna()
        valid_data = df_with_1rm[valid_mask]
        
        summary = {
            'total_sets_with_1rm': len(valid_data),
            'exercises_with_1rm': df_with_1rm['exercise'].nunique(),
            'max_1rm_by_exercise': max_1rm,
            'overall_stats': {
                'epley': {
                    'min': valid_data['one_rm_epley'].min(),
                    'max': valid_data['one_rm_epley'].max(),
                    'mean': valid_data['one_rm_epley'].mean(),
                    'std': valid_data['one_rm_epley'].std()
                },
                'brzycki': {
                    'min': valid_data['one_rm_brzycki'].min(),
                    'max': valid_data['one_rm_brzycki'].max(),
                    'mean': valid_data['one_rm_brzycki'].mean(),
                    'std': valid_data['one_rm_brzycki'].std()
                }
            }
        }
        
        if progression is not None:
            summary['progression'] = progression
        
        return summary
