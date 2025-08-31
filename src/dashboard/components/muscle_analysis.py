"""
Composant pour l'analyse musculaire
"""
import pandas as pd
import streamlit as st
from typing import Dict, List, Tuple

from ..components.charts import create_muscle_radar_chart, apply_theme_to_chart
from ..services.api_client import get_api_client

# Suggestions d'exercices par muscle (défini localement)
EXERCISE_SUGGESTIONS = {
    'Pectoraux': ['Développé couché', 'Développé incliné', 'Dips'],
    'Dos': ['Tractions', 'Rowing', 'Soulevé de terre'],
    'Jambes': ['Squat', 'Fentes', 'Presse à cuisses'],
    'Épaules': ['Développé militaire', 'Élévations latérales', 'Oiseau'],
    'Bras': ['Curl biceps', 'Extensions triceps', 'Dips'],
    'Core': ['Planche', 'Crunchs', 'Mountain climbers']
}

def display_muscle_analysis(filters: Dict):
    """Affiche l'analyse par groupe musculaire"""
    st.header("💪 Analyse Musculaire")
    
    # Information sur l'état de développement
    st.info("📋 Cette section utilise des données simulées en attendant l'implémentation de l'endpoint `/analytics/muscles` dans l'API")
    
    # Simulation des données musculaires
    muscle_balance = _simulate_muscle_balance(filters)
    
    # Vue d'ensemble de l'équilibre musculaire
    _display_muscle_balance_overview(muscle_balance, filters)
    
    # Analyse détaillée par muscle
    _display_detailed_muscle_analysis(muscle_balance)
    
    # Recommandations d'équilibrage
    _display_muscle_recommendations(muscle_balance)
    
    # Suggestions d'exercices
    _display_exercise_suggestions(muscle_balance)

def _simulate_muscle_balance(filters: Dict) -> Dict[str, float]:
    """Simule des données d'équilibre musculaire basées sur les exercices disponibles"""
    api_client = get_api_client()
    exercises = api_client.get_exercises()
    
    # Mapping exercices vers groupes musculaires (simplifié)
    exercise_to_muscle = {
        "Développé couché": "Pectoraux",
        "Développé incliné": "Pectoraux", 
        "Dips": "Pectoraux",
        "Tractions": "Dos",
        "Rowing": "Dos",
        "Soulevé de terre": "Dos",
        "Squat": "Jambes",
        "Fentes": "Jambes",
        "Presse à cuisses": "Jambes",
        "Développé militaire": "Épaules",
        "Élévations latérales": "Épaules",
        "Curl biceps": "Bras",
        "Extensions triceps": "Bras"
    }
    
    # Simuler une répartition basée sur les exercices disponibles
    muscle_balance = {}
    for exercise in exercises:
        muscle = exercise_to_muscle.get(exercise, "Autre")
        if muscle in muscle_balance:
            muscle_balance[muscle] += 15  # Volume simulé
        else:
            muscle_balance[muscle] = 20   # Volume initial
    
    # Ajouter des groupes manquants avec des valeurs simulées
    default_muscles = ["Pectoraux", "Dos", "Jambes", "Épaules", "Bras", "Core"]
    for muscle in default_muscles:
        if muscle not in muscle_balance:
            muscle_balance[muscle] = 10  # Valeur par défaut
    
    return muscle_balance

def _display_muscle_balance_overview(muscle_balance: Dict[str, float], filters: Dict):
    """Affiche la vue d'ensemble de l'équilibre musculaire"""
    st.subheader("⚖️ Équilibre Musculaire")
    
    # Création du graphique radar
    fig_radar = create_muscle_radar_chart(muscle_balance)
    fig_radar = apply_theme_to_chart(fig_radar, filters)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(fig_radar, use_container_width=True)
    
    with col2:
        _display_balance_metrics(muscle_balance)

