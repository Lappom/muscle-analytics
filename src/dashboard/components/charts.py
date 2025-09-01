"""
Composants pour les graphiques et visualisations
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
from typing import Dict, List, Optional

from ..services.api_client import get_api_client
from ..utils import format_weight, create_progress_trend_chart

def _display_trend_metric(label: str, value: float, filters: Dict):
    """Affiche une métrique de tendance avec formatage automatique"""
    color = "normal" if value == 0 else "delta" if value > 0 else "inverse"
    st.metric(
        label,
        f"{value:.1f}%" if pd.notna(value) else "N/A",
        delta=f"{abs(value):.1f}%" if pd.notna(value) and value != 0 else None,
        delta_color=color
    )

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
        exercise=None,  # Pas d'exercice spécifique - vue générale
        start_date=filters['start_date'],
        end_date=filters['end_date']
    )
    
    if not volume_data:
        st.warning("Aucune donnée de volume disponible pour la période sélectionnée")
        return
    
    # Conversion en DataFrame
    df_volume = pd.DataFrame(volume_data)
    
    # Toujours afficher la vue générale maintenant
    _display_overall_volume_charts(df_volume, filters)

def _display_exercise_volume_detail(df_volume: pd.DataFrame, filters: Dict):
    """Affiche les détails de volume pour un exercice spécifique - FONCTION NON UTILISÉE"""
    # NOTE: Cette fonction n'est plus utilisée depuis la suppression de la sélection d'exercice
    # Elle reste pour référence mais ne sera pas appelée
    pass
    # st.subheader(f"Volume pour {filters['exercise']}")
    # 
    # # Métriques spécifiques à l'exercice
    # exercise_data = df_volume[df_volume['exercise'] == filters['exercise']].iloc[0]
    # 
    # col1, col2, col3 = st.columns(3)
    # with col1:
    #     st.metric("Volume total", format_weight(exercise_data['total_volume']))
    # with col2:
    #     st.metric("Volume moyen/set", f"{exercise_data['avg_volume_per_set']:.1f} kg")
    # with col3:
    #     st.metric("Volume moyen/session", f"{exercise_data['avg_volume_per_session']:.1f} kg")

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
        exercise=None,  # Pas d'exercice spécifique - vue générale
        start_date=filters['start_date'],
        end_date=filters['end_date']
    )
    
    if not progression_data:
        st.warning("Aucune donnée de progression disponible pour la période sélectionnée")
        return
    
    # Conversion en DataFrame
    df_progression = pd.DataFrame(progression_data)
    
    # Toujours afficher la vue générale maintenant
    _display_overall_progression_charts(df_progression, filters)

def _display_exercise_progression_detail(df_progression: pd.DataFrame, filters: Dict):
    """Affiche les détails de progression pour un exercice spécifique - FONCTION NON UTILISÉE"""
    # NOTE: Cette fonction n'est plus utilisée depuis la suppression de la sélection d'exercice
    # Elle reste pour référence mais ne sera pas appelée
    pass
    # st.subheader(f"Progression pour {filters['exercise']}")
    # 
    # exercise_data = df_progression[df_progression['exercise'] == filters['exercise']].iloc[0]
    # 
    # # Métriques de progression
    # col1, col2, col3, col4 = st.columns(4)
    # 
    # with col1:
    #     st.metric("Sessions totales", exercise_data['total_sessions'])
    # 
    # with col2:
    #     trend = exercise_data.get('progression_trend', 'Inconnue')
    #     trend_icons = {'positive': '📈', 'negative': '📉', 'stable': '➡️'}
    #     trend_icon = trend_icons.get(trend.lower(), '❓')
    #     st.metric("Tendance", f"{trend_icon} {trend.title()}")
    # 
    # with col3:
    #     plateau = exercise_data.get('plateau_detected', False)
    #     plateau_status = "⚠️ Détecté" if plateau else "✅ Non détecté"
    #     st.metric("Plateau", plateau_status)
    # 
    # with col4:
    #     days_since_pr = exercise_data.get('days_since_last_pr')
    #     if days_since_pr is not None:
    #         st.metric("Jours depuis dernier PR", f"{days_since_pr} jours")
    #     else:
    #         st.metric("Dernier PR", "Aucun")
    # 
    # # Graphiques spécifiques à l'exercice
    # _display_exercise_trend_analysis(exercise_data, filters)
    # _display_exercise_volume_trends(exercise_data, filters)

def _display_overall_progression_charts(df_progression: pd.DataFrame, filters: Dict):
    """Affiche la vue d'ensemble des progressions"""
    st.subheader("Vue d'ensemble de la progression")
    
    # Vue d'ensemble avec métriques globales
    _display_progression_overview_metrics(df_progression)
    
    # Graphiques de tendances
    col1, col2 = st.columns(2)
    
    with col1:
        _display_progression_trend_chart(df_progression, filters)
    
    with col2:
        _display_volume_trends_chart(df_progression, filters)
    
    # Nouveau graphique scatter des tendances de progression
    st.subheader("📊 Analyse des tendances de progression par exercice")
    _display_progress_trend_scatter_chart(df_progression, filters)
    
    # Graphiques complémentaires
    _display_sessions_distribution_chart(df_progression, filters)
    _display_plateau_analysis_chart(df_progression, filters)
    
    # Tableau des exercices avec alerte plateau
    _display_plateau_alerts(df_progression)

