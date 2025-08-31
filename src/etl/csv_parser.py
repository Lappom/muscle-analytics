"""
Parser CSV robuste pour les fichiers d'entraînement de musculation.

Gère les spécificités du format français :
- Virgules décimales
- Espaces insécables
- Formats de dates DD/MM/YYYY
- Unités locales (kg, répétitions)
"""

import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CSVParserError(Exception):
    """Exception spécifique au parser CSV"""
    pass


class CSVParser:
    """Parser CSV robuste pour les données d'entraînement français"""
    
    # Colonnes attendues dans le CSV (mapping flexible)
    COLUMN_MAPPING = {
        'date': ['Date', 'date'],
        'training': ['Entraînement', 'entrainement', 'training', 'workout'],
        'time': ['Heure', 'heure', 'time', 'hour'],
        'exercise': ['Exercice', 'exercice', 'exercise'],
        'region': ['Région', 'region', 'zone'],
        'muscles_primary': [
            'Groupes musculaires (Primaires)', 
            'Muscles primaires', 
            'muscles_primary',
            'primary_muscles'
        ],
        'muscles_secondary': [
            'Groupes musculaires (Secondaires)', 
            'Muscles secondaires',
            'muscles_secondary',
            'secondary_muscles'
        ],
        'series_type': [
            'Série / Série d\'échauffement / Série de récupération',
            'Type de série',
            'series_type',
            'set_type'
        ],
        'reps': ['Répétitions / Temps', 'Répétitions', 'reps', 'repetitions'],
        'weight': ['Poids / Distance', 'Poids', 'weight', 'poids'],
        'notes': ['Notes', 'notes', 'commentaires'],
        'skipped': ['Sautée', 'sautee', 'skipped', 'skip']
    }
    
    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialise le parser CSV.
        
        Args:
            encoding: Encodage du fichier CSV (utf-8, cp1252, iso-8859-1)
        """
        self.encoding = encoding
        
    def parse_file(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Parse un fichier CSV d'entraînement.
        
        Args:
            file_path: Chemin vers le fichier CSV
            
        Returns:
            DataFrame avec colonnes normalisées
            
        Raises:
            CSVParserError: En cas d'erreur de parsing
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise CSVParserError(f"Fichier non trouvé: {file_path}")
                
            # Lecture du CSV avec plusieurs encodages possibles
            df = self._read_csv_with_fallback(file_path)
            
            # Normalisation des noms de colonnes
            df = self._normalize_column_names(df)
            
            # Validation des colonnes obligatoires
            self._validate_required_columns(df)
            
            logger.info(f"CSV parsé avec succès: {len(df)} lignes, colonnes: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            raise CSVParserError(f"Erreur lors du parsing du CSV {file_path}: {str(e)}")
    
    def _read_csv_with_fallback(self, file_path: Path) -> pd.DataFrame:
        """Lit le CSV en testant plusieurs encodages et stratégies de parsing"""
        # Encodages à tester, incluant UTF-16 pour les fichiers avec BOM
        encodings = [self.encoding, 'utf-8', 'utf-16', 'utf-16le', 'utf-16be', 'cp1252', 'iso-8859-1']
        
        # Stratégies de parsing à essayer
        parsing_strategies = [
            # Stratégie standard
            {
                'sep': ',',
                'quotechar': '"',
                'skipinitialspace': True,
                'escapechar': None,
                'on_bad_lines': 'error'
            },
            # Stratégie avec gestion des erreurs tolérante
            {
                'sep': ',',
                'quotechar': '"',
                'skipinitialspace': True,
                'escapechar': None,
                'on_bad_lines': 'skip'
            },
            # Stratégie avec échappement
            {
                'sep': ',',
                'quotechar': '"',
                'skipinitialspace': True,
                'escapechar': '\\',
                'on_bad_lines': 'skip'
            },
            # Stratégie avec quote minimal
            {
                'sep': ',',
                'quotechar': '"',
                'skipinitialspace': True,
                'quoting': 1,  # QUOTE_ALL
                'on_bad_lines': 'skip'
            }
        ]
        
        for encoding in encodings:
            for strategy in parsing_strategies:
                try:
                    # Vérification de la version de pandas pour compatibilité
                    pandas_version = pd.__version__
                    
                    # Pour pandas < 1.3.0, utiliser error_bad_lines au lieu de on_bad_lines
                    if pandas_version < '1.3.0':
                        strategy_copy = strategy.copy()
                        if 'on_bad_lines' in strategy_copy:
                            if strategy_copy['on_bad_lines'] == 'skip':
                                strategy_copy['error_bad_lines'] = False
                            else:
                                strategy_copy['error_bad_lines'] = True
                            del strategy_copy['on_bad_lines']
                        strategy = strategy_copy
                    
                    df = pd.read_csv(
                        file_path,
                        encoding=encoding,
                        **strategy
                    )
                    
                    # Vérification et nettoyage des colonnes avec BOM
                    if not df.empty and len(df.columns) > 0:
                        first_col = df.columns[0]
                        # Détection et suppression du BOM UTF-16/UTF-8
                        if first_col.startswith('\ufeff') or first_col.startswith('ÿþ') or 'ÿþ' in first_col:
                            logger.debug(f"BOM détecté dans la première colonne: {repr(first_col)}")
                            # Nettoyage du nom de la première colonne
                            cleaned_first_col = first_col.replace('\ufeff', '').replace('ÿþ', '').strip()
                            if cleaned_first_col:
                                df = df.rename(columns={first_col: cleaned_first_col})
                            else:
                                # Si la première colonne est vide après nettoyage, on tente de réorganiser
                                if len(df.columns) > 12:  # Plus de colonnes que prévu
                                    # Supprimer les colonnes vides au début
                                    cols_to_drop = []
                                    for col in df.columns:
                                        if col.startswith('Unnamed:') or 'ÿþ' in col or col.strip() == '':
                                            cols_to_drop.append(col)
                                        else:
                                            break
                                    if cols_to_drop:
                                        df = df.drop(columns=cols_to_drop)
                                        logger.debug(f"Colonnes supprimées: {cols_to_drop}")
                    
                    logger.debug(f"CSV lu avec l'encodage {encoding} et stratégie {strategy}")
                    return df
                    
                except (UnicodeDecodeError, pd.errors.ParserError) as e:
                    logger.debug(f"Échec avec encodage {encoding} et stratégie {strategy}: {e}")
                    continue
                except Exception as e:
                    logger.debug(f"Erreur inattendue avec encodage {encoding}: {e}")
                    continue
                
        raise CSVParserError(f"Impossible de lire le fichier avec tous les encodages et stratégies testés")
    
    def _normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalise les noms de colonnes selon le mapping"""
        normalized_columns = {}
        
        for standard_name, possible_names in self.COLUMN_MAPPING.items():
            for col in df.columns:
                # Nettoyage du nom de colonne (espaces, accents)
                clean_col = self._clean_text(col)
                
                for possible_name in possible_names:
                    clean_possible = self._clean_text(possible_name)
                    if clean_col.lower() == clean_possible.lower():
                        normalized_columns[col] = standard_name
                        break
        
        # Renommage des colonnes
        df_renamed = df.rename(columns=normalized_columns)
        
        # Ajout des colonnes manquantes avec valeurs par défaut
        for standard_name in self.COLUMN_MAPPING.keys():
            if standard_name not in df_renamed.columns:
                df_renamed[standard_name] = None
        
        # Suppression des colonnes originales pour éviter les doublons
        original_columns_to_remove = []
        for original_col, new_col in normalized_columns.items():
            if original_col != new_col and original_col in df_renamed.columns:
                original_columns_to_remove.append(original_col)
        
        df_renamed = df_renamed.drop(columns=original_columns_to_remove)
                
        return df_renamed
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte (espaces insécables, accents, etc.)"""
        if not isinstance(text, str):
            return str(text)
            
        # Remplacement des espaces insécables par des espaces normaux
        text = text.replace('\u00a0', ' ')
        text = text.replace('\xa0', ' ')
        
        # Suppression des espaces en début/fin
        text = text.strip()
        
        return text
    
    def _validate_required_columns(self, df: pd.DataFrame) -> None:
        """Valide la présence des colonnes obligatoires"""
        required_columns = ['date', 'exercise', 'reps', 'weight']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise CSVParserError(f"Colonnes obligatoires manquantes: {missing_columns}")
    
    def parse_french_decimal(self, value: str) -> float:
        """
        Convertit une décimale française (virgule) en float.
        Gère les cas avec plusieurs virgules en prenant les deux premiers segments.

        Args:
            value: Valeur avec virgule décimale (ex: "12,5", "12,5,5")

        Returns:
            Valeur float
        """
        if pd.isna(value) or value == '':
            return 0.0

        # Nettoyage du texte
        cleaned = self._clean_text(str(value))

        # Suppression des unités communes
        units_pattern = r'\s*(kg|kilogrammes?|grammes?|g|lbs?|pounds?|répétitions?|reps?)\s*'
        cleaned = re.sub(units_pattern, '', cleaned, flags=re.IGNORECASE)

        # Suppression des espaces
        cleaned = re.sub(r'\s+', '', cleaned)

        # Gestion des virgules et conversion
        try:
            parts = cleaned.split(',')
            int_part = parts[0] if parts[0] != '' else '0'
            frac_part = parts[1] if len(parts) > 1 and parts[1] != '' else '0'
            cleaned = f"{int_part}.{frac_part}" if len(parts) > 1 else int_part
            return float(cleaned)
        except ValueError:
            logger.warning(f"Impossible de convertir '{value}' en float, retour 0.0")
            return 0.0
    
    def parse_weight(self, weight_str: str) -> float:
        """
        Parse une valeur de poids avec unité.
        
        Args:
            weight_str: Poids avec unité (ex: "12,5 kg", "0,00 kg")
            
        Returns:
            Poids en kg (float)
        """
        if pd.isna(weight_str) or weight_str == '':
            return 0.0
            
        # Nettoyage et suppression des unités
        cleaned = self._clean_text(str(weight_str))
        
        # Suppression des unités communes
        units_pattern = r'\s*(kg|kilogrammes?|grammes?|g|lbs?|pounds?)\s*'
        cleaned = re.sub(units_pattern, '', cleaned, flags=re.IGNORECASE)
        
        return self.parse_french_decimal(cleaned)
    
    def parse_reps(self, reps_str: str) -> int:
        """
        Parse une valeur de répétitions.
        
        Args:
            reps_str: Répétitions (ex: "12 répétitions", "8")
            
        Returns:
            Nombre de répétitions (int)
        """
        if pd.isna(reps_str) or reps_str == '':
            return 0
            
        # Nettoyage du texte
        cleaned = self._clean_text(str(reps_str))
        
        # Extraction du nombre
        numbers = re.findall(r'\d+', cleaned)
        
        if numbers:
            return int(numbers[0])
        else:
            logger.warning(f"Impossible d'extraire le nombre de répétitions de '{reps_str}', retour 0")
            return 0
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse une date au format français DD/MM/YYYY.
        
        Args:
            date_str: Date au format français
            
        Returns:
            Objet datetime ou None si parsing impossible
        """
        if pd.isna(date_str) or date_str == '':
            return None
            
        cleaned = self._clean_text(str(date_str))
        
        # Formats de date supportés
        date_formats = ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(cleaned, fmt)
            except ValueError:
                continue
                
        logger.warning(f"Impossible de parser la date '{date_str}'")
        return None
    
    def parse_boolean(self, bool_str: str) -> bool:
        """
        Parse une valeur booléenne française.
        
        Args:
            bool_str: Valeur booléenne (Oui/Non, True/False)
            
        Returns:
            Valeur booléenne
        """
        if pd.isna(bool_str) or bool_str == '':
            return False
            
        cleaned = self._clean_text(str(bool_str)).lower()
        
        true_values = ['oui', 'yes', 'true', '1', 'vrai']
        false_values = ['non', 'no', 'false', '0', 'faux']
        
        if cleaned in true_values:
            return True
        elif cleaned in false_values:
            return False
        else:
            logger.warning(f"Valeur booléenne non reconnue '{bool_str}', retour False")
            return False