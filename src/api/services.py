"""
Services et dépendances pour l'API Muscle-Analytics.

Ce module contient les services de base de données et d'analytics
utilisés par les endpoints de l'API FastAPI.
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple, Any, Literal, NoReturn
from datetime import date, datetime, timedelta
from fastapi import Depends, HTTPException
import logging

from ..database import DatabaseManager, get_database
from ..features import FeatureCalculator
from .models import (
    Session, Set, Exercise, VolumeStats, OneRMStats, 
    ProgressionStats, ExerciseAnalytics, DashboardData
)

logger = logging.getLogger(__name__)

# Types Literal pour les opérations de base de données
DatabaseOperation = Literal[
    "récupération des sessions",
    "récupération de la session", 
    "récupération des sets",
    "récupération des exercices",
    "récupération des exercices pratiqués",
    "insertion de session",
    "insertion de set",
    "mise à jour de session",
    "mise à jour de set",
    "suppression de session",
    "suppression de set"
]


class DatabaseService:
    """Service pour les opérations de base de données"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_sessions(self, start_date: Optional[date] = None, 
                    end_date: Optional[date] = None) -> List[Session]:
        """Récupère les sessions avec filtres optionnels"""
        query = """
        SELECT id, date, start_time, training_name, notes, created_at
        FROM sessions
        WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= %s"
            params.append(end_date)
        
        query += " ORDER BY date DESC, created_at DESC"
        
        try:
            results = self.db.execute_query(query, tuple(params) if params else None)
            return [
                Session(
                    id=row[0],
                    date=row[1],
                    start_time=str(row[2]) if row[2] else None,
                    training_name=row[3],
                    notes=row[4],
                    created_at=row[5]
                )
                for row in results
            ]
        except Exception as e:
            self._handle_database_error("récupération des sessions", e)
    
    def get_session_by_id(self, session_id: int) -> Optional[Session]:
        """Récupère une session spécifique par son ID"""
        query = """
        SELECT id, date, start_time, training_name, notes, created_at
        FROM sessions
        WHERE id = %s
        """
        
        try:
            results = self.db.execute_query(query, (session_id,))
            if not results:
                return None
            
            row = results[0]
            return Session(
                id=row[0],
                date=row[1],
                start_time=str(row[2]) if row[2] else None,
                training_name=row[3],
                notes=row[4],
                created_at=row[5]
            )
        except Exception as e:
            self._handle_database_error("récupération de la session", e)
        
    def _handle_database_error(self, operation: DatabaseOperation, error: Exception) -> NoReturn:
        """
        Gère les erreurs de base de données de manière cohérente.
        
        Args:
            operation: Description typée de l'opération qui a échoué
            error: Exception capturée
            
        Raises:
            HTTPException: Exception formatée pour FastAPI
        """
        error_msg = f"Erreur lors de {operation}: {error}"
        logger.error(error_msg)
        
        # Vérifier si c'est un problème de connexion à la base de données
        error_str = str(error).lower()
        if any(keyword in error_str for keyword in [
            'connection', 'connexion', 'role', 'authentication', 'password', 
            'database', 'server', 'host', 'port', 'timeout'
        ]):
            # Erreur de connexion DB - retourner 503 Service Unavailable
            raise HTTPException(
                status_code=503, 
                detail=f"Service de base de données indisponible lors de {operation}"
            )
        else:
            # Autre erreur - retourner 500 Internal Server Error
            raise HTTPException(status_code=500, detail=f"Erreur lors de {operation}")
    
    def _is_connection_error(self, error: Exception) -> bool:
        """
        Détermine si une erreur est liée à la connexion à la base de données.
        
        Args:
            error: Exception à analyser
            
        Returns:
            True si c'est une erreur de connexion
        """
        error_str = str(error).lower()
        connection_keywords = [
            'connection', 'connexion', 'role', 'authentication', 'password', 
            'database', 'server', 'host', 'port', 'timeout', 'refused',
            'does not exist', 'failed for user'
        ]
        return any(keyword in error_str for keyword in connection_keywords)
    
    def get_sets(self, session_id: Optional[int] = None,
                 exercise: Optional[str] = None,
                 start_date: Optional[date] = None,
                 end_date: Optional[date] = None) -> List[Set]:
        """Récupère les sets avec filtres optionnels"""
        query = """
        SELECT s.id, s.session_id, s.exercise, s.series_type, s.reps, 
               s.weight_kg, s.notes, s.skipped, s.created_at
        FROM sets s
        JOIN sessions sess ON s.session_id = sess.id
        WHERE 1=1
        """
        params = []
        
        if session_id:
            query += " AND s.session_id = %s"
            params.append(session_id)
        
        if exercise:
            query += " AND s.exercise = %s"
            params.append(exercise)
        
        if start_date:
            query += " AND sess.date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND sess.date <= %s"
            params.append(end_date)
        
        query += " ORDER BY sess.date DESC, s.created_at ASC"
        
        try:
            results = self.db.execute_query(query, tuple(params) if params else None)
            return [
                Set(
                    id=row[0],
                    session_id=row[1],
                    exercise=row[2],
                    series_type=row[3],
                    reps=row[4],
                    weight_kg=row[5],
                    notes=row[6],
                    skipped=row[7],
                    created_at=row[8]
                )
                for row in results
            ]
        except Exception as e:
            self._handle_database_error("récupération des sets", e)
    
    def get_exercises(self) -> List[Exercise]:
        """Récupère tous les exercices du catalogue"""
        query = """
        SELECT name, main_region, muscles_primary, muscles_secondary, created_at
        FROM exercises
        ORDER BY name
        """
        
        try:
            results = self.db.execute_query(query)
            return [
                Exercise(
                    name=row[0],
                    main_region=row[1],
                    muscles_primary=row[2] if row[2] else [],
                    muscles_secondary=row[3] if row[3] else [],
                    created_at=row[4]
                )
                for row in results
            ]
        except Exception as e:
            self._handle_database_error("récupération des exercices", e)
    
    def get_unique_exercises_from_sets(self) -> List[str]:
        """Récupère la liste unique des exercices pratiqués"""
        query = "SELECT DISTINCT exercise FROM sets ORDER BY exercise"
        
        try:
            results = self.db.execute_query(query)
            return [row[0] for row in results]
        except Exception as e:
            self._handle_database_error("récupération des exercices pratiqués", e)


class AnalyticsService:
    """Service pour les calculs d'analytics"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.feature_calculator = FeatureCalculator()
    
    def _safe_extract_value(
        self,
        df: pd.DataFrame,
        column: str,
        type_func: Any,
        use_max: bool = False,
        default: Any = None
    ) -> Any:
        """
        Extrait une valeur d'une colonne DataFrame de manière sécurisée et la convertit selon type_func.
        
        Args:
            df: DataFrame source
            column: Nom de la colonne à extraire
            type_func: Fonction de conversion (float, int, bool, str, etc.)
            use_max: Si True, utilise la valeur maximale de la colonne (utile pour float)
            default: Valeur de retour par défaut si extraction impossible
            
        Returns:
            Valeur convertie ou valeur par défaut
        """
        if column not in df.columns or df.empty:
            return default
        
        try:
            if use_max:
                raw_value = df[column].max()
            else:
                raw_value = df[column].iloc[-1]
            
            if pd.isna(raw_value):
                return default
                
            return type_func(raw_value)
                
        except (ValueError, TypeError, IndexError):
            return default

    def _safe_extract_float(self, df: pd.DataFrame, column: str, use_max: bool = False) -> Optional[float]:
        """Extrait une valeur float d'une colonne DataFrame de manière sécurisée."""
        return self._safe_extract_value(df, column, float, use_max=use_max, default=None)

    def _safe_extract_int(self, df: pd.DataFrame, column: str) -> Optional[int]:
        """Extrait une valeur int d'une colonne DataFrame de manière sécurisée."""
        return self._safe_extract_value(df, column, int, use_max=False, default=None)

    def _safe_extract_bool(self, df: pd.DataFrame, column: str, default: bool = False) -> bool:
        """Extrait une valeur bool d'une colonne DataFrame de manière sécurisée."""
        return self._safe_extract_value(df, column, bool, use_max=False, default=default)

    def _safe_extract_str(self, df: pd.DataFrame, column: str) -> Optional[str]:
        """Extrait une valeur string d'une colonne DataFrame de manière sécurisée."""
        return self._safe_extract_value(df, column, str, use_max=False, default=None)
    
    def _convert_to_dataframe(self, data_list: List, data_type: str) -> pd.DataFrame:
        """
        Convertit une liste d'objets en DataFrame de manière générique.
        
        Args:
            data_list: Liste des objets à convertir
            data_type: Type de données ('sets' ou 'sessions')
            
        Returns:
            DataFrame correspondant
        """
        if not data_list:
            return pd.DataFrame()
        
        if data_type == 'sets':
            return pd.DataFrame([
                {
                    'id': item.id,
                    'session_id': item.session_id,
                    'exercise': item.exercise,
                    'series_type': item.series_type,
                    'reps': item.reps,
                    'weight_kg': float(item.weight_kg) if item.weight_kg else None,
                    'notes': item.notes,
                    'skipped': item.skipped,
                    'created_at': item.created_at
                }
                for item in data_list
            ])
        elif data_type == 'sessions':
            return pd.DataFrame([
                {
                    'id': item.id,
                    'date': item.date,
                    'start_time': item.start_time,
                    'training_name': item.training_name,
                    'notes': item.notes,
                    'created_at': item.created_at
                }
                for item in data_list
            ])
        else:
            raise ValueError(f"Type de données non supporté: {data_type}")
    
    def _sets_to_dataframe(self, sets: List[Set]) -> pd.DataFrame:
        """Convertit une liste de sets en DataFrame pour les calculs."""
        return self._convert_to_dataframe(sets, 'sets')
    
    def _sessions_to_dataframe(self, sessions: List[Session]) -> pd.DataFrame:
        """Convertit une liste de sessions en DataFrame."""
        return self._convert_to_dataframe(sessions, 'sessions')
    
    def get_volume_analytics(self, exercise: Optional[str] = None,
                           start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> List[VolumeStats]:
        """Calcule les analytics de volume"""
        sets = self.db_service.get_sets(
            exercise=exercise, start_date=start_date, end_date=end_date
        )
        
        if not sets:
            return []
        
        df = self._sets_to_dataframe(sets)
        sessions = self.db_service.get_sessions(start_date=start_date, end_date=end_date)
        sessions_df = self._sessions_to_dataframe(sessions)
        
        # Calcul des features
        features_df = self.feature_calculator.calculate_all_features(
            df, sessions_df, include_1rm=False
        )
        
        # Groupement par exercice
        volume_stats = []
        for exercise_name in df['exercise'].unique():
            exercise_data = features_df[features_df['exercise'] == exercise_name]
            
            if not exercise_data.empty:
                volume_stats.append(VolumeStats(
                    exercise=exercise_name,
                    total_volume=float(exercise_data['volume'].sum()),
                    avg_volume_per_set=float(exercise_data['volume'].mean()),
                    avg_volume_per_session=float(exercise_data.groupby('session_id')['volume'].sum().mean()),
                    weekly_volume=self._safe_extract_float(exercise_data, 'weekly_volume'),
                    monthly_volume=self._safe_extract_float(exercise_data, 'monthly_volume')
                ))
        
        return volume_stats
    
    def get_one_rm_analytics(self, exercise: Optional[str] = None,
                           start_date: Optional[date] = None,
                           end_date: Optional[date] = None) -> List[OneRMStats]:
        """Calcule les analytics de 1RM"""
        sets = self.db_service.get_sets(
            exercise=exercise, start_date=start_date, end_date=end_date
        )
        
        if not sets:
            return []
        
        df = self._sets_to_dataframe(sets)
        
        # Récupération des sessions et conversion en DataFrame
        sessions = self.db_service.get_sessions(
            start_date=start_date, end_date=end_date
        )
        sessions_df = self._sessions_to_dataframe(sessions)
        
        # Calcul des features
        features_df = self.feature_calculator.calculate_all_features(
            df, sessions_df
        )
        
        # Groupement par exercice
        one_rm_stats = []
        for exercise_name in df['exercise'].unique():
            exercise_data = features_df[features_df['exercise'] == exercise_name]
            
            if not exercise_data.empty:
                one_rm_stats.append(OneRMStats(
                    exercise=exercise_name,
                    best_1rm_epley=self._safe_extract_float(exercise_data, '1rm_epley', use_max=True),
                    best_1rm_brzycki=self._safe_extract_float(exercise_data, '1rm_brzycki', use_max=True),
                    best_1rm_lander=self._safe_extract_float(exercise_data, '1rm_lander', use_max=True),
                    best_1rm_oconner=self._safe_extract_float(exercise_data, '1rm_oconner', use_max=True),
                    best_1rm_average=self._safe_extract_float(exercise_data, '1rm_average', use_max=True),
                    current_1rm_epley=self._safe_extract_float(exercise_data, '1rm_epley'),
                    current_1rm_brzycki=self._safe_extract_float(exercise_data, '1rm_brzycki'),
                    current_1rm_lander=self._safe_extract_float(exercise_data, '1rm_lander'),
                    current_1rm_oconner=self._safe_extract_float(exercise_data, '1rm_oconner'),
                    current_1rm_average=self._safe_extract_float(exercise_data, '1rm_average')
                ))
        
        return one_rm_stats
    
    def get_progression_analytics(self, exercise: Optional[str] = None,
                                start_date: Optional[date] = None,
                                end_date: Optional[date] = None) -> List[ProgressionStats]:
        """Calcule les analytics de progression"""
        sets = self.db_service.get_sets(
            exercise=exercise, start_date=start_date, end_date=end_date
        )
        
        if not sets:
            return []
        
        df = self._sets_to_dataframe(sets)
        sessions = self.db_service.get_sessions(start_date=start_date, end_date=end_date)
        sessions_df = self._sessions_to_dataframe(sessions)
        
        # Calculer les tendances de volume
        volume_trends = self.feature_calculator.progression_analyzer.calculate_volume_trends(
            df, sessions_df, periods=[7, 30]
        )
        
        # Calcul des features de base
        features_df = self.feature_calculator.calculate_all_features(
            df, sessions_df, include_1rm=False
        )
        
        # Calcul des Personal Records
        pr_data = self.feature_calculator.progression_analyzer.calculate_personal_records(
            df, sessions_df, 'volume'
        )
        
        # Créer un dictionnaire pour accès rapide aux données PR
        pr_dict = {}
        if not pr_data.empty:
            pr_dict = pr_data.set_index('exercise').to_dict('index')
        
        # Détection de plateaux
        try:
            plateau_data = self.feature_calculator.progression_analyzer.detect_plateaus(df, 'volume')
            plateau_exercises = set()
            if not plateau_data.empty and 'exercise' in plateau_data.columns:
                plateau_exercises = set(plateau_data[plateau_data.get('plateau_detected', False) == True]['exercise'].unique())
        except Exception:
            plateau_exercises = set()
        
        # Groupement par exercice
        progression_stats = []
        for exercise_name in df['exercise'].unique():
            exercise_data = features_df[features_df['exercise'] == exercise_name]
            exercise_sessions = len(exercise_data['session_id'].unique())
            
            # Extraire les tendances de volume pour cet exercice
            volume_trend_7d = None
            volume_trend_30d = None
            
            if '7d' in volume_trends:
                trend_7d_data = volume_trends['7d'][volume_trends['7d']['exercise'] == exercise_name]
                if not trend_7d_data.empty:
                    volume_trend_7d = trend_7d_data['trend_pct'].iloc[0]
            
            if '30d' in volume_trends:
                trend_30d_data = volume_trends['30d'][volume_trends['30d']['exercise'] == exercise_name]
                if not trend_30d_data.empty:
                    volume_trend_30d = trend_30d_data['trend_pct'].iloc[0]
            
            # Déterminer la tendance générale
            progression_trend = self._determine_progression_trend(volume_trend_7d, volume_trend_30d, exercise_sessions)
            
            # Vérifier si l'exercice est en plateau
            plateau_detected = exercise_name in plateau_exercises
            
            # Extraire les données PR pour cet exercice
            days_since_last_pr = None
            if exercise_name in pr_dict:
                days_since_last_pr = pr_dict[exercise_name].get('days_since_last_pr')
            
            if not exercise_data.empty:
                progression_stats.append(ProgressionStats(
                    exercise=exercise_name,
                    total_sessions=exercise_sessions,
                    progression_trend=progression_trend,
                    volume_trend_7d=volume_trend_7d,
                    volume_trend_30d=volume_trend_30d,
                    plateau_detected=plateau_detected,
                    days_since_last_pr=days_since_last_pr
                ))
        
        return progression_stats
    
    def _determine_progression_trend(self, volume_trend_7d: Optional[float], 
                                   volume_trend_30d: Optional[float], 
                                   total_sessions: int) -> str:
        """Détermine la tendance générale de progression basée sur les tendances de volume"""
        # Si pas assez de sessions, retourner unknown
        if total_sessions < 3:
            return 'unknown'
        
        # Vérifier si aucune tendance n'est disponible
        if volume_trend_7d is None and volume_trend_30d is None:
            return 'unknown'
        
        # Analyse pondérée des deux tendances pour une évaluation plus complète
        short_term_weight = 0.6  # Poids plus important pour la tendance récente
        long_term_weight = 0.4   # Poids pour la tendance à long terme
        
        if volume_trend_7d is not None and volume_trend_30d is not None:
            # Calcul de la tendance pondérée combinant les deux périodes
            weighted_trend = (volume_trend_7d * short_term_weight + 
                            volume_trend_30d * long_term_weight)
        else:
            # Utiliser la seule tendance disponible
            weighted_trend = volume_trend_7d if volume_trend_7d is not None else volume_trend_30d
        
        # Seuils pour déterminer la tendance basée sur l'analyse pondérée
        if weighted_trend > 5.0:
            return 'positive'
        elif weighted_trend < -5.0:
            return 'negative'
        else:
            return 'stable'
    
    def get_dashboard_data(self) -> DashboardData:
        """Récupère les données du dashboard - Version optimisée"""
        try:
            # Données de base - optimisé avec une seule requête
            all_sessions = self.db_service.get_sessions()
            if not all_sessions:
                return DashboardData(
                    total_sessions=0,
                    total_exercises=0,
                    total_volume_this_week=0.0,
                    total_volume_this_month=0.0,
                    recent_sessions=[],
                    top_exercises_by_volume=[],
                    exercises_with_plateau=[],
                    latest_session_date=None,
                    weekly_frequency=0.0,
                    consistency_score=0.0
                )
            
            recent_sessions = all_sessions[:5]  # 5 sessions les plus récentes
            latest_session_date = all_sessions[0].date

            # Calculs de fréquence optimisés
            first_date = all_sessions[-1].date
            last_date = all_sessions[0].date
            nb_weeks = max(1, ((last_date - first_date).days / 7))
            weekly_frequency = len(all_sessions) / nb_weeks
            
            # Score de régularité optimisé avec gestion des semaines partielles
            def _get_week_number(session_date):
                """Extrait le numéro de semaine ISO d'une date de session"""
                year, week, _ = session_date.isocalendar()
                return (year, week)
            
            # Calcul des semaines actives (avec sessions)
            week_numbers = set(_get_week_number(s.date) for s in all_sessions)
            
            # Gestion des semaines partielles pour un calcul plus précis
            today = date.today()
            current_week = today.isocalendar()[1]
            last_session_week = last_date.isocalendar()[1]
            
            # Ajuster le nombre total de semaines si on est dans la semaine actuelle
            # et qu'elle contient des sessions
            if last_session_week == current_week and len(week_numbers) > 0:
                # Compter la semaine actuelle seulement si elle a des sessions
                total_weeks_for_consistency = nb_weeks
            else:
                # Exclure la semaine actuelle si elle n'a pas de sessions
                total_weeks_for_consistency = max(1, nb_weeks - 1)
            
            consistency_score = len(week_numbers) / total_weeks_for_consistency

            # Volume optimisé - une seule requête avec agrégation
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
            month_start = today.replace(day=1)

            # Récupération optimisée du volume
            volume_data = self._get_optimized_volume_data(week_start, month_start)
            
            # Exercices uniques - optimisé
            unique_exercises = self.db_service.get_unique_exercises_from_sets()

            # Exercices avec plateau - optimisé avec limite
            progression_limited = self._get_limited_progression_data()
            exercises_with_plateau = [p.exercise for p in progression_limited if p.plateau_detected]

            return DashboardData(
                total_sessions=len(all_sessions),
                total_exercises=len(unique_exercises),
                total_volume_this_week=volume_data['week'],
                total_volume_this_month=volume_data['month'],
                recent_sessions=recent_sessions,
                top_exercises_by_volume=volume_data['top_exercises'],
                exercises_with_plateau=exercises_with_plateau,
                latest_session_date=latest_session_date,
                weekly_frequency=weekly_frequency,
                consistency_score=consistency_score
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données du dashboard: {e}")
            # Retourner des données minimales en cas d'erreur
            return DashboardData(
                total_sessions=0,
                total_exercises=0,
                total_volume_this_week=0.0,
                total_volume_this_month=0.0,
                recent_sessions=[],
                top_exercises_by_volume=[],
                exercises_with_plateau=[],
                latest_session_date=None,
                weekly_frequency=0.0,
                consistency_score=0.0
            )
    
    def _get_optimized_volume_data(self, week_start: date, month_start: date) -> Dict:
        """Récupère les données de volume de manière optimisée avec une seule requête"""
        try:
            # Requête combinée pour récupérer toutes les données de volume en une seule fois
            combined_volume_query = """
            WITH volume_stats AS (
                SELECT 
                    exercise,
                    SUM(weight_kg * reps) as total_volume,
                    AVG(weight_kg * reps) as avg_volume_per_set,
                    COUNT(*) as total_sets
                FROM sets 
                WHERE weight_kg IS NOT NULL AND reps IS NOT NULL
                GROUP BY exercise
                ORDER BY total_volume DESC
                LIMIT 10
            ),
            week_volume AS (
                SELECT SUM(weight_kg * reps) as week_volume
                FROM sets s
                JOIN sessions sess ON s.session_id = sess.id
                WHERE s.weight_kg IS NOT NULL AND s.reps IS NOT NULL
                AND sess.date >= %s
            ),
            month_volume AS (
                SELECT SUM(weight_kg * reps) as month_volume
                FROM sets s
                JOIN sessions sess ON s.session_id = sess.id
                WHERE s.weight_kg IS NOT NULL AND s.reps IS NOT NULL
                AND sess.date >= %s
            )
            SELECT 
                v.exercise,
                v.total_volume,
                v.avg_volume_per_set,
                v.total_sets,
                w.week_volume,
                m.month_volume
            FROM volume_stats v
            CROSS JOIN week_volume w
            CROSS JOIN month_volume m
            """
            
            combined_results = self.db_service.db.execute_query(combined_volume_query, (week_start, month_start))
            
            # Extraction des volumes par période (première ligne contient les données)
            week_volume = 0.0
            month_volume = 0.0
            top_exercises = []
            
            if combined_results:
                # Les volumes par période sont identiques pour toutes les lignes
                week_volume = float(combined_results[0][4]) if combined_results[0][4] else 0.0
                month_volume = float(combined_results[0][5]) if combined_results[0][5] else 0.0
                
                # Construction des objets VolumeStats
                for row in combined_results:
                    top_exercises.append(VolumeStats(
                        exercise=row[0],
                        total_volume=float(row[1]) if row[1] else 0.0,
                        avg_volume_per_set=float(row[2]) if row[2] else 0.0,
                        avg_volume_per_session=0.0  # Calculé plus tard si nécessaire
                    ))
            

            
            return {
                'week': week_volume,
                'month': month_volume,
                'top_exercises': top_exercises
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données de volume: {e}")
            return {
                'week': 0.0,
                'month': 0.0,
                'top_exercises': []
            }
    
    def _get_limited_progression_data(self, limit: int = 20) -> List[ProgressionStats]:
        """Récupère les données de progression avec une limite pour éviter les timeouts"""
        try:
            # Requête optimisée pour la progression
            progression_query = """
            SELECT 
                exercise,
                COUNT(DISTINCT s.session_id) as total_sessions,
                CASE 
                    WHEN COUNT(DISTINCT s.session_id) >= 3 THEN 'stable'
                    ELSE 'unknown'
                END as progression_trend,
                false as plateau_detected,
                NULL as days_since_last_pr
            FROM sets s
            GROUP BY exercise
            ORDER BY total_sessions DESC
            LIMIT %s
            """
            
            progression_results = self.db_service.db.execute_query(progression_query, (limit,))
            
            progression_stats = []
            for row in progression_results:
                progression_stats.append(ProgressionStats(
                    exercise=row[0],
                    total_sessions=row[1],
                    progression_trend=row[2],
                    volume_trend_7d=None,
                    volume_trend_30d=None,
                    plateau_detected=row[3],
                    days_since_last_pr=row[4]
                ))
            
            return progression_stats
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données de progression: {e}")
            return []


# Dépendances FastAPI
def get_database_service() -> DatabaseService:
    """Dépendance pour obtenir le service de base de données"""
    db = get_database()
    return DatabaseService(db)


def get_analytics_service(db_service: DatabaseService = Depends(get_database_service)) -> AnalyticsService:
    """Dépendance pour obtenir le service d'analytics"""
    return AnalyticsService(db_service)
