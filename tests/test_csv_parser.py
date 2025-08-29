"""
Tests unitaires pour le parser CSV.

Teste tous les cas limites et formats français.
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
from src.etl.csv_parser import CSVParser, CSVParserError


class TestCSVParser:
    """Tests pour la classe CSVParser"""
    
    @pytest.fixture
    def parser(self):
        """Instance du parser pour les tests"""
        return CSVParser()
    
    @pytest.fixture
    def sample_csv_content(self):
        """Contenu CSV d'exemple avec format français"""
        return """Date,Entraînement,Heure,Exercice,Région,Groupes musculaires (Primaires),Groupes musculaires (Secondaires),Série / Série d'échauffement / Série de récupération,Répétitions / Temps,Poids / Distance,Notes,Sautée
29/08/2025,"Pecs Dos 2",16:05,"Traction à la Barre Fixe",Dos,"Trapèzes, Muscles dorsaux","Biceps",Série,"13 répétitions","0,00 kg",,Non
30/08/2025,"Upper Body",09:00,"Développé couché",Pectoraux,"Pectoraux","Triceps",Principale,"8","75,5 kg","Forme parfaite",Non
31/08/2025,"Legs",14:30,"Squat",Jambes,"Quadriceps","Fessiers",Échauffement,"5","40,0 kg",,Oui"""
    
    @pytest.fixture
    def csv_file(self, sample_csv_content):
        """Fichier CSV temporaire pour les tests"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(sample_csv_content)
            f.flush()
            yield Path(f.name)
        # Cleanup
        Path(f.name).unlink(missing_ok=True)
    
    def test_parse_file_success(self, parser, csv_file):
        """Test parsing réussi d'un fichier CSV"""
        df = parser.parse_file(csv_file)
        
        assert not df.empty
        assert len(df) == 3
        assert 'date' in df.columns
        assert 'exercise' in df.columns
        assert 'weight' in df.columns
        assert 'reps' in df.columns
    
    def test_parse_file_not_found(self, parser):
        """Test parsing d'un fichier inexistant"""
        with pytest.raises(CSVParserError):
            parser.parse_file("nonexistent_file.csv")
    
    def test_parse_french_decimal(self, parser):
        """Test conversion des décimales françaises"""
        assert parser.parse_french_decimal("12,5") == 12.5
        assert parser.parse_french_decimal("0,00") == 0.0
        assert parser.parse_french_decimal("150,75") == 150.75
        assert parser.parse_french_decimal("") == 0.0
        assert parser.parse_french_decimal(None) == 0.0
    
    def test_parse_weight(self, parser):
        """Test parsing des poids avec unités"""
        assert parser.parse_weight("75,5 kg") == 75.5
        assert parser.parse_weight("0,00 kg") == 0.0
        assert parser.parse_weight("100 kilogrammes") == 100.0
        assert parser.parse_weight("80") == 80.0
        assert parser.parse_weight("") == 0.0
        assert parser.parse_weight(None) == 0.0
    
    def test_parse_reps(self, parser):
        """Test parsing des répétitions"""
        assert parser.parse_reps("12 répétitions") == 12
        assert parser.parse_reps("8") == 8
        assert parser.parse_reps("15 reps") == 15
        assert parser.parse_reps("") == 0
        assert parser.parse_reps(None) == 0
        assert parser.parse_reps("aucun nombre") == 0
    
    def test_parse_date(self, parser):
        """Test parsing des dates françaises"""
        date1 = parser.parse_date("29/08/2025")
        assert date1 is not None
        assert date1.year == 2025
        assert date1.month == 8
        assert date1.day == 29
        
        date2 = parser.parse_date("01-12-2024")
        assert date2 is not None
        assert date2.year == 2024
        
        assert parser.parse_date("") is None
        assert parser.parse_date(None) is None
        assert parser.parse_date("invalid") is None
    
    def test_parse_boolean(self, parser):
        """Test parsing des booléens français"""
        assert parser.parse_boolean("Oui") is True
        assert parser.parse_boolean("oui") is True
        assert parser.parse_boolean("Non") is False
        assert parser.parse_boolean("non") is False
        assert parser.parse_boolean("True") is True
        assert parser.parse_boolean("False") is False
        assert parser.parse_boolean("") is False
        assert parser.parse_boolean(None) is False
        assert parser.parse_boolean("invalid") is False
    
    def test_clean_text(self, parser):
        """Test nettoyage du texte"""
        # Test espaces insécables
        assert parser._clean_text("texte\u00a0avec\u00a0espaces") == "texte avec espaces"
        assert parser._clean_text("  texte  ") == "texte"
        assert parser._clean_text("") == ""
    
    def test_normalize_column_names(self, parser, csv_file):
        """Test normalisation des noms de colonnes"""
        df = parser.parse_file(csv_file)
        
        expected_columns = [
            'date', 'training', 'time', 'exercise', 'region',
            'muscles_primary', 'muscles_secondary', 'series_type',
            'reps', 'weight', 'notes', 'skipped'
        ]
        
        for col in expected_columns:
            assert col in df.columns
    
    def test_validate_required_columns(self, parser):
        """Test validation des colonnes obligatoires"""
        # DataFrame valide
        valid_df = pd.DataFrame({
            'date': ['2025-08-29'],
            'exercise': ['pull-up'],
            'reps': [10],
            'weight': [0.0]
        })
        
        # Ne doit pas lever d'exception
        parser._validate_required_columns(valid_df)
        
        # DataFrame invalide (manque 'exercise')
        invalid_df = pd.DataFrame({
            'date': ['2025-08-29'],
            'reps': [10],
            'weight': [0.0]
        })
        
        with pytest.raises(CSVParserError):
            parser._validate_required_columns(invalid_df)
    
    def test_edge_cases_decimal_parsing(self, parser):
        """Test cas limites pour le parsing des décimales"""
        # Espaces multiples
        assert parser.parse_french_decimal("  12,5  ") == 12.5
        
        # Espaces insécables
        assert parser.parse_french_decimal("12,5\u00a0kg") == 12.5
        
        # Nombres sans décimale
        assert parser.parse_french_decimal("100") == 100.0
        
        # Valeurs invalides
        assert parser.parse_french_decimal("abc") == 0.0
        assert parser.parse_french_decimal("12,5,5") == 12.5  # Prend la première partie valide
    
    def test_encoding_fallback(self, parser):
        """Test fallback d'encodage"""
        # Créer un fichier avec encodage spécial
        content_with_accents = """Date,Exercice
01/01/2025,Développé couchéééé"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='cp1252') as f:
            f.write(content_with_accents)
            f.flush()
            csv_path = Path(f.name)
        
        try:
            # Le parser devrait réussir avec le fallback
            df = parser.parse_file(csv_path)
            assert not df.empty
            assert 'exercise' in df.columns
        finally:
            csv_path.unlink(missing_ok=True)


class TestCSVParserIntegration:
    """Tests d'intégration pour le parser CSV"""
    
    def test_full_pipeline_with_sample_data(self):
        """Test du pipeline complet avec données d'exemple"""
        parser = CSVParser()
        
        # Données d'exemple complexes
        complex_csv = """Date,Entraînement,Heure,Exercice,Région,Groupes musculaires (Primaires),Groupes musculaires (Secondaires),Série / Série d'échauffement / Série de récupération,Répétitions / Temps,Poids / Distance,Notes,Sautée
29/08/2025,"Pecs Dos 2",16:05,"Traction à la Barre Fixe",Dos,"Trapèzes, Muscles dorsaux","Biceps",Série,"13 répétitions","0,00 kg","RAS",Non
30/08/2025,"Upper Body",09:00,"Développé couché",Pectoraux,"Pectoraux","Triceps",Principale,"8","75,5 kg","Forme parfaite",Non
31/08/2025,"Legs",14:30,"Squat",Jambes,"Quadriceps","Fessiers",Échauffement,"5","40,0 kg",,Oui
01/09/2025,Rest Day,,,,,,,,,Jour de repos,Oui"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(complex_csv)
            f.flush()
            csv_file = Path(f.name)
        
        try:
            df = parser.parse_file(csv_file)
            
            # Vérifications
            assert len(df) == 4
            assert df.iloc[0]['exercise'] == 'Traction à la Barre Fixe'
            assert df.iloc[1]['weight'] == '75,5 kg'
            assert df.iloc[2]['skipped'] == 'Oui'
            assert df.iloc[3]['exercise'] is None or pd.isna(df.iloc[3]['exercise'])
            
        finally:
            csv_file.unlink(missing_ok=True)