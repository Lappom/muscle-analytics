"""
Fonctions utilitaires pour le dashboard Streamlit
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import base64
from io import BytesIO

from .config import MUSCLE_GROUPS, CHART_CONFIG, get_muscle_color

def load_css(file_path: str) -> None:
    """Charge un fichier CSS personnalisé"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Fichier CSS non trouvé: {file_path}")

def format_date_ago(date_str: str) -> str:
    """Formate une date en 'il y a X jours'"""
    if not date_str:
        return "Aucune"
    
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        days_ago = (datetime.now().replace(tzinfo=date_obj.tzinfo) - date_obj).days
        
        if days_ago == 0:
            return "Aujourd'hui"
        elif days_ago == 1:
            return "Hier"
        else:
            return f"Il y a {days_ago} jours"
    except:
        return date_str[:10] if len(date_str) >= 10 else date_str

def format_weight(weight: float) -> str:
    """Formate un poids avec l'unité appropriée"""
    if weight is None:
        return "N/A"
    
    if weight > 1000:
        return f"{weight/1000:.1f}k kg"
    else:
        return f"{weight:.0f} kg"

def format_percentage(value: float) -> str:
    """Formate un pourcentage"""
    if value is None:
        return "N/A"
    return f"{value:.0%}"

def format_delta(value: float, format_type: str = "percentage") -> Optional[str]:
    """Formate un delta avec le bon format"""
    if value is None or value == 0:
        return None
    
    if format_type == "percentage":
        return f"{value:+.1f}%"
    else:
        return f"{value:+.1f}"

def create_muscle_radar_chart(muscle_data: Dict[str, float]) -> go.Figure:
    """Crée un graphique radar pour l'équilibre musculaire"""
    muscle_names = list(muscle_data.keys())
    muscle_values = list(muscle_data.values())
    
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
    ideal_balance = [100/len(muscle_names)] * len(muscle_names)
    fig.add_trace(go.Scatterpolar(
        r=ideal_balance,
        theta=muscle_names,
        mode='lines',
        name='Équilibre idéal',
        line=dict(color='red', dash='dash', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(muscle_values) * 1.2],
                ticksuffix='%'
            )),
        showlegend=True,
        title="Répartition du Volume par Groupe Musculaire",
        height=500
    )
    
    return fig

