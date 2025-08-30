"""
API principale FastAPI pour Muscle-Analytics
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import date

from .models import (
    Session, Set, Exercise, VolumeStats, OneRMStats, 
    ProgressionStats, ExerciseAnalytics, DashboardData,
    SessionWithSets, AnalyticsRequest, ErrorResponse
)
from .services import DatabaseService, AnalyticsService, get_database_service, get_analytics_service

app = FastAPI(
    title="Muscle-Analytics API",
    description="API pour l'analyse d'entrainements de musculation",
    version="0.1.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Muscle-Analytics API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "sessions": "/sessions",
            "sets": "/sets", 
            "exercises": "/exercises",
            "analytics": {
                "volume": "/analytics/volume",
                "one_rm": "/analytics/one-rm",
                "progression": "/analytics/progression",
                "dashboard": "/analytics/dashboard"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    return {"status": "healthy"}


# =============================================================================
# ENDPOINTS POUR LES DONNÉES DE BASE
# =============================================================================

@app.get("/sessions", response_model=List[Session])
async def get_sessions(
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """Récupère la liste des sessions d'entraînement"""
    try:
        return db_service.get_sessions(start_date=start_date, end_date=end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}", response_model=SessionWithSets)
async def get_session_details(
    session_id: int,
    db_service: DatabaseService = Depends(get_database_service)
):
    """Récupère les détails d'une session avec ses sets"""
    try:
        sessions = db_service.get_sessions()
        session = next((s for s in sessions if s.id == session_id), None)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        sets = db_service.get_sets(session_id=session_id)
        
        return SessionWithSets(
            **session.dict(),
            sets=sets
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sets", response_model=List[Set])
async def get_sets(
    session_id: Optional[int] = Query(None, description="ID de la session"),
    exercise: Optional[str] = Query(None, description="Nom de l'exercice"),
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """Récupère la liste des sets avec filtres optionnels"""
    try:
        return db_service.get_sets(
            session_id=session_id,
            exercise=exercise,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/exercises", response_model=List[Exercise])
async def get_exercises(
    db_service: DatabaseService = Depends(get_database_service)
):
    """Récupère le catalogue des exercices"""
    try:
        return db_service.get_exercises()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/exercises/practiced", response_model=List[str])
async def get_practiced_exercises(
    db_service: DatabaseService = Depends(get_database_service)
):
    """Récupère la liste des exercices effectivement pratiqués"""
    try:
        return db_service.get_unique_exercises_from_sets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ENDPOINTS POUR LES ANALYTICS
# =============================================================================

@app.get("/analytics/volume", response_model=List[VolumeStats])
async def get_volume_analytics(
    exercise: Optional[str] = Query(None, description="Exercice spécifique"),
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Calcule les analytics de volume d'entraînement"""
    try:
        return analytics_service.get_volume_analytics(
            exercise=exercise,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/one-rm", response_model=List[OneRMStats])
async def get_one_rm_analytics(
    exercise: Optional[str] = Query(None, description="Exercice spécifique"),
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Calcule les analytics de 1RM (One Rep Max)"""
    try:
        return analytics_service.get_one_rm_analytics(
            exercise=exercise,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/progression", response_model=List[ProgressionStats])
async def get_progression_analytics(
    exercise: Optional[str] = Query(None, description="Exercice spécifique"),
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Calcule les analytics de progression"""
    try:
        return analytics_service.get_progression_analytics(
            exercise=exercise,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/exercise/{exercise_name}", response_model=ExerciseAnalytics)
async def get_exercise_analytics(
    exercise_name: str,
    start_date: Optional[date] = Query(None, description="Date de début (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Date de fin (YYYY-MM-DD)"),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Récupère tous les analytics pour un exercice spécifique"""
    try:
        # Récupération de tous les types d'analytics
        volume_stats = analytics_service.get_volume_analytics(
            exercise=exercise_name, start_date=start_date, end_date=end_date
        )
        one_rm_stats = analytics_service.get_one_rm_analytics(
            exercise=exercise_name, start_date=start_date, end_date=end_date
        )
        progression_stats = analytics_service.get_progression_analytics(
            exercise=exercise_name, start_date=start_date, end_date=end_date
        )
        
        # Vérification que l'exercice existe
        if not volume_stats and not one_rm_stats and not progression_stats:
            raise HTTPException(status_code=404, detail="Exercice non trouvé ou sans données")
        
        # Construction de la réponse
        return ExerciseAnalytics(
            exercise=exercise_name,
            volume_stats=volume_stats[0] if volume_stats else VolumeStats(
                exercise=exercise_name, total_volume=0, avg_volume_per_set=0, avg_volume_per_session=0
            ),
            one_rm_stats=one_rm_stats[0] if one_rm_stats else OneRMStats(exercise=exercise_name),
            progression_stats=progression_stats[0] if progression_stats else ProgressionStats(
                exercise=exercise_name, total_sessions=0, plateau_detected=False
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/dashboard", response_model=DashboardData)
async def get_dashboard_analytics(
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Récupère les données pour le dashboard principal"""
    try:
        return analytics_service.get_dashboard_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# ENDPOINTS DE STATUT ET DEBUG
# =============================================================================

@app.get("/status")
async def get_api_status(
    db_service: DatabaseService = Depends(get_database_service)
):
    """Récupère le statut de l'API et de la base de données"""
    try:
        # Test de connexion à la base de données
        db_connected = db_service.db.test_connection()
        
        # Statistiques rapides
        sessions = db_service.get_sessions()
        exercises = db_service.get_unique_exercises_from_sets()
        
        return {
            "api_status": "healthy",
            "database_connected": db_connected,
            "total_sessions": len(sessions),
            "total_exercises": len(exercises),
            "latest_session": sessions[0].date.isoformat() if sessions else None
        }
    except Exception as e:
        return {
            "api_status": "degraded",
            "database_connected": False,
            "error": str(e)
        }