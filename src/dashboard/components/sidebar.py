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

SET_TYPES = ["✨ Principales", "🔥 Échauffement", "💥 Drop-set", "⚡ Super-set"]

INTENSITY_PRESETS = {
    "🎯 Personnalisé": None,
    "🟢 Légère (50-70%)": (50, 70),
    "🟡 Modérée (70-85%)": (70, 85),
    "🔴 Intense (85-100%)": (85, 100),
    "🌈 Toutes intensités": (0, 100)
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

def create_exercise_section() -> Dict[str, Any]:
    """Crée la section de sélection d'exercices"""
    st.sidebar.markdown("""
    <div style="margin: 2rem 0 1.25rem 0;">
        <div style="
            height: 2px;
            background: linear-gradient(90deg, #2ecc71 0%, #3498db 100%);
            border-radius: 1px;
            margin: 0 0 1rem 0;
        "></div>
        <h3 style="
            margin: 0 0 1rem 0; 
            padding: 0;
            color: #2ecc71; 
            font-weight: 700;
            font-size: 1.1rem;
            line-height: 1.2;
            display: flex;
            align-items: center;
            gap: 8px;
        ">🏋️‍♂️ Sélection d'Exercices</h3>
    </div>
    """, unsafe_allow_html=True)
    
    api_client = get_api_client()
    exercises = api_client.get_exercises()
    clean_muscle = "Tous les muscles"
    clean_exercise = None
    
    if exercises:
        # Filtre par groupe musculaire d'abord
        muscle_groups = ["🎯 Tous les muscles", "💪 Pectoraux", "🔙 Dos", "🦵 Jambes", "👐 Épaules", "💪 Bras", "🏃 Core"]
        selected_muscle = st.sidebar.selectbox(
            "Groupe musculaire",
            muscle_groups,
            index=0,
            help="Filtrez par groupe musculaire pour une analyse ciblée",
            key='selected_muscle'
        )
        
        # Nettoyage du nom du muscle (retirer l'emoji)
        clean_muscle = selected_muscle.split(" ", 1)[1] if " " in selected_muscle else selected_muscle
        
        # Espacement entre les sélecteurs
        st.sidebar.markdown('<div style="margin: 0.75rem 0;"></div>', unsafe_allow_html=True)
        
        # Filtrage des exercices selon le muscle sélectionné
        if clean_muscle == "Tous les muscles":
            available_exercises = ["🎯 Tous les exercices"] + [f"🏋️‍♂️ {ex}" for ex in exercises]
        else:
            available_exercises = ["🎯 Tous les exercices"] + [f"🏋️‍♂️ {ex}" for ex in exercises]
        
        selected_exercise = st.sidebar.selectbox(
            "Exercice spécifique",
            available_exercises,
            index=0,
            help="Sélectionnez un exercice pour une analyse détaillée",
            key='selected_exercise'
        )
        
        # Nettoyage du nom de l'exercice
        if selected_exercise.startswith("🏋️‍♂️ "):
            clean_exercise = selected_exercise[5:]
        else:
            clean_exercise = None
        
    else:
        st.sidebar.markdown("""
        <div style="
            padding: 12px;
            background: linear-gradient(135deg, #fff3cd 0%, #fef9e7 100%);
            border: 1px solid #ffc107;
            border-radius: 8px;
            margin: 1rem 0;
        ">
            <span style="
                font-size: 0.85rem;
                color: #856404;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 6px;
            ">⚠️ Aucun exercice trouvé dans la base de données</span>
        </div>
        """, unsafe_allow_html=True)
    
    return {
        'muscle_group': clean_muscle if clean_muscle != "Tous les muscles" else None,
        'exercise': clean_exercise,
        'exercises_list': exercises
    }

def create_advanced_filters_section() -> Dict[str, Any]:
    """Crée la section des filtres avancés"""
    st.sidebar.markdown("""
    <div style="margin: 2rem 0 1rem 0;">
        <div style="
            height: 2px;
            background: linear-gradient(90deg, #9b59b6 0%, #e74c3c 100%);
            border-radius: 1px;
            margin: 0;
        "></div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar.expander("⚙️ Filtres Avancés", expanded=False):
        # Type de série
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
        ">🎯 Types de Séries</div>
        """, unsafe_allow_html=True)
        
        set_types = st.multiselect(
            "Types de séries",
            SET_TYPES,
            default=["✨ Principales"],
            help="Sélectionnez les types de séries à inclure dans l'analyse",
            label_visibility="hidden",
            key='set_types'
        )
        
        # Espacement entre les sections
        st.markdown('<div style="margin: 1.25rem 0;"></div>', unsafe_allow_html=True)
        
        # Plage d'intensité
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
        ">💪 Intensité d'Entraînement</div>
        """, unsafe_allow_html=True)
        
        intensity_preset = st.selectbox(
            "Intensité d'entraînement",
            list(INTENSITY_PRESETS.keys()),
            index=4,
            help="Sélectionnez une plage d'intensité prédéfinie",
            label_visibility="hidden",
            key='intensity_preset'
        )
        
        if INTENSITY_PRESETS[intensity_preset] is not None:
            intensity_range = INTENSITY_PRESETS[intensity_preset]
            # Plus de pastille pour les presets d'intensité - interface plus épurée
        else:  # Personnalisé
            st.markdown('<div style="margin: 0.5rem 0;"></div>', unsafe_allow_html=True)
            intensity_range = st.slider(
                "Plage d'intensité (%)",
                min_value=0,
                max_value=100,
                value=(70, 100),
                step=5,
                help="Ajustez la plage d'intensité manuellement",
                key='intensity_range'
            )
    
    return {
        'set_types': [st.replace("✨ ", "").replace("🔥 ", "").replace("💥 ", "").replace("⚡ ", "") for st in set_types],
        'intensity_range': intensity_range
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
        <div style="
            height: 2px;
            background: linear-gradient(90deg, #16a085 0%, #27ae60 100%);
            border-radius: 1px;
            margin: 0 0 1rem 0;
        "></div>
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
    </div>
    """, unsafe_allow_html=True)
    
    # Actions d'export
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("📥 Export PDF", help="Exporter le rapport en PDF", use_container_width=True):
            st.info("🚧 Export PDF en développement")
    with col2:
        if st.button("📊 Export Excel", help="Exporter les données en Excel", use_container_width=True):
            st.info("🚧 Export Excel en développement")
    
    st.sidebar.markdown('<div style="margin: 0.75rem 0;"></div>', unsafe_allow_html=True)
    
    # Actions de contrôle
    col3, col4 = st.sidebar.columns(2)
    with col3:
        if st.button("🔄 Actualiser", help="Recharger toutes les données", use_container_width=True):
            st.rerun()
    with col4:
        if st.button("🧹 Réinitialiser", help="Remettre les filtres par défaut", use_container_width=True):
            # Réinitialiser tous les filtres dans le session state
            keys_to_reset = [
                'period_preset',
                'start_date', 
                'end_date',
                'selected_muscle',
                'selected_exercise',
                'set_types',
                'intensity_preset',
                'intensity_range',
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

    # Import de données (CSV/XML)
    st.sidebar.markdown('<div style="margin: 1rem 0 0.5rem 0;"></div>', unsafe_allow_html=True)
    with st.sidebar.expander("📂 Importer des données (CSV/XML)", expanded=False):
        uploaded = st.file_uploader(
            "Sélectionnez un fichier",
            type=["csv", "xml"],
            help="Importe des données d'entraînement au format CSV ou XML",
            key="upload_import_file"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            force = st.checkbox(
                "Forcer l'import (ignorer les doublons)",
                value=False,
                help="Insère même si la session existe déjà",
                key="force_import_checkbox"
            )
        with col2:
            clear_before = st.checkbox(
                "Vider la base avant import",
                value=False,
                help="⚠️ Supprime toutes les données existantes",
                key="clear_before_import"
            )
        if st.button("⬆️ Importer en base", use_container_width=True, key="run_import_button"):
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
                        if st.button("🔐 Confirmer la suppression (Admin uniquement)", type="secondary"):
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

def create_active_filters_summary(filters: Dict) -> int:
    """Crée le résumé des filtres actifs et retourne le nombre de filtres"""
    st.sidebar.markdown("""
    <div style="margin: 2rem 0 1.25rem 0;">
        <div style="
            height: 2px;
            background: linear-gradient(90deg, #8e44ad 0%, #3498db 100%);
            border-radius: 1px;
            margin: 0 0 1rem 0;
        "></div>
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
        ">📋 Filtres Actifs</h3>
    </div>
    """, unsafe_allow_html=True)
    
    active_filters = []
    if filters.get('exercise'):
        active_filters.append(f"🏋️‍♂️ {filters['exercise']}")
    if filters.get('muscle_group'):
        active_filters.append(f"💪 {filters['muscle_group']}")
    if filters.get('period_preset') != "📈 30 derniers jours":
        active_filters.append(f"📅 {filters['period_preset'].split(' ', 1)[1]}")
    if len(filters.get('set_types', [])) < 4:
        active_filters.append(f"🎯 {len(filters.get('set_types', []))} type(s) de série")
    if filters.get('intensity_range') != (0, 100):
        intensity = filters.get('intensity_range', (0, 100))
        active_filters.append(f"💪 {intensity[0]}-{intensity[1]}%")
    
    if active_filters:
        # Affichage des badges avec espacement optimisé
        st.sidebar.markdown("""
        <div style="
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            align-items: flex-start;
            margin: 0 0 12px 0;
            padding: 0;
        ">
        """, unsafe_allow_html=True)
        
        # Affichage de chaque badge individuellement
        for i, filter_item in enumerate(active_filters):
            # Couleurs alternées pour différencier les filtres
            colors = [
                "#1f77b4",  # Bleu
                "#2ecc71",  # Vert
                "#e74c3c",  # Rouge
                "#f39c12",  # Orange
                "#9b59b6"   # Violet
            ]
            color = colors[i % len(colors)]
            
            st.sidebar.markdown(f"""
            <span style="
                display: inline-block;
                background: {color};
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.7rem;
                font-weight: 600;
                line-height: 1.3;
                white-space: nowrap;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 0;
                border: 1px solid rgba(255,255,255,0.2);
            ">{filter_item}</span>
            """, unsafe_allow_html=True)
        
        st.sidebar.markdown("</div>", unsafe_allow_html=True)
        
        # Indicateur du nombre de filtres plus compact
        st.sidebar.markdown(f"""
        <div style="
            text-align: center;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 6px 8px;
            margin: 0;
        ">
            <span style="
                color: #495057;
                font-size: 0.75rem;
                font-weight: 600;
            ">{len(active_filters)} filtre(s) actif(s)</span>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        # État "aucun filtre" plus épuré
        st.sidebar.markdown("""
        <div style="
            text-align: center;
            background: linear-gradient(135deg, #e8f5e8 0%, #f0fdf4 100%);
            border: 1px solid #22c55e;
            border-radius: 8px;
            padding: 12px;
            margin: 0;
        ">
            <div style="
                color: #16a34a;
                font-weight: 600;
                font-size: 0.85rem;
                margin-bottom: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
            ">🎯 Analyse complète</div>
            <div style="
                color: #15803d;
                font-size: 0.7rem;
                opacity: 0.8;
            ">Toutes les données incluses</div>
        </div>
        """, unsafe_allow_html=True)
    
    return len(active_filters)

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
    
    # Section exercices
    exercise_data = create_exercise_section()
    
    # Section filtres avancés
    advanced_filters = create_advanced_filters_section()
    
    # Section apparence
    appearance_data = create_appearance_section()
    
    # Actions rapides
    create_quick_actions_section()
    
    # Combinaison de tous les filtres
    filters = {
        **period_data,
        **exercise_data,
        **advanced_filters,
        **appearance_data,
        'api_connected': api_connected
    }
    
    # Résumé des filtres actifs
    active_filters_count = create_active_filters_summary(filters)
    filters['active_filters_count'] = active_filters_count
    
    # Espacement avant la section d'aide
    st.sidebar.markdown('<div style="margin: 2rem 0;"></div>', unsafe_allow_html=True)
    
    # Section d'aide
    create_help_section()
    
    return filters