def _display_plateau_alerts(df_progression: pd.DataFrame):
    """Affiche les alertes de plateau avec recommandations détaillées"""
    plateaus = df_progression[df_progression.get('plateau_detected', False) == True]
    
    if not plateaus.empty:
        # Alerte principale avec icône et style
        st.error("🚨 **ALERTE PLATEAU DÉTECTÉE**")
        st.markdown("""
        **Plusieurs exercices semblent être en plateau de progression.**
        Voici une analyse détaillée et des recommandations pour relancer votre progression.
        """)
        
        # Métriques des plateaux
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Exercices en plateau", len(plateaus), delta=f"+{len(plateaus)}", delta_color="inverse")
        
        with col2:
            avg_sessions = plateaus['total_sessions'].mean()
            st.metric("Sessions moyennes", f"{avg_sessions:.1f}")
        
        with col3:
            plateau_percentage = (len(plateaus) / len(df_progression)) * 100
            st.metric("% d'exercices en plateau", f"{plateau_percentage:.1f}%", delta_color="inverse")
        
        # Tableau détaillé des plateaux
        st.subheader("📋 Détail des exercices en plateau")
        plateau_data = []
        for _, exercise in plateaus.iterrows():
            days_since_pr = exercise.get('days_since_last_pr', 'N/A')
            trend = exercise.get('progression_trend', 'Inconnue')
            
            plateau_data.append({
                'Exercice': exercise['exercise'],
                'Sessions': exercise['total_sessions'],
                'Tendance': trend,
                'Jours depuis PR': f"{days_since_pr} jours" if days_since_pr != 'N/A' else 'Aucun PR',
                'Niveau d\'alerte': '🔴 Critique' if days_since_pr and days_since_pr > 30 else '🟡 Modéré'
            })
        
        if plateau_data:
            df_plateau = pd.DataFrame(plateau_data)
            st.dataframe(df_plateau, use_container_width=True)
        
        # Recommandations personnalisées
        st.subheader("💡 Recommandations pour relancer la progression")
        
        # Recommandations basées sur le nombre de plateaux
        if len(plateaus) >= 3:
            st.warning("""
            **🔄 Programme complet à revoir** - Plus de 50% de vos exercices sont en plateau.
            
            **Actions recommandées :**
            - Changez complètement votre programme d'entraînement
            - Intégrez de nouveaux exercices et variations
            - Considérez une période de deload ou de récupération
            - Consultez un coach pour un programme personnalisé
            """)
        elif len(plateaus) == 2:
            st.info("""
            **⚖️ Ajustement modéré nécessaire** - 2 exercices en plateau détectés.
            
            **Actions recommandées :**
            - Variez les rep ranges et intensités
            - Ajoutez des techniques d'intensification (drop-sets, super-sets)
            - Modifiez l'ordre des exercices
            - Intégrez des exercices de substitution
            """)
        else:
            st.info("""
            **🎯 Ajustement ciblé** - 1 exercice en plateau détecté.
            
            **Actions recommandées :**
            - Variez les paramètres de l'exercice (reps, poids, tempo)
            - Ajoutez des variations (grip différent, position modifiée)
            - Considérez une progression plus lente mais constante
            """)
        
        # Recommandations spécifiques par exercice
        st.subheader("📝 Actions spécifiques par exercice")
        for _, exercise in plateaus.iterrows():
            exercise_name = exercise['exercise']
            days_since_pr = exercise.get('days_since_last_pr', 0)
            
            if days_since_pr and days_since_pr > 30:
                st.error(f"**{exercise_name}** - Plateau critique depuis {days_since_pr} jours")
                st.markdown(f"""
                - 🔄 **Changement d'exercice recommandé** pour {exercise_name}
                - 📊 Analysez votre technique et form
                - 🎯 Considérez un exercice de substitution
                - 💪 Travaillez les muscles antagonistes
                """)
            else:
                st.warning(f"**{exercise_name}** - Plateau modéré détecté")
                st.markdown(f"""
                - ⚡ Variez l'intensité et le volume
                - 🔄 Changez l'ordre dans votre routine
                - 📈 Progression plus lente mais constante
                """)
        
    else:
        st.success("✅ **Aucun plateau détecté - excellente progression !** 🎯")
        st.markdown("""
        **Votre progression semble optimale !** 
        
        **🎉 Continuez sur cette lancée :**
        - Maintenez votre programme actuel
        - Surveillez régulièrement vos performances
        - Conservez la cohérence dans votre entraînement
        - Célébrez vos progrès !
        
        **💡 Conseils pour maintenir la progression :**
        - Variez légèrement les paramètres d'entraînement
        - Maintenez une intensité progressive
        - Écoutez votre corps et ajustez si nécessaire
        """)

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

