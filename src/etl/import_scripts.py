"""
Scripts ETL pour l'import de données d'entraînement.

Fonctions utilitaires pour l'import incrémental et la gestion des données.
"""

import pandas as pd
from pathlib import Path
from typing import List, Union, Optional, Dict, Any
import logging
from datetime import datetime, date, timedelta

from .pipeline import ETLPipeline
from ..database import DatabaseManager, DatabaseError

logger = logging.getLogger(__name__)


class ETLImportError(Exception):
    """Exception spécifique aux imports ETL"""
    pass


class ETLImporter:
    """Gestionnaire d'imports ETL pour Muscle-Analytics"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """
        Initialise l'importateur ETL.
        
        Args:
            db_manager: Gestionnaire de base de données (optionnel)
        """
        self.pipeline = ETLPipeline()
        self.db_manager = db_manager or DatabaseManager()
        
        # Test de connexion à l'initialisation
        if not self.db_manager.test_connection():
            logger.warning("Impossible de se connecter à la base de données")
    
    def import_file(self, file_path: Union[str, Path], 
                   force_import: bool = False) -> Dict[str, Any]:
        """
        Importe un fichier unique avec gestion des doublons.
        
        Args:
            file_path: Chemin vers le fichier
            force_import: Force l'import même si des données existent
            
        Returns:
            Dictionnaire avec résultats de l'import
        """
        try:
            file_path = Path(file_path)
            logger.info(f"Début de l'import: {file_path.name}")
            
            # Traitement du fichier
            df = self.pipeline.process_file(file_path)
            
            if df.empty:
                logger.warning(f"Aucune donnée extraite de {file_path.name}")
                return {
                    'success': False,
                    'message': 'Aucune donnée trouvée',
                    'file': str(file_path),
                    'stats': {}
                }
            
            # Vérification des doublons si pas de force
            if not force_import:
                df = self._filter_existing_data(df)
                
                if df.empty:
                    logger.info(f"Toutes les données de {file_path.name} existent déjà")
                    return {
                        'success': True,
                        'message': 'Données déjà existantes',
                        'file': str(file_path),
                        'stats': {'duplicates_skipped': True}
                    }
            
            # Import en base
            insert_stats = self.db_manager.bulk_insert_from_dataframe(df)
            
            # Génération du rapport
            quality_metrics = self.pipeline.validate_data_quality(df)
            
            result = {
                'success': True,
                'message': f'Import réussi: {insert_stats["sets_inserted"]} séries',
                'file': str(file_path),
                'stats': {
                    **insert_stats,
                    **quality_metrics
                }
            }
            
            logger.info(f"Import terminé pour {file_path.name}: {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"Erreur lors de l'import de {file_path}: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'file': str(file_path),
                'stats': {}
            }
    
    def import_directory(self, directory_path: Union[str, Path],
                        file_pattern: str = "*.{csv,xml}",
                        force_import: bool = False) -> Dict[str, Any]:
        """
        Importe tous les fichiers d'un répertoire.
        
        Args:
            directory_path: Chemin vers le répertoire
            file_pattern: Pattern pour filtrer les fichiers (par défaut: "*.{csv,xml}")
            force_import: Force l'import même si des données existent
            
        Returns:
            Dictionnaire avec résultats globaux
        """
        try:
            directory_path = Path(directory_path)
            
            if not directory_path.exists():
                raise ETLImportError(f"Répertoire non trouvé: {directory_path}")
            
            # Recherche des fichiers selon le pattern spécifié
            all_files = []
            
            # Support pour les patterns avec accolades comme "*.{csv,xml}"
            if '{' in file_pattern and '}' in file_pattern:
                # Extraire les extensions des accolades
                start = file_pattern.find('{')
                end = file_pattern.find('}')
                prefix = file_pattern[:start]
                extensions = file_pattern[start+1:end].split(',')
                
                for ext in extensions:
                    pattern = prefix + ext.strip()
                    all_files.extend(directory_path.glob(pattern))
            else:
                # Pattern simple
                all_files = list(directory_path.glob(file_pattern))
            
            if not all_files:
                logger.warning(f"Aucun fichier trouvé avec le pattern '{file_pattern}' dans {directory_path}")
                return {
                    'success': False,
                    'message': f'Aucun fichier trouvé avec le pattern: {file_pattern}',
                    'directory': str(directory_path),
                    'files_processed': [],
                    'global_stats': {}
                }
            
            logger.info(f"Traitement de {len(all_files)} fichiers dans {directory_path}")
            
            # Import de chaque fichier
            results = []
            global_stats = {
                'files_processed': 0,
                'files_successful': 0,
                'files_failed': 0,
                'total_sessions': 0,
                'total_sets': 0,
                'total_errors': 0
            }
            
            for file_path in all_files:
                result = self.import_file(file_path, force_import)
                results.append(result)
                
                global_stats['files_processed'] += 1
                
                if result['success']:
                    global_stats['files_successful'] += 1
                    stats = result.get('stats', {})
                    global_stats['total_sessions'] += stats.get('sessions_created', 0)
                    global_stats['total_sets'] += stats.get('sets_inserted', 0)
                    global_stats['total_errors'] += stats.get('errors', 0)
                else:
                    global_stats['files_failed'] += 1
            
            success = global_stats['files_successful'] > 0
            message = f"Import terminé: {global_stats['files_successful']}/{global_stats['files_processed']} fichiers"
            
            return {
                'success': success,
                'message': message,
                'directory': str(directory_path),
                'files_processed': results,
                'global_stats': global_stats
            }
            
        except Exception as e:
            error_msg = f"Erreur lors de l'import du répertoire {directory_path}: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'directory': str(directory_path),
                'files_processed': [],
                'global_stats': {}
            }
    
    def incremental_import(self, file_or_directory: Union[str, Path],
                          days_threshold: int = 7, reference_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Import incrémental intelligent.
        
        Args:
            file_or_directory: Fichier ou répertoire à importer
            days_threshold: Seuil en jours pour considérer les données comme récentes
            reference_date: Date de référence pour le calcul (optionnel, par défaut: aujourd'hui)
            
        Returns:
            Dictionnaire avec résultats de l'import
        """
        try:
            path = Path(file_or_directory)
            
            # Récupération des dates existantes
            existing_dates = set(self.db_manager.get_existing_data_dates())
            
            if path.is_file():
                # Import d'un fichier unique
                return self._incremental_import_file(path, existing_dates, days_threshold, reference_date)
            
            elif path.is_dir():
                # Import d'un répertoire
                return self._incremental_import_directory(path, existing_dates, days_threshold, reference_date)
            
            else:
                raise ETLImportError(f"Chemin non valide: {path}")
                
        except Exception as e:
            error_msg = f"Erreur lors de l'import incrémental: {e}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'stats': {}
            }
    
    def _incremental_import_file(self, file_path: Path, existing_dates: set,
                                days_threshold: int, reference_date: Optional[date] = None) -> Dict[str, Any]:
        """Import incrémental d'un fichier"""
        logger.info(f"Import incrémental de {file_path.name}")
        
        # Prévisualisation des données
        df = self.pipeline.process_file(file_path)
        
        if df.empty:
            return {
                'success': False,
                'message': 'Aucune donnée dans le fichier',
                'stats': {}
            }
        
        # Filtrage des données récentes
        new_data = self._filter_new_data(df, existing_dates, days_threshold, reference_date)
        
        if new_data.empty:
            return {
                'success': True,
                'message': 'Aucune nouvelle donnée à importer',
                'stats': {'new_data_found': False}
            }
        
        # Import des nouvelles données
        insert_stats = self.db_manager.bulk_insert_from_dataframe(new_data)
        
        return {
            'success': True,
            'message': f'Import incrémental réussi: {insert_stats["sets_inserted"]} nouvelles séries',
            'stats': {
                **insert_stats,
                'new_data_found': True,
                'original_rows': len(df),
                'new_rows': len(new_data)
            }
        }
    
    def _incremental_import_directory(self, directory_path: Path, existing_dates: set,
                                     days_threshold: int, reference_date: Optional[date] = None) -> Dict[str, Any]:
        """Import incrémental d'un répertoire"""
        csv_files = list(directory_path.glob("*.csv"))
        xml_files = list(directory_path.glob("*.xml"))
        all_files = csv_files + xml_files
        
        if not all_files:
            return {
                'success': False,
                'message': 'Aucun fichier trouvé',
                'stats': {}
            }
        
        global_stats = {
            'files_processed': 0,
            'files_with_new_data': 0,
            'total_new_sets': 0,
            'total_errors': 0
        }
        
        for file_path in all_files:
            try:
                result = self._incremental_import_file(file_path, existing_dates, days_threshold, reference_date)
                global_stats['files_processed'] += 1
                
                if result['success'] and result['stats'].get('new_data_found', False):
                    global_stats['files_with_new_data'] += 1
                    global_stats['total_new_sets'] += result['stats'].get('sets_inserted', 0)
                
                global_stats['total_errors'] += result['stats'].get('errors', 0)
                
            except Exception as e:
                logger.error(f"Erreur sur {file_path}: {e}")
                global_stats['total_errors'] += 1
        
        return {
            'success': global_stats['files_with_new_data'] > 0,
            'message': f"Import incrémental: {global_stats['total_new_sets']} nouvelles séries",
            'stats': global_stats
        }
    
    def _filter_existing_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtre les données déjà existantes en base"""
        if df.empty:
            return df
        
        # Grouper par sessions uniques
        filtered_data = []
        
        for (session_date, training_name), group in df.groupby(['date', 'training']):
            try:
                # Convertir la date si nécessaire
                if isinstance(session_date, str):
                    check_date = pd.to_datetime(session_date).date()
                else:
                    check_date = session_date
                
                # Vérifier si cette session existe
                if not self.db_manager.check_data_exists(check_date, training_name):
                    filtered_data.append(group)
                    
            except Exception as e:
                logger.warning(f"Erreur lors de la vérification: {e}")
                # En cas d'erreur, inclure les données par sécurité
                filtered_data.append(group)
        
        if filtered_data:
            return pd.concat(filtered_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def _filter_new_data(self, df: pd.DataFrame, existing_dates: set,
                        days_threshold: int, reference_date: Optional[date] = None) -> pd.DataFrame:
        """
        Filters the input DataFrame to retain only recent data entries that do not already exist in the database.
        The method uses `days_threshold` and `reference_date` together to determine which rows are considered "recent":
        - `reference_date` (date, optional): The anchor date from which to calculate recency. If not provided, defaults to today's date.
        - `days_threshold` (int): The number of days before the `reference_date` to include. Only rows with a 'date' within this window are considered.
        
        Filtering logic:
        - For each row, parse the 'date' column as a date.
        - Keep rows where 'date' >= (`reference_date` - `days_threshold` days).
        - Exclude rows whose 'date' is present in `existing_dates`.
        
        Args:
            df (pd.DataFrame): Input data to filter. Must contain a 'date' column.
            existing_dates (set): Set of dates already present in the database.
            days_threshold (int): Number of days to look back from `reference_date`.
            reference_date (date, optional): Anchor date for filtering. Defaults to today if None.
            
        Returns:
            pd.DataFrame: Filtered DataFrame containing only new and recent rows.
        """
        if df.empty:
            return df
        
        # Convertir les dates du DataFrame
        df_copy = df.copy()
        df_copy['date_parsed'] = pd.to_datetime(df_copy['date']).dt.date
        
        # Calculer la date seuil (utilise la date de référence ou la date actuelle)
        cutoff_date = reference_date or datetime.now().date()
        
        # Filtrer les données récentes et non existantes
        mask = (df_copy['date_parsed'] >= (cutoff_date - timedelta(days=days_threshold))) & \
               (~df_copy['date_parsed'].isin(existing_dates))
        
        new_data = df_copy[mask].drop('date_parsed', axis=1)
        
        logger.info(f"Filtrage: {len(new_data)}/{len(df)} lignes sont nouvelles et récentes")
        
        return new_data
    
    def generate_import_report(self, results: Dict) -> str:
        """
        Génère un rapport d'import formaté.
        
        Args:
            results: Résultats d'import
            
        Returns:
            Rapport formaté
        """
        if not results.get('success', False):
            return f"❌ ÉCHEC D'IMPORT\n{results.get('message', 'Erreur inconnue')}"
        
        stats = results.get('stats', {})
        
        if 'global_stats' in results:
            # Rapport pour import de répertoire
            global_stats = results['global_stats']
            report = f"""
