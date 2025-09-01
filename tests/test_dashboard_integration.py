"""
Tests d'intégration pour les nouvelles fonctionnalités du dashboard
- Graphiques de tendance de progression
- Alertes automatiques de plateau
- Utilisation de create_progress_trend_chart
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
from unittest.mock import Mock, patch

from src.dashboard.utils import create_progress_trend_chart
from src.dashboard.components.charts import _display_progress_trend_scatter_chart
from src.dashboard.components.kpis import _display_alerts_and_recommendations


class TestProgressTrendChart:
    """Tests pour le graphique de tendance de progression"""
    
    def test_create_progress_trend_chart_with_valid_data(self):
        """Test de création du graphique avec des données valides"""
        # Données de test
        data = pd.DataFrame({
            'exercise': ['Squat', 'Bench Press', 'Deadlift'],
            'total_sessions': [10, 8, 12],
            'trend_slope': [0.5, -0.2, 0.8]
        })
        
        # Créer le graphique
        fig = create_progress_trend_chart(data)
        
        # Vérifications
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0  # Au moins une trace
        
        # Vérifier que toutes les données sont bien présentes dans les traces
        total_points = 0
        for trace in fig.data:
            if hasattr(trace, 'x') and hasattr(trace, 'y'):
                total_points += len(trace.x)
        
        assert total_points == 3  # 3 exercices au total
    
    def test_create_progress_trend_chart_with_empty_data(self):
        """Test de création du graphique avec des données vides"""
        # DataFrame vide
        data = pd.DataFrame()
        
        # Créer le graphique
        fig = create_progress_trend_chart(data)
        
        # Vérifier qu'une annotation est affichée
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) > 0
    
    def test_create_progress_trend_chart_with_missing_columns(self):
        """Test de création du graphique avec des colonnes manquantes"""
        # Données avec colonnes manquantes
        data = pd.DataFrame({
            'exercise': ['Squat'],
            'total_sessions': [10]
            # Pas de colonne trend_slope
        })
        
        # Créer le graphique
        fig = create_progress_trend_chart(data)
        
        # Vérifier qu'une annotation est affichée
        assert isinstance(fig, go.Figure)
        assert len(fig.layout.annotations) > 0


class TestProgressTrendScatterChart:
    """Tests pour l'affichage du graphique scatter de tendance"""
    
    @patch('streamlit.plotly_chart')
    @patch('streamlit.info')
    def test_display_progress_trend_scatter_chart_with_valid_data(self, mock_info, mock_plotly):
        """Test d'affichage avec des données valides"""
        # Données de test
        df_progression = pd.DataFrame({
            'exercise': ['Squat', 'Bench Press'],
            'total_sessions': [10, 8],
            'trend_slope': [0.5, -0.2]
        })
        
        filters = {'theme': 'Clair', 'show_animations': True}
        
        # Appeler la fonction
        _display_progress_trend_scatter_chart(df_progression, filters)
        
        # Vérifier que plotly_chart a été appelé
        mock_plotly.assert_called()
    
    @patch('streamlit.info')
    def test_display_progress_trend_scatter_chart_with_missing_columns(self, mock_info):
        """Test d'affichage avec des colonnes manquantes"""
        # Données avec colonnes manquantes
        df_progression = pd.DataFrame({
            'exercise': ['Squat'],
            'total_sessions': [10]
            # Pas de colonne trend_slope
        })
        
        filters = {'theme': 'Clair'}
        
        # Appeler la fonction
        _display_progress_trend_scatter_chart(df_progression, filters)
        
        # Vérifier qu'un message d'info est affiché
        mock_info.assert_called_with("Calcul des tendances de progression en cours...")


