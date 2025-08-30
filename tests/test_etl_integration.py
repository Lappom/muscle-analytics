"""
Tests pour les scripts ETL et la base de données.
"""

import unittest
import pandas as pd
from datetime import date, datetime
from pathlib import Path
import tempfile
import os
import sys
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

# Ajout du chemin pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))  # Pour test_config

# Import du module ETL original + configuration unifiée
from etl.database import DatabaseManager, DatabaseError
from etl.import_scripts import ETLImporter
from etl.pipeline import ETLPipeline

# Import de la configuration unifiée
from database import get_database_config, DatabaseEnvironment


class TestDatabaseManager(unittest.TestCase):
    """Tests pour le gestionnaire de base de données"""
    
    def setUp(self):
        """Configuration des tests"""
        # Utilisation de la configuration sécurisée unifiée
        db_config = get_database_config(DatabaseEnvironment.TEST)
        self.db_manager = DatabaseManager(**db_config)
    
    def test_connection_params(self):
        """Test des paramètres de connexion"""
        # Test que les paramètres sont bien configurés (sans exposer les valeurs)
        self.assertIsNotNone(self.db_manager.connection_params.get('host'))
        self.assertIsNotNone(self.db_manager.connection_params.get('database'))
        self.assertIsNotNone(self.db_manager.connection_params.get('user'))
        self.assertIsNotNone(self.db_manager.connection_params.get('password'))
    
    def test_insert_session(self):
        """Test d'insertion de session"""
        # Note: Ce test nécessite une base de données de test
        try:
            session_id = self.db_manager.insert_session(
                date=date.today(),
                start_time="10:00",
                training_name="Test Session",
                notes="Session de test"
            )
            self.assertIsInstance(session_id, int)
            self.assertGreater(session_id, 0)
        except DatabaseError:
            self.skipTest("Base de données de test non disponible")
    
    def test_insert_exercise_catalog(self):
        """Test d'insertion dans le catalogue d'exercices"""
        try:
            result = self.db_manager.insert_exercise_catalog(
                name="Développé couché test",
                main_region="Pectoraux",
                muscles_primary=["Pectoraux"],
                muscles_secondary=["Triceps"]
            )
            self.assertTrue(result)
        except DatabaseError:
            self.skipTest("Base de données de test non disponible")


