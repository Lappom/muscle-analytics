"""
Pipeline ETL principal pour Muscle-Analytics.

Orchestrateur qui combine parsing et normalisation.
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Union, Sequence, Dict, Any
import logging

from .csv_parser import CSVParser, CSVParserError
from .xml_parser import XMLParser, XMLParserError
from .normalization import DataNormalizer, NormalizationError

logger = logging.getLogger(__name__)


class ETLPipelineError(Exception):
    """Exception spécifique au pipeline ETL"""
    pass


class ETLPipeline:
    """Pipeline ETL complet pour les données d'entraînement"""
    
    def __init__(self):
        """Initialise le pipeline ETL"""
        self.csv_parser = CSVParser()
        self.xml_parser = XMLParser()
        self.normalizer = DataNormalizer()
    
    def process_file(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Traite un fichier d'entraînement (CSV ou XML).
        
        Args:
            file_path: Chemin vers le fichier à traiter
            
        Returns:
            DataFrame normalisé prêt pour insertion en base
            
        Raises:
            ETLPipelineError: En cas d'erreur de traitement
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise ETLPipelineError(f"Fichier non trouvé: {file_path}")
            
            # Détection du format du fichier
            file_extension = file_path.suffix.lower()
            
            logger.info(f"Traitement du fichier: {file_path} (format: {file_extension})")
            
            # Parsing selon le format
            if file_extension == '.csv':
                raw_df = self.csv_parser.parse_file(file_path)
            elif file_extension == '.xml':
                raw_df = self.xml_parser.parse_file(file_path)
            else:
                raise ETLPipelineError(f"Format de fichier non supporté: {file_extension}")
            
            if raw_df.empty:
                logger.warning(f"Aucune donnée extraite du fichier: {file_path}")
                return pd.DataFrame()
            
            # Normalisation des données
            normalized_df = self.normalizer.normalize_dataframe(raw_df)
            
            logger.info(f"Pipeline terminé: {len(normalized_df)} lignes normalisées")
            
            return normalized_df
            
        except (CSVParserError, XMLParserError, NormalizationError) as e:
            raise ETLPipelineError(f"Erreur de traitement: {str(e)}")
        except Exception as e:
            raise ETLPipelineError(f"Erreur inattendue: {str(e)}")
    
    def process_multiple_files(self, file_paths: Sequence[Union[str, Path]]) -> pd.DataFrame:
        """
        Traite plusieurs fichiers et combine les résultats.
        
        Args:
            file_paths: Liste des chemins de fichiers à traiter
            
        Returns:
            DataFrame combiné et normalisé
        """
        combined_data = []
        
        for file_path in file_paths:
            try:
                df = self.process_file(file_path)
                if not df.empty:
                    # Ajout de métadonnées sur la source
                    df['source_file'] = str(Path(file_path).name)
                    combined_data.append(df)
                    
            except ETLPipelineError as e:
                logger.error(f"Erreur lors du traitement de {file_path}: {e}")
                continue
        
        if not combined_data:
            logger.warning("Aucune donnée valide trouvée dans les fichiers")
            return pd.DataFrame()
        
        # Combinaison des DataFrames
        final_df = pd.concat(combined_data, ignore_index=True)
        
        # Tri par date et heure
        final_df = self._sort_by_datetime(final_df)
        
        logger.info(f"Traitement multiple terminé: {len(final_df)} lignes totales")
        
        return final_df
    
    def _sort_by_datetime(self, df: pd.DataFrame) -> pd.DataFrame:
        """Trie le DataFrame par date et heure"""
        if 'date' in df.columns:
            # Conversion en datetime pour le tri
            df['_sort_datetime'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Ajout de l'heure si disponible
            if 'time' in df.columns:
                time_series = pd.to_datetime(df['time'], format='%H:%M', errors='coerce').dt.time
                for i, (date, time_val) in enumerate(zip(df['_sort_datetime'], time_series)):
                    if pd.notna(date) and time_val is not None:
                        df.loc[i, '_sort_datetime'] = pd.Timestamp.combine(date.date(), time_val)
            
            # Tri et suppression de la colonne temporaire
            df = df.sort_values('_sort_datetime', na_position='last')
            df = df.drop('_sort_datetime', axis=1)
            df = df.reset_index(drop=True)
        
        return df
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valide la qualité des données normalisées.
        
        Args:
            df: DataFrame normalisé
            
        Returns:
            Dictionnaire avec métriques de qualité
        """
        quality_metrics: Dict[str, Any] = {
            'total_rows': len(df),
            'valid_sets': 0,
            'missing_dates': 0,
            'missing_exercises': 0,
            'invalid_weights': 0,
            'invalid_reps': 0,
            'skipped_sets': 0,
            'quality_percentage': 0.0
        }
        
        if df.empty:
            quality_metrics['quality_percentage'] = 0.0
            return quality_metrics
        
        # Calcul des métriques
        if 'is_valid_set' in df.columns:
            quality_metrics['valid_sets'] = df['is_valid_set'].sum()
        
        if 'date' in df.columns:
            quality_metrics['missing_dates'] = df['date'].isna().sum()
        
        if 'exercise' in df.columns:
            quality_metrics['missing_exercises'] = (
                df['exercise'].isna() | (df['exercise'] == 'unknown')
            ).sum()
        
        if 'weight_kg' in df.columns:
            quality_metrics['invalid_weights'] = (df['weight_kg'] < 0).sum()
        
        if 'reps' in df.columns:
            quality_metrics['invalid_reps'] = (df['reps'] <= 0).sum()
        
        if 'skipped' in df.columns:
            quality_metrics['skipped_sets'] = df['skipped'].sum()
        
        # Calcul du pourcentage de qualité
        if quality_metrics['total_rows'] > 0:
            quality_metrics['quality_percentage'] = float(
                quality_metrics['valid_sets'] / quality_metrics['total_rows'] * 100
            )
        else:
            quality_metrics['quality_percentage'] = 0.0
        
        return quality_metrics
    
    def generate_summary_report(self, df: pd.DataFrame) -> str:
        """
        Génère un rapport de synthèse des données.
        
        Args:
            df: DataFrame normalisé
            
        Returns:
            Rapport sous forme de string
        """
        if df.empty:
            return "Aucune donnée à analyser."
        
        quality = self.validate_data_quality(df)
        
        # Statistiques de base
        unique_exercises = df['exercise'].nunique() if 'exercise' in df.columns else 0
        date_range = None
        
        if 'date' in df.columns and not df['date'].isna().all():
            dates = pd.to_datetime(df['date'], errors='coerce').dropna()
            if not dates.empty:
                date_range = f"{dates.min().strftime('%Y-%m-%d')} à {dates.max().strftime('%Y-%m-%d')}"
        
        total_volume = df['volume'].sum() if 'volume' in df.columns else 0
        
        # Génération du rapport
        report = f"""
📊 RAPPORT DE SYNTHÈSE - MUSCLE ANALYTICS
==========================================

📈 Statistiques générales:
- Total d'enregistrements: {quality['total_rows']}
- Séries valides: {quality['valid_sets']} ({quality['quality_percentage']:.1f}%)
- Exercices uniques: {unique_exercises}
- Période: {date_range or 'Non définie'}
- Volume total: {total_volume:.1f} kg

⚠️  Qualité des données:
- Dates manquantes: {quality['missing_dates']}
- Exercices non identifiés: {quality['missing_exercises']}
- Poids invalides: {quality['invalid_weights']}
- Répétitions invalides: {quality['invalid_reps']}
- Séries sautées: {quality['skipped_sets']}

💪 Top exercices (par nombre de séries):
"""
        
        # Top exercices
        if 'exercise' in df.columns:
            top_exercises = df['exercise'].value_counts().head(5)
            for exercise, count in top_exercises.items():
                report += f"- {exercise}: {count} séries\n"
        
        return report

