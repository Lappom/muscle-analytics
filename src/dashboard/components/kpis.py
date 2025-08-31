"""
Composants pour l'affichage des KPIs
"""
import streamlit as st
from typing import Dict, Optional

from ..config import KPI_CONFIG, format_value
from ..utils import format_date_ago, format_weight, format_delta

def display_kpis(dashboard_data: Dict, filters: Optional[Dict] = None):
    """Affiche les KPIs principaux"""
    # Application de la vue compacte si demandée
    if filters and filters.get('compact_view', False):
        st.subheader("📊 Indicateurs Clés")
    else:
        st.header("📊 Indicateurs Clés")
    
    if not dashboard_data:
        st.warning("Aucune donnée disponible pour les KPIs")
        return
    
    # Tous les KPIs sur une seule ligne
    _display_all_kpis(dashboard_data, filters)
    
    # Alertes et recommandations
    _display_alerts_and_recommendations(dashboard_data)

def _display_all_kpis(dashboard_data: Dict, filters: Optional[Dict] = None):
    """Affiche tous les KPIs sur une seule ligne"""
    # Adaptation selon la vue compacte
    if filters and filters.get('compact_view', False):
        col1, col2, col3, col4 = st.columns(4)
    else:
        col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sessions = dashboard_data.get('total_sessions', 0)
        st.metric(
            label="📅 Sessions totales",
            value=total_sessions,
            help="Nombre total de sessions d'entraînement"
        )
    
    with col2:
        latest_session = dashboard_data.get('latest_session_date')
        date_display = format_date_ago(latest_session) if latest_session else "Aucune"
        
        st.metric(
            label="🕒 Dernière session",
            value=date_display,
            help="Date de la dernière session d'entraînement"
        )
    
    with col3:
        weekly_frequency = dashboard_data.get('weekly_frequency', 0)
        frequency_trend = dashboard_data.get('frequency_trend', 0)
        st.metric(
            label="📈 Fréquence/semaine",
            value=f"{weekly_frequency:.1f}",
            delta=format_delta(frequency_trend, "number"),
            help="Nombre moyen de sessions par semaine"
        )
    
    with col4:
        consistency_score = dashboard_data.get('consistency_score', 0)
        st.metric(
            label="🎯 Score de régularité",
            value=f"{consistency_score:.0%}",
            help="Régularité d'entraînement sur la période"
        )

def _display_alerts_and_recommendations(dashboard_data: Dict):
    """Affiche les alertes et recommandations"""
    # Alertes sur les plateaux
    plateaus_detected = dashboard_data.get('plateaus_detected', [])
    if plateaus_detected:
        st.markdown('<div class="alert-warning">', unsafe_allow_html=True)
        st.warning(f"⚠️ Plateaux détectés sur {len(plateaus_detected)} exercice(s)")
        for exercise in plateaus_detected[:3]:  # Afficher max 3 exercices
            st.write(f"• {exercise}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recommandations positives
    good_progress = dashboard_data.get('good_progress', [])
    if good_progress:
        st.markdown('<div class="alert-success">', unsafe_allow_html=True)
        st.success(f"✅ Bonne progression sur {len(good_progress)} exercice(s)")
        for exercise in good_progress[:2]:  # Afficher max 2 exercices
            st.write(f"• {exercise}")
        st.markdown('</div>', unsafe_allow_html=True)

def display_metric_card(title: str, value: str, delta: Optional[str] = None, help_text: str = "", icon: str = "📊"):
    """Affiche une carte de métrique personnalisée"""
    delta_html = f"<small style='color: green;'>{delta}</small>" if delta and delta.startswith('+') else f"<small style='color: red;'>{delta}</small>" if delta else ""
    
    st.markdown(f"""
    <div class="metric-card">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
            <span style="font-weight: 500; color: var(--text-muted);">{title}</span>
        </div>
        <div style="font-size: 2rem; font-weight: bold; color: var(--text-dark);">
            {value} {delta_html}
        </div>
        {f"<small style='color: var(--text-muted);'>{help_text}</small>" if help_text else ""}
    </div>
    """, unsafe_allow_html=True)
