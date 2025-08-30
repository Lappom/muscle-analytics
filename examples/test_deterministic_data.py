#!/usr/bin/env python3
"""Test simple du générateur de données déterministes."""

import sys
import os

# Ajouter le chemin projet
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(project_root)

from demo_advanced_features import create_sample_data

print("=== Test du générateur de données déterministes ===")
print()

# Test 1: Générer les données
print("1. Génération des données...")
df = create_sample_data()

print(f"Nombre d'enregistrements: {len(df)}")
print(f"Exercices: {list(df['exercise'].unique())}")
print(f"Sessions: {df['session_id'].nunique()}")
print(f"Types de séries: {list(df['series_type'].unique())}")
print()

# Test 2: Vérifier la reproductibilité
print("2. Test de reproductibilité...")
df2 = create_sample_data()
is_identical = df.equals(df2)
print(f"Les données sont identiques: {is_identical}")
print()

# Test 3: Afficher un échantillon
print("3. Échantillon des données:")
sample = df.head(10)[['session_id', 'exercise', 'reps', 'weight_kg', 'series_type']]
print(sample.to_string(index=False))
print()

# Test 4: Vérifier la progression
print("4. Vérification de la progression (Bench Press):")
bench_data = df[df['exercise'] == 'Bench Press'].head(12)
for _, row in bench_data.iterrows():
    print(f"Session {row['session_id']}: {row['weight_kg']}kg x {row['reps']} reps")

print("\n✅ Tests terminés avec succès!")