def _display_progression_overview_metrics(df_progression: pd.DataFrame):
    """Affiche les métriques globales de progression"""
    col1, col2, col3, col4 = st.columns(4)
    
    total_exercises = len(df_progression)
    exercises_with_plateaus = len(df_progression[df_progression.get('plateau_detected', False) == True])
    positive_trends = len(df_progression[df_progression.get('progression_trend', '').str.lower() == 'positive'])
    avg_sessions = df_progression['total_sessions'].mean() if not df_progression.empty else 0
    
    with col1:
        st.metric("Total exercices", total_exercises)
    
    with col2:
        st.metric("Tendances positives", f"{positive_trends}/{total_exercises}")
    
    with col3:
        st.metric("Exercices en plateau", exercises_with_plateaus, 
                 delta=f"-{exercises_with_plateaus}" if exercises_with_plateaus > 0 else None)
    
    with col4:
        st.metric("Sessions moyennes", f"{avg_sessions:.1f}")

def _display_progression_trend_chart(df_progression: pd.DataFrame, filters: Dict):
    """Affiche le graphique des tendances de progression"""
    if df_progression.empty:
        st.info("Aucune donnée de tendance disponible")
        return
    
    # Vérifier si la colonne progression_trend existe et a des données
    if 'progression_trend' not in df_progression.columns or df_progression['progression_trend'].isna().all():
        st.info("Données de tendance non disponibles - l'API calcule maintenant les tendances automatiquement")
        return
    
    # Préparation des données pour le graphique
    trend_counts = df_progression['progression_trend'].value_counts().reset_index()
    trend_counts.columns = ['Tendance', 'Nombre']
    
    # Filtrer les valeurs nulles
    trend_counts = trend_counts[trend_counts['Tendance'].notna()]
    
    if trend_counts.empty:
        st.info("Aucune donnée de tendance disponible pour affichage")
        return
    
    # Mappage des couleurs
    color_map = {
        'positive': '#2ecc71',
        'negative': '#e74c3c', 
        'stable': '#f39c12',
        'unknown': '#95a5a6'
    }
    
    # Créer le color_discrete_map dynamiquement
    color_discrete_map = {}
    for _, row in trend_counts.iterrows():
        trend = row['Tendance']
        color_discrete_map[trend] = color_map.get(trend.lower() if pd.notna(trend) else 'unknown', '#95a5a6')
    
    fig_pie = px.pie(
        trend_counts,
        values='Nombre',
        names='Tendance',
        title="Répartition des tendances",
        color_discrete_map=color_discrete_map
    )
    
    fig_pie = apply_theme_to_chart(fig_pie, filters)
    st.plotly_chart(fig_pie, use_container_width=True)

