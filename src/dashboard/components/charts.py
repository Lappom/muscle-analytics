"""
Composants pour les graphiques et visualisations
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from typing import Dict, List, Optional

from ..services.api_client import get_api_client
from ..utils import format_weight

def apply_theme_to_chart(fig, filters: Dict):
    """Applique les paramètres de personnalisation aux graphiques"""
    theme = filters.get('theme', 'Clair')
    show_animations = filters.get('show_animations', True)
    compact_view = filters.get('compact_view', False)
    
    # Configuration du thème
    if theme == 'Sombre':
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
    elif theme == 'Auto':
        fig.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
    else:  # Clair
        fig.update_layout(
            template='plotly_white',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
    
    # Configuration des animations
    if not show_animations:
        fig.update_layout(transition_duration=0)
    
    # Vue compacte
    if compact_view:
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(size=10)
        )
    else:
        fig.update_layout(
            height=500,
            margin=dict(l=40, r=40, t=60, b=40)
        )
    
    return fig

def display_volume_charts(filters: Dict):
    """Affiche les graphiques de volume"""
    st.header("📈 Analyse du Volume")
    
    api_client = get_api_client()
    volume_data = api_client.get_volume_analytics(
        exercise=filters['exercise'],
        start_date=filters['start_date'],
        end_date=filters['end_date']
    )
    
    if not volume_data:
        st.warning("Aucune donnée de volume disponible pour la période sélectionnée")
        return
    
    # Conversion en DataFrame
    df_volume = pd.DataFrame(volume_data)
    
    if filters['exercise']:
        _display_exercise_volume_detail(df_volume, filters)
    else:
        _display_overall_volume_charts(df_volume, filters)

def _display_exercise_volume_detail(df_volume: pd.DataFrame, filters: Dict):
    """Affiche les détails de volume pour un exercice spécifique"""
    st.subheader(f"Volume pour {filters['exercise']}")
    
    # Métriques spécifiques à l'exercice
    exercise_data = df_volume[df_volume['exercise'] == filters['exercise']].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Volume total", format_weight(exercise_data['total_volume']))
    with col2:
        st.metric("Volume moyen/set", f"{exercise_data['avg_volume_per_set']:.1f} kg")
    with col3:
        st.metric("Volume moyen/session", f"{exercise_data['avg_volume_per_session']:.1f} kg")

def _display_overall_volume_charts(df_volume: pd.DataFrame, filters: Dict):
    """Affiche la vue d'ensemble des volumes"""
    st.subheader("Volume par exercice")
    
    # Graphique en barres du volume total par exercice
    fig_bar = px.bar(
        df_volume.sort_values('total_volume', ascending=True).tail(10),
        x='total_volume',
        y='exercise',
        orientation='h',
        title="Top 10 - Volume total par exercice",
        labels={'total_volume': 'Volume total (kg)', 'exercise': 'Exercice'},
        color='total_volume',
        color_continuous_scale='viridis'
    )
    fig_bar.update_layout(
        height=500,
        showlegend=False,
        xaxis_title="Volume total (kg)",
        yaxis_title="Exercice"
    )
    fig_bar.update_traces(
        hovertemplate="<b>%{y}</b><br>Volume: %{x:.0f} kg<extra></extra>"
    )
    
    # Application du thème personnalisé
    fig_bar = apply_theme_to_chart(fig_bar, filters)
    
    # Affichage des tooltips selon les préférences
    if not filters.get('show_tooltips', True):
        fig_bar.update_traces(hovertemplate=None, hoverinfo='skip')
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Graphique en secteurs du volume moyen par set
    _display_volume_pie_chart(df_volume, filters)

def _display_volume_pie_chart(df_volume: pd.DataFrame, filters: Dict):
    """Affiche le graphique en secteurs du volume"""
    fig_pie = px.pie(
        df_volume.head(8),  # Top 8 pour la lisibilité
        values='avg_volume_per_set',
        names='exercise',
        title="Répartition du volume moyen par set",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate="<b>%{label}</b><br>Volume moyen: %{value:.1f} kg<br>Pourcentage: %{percent}<extra></extra>"
    )
    
    # Application du thème personnalisé
    fig_pie = apply_theme_to_chart(fig_pie, filters)
    
    # Affichage des tooltips selon les préférences
    if not filters.get('show_tooltips', True):
        fig_pie.update_traces(hovertemplate=None, hoverinfo='skip')
    
    st.plotly_chart(fig_pie, use_container_width=True)

def display_progression_charts(filters: Dict):
    """Affiche les graphiques de progression"""
    st.header("🚀 Analyse de Progression")
    
    api_client = get_api_client()
    progression_data = api_client.get_progression_analytics(
        exercise=filters['exercise'],
        start_date=filters['start_date'],
        end_date=filters['end_date']
    )
    
    if not progression_data:
        st.warning("Aucune donnée de progression disponible pour la période sélectionnée")
        return
    
    # Conversion en DataFrame
    df_progression = pd.DataFrame(progression_data)
    
    if filters['exercise']:
        _display_exercise_progression_detail(df_progression, filters)
    else:
        _display_overall_progression_charts(df_progression, filters)

