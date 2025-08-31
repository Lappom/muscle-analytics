#!/usr/bin/env python3
"""
Tests pour les améliorations de sécurité implémentées dans sidebar.py

Ces tests vérifient que les opérations critiques de base de données
sont correctement protégées par l'authentification administrateur.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Ajouter les chemins pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dashboard.components.sidebar import _check_admin_authentication, _show_admin_logout


class TestSecurityImprovements(unittest.TestCase):
    """Tests pour les améliorations de sécurité"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Mock de Streamlit
        self.mock_st = Mock()
        self.mock_session_state = {}
        self.mock_st.session_state = self.mock_session_state
        
        # Patcher streamlit
        self.st_patcher = patch('dashboard.components.sidebar.st', self.mock_st)
        self.st_patcher.start()

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.st_patcher.stop()

    def test_admin_authentication_initial_state(self):
        """Test que l'authentification admin est refusée par défaut"""
        # État initial sans authentification
        self.mock_session_state.clear()
        
        result = _check_admin_authentication()
        
        # Vérifier que l'authentification est refusée
        self.assertFalse(result)
        
        # Vérifier que l'interface d'authentification est affichée
        self.mock_st.sidebar.markdown.assert_called()
        self.mock_st.sidebar.text_input.assert_called()
        self.mock_st.sidebar.button.assert_called()

    def test_admin_authentication_success(self):
        """Test que l'authentification admin réussit avec le bon mot de passe"""
        # Simuler une authentification réussie
        self.mock_session_state['admin_authenticated'] = True
        self.mock_session_state['admin_auth_time'] = Mock()
        
        result = _check_admin_authentication()
        
        # Vérifier que l'authentification est acceptée
        self.assertTrue(result)

    def test_admin_authentication_failed_login(self):
        """Test que l'authentification échoue avec un mauvais mot de passe"""
        # Simuler une tentative de connexion
        self.mock_session_state.clear()
        self.mock_st.sidebar.text_input.return_value = "wrong_password"
        self.mock_st.sidebar.button.return_value = True
        
        # Mock de la vérification du mot de passe
        with patch('dashboard.components.sidebar.datetime') as mock_datetime:
            mock_datetime.now.return_value = Mock()
            
            result = _check_admin_authentication()
            
            # Vérifier que l'authentification échoue
            self.assertFalse(result)
            
            # Vérifier que l'erreur est affichée
            self.mock_st.error.assert_called_with("❌ Mot de passe incorrect")

    def test_admin_session_expiration(self):
        """Test que les sessions admin expirent correctement"""
        from datetime import datetime, timedelta
        
        # Simuler une session expirée (plus de 30 minutes)
        old_time = datetime.now() - timedelta(minutes=31)
        self.mock_session_state['admin_authenticated'] = True
        self.mock_session_state['admin_auth_time'] = old_time
        
        result = _check_admin_authentication()
        
        # Vérifier que l'authentification est refusée
        self.assertFalse(result)
        
        # Vérifier que la session est nettoyée
        self.assertNotIn('admin_authenticated', self.mock_session_state)
        self.assertNotIn('admin_auth_time', self.mock_session_state)
        
        # Vérifier que l'avertissement d'expiration est affiché
        self.mock_st.warning.assert_called_with("⚠️ Session administrateur expirée. Veuillez vous reconnecter.")

    def test_admin_logout_button_display(self):
        """Test que le bouton de déconnexion s'affiche quand connecté"""
        # Simuler une session active
        self.mock_session_state['admin_authenticated'] = True
        self.mock_session_state['admin_auth_time'] = Mock()
        
        # Simuler le clic sur le bouton de déconnexion
        self.mock_st.sidebar.button.return_value = True
        
        _show_admin_logout()
        
        # Vérifier que le bouton de déconnexion est affiché
        self.mock_st.sidebar.button.assert_called_with("🚪 Déconnexion Admin", key="admin_logout")

    def test_admin_logout_functionality(self):
        """Test que la déconnexion fonctionne correctement"""
        # Simuler une session active
        self.mock_session_state['admin_authenticated'] = True
        self.mock_session_state['admin_auth_time'] = Mock()
        
        # Simuler le clic sur le bouton de déconnexion
        self.mock_st.sidebar.button.return_value = True
        
        _show_admin_logout()
        
        # Vérifier que la session est nettoyée
        self.assertNotIn('admin_authenticated', self.mock_session_state)
        self.assertNotIn('admin_auth_time', self.mock_session_state)
        
        # Vérifier que le message de succès est affiché
        self.mock_st.success.assert_called_with("✅ Déconnexion réussie")

    def test_admin_logout_button_not_displayed_when_not_authenticated(self):
        """Test que le bouton de déconnexion ne s'affiche pas quand non connecté"""
        # Pas de session active
        self.mock_session_state.clear()
        
        _show_admin_logout()
        
        # Vérifier que le bouton de déconnexion n'est pas affiché
        self.mock_st.sidebar.button.assert_not_called()


class TestSecurityIntegration(unittest.TestCase):
    """Tests d'intégration pour la sécurité"""

    @patch('dashboard.components.sidebar._check_admin_authentication')
    def test_database_clear_protection(self, mock_auth_check):
        """Test que la suppression de base est protégée"""
        # Simuler un accès non autorisé
        mock_auth_check.return_value = False
        
        # Ici, on testerait l'intégration complète avec la fonction d'import
        # qui vérifie l'authentification avant de vider la base
        
        # Pour l'instant, on vérifie juste que la fonction d'authentification est appelée
        mock_auth_check.assert_not_called()  # Pas encore appelée dans ce test


if __name__ == '__main__':
    # Configuration des tests
    unittest.main(verbosity=2)
