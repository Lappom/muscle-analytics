"""
Utilitaires communs pour le module ETL
"""
import re
from typing import Union


class TextCleaner:
    """Classe utilitaire pour le nettoyage de texte"""
    
    @staticmethod
    def clean_text(text: Union[str, any]) -> str:
        """
        Nettoie un texte (espaces insécables, trim)
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            Texte nettoyé
        """
        if not isinstance(text, str):
            return str(text)
            
        # Remplacement espaces insécables
        text = text.replace('\u00a0', ' ').replace('\xa0', ' ')
        
        # Nettoyage espaces multiples
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    @staticmethod
    def clean_tag_name(tag: str) -> str:
        """
        Nettoie un nom de tag XML
        
        Args:
            tag: Nom de tag à nettoyer
            
        Returns:
            Nom de tag nettoyé
        """
        # Suppression des namespaces
        if '}' in tag:
            tag = tag.split('}')[1]
        
        # Nettoyage des caractères spéciaux
        tag = re.sub(r'[^\w]', '_', tag)
        tag = tag.strip('_')
        
        return tag
    
    @staticmethod
    def clean_xml_value(value: str) -> str:
        """
        Nettoie une valeur XML
        
        Args:
            value: Valeur à nettoyer
            
        Returns:
            Valeur nettoyée
        """
        if not value:
            return ''
        
        # Décodage des entités HTML/XML
        value = value.replace('&amp;', '&')
        value = value.replace('&lt;', '<')
        value = value.replace('&gt;', '>')
        value = value.replace('&quot;', '"')
        value = value.replace('&apos;', "'")
        
        # Nettoyage des espaces
        value = value.replace('\u00a0', ' ')
        value = value.replace('\xa0', ' ')
        value = value.strip()
        
        return value
