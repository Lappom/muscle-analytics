"""
Module de normalisation des données d'entraînement.

Transforme les données brutes en format canonique pour insertion en base.
Inclut feature engineering basique (volume, 1RM estimé).
"""

import pandas as pd
import re
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, time
import logging

from .utils import TextCleaner

logger = logging.getLogger(__name__)


class NormalizationError(Exception):
    """Exception spécifique à la normalisation"""
    pass


class DataNormalizer:
    """Normalise les données d'entraînement en format canonique"""
    
    # Mapping des exercices vers noms canoniques
    EXERCISE_MAPPING = {
        'traction à la barre fixe': 'pull-up',
        'tractions barre fixe': 'pull-up',
        'traction': 'pull-up',
        'pull-up': 'pull-up',
        'développé couché': 'bench-press',
        'développé couche': 'bench-press',
        'développé': 'bench-press',
        'bench press': 'bench-press',
        'squat': 'squat',
        'squat arrière': 'back-squat',
        'squat à la barre': 'squat',
        'deadlift': 'deadlift',
        'soulevé de terre': 'deadlift',
        'overhead press': 'overhead-press',
        'développé militaire': 'overhead-press',
        'curl biceps': 'bicep-curl',
        'curl haltères': 'bicep-curl',
        'curl': 'bicep-curl',
        'dips': 'dips',
        'pompes': 'push-up',
        'push-up': 'push-up'
    }
    
    # Mapping des régions musculaires
    REGION_MAPPING = {
        'dos': 'Back',
        'back': 'Back',
        'pectoraux': 'Chest',
        'chest': 'Chest',
        'pecs': 'Chest',
        'jambes': 'Legs',
        'legs': 'Legs',
        'quadriceps': 'Legs',
        'ischio': 'Legs',
        'épaules': 'Shoulders',
        'shoulders': 'Shoulders',
        'deltoïdes': 'Shoulders',
        'bras': 'Arms',
        'arms': 'Arms',
        'biceps': 'Arms',
        'triceps': 'Arms',
        'abdominaux': 'Core',
        'core': 'Core',
        'abs': 'Core'
    }
    
    # Types de séries
    SERIES_TYPE_MAPPING = {
        'série': 'working_set',
        'principale': 'working_set',
        'working': 'working_set',
        'échauffement': 'warmup',
        'warmup': 'warmup',
        'warm-up': 'warmup',
        'récupération': 'cooldown',
        'recovery': 'cooldown',
        'cooldown': 'cooldown'
    }
    
    def __init__(self):
        """Initialise le normalisateur"""
        pass
    
    def normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalise un DataFrame complet.
        
        Args:
            df: DataFrame brut du parser
            
        Returns:
            DataFrame normalisé
        """
        try:
            df_normalized = df.copy()
            
            # Normalisation par colonne
            df_normalized['date'] = df_normalized['date'].apply(self._normalize_date)
            df_normalized['time'] = df_normalized['time'].apply(self._normalize_time)
            df_normalized['training'] = df_normalized['training'].apply(self._normalize_text)
            df_normalized['exercise'] = df_normalized['exercise'].apply(self._normalize_exercise)
            df_normalized['region'] = df_normalized['region'].apply(self._normalize_region)
            df_normalized['muscles_primary'] = df_normalized['muscles_primary'].apply(self._normalize_muscle_list)
            df_normalized['muscles_secondary'] = df_normalized['muscles_secondary'].apply(self._normalize_muscle_list)
            df_normalized['series_type'] = df_normalized['series_type'].apply(self._normalize_series_type)
            df_normalized['reps'] = df_normalized['reps'].apply(self._normalize_reps)
            df_normalized['weight_kg'] = df_normalized['weight'].apply(self._normalize_weight)
            df_normalized['skipped'] = df_normalized['skipped'].apply(self._normalize_boolean)
            df_normalized['notes'] = df_normalized['notes'].apply(self._normalize_text)
            
            # Suppression de la colonne 'weight' originale
            if 'weight' in df_normalized.columns:
                df_normalized = df_normalized.drop('weight', axis=1)
            
            # Feature engineering
            df_normalized = self._add_computed_features(df_normalized)
            
            # Nettoyage des lignes invalides
            df_normalized = self._clean_invalid_rows(df_normalized)
            
            logger.info(f"Normalisation terminée: {len(df_normalized)} lignes valides")
            
            return df_normalized
            
        except Exception as e:
            raise NormalizationError(f"Erreur lors de la normalisation: {str(e)}")
    
    def _normalize_date(self, date_value: Union[str, datetime, None]) -> Optional[str]:
        """Normalise une date en format ISO (YYYY-MM-DD)"""
        if pd.isna(date_value) or date_value is None:
            return None
            
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d')
        
        # Parse date française
        cleaned = self._clean_text(str(date_value))
        date_formats = ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d']
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(cleaned, fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        logger.warning(f"Date non parsable: '{date_value}'")
        return None
    
    def _normalize_time(self, time_value: Union[str, time, None]) -> Optional[str]:
        """Normalise une heure en format HH:MM"""
        if pd.isna(time_value) or time_value is None:
            return None
            
        if isinstance(time_value, time):
            return time_value.strftime('%H:%M')
            
        cleaned = self._clean_text(str(time_value))
        time_formats = ['%H:%M', '%H:%M:%S', '%H.%M', '%Hh%M']
        
        for fmt in time_formats:
            try:
                parsed_time = datetime.strptime(cleaned, fmt).time()
                return parsed_time.strftime('%H:%M')
            except ValueError:
                continue
                
        logger.warning(f"Heure non parsable: '{time_value}'")
        return None
    
    def _normalize_exercise(self, exercise_name: str) -> str:
        """Normalise le nom d'un exercice"""
        if pd.isna(exercise_name) or exercise_name is None or exercise_name == '':
            return 'unknown'
            
        cleaned = self._clean_text(str(exercise_name)).lower()
        
        # Recherche fuzzy dans le mapping
        for pattern, canonical in self.EXERCISE_MAPPING.items():
            if pattern.lower() in cleaned or cleaned in pattern.lower():
                return canonical
        
        # Si pas trouvé, retourne une version nettoyée
        canonical = re.sub(r'[^\w\s-]', '', cleaned)
        canonical = re.sub(r'\s+', '-', canonical.strip())
        
        if not canonical:
            return 'unknown'
        
        logger.debug(f"Exercice non mappé: '{exercise_name}' -> '{canonical}'")
        return canonical
    
    def _normalize_region(self, region: str) -> Optional[str]:
        """Normalise une région musculaire"""
        if pd.isna(region) or region is None:
            return None
            
        cleaned = self._clean_text(str(region)).lower()
        
        for pattern, canonical in self.REGION_MAPPING.items():
            if pattern in cleaned:
                return canonical
                
        return cleaned.title()
    
    def _normalize_muscle_list(self, muscles_str: str) -> List[str]:
        """Normalise une liste de muscles (séparés par virgules)"""
        if pd.isna(muscles_str) or muscles_str is None:
            return []
            
        cleaned = self._clean_text(str(muscles_str))
        
        # Séparation par virgules et nettoyage
        muscles = [m.strip() for m in cleaned.split(',') if m.strip()]
        
        return muscles
    
    def _normalize_series_type(self, series_type: str) -> str:
        """Normalise le type de série"""
        if pd.isna(series_type) or series_type is None:
            return 'working_set'
            
        cleaned = self._clean_text(str(series_type)).lower()
        
        for pattern, canonical in self.SERIES_TYPE_MAPPING.items():
            if pattern in cleaned:
                return canonical
                
        return 'working_set'
    
    def _normalize_reps(self, reps_value: Union[str, int, float]) -> int:
        """Normalise le nombre de répétitions"""
        if pd.isna(reps_value) or reps_value is None:
            return 0
            
        if isinstance(reps_value, (int, float)):
            return int(reps_value) if reps_value >= 0 else 0
            
        # Extraction du nombre depuis string
        cleaned = self._clean_text(str(reps_value))
        numbers = re.findall(r'\d+', cleaned)
        
        if numbers:
            return int(numbers[0])
        else:
            return 0
    
    def _normalize_weight(self, weight_value: Union[str, int, float]) -> float:
        """Normalise le poids en kg"""
        if pd.isna(weight_value) or weight_value is None:
            return 0.0
            
        if isinstance(weight_value, (int, float)):
            return float(weight_value) if weight_value >= 0 else 0.0
            
        # Nettoyage et conversion depuis string
        cleaned = self._clean_text(str(weight_value))
        
        # Suppression des unités
        units_pattern = r'\s*(kg|kilogrammes?|grammes?|g|lbs?|pounds?)\s*'
        cleaned = re.sub(units_pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remplacement virgule par point
        cleaned = cleaned.replace(',', '.')
        
        # Extraction du nombre
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    
    def _normalize_boolean(self, bool_value: Union[str, bool]) -> bool:
        """Normalise une valeur booléenne"""
        if pd.isna(bool_value) or bool_value is None:
            return False
            
        if isinstance(bool_value, bool):
            return bool_value
            
        cleaned = self._clean_text(str(bool_value)).lower()
        
        true_values = ['oui', 'yes', 'true', '1', 'vrai']
        return cleaned in true_values
    
    def _normalize_text(self, text_value: str) -> Optional[str]:
        """Normalise un texte général"""
        if pd.isna(text_value) or text_value is None:
            return None
            
        cleaned = self._clean_text(str(text_value))
        return cleaned if cleaned else None
    
    def _clean_text(self, text: str) -> str:
        """Nettoie un texte (espaces insécables, trim)"""
        return TextCleaner.clean_text(text)
    
    def _add_computed_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ajoute des features calculées"""
        df = df.copy()
        
        # Volume par série (reps * poids)
        df['volume'] = df['reps'] * df['weight_kg']
        
        # 1RM estimé (formule d'Epley)
        df['estimated_1rm'] = df.apply(lambda row: row['weight_kg'] * (1 + row['reps'] / 30) if row['reps'] > 0 and row['weight_kg'] > 0 and not row['skipped'] else 0.0, axis=1)
        
        # Indicateur de série valide
        df['is_valid_set'] = (df['reps'] > 0) & (~df['skipped'])
        
        return df
    

    
    def _clean_invalid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """Supprime les lignes avec des données invalides"""
        initial_count = len(df)
        
        # Suppression des lignes sans exercice
        df = df[df['exercise'].notna() & (df['exercise'] != '')]
        
        # Suppression des lignes sans date valide
        df = df[df['date'].notna()]
        
        final_count = len(df)
        
        if initial_count != final_count:
            logger.info(f"Suppression de {initial_count - final_count} lignes invalides")
            
        return df