#!/usr/bin/env python3
"""
Script de nettoyage automatique du projet Muscle-Analytics.

Ce script identifie et supprime :
- Fichiers de démonstration inutiles
- Code dupliqué
- Fichiers de test obsolètes
- Fichiers temporaires
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Set


class ProjectCleaner:
    """Classe pour nettoyer automatiquement le projet"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.files_to_remove = set()
        self.duplicated_code = set()
        
    def find_demo_files(self) -> Set[Path]:
        """Trouve les fichiers de démonstration inutiles"""
        demo_patterns = [
            "demo_*.py",
            "sample_*.csv",
            "sample_*.xml",
            "test_*_fixed.py",
            "test_*_refactoring.py"
        ]
        
        demo_files = set()
        try:
            for pattern in demo_patterns:
                for file_path in self.project_root.rglob(pattern):
                    if file_path.is_file():
                        demo_files.add(file_path)
        except Exception as e:
            print(f"⚠️ Erreur lors de la recherche des fichiers de démonstration: {e}")
        
        return demo_files
    
    def find_duplicated_functions(self) -> Set[str]:
        """Identifie les fonctions potentiellement dupliquées"""
        function_patterns = [
            r"def _clean_text\(",
            r"def _safe_extract_\w+\(",
            r"def _calculate_1rm\(",
            r"def _display_\w+_detail\("
        ]
        
        duplicated = set()
        try:
            for pattern in function_patterns:
                matches = []
                for file_path in self.project_root.rglob("*.py"):
                    if file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if len(re.findall(pattern, content)) > 1:
                                    matches.append(str(file_path))
                        except Exception as e:
                            print(f"⚠️ Erreur lecture {file_path}: {e}")
                            continue
                
                if len(matches) > 1:
                    duplicated.add(f"Pattern {pattern}: {matches}")
        except Exception as e:
            print(f"⚠️ Erreur lors de la recherche de code dupliqué: {e}")
        
        return duplicated
    
    def find_unused_imports(self) -> Set[str]:
        """Identifie les imports potentiellement inutilisés"""
        # Cette fonction nécessiterait une analyse plus approfondie
        # avec un outil comme pyflakes ou pylint
        return set()
    
    def clean_pycache(self):
        """Supprime les dossiers __pycache__"""
        try:
            for pycache_dir in self.project_root.rglob("__pycache__"):
                if pycache_dir.is_dir():
                    try:
                        shutil.rmtree(pycache_dir)
                        print(f"✅ Supprimé: {pycache_dir}")
                    except Exception as e:
                        print(f"⚠️ Erreur suppression {pycache_dir}: {e}")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage pycache: {e}")
    
    def clean_coverage_reports(self):
        """Supprime les rapports de couverture de test"""
        try:
            coverage_dir = self.project_root / "htmlcov"
            if coverage_dir.exists() and coverage_dir.is_dir():
                try:
                    shutil.rmtree(coverage_dir)
                    print(f"✅ Supprimé: {coverage_dir}")
                except Exception as e:
                    print(f"⚠️ Erreur suppression {coverage_dir}: {e}")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage coverage: {e}")
    
    def clean_temp_files(self):
        """Supprime les fichiers temporaires"""
        temp_patterns = [
            "*.tmp",
            "*.temp",
            "*.log",
            "*.bak"
        ]
        
        try:
            for pattern in temp_patterns:
                for file_path in self.project_root.rglob(pattern):
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            print(f"✅ Supprimé: {file_path}")
                        except Exception as e:
                            print(f"⚠️ Erreur suppression {file_path}: {e}")
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage des fichiers temporaires: {e}")
    
    def generate_cleanup_report(self) -> str:
        """Génère un rapport de nettoyage"""
        report = []
        report.append("=== RAPPORT DE NETTOYAGE DU PROJET ===\n")
        
        # Fichiers de démonstration
        demo_files = self.find_demo_files()
        if demo_files:
            report.append(f"📁 Fichiers de démonstration trouvés: {len(demo_files)}")
            for file_path in sorted(demo_files):
                report.append(f"  - {file_path}")
        else:
            report.append("✅ Aucun fichier de démonstration trouvé")
        
        report.append("")
        
        # Code dupliqué
        duplicated = self.find_duplicated_functions()
        if duplicated:
            report.append(f"🔄 Patterns de code dupliqué trouvés: {len(duplicated)}")
            for pattern in duplicated:
                report.append(f"  - {pattern}")
        else:
            report.append("✅ Aucun code dupliqué détecté")
        
        report.append("")
        
        # Nettoyage effectué
        report.append("🧹 Nettoyage effectué:")
        self.clean_pycache()
        self.clean_coverage_reports()
        self.clean_temp_files()
        
        return "\n".join(report)
    
    def run_cleanup(self):
        """Exécute le nettoyage complet"""
        print("🧹 Début du nettoyage du projet...")
        print("=" * 50)
        
        try:
            report = self.generate_cleanup_report()
            print(report)
            
            print("\n" + "=" * 50)
            print("✅ Nettoyage terminé avec succès !")
            
        except Exception as e:
            print(f"\n❌ Erreur lors du nettoyage: {e}")
            print("Le script s'est arrêté prématurément.")


def main():
    """Fonction principale"""
    try:
        cleaner = ProjectCleaner()
        cleaner.run_cleanup()
    except KeyboardInterrupt:
        print("\n\n⏹️ Nettoyage interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")


if __name__ == "__main__":
    main()