def _display_balance_metrics(muscle_balance: Dict[str, float]):
    """Affiche les métriques d'équilibre"""
    st.subheader("📊 Métriques")
    
    muscle_values = list(muscle_balance.values())
    
    # Calcul de l'écart-type pour mesurer l'équilibre
    balance_std = pd.Series(muscle_values).std()
    balance_score = max(0, 100 - balance_std * 2)
    
    st.metric(
        "Score d'équilibre",
        f"{balance_score:.0f}/100",
        help="Score basé sur l'écart-type de la répartition"
    )
    
    # Muscle le plus/moins travaillé
    max_muscle = max(muscle_balance.keys(), key=lambda k: muscle_balance[k])
    min_muscle = min(muscle_balance.keys(), key=lambda k: muscle_balance[k])
    
    st.metric("Muscle + travaillé", max_muscle)
    st.metric("Muscle - travaillé", min_muscle)

def _display_detailed_muscle_analysis(muscle_balance: Dict[str, float]):
    """Affiche l'analyse détaillée par muscle"""
    st.subheader("🎯 Analyse Détaillée")
    
    muscle_names = list(muscle_balance.keys())
    selected_muscle_detail = st.selectbox(
        "Sélectionner un groupe musculaire pour l'analyse détaillée",
        muscle_names
    )
    
    if selected_muscle_detail:
        col1, col2, col3 = st.columns(3)
        
        muscle_volume = muscle_balance[selected_muscle_detail]
        avg_volume = sum(muscle_balance.values()) / len(muscle_balance)
        
        with col1:
            st.metric("Volume actuel", f"{muscle_volume:.0f} unités")
        
        with col2:
            percentage = (muscle_volume / sum(muscle_balance.values())) * 100
            st.metric("Pourcentage du total", f"{percentage:.1f}%")
        
        with col3:
            vs_average = ((muscle_volume - avg_volume) / avg_volume) * 100
            st.metric("vs Moyenne", f"{vs_average:+.1f}%")

def _display_muscle_recommendations(muscle_balance: Dict[str, float]):
    """Affiche les recommandations d'équilibrage"""
    st.subheader("💡 Recommandations")
    
    # Détection des déséquilibres
    imbalances = _detect_muscle_imbalances(muscle_balance)
    
    if imbalances:
        st.warning("⚠️ Déséquilibres détectés")
        for muscle, status in imbalances:
            if status == "sous-développé":
                st.write(f"• **{muscle}**: {status} - Augmentez le volume d'entraînement")
            else:
                st.write(f"• **{muscle}**: {status} - Réduisez légèrement le volume")
    else:
        st.success("✅ Équilibre musculaire optimal !")

def _detect_muscle_imbalances(muscle_balance: Dict[str, float], threshold: float = 0.3) -> List[Tuple[str, str]]:
    """Détecte les déséquilibres musculaires"""
    avg_volume = sum(muscle_balance.values()) / len(muscle_balance)
    imbalances = []
    
    for muscle, volume in muscle_balance.items():
        if volume < avg_volume * (1 - threshold):
            imbalances.append((muscle, "sous-développé"))
        elif volume > avg_volume * (1 + threshold):
            imbalances.append((muscle, "sur-développé"))
    
    return imbalances

def _display_exercise_suggestions(muscle_balance: Dict[str, float]):
    """Affiche les suggestions d'exercices"""
    st.subheader("🏋️‍♂️ Suggestions d'Exercices")
    
    # Détecter les muscles sous-développés
    imbalances = _detect_muscle_imbalances(muscle_balance)
    underdeveloped = [muscle for muscle, status in imbalances if status == "sous-développé"]
    
    if underdeveloped:
        for muscle in underdeveloped:
            if muscle in EXERCISE_SUGGESTIONS:
                exercises = ", ".join(EXERCISE_SUGGESTIONS[muscle][:3])
                st.info(f"**{muscle}**: {exercises}")
    else:
        st.info("Votre équilibre musculaire est bon ! Continuez votre programme actuel.")
    
    # Note explicative
    st.info("💡 **Note**: Cette analyse sera enrichie une fois l'endpoint `/analytics/muscles` implémenté dans l'API pour fournir des données réelles basées sur votre historique d'entraînement.")
