"""
Application principale du dashboard Streamlit pour Muscle-Analytics
Version refactorisée avec architecture modulaire
"""
import logging
import streamlit as st
from typing import Dict

# Imports des composants modulaires
from src.dashboard.config import DASHBOARD_CONFIG
from src.dashboard.styles.css import get_main_css, get_dark_theme_css, get_light_theme_css
from src.dashboard.components.sidebar import create_sidebar
from src.dashboard.components.kpis import display_kpis
from src.dashboard.components.charts import (
    display_volume_charts, 
    display_progression_charts, 
    display_heatmap_calendar
)
from src.dashboard.components.muscle_analysis import display_muscle_analysis
from src.dashboard.services.api_client import get_api_client

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_page_config():
    """Configure la page Streamlit"""
    st.set_page_config(
        page_title=DASHBOARD_CONFIG["title"],
        page_icon=DASHBOARD_CONFIG["icon"],
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_styles(theme: str = "Clair"):
    """Applique les styles CSS selon le thème choisi"""
    # Styles principaux
    st.markdown(get_main_css(), unsafe_allow_html=True)
    
    # Styles spécifiques au thème
    if theme == "Sombre":
        st.markdown(get_dark_theme_css(), unsafe_allow_html=True)
    else:  # Clair ou Auto - Force le mode clair
        st.markdown(get_light_theme_css(), unsafe_allow_html=True)

def display_header():
    """Affiche l'en-tête principal du dashboard"""
    st.title("💪 Muscle-Analytics Dashboard")
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def check_api_connection():
    """Vérifie la connexion à l'API et affiche les erreurs si nécessaire"""
    api_client = get_api_client()
    if not api_client.check_health():
        st.error("🚨 Impossible de se connecter à l'API")
        st.info("Vérifiez que l'API FastAPI est démarrée avec `docker compose up` ou `uvicorn src.api.main:app --reload`")
        return False
    return True

def display_tabs(filters: Dict):
    """Affiche les onglets principaux avec le contenu"""
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Volume", 
        "🚀 Progression", 
        "🔍 Détail Exercice", 
        "💪 Analyse Musculaire",
        "📅 Calendrier"
    ])
    
    with tab1:
        with st.spinner("📈 Chargement de l'analyse de volume..."):
            display_volume_charts(filters)
    
    with tab2:
        with st.spinner("🚀 Chargement de l'analyse de progression..."):
            display_progression_charts(filters)
    
    with tab3:
        st.info("� Analyse d'exercice détaillée temporairement désactivée")
    
    with tab4:
        with st.spinner("💪 Chargement de l'analyse musculaire..."):
            display_muscle_analysis(filters)
    
    with tab5:
        with st.spinner("📅 Chargement du calendrier..."):
            display_heatmap_calendar(filters)

def display_footer(filters: Dict):
    """Affiche le pied de page avec les informations sur les filtres"""
    st.divider()
    
    # Informations sur l'état du système
    _display_system_status(filters)

def _display_automatic_plateau_alerts(dashboard_data: Dict):
    """Affiche les alertes automatiques de plateau en haut du dashboard"""
    exercises_with_plateau = dashboard_data.get('exercises_with_plateau', [])
    
    if not exercises_with_plateau:
        return
    
    # Container d'alerte avec style d'urgence
    with st.container():
        st.markdown("""
        <div style="
            background: linear-gradient(90deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 5px solid #c44569;
        ">
        """, unsafe_allow_html=True)
        
        st.markdown("🚨 **ALERTE PLATEAU AUTOMATIQUE DÉTECTÉE**")
        
        # Métriques rapides
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Exercices en plateau", len(exercises_with_plateau), delta_color="inverse")
        
        with col2:
            total_exercises = dashboard_data.get('total_exercises', 0)
            if total_exercises > 0:
                plateau_percentage = (len(exercises_with_plateau) / total_exercises) * 100
                st.metric("% d'exercices en plateau", f"{plateau_percentage:.1f}%", delta_color="inverse")
            else:
                st.metric("% d'exercices en plateau", "N/A")
        
        with col3:
            st.metric("Niveau d'alerte", 
                     "🔴 Critique" if len(exercises_with_plateau) >= 3 else "🟡 Modéré" if len(exercises_with_plateau) == 2 else "🟠 Faible")
        
        # Message d'alerte contextuel
        if len(exercises_with_plateau) >= 3:
            st.warning("""
            **🔄 Programme complet à revoir** - Plus de 50% de vos exercices sont en plateau.
            
            **Actions immédiates recommandées :**
            - Changez complètement votre programme d'entraînement
            - Intégrez de nouveaux exercices et variations
            - Considérez une période de deload ou de récupération
            """)
        elif len(exercises_with_plateau) == 2:
            st.info("""
            **⚖️ Ajustement modéré nécessaire** - 2 exercices en plateau détectés.
            
            **Actions recommandées :**
            - Variez les rep ranges et intensités
            - Ajoutez des techniques d'intensification
            - Modifiez l'ordre des exercices
            """)
        else:
            st.info("""
            **🎯 Ajustement ciblé** - 1 exercice en plateau détecté.
            
            **Actions recommandées :**
            - Variez les paramètres de l'exercice
            - Ajoutez des variations
            - Considérez une progression plus lente
            """)
        
        # Liste des exercices en plateau
        st.markdown(f"**📋 Exercices en plateau :** {', '.join(exercises_with_plateau)}")
        
        st.markdown("</div>", unsafe_allow_html=True)

def _display_system_status(filters: Dict):
    """Affiche l'état du système"""
    col1, col2, col3 = st.columns(3)
    with col1:
        api_status = "🟢 Connectée" if filters.get('api_connected', False) else "🔴 Déconnectée"
        st.caption(f"**API**: {api_status}")
    with col2:
        exercises_count = len(filters.get('exercises_list', []))
        st.caption(f"**Exercices**: {exercises_count} disponibles")
    with col3:
        period_info = filters.get('period_preset', 'Non définie')
        if period_info.startswith(('📊', '📈', '📉', '📋', '📅')):
            period_info = period_info.split(' ', 1)[1] if ' ' in period_info else period_info
        st.caption(f"**Période**: {period_info}")

def main():
    """Fonction principale du dashboard"""
    # Configuration de la page
    setup_page_config()
    
    # Création de la barre latérale avec filtres
    filters = create_sidebar()
    
    # Application des styles selon le thème choisi
    apply_styles(filters.get('theme', 'Clair'))
    
    # En-tête principal
    display_header()
    
    # Vérification de la connexion API
    if not check_api_connection():
        st.stop()
    
    # Récupération des données du dashboard
    with st.spinner("🔄 Chargement des données..."):
        api_client = get_api_client()
        dashboard_data = api_client.get_dashboard_data()
    
    # Affichage des KPIs
    display_kpis(dashboard_data, filters)
    
    # Affichage des alertes automatiques de plateau
    if dashboard_data.get('exercises_with_plateau'):
        st.markdown("---")
        _display_automatic_plateau_alerts(dashboard_data)
        
    # Navigation par onglets
    display_tabs(filters)
    
    # Pied de page
    display_footer(filters)

if __name__ == "__main__":
    main()
