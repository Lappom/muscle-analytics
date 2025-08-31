"""
Parser XML robuste pour les fichiers d'entraînement de musculation.

Support des formats XML avec structure flexible et validation.
"""

import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import logging
from .utils import TextCleaner

logger = logging.getLogger(__name__)


class XMLParserError(Exception):
    """Exception spécifique au parser XML"""
    pass


class XMLParser:
    """Parser XML robuste pour les données d'entraînement"""
    
    # Mapping des tags XML vers colonnes standardisées
    TAG_MAPPING = {
        # Tags principaux
        'date': ['date', 'Date'],
        'training': ['training', 'workout', 'entraînement', 'entrainement'],
        'time': ['time', 'heure', 'hour', 'start_time'],
        'exercise': ['exercise', 'exercice'],
        'region': ['region', 'région', 'zone', 'muscle_group'],
        'muscles_primary': ['muscles_primary', 'primary_muscles', 'muscles_primaires'],
        'muscles_secondary': ['muscles_secondary', 'secondary_muscles', 'muscles_secondaires'],
        'series_type': ['series_type', 'set_type', 'type_serie', 'type'],
        'reps': ['reps', 'repetitions', 'répétitions', 'rep'],
        'weight': ['weight', 'poids', 'load', 'charge'],
        'notes': ['notes', 'comment', 'commentaire', 'remarks'],
        'skipped': ['skipped', 'sautee', 'sautée', 'skip']
    }
    
    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialise le parser XML.
        
        Args:
            encoding: Encodage du fichier XML
        """
        self.encoding = encoding
    
    def parse_file(self, file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Parse un fichier XML d'entraînement.
        
        Args:
            file_path: Chemin vers le fichier XML
            
        Returns:
            DataFrame avec colonnes normalisées
            
        Raises:
            XMLParserError: En cas d'erreur de parsing
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise XMLParserError(f"Fichier non trouvé: {file_path}")
            
            # Parse du XML
            tree = self._parse_xml_file(file_path)
            root = tree.getroot()
            
            if root is None:
                raise XMLParserError(f"Racine XML vide dans {file_path}")
            
            # Extraction des données
            data_records = self._extract_records(root)
            
            if not data_records:
                logger.warning(f"Aucune donnée extraite du fichier XML: {file_path}")
                return pd.DataFrame()
            
            # Conversion en DataFrame
            df = pd.DataFrame(data_records)
            
            # Normalisation des colonnes
            df = self._normalize_columns(df)
            
            logger.info(f"XML parsé avec succès: {len(df)} lignes, colonnes: {list(df.columns)}")
            
            return df
            
        except ET.ParseError as e:
            raise XMLParserError(f"Erreur de format XML dans {file_path}: {str(e)}")
        except Exception as e:
            raise XMLParserError(f"Erreur lors du parsing XML {file_path}: {str(e)}")
    
    def _parse_xml_file(self, file_path: Path) -> ET.ElementTree:
        """Parse le fichier XML avec gestion des encodages"""
        # Encodages à tester, incluant UTF-16 pour les fichiers avec BOM
        encodings = [self.encoding, 'utf-8', 'utf-16', 'utf-16le', 'utf-16be', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # Nettoyage du contenu XML si nécessaire
                content = self._clean_xml_content(content)
                
                tree = ET.fromstring(content)
                logger.debug(f"XML lu avec l'encodage {encoding}")
                return ET.ElementTree(tree)
                
            except (UnicodeDecodeError, ET.ParseError) as e:
                logger.debug(f"Échec avec encodage {encoding}: {e}")
                continue
                
        raise XMLParserError(f"Impossible de parser le XML avec les encodages: {encodings}")
    
    def _clean_xml_content(self, content: str) -> str:
        """Nettoie le contenu XML"""
        # Suppression du BOM UTF-16/UTF-8 si présent
        if content.startswith('\ufeff'):
            content = content[1:]
        if content.startswith('ÿþ'):
            content = content[2:]
            
        # Suppression des caractères de contrôle problématiques
        content = content.replace('\x00', '')
        
        # Remplacement des espaces insécables
        content = content.replace('\u00a0', ' ')
        content = content.replace('\xa0', ' ')
        
        return content
    
    def _extract_records(self, root: ET.Element) -> List[Dict[str, Any]]:
        """
        Extrait les enregistrements depuis l'élément racine.
        
        Supporte plusieurs formats XML :
        - <logs><log>...</log></logs>
        - <workouts><workout>...</workout></workouts>
        - <sessions><session>...</session></sessions>
        """
        records = []
        
        # Détection automatique de la structure
        record_elements = self._find_record_elements(root)
        
        for element in record_elements:
            record = self._extract_single_record(element)
            if record:  # Ignore les enregistrements vides
                records.append(record)
        
        return records
    
    def _find_record_elements(self, root: ET.Element) -> List[ET.Element]:
        """Trouve les éléments contenant les enregistrements individuels"""
        # Patterns de recherche pour les éléments d'enregistrement
        record_patterns = [
            'log', 'logs/log', './/log',
            'workout', 'workouts/workout', './/workout',
            'session', 'sessions/session', './/session',
            'set', 'sets/set', './/set',
            'entry', 'entries/entry', './/entry'
        ]
        
        for pattern in record_patterns:
            elements = root.findall(pattern)
            if elements:
                logger.debug(f"Trouvé {len(elements)} éléments avec le pattern '{pattern}'")
                return elements
        
        # Si aucun pattern trouvé, essaie les enfants directs
        if len(root) > 0:
            logger.debug(f"Utilisation des enfants directs: {len(root)} éléments")
            return list(root)
        
        # Dernier recours: l'élément racine lui-même
        logger.debug("Utilisation de l'élément racine comme enregistrement unique")
        return [root]
    
    def _extract_single_record(self, element: ET.Element) -> Optional[Dict[str, Any]]:
        """Extrait un enregistrement unique depuis un élément XML"""
        record = {}
        
        # Extraction des attributs de l'élément
        for attr_name, attr_value in element.attrib.items():
            column_name = self._map_tag_to_column(attr_name)
            if column_name:
                record[column_name] = self._clean_value(attr_value)
        
        # Extraction des éléments enfants
        for child in element:
            column_name = self._map_tag_to_column(child.tag)
            if column_name:
                value = child.text if child.text else ''
                record[column_name] = self._clean_value(value)
            
            # Gestion des sous-éléments (par exemple, listes de muscles)
            if len(child) > 0:
                sub_values = [sub.text for sub in child if sub.text]
                if sub_values:
                    record[column_name] = ', '.join(sub_values)
        
        # Si l'élément n'a pas d'enfants, utilise son texte direct
        if not record and element.text:
            # Tente de parser le texte comme données structurées
            text_record = self._parse_text_content(element.text)
            record.update(text_record)
        
        return record if record else None
    
    def _map_tag_to_column(self, tag: str) -> Optional[str]:
        """Mappe un tag XML vers un nom de colonne standardisé"""
        tag_cleaned = self._clean_tag_name(tag)
        
        for column, possible_tags in self.TAG_MAPPING.items():
            for possible_tag in possible_tags:
                if tag_cleaned.lower() == possible_tag.lower():
                    return column
        
        # Si pas de mapping trouvé, utilise le tag nettoyé
        return tag_cleaned if tag_cleaned else None
    
    def _clean_tag_name(self, tag: str) -> str:
        """Nettoie un nom de tag XML"""
        return TextCleaner.clean_tag_name(tag)
    
    def _clean_value(self, value: str) -> str:
        """Nettoie une valeur XML"""
        return TextCleaner.clean_xml_value(value)
    
    def _parse_text_content(self, text: str) -> Dict[str, str]:
        """Parse le contenu texte pour extraire des données structurées"""
        record = {}
        
        # Pattern simple pour "key: value" ou "key=value"
        import re
        patterns = [
            r'(\w+):\s*([^\n,]+)',
            r'(\w+)=([^\n,]+)',
            r'(\w+)\s*-\s*([^\n,]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for key, value in matches:
                column_name = self._map_tag_to_column(key)
                if column_name:
                    record[column_name] = self._clean_value(value)
        
        return record
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalise les colonnes du DataFrame"""
        # Ajout des colonnes manquantes
        for standard_column in self.TAG_MAPPING.keys():
            if standard_column not in df.columns:
                df[standard_column] = None
        
        # Réorganisation des colonnes dans un ordre logique
        column_order = [
            'date', 'time', 'training', 'exercise', 'region',
            'muscles_primary', 'muscles_secondary', 'series_type',
            'reps', 'weight', 'notes', 'skipped'
        ]
        
        # Ajout des colonnes supplémentaires non prévues
        extra_columns = [col for col in df.columns if col not in column_order]
        final_columns = column_order + extra_columns
        
        # Filtrage des colonnes existantes
        existing_columns = [col for col in final_columns if col in df.columns]
        
        return df[existing_columns]
    
    def parse_string(self, xml_content: str) -> pd.DataFrame:
        """
        Parse du contenu XML depuis une chaîne.
        
        Args:
            xml_content: Contenu XML sous forme de string
            
        Returns:
            DataFrame avec colonnes normalisées
        """
        try:
            xml_content = self._clean_xml_content(xml_content)
            root = ET.fromstring(xml_content)
            
            data_records = self._extract_records(root)
            
            if not data_records:
                return pd.DataFrame()
            
            df = pd.DataFrame(data_records)
            df = self._normalize_columns(df)
            
            return df
            
        except ET.ParseError as e:
            raise XMLParserError(f"Erreur de format XML: {str(e)}")
        except Exception as e:
            raise XMLParserError(f"Erreur lors du parsing XML: {str(e)}")

