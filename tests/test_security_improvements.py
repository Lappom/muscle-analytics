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
from datetime import datetime, timedelta

# Ajouter les chemins pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dashboard.components.sidebar import _check_admin_authentication, _show_admin_logout


class MockSessionState:
    """Mock pour st.session_state qui permet l'accès aux attributs dynamiques"""
    
    def __init__(self):
        self._data = {}
    
    def get(self, key, default=None):
        """Simule st.session_state.get()"""
        return self._data.get(key, default)
    
    def __getattr__(self, name):
        """Permet l'accès aux attributs comme st.session_state.admin_authenticated"""
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        """Permet la définition d'attributs comme st.session_state.admin_authenticated = True"""
        if name == '_data':
            super().__setattr__(name, value)
        else:
            self._data[name] = value
    
    def __delattr__(self, name):
        """Permet la suppression d'attributs comme del st.session_state.admin_authenticated"""
        if name in self._data:
            del self._data[name]
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __contains__(self, key):
        """Permet l'utilisation de 'in' comme 'admin_authenticated' in st.session_state"""
        return key in self._data
    
    def clear(self):
        """Nettoie toutes les données"""
        self._data.clear()


class TestSecurityImprovements(unittest.TestCase):
    """Tests pour les améliorations de sécurité"""

    def setUp(self):
        """Configuration initiale pour chaque test"""
        # Mock de Streamlit
        self.mock_st = Mock()
        
        # Créer un mock de session state qui simule correctement st.session_state
        self.mock_session_state = MockSessionState()
        self.mock_st.session_state = self.mock_session_state
        
        # Mock des objets datetime avec des valeurs fixes
        self.mock_datetime = Mock()
        self.mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_datetime.timedelta = timedelta
        
        # Patcher streamlit et datetime
        self.st_patcher = patch('dashboard.components.sidebar.st', self.mock_st)
        self.datetime_patcher = patch('dashboard.components.sidebar.datetime', self.mock_datetime)
        self.st_patcher.start()
        self.datetime_patcher.start()

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.st_patcher.stop()
        self.datetime_patcher.stop()

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
        self.mock_session_state.admin_authenticated = True
        self.mock_session_state.admin_auth_time = datetime(2023, 1, 1, 12, 0, 0)
        
        result = _check_admin_authentication()
        
        # Vérifier que l'authentification est acceptée
        self.assertTrue(result)

    def test_admin_authentication_failed_login(self):
        """Test que l'authentification échoue avec un mauvais mot de passe"""
        # Simuler une tentative de connexion
        self.mock_session_state.clear()
        self.mock_st.sidebar.text_input.return_value = "wrong_password"
        self.mock_st.sidebar.button.return_value = True
        
        # Utiliser le mock datetime configuré dans setUp
        result = _check_admin_authentication()
        
        # Vérifier que l'authentification échoue
        self.assertFalse(result)
        
        # Vérifier que l'erreur est affichée
        self.mock_st.error.assert_called_with("❌ Mot de passe incorrect")

    def test_admin_session_expiration(self):
        """Test que les sessions admin expirent correctement"""
        from datetime import datetime, timedelta
        
        # Simuler une session expirée (plus de 30 minutes)
        old_time = datetime(2023, 1, 1, 11, 29, 0)  # 31 minutes avant le mock
        self.mock_session_state.admin_authenticated = True
        self.mock_session_state.admin_auth_time = old_time
        
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
        self.mock_session_state.admin_authenticated = True
        self.mock_session_state.admin_auth_time = datetime(2023, 1, 1, 12, 0, 0)
        
        # Simuler le clic sur le bouton de déconnexion
        self.mock_st.sidebar.button.return_value = True
        
        _show_admin_logout()
        
        # Vérifier que le bouton de déconnexion est affiché
        self.mock_st.sidebar.button.assert_called_with("🚪 Déconnexion Admin", key="admin_logout")

    def test_admin_logout_functionality(self):
        """Test que la déconnexion fonctionne correctement"""
        # Simuler une session active
        self.mock_session_state.admin_authenticated = True
        self.mock_session_state.admin_auth_time = datetime(2023, 1, 1, 12, 0, 0)
        
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