def _display_exercise_progression_detail(df_progression: pd.DataFrame, filters: Dict):
    """Affiche les détails de progression pour un exercice spécifique"""
    st.subheader(f"Progression pour {filters['exercise']}")
    
    exercise_data = df_progression[df_progression['exercise'] == filters['exercise']].iloc[0]
    
    # Métriques de progression
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sessions totales", exercise_data['total_sessions'])
    
    with col2:
        trend = exercise_data.get('trend_slope', 0)
        trend_direction = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
        st.metric("Tendance", f"{trend_direction} {trend:.3f}")
    
    with col3:
        plateau = exercise_data.get('plateau_detected', False)
        plateau_status = "⚠️ Détecté" if plateau else "✅ Non détecté"
        st.metric("Plateau", plateau_status)
    
    with col4:
        consistency = exercise_data.get('consistency_score', 0)
        st.metric("Consistance", f"{consistency:.1%}")

def _display_overall_progression_charts(df_progression: pd.DataFrame, filters: Dict):
    """Affiche la vue d'ensemble des progressions"""
    st.subheader("Progression par exercice")
    
    # Graphique des tendances
    if 'trend_slope' in df_progression.columns:
        # Ajouter une colonne pour la couleur basée sur la tendance
        df_progression['trend_color'] = df_progression['trend_slope'].apply(
            lambda x: 'Positive' if x > 0 else 'Négative' if x < 0 else 'Stable'
        )
        
        fig_scatter = px.scatter(
            df_progression,
            x='total_sessions',
            y='trend_slope',
            color='trend_color',
            size='consistency_score',
            hover_name='exercise',
            title="Tendances de progression par exercice",
            labels={
                'total_sessions': 'Nombre de sessions',
                'trend_slope': 'Pente de progression',
                'trend_color': 'Type de tendance'
            },
            color_discrete_map={
                'Positive': '#2ecc71',
                'Négative': '#e74c3c',
                'Stable': '#95a5a6'
            }
        )
        
        # Application du thème
        fig_scatter = apply_theme_to_chart(fig_scatter, filters)
        
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Tableau des exercices avec alerte plateau
    _display_plateau_alerts(df_progression)

def _display_plateau_alerts(df_progression: pd.DataFrame):
    """Affiche les alertes de plateau"""
    plateaus = df_progression[df_progression.get('plateau_detected', False) == True]
    if not plateaus.empty:
        st.warning("⚠️ Exercices en plateau détectés")
        for _, exercise in plateaus.iterrows():
            st.write(f"• {exercise['exercise']}")

def create_muscle_radar_chart(muscle_balance: Dict[str, float], ideal_balance: Optional[List[float]] = None) -> go.Figure:
    """Crée un graphique radar pour l'équilibre musculaire"""
    muscle_names = list(muscle_balance.keys())
    muscle_values = list(muscle_balance.values())
    
    fig = go.Figure()
    
    # Données actuelles
    fig.add_trace(go.Scatterpolar(
        r=muscle_values,
        theta=muscle_names,
        fill='toself',
        name='Volume actuel',
        line=dict(color='rgba(31, 119, 180, 0.8)'),
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    # Ligne de référence pour l'équilibre parfait
    if ideal_balance is None:
        ideal_balance = [sum(muscle_values)/len(muscle_values)] * len(muscle_names)
    
    fig.add_trace(go.Scatterpolar(
        r=ideal_balance,
        theta=muscle_names,
        mode='lines',
        name='Équilibre idéal',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(muscle_values) * 1.2]
            )),
        showlegend=True,
        title="Répartition du Volume par Groupe Musculaire"
    )
    
    return fig

def display_heatmap_calendar(filters: Dict):
    """Affiche un calendrier heatmap des sessions"""
    st.header("📅 Calendrier d'Entraînement")
    
    api_client = get_api_client()
    sessions = api_client.get_sessions(
        start_date=filters['start_date'],
        end_date=filters['end_date']
    )
    
    if not sessions:
        st.warning("Aucune session trouvée pour la période sélectionnée")
        return
    
    # Conversion en DataFrame et agrégation par date
    df_sessions = pd.DataFrame(sessions)
    df_sessions['date'] = pd.to_datetime(df_sessions['date'])
    df_sessions['date_only'] = df_sessions['date'].dt.date
    
    # Comptage des sessions par jour
    session_counts = df_sessions.groupby('date_only').size().reset_index(name='sessions_count')
    session_counts['date_str'] = session_counts['date_only'].astype(str)
    
    # Informations supplémentaires
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sessions totales", len(sessions))
    with col2:
        unique_days = len(session_counts)
        st.metric("Jours d'entraînement", unique_days)
    with col3:
        if unique_days > 0:
            avg_sessions = len(sessions) / unique_days
            st.metric("Sessions/jour moyen", f"{avg_sessions:.1f}")
    
    # Graphique simple de fréquence
    if len(session_counts) > 1:
        _display_frequency_chart(session_counts, filters)

def _display_frequency_chart(session_counts: pd.DataFrame, filters: Dict):
    """Affiche le graphique de fréquence d'entraînement"""
    fig_freq = px.bar(
        session_counts.sort_values('date_only'),
        x='date_str',
        y='sessions_count',
        title="Fréquence d'entraînement par jour",
        labels={'date_str': 'Date', 'sessions_count': 'Nombre de sessions'}
    )
    fig_freq.update_layout(xaxis_tickangle=-45)
    
    # Application du thème personnalisé
    fig_freq = apply_theme_to_chart(fig_freq, filters)
    
    # Affichage des tooltips selon les préférences
    if not filters.get('show_tooltips', True):
        fig_freq.update_traces(hovertemplate=None, hoverinfo='skip')
    
    st.plotly_chart(fig_freq, use_container_width=True)
