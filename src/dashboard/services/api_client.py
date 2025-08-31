"""
Client API pour communiquer avec le backend FastAPI
"""
import logging
import requests
import streamlit as st
from typing import Dict, List, Optional
import time

from ..config import API_BASE_URL, API_TIMEOUT

logger = logging.getLogger(__name__)

class APIClient:
    """Client pour communiquer avec l'API FastAPI"""
    
    def __init__(self, base_url: str = API_BASE_URL, timeout: int = API_TIMEOUT):
        self.base_url = base_url
        self.timeout = timeout
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, retries: int = 2) -> Dict:
        """Effectue une requête HTTP vers l'API avec retry"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(retries + 1):
            start_time = time.time()
            try:
                logger.info(f"Tentative {attempt + 1}/{retries + 1} pour {endpoint}")
                
                response = requests.get(url, params=params or {}, timeout=self.timeout)
                response.raise_for_status()
                
                elapsed = time.time() - start_time
                logger.info(f"Requête {endpoint} réussie en {elapsed:.2f}s")
                
                return response.json()
                
            except requests.exceptions.Timeout as e:
                elapsed = time.time() - start_time
                logger.warning(f"Timeout sur {endpoint} après {elapsed:.2f}s (tentative {attempt + 1})")
                if attempt == retries:
                    logger.error(f"Toutes les tentatives ont échoué pour {endpoint}: Timeout")
                    st.error(f"⏰ Timeout sur {endpoint} - L'API prend trop de temps à répondre")
                    return {}
                time.sleep(1)  # Attendre avant retry
                
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Erreur de connexion vers {endpoint}: {e}")
                if attempt == retries:
                    st.error(f"🔌 Impossible de se connecter à l'API - Vérifiez que l'API est démarrée")
                    return {}
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Erreur lors de la requête vers {endpoint}: {e}")
                if attempt == retries:
                    st.error(f"❌ Erreur API sur {endpoint}: {e}")
                    return {}
                time.sleep(1)
        
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
        return self._make_request("/analytics/dashboard")
    
    def get_exercises(self) -> List[str]:
        """Récupère la liste des exercices pratiqués"""
        data = self._make_request("/exercises/practiced")
        return data if isinstance(data, list) else []
    
    def get_exercise_analytics(self, exercise: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """Récupère les analytics pour un exercice spécifique"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        return self._make_request(f"/analytics/exercise/{exercise}", params)
    
    def get_volume_analytics(self, exercise: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Récupère les analytics de volume"""
        params = {}
        if exercise:
            params['exercise'] = exercise
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        data = self._make_request("/analytics/volume", params)
        return data if isinstance(data, list) else []
    
    def get_progression_analytics(self, exercise: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Récupère les analytics de progression"""
        params = {}
        if exercise:
            params['exercise'] = exercise
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        data = self._make_request("/analytics/progression", params)
        return data if isinstance(data, list) else []
    
    def get_sessions(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        """Récupère les sessions d'entraînement"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        data = self._make_request("/sessions", params)
        return data if isinstance(data, list) else []
    
    def get_exercise_by_muscle(self) -> Dict:
        """Récupère le mapping exercices/muscles"""
        # Endpoint pas encore implémenté, retourner un dict vide
        return {}


@st.cache_resource
def get_api_client():
    """Retourne une instance singleton du client API"""
    return APIClient()