def create_progress_trend_chart(data: pd.DataFrame) -> go.Figure:
    """Crée un graphique de tendance de progression"""
    if data.empty:
        return go.Figure().add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
    
    # Vérifier que les colonnes requises sont présentes
    required_columns = ['exercise', 'total_sessions', 'trend_slope']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        return go.Figure().add_annotation(
            text=f"Colonnes manquantes: {', '.join(missing_columns)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
    
    # Filtrer les données valides (sans NaN)
    valid_data = data.dropna(subset=['trend_slope', 'total_sessions', 'exercise'])
    
    if valid_data.empty:
        return go.Figure().add_annotation(
            text="Aucune donnée valide disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
    
    # Ajouter une colonne pour la couleur basée sur la tendance
    valid_data['trend_color'] = valid_data['trend_slope'].apply(
        lambda x: 'Positive' if x > 0 else 'Négative' if x < 0 else 'Stable'
    )
    
    fig = px.scatter(
        valid_data,
        x='total_sessions',
        y='trend_slope',
        size='total_sessions',
        color='trend_color',
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
    
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                     "Sessions: %{x}<br>" +
                     "Tendance: %{y:.3f}<br>" +
                     "<extra></extra>"
    )
    
    # Ajouter une ligne de référence à y=0
    fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                  annotation_text="Pas de progression")
    
    fig.update_layout(
        xaxis_title="Nombre de sessions",
        yaxis_title="Pente de progression",
        showlegend=True,
        height=500
    )
    
    return fig

def create_volume_bar_chart(data: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Crée un graphique en barres pour le volume"""
    if data.empty:
        return go.Figure().add_annotation(
            text="Aucune donnée disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
    
    # Prendre les top N exercices
    top_data = data.nlargest(top_n, 'total_volume')
    
    fig = px.bar(
        top_data,
        x='total_volume',
        y='exercise',
        orientation='h',
        title=f"Top {top_n} - Volume total par exercice",
        labels={'total_volume': 'Volume total (kg)', 'exercise': 'Exercice'},
        color='total_volume',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        height=500,
        showlegend=False,
        xaxis_title="Volume total (kg)",
        yaxis_title="Exercice",
        yaxis={'categoryorder': 'total ascending'}
    )
    
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Volume: %{x:.0f} kg<extra></extra>"
    )
    
    return fig

def create_training_calendar(sessions_data: List[Dict]) -> go.Figure:
    """Crée un calendrier d'entraînement"""
    if not sessions_data:
        return go.Figure().add_annotation(
            text="Aucune session trouvée",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False, font_size=16
        )
    
    df = pd.DataFrame(sessions_data)
    df['date'] = pd.to_datetime(df['date'])
    df['date_only'] = df['date'].dt.date
    
    # Comptage des sessions par jour
    session_counts = df.groupby('date_only').size().reset_index(name='sessions_count')
    session_counts['date_str'] = session_counts['date_only'].astype(str)
    
    fig = px.bar(
        session_counts.sort_values('date_only'),
        x='date_str',
        y='sessions_count',
        title="Fréquence d'entraînement par jour",
        labels={'date_str': 'Date', 'sessions_count': 'Nombre de sessions'},
        color='sessions_count',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        showlegend=False
    )
    
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Sessions: %{y}<extra></extra>"
    )
    
    return fig

def detect_muscle_imbalances(muscle_data: Dict[str, float], threshold: float = 0.3) -> List[Tuple[str, str]]:
    """Détecte les déséquilibres musculaires"""
    if not muscle_data:
        return []
    
    avg_volume = sum(muscle_data.values()) / len(muscle_data)
    imbalances = []
    
    for muscle, volume in muscle_data.items():
        if volume < avg_volume * (1 - threshold):
            imbalances.append((muscle, "sous-développé"))
        elif volume > avg_volume * (1 + threshold):
            imbalances.append((muscle, "sur-développé"))
    
    return imbalances

def calculate_balance_score(muscle_data: Dict[str, float]) -> float:
    """Calcule un score d'équilibre musculaire (0-100)"""
    if not muscle_data:
        return 0
    
    values = list(muscle_data.values())
    std_dev = pd.Series(values).std()
    
    # Plus l'écart-type est faible, meilleur est l'équilibre
    # Score inversé et normalisé sur 100
    score = max(0, 100 - (std_dev * 2))
    return min(100, score)

def generate_recommendations(
    muscle_imbalances: List[Tuple[str, str]], 
    plateau_exercises: List[str],
    progress_exercises: List[str]
) -> List[str]:
    """Génère des recommandations personnalisées"""
    recommendations = []
    
    # Recommandations pour les déséquilibres musculaires
    underdeveloped = [muscle for muscle, status in muscle_imbalances if status == "sous-développé"]
    overdeveloped = [muscle for muscle, status in muscle_imbalances if status == "sur-développé"]
    
    if underdeveloped:
        recommendations.append(
            f"💡 Augmentez le volume d'entraînement pour: {', '.join(underdeveloped)}"
        )
    
    if overdeveloped:
        recommendations.append(
            f"⚖️ Considérez réduire le volume pour: {', '.join(overdeveloped)}"
        )
    
    # Recommandations pour les plateaux
    if plateau_exercises:
        recommendations.append(
            f"🔄 Variez les exercices en plateau: {', '.join(plateau_exercises[:3])}"
        )
        recommendations.append(
            "📈 Essayez de nouvelles techniques: drop-sets, super-sets, ou changez de rep range"
        )
    
    # Encouragements pour les bons progrès
    if progress_exercises:
        recommendations.append(
            f"✅ Continuez sur cette lancée pour: {', '.join(progress_exercises[:3])}"
        )
    
    # Recommandations générales
    if not recommendations:
        recommendations.append("🎯 Votre progression est équilibrée, continuez votre programme actuel!")
    
    return recommendations

def export_to_excel(data: Dict, filename: str = "muscle_analytics_report.xlsx") -> bytes:
    """Exporte les données vers Excel"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Feuille KPIs
        if 'kpis' in data:
            kpis_df = pd.DataFrame([data['kpis']])
            kpis_df.to_excel(writer, sheet_name='KPIs', index=False)
        
        # Feuille Volume
        if 'volume' in data:
            volume_df = pd.DataFrame(data['volume'])
            volume_df.to_excel(writer, sheet_name='Volume', index=False)
        
        # Feuille Progression
        if 'progression' in data:
            progression_df = pd.DataFrame(data['progression'])
            progression_df.to_excel(writer, sheet_name='Progression', index=False)
        
        # Feuille Analyse Musculaire
        if 'muscle_analysis' in data:
            muscle_df = pd.DataFrame([data['muscle_analysis']])
            muscle_df.to_excel(writer, sheet_name='Muscle_Analysis', index=False)
    
    output.seek(0)
    return output.getvalue()

def create_download_link(data: bytes, filename: str, text: str) -> str:
    """Crée un lien de téléchargement pour des données binaires"""
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'
    return href

def apply_filters(data: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """Applique les filtres aux données"""
    filtered_data = data.copy()
    
    # Filtre par exercice
    if filters.get('exercise'):
        filtered_data = filtered_data[filtered_data['exercise'] == filters['exercise']]
    
    # Filtre par groupe musculaire
    if filters.get('muscle_group'):
        # Cette logique nécessiterait un mapping exercice -> muscle
        pass
    
    # Filtre par type de série
    if filters.get('set_types'):
        filtered_data = filtered_data[filtered_data['set_type'].isin(filters['set_types'])]
    
    # Filtre par plage d'intensité
    if filters.get('intensity_range'):
        min_intensity, max_intensity = filters['intensity_range']
        if 'intensity' in filtered_data.columns:
            filtered_data = filtered_data[
                (filtered_data['intensity'] >= min_intensity) &
                (filtered_data['intensity'] <= max_intensity)
            ]
    
    return filtered_data

def show_loading_message(message: str):
    """Affiche un message de chargement personnalisé"""
    return st.spinner(message)