def _display_progress_trend_scatter_chart(df_progression: pd.DataFrame, filters: Dict):
    """Affiche le graphique scatter des tendances de progression avec pente"""
    if df_progression.empty:
        st.info("Aucune donnée de progression disponible")
        return
    
    # Vérifier si nous avons les colonnes nécessaires pour le graphique scatter
    required_columns = ['total_sessions', 'trend_slope']
    if not all(col in df_progression.columns for col in required_columns):
        # Si les colonnes n'existent pas, essayer de les calculer
        st.info("Calcul des tendances de progression en cours...")
        return
    
    # Préparer les données pour create_progress_trend_chart
    # Cette fonction attend une colonne 'trend_slope' et 'exercise'
    scatter_data = df_progression[['exercise', 'total_sessions', 'trend_slope']].copy()
    
    # Filtrer les données valides
    scatter_data = scatter_data.dropna(subset=['trend_slope'])
    
    if scatter_data.empty:
        st.info("Aucune donnée de tendance de progression disponible")
        return
    
    # Créer le graphique avec la fonction utils
    fig = create_progress_trend_chart(scatter_data)
    
    # Appliquer le thème
    fig = apply_theme_to_chart(fig, filters)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ajouter des informations contextuelles
    st.markdown("""
    **📊 Interprétation du graphique :**
    - **Points verts** : Progression positive
    - **Points rouges** : Progression négative  
    - **Points gris** : Progression stable
    - **Taille des points** : Nombre de sessions
    - **Position Y** : Pente de progression (plus élevée = progression plus rapide)
    """)

def _display_volume_trends_chart(df_progression: pd.DataFrame, filters: Dict):
    """Affiche le graphique des tendances de volume"""
    if df_progression.empty:
        st.info("Aucune donnée de volume disponible")
        return
    
    # Vérifier que les colonnes de tendances existent et ont des données valides
    has_7d_data = 'volume_trend_7d' in df_progression.columns and not df_progression['volume_trend_7d'].isna().all()
    has_30d_data = 'volume_trend_30d' in df_progression.columns and not df_progression['volume_trend_30d'].isna().all()
    
    if not has_7d_data and not has_30d_data:
        st.info("Données de tendance de volume non disponibles - vérifiez que vous avez suffisamment de données d'entraînement")
        return
    
    # Création du graphique des tendances de volume
    fig_bar = go.Figure()
    
    # Tendances 7 jours
    if has_7d_data:
        fig_bar.add_trace(go.Bar(
            name='Tendance 7j',
            x=df_progression['exercise'],
            y=df_progression['volume_trend_7d'].fillna(0),
            marker_color='lightblue',
            opacity=0.7,
            hovertemplate="<b>%{x}</b><br>Tendance 7j: %{y:.1f}%<extra></extra>"
        ))
    
    # Tendances 30 jours
    if has_30d_data:
        fig_bar.add_trace(go.Bar(
            name='Tendance 30j',
            x=df_progression['exercise'],
            y=df_progression['volume_trend_30d'].fillna(0),
            marker_color='darkblue',
            opacity=0.8,
            hovertemplate="<b>%{x}</b><br>Tendance 30j: %{y:.1f}%<extra></extra>"
        ))
    
    fig_bar.update_layout(
        title="Tendances de volume par exercice",
        xaxis_title="Exercice",
        yaxis_title="Tendance (%)",
        barmode='group',
        xaxis_tickangle=-45
    )
    
    # Ligne de référence à 0
    fig_bar.add_hline(y=0, line_dash="dash", line_color="gray", 
                     annotation_text="Pas de changement")
    
    fig_bar = apply_theme_to_chart(fig_bar, filters)
    st.plotly_chart(fig_bar, use_container_width=True)

