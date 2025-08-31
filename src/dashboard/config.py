"""
Configuration et paramètres pour le dashboard Streamlit
"""

import os
from typing import Dict, List

# Configuration de l'API
API_BASE_URL = os.getenv("API_BASE_URL", "https://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# Configuration du dashboard
DASHBOARD_CONFIG = {
    "title": "Muscle-Analytics Dashboard",
    "icon": "💪",
    "layout": "wide",
    "theme": {
        "primary_color": "#1f77b4",
        "secondary_color": "#ff7f0e",
        "success_color": "#2ecc71",
        "warning_color": "#f39c12",
        "danger_color": "#e74c3c"
    }
}

# Mapping des groupes musculaires
MUSCLE_GROUPS = {
    "Pectoraux": {
        "exercises": ["Développé couché", "Développé incliné", "Dips", "Écarté"],
        "color": "#e74c3c"
    },
    "Dos": {
        "exercises": ["Tractions", "Rowing", "Soulevé de terre", "Tirage vertical"],
        "color": "#3498db"
    },
    "Jambes": {
        "exercises": ["Squat", "Fentes", "Presse à cuisses", "Extensions quadriceps"],
        "color": "#2ecc71"
    },
    "Épaules": {
        "exercises": ["Développé militaire", "Élévations latérales", "Oiseau", "Développé Arnold"],
        "color": "#f39c12"
    },
    "Bras": {
        "exercises": ["Curl biceps", "Extensions triceps", "Dips", "Curl marteau"],
        "color": "#9b59b6"
    },
    "Core": {
        "exercises": ["Planche", "Crunchs", "Mountain climbers", "Russian twists"],
        "color": "#1abc9c"
    }
}

# Configuration des filtres
FILTER_CONFIG = {
    "periods": {
        "7 derniers jours": 7,
        "30 derniers jours": 30,
        "3 derniers mois": 90,
        "6 derniers mois": 180,
        "1 an": 365
    },
    "set_types": ["Principales", "Échauffement", "Drop-set", "Super-set"],
    "intensity_ranges": {
        "Légère": (50, 70),
        "Modérée": (70, 85),
        "Intense": (85, 100)
    }
}

# Configuration des KPIs
KPI_CONFIG = {
    "primary_kpis": [
        {
            "name": "Sessions totales",
            "icon": "📅",
            "field": "total_sessions",
            "format": "number",
            "help": "Nombre total de sessions d'entraînement"
        },
        {
            "name": "Exercices pratiqués",
            "icon": "🏋️‍♂️",
            "field": "total_exercises",
            "format": "number",
            "help": "Nombre d'exercices différents pratiqués"
        },
        {
            "name": "Volume total",
            "icon": "💪",
            "field": "total_volume",
            "format": "weight",
            "help": "Volume total d'entraînement (poids × répétitions)"
        },
        {
            "name": "Dernière session",
            "icon": "🕒",
            "field": "latest_session_date",
            "format": "date_ago",
            "help": "Date de la dernière session d'entraînement"
        }
    ],
    "secondary_kpis": [
        {
            "name": "Charge moyenne",
            "icon": "⚖️",
            "field": "average_weight",
            "format": "weight",
            "delta_field": "weight_trend",
            "help": "Charge moyenne par série"
        },
        {
            "name": "Fréquence/semaine",
            "icon": "📈",
            "field": "weekly_frequency",
            "format": "decimal",
            "delta_field": "frequency_trend",
            "help": "Nombre moyen de sessions par semaine"
        },
        {
            "name": "Score de régularité",
            "icon": "🎯",
            "field": "consistency_score",
            "format": "percentage",
            "help": "Régularité d'entraînement sur la période"
        },
        {
            "name": "Sets totaux",
            "icon": "📊",
            "field": "total_sets",
            "format": "number",
            "help": "Nombre total de séries effectuées"
        }
    ]
}

# Configuration des graphiques
CHART_CONFIG = {
    "color_schemes": {
        "volume": "viridis",
        "progression": ["#2ecc71", "#e74c3c", "#95a5a6"],
        "muscle_balance": ["#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c"]
    },
    "default_height": 500,
    "hover_template": {
        "volume": "<b>%{y}</b><br>Volume: %{x:.0f} kg<extra></extra>",
        "progression": "<b>%{hovertext}</b><br>Sessions: %{x}<br>Tendance: %{y:.3f}<br><extra></extra>"
    }
}

# Messages et textes
MESSAGES = {
    "loading": {
        "data": "🔄 Chargement des données...",
        "volume": "📈 Chargement de l'analyse de volume...",
        "progression": "🚀 Chargement de l'analyse de progression...",
        "muscle": "💪 Chargement de l'analyse musculaire...",
        "calendar": "📅 Chargement du calendrier..."
    },
    "errors": {
        "api_connection": "🚨 Impossible de se connecter à l'API",
        "no_data": "Aucune donnée disponible pour la période sélectionnée",
        "api_help": "Vérifiez que l'API FastAPI est démarrée avec `docker compose up` ou `uvicorn src.api.main:app --reload`"
    },
    "warnings": {
        "plateau_detected": "⚠️ Plateaux détectés",
        "imbalance_detected": "⚠️ Déséquilibres musculaires détectés"
    },
    "success": {
        "good_progress": "✅ Bonne progression détectée",
        "balanced_training": "✅ Équilibre musculaire optimal !"
    }
}

# Configuration des recommandations
RECOMMENDATIONS_CONFIG = {
    "plateau_threshold": 0.001,  # Seuil pour détecter un plateau
    "imbalance_threshold": 0.3,  # 30% d'écart pour détecter un déséquilibre
    "progress_threshold": 0.05,  # 5% de progression pour considérer comme "bonne"
    "consistency_threshold": 0.8  # 80% pour considérer comme régulier
}

# Configuration de l'export
EXPORT_CONFIG = {
    "formats": ["PDF", "Excel", "CSV"],
    "pdf": {
        "title": "Rapport Muscle-Analytics",
        "author": "Dashboard Muscle-Analytics",
        "margins": {"top": 20, "bottom": 20, "left": 20, "right": 20}
    },
    "excel": {
        "sheet_names": ["KPIs", "Volume", "Progression", "Muscle_Analysis"],
        "chart_size": (800, 400)
    }
}

def get_muscle_color(muscle_group: str) -> str:
    """Get the color code associated with a muscle group.

    Args:
        muscle_group: Name of the muscle group

    Returns:
        str: Hex color code (#RRGGBB). Returns '#95a5a6' if muscle group not found.
    """
    return MUSCLE_GROUPS.get(muscle_group, {}).get("color", "#95a5a6")

def get_exercises_for_muscle(muscle_group: str) -> List[str]:
    """Retourne la liste des exercices pour un groupe musculaire"""
    return MUSCLE_GROUPS.get(muscle_group, {}).get("exercises", [])

def format_value(value, format_type: str) -> str:
    """Formate une valeur selon le type spécifié
    Args:
        value: La valeur à formater
        format_type: Le type de format ('number', 'weight', 'percentage', 'decimal', 'date_ago', ...)
    Returns:
        str: La valeur formatée ou 'N/A' en cas d'erreur ou de type non supporté
    """
    if value is None:
        return "N/A"
    try:
        if format_type == "number":
            return f"{float(value):,.0f}"
        elif format_type == "weight":
            value = float(value)
            if value > 1000:
                return f"{value/1000:.1f}k kg"
            return f"{value:.0f} kg"
        elif format_type == "percentage":
            return f"{float(value):.0%}"
        elif format_type == "decimal":
            return f"{float(value):.1f}"
        elif format_type == "date_ago":
            # Cette logique sera implémentée dans le dashboard
            return str(value)
        else:
            return str(value)
    except (ValueError, TypeError):
        return "N/A"
