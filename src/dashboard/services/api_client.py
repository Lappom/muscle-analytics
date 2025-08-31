"""
FastAPI client handling backend communication for dashboard analytics.

Provides methods to fetch training data, exercise analytics, and session information
while handling retries and error reporting
"""
import logging
import requests
import streamlit as st
from typing import Dict, List, Optional
import time
from urllib.parse import urljoin
from ..config import API_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)

class APIClient:
    def _build_date_params(self, exercise: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Construit le dictionnaire de paramètres pour les requêtes avec exercise, start_date et end_date"""
        params = {}
        if exercise:
            params['exercise'] = exercise
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return params
    """Client pour communiquer avec l'API FastAPI"""
    
    RETRY_DELAY_SECONDS = 1  # Temps d'attente entre les tentatives de retry

    def __init__(self, base_url: str = API_BASE_URL, timeout: int = API_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None, params: Optional[Dict] = None, retries: int = 2) -> Dict:
        """Effectue une requête HTTP vers l'API avec support des méthodes et retry"""
        url = urljoin(self.base_url, endpoint.lstrip('/'))
        for attempt in range(retries + 1):
            start_time = time.time()
            try:
                logger.info(f"Tentative {attempt + 1}/{retries + 1} pour {endpoint} [{method}]")
                response = requests.request(
                    method=method,
                    url=url,
                    params=params or {},
                    json=data,
                    timeout=self.timeout
                )
                response.raise_for_status()
                elapsed = time.time() - start_time
                logger.info(f"Requête {endpoint} [{method}] réussie en {elapsed:.2f}s")
                return response.json()
            except requests.exceptions.Timeout as e:
                elapsed = time.time() - start_time
                logger.warning(f"Timeout sur {endpoint} [{method}] après {elapsed:.2f}s (tentative {attempt + 1})")
                if attempt == retries:
                    logger.error(f"Toutes les tentatives ont échoué pour {endpoint} [{method}]: Timeout")
                    st.error(f"⏰ Timeout sur {endpoint} [{method}] - L'API prend trop de temps à répondre")
                    return {}
                time.sleep(self.RETRY_DELAY_SECONDS)
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Erreur de connexion vers {endpoint} [{method}]: {e}")
                if attempt == retries:
                    st.error(f"🔌 Impossible de se connecter à l'API [{method}] - Vérifiez que l'API est démarrée")
                    return {}
                time.sleep(self.RETRY_DELAY_SECONDS)
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la requête vers {endpoint} [{method}]: {e}")
                if attempt == retries:
                    st.error(f"❌ Erreur API sur {endpoint} [{method}]: {e}")
                    return {}
                time.sleep(self.RETRY_DELAY_SECONDS)
        # Fallback si on arrive ici (ne devrait pas arriver)
        return {}
    
    def check_health(self) -> bool:
        """Vérifie la santé de l'API"""
        try:
            response = self._make_request("/health")
            return response.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Erreur lors du check health: {e}")
            return False
    
    def get_dashboard_data(self) -> Dict:
        """Récupère les données du dashboard principal"""
        return self._make_request("/analytics/dashboard", method="GET")
    
    def get_exercises(self) -> List[str]:
        """Récupère la liste des exercices pratiqués"""
        data = self._make_request("/exercises/practiced", method="GET")
        return data if isinstance(data, list) else []
    
    def get_exercise_analytics(self, exercise: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Récupère les analytics pour un exercice spécifique"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self._make_request(f"/analytics/exercise/{exercise}", method="GET", params=params)
    
    def get_volume_analytics(self, exercise: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Récupère les analytics de volume"""
        params = self._build_date_params(exercise, start_date, end_date)
        data = self._make_request("/analytics/volume", method="GET", params=params)
        return data if isinstance(data, list) else []
    
    def get_progression_analytics(self, exercise: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Récupère les analytics de progression"""
        params = self._build_date_params(exercise, start_date, end_date)
        data = self._make_request("/analytics/progression", method="GET", params=params)
        return data if isinstance(data, list) else []
    
    def get_sessions(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Récupère les sessions d'entraînement"""
        params = self._build_date_params(None, start_date, end_date)
        data = self._make_request("/sessions", method="GET", params=params)
        return data if isinstance(data, list) else []
    
    def get_exercise_by_muscle(self) -> Dict:
        """Récupère le mapping exercices/muscles"""
        data = self._make_request("/exercises/muscle-mapping", method="GET")
        return data if isinstance(data, dict) else {}


@st.cache_resource
def get_api_client():
    """Retourne une instance singleton du client API"""
    return APIClient()
