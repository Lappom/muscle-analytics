"""
Module de gestion de la base de données pour Muscle-Analytics.

Gère les connexions, insertions et opérations CRUD pour les données d'entraînement.
"""

import psycopg2
import pandas as pd
from typing import Optional, List, Dict, Tuple, Any
import logging
from datetime import datetime, date
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)


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
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        
        # Configuration depuis variables d'environnement si disponibles
        self.connection_params.update({
            'host': os.getenv('DB_HOST', host),
            'port': int(os.getenv('DB_PORT', port)),
            'database': os.getenv('DB_NAME', database),
            'user': os.getenv('DB_USER', user),
            'password': os.getenv('DB_PASSWORD', password)
        })
    
    @contextmanager
    def get_connection(self):
        """Context manager pour les connexions à la base de données"""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
            conn.commit()
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Erreur de base de données: {e}")
        except Exception as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Erreur inattendue: {e}")
        finally:
            if conn:
                conn.close()
    
    def test_connection(self) -> bool:
        """
        Test la connexion à la base de données.
        
        Returns:
            True si la connexion réussit, False sinon
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    logger.info("Connexion à la base de données réussie")
                    return result[0] == 1
        except DatabaseError as e:
            logger.error(f"Échec de la connexion à la base de données: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur inattendue lors du test de connexion: {e}")
            return False
    
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
        """
        Parse une valeur de muscle en liste de strings.
        
        Gère de manière cohérente les valeurs string, NaN, et None
        pour les champs muscles_primary et muscles_secondary.
        
        Args:
            muscle_value: Valeur à parser (peut être string, NaN, None, etc.)
            
        Returns:
            Liste de muscles (vide si la valeur est invalide)
        """
        if isinstance(muscle_value, str) and pd.notna(muscle_value):
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
        """
        Récupère les dates des données déjà présentes en base.
        
        Returns:
            Liste des dates des sessions existantes
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT date FROM sessions ORDER BY date")
                    return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            raise DatabaseError(f"Erreur lors de la récupération des dates: {e}")
    
    def check_data_exists(self, date: date, training_name: Optional[str] = None) -> bool:
        """
        Vérifie si des données existent pour une date donnée.
        
        Args:
            date: Date à vérifier
            training_name: Nom d'entraînement optionnel
            
        Returns:
            True si des données existent
        """
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
        """
        Récupère les statistiques de la base de données.
        
        Returns:
            Dictionnaire avec les statistiques
        """
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