class TestETLImporter(unittest.TestCase):
    """Tests pour l'importateur ETL"""
    
    def setUp(self):
        """Configuration des tests"""
        # Créer un importer avec configuration sécurisée
        try:
            db_config = get_database_config(DatabaseEnvironment.TEST)
            db_manager = DatabaseManager(**db_config)
            
            # Tester la connexion
            if db_manager.test_connection():
                self.importer = ETLImporter(db_manager)
                self.has_database = True
                logger.info("Base de données de test connectée avec succès")
            else:
                # Créer un mock simple pour les tests
                self.importer = ETLImporter()
                self.has_database = False
                logger.warning("Base de données non disponible, utilisation de mocks pour les tests")
        except Exception as e:
            self.importer = ETLImporter()
            self.has_database = False
            logger.warning(f"Base de données non disponible ({e}), utilisation de mocks pour les tests")
    
    def test_filter_new_data(self):
        """
        Test du filtrage des nouvelles données
        
        Note: Ce test accède à une méthode privée (_filter_new_data) pour valider
        la logique de filtrage de façon isolée. Cette approche est justifiée car
        la logique de filtrage est complexe et critique pour l'import incrémental.
        """
        from datetime import date, timedelta
        
        # Utilisation de dates récentes pour le test
        today = date.today()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)
        
        # Création d'un DataFrame de test avec des dates récentes
        test_data = pd.DataFrame({
            'date': [two_days_ago.strftime('%Y-%m-%d'), 
                    yesterday.strftime('%Y-%m-%d'), 
                    today.strftime('%Y-%m-%d')],
            'exercise': ['Test1', 'Test2', 'Test3'],
            'reps': [10, 12, 8],
            'weight_kg': [50.0, 60.0, 70.0]
        })
        
        # Définir qu'une des dates existe déjà
        existing_dates = {two_days_ago}
        
        # Le filtrage doit garder seulement les nouvelles dates récentes
        filtered = self.importer._filter_new_data(test_data, existing_dates, 30)
        
        self.assertEqual(len(filtered), 2)  # 2 nouvelles dates
        self.assertNotIn(two_days_ago.strftime('%Y-%m-%d'), filtered['date'].values)
    
    def test_filter_new_data_with_reference_date(self):
        """Test du filtrage avec date de référence spécifique"""
        from datetime import date
        
        # Test avec date de référence spécifique
        reference_date = date(2024, 8, 31)
        
        # Création d'un DataFrame de test
        test_data = pd.DataFrame({
            'date': ['2024-08-29', '2024-08-30', '2024-08-31'],
            'exercise': ['Test1', 'Test2', 'Test3'],
            'reps': [10, 12, 8],
            'weight_kg': [50.0, 60.0, 70.0]
        })
        
        existing_dates = {date(2024, 8, 29)}
        
        # Test avec la méthode unifiée qui accepte une date de référence
        filtered = self.importer._filter_new_data(
            test_data, existing_dates, 30, reference_date
        )
        self.assertEqual(len(filtered), 2)  # 2 nouvelles dates
        self.assertNotIn('2024-08-29', filtered['date'].values)
    
    def test_incremental_import_filtering_integration(self):
        """
        Test d'intégration du filtrage via l'interface publique incremental_import
        
        Ce test valide que la fonctionnalité de filtrage fonctionne correctement
        à travers l'interface publique, comme suggéré par les bonnes pratiques de test.
        """
        import tempfile
        import os
        from datetime import date, timedelta
        
        # Création d'un fichier CSV temporaire pour le test
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        test_csv_content = f"""date,exercise,reps,weight_kg
{yesterday.strftime('%Y-%m-%d')},Squat,10,50.0
{today.strftime('%Y-%m-%d')},Bench Press,8,60.0
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(test_csv_content)
            temp_file = f.name
        
        try:
            # Mock la méthode get_existing_data_dates pour simuler des données existantes
            original_method = self.importer.db_manager.get_existing_data_dates
            self.importer.db_manager.get_existing_data_dates = lambda: [yesterday]
            
            # Mock bulk_insert_from_dataframe pour éviter l'insertion réelle
            inserted_data = []
            def mock_insert(df):
                inserted_data.append(df)
                return {'sessions_created': 1, 'sets_inserted': len(df)}
            
            self.importer.db_manager.bulk_insert_from_dataframe = mock_insert
            
            # Test de l'import incrémental
            result = self.importer.incremental_import(temp_file, days_threshold=30)
            
            # Vérifications
            self.assertTrue(result['success'])
            if inserted_data:
                # Seules les nouvelles données (aujourd'hui) doivent être importées
                self.assertEqual(len(inserted_data[0]), 1)
                self.assertEqual(inserted_data[0]['date'].iloc[0], today.strftime('%Y-%m-%d'))
            
            # Restore la méthode originale
            self.importer.db_manager.get_existing_data_dates = original_method
            
        finally:
            # Nettoyage du fichier temporaire
            os.unlink(temp_file)

    def test_generate_import_report(self):
        """Test de génération de rapport"""
        test_results = {
            'success': True,
            'message': 'Import réussi',
            'file': 'test.csv',
            'stats': {
                'sessions_created': 2,
                'sets_inserted': 10,
                'exercises_added': 5,
                'errors': 0,
                'total_rows': 10,
                'valid_sets': 10,
                'quality_percentage': 100.0
            }
        }
        
        report = self.importer.generate_import_report(test_results)
        
        self.assertIn('Import réussi', report)
        self.assertIn('Sessions créées: 2', report)
        self.assertIn('Séries insérées: 10', report)
        self.assertIn('100.0%', report)


class TestETLPipelineIntegration(unittest.TestCase):
    """Tests d'intégration du pipeline ETL"""
    
    def setUp(self):
        """Configuration des tests"""
        self.pipeline = ETLPipeline()
        self.test_dir = Path(__file__).parent.parent / 'examples'
    
    def test_process_sample_csv(self):
        """Test de traitement du fichier CSV d'exemple"""
        csv_file = self.test_dir / 'sample_data.csv'
        
        if csv_file.exists():
            df = self.pipeline.process_file(csv_file)
            
            self.assertFalse(df.empty)
            self.assertIn('exercise', df.columns)
            self.assertIn('reps', df.columns)
            self.assertIn('weight_kg', df.columns)
            self.assertIn('date', df.columns)
            
            # Vérification de la qualité
            quality = self.pipeline.validate_data_quality(df)
            self.assertIn('total_rows', quality)
            self.assertIn('valid_sets', quality)
            self.assertIn('quality_percentage', quality)
        else:
            self.skipTest("Fichier CSV d'exemple non trouvé")
    
    def test_process_sample_xml(self):
        """Test de traitement du fichier XML d'exemple"""
        xml_file = self.test_dir / 'sample_data.xml'
        
        if xml_file.exists():
            df = self.pipeline.process_file(xml_file)
            
            self.assertFalse(df.empty)
            self.assertIn('exercise', df.columns)
            self.assertIn('reps', df.columns)
            self.assertIn('weight_kg', df.columns)
            self.assertIn('date', df.columns)
        else:
            self.skipTest("Fichier XML d'exemple non trouvé")
    
    def test_multiple_files_processing(self):
        """Test de traitement de plusieurs fichiers"""
        if self.test_dir.exists():
            csv_files = list(self.test_dir.glob("*.csv"))
            xml_files = list(self.test_dir.glob("*.xml"))
            all_files = csv_files + xml_files
            
            if all_files:
                df = self.pipeline.process_multiple_files(all_files)
                
                if not df.empty:
                    self.assertIn('source_file', df.columns)
                    self.assertIn('exercise', df.columns)
                    
                    # Vérification que les données sont triées par date
                    if 'date' in df.columns:
                        dates = pd.to_datetime(df['date'], errors='coerce').dropna()
                        if len(dates) > 1:
                            self.assertTrue(dates.is_monotonic_increasing)
            else:
                self.skipTest("Aucun fichier d'exemple trouvé")
    
    def test_summary_report_generation(self):
        """Test de génération de rapport de synthèse"""
        # Création d'un DataFrame de test
        test_data = pd.DataFrame({
            'date': ['2024-08-29', '2024-08-30', '2024-08-31'],
            'exercise': ['Développé couché', 'Squat', 'Développé couché'],
            'reps': [8, 12, 6],
            'weight_kg': [70.0, 100.0, 75.0],
            'volume': [560.0, 1200.0, 450.0],
            'is_valid_set': [True, True, True],
            'skipped': [False, False, False]
        })
        
        report = self.pipeline.generate_summary_report(test_data)
        
        self.assertIn('RAPPORT DE SYNTHÈSE', report)
        self.assertIn('Total d\'enregistrements: 3', report)
        self.assertIn('Volume total: 2210.0 kg', report)
        self.assertIn('Développé couché', report)


