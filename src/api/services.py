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
    
    # Instance partagée du calculateur (stateless avec valeurs par défaut)
    _feature_calculator = FeatureCalculator()
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.feature_calculator = self._feature_calculator
    
    def _safe_extract_float(self, df: pd.DataFrame, column: str, use_max: bool = False) -> Optional[float]:
        """Extrait une valeur float d'une colonne DataFrame de manière sécurisée."""
        if column not in df.columns or df.empty:
            return None
        
        try:
            if use_max:
                raw_value = df[column].max()
            else:
                raw_value = df[column].iloc[-1]
            
            if pd.isna(raw_value):
                return None
                
            return float(raw_value)
                
        except (ValueError, TypeError, IndexError):
            return None

    def _safe_extract_int(self, df: pd.DataFrame, column: str) -> Optional[int]:
        """Extrait une valeur int d'une colonne DataFrame de manière sécurisée."""
        if column not in df.columns or df.empty:
            return None
        
        try:
            raw_value = df[column].iloc[-1]
            
            if pd.isna(raw_value):
                return None
                
            return int(raw_value)
                
        except (ValueError, TypeError, IndexError):
            return None

    def _safe_extract_bool(self, df: pd.DataFrame, column: str, default: bool = False) -> bool:
        """Extrait une valeur bool d'une colonne DataFrame de manière sécurisée."""
        if column not in df.columns or df.empty:
            return default
        
        try:
            raw_value = df[column].iloc[-1]
            
            if pd.isna(raw_value):
                return default
                
            return bool(raw_value)
                
        except (ValueError, TypeError, IndexError):
            return default

    def _safe_extract_str(self, df: pd.DataFrame, column: str) -> Optional[str]:
        """Extrait une valeur string d'une colonne DataFrame de manière sécurisée."""
        if column not in df.columns or df.empty:
            return None
        
        try:
            raw_value = df[column].iloc[-1]
            
            if pd.isna(raw_value):
                return None
                
            return str(raw_value)
                
        except (ValueError, TypeError, IndexError):
            return None
    
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
        
        # Calcul des features
        features_df = self.feature_calculator.calculate_all_features(
            df, sessions_df, include_1rm=False
        )
        
        # Groupement par exercice
        progression_stats = []
        for exercise_name in df['exercise'].unique():
            exercise_data = features_df[features_df['exercise'] == exercise_name]
            exercise_sessions = len(exercise_data['session_id'].unique())
            
            if not exercise_data.empty:
                progression_stats.append(ProgressionStats(
                    exercise=exercise_name,
                    total_sessions=exercise_sessions,
                    progression_trend=self._safe_extract_str(exercise_data, 'progression_trend'),
                    volume_trend_7d=self._safe_extract_float(exercise_data, 'volume_trend_7d'),
                    volume_trend_30d=self._safe_extract_float(exercise_data, 'volume_trend_30d'),
                    plateau_detected=self._safe_extract_bool(exercise_data, 'plateau_detected', False),
                    days_since_last_pr=self._safe_extract_int(exercise_data, 'days_since_last_pr')
                ))
        
        return progression_stats
    
    def get_dashboard_data(self) -> DashboardData:
        """Récupère les données du dashboard"""
        # Données de base
        all_sessions = self.db_service.get_sessions()
        recent_sessions = all_sessions[:5]  # 5 sessions les plus récentes
        
        # Volume cette semaine et ce mois
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        volume_week = self.get_volume_analytics(start_date=week_start)
        volume_month = self.get_volume_analytics(start_date=month_start)
        
        total_volume_week = sum(v.total_volume for v in volume_week)
        total_volume_month = sum(v.total_volume for v in volume_month)
        
        # Top exercices par volume
        volume_all = self.get_volume_analytics()
        top_exercises = sorted(volume_all, key=lambda x: x.total_volume, reverse=True)[:10]
        
        # Exercices avec plateau
        progression_all = self.get_progression_analytics()
        exercises_with_plateau = [p.exercise for p in progression_all if p.plateau_detected]
        
        # Exercices uniques
        unique_exercises = self.db_service.get_unique_exercises_from_sets()
        
        return DashboardData(
            total_sessions=len(all_sessions),
            total_exercises=len(unique_exercises),
            total_volume_this_week=total_volume_week,
            total_volume_this_month=total_volume_month,
            recent_sessions=recent_sessions,
            top_exercises_by_volume=top_exercises,
            exercises_with_plateau=exercises_with_plateau
        )


# Dépendances FastAPI
def get_database_service() -> DatabaseService:
    """Dépendance pour obtenir le service de base de données"""
    db = get_database()
    return DatabaseService(db)


def get_analytics_service(db_service: DatabaseService = Depends(get_database_service)) -> AnalyticsService:
    """Dépendance pour obtenir le service d'analytics"""
    return AnalyticsService(db_service)
