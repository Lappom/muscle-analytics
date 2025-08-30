"""
Services et dépendances pour l'API Muscle-Analytics
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
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
            logger.error(f"Erreur lors de la récupération des sessions: {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la récupération des sessions")
    
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
            logger.error(f"Erreur lors de la récupération des sets: {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la récupération des sets")
    
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
            logger.error(f"Erreur lors de la récupération des exercices: {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la récupération des exercices")
    
    def get_unique_exercises_from_sets(self) -> List[str]:
        """Récupère la liste unique des exercices pratiqués"""
        query = "SELECT DISTINCT exercise FROM sets ORDER BY exercise"
        
        try:
            results = self.db.execute_query(query)
            return [row[0] for row in results]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des exercices pratiqués: {e}")
            raise HTTPException(status_code=500, detail="Erreur lors de la récupération des exercices")


class AnalyticsService:
    """Service pour les calculs d'analytics"""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.feature_calculator = FeatureCalculator()
    
    def _sets_to_dataframe(self, sets: List[Set]) -> pd.DataFrame:
        """Convertit une liste de sets en DataFrame pour les calculs"""
        if not sets:
            return pd.DataFrame()
        
        data = []
        for set_obj in sets:
            data.append({
                'id': set_obj.id,
                'session_id': set_obj.session_id,
                'exercise': set_obj.exercise,
                'series_type': set_obj.series_type,
                'reps': set_obj.reps,
                'weight_kg': float(set_obj.weight_kg) if set_obj.weight_kg else None,
                'notes': set_obj.notes,
                'skipped': set_obj.skipped,
                'created_at': set_obj.created_at
            })
        
        df = pd.DataFrame(data)
        return df
    
    def _sessions_to_dataframe(self, sessions: List[Session]) -> pd.DataFrame:
        """Convertit une liste de sessions en DataFrame"""
        if not sessions:
            return pd.DataFrame()
        
        data = []
        for session in sessions:
            data.append({
                'id': session.id,
                'date': session.date,
                'start_time': session.start_time,
                'training_name': session.training_name,
                'notes': session.notes,
                'created_at': session.created_at
            })
        
        return pd.DataFrame(data)
    
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
            df, sessions_df, include_1rm=False, include_progression=False
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
                    weekly_volume=float(exercise_data['weekly_volume'].iloc[-1]) if 'weekly_volume' in exercise_data.columns else None,
                    monthly_volume=float(exercise_data['monthly_volume'].iloc[-1]) if 'monthly_volume' in exercise_data.columns else None
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
            df, sessions_df, include_progression=False
        )
        
        # Groupement par exercice
        one_rm_stats = []
        for exercise_name in df['exercise'].unique():
            exercise_data = features_df[features_df['exercise'] == exercise_name]
            
            if not exercise_data.empty:
                one_rm_stats.append(OneRMStats(
                    exercise=exercise_name,
                    best_1rm_epley=float(exercise_data['1rm_epley'].max()) if '1rm_epley' in exercise_data.columns else None,
                    best_1rm_brzycki=float(exercise_data['1rm_brzycki'].max()) if '1rm_brzycki' in exercise_data.columns else None,
                    best_1rm_lander=float(exercise_data['1rm_lander'].max()) if '1rm_lander' in exercise_data.columns else None,
                    best_1rm_oconner=float(exercise_data['1rm_oconner'].max()) if '1rm_oconner' in exercise_data.columns else None,
                    best_1rm_average=float(exercise_data['1rm_average'].max()) if '1rm_average' in exercise_data.columns else None,
                    current_1rm_epley=float(exercise_data['1rm_epley'].iloc[-1]) if '1rm_epley' in exercise_data.columns else None,
                    current_1rm_brzycki=float(exercise_data['1rm_brzycki'].iloc[-1]) if '1rm_brzycki' in exercise_data.columns else None,
                    current_1rm_lander=float(exercise_data['1rm_lander'].iloc[-1]) if '1rm_lander' in exercise_data.columns else None,
                    current_1rm_oconner=float(exercise_data['1rm_oconner'].iloc[-1]) if '1rm_oconner' in exercise_data.columns else None,
                    current_1rm_average=float(exercise_data['1rm_average'].iloc[-1]) if '1rm_average' in exercise_data.columns else None
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
                    progression_trend=exercise_data['progression_trend'].iloc[-1] if 'progression_trend' in exercise_data.columns else None,
                    volume_trend_7d=float(exercise_data['volume_trend_7d'].iloc[-1]) if 'volume_trend_7d' in exercise_data.columns else None,
                    volume_trend_30d=float(exercise_data['volume_trend_30d'].iloc[-1]) if 'volume_trend_30d' in exercise_data.columns else None,
                    plateau_detected=bool(exercise_data['plateau_detected'].iloc[-1]) if 'plateau_detected' in exercise_data.columns else False,
                    days_since_last_pr=int(exercise_data['days_since_last_pr'].iloc[-1]) if 'days_since_last_pr' in exercise_data.columns else None
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