class TestDataValidation(unittest.TestCase):
    """Tests de validation des données"""
    
    def setUp(self):
        """Configuration des tests"""
        self.pipeline = ETLPipeline()
    
    def test_data_quality_validation(self):
        """Test de validation de la qualité des données"""
        # DataFrame avec différents types de problèmes
        test_data = pd.DataFrame({
            'exercise': ['Développé couché', 'unknown', 'Squat', None],
            'reps': [8, 0, 12, 10],
            'weight_kg': [70.0, -5.0, 100.0, 80.0],
            'date': ['2024-08-29', None, '2024-08-30', '2024-08-31'],
            'is_valid_set': [True, False, True, True],
            'skipped': [False, False, True, False]
        })
        
        quality = self.pipeline.validate_data_quality(test_data)
        
        self.assertEqual(quality['total_rows'], 4)
        self.assertEqual(quality['valid_sets'], 3)
        self.assertEqual(quality['missing_dates'], 1)
        self.assertEqual(quality['missing_exercises'], 2)  # 'unknown' + None
        self.assertEqual(quality['invalid_weights'], 1)    # -5.0
        self.assertEqual(quality['invalid_reps'], 1)       # 0
        self.assertEqual(quality['skipped_sets'], 1)
        
        # Vérification du pourcentage de qualité
        expected_percentage = (3 / 4) * 100  # 75%
        self.assertEqual(quality['quality_percentage'], expected_percentage)
    
    def test_empty_dataframe_validation(self):
        """Test de validation d'un DataFrame vide"""
        empty_df = pd.DataFrame()
        
        quality = self.pipeline.validate_data_quality(empty_df)
        
        self.assertEqual(quality['total_rows'], 0)
        self.assertEqual(quality['valid_sets'], 0)
        self.assertEqual(quality['quality_percentage'], 0.0)


def run_tests():
    """Exécute tous les tests"""
    # Configuration du logging pour les tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Réduire le bruit pendant les tests
    
    # Création de la suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajout des tests
    test_suite.addTest(unittest.makeSuite(TestETLImporter))
    test_suite.addTest(unittest.makeSuite(TestETLPipelineIntegration))
    test_suite.addTest(unittest.makeSuite(TestDataValidation))
    
    # Tests de base de données seulement si disponible
    try:
        db_config = get_database_config(DatabaseEnvironment.TEST)
        db_manager = DatabaseManager(**db_config)
        if db_manager.test_connection():
            test_suite.addTest(unittest.makeSuite(TestDatabaseManager))
            print("✅ Tests de base de données inclus")
        else:
            print("⚠️  Tests de base de données ignorés (connexion échouée)")
    except Exception as e:
        print(f"⚠️  Tests de base de données ignorés (erreur: {e})")
    
    # Exécution des tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
