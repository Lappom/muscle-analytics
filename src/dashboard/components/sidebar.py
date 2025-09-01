"""
Composants pour la barre latérale (sidebar)
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import tempfile
import os

from ..services.api_client import get_api_client
from src.etl.import_scripts import ETLImporter
from src.database import get_database, DatabaseEnvironment

def _check_admin_authentication() -> bool:
    """
    Vérifie si l'utilisateur a les droits d'administrateur.
    
    Cette fonction implémente une vérification de sécurité basique.
    En production, elle devrait être remplacée par un système d'authentification robuste.
    """
    # Vérification basique via session state (pour démonstration)
    # En production, utiliser un système d'authentification approprié
    if 'admin_authenticated' not in st.session_state:
        # Demander l'authentification admin
        st.sidebar.markdown("### 🔐 Authentification Administrateur")
        admin_password = st.sidebar.text_input(
            "Mot de passe administrateur", 
            type="password",
            key="admin_password_input"
        )
        
        if st.sidebar.button("🔑 Se connecter", key="admin_login"):
            # En production, vérifier contre une base de données sécurisée
            # Pour ce démonstrateur, utiliser un mot de passe simple
            if admin_password == "admin123":  # À remplacer par un système sécurisé
                st.session_state.admin_authenticated = True
                st.session_state.admin_auth_time = datetime.now()
                st.success("✅ Authentification administrateur réussie")
                st.rerun()
            else:
                st.error("❌ Mot de passe incorrect")
                return False
        
        return False
    
    # Vérifier l'expiration de la session (30 minutes)
    auth_time = st.session_state.get('admin_auth_time')
    if auth_time and (datetime.now() - auth_time) > timedelta(minutes=30):
        del st.session_state.admin_authenticated
        del st.session_state.admin_auth_time
        st.warning("⚠️ Session administrateur expirée. Veuillez vous reconnecter.")
        return False
    
    return True

def _show_admin_logout():
    """Affiche le bouton de déconnexion administrateur"""
    if st.session_state.get('admin_authenticated'):
        if st.sidebar.button("🚪 Déconnexion Admin", key="admin_logout"):
            del st.session_state.admin_authenticated
            del st.session_state.admin_auth_time
            st.success("✅ Déconnexion réussie")
            st.rerun()

# Constantes définies localement en attendant la mise à jour de config.py
PERIOD_OPTIONS = {
    "🌟 Depuis toujours": "all",
    "📊 1 semaine": 7,
    "📈 1 mois": 30, 
    "📉 3 mois": 90,
    "📋 6 mois": 180,
    "📅 1 an": 365,
    "🎯 Personnalisé": None
}

THEMES = ["🌅 Clair", "🌙 Sombre", "🤖 Auto"]

def create_api_status_header() -> bool:
    """Crée l'en-tête avec le statut de l'API"""
    api_client = get_api_client()
    api_connected = api_client.check_health()
    
    if api_connected:
        st.sidebar.markdown("""
        <div style="
            display: flex; 
            justify-content: center; 
            align-items: center; 
            margin: 0 0 1.5rem 0; 
            padding: 8px 12px;
            background: linear-gradient(135deg, #e8f5e8 0%, #f0fdf4 100%);
            border: 1px solid #22c55e;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(34, 197, 94, 0.1);
        ">
            <span style="
                font-size: 0.85rem; 
                font-weight: 600; 
                color: #16a34a;
                display: flex;
                align-items: center;
                gap: 6px;
            ">✅ API Connectée</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="
            display: flex; 
            justify-content: center; 
            align-items: center; 
            margin: 0 0 1.5rem 0; 
            padding: 8px 12px;
            background: linear-gradient(135deg, #fef2f2 0%, #fff5f5 100%);
            border: 1px solid #ef4444;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(239, 68, 68, 0.1);
        ">
            <span style="
                font-size: 0.85rem; 
                font-weight: 600; 
                color: #dc2626;
                display: flex;
                align-items: center;
                gap: 6px;
            ">❌ API Déconnectée</span>
        </div>
        """, unsafe_allow_html=True)
        st.sidebar.info("💡 Démarrez l'API avec `docker compose up` ou `uvicorn src.api.main:app --reload`")
    
    return api_connected

def create_period_section() -> Dict[str, Any]:
    """Crée la section de sélection de période"""
    st.sidebar.markdown("""
    <div style="margin: 0 0 1.25rem 0;">
        <h3 style="
            margin: 0 0 1rem 0; 
            padding: 0;
            color: #1f77b4; 
            font-weight: 700;
            font-size: 1.1rem;
            line-height: 1.2;
            display: flex;
            align-items: center;
            gap: 8px;
        ">📅 Période d'Analyse</h3>
        <div style="
            height: 2px;
            background: linear-gradient(90deg, #1f77b4 0%, #3498db 100%);
            border-radius: 1px;
            margin: 0 0 1rem 0;
        "></div>
    </div>
    """, unsafe_allow_html=True)
    
    period_preset = st.sidebar.selectbox(
        "Sélection rapide",
        list(PERIOD_OPTIONS.keys()),
        index=5,  # 1 an par défaut
        help="Choisissez une période prédéfinie ou personnalisez",
        key='period_preset'
    )
    
    # Calcul des dates selon le preset
    period_value = PERIOD_OPTIONS[period_preset]
    if period_value == "all":
        # Toutes les dates - utilisation de dates très larges
        default_start = datetime(2000, 1, 1)  # Date très ancienne
        default_end = datetime.now()
        custom_dates = False
    elif period_value is not None:
        days_back = period_value
        default_start = datetime.now() - timedelta(days=days_back)
        default_end = datetime.now()
        custom_dates = False
    else:
        default_start = datetime.now() - timedelta(days=30)
        default_end = datetime.now()
        custom_dates = True
    
    # Dates personnalisées (affichées uniquement si personnalisé est sélectionné)
    if custom_dates:
        st.sidebar.markdown("""
        <div style="margin: 0.75rem 0 0.5rem 0;">
            <span style="
                font-size: 0.85rem; 
                font-weight: 600; 
                color: #374151;
                display: block;
                margin-bottom: 8px;
            ">📅 Dates personnalisées</span>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input(
                "Début",
                value=default_start.date(),
                max_value=date.today(),
                help="Date de début de l'analyse",
                key='start_date'
            )
        
        with col2:
            end_date = st.date_input(
                "Fin", 
                value=default_end.date(),
                max_value=date.today(),
                help="Date de fin de l'analyse",
                key='end_date'
            )
    else:
        start_date = default_start.date()
        end_date = default_end.date()
    
    return {
        'start_date': start_date.isoformat() if start_date else None,
        'end_date': end_date.isoformat() if end_date else None,
        'period_preset': period_preset,
        'custom_dates': custom_dates
    }





def create_appearance_section() -> Dict[str, Any]:
    """Crée la section de personnalisation d'apparence"""
    with st.sidebar.expander("🎨 Personnalisation", expanded=False):
        # Thème de l'interface
        st.markdown("""
        <div style="
            font-size: 0.9rem; 
            font-weight: 600; 
            color: #374151;
            margin: 0 0 8px 0;
            padding: 0;
            display: flex;
            align-items: center;
            gap: 6px;
        ">🎨 Thème de l'interface</div>
        """, unsafe_allow_html=True)
        
        theme = st.selectbox(
            "Thème de l'interface",
            THEMES,
            index=0,
            help="Choisissez l'apparence de l'interface",
            label_visibility="hidden",
            key='theme'
        )
        
        # Espacement entre les sections
        st.markdown('<div style="margin: 1.25rem 0;"></div>', unsafe_allow_html=True)
        
        # Préférences d'affichage
        st.markdown("""
        <div style="
            font-size: 0.9rem; 
            font-weight: 600; 
            color: #374151;
            margin: 0 0 12px 0;
            padding: 0;
            display: flex;
            align-items: center;
            gap: 6px;
        ">📊 Préférences d'Affichage</div>
        """, unsafe_allow_html=True)
        
        show_tooltips = st.checkbox(
            "💡 Afficher les info-bulles", 
            value=True,
            help="Activer/désactiver les info-bulles explicatives",
            key='show_tooltips'
        )
        show_animations = st.checkbox(
            "✨ Animations des graphiques", 
            value=True,
            help="Activer/désactiver les animations dans les graphiques",
            key='show_animations'
        )
        compact_view = st.checkbox(
            "📱 Vue compacte", 
            value=False,
            help="Optimiser l'affichage pour les petits écrans",
            key='compact_view'
        )
    
    return {
        'theme': theme.split(" ", 1)[1] if " " in theme else theme,
        'show_tooltips': show_tooltips,
        'show_animations': show_animations,
        'compact_view': compact_view
    }

def create_quick_actions_section():
    """Crée la section des actions rapides"""
    st.sidebar.markdown("""
    <div style="margin: 2rem 0 1.25rem 0;">
        <h3 style="
            margin: 0 0 1rem 0; 
            padding: 0;
            color: #16a085; 
            font-weight: 700;
            font-size: 1.1rem;
            line-height: 1.2;
            display: flex;
            align-items: center;
            gap: 8px;
        ">⚡ Actions Rapides</h3>
        <div style="
            height: 2px;
            background: linear-gradient(90deg, #16a085 0%, #27ae60 100%);
            border-radius: 1px;
            margin: 0 0 1rem 0;
        "></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Actions rapides - boutons en colonne
    if st.sidebar.button("📥 Export PDF", help="Exporter le rapport en PDF", use_container_width=True):
        st.info("🚧 Export PDF en développement")
    
    if st.sidebar.button("🔄 Actualiser", help="Recharger toutes les données", use_container_width=True):
        st.rerun()
    
    if st.sidebar.button("🧹 Réinitialiser", help="Remettre les filtres par défaut", use_container_width=True):
        # Réinitialiser tous les filtres dans le session state
        keys_to_reset = [
            'period_preset',
            'start_date', 
            'end_date',
            'theme',
            'show_tooltips',
            'show_animations',
            'compact_view'
        ]
        
        for key in keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("🎯 Filtres réinitialisés avec succès!")
        st.rerun()
    
    # Affichage du statut d'authentification administrateur
    _show_admin_logout()

def create_data_import_section():
    """Crée la section d'import de données"""
    st.sidebar.markdown("""
    <div style="margin: 2rem 0 1.25rem 0;">
        <h3 style="
            margin: 0 0 1rem 0; 
            padding: 0;
            color: #8e44ad; 
            font-weight: 700;
            font-size: 1.1rem;
            line-height: 1.2;
            display: flex;
            align-items: center;
            gap: 8px;
        ">📂 Import de Données</h3>
        <div style="
            height: 2px;
            background: linear-gradient(90deg, #8e44ad 0%, #9b59b6 100%);
            border-radius: 1px;
            margin: 0 0 1rem 0;
        "></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section de sélection du fichier
    st.sidebar.markdown("""
    <div style="
        font-size: 0.9rem; 
        font-weight: 600; 
        color: #374151;
        margin: 0 0 8px 0;
        padding: 0;
        display: flex;
        align-items: center;
        gap: 6px;
    ">📁 Sélection du fichier</div>
    """, unsafe_allow_html=True)
    
    uploaded = st.sidebar.file_uploader(
        "Fichier d'entraînement",
        type=["csv", "xml"],
        help="Sélectionnez un fichier CSV ou XML contenant vos données d'entraînement",
        key="upload_import_file",
        label_visibility="collapsed"
    )
    
    # Section des options d'import
    st.sidebar.markdown("""
    <div style="
        font-size: 0.9rem; 
        font-weight: 600; 
        color: #374151;
        margin: 1rem 0 8px 0;
        padding: 0;
        display: flex;
        align-items: center;
        gap: 6px;
    ">⚙️ Options d'import</div>
    """, unsafe_allow_html=True)
    
    force = st.sidebar.checkbox(
        "🔄 Forcer l'import (ignorer les doublons)",
        value=False,
        help="Insère les données même si la session existe déjà",
        key="force_import_checkbox"
    )
    
    clear_before = st.sidebar.checkbox(
        "🗑️ Vider la base avant import",
        value=False,
        help="⚠️ Supprime toutes les données existantes avant l'import",
        key="clear_before_import"
    )
    
    # Bouton d'import
    st.sidebar.markdown('<div style="margin: 1rem 0 0.5rem 0;"></div>', unsafe_allow_html=True)
    
    if st.sidebar.button("⬆️ Lancer l'import", 
                        use_container_width=True, 
                        key="run_import_button",
                        type="primary"):
        if not uploaded:
            st.warning("Veuillez sélectionner un fichier CSV ou XML.")
        else:
            # ✅ **VÉRIFICATION DE SÉCURITÉ : Authentification requise pour vider la base**
            if clear_before:
                # Vérification d'authentification avant suppression
                if not _check_admin_authentication():
                    st.error("❌ Accès refusé : Seuls les administrateurs peuvent vider la base de données")
                    return
                
                # Confirmation supplémentaire pour suppression
                if not st.session_state.get('confirmed_deletion', False):
                    st.warning("⚠️ ATTENTION : Cette action supprimera TOUTES les données existantes !")
                    if st.sidebar.button("🔐 Confirmer la suppression (Admin uniquement)", type="secondary"):
                        st.session_state.confirmed_deletion = True
                        st.rerun()
                    return
            
            # Écriture dans un fichier temporaire pour l'ETL
            suffix = Path(uploaded.name).suffix
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    file_content = uploaded.getbuffer()
                    tmp.write(file_content)
                    tmp_path = tmp.name
                
                # Vérification du fichier temporaire
                if os.path.exists(tmp_path):
                    temp_size = os.path.getsize(tmp_path)
                    if temp_size != len(file_content):
                        st.warning(f"⚠️ Différence de taille détectée!")
                
                # Détection de gros fichier pour optimisations
                is_large_file = len(file_content) > 1_000_000  # > 1MB
                
                # Lancer l'import ETL
                with st.spinner("🚚 Import des données en cours..."):
                    # ✅ **ÉTAPE 1 : Vider la base si demandé (avec vérification de sécurité)**
                    if clear_before:
                        try:
                            db = get_database()
                            # Suppression en cascade dans l'ordre correct
                            sets_deleted = db.execute_update("DELETE FROM sets")
                            sessions_deleted = db.execute_update("DELETE FROM sessions")
                            st.success(f"🗑️ Base vidée : {sets_deleted} séries, {sessions_deleted} sessions supprimées")
                            # Réinitialiser la confirmation après suppression réussie
                            st.session_state.confirmed_deletion = False
                        except Exception as e:
                            st.error(f"❌ Erreur lors du vidage : {e}")
                            return
                    
                    # ✅ **ÉTAPE 2 : Import des données**
                    importer = ETLImporter(db_manager=get_database())
                    result = importer.import_file(tmp_path, force_import=force)
                    report = importer.generate_import_report(result)
                # Affichage du résultat
                if result.get('success'):
                    st.success("Import réussi ✔")
                    st.code(report)
                    # Forcer le rechargement pour mettre à jour la liste des exercices
                    st.rerun()
                else:
                    st.error("Échec de l'import ❌")
                    st.code(report)
            except Exception as e:
                st.error(f"Erreur lors de l'import: {e}")
            finally:
                # Nettoyage du fichier temporaire
                try:
                    if tmp_path and os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except Exception:
                    pass



def create_help_section():
    """Crée la section d'aide et support"""
    with st.sidebar.expander("❓ Aide & Support", expanded=False):
        st.markdown("**🚀 Démarrage rapide:**")
        st.markdown("""
        1. Sélectionnez votre période d'analyse
        2. Choisissez un exercice ou muscle  
        3. Explorez les onglets d'analyse
        """)
        
        st.markdown("**💡 Conseils:**")
        st.markdown("""
        - Utilisez les presets pour analyser rapidement
        - Les filtres avancés permettent une analyse précise
        - Exportez vos rapports pour les partager
        """)
        
        st.markdown("**🆘 Problèmes courants:**")
        st.markdown("""
        - API non connectée → Vérifiez le serveur
        - Pas de données → Vérifiez la période
        - Graphiques vides → Ajustez les filtres
        """)

def create_sidebar() -> Dict:
    """Crée la barre latérale complète avec tous les filtres"""
    # En-tête avec status API
    api_connected = create_api_status_header()
    
    # Section période
    period_data = create_period_section()
    
    # Section apparence
    appearance_data = create_appearance_section()
    
    # Actions rapides
    create_quick_actions_section()
    
    # Section d'import de données
    create_data_import_section()
    
    # Combinaison de tous les filtres
    filters = {
        **period_data,
        **appearance_data,
        'api_connected': api_connected
    }
    
    # Espacement avant la section d'aide
    st.sidebar.markdown('<div style="margin: 2rem 0;"></div>', unsafe_allow_html=True)
    
    # Section d'aide
    create_help_section()
    
    return filters
