#!/usr/bin/env python3
"""
Script de nettoyage de l'arborescence du projet Muscle-Analytics

Ce script supprime automatiquement les fichiers et dossiers générés 
automatiquement qui ne doivent pas être versionnés.

Usage:
    python scripts/clean_project.py [--dry-run]
    
Options:
    --dry-run  Affiche ce qui serait supprimé sans effectuer la suppression
"""

import os
import shutil
import argparse
from pathlib import Path
import glob


def get_project_root():
    """Retourne le dossier racine du projet"""
    return Path(__file__).parent.parent


def find_pycache_dirs(root_path):
    """Trouve tous les dossiers __pycache__ (sauf dans .venv)"""
    pycache_dirs = []
    for root, dirs, files in os.walk(root_path):
        # Ignorer .venv
        if '.venv' in root or '.git' in root:
            continue
        if '__pycache__' in dirs:
            pycache_dirs.append(os.path.join(root, '__pycache__'))
    return pycache_dirs


def find_temp_files(root_path):
    """Trouve les fichiers temporaires à supprimer"""
    temp_patterns = [
        '**/*.pyc',
        '**/*.pyo', 
        '**/*.pyd',
        '**/.*~',
        '**/*.log',
        '**/.DS_Store',
        '**/Thumbs.db',
        '**/desktop.ini'
    ]
    
    temp_files = []
    for pattern in temp_patterns:
        matches = glob.glob(str(root_path / pattern), recursive=True)
        # Filtrer pour exclure .venv et .git
        filtered_matches = [
            f for f in matches 
            if '.venv' not in f and '.git' not in f
        ]
        temp_files.extend(filtered_matches)
    
    return temp_files


def find_coverage_files(root_path):
    """Trouve les fichiers de couverture de tests"""
    coverage_patterns = [
        '.coverage*',
        'htmlcov/',
        '.pytest_cache/',
        '.tox/',
        '.cache/'
    ]
    
    coverage_items = []
    for pattern in coverage_patterns:
        matches = glob.glob(str(root_path / pattern))
        coverage_items.extend(matches)
    
    return coverage_items


def clean_project(dry_run=False):
    """Nettoie le projet"""
    root_path = get_project_root()
    
    print(f"🧹 Nettoyage du projet: {root_path}")
    print("=" * 60)
    
    # 1. Dossiers __pycache__
    pycache_dirs = find_pycache_dirs(root_path)
    if pycache_dirs:
        print(f"\n📁 Dossiers __pycache__ trouvés: {len(pycache_dirs)}")
        for dir_path in pycache_dirs:
            rel_path = os.path.relpath(dir_path, root_path)
            if dry_run:
                print(f"   [DRY-RUN] Supprimerait: {rel_path}")
            else:
                try:
                    shutil.rmtree(dir_path)
                    print(f"   ✅ Supprimé: {rel_path}")
                except Exception as e:
                    print(f"   ❌ Erreur sur {rel_path}: {e}")
    
    # 2. Fichiers temporaires
    temp_files = find_temp_files(root_path)
    if temp_files:
        print(f"\n📄 Fichiers temporaires trouvés: {len(temp_files)}")
        for file_path in temp_files:
            rel_path = os.path.relpath(file_path, root_path)
            if dry_run:
                print(f"   [DRY-RUN] Supprimerait: {rel_path}")
            else:
                try:
                    os.remove(file_path)
                    print(f"   ✅ Supprimé: {rel_path}")
                except Exception as e:
                    print(f"   ❌ Erreur sur {rel_path}: {e}")
    
    # 3. Fichiers de couverture
    coverage_items = find_coverage_files(root_path)
    if coverage_items:
        print(f"\n📊 Fichiers/dossiers de couverture trouvés: {len(coverage_items)}")
        for item_path in coverage_items:
            rel_path = os.path.relpath(item_path, root_path)
            if dry_run:
                print(f"   [DRY-RUN] Supprimerait: {rel_path}")
            else:
                try:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                    print(f"   ✅ Supprimé: {rel_path}")
                except Exception as e:
                    print(f"   ❌ Erreur sur {rel_path}: {e}")
    
    # Résumé
    total_items = len(pycache_dirs) + len(temp_files) + len(coverage_items)
    if total_items == 0:
        print("\n🎉 Projet déjà propre ! Aucun fichier à nettoyer.")
    else:
        action = "seraient supprimés" if dry_run else "ont été supprimés"
        print(f"\n📋 Résumé: {total_items} éléments {action}")
        if dry_run:
            print("💡 Exécutez sans --dry-run pour effectuer le nettoyage")


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="Nettoie l'arborescence du projet")
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Affiche ce qui serait supprimé sans effectuer la suppression"
    )
    
    args = parser.parse_args()
    
    try:
        clean_project(dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\n\n⏹️ Nettoyage interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du nettoyage: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
