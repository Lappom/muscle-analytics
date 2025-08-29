"""
Tests unitaires pour le parser XML.
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
from src.etl.xml_parser import XMLParser, XMLParserError


class TestXMLParser:
    """Tests pour la classe XMLParser"""
    
    @pytest.fixture
    def parser(self):
        return XMLParser()
    
    @pytest.fixture
    def sample_xml_content(self):
        return """<?xml version="1.0" encoding="UTF-8"?>
<logs>
  <log>
    <date>29/08/2025</date>
    <training>Pecs Dos 2</training>
    <heure>16:05</heure>
    <exercice>Traction à la Barre Fixe</exercice>
    <region>Dos</region>
    <muscles_primary>Trapèzes, Muscles dorsaux</muscles_primary>
    <muscles_secondary>Biceps</muscles_secondary>
    <series_type>Série</series_type>
    <reps>13</reps>
    <weight>0,00 kg</weight>
    <notes>RAS</notes>
    <skipped>Non</skipped>
  </log>
  <log>
    <date>30/08/2025</date>
    <training>Upper Body</training>
    <heure>09:00</heure>
    <exercice>Développé couché</exercice>
    <region>Pectoraux</region>
    <muscles_primary>Pectoraux</muscles_primary>
    <muscles_secondary>Triceps</muscles_secondary>
    <series_type>Principale</series_type>
    <reps>8</reps>
    <weight>75,5 kg</weight>
    <notes>Forme parfaite</notes>
    <skipped>Non</skipped>
  </log>
</logs>"""
    
    @pytest.fixture
    def xml_file(self, sample_xml_content):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
            f.write(sample_xml_content)
            f.flush()
            yield Path(f.name)
        Path(f.name).unlink(missing_ok=True)
    
    def test_parse_file_success(self, parser, xml_file):
        """Test parsing réussi d'un fichier XML"""
        df = parser.parse_file(xml_file)
        
        assert not df.empty
        assert len(df) == 2
        assert 'date' in df.columns
        assert 'exercise' in df.columns
        assert 'weight' in df.columns
        assert 'reps' in df.columns
    
    def test_parse_string_success(self, parser, sample_xml_content):
        """Test parsing d'une chaîne XML"""
        df = parser.parse_string(sample_xml_content)
        
        assert not df.empty
        assert len(df) == 2
        assert df.iloc[0]['exercise'] == 'Traction à la Barre Fixe'
        assert df.iloc[1]['weight'] == '75,5 kg'
    
    def test_parse_file_not_found(self, parser):
        """Test parsing d'un fichier inexistant"""
        with pytest.raises(XMLParserError):
            parser.parse_file("nonexistent.xml")
    
    def test_parse_invalid_xml(self, parser):
        """Test parsing XML invalide"""
        invalid_xml = "<logs><log><date>2025-08-29</log>"  # Tag non fermé
        
        with pytest.raises(XMLParserError):
            parser.parse_string(invalid_xml)
    
    def test_different_xml_structures(self, parser):
        """Test différentes structures XML"""
        # Structure avec workouts
        xml_workouts = """<?xml version="1.0"?>
<workouts>
  <workout date="29/08/2025" exercise="Squat">
    <reps>10</reps>
    <weight>100 kg</weight>
  </workout>
</workouts>"""
        
        df = parser.parse_string(xml_workouts)
        assert not df.empty
        assert len(df) == 1
        assert 'date' in df.columns
        assert 'exercise' in df.columns
    
    def test_xml_with_attributes(self, parser):
        """Test XML avec attributs"""
        xml_with_attrs = """<?xml version="1.0"?>
<sessions>
  <session date="29/08/2025" training="Test">
    <exercise name="Pull-up" reps="10" weight="0"/>
  </session>
</sessions>"""
        
        df = parser.parse_string(xml_with_attrs)
        assert not df.empty
    
    def test_clean_xml_content(self, parser):
        """Test nettoyage du contenu XML"""
        dirty_content = "Test\u00a0avec\u00a0espaces\x00"
        cleaned = parser._clean_xml_content(dirty_content)
        
        assert '\x00' not in cleaned
        assert '\u00a0' not in cleaned
        assert 'avec espaces' in cleaned
    
    def test_map_tag_to_column(self, parser):
        """Test mapping des tags vers colonnes"""
        assert parser._map_tag_to_column('date') == 'date'
        assert parser._map_tag_to_column('exercice') == 'exercise'
        assert parser._map_tag_to_column('heure') == 'time'
        assert parser._map_tag_to_column('unknown_tag') == 'unknown_tag'
    
    def test_clean_value(self, parser):
        """Test nettoyage des valeurs"""
        assert parser._clean_value('&amp;test&lt;') == '&test<'
        assert parser._clean_value('  value  ') == 'value'
        assert parser._clean_value('') == ''
    
    def test_empty_xml(self, parser):
        """Test XML vide"""
        empty_xml = "<?xml version='1.0'?><root></root>"
        df = parser.parse_string(empty_xml)
        
        # Doit retourner un DataFrame vide mais pas lever d'erreur
        assert df.empty or len(df) == 0


class TestXMLParserIntegration:
    """Tests d'intégration pour le parser XML"""
    
    def test_complex_xml_structure(self):
        """Test structure XML complexe"""
        parser = XMLParser()
        
        complex_xml = """<?xml version="1.0"?>
<muscle_analytics>
  <sessions>
    <session date="29/08/2025" training="Full Body">
      <sets>
        <set exercise="Pull-up" reps="10" weight="0"/>
        <set exercise="Push-up" reps="15" weight="0"/>
      </sets>
    </session>
  </sessions>
</muscle_analytics>"""
        
        df = parser.parse_string(complex_xml)
        # Structure complexe peut ne pas être parfaitement parsée
        # mais ne doit pas lever d'erreur
        assert isinstance(df, pd.DataFrame)
    
    def test_xml_with_special_characters(self):
        """Test XML avec caractères spéciaux"""
        parser = XMLParser()
        
        special_xml = """<?xml version="1.0" encoding="UTF-8"?>
<logs>
  <log>
    <exercise>Développé couchéééé</exercise>
    <notes>Séance très difficile !!!</notes>
    <reps>10</reps>
  </log>
</logs>"""
        
        df = parser.parse_string(special_xml)
        assert not df.empty
        assert 'Développé couchéééé' in df.iloc[0]['exercise']

