"""
Modèles Pydantic pour l'API Muscle-Analytics
"""

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal


class SessionBase(BaseModel):
    """Modèle de base pour une session d'entraînement"""
    date: date
    start_time: Optional[str] = None
    training_name: Optional[str] = None
    notes: Optional[str] = None


class Session(SessionBase):
    """Modèle complet d'une session d'entraînement"""
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SetBase(BaseModel):
    """Modèle de base pour un set"""
    exercise: str
    series_type: Optional[str] = None
    reps: Optional[int] = None
    weight_kg: Optional[Decimal] = None
    notes: Optional[str] = None
    skipped: bool = False


class Set(SetBase):
    """Modèle complet d'un set"""
    id: int
    session_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Exercise(BaseModel):
    """Modèle d'un exercice"""
    name: str
    main_region: Optional[str] = None
    muscles_primary: Optional[List[str]] = None
    muscles_secondary: Optional[List[str]] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Modèles pour les features calculées
class VolumeStats(BaseModel):
    """Statistiques de volume"""
    exercise: str
    total_volume: float
    avg_volume_per_set: float
    avg_volume_per_session: float
    weekly_volume: Optional[float] = None
    monthly_volume: Optional[float] = None


class OneRMStats(BaseModel):
    """Statistiques de 1RM"""
    exercise: str
    best_1rm_epley: Optional[float] = None
    best_1rm_brzycki: Optional[float] = None
    best_1rm_lander: Optional[float] = None
    best_1rm_oconner: Optional[float] = None
    best_1rm_average: Optional[float] = None
    current_1rm_epley: Optional[float] = None
    current_1rm_brzycki: Optional[float] = None
    current_1rm_lander: Optional[float] = None
    current_1rm_oconner: Optional[float] = None
    current_1rm_average: Optional[float] = None


class ProgressionStats(BaseModel):
    """Statistiques de progression"""
    exercise: str
    total_sessions: int
    progression_trend: Optional[str] = None
    volume_trend_7d: Optional[float] = None
    volume_trend_30d: Optional[float] = None
    plateau_detected: bool = False
    days_since_last_pr: Optional[int] = None


class SessionWithSets(Session):
    """Session avec ses sets"""
    sets: List[Set] = []


class ExerciseAnalytics(BaseModel):
    """Analytics complètes pour un exercice"""
    exercise: str
    volume_stats: VolumeStats
    one_rm_stats: OneRMStats
    progression_stats: ProgressionStats


class DashboardData(BaseModel):
    """Données complètes du dashboard"""
    total_sessions: int
    total_exercises: int
    total_volume_this_week: float
    total_volume_this_month: float
    recent_sessions: List[Session]
    top_exercises_by_volume: List[VolumeStats]
    exercises_with_plateau: List[str]


class DateRange(BaseModel):
    """Modèle pour les filtres de date"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ExerciseFilter(BaseModel):
    """Modèle pour les filtres d'exercice"""
    exercises: Optional[List[str]] = None
    muscle_groups: Optional[List[str]] = None


class AnalyticsRequest(BaseModel):
    """Requête pour les analytics"""
    date_range: Optional[DateRange] = None
    exercise_filter: Optional[ExerciseFilter] = None
    include_volume: bool = True
    include_1rm: bool = True
    include_progression: bool = True


# Modèles de réponse pour les erreurs
class ErrorResponse(BaseModel):
    """Modèle de réponse d'erreur"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Modèle de réponse de succès"""
    message: str
    data: Optional[Dict[str, Any]] = None
