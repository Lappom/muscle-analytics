"""
Module unifié de gestion de base de données pour Muscle-Analytics.

Ce module combine :
1. Configuration multi-environnements (DatabaseConfig)  
2. Gestionnaire de base de données (DatabaseManager)
3. Utilitaires de connexion

Usage simple :
    from src.database import get_database, DatabaseEnvironment
    
    # Automatique selon l'environnement
    db = get_database()
    
    # Spécifique
    test_db = get_database(DatabaseEnvironment.TEST)
"""

import psycopg2
import pandas as pd
import os
from typing import Optional, List, Dict, Tuple, Any
from enum import Enum
from pathlib import Path
import logging
from datetime import datetime, date
from contextlib import contextmanager

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

class DatabaseEnvironment(Enum):
    """Types d'environnements de base de données"""
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"
    DOCKER = "docker"


class DatabaseConfig:
    """Gestionnaire de configuration de base de données"""
    
    def __init__(self):
        self.project_root = self._find_project_root()
        self.env_file = self.project_root / '.env'
        self.load_env_file()
    
    def _find_project_root(self) -> Path:
        """Trouve la racine du projet (où se trouve .env)"""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / '.env').exists() or (current / 'pyproject.toml').exists():
                return current
            current = current.parent
        return Path(__file__).parent.parent  # Fallback
    
    def load_env_file(self):
        """Charge le fichier .env s'il existe"""
        if self.env_file.exists():
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key, value)
    
    def get_config(self, environment: DatabaseEnvironment) -> Dict[str, Any]:
        """Récupère la configuration pour un environnement spécifique"""
        if environment == DatabaseEnvironment.DEVELOPMENT:
            return self._get_dev_config()
        elif environment == DatabaseEnvironment.TEST:
            return self._get_test_config()
        elif environment == DatabaseEnvironment.PRODUCTION:
            return self._get_prod_config()
        elif environment == DatabaseEnvironment.DOCKER:
            return self._get_docker_config()
        else:
            raise ValueError(f"Environnement non supporté: {environment}")
    
    def _get_dev_config(self) -> Dict[str, Any]:
        """Configuration pour le développement local"""
        return {
            'host': os.getenv('DEV_DB_HOST', 'localhost'),
            'port': int(os.getenv('DEV_DB_PORT', '5432')),
            'database': os.getenv('DEV_DB_NAME', 'muscle_analytics_dev'),
            'user': os.getenv('DEV_DB_USER', 'dev_user'),
            'password': os.getenv('DEV_DB_PASSWORD', 'dev_password_change_me')
        }
    
    def _get_test_config(self) -> Dict[str, Any]:
        """Configuration pour les tests"""
        return {
            'host': os.getenv('TEST_DB_HOST', 'localhost'),
            'port': int(os.getenv('TEST_DB_PORT', '5432')),  # Port CI identique
            'database': os.getenv('TEST_DB_NAME', 'muscle_analytics_test'),
            'user': os.getenv('TEST_DB_USER', 'postgres'),
            'password': os.getenv('TEST_DB_PASSWORD', 'password')
        }
    
    def _get_prod_config(self) -> Dict[str, Any]:
        """Configuration pour la production"""
        required_vars = ['PROD_DB_HOST', 'PROD_DB_NAME', 'PROD_DB_USER', 'PROD_DB_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Variables de production manquantes: {missing_vars}")
        
        return {
            'host': os.getenv('PROD_DB_HOST'),
            'port': int(os.getenv('PROD_DB_PORT', '5432')),
            'database': os.getenv('PROD_DB_NAME'),
            'user': os.getenv('PROD_DB_USER'),
            'password': os.getenv('PROD_DB_PASSWORD')
        }
    
    def _get_docker_config(self) -> Dict[str, Any]:
        """Configuration pour Docker"""
        return {
            'host': os.getenv('DB_HOST', 'postgres'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database': os.getenv('DB_NAME', 'muscle_analytics'),
            'user': os.getenv('DB_USER', 'dev'),
            'password': os.getenv('DB_PASSWORD', 'devpass')
        }
    
    def get_current_environment(self) -> DatabaseEnvironment:
        """Détermine l'environnement actuel"""
        env = os.getenv('APP_ENV', '').lower()
        
        if env == 'production':
            return DatabaseEnvironment.PRODUCTION
        elif env == 'test':
            return DatabaseEnvironment.TEST
        elif env == 'docker':
            return DatabaseEnvironment.DOCKER
        else:
            return DatabaseEnvironment.DEVELOPMENT


# =============================================================================
# GESTIONNAIRE DE BASE DE DONNÉES
# =============================================================================

class DatabaseError(Exception):
    """Exception spécifique aux opérations de base de données"""
    pass


class DatabaseManager:
    """Gestionnaire de base de données pour Muscle-Analytics"""
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 5432,
                 database: str = "muscle_analytics",
                 user: str = "postgres", 
                 password: str = "password"):
        """
        Initialise le gestionnaire de base de données.
        
        Args:
            host: Hôte PostgreSQL
            port: Port PostgreSQL
            database: Nom de la base de données
            user: Utilisateur
            password: Mot de passe
        """
        # Validation stricte de l'utilisateur pour éviter l'erreur 'role root does not exist'
        if not user or user.strip() == '':
            raise ValueError("L'utilisateur de base de données ne peut pas être vide")
        
        if user == 'root':
            logger.warning("⚠️  Utilisateur 'root' détecté - risque d'erreur 'role root does not exist'")
            logger.warning("   Assurez-vous que l'utilisateur 'root' existe dans PostgreSQL ou utilisez un autre utilisateur")
        
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        
        logger.info(f"DatabaseManager configuré pour {user}@{host}:{port}/{database}")
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'DatabaseManager':
        """Crée un DatabaseManager à partir d'une configuration"""
        return cls(**config)
    
    @classmethod
    def from_environment(cls, environment: DatabaseEnvironment) -> 'DatabaseManager':
        """Crée un DatabaseManager pour un environnement spécifique"""
        config_manager = DatabaseConfig()
        config = config_manager.get_config(environment)
        return cls.from_config(config)
    
    def test_connection(self) -> bool:
        """
        Teste la connexion à la base de données.
        
        Returns:
            True si la connexion réussit, False sinon
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Échec de la connexion à la base de données: {e}")
            return False
    
    @contextmanager
    def get_connection(self):
        """
        Context manager pour obtenir une connexion à la base de données.
        
        Yields:
            Connexion psycopg2
            
        Raises:
            DatabaseError: Si la connexion échoue
        """
        conn = None
        try:
            # Validation des paramètres avant connexion
            required_params = ['host', 'port', 'database', 'user', 'password']
            missing_params = [param for param in required_params if not self.connection_params.get(param)]
            
            if missing_params:
                raise DatabaseError(f"Paramètres de connexion manquants: {missing_params}")
            
            # Log des paramètres de connexion (sans mot de passe)
            safe_params = self.connection_params.copy()
            safe_params['password'] = '*' * len(safe_params['password'])
            logger.debug(f"Tentative de connexion avec: {safe_params}")
            
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            error_msg = f"Erreur de base de données: {e}"
            logger.error(error_msg)
            logger.error(f"Paramètres utilisés: host={self.connection_params.get('host')}, "
                        f"port={self.connection_params.get('port')}, "
                        f"database={self.connection_params.get('database')}, "
                        f"user={self.connection_params.get('user')}")
            raise DatabaseError(error_msg)
        except Exception as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Erreur inattendue: {e}")
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
        """
        Exécute une requête SELECT et retourne les résultats.
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
            
        Returns:
            Liste des résultats
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> int:
        """
        Exécute une requête UPDATE/INSERT/DELETE.
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
            
        Returns:
            Nombre de lignes affectées
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount
    
    # =============================================================================
    # MÉTHODES POUR L'ETL
    # =============================================================================
    
    def insert_session(self, date: date, start_time: Optional[str] = None, 
                      training_name: Optional[str] = None, notes: Optional[str] = None) -> int:
        """
        Insère une nouvelle session d'entraînement.
        
        Args:
            date: Date de la session
            start_time: Heure de début (format HH:MM)
            training_name: Nom de l'entraînement
            notes: Notes de session
            
        Returns:
            ID de la session créée
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Vérifier si la session existe déjà
                    cursor.execute("""
                        SELECT id FROM sessions 
                        WHERE date = %s AND start_time = %s AND training_name = %s
                    """, (date, start_time, training_name))
                    
                    existing = cursor.fetchone()
                    if existing:
                        logger.info(f"Session existante trouvée: ID {existing[0]}")
                        return existing[0]
                    
                    # Insérer nouvelle session
                    cursor.execute("""
                        INSERT INTO sessions (date, start_time, training_name, notes)
                        VALUES (%s, %s, %s, %s) RETURNING id
                    """, (date, start_time, training_name, notes))
                    
                    session_id = cursor.fetchone()[0]
                    logger.info(f"Nouvelle session créée: ID {session_id}")
                    return session_id
                    
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Erreur lors de l'insertion de session: {e}")
    
    def insert_set(self, session_id: int, exercise: str, reps: Optional[int] = None,
                   weight_kg: Optional[float] = None, series_type: Optional[str] = None,
                   notes: Optional[str] = None, skipped: bool = False) -> int:
        """
        Insère une nouvelle série d'exercice.
        
        Args:
            session_id: ID de la session
            exercise: Nom de l'exercice
            reps: Nombre de répétitions
            weight_kg: Poids en kg
            series_type: Type de série ('échauffement', 'principale', 'récupération')
            notes: Notes de la série
            skipped: Si la série a été sautée
            
        Returns:
            ID de la série créée
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO sets (session_id, exercise, reps, weight_kg, 
                                        series_type, notes, skipped)
                        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                    """, (session_id, exercise, reps, weight_kg, series_type, notes, skipped))
                    
                    set_id = cursor.fetchone()[0]
                    logger.debug(f"Série insérée: ID {set_id}")
                    return set_id
                    
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Erreur lors de l'insertion de série: {e}")
    
    def _parse_muscle_list(self, muscle_value: Any) -> List[str]:
        """Parse une valeur de muscle en liste de strings."""
        if isinstance(muscle_value, str) and muscle_value is not None and muscle_value != '':
            return muscle_value.split(', ')
        return []
    
    def insert_exercise_catalog(self, name: str, main_region: str,
                               muscles_primary: List[str], muscles_secondary: List[str]) -> bool:
        """
        Insère ou met à jour un exercice dans le catalogue.
        
        Args:
            name: Nom de l'exercice
            main_region: Région principale
            muscles_primary: Muscles primaires
            muscles_secondary: Muscles secondaires
            
        Returns:
            True si insertion réussie
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO exercises (name, main_region, muscles_primary, muscles_secondary)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (name) DO UPDATE SET
                            main_region = EXCLUDED.main_region,
                            muscles_primary = EXCLUDED.muscles_primary,
                            muscles_secondary = EXCLUDED.muscles_secondary
                    """, (name, main_region, muscles_primary, muscles_secondary))
                    
                    logger.debug(f"Exercice '{name}' ajouté/mis à jour dans le catalogue")
                    return True
                    
        except DatabaseError:
            raise
        except Exception as e:
            raise DatabaseError(f"Erreur lors de l'insertion d'exercice: {e}")
    
    def bulk_insert_from_dataframe(self, df: pd.DataFrame) -> Dict[str, int]:
        """
        Insertion en masse depuis un DataFrame normalisé.
        
        Args:
            df: DataFrame normalisé avec colonnes attendues
            
        Returns:
            Dictionnaire avec statistiques d'insertion
        """
        stats = {
            'sessions_created': 0,
            'sets_inserted': 0,
            'exercises_added': 0,
            'errors': 0
        }
        
        if df.empty:
            logger.warning("DataFrame vide, aucune insertion effectuée")
            return stats
        
        try:
            # Grouper par sessions (date + training + time)
            session_groups = df.groupby(['date', 'training', 'time'], dropna=False)
            
            for (session_date, training_name, start_time), session_data in session_groups:
                try:
                    # Convertir la date si nécessaire
                    if isinstance(session_date, str):
                        session_date = pd.to_datetime(session_date).date()
                    
                    # Insérer la session
                    session_id = self.insert_session(
                        date=session_date,
                        start_time=start_time if pd.notna(start_time) else None,
                        training_name=training_name if pd.notna(training_name) else None
                    )
                    
                    # Vérifier si c'est une nouvelle session
                    if session_id:
                        stats['sessions_created'] += 1
                    
                    # Insérer les séries de cette session
                    for _, row in session_data.iterrows():
                        try:
                            # Ajouter l'exercice au catalogue si nouvelles infos disponibles
                            if all(col in row and pd.notna(row[col]) for col in 
                                  ['exercise', 'main_region', 'muscles_primary']):
                                
                                primary_muscles = self._parse_muscle_list(row['muscles_primary'])
                                secondary_muscles = self._parse_muscle_list(row['muscles_secondary'])
                                
                                self.insert_exercise_catalog(
                                    name=row['exercise'],
                                    main_region=row['main_region'],
                                    muscles_primary=primary_muscles,
                                    muscles_secondary=secondary_muscles
                                )
                                stats['exercises_added'] += 1
                            
                            # Insérer la série
                            self.insert_set(
                                session_id=session_id,
                                exercise=row['exercise'],
                                reps=int(row['reps']) if pd.notna(row['reps']) and row['reps'] != '' else None,
                                weight_kg=float(row['weight_kg']) if pd.notna(row['weight_kg']) else None,
                                series_type=row.get('series_type'),
                                notes=row.get('notes') if pd.notna(row.get('notes')) else None,
                                skipped=bool(row.get('skipped', False))
                            )
                            stats['sets_inserted'] += 1
                            
                        except Exception as e:
                            logger.error(f"Erreur lors de l'insertion d'une série: {e}")
                            stats['errors'] += 1
                            continue
                
                except Exception as e:
                    logger.error(f"Erreur lors de l'insertion de session: {e}")
                    stats['errors'] += 1
                    continue
            
            logger.info(f"Insertion terminée: {stats}")
            return stats
            
        except Exception as e:
            raise DatabaseError(f"Erreur lors de l'insertion en masse: {e}")
    
    def get_existing_data_dates(self) -> List[date]:
        """Récupère les dates des données déjà présentes en base."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT date FROM sessions ORDER BY date")
                    return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            raise DatabaseError(f"Erreur lors de la récupération des dates: {e}")
    
    def check_data_exists(self, date: date, training_name: Optional[str] = None) -> bool:
        """Vérifie si des données existent pour une date donnée."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    if training_name:
                        cursor.execute("""
                            SELECT COUNT(*) FROM sessions 
                            WHERE date = %s AND training_name = %s
                        """, (date, training_name))
                    else:
                        cursor.execute("""
                            SELECT COUNT(*) FROM sessions WHERE date = %s
                        """, (date,))
                    
                    return cursor.fetchone()[0] > 0
        except Exception as e:
            raise DatabaseError(f"Erreur lors de la vérification: {e}")
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques de la base de données."""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    stats = {}
                    
                    # Nombre de sessions
                    cursor.execute("SELECT COUNT(*) FROM sessions")
                    stats['total_sessions'] = cursor.fetchone()[0]
                    
                    # Nombre de séries
                    cursor.execute("SELECT COUNT(*) FROM sets")
                    stats['total_sets'] = cursor.fetchone()[0]
                    
                    # Nombre d'exercices uniques
                    cursor.execute("SELECT COUNT(DISTINCT exercise) FROM sets")
                    stats['unique_exercises'] = cursor.fetchone()[0]
                    
                    # Nombre d'exercices catalogués
                    cursor.execute("SELECT COUNT(*) FROM exercises")
                    stats['catalogued_exercises'] = cursor.fetchone()[0]
                    
                    # Période de données
                    cursor.execute("SELECT MIN(date), MAX(date) FROM sessions")
                    date_range = cursor.fetchone()
                    stats['date_range'] = {
                        'start': date_range[0] if date_range[0] else None,
                        'end': date_range[1] if date_range[1] else None
                    }
                    
                    return stats
        except Exception as e:
            raise DatabaseError(f"Erreur lors de la récupération des stats: {e}")


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

# Instance globale de configuration
_config_manager = DatabaseConfig()


def get_database_config(environment: Optional[DatabaseEnvironment] = None) -> Dict[str, Any]:
    """
    Récupère la configuration de base de données.
    
    Args:
        environment: Environnement spécifique ou None pour auto-détection
        
    Returns:
        Configuration de base de données
    """
    if environment is None:
        environment = _config_manager.get_current_environment()
    
    return _config_manager.get_config(environment)


def get_database(environment: Optional[DatabaseEnvironment] = None) -> DatabaseManager:
    """
    Crée un DatabaseManager configuré automatiquement.
    
    Args:
        environment: Environnement spécifique ou None pour auto-détection
        
    Returns:
        Instance de DatabaseManager configurée
        
    Examples:
        # Configuration automatique
        db = get_database()
        
        # Configuration spécifique
        test_db = get_database(DatabaseEnvironment.TEST)
        prod_db = get_database(DatabaseEnvironment.PRODUCTION)
    """
    config = get_database_config(environment)
    return DatabaseManager.from_config(config)


def setup_test_database() -> DatabaseManager:
    """Utilitaire pour configurer rapidement une base de test"""
    return get_database(DatabaseEnvironment.TEST)


def setup_development_database() -> DatabaseManager:
    """Utilitaire pour configurer rapidement une base de développement"""
    return get_database(DatabaseEnvironment.DEVELOPMENT)


# =============================================================================
# COMPATIBILITÉ AVEC L'ANCIEN CODE
# =============================================================================

# Pour compatibilité avec l'ancien code
def get_db_config(environment: Optional[DatabaseEnvironment] = None) -> Dict[str, Any]:
    """Alias pour get_database_config (compatibilité)"""
    return get_database_config(environment)


# Export des classes principales
__all__ = [
    'DatabaseManager', 'DatabaseConfig', 'DatabaseEnvironment', 'DatabaseError',
    'get_database', 'get_database_config', 'setup_test_database', 'setup_development_database'
]


if __name__ == "__main__":
    # Test rapide
    print("🔧 Configuration de base de données")
    
    current_env = _config_manager.get_current_environment()
    print(f"🌍 Environnement: {current_env.value}")
    
    config = get_database_config()
    print(f"📊 Configuration: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
    
    # Test de connexion
    try:
        db = get_database()
        if db.test_connection():
            print("✅ Connexion réussie")
        else:
            print("❌ Connexion échouée")
    except Exception as e:
        print(f"❌ Erreur: {e}")
