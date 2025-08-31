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
        
        # Formatage de la fréquence hebdomadaire
        if weekly_frequency > 10:
            frequency_display = f"{weekly_frequency:.0f}"
        elif weekly_frequency > 1:
            frequency_display = f"{weekly_frequency:.1f}"
        else:
            frequency_display = f"{weekly_frequency:.2f}"
            
        st.metric(
            label="📈 Fréquence/semaine",
            value=frequency_display,
            delta=format_delta(frequency_trend, "number"),
            help="Nombre moyen de sessions par semaine"
        )
    
    with col4:
        consistency_score = dashboard_data.get('consistency_score', 0)
        
        # Formatage du score de régularité
        if consistency_score >= 0.8:
            consistency_display = f"{consistency_score:.0%}"
            delta_color = "normal"
        elif consistency_score >= 0.6:
            consistency_display = f"{consistency_score:.0%}"
            delta_color = "normal"
        else:
            consistency_display = f"{consistency_score:.0%}"
            delta_color = "inverse"
            
        st.metric(
            label="🎯 Score de régularité",
            value=consistency_display,
            help="Régularité d'entraînement sur la période"
        )

def _display_alerts_and_recommendations(dashboard_data: Dict):
    """Affiche les alertes et recommandations"""
    # Alertes sur les plateaux
    exercises_with_plateau = dashboard_data.get('exercises_with_plateau', [])
    
    if exercises_with_plateau:
        # Alerte principale avec style d'urgence
        st.error("🚨 **ALERTE PLATEAU DÉTECTÉE**")
        
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
        
        # Bouton pour voir l'analyse détaillée
        if st.button("🔍 Voir l'analyse détaillée des plateaux", type="primary"):
            st.session_state.show_plateau_analysis = True
            st.rerun()
    else:
        # Aucun plateau détecté - afficher un message de succès
        st.success("🎉 **Aucun plateau détecté !** Votre progression est régulière.")
        
        # Métriques positives
        col1, col2, col3 = st.columns(3)
        with col1:
            total_exercises = dashboard_data.get('total_exercises', 0)
            st.metric("Total exercices", total_exercises, delta_color="normal")
        
        with col2:
            weekly_frequency = dashboard_data.get('weekly_frequency', 0)
            st.metric("Fréquence hebdomadaire", f"{weekly_frequency}/sem", delta_color="normal")
        
        with col3:
            consistency_score = dashboard_data.get('consistency_score', 0)
            st.metric("Score de régularité", f"{consistency_score:.1f}", delta_color="normal")
    
    # Alertes sur la fréquence d'entraînement
    weekly_frequency = dashboard_data.get('weekly_frequency', 0)
    if weekly_frequency < 2:
        st.warning("""
        **📉 Fréquence d'entraînement faible** - Moins de 2 sessions par semaine.
        
        **Recommandations :**
        - Augmentez progressivement la fréquence
        - Planifiez vos sessions à l'avance
        - Commencez par des sessions courtes mais régulières
        """)
    
    # Alertes sur la régularité
    consistency_score = dashboard_data.get('consistency_score', 0)
    if consistency_score < 0.6:
        st.warning("""
        **🎯 Régularité d'entraînement à améliorer** - Score de régularité faible.
        
        **Recommandations :**
        - Établissez une routine fixe
        - Utilisez des rappels et planifications
        - Commencez par des objectifs modestes
        """)
    


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