def _display_sessions_distribution_chart(df_progression: pd.DataFrame, filters: Dict):
    """Affiche la distribution des sessions par exercice"""
    if df_progression.empty:
        return
    
    st.subheader("Distribution des sessions d'entraînement")
    
    # Tri par nombre de sessions
    df_sorted = df_progression.sort_values('total_sessions', ascending=True)
    
    fig_bar = px.bar(
        df_sorted,
        x='total_sessions',
        y='exercise',
        orientation='h',
        title="Nombre de sessions par exercice",
        labels={'total_sessions': 'Nombre de sessions', 'exercise': 'Exercice'},
        color='total_sessions',
        color_continuous_scale='viridis'
    )
    
    fig_bar.update_layout(
        height=max(400, len(df_progression) * 25),
        showlegend=False
    )
    
    fig_bar = apply_theme_to_chart(fig_bar, filters)
    st.plotly_chart(fig_bar, use_container_width=True)

def _display_plateau_analysis_chart(df_progression: pd.DataFrame, filters: Dict):
    """Affiche l'analyse des plateaux avec temps depuis dernier PR - Version améliorée"""
    if df_progression.empty:
        return
    
    # Filtrer les exercices avec des données de PR
    pr_data = df_progression[df_progression['days_since_last_pr'].notna()].copy()
    
    if pr_data.empty:
        st.info("📊 Aucune donnée de PR disponible pour l'analyse des plateaux")
        st.markdown("""
        **Les Personal Records (PR) sont calculés automatiquement à partir de vos données d'entraînement.**
        
        Pour voir l'analyse des PR, assurez-vous d'avoir :
        - Au moins quelques sessions d'entraînement enregistrées
        - Des données de volume (répétitions × poids) complètes
        - Des exercices pratiqués régulièrement
        
        Les PR seront affichés dès que suffisamment de données seront disponibles.
        """)
        return
    
    st.subheader("🏆 Analyse des Personal Records (PR)")
    
    # Créer des catégories de temps avec couleurs
    pr_data['pr_category'] = pd.cut(
        pr_data['days_since_last_pr'],
        bins=[0, 7, 30, 90, float('inf')],
        labels=['< 1 semaine', '1-4 semaines', '1-3 mois', '> 3 mois']
    )
    
    # Compter par catégorie
    category_counts = pr_data['pr_category'].value_counts().reset_index()
    category_counts.columns = ['Période', 'Nombre']
    
    # Couleurs par catégorie (vert = récent, rouge = ancien)
    color_map = {
        '< 1 semaine': '#2ecc71',      # Vert
        '1-4 semaines': '#f39c12',     # Orange
        '1-3 mois': '#e67e22',         # Rouge-orange
        '> 3 mois': '#e74c3c'          # Rouge
    }
    
    # Graphique en barres horizontal avec couleurs
    fig_bar = px.bar(
        category_counts,
        x='Nombre',
        y='Période',
        orientation='h',
        title="📊 Répartition des Personal Records par ancienneté",
        color='Période',
        color_discrete_map=color_map,
        labels={'Nombre': 'Nombre d\'exercices', 'Période': 'Temps depuis le PR'}
    )
    
    fig_bar.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Nombre d'exercices",
        yaxis_title="Temps écoulé depuis le PR"
    )
    
    fig_bar.update_traces(
        hovertemplate="<b>%{y}</b><br>Exercices: %{x}<extra></extra>"
    )
    
    fig_bar = apply_theme_to_chart(fig_bar, filters)
    st.plotly_chart(fig_bar, use_container_width=True)
    

    
    # Graphique radar des PR par exercice (top 10)
    st.subheader("🎯 Top 10 des exercices par PR")
    
    # Vérifier si current_pr existe, sinon utiliser days_since_last_pr
    if 'current_pr' in pr_data.columns:
        sort_column = 'current_pr'
        top_pr = pr_data.nlargest(10, 'current_pr')
        radar_values = top_pr['current_pr']
        chart_title = "Personal Records par exercice (Top 10)"
        value_name = 'Volume PR'
    else:
        # Si pas de current_pr, trier par jours depuis PR (plus récent = plus petit nombre)
        sort_column = 'days_since_last_pr'
        top_pr = pr_data.nsmallest(10, 'days_since_last_pr')
        radar_values = top_pr['days_since_last_pr']
        chart_title = "Jours depuis dernier PR par exercice (Top 10)"
        value_name = 'Jours depuis PR'
        st.info("ℹ️ Utilisation des jours depuis PR (plus récent = plus petit nombre)")
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=radar_values,
        theta=top_pr['exercise'],
        fill='toself',
        name=value_name,
        line=dict(color='rgba(31, 119, 180, 0.8)', width=2),
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, radar_values.max() * 1.1]
            )),
        showlegend=False,
        title=chart_title,
        height=500
    )
    
    fig_radar = apply_theme_to_chart(fig_radar, filters)
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # Tableau détaillé des PR
    st.subheader("📋 Détail des Personal Records")
    
    # Préparer les données pour le tableau
    display_data = pr_data.copy()
    
    # Adapter selon les colonnes disponibles
    if 'current_pr' in pr_data.columns:
        display_data['PR_kg'] = display_data['current_pr'].round(1)
        sort_column = 'current_pr'
        ascending = False
    else:
        # Si pas de current_pr, créer une colonne factice et trier par jours
        display_data['PR_kg'] = 'N/A'
        sort_column = 'days_since_last_pr'
        ascending = True  # Plus récent = plus petit nombre
    
    display_data['Jours_depuis_PR'] = display_data['days_since_last_pr']
    
    # Gérer last_pr_date si disponible
    if 'last_pr_date' in pr_data.columns:
        display_data['Dernier_PR'] = display_data['last_pr_date'].dt.strftime('%d/%m/%Y')
    else:
        display_data['Dernier_PR'] = 'N/A'
    
    # Trier selon la colonne disponible
    display_data = display_data.sort_values(sort_column, ascending=ascending)
    
    # Sélectionner les colonnes à afficher (en vérifiant leur existence)
    available_columns = []
    column_names = []
    
    # Colonnes obligatoires
    if 'exercise' in display_data.columns:
        available_columns.append('exercise')
        column_names.append('Exercice')
    
    if 'PR_kg' in display_data.columns:
        available_columns.append('PR_kg')
        column_names.append('PR (kg)')
    
    if 'Jours_depuis_PR' in display_data.columns:
        available_columns.append('Jours_depuis_PR')
        column_names.append('Jours depuis PR')
    
    if 'Dernier_PR' in display_data.columns:
        available_columns.append('Dernier_PR')
        column_names.append('Date dernier PR')
    
    # Colonnes optionnelles
    if 'total_pr_count' in display_data.columns:
        available_columns.append('total_pr_count')
        column_names.append('Nombre PR')
    
    # Créer le DataFrame d'affichage
    display_df = display_data[available_columns].copy()
    display_df.columns = column_names
    
    # Appliquer des couleurs conditionnelles si la colonne 'Jours depuis PR' existe
    if 'Jours depuis PR' in display_df.columns:
        def color_days(val):
            if pd.isna(val):
                return 'background-color: lightgray'
            elif val <= 7:
                return 'background-color: #d4edda; color: #155724'  # Vert
            elif val <= 30:
                return 'background-color: #fff3cd; color: #856404'  # Jaune
            elif val <= 90:
                return 'background-color: #f8d7da; color: #721c24'  # Rouge-orange
            else:
                return 'background-color: #f5c6cb; color: #721c24'  # Rouge
        
        # Appliquer le style
        styled_df = display_df.style.applymap(color_days, subset=['Jours depuis PR'])
        st.dataframe(styled_df, use_container_width=True)
    else:
        # Afficher sans style si la colonne n'existe pas
        st.dataframe(display_df, use_container_width=True)

