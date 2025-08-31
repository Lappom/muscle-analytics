"""
Composant pour l'analyse détaillée des exercices
"""
import streamlit as st
from typing import Dict

from ..services.api_client import get_api_client
from ..utils import format_weight, format_date_ago

def display_exercise_detail(exercise: str, filters: Dict):
    """Affiche les détails complets d'un exercice"""
    if not exercise:
        st.info("👈 Sélectionnez un exercice spécifique dans la barre latérale pour voir l'analyse détaillée")
        return
    
    st.header(f"🔍 Analyse détaillée: {exercise}")
    
    # Récupération des analytics complets pour l'exercice
    api_client = get_api_client()
    exercise_analytics = api_client.get_exercise_analytics(
        exercise=exercise,
        start_date=filters['start_date'],
        end_date=filters['end_date']
    )
    
    if not exercise_analytics:
        st.warning(f"Aucune donnée disponible pour {exercise}")
        return
    
    # Affichage des différentes sections d'analyse
    _display_volume_stats(exercise_analytics)
    _display_one_rm_stats(exercise_analytics)
    _display_progression_stats(exercise_analytics)
    _display_recent_sessions(exercise, filters)

def _display_volume_stats(exercise_analytics: Dict):
    """Affiche les statistiques de volume"""
    volume_stats = exercise_analytics.get('volume_stats', {})
    if not volume_stats:
        return
        
    st.subheader("📊 Statistiques de Volume")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_volume = volume_stats.get('total_volume', 0)
        st.metric("Volume total", format_weight(total_volume))
    
    with col2:
        avg_volume_per_set = volume_stats.get('avg_volume_per_set', 0)
        st.metric("Volume moyen/série", f"{avg_volume_per_set:.1f} kg")
    
    with col3:
        avg_volume_per_session = volume_stats.get('avg_volume_per_session', 0)
        st.metric("Volume moyen/session", f"{avg_volume_per_session:.1f} kg")

def _display_one_rm_stats(exercise_analytics: Dict):
    """Affiche les statistiques de 1RM"""
    one_rm_stats = exercise_analytics.get('one_rm_stats', {})
    if not one_rm_stats or not one_rm_stats.get('estimated_1rm'):
        return
        
    st.subheader("💪 1RM Estimé")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        estimated_1rm = one_rm_stats.get('estimated_1rm', 0)
        st.metric("1RM estimé", format_weight(estimated_1rm))
    
    with col2:
        max_weight = one_rm_stats.get('max_weight_lifted', 0)
        st.metric("Charge max réalisée", format_weight(max_weight))
    
    with col3:
        one_rm_trend = one_rm_stats.get('trend', 0)
        trend_display = f"{one_rm_trend:+.1f}%" if one_rm_trend != 0 else "Stable"
        st.metric("Évolution 1RM", trend_display)
    
    with col4:
        last_pr_date = one_rm_stats.get('last_pr_date')
        pr_display = format_date_ago(last_pr_date) if last_pr_date else "Aucun PR"
        st.metric("Dernier PR", pr_display)

def _display_progression_stats(exercise_analytics: Dict):
    """Affiche les statistiques de progression"""
    progression_stats = exercise_analytics.get('progression_stats', {})
    if not progression_stats:
        return
        
    st.subheader("🚀 Progression")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sessions_count = progression_stats.get('total_sessions', 0)
        st.metric("Sessions totales", sessions_count)
    
    with col2:
        trend_slope = progression_stats.get('trend_slope', 0)
        if trend_slope > 0.01:
            trend_status = "📈 Positive"
        elif trend_slope < -0.01:
            trend_status = "📉 Négative"
        else:
            trend_status = "➡️ Stable"
        st.metric("Tendance", trend_status)
    
    with col3:
        plateau_detected = progression_stats.get('plateau_detected', False)
        plateau_status = "⚠️ Oui" if plateau_detected else "✅ Non"
        st.metric("Plateau détecté", plateau_status)

def _display_recent_sessions(exercise: str, filters: Dict):
    """Affiche les sessions récentes pour l'exercice"""
    st.subheader("📅 Sessions Récentes")
    
    api_client = get_api_client()
    sessions = api_client.get_sessions(
        start_date=filters['start_date'],
        end_date=filters['end_date']
    )
    
    if not sessions:
        st.info("Aucune session trouvée pour la période sélectionnée")
        return
    
    # Filtrer les sessions contenant l'exercice (simulation)
    # Dans une vraie implémentation, il faudrait filtrer côté API
    recent_sessions = sessions[:5]  # Prendre les 5 dernières sessions
    
    if recent_sessions:
        st.write("**Dernières sessions d'entraînement:**")
        for i, session in enumerate(recent_sessions, 1):
            session_date = session.get('date', 'Date inconnue')
            session_duration = session.get('duration', 'Durée inconnue')
            
            with st.expander(f"Session {i} - {session_date[:10] if len(session_date) >= 10 else session_date}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Date**: {session_date}")
                    st.write(f"**Durée**: {session_duration}")
                with col2:
                    # Ici on pourrait afficher les détails spécifiques à l'exercice
                    st.write("**Exercices de la session**: À implémenter")
                    st.write("**Volume total session**: À implémenter")
    else:
        st.info(f"Aucune session récente trouvée contenant l'exercice {exercise}")

def display_exercise_comparison(exercises: list, filters: Dict):
    """Affiche une comparaison entre plusieurs exercices"""
    if len(exercises) < 2:
        st.info("Sélectionnez au moins 2 exercices pour la comparaison")
        return
    
    st.subheader("⚖️ Comparaison d'Exercices")
    
    # Tableau comparatif
    comparison_data = []
    api_client = get_api_client()
    
    for exercise in exercises:
        exercise_data = api_client.get_exercise_analytics(
            exercise=exercise,
            start_date=filters['start_date'],
            end_date=filters['end_date']
        )
        
        if exercise_data:
            volume_stats = exercise_data.get('volume_stats', {})
            progression_stats = exercise_data.get('progression_stats', {})
            
            comparison_data.append({
                'Exercice': exercise,
                'Volume total': format_weight(volume_stats.get('total_volume', 0)),
                'Volume moyen/série': f"{volume_stats.get('avg_volume_per_set', 0):.1f} kg",
                'Sessions': progression_stats.get('total_sessions', 0),
                'Tendance': '📈' if progression_stats.get('trend_slope', 0) > 0 else '📉' if progression_stats.get('trend_slope', 0) < 0 else '➡️'
            })
    
    if comparison_data:
        import pandas as pd
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True)
    else:
        st.warning("Aucune donnée disponible pour la comparaison")
