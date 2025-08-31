"""
Module d'analyse de progression pour l'entraînement de musculation.

Ce module fournit des outils pour analyser la progression :
- Tendances de volume et intensité
- Détection de plateaux
- Indicateurs de performance
- Comparaisons temporelles
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from scipy import stats


class ProgressionAnalyzer:
    """Analyseur de progression d'entraînement."""
    
    def __init__(self):
        """Initialise l'analyseur de progression."""
        self.trend_threshold = 0.05  # Seuil de tendance significative (5%)
        self.plateau_threshold = 0.02  # Seuil de plateau (2%)
        self.min_sessions_for_trend = 5  # Nombre minimum de séances pour détecter une tendance
    
    def calculate_volume_progression(self, df: pd.DataFrame,
                                   sessions_df: Optional[pd.DataFrame] = None,
                                   window_size: int = 4) -> pd.DataFrame:
        """
        Calcule la progression du volume par exercice.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des séances avec dates
            window_size: Taille de la fenêtre pour moyennes mobiles
            
        Returns:
            DataFrame avec progression du volume
        """
        # Calculer volume si pas présent
        if 'volume' not in df.columns:
            df = df.copy()
            df['volume'] = df['reps'].fillna(0) * df['weight_kg'].fillna(0)
        
        # Joindre avec les dates
        if sessions_df is not None:
            df_with_dates = df.merge(
                sessions_df[['id', 'date']], 
                left_on='session_id', 
                right_on='id', 
                how='left'
            )
            df_with_dates['date'] = pd.to_datetime(df_with_dates['date'])
        else:
            df_with_dates = df.copy()
            df_with_dates['date'] = df_with_dates['session_id']  # Proxy temporel
        
        # Filtrer les sets principaux
        mask = (df_with_dates['series_type'] == 'principale') & (df_with_dates['skipped'] != True)
        working_sets = df_with_dates[mask].copy()
        
        # Progression par exercice
        progression_data = []
        
        for exercise in working_sets['exercise'].unique():
            exercise_data = working_sets[working_sets['exercise'] == exercise].copy()
            
            # Volume par séance
            session_volumes = (exercise_data
                             .groupby(['session_id', 'date'])
                             .agg({
                                 'volume': 'sum',
                                 'reps': 'sum',
                                 'weight_kg': 'max'
                             })
                             .reset_index())
            
            session_volumes = session_volumes.sort_values('date')
            
            if len(session_volumes) < 2:
                continue
            
            # Moyennes mobiles
            session_volumes['volume_ma'] = (
                session_volumes['volume']
                .rolling(window=window_size, min_periods=1)
                .mean()
                .round(2)
            )
            
            # Progression absolue et relative
            first_volume = session_volumes['volume'].iloc[0]
            session_volumes['volume_progression'] = session_volumes['volume'] - first_volume
            session_volumes['volume_progression_pct'] = (
                (session_volumes['volume'] / first_volume - 1) * 100
            ).round(2)
            
            # Tendance linéaire
            if len(session_volumes) >= self.min_sessions_for_trend:
                x = np.arange(len(session_volumes))
                try:
                    # Utiliser stats.linregress avec accès direct aux attributs
                    linregress_result = stats.linregress(x, session_volumes['volume'])
                    
                    # Accès direct aux attributs du résultat linregress
                    session_volumes['trend_slope'] = linregress_result.slope  # type: ignore
                    rvalue = linregress_result.rvalue  # type: ignore
                    session_volumes['trend_r_squared'] = rvalue * rvalue
                    session_volumes['trend_p_value'] = linregress_result.pvalue  # type: ignore
                except (ValueError, TypeError):
                    # En cas d'erreur, valeurs par défaut
                    session_volumes['trend_slope'] = 0.0
                    session_volumes['trend_r_squared'] = 0.0
                    session_volumes['trend_p_value'] = 1.0
            
            session_volumes['exercise'] = exercise
            progression_data.append(session_volumes)
        
        if progression_data:
            result = pd.concat(progression_data, ignore_index=True)
            return result
        else:
            return pd.DataFrame()
    
    def calculate_intensity_progression(self, df: pd.DataFrame,
                                      sessions_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Calcule la progression de l'intensité (poids moyen).
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des séances
            
        Returns:
            DataFrame avec progression de l'intensité
        """
        # Calculer volume si pas présent
        if 'volume' not in df.columns:
            df = df.copy()
            df['volume'] = df['reps'].fillna(0) * df['weight_kg'].fillna(0)
        
        # Joindre avec les dates
        if sessions_df is not None:
            df_with_dates = df.merge(
                sessions_df[['id', 'date']], 
                left_on='session_id', 
                right_on='id', 
                how='left'
            )
            df_with_dates['date'] = pd.to_datetime(df_with_dates['date'])
        else:
            df_with_dates = df.copy()
            df_with_dates['date'] = df_with_dates['session_id']
        
        # Filtrer les sets principaux
        mask = (df_with_dates['series_type'] == 'principale') & (df_with_dates['skipped'] != True)
        working_sets = df_with_dates[mask].copy()
        
        # Intensité par exercice et séance
        intensity_data = []
        
        for exercise in working_sets['exercise'].unique():
            exercise_data = working_sets[working_sets['exercise'] == exercise].copy()
            
            session_intensity = (exercise_data
                               .groupby(['session_id', 'date'])
                               .agg({
                                   'weight_kg': ['mean', 'max'],
                                   'reps': 'mean',
                                   'volume': 'sum'
                               })
                               .reset_index())
            
            # Aplatir colonnes
            session_intensity.columns = [
                col[0] if col[1] == '' else f"{col[0]}_{col[1]}"
                for col in session_intensity.columns
            ]
            
            session_intensity = session_intensity.sort_values('date')
            
            if len(session_intensity) < 2:
                continue
            
            # Progression de l'intensité
            first_weight = session_intensity['weight_kg_mean'].iloc[0]
            session_intensity['intensity_progression'] = (
                session_intensity['weight_kg_mean'] - first_weight
            )
            session_intensity['intensity_progression_pct'] = (
                (session_intensity['weight_kg_mean'] / first_weight - 1) * 100
            ).round(2)
            
            session_intensity['exercise'] = exercise
            intensity_data.append(session_intensity)
        
        if intensity_data:
            result = pd.concat(intensity_data, ignore_index=True)
            return result
        else:
            return pd.DataFrame()
    
    def detect_plateaus(self, progression_df: pd.DataFrame,
                       metric_col: str = 'volume',
                       window_size: int = 6) -> pd.DataFrame:
        """
        Détecte les plateaux dans la progression.
        
        Args:
            progression_df: DataFrame avec données de progression
            metric_col: Colonne métrique à analyser
            window_size: Taille de fenêtre pour détection plateau
            
        Returns:
            DataFrame avec indicateurs de plateau
        """
        if progression_df.empty:
            return pd.DataFrame()
        
        result_data = []
        
        for exercise in progression_df['exercise'].unique():
            exercise_data = progression_df[
                progression_df['exercise'] == exercise
            ].copy()
            
            if 'date' in exercise_data.columns:
                exercise_data = exercise_data.sort_values('date')
            else:
                exercise_data = exercise_data.reset_index(drop=True)
            
            if len(exercise_data) < window_size:
                # Pas assez de données pour détecter un plateau
                exercise_data['plateau_indicator'] = False
                result_data.append(exercise_data)
                continue
            
            # Initialiser la colonne plateau_indicator
            exercise_data['plateau_indicator'] = False
            
            # Calculer variation sur fenêtre glissante
            for i in range(window_size, len(exercise_data)):
                window_data = exercise_data.iloc[i-window_size:i][metric_col]
                
                if window_data.empty or window_data.isna().all():
                    continue
                
                # Coefficient de variation (std/mean)
                mean_val = window_data.mean()
                std_val = window_data.std()
                
                if mean_val == 0 or pd.isna(mean_val) or pd.isna(std_val):
                    cv = 0
                else:
                    cv = std_val / abs(mean_val)
                
                # Tendance de la fenêtre (régression linéaire)
                x = np.arange(len(window_data))
                try:
                    if len(window_data) > 1 and not window_data.isna().all():
                        # Filtrer les valeurs NaN
                        valid_mask = ~window_data.isna()
                        if valid_mask.sum() > 1:  # Au moins 2 points valides
                            valid_x = x[valid_mask]
                            valid_y = window_data[valid_mask]

                            linregress_result = stats.linregress(valid_x, valid_y)
                            # Accès direct aux attributs du résultat linregress
                            slope = linregress_result.slope  # type: ignore
                            rvalue = linregress_result.rvalue  # type: ignore
                            r_squared = rvalue * rvalue
                            
                            # Plateau si faible variation ET tendance plate
                            threshold_cv = self.plateau_threshold  # 0.02 par défaut
                            threshold_slope = abs(mean_val) * 0.01 if mean_val != 0 else 0.01
                            
                            is_plateau = (cv < threshold_cv and abs(slope) < threshold_slope)  # type: ignore
                            
                            # Mettre à jour l'indicateur
                            exercise_data.iloc[i, exercise_data.columns.get_loc('plateau_indicator')] = is_plateau
                        
                except (ValueError, np.linalg.LinAlgError):
                    # En cas d'erreur dans la régression, considérer comme pas de plateau
                    exercise_data.iloc[i, exercise_data.columns.get_loc('plateau_indicator')] = False
            
            result_data.append(exercise_data)
        
        if result_data:
            return pd.concat(result_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def calculate_performance_metrics(self, df: pd.DataFrame,
                                    sessions_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Calcule des métriques de performance globales.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des séances
            
        Returns:
            Dictionnaire avec métriques de performance
        """
        # Progression volume
        volume_prog = self.calculate_volume_progression(df, sessions_df)
        
        # Progression intensité
        intensity_prog = self.calculate_intensity_progression(df, sessions_df)
        
        # Détection plateaux
        plateaus = self.detect_plateaus(volume_prog) if not volume_prog.empty else pd.DataFrame()
        
        # Métriques par exercice
        exercise_metrics = {}
        
        if not volume_prog.empty:
            for exercise in volume_prog['exercise'].unique():
                exercise_vol = volume_prog[volume_prog['exercise'] == exercise]
                exercise_int = intensity_prog[intensity_prog['exercise'] == exercise] if not intensity_prog.empty else pd.DataFrame()
                exercise_plat = plateaus[plateaus['exercise'] == exercise] if not plateaus.empty else pd.DataFrame()
                
                metrics = {
                    'sessions_count': len(exercise_vol),
                    'volume_progression_total_pct': exercise_vol['volume_progression_pct'].iloc[-1] if len(exercise_vol) > 0 else 0,
                    'volume_trend_slope': exercise_vol['trend_slope'].iloc[-1] if 'trend_slope' in exercise_vol.columns and len(exercise_vol) > 0 else 0,
                    'volume_trend_r_squared': exercise_vol['trend_r_squared'].iloc[-1] if 'trend_r_squared' in exercise_vol.columns and len(exercise_vol) > 0 else 0,
                    'current_plateau': exercise_plat['plateau_indicator'].iloc[-1] if len(exercise_plat) > 0 and 'plateau_indicator' in exercise_plat.columns else False,
                    'plateau_sessions': exercise_plat['plateau_indicator'].sum() if len(exercise_plat) > 0 and 'plateau_indicator' in exercise_plat.columns else 0
                }
                
                if not exercise_int.empty:
                    metrics['intensity_progression_total_pct'] = exercise_int['intensity_progression_pct'].iloc[-1] if len(exercise_int) > 0 else 0
                
                exercise_metrics[exercise] = metrics
        
        # Métriques globales
        global_metrics = {
            'total_exercises': len(exercise_metrics),
            'exercises_in_progression': sum(1 for m in exercise_metrics.values() 
                                          if m['volume_progression_total_pct'] > 5),
            'exercises_in_plateau': sum(1 for m in exercise_metrics.values() 
                                      if m['current_plateau']),
            'avg_volume_progression': np.mean([m['volume_progression_total_pct'] 
                                             for m in exercise_metrics.values()]) if exercise_metrics else 0
        }
        
        return {
            'global_metrics': global_metrics,
            'exercise_metrics': exercise_metrics,
            'volume_progression': volume_prog,
            'intensity_progression': intensity_prog,
            'plateaus': plateaus
        }
    
    def generate_progression_report(self, df: pd.DataFrame,
                                  sessions_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Génère un rapport complet de progression.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des séances
            
        Returns:
            Dictionnaire avec rapport de progression
        """
        # Calculer toutes les métriques
        performance_metrics = self.calculate_performance_metrics(df, sessions_df)
        
        # Analyses supplémentaires
        report = {
            'summary': {
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_exercises': performance_metrics['global_metrics']['total_exercises'],
                'exercises_progressing': performance_metrics['global_metrics']['exercises_in_progression'],
                'exercises_plateauing': performance_metrics['global_metrics']['exercises_in_plateau'],
                'avg_progression_rate': performance_metrics['global_metrics']['avg_volume_progression']
            },
            'detailed_metrics': performance_metrics,
            'recommendations': self._generate_recommendations(performance_metrics)
        }
        
        return report
    
    def _generate_recommendations(self, metrics: Dict) -> List[str]:
        """
        Génère des recommandations basées sur les métriques.
        
        Args:
            metrics: Métriques de performance
            
        Returns:
            Liste de recommandations
        """
        recommendations = []
        
        exercise_metrics = metrics['exercise_metrics']
        
        for exercise, exercise_metric in exercise_metrics.items():
            # Plateau détecté
            if exercise_metric['current_plateau']:
                recommendations.append(
                    f"🔄 {exercise}: Plateau détecté. Considérer une variation "
                    f"(augmentation poids, changement tempo, exercice similaire)."
                )
            
            # Forte progression
            elif exercise_metric['volume_progression_total_pct'] > 20:
                recommendations.append(
                    f"📈 {exercise}: Excellente progression (+{exercise_metric['volume_progression_total_pct']:.1f}%). "
                    f"Continuer sur cette lancée."
                )
            
            # Progression faible
            elif 0 < exercise_metric['volume_progression_total_pct'] < 5:
                recommendations.append(
                    f"⚠️ {exercise}: Progression lente (+{exercise_metric['volume_progression_total_pct']:.1f}%). "
                    f"Vérifier la charge et la technique."
                )
            
            # Régression
            elif exercise_metric['volume_progression_total_pct'] < 0:
                recommendations.append(
                    f"⬇️ {exercise}: Régression détectée ({exercise_metric['volume_progression_total_pct']:.1f}%). "
                    f"Vérifier récupération et planification."
                )
        
        # Recommandations globales
        global_metrics = metrics['global_metrics']
        
        if global_metrics['exercises_in_plateau'] > global_metrics['total_exercises'] * 0.5:
            recommendations.append(
                "🔄 Plus de 50% des exercices sont en plateau. "
                "Considérer une décharge ou une variation du programme."
            )
        
        if global_metrics['avg_volume_progression'] < 0:
            recommendations.append(
                "⚠️ Progression moyenne négative. Vérifier la récupération, "
                "la nutrition et l'intensité d'entraînement."
            )
        
        return recommendations
    
    def calculate_volume_trends(self, df: pd.DataFrame,
                              sessions_df: Optional[pd.DataFrame] = None,
                              periods: List[int] = [7, 30]) -> Dict[str, pd.DataFrame]:
        """
        Calcule les tendances de volume sur différentes périodes.
        
        Args:
            df: DataFrame avec données d'entraînement
            sessions_df: DataFrame des séances
            periods: Liste des périodes en jours pour calculer les tendances
            
        Returns:
            Dictionnaire avec les tendances par période et par exercice
        """
        from datetime import datetime, timedelta
        
        # Calculer volume si pas présent
        if 'volume' not in df.columns:
            df = df.copy()
            df['volume'] = df['reps'].fillna(0) * df['weight_kg'].fillna(0)
        
        # Joindre avec les dates
        if sessions_df is not None:
            df_with_dates = df.merge(
                sessions_df[['id', 'date']], 
                left_on='session_id', 
                right_on='id', 
                how='left'
            )
            df_with_dates['date'] = pd.to_datetime(df_with_dates['date'])
        else:
            return {}
        
        # Filtrer les sets principaux (utiliser 'working_set' et non 'principale')
        mask = (df_with_dates['series_type'] == 'working_set') & (df_with_dates['skipped'] != True)
        working_sets = df_with_dates[mask].copy()
        
        if working_sets.empty:
            return {}
        
        # Date la plus récente dans les données
        max_date = working_sets['date'].max()
        
        trends_by_period = {}
        
        for period_days in periods:
            # Pour les courtes périodes, utiliser des sessions récentes plutôt qu'une date fixe
            if period_days <= 30:
                # Prendre les N dernières sessions au lieu d'une période de temps fixe
                recent_sessions = (working_sets
                                 .groupby(['exercise', 'session_id', 'date'])['volume']
                                 .sum()
                                 .reset_index()
                                 .sort_values('date')
                                 .groupby('exercise')
                                 .tail(max(2, period_days // 3))  # Au moins 2 points, environ 1 session tous les 3 jours
                                 .reset_index(drop=True))
                session_volume = recent_sessions
            else:
                # Pour les longues périodes, utiliser la méthode basée sur les dates
                start_date = max_date - timedelta(days=period_days)
                period_data = working_sets[working_sets['date'] >= start_date].copy()
                
                if period_data.empty:
                    continue
                
                session_volume = (period_data
                                .groupby(['exercise', 'session_id', 'date'])['volume']
                                .sum()
                                .reset_index())
            
            trends_data = []
            
            for exercise in session_volume['exercise'].unique():
                exercise_data = session_volume[session_volume['exercise'] == exercise].copy()
                exercise_data = exercise_data.sort_values('date')
                
                if len(exercise_data) < 2:  # Minimum 2 points pour calculer une tendance
                    continue
                
                # Calculer la tendance linéaire
                x = np.arange(len(exercise_data))
                y = exercise_data['volume'].values
                
                try:
                    # Régression linéaire
                    linregress_result = stats.linregress(x, y)
                    slope = linregress_result.slope
                    
                    # Calculer le pourcentage de changement
                    mean_volume = y.mean()
                    if mean_volume > 0:
                        # Tendance en pourcentage par jour * nombre de jours
                        trend_pct = (slope / mean_volume) * 100 * len(x)
                    else:
                        trend_pct = 0.0
                    
                    # Limiter la tendance pour éviter des valeurs aberrantes
                    trend_pct = max(-100, min(100, trend_pct))
                    
                    trends_data.append({
                        'exercise': exercise,
                        'period_days': period_days,
                        'trend_slope': slope,
                        'trend_pct': round(trend_pct, 2),
                        'data_points': len(exercise_data),
                        'mean_volume': round(mean_volume, 2)
                    })
                    
                except Exception as e:
                    # En cas d'erreur, tendance nulle
                    trends_data.append({
                        'exercise': exercise,
                        'period_days': period_days,
                        'trend_slope': 0.0,
                        'trend_pct': 0.0,
                        'data_points': len(exercise_data),
                        'mean_volume': round(y.mean() if len(y) > 0 else 0, 2)
                    })
            
            if trends_data:
                trends_by_period[f'{period_days}d'] = pd.DataFrame(trends_data)
        
        return trends_by_period