def _display_exercise_trend_analysis(exercise_data: pd.Series, filters: Dict):
    """Affiche l'analyse de tendance pour un exercice spécifique"""
    st.subheader("Analyse de tendance détaillée")
    
    # Créer un graphique de métriques
    metrics_data = {
        'Métrique': ['Tendance 7j', 'Tendance 30j'],
        'Valeur': [
            exercise_data.get('volume_trend_7d', 0),
            exercise_data.get('volume_trend_30d', 0)
        ]
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    
    if not metrics_df['Valeur'].isna().all():
        fig_bar = px.bar(
            metrics_df,
            x='Métrique',
            y='Valeur',
            title="Tendances de volume",
            labels={'Valeur': 'Tendance (%)'},
            color='Valeur',
            color_continuous_scale='RdYlGn'
        )
        
        fig_bar.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_bar = apply_theme_to_chart(fig_bar, filters)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Données de tendance non disponibles pour cet exercice")

def _display_exercise_volume_trends(exercise_data: pd.Series, filters: Dict):
    """Affiche les tendances de volume pour un exercice spécifique"""
    st.subheader("Évolution du volume")
    
    # Graphique de tendance simplifiée
    trend_7d = exercise_data.get('volume_trend_7d', 0)
    trend_30d = exercise_data.get('volume_trend_30d', 0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        _display_trend_metric("Tendance 7 jours", trend_7d, filters)
    
    with col2:
        _display_trend_metric("Tendance 30 jours", trend_30d, filters)
    
    # Recommandations basées sur les tendances
    _display_progression_recommendations(exercise_data)

def _display_progression_recommendations(exercise_data: pd.Series):
    """Affiche des recommandations basées sur la progression"""
    st.subheader("💡 Recommandations")
    
    recommendations = []
    
    # Analyse du plateau
    if exercise_data.get('plateau_detected', False):
        days_since_pr = exercise_data.get('days_since_last_pr')
        if days_since_pr and days_since_pr > 30:
            recommendations.append("🔄 Plateau détecté depuis plus de 30 jours - considérez un changement de programme")
        else:
            recommendations.append("⚠️ Plateau détecté - maintenez votre programme encore quelques séances")
    
    # Analyse des tendances
    trend_7d = exercise_data.get('volume_trend_7d', 0)
    trend_30d = exercise_data.get('volume_trend_30d', 0)
    
    if pd.notna(trend_7d) and trend_7d > 5:
        recommendations.append("📈 Excellente progression récente - continuez sur cette voie !")
    elif pd.notna(trend_7d) and trend_7d < -5:
        recommendations.append("📉 Baisse de volume récente - vérifiez votre récupération")
    
    if pd.notna(trend_30d) and trend_30d > 10:
        recommendations.append("🚀 Progression exceptionnelle sur le mois - maintenez l'intensité")
    elif pd.notna(trend_30d) and trend_30d < -10:
        recommendations.append("⚡ Baisse significative sur le mois - considérez une semaine de décharge")
    
    # Analyse du nombre de sessions
    total_sessions = exercise_data.get('total_sessions', 0)
    if total_sessions < 3:
        recommendations.append("📊 Peu de données disponibles - continuez l'entraînement pour plus d'analyses")
    elif total_sessions > 20:
        recommendations.append("🎯 Excellente consistance d'entraînement !")
    
    # Affichage des recommandations
    if recommendations:
        for rec in recommendations:
            st.write(f"• {rec}")
    else:
        st.info("Continuez votre programme actuel - progression stable")