class TestPlateauAlerts:
    """Tests pour les alertes de plateau"""
    
    @patch('streamlit.error')
    @patch('streamlit.warning')
    @patch('streamlit.info')
    @patch('streamlit.success')
    @patch('streamlit.metric')
    def test_display_alerts_with_plateaus(self, mock_metric, mock_success, mock_info, mock_warning, mock_error):
        """Test d'affichage des alertes avec des plateaux détectés"""
        # Données de test avec plateaux
        dashboard_data = {
            'exercises_with_plateau': ['Squat', 'Bench Press'],
            'total_exercises': 5,
            'weekly_frequency': 3,
            'consistency_score': 0.8
        }
        
        # Appeler la fonction
        _display_alerts_and_recommendations(dashboard_data)
        
        # Vérifier que les alertes sont affichées
        mock_error.assert_called()  # Alerte principale
        mock_info.assert_called()   # Recommandations modérées
    
    @patch('streamlit.error')
    @patch('streamlit.warning')
    @patch('streamlit.info')
    @patch('streamlit.success')
    def test_display_alerts_without_plateaus(self, mock_success, mock_info, mock_warning, mock_error):
        """Test d'affichage des alertes sans plateau"""
        # Données de test sans plateau
        dashboard_data = {
            'exercises_with_plateau': [],
            'total_exercises': 5,
            'weekly_frequency': 4,
            'consistency_score': 0.9
        }
        
        # Appeler la fonction
        _display_alerts_and_recommendations(dashboard_data)
        
        # Vérifier qu'aucun message de succès n'est affiché (pas de plateau = pas d'affichage)
        mock_success.assert_not_called()
        # Vérifier qu'aucune alerte d'erreur n'est affichée
        mock_error.assert_not_called()
        # Vérifier qu'aucun warning n'est affiché (fréquence et consistency OK)
        mock_warning.assert_not_called()
        # Vérifier qu'aucune info n'est affichée
        mock_info.assert_not_called()
    
    @patch('streamlit.warning')
    def test_display_alerts_low_frequency(self, mock_warning):
        """Test d'alerte sur la fréquence d'entraînement faible"""
        # Données de test avec fréquence faible
        dashboard_data = {
            'exercises_with_plateau': [],
            'weekly_frequency': 1,  # Fréquence faible
            'consistency_score': 0.7
        }
        
        # Appeler la fonction
        _display_alerts_and_recommendations(dashboard_data)
        
        # Vérifier que l'alerte de fréquence est affichée
        mock_warning.assert_called()


class TestDashboardIntegration:
    """Tests d'intégration complète du dashboard"""
    
    def test_progress_trend_chart_integration(self):
        """Test d'intégration complète du graphique de tendance"""
        # Créer des données de test complètes
        test_data = pd.DataFrame({
            'exercise': ['Squat', 'Bench Press', 'Deadlift', 'Overhead Press'],
            'total_sessions': [15, 12, 18, 10],
            'trend_slope': [0.8, -0.1, 1.2, 0.3]
        })
        
        # Créer le graphique
        fig = create_progress_trend_chart(test_data)
        
        # Vérifications de base
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == "Tendances de progression par exercice"
        
        # Vérifier que les couleurs sont appliquées correctement
        scatter_data = fig.data[0]
        assert 'marker' in scatter_data
        assert 'color' in scatter_data.marker
    
    def test_plateau_detection_integration(self):
        """Test d'intégration de la détection de plateaux"""
        # Simuler des données de progression avec plateaux
        progression_data = pd.DataFrame({
            'exercise': ['Squat', 'Bench Press', 'Deadlift'],
            'total_sessions': [20, 15, 25],
            'progression_trend': ['stable', 'negative', 'positive'],
            'plateau_detected': [True, False, False],
            'days_since_last_pr': [45, 10, 5]
        })
        
        # Vérifier que les données sont bien structurées
        assert 'plateau_detected' in progression_data.columns
        assert 'days_since_last_pr' in progression_data.columns
        
        # Vérifier la détection des plateaux
        plateaus = progression_data[progression_data['plateau_detected'] == True]
        assert len(plateaus) == 1
        assert plateaus.iloc[0]['exercise'] == 'Squat'


if __name__ == "__main__":
    pytest.main([__file__])