✅ RAPPORT D'IMPORT - RÉPERTOIRE
=================================

📂 Répertoire: {results.get('directory', 'N/A')}
📊 Résumé:
- Fichiers traités: {global_stats.get('files_processed', 0)}
- Fichiers réussis: {global_stats.get('files_successful', 0)}
- Fichiers échoués: {global_stats.get('files_failed', 0)}

📈 Données importées:
- Sessions créées: {global_stats.get('total_sessions', 0)}
- Séries insérées: {global_stats.get('total_sets', 0)}
- Erreurs rencontrées: {global_stats.get('total_errors', 0)}

🎯 Statut: {results.get('message', 'Import terminé')}
"""
        else:
            # Rapport pour import de fichier unique
            report = f"""
✅ RAPPORT D'IMPORT - FICHIER
=============================

📄 Fichier: {results.get('file', 'N/A')}
📊 Résultats:
- Sessions créées: {stats.get('sessions_created', 0)}
- Séries insérées: {stats.get('sets_inserted', 0)}
- Exercices catalogués: {stats.get('exercises_added', 0)}
- Erreurs: {stats.get('errors', 0)}

📈 Qualité des données:
- Total de lignes: {stats.get('total_rows', 0)}
- Séries valides: {stats.get('valid_sets', 0)}
- Qualité: {stats.get('quality_percentage', 0):.1f}%

🎯 Statut: {results.get('message', 'Import terminé')}
"""
        
        return report


def main():
    """Fonction principale pour tests en ligne de commande"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Import ETL pour Muscle-Analytics')
    parser.add_argument('path', help='Chemin vers fichier ou répertoire')
    parser.add_argument('--force', action='store_true', help='Force l\'import même si données existantes')
    parser.add_argument('--incremental', action='store_true', help='Import incrémental')
    parser.add_argument('--days', type=int, default=7, help='Seuil en jours pour import incrémental')
    
    args = parser.parse_args()
    
    # Configuration du logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Import
    importer = ETLImporter()
    
    if args.incremental:
        results = importer.incremental_import(args.path, args.days)
    else:
        path = Path(args.path)
        if path.is_file():
            results = importer.import_file(args.path, args.force)
        else:
            results = importer.import_directory(args.path, force_import=args.force)
    
    # Affichage du rapport
    report = importer.generate_import_report(results)
    print(report)


if __name__ == "__main__":
    main()
