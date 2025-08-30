"""
Démonstration complète de l'API Muscle-Analytics

Ce script montre comment utiliser tous les endpoints de l'API
pour récupérer et analyser les données d'entraînement.
"""

import requests
import json
import pandas as pd
from datetime import date, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any
import sys


class MuscleAnalyticsAPIDemo:
    """Démonstration de l'API Muscle-Analytics"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Effectue une requête à l'API avec gestion d'erreurs"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur API pour {endpoint}: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Erreur décodage JSON pour {endpoint}: {e}")
            return {}
    
    def demo_basic_data(self):
        """Démo des données de base"""
        print("📊 DONNÉES DE BASE")
        print("=" * 50)
        
        # Statut de l'API
        status = self._make_request("/status")
        if status:
            print(f"🟢 API Status: {status.get('api_status')}")
            print(f"🗄️ Base de données: {'✅ Connectée' if status.get('database_connected') else '❌ Déconnectée'}")
            print(f"📝 Sessions totales: {status.get('total_sessions', 0)}")
            print(f"💪 Exercices pratiqués: {status.get('total_exercises', 0)}")
            print()
        
        # Sessions récentes
        sessions = self._make_request("/sessions", {"limit": 10})
        if sessions:
            print(f"📝 Dernières sessions ({len(sessions)} trouvées):")
            for session in sessions[:5]:
                date_str = session.get('date', 'N/A')
                name = session.get('training_name', 'Sans nom')
                print(f"   {date_str}: {name}")
            print()
        
        # Exercices pratiqués
        exercises = self._make_request("/exercises/practiced")
        if exercises:
            print(f"💪 Exercices pratiqués ({len(exercises)} total):")
            for exercise in exercises[:10]:
                print(f"   • {exercise}")
            if len(exercises) > 10:
                print(f"   ... et {len(exercises) - 10} autres")
            print()
    
    def demo_volume_analytics(self):
        """Démo des analytics de volume"""
        print("📈 ANALYTICS DE VOLUME")
        print("=" * 50)
        
        volume_stats = self._make_request("/analytics/volume")
        if not volume_stats:
            print("❌ Aucune donnée de volume disponible")
            return
        
        # Tri par volume total
        volume_stats.sort(key=lambda x: x.get('total_volume', 0), reverse=True)
        
        print(f"🏋️ Top 10 exercices par volume total:")
        for i, stats in enumerate(volume_stats[:10], 1):
            exercise = stats.get('exercise', 'N/A')
            total_vol = stats.get('total_volume', 0)
            avg_vol = stats.get('avg_volume_per_set', 0)
            print(f"   {i:2d}. {exercise:<25} {total_vol:>8.1f}kg (moy: {avg_vol:>5.1f}kg/set)")
        
        print()
        
        # Analytics pour un exercice spécifique
        if volume_stats:
            top_exercise = volume_stats[0]['exercise']
            print(f"🎯 Analytics détaillées pour: {top_exercise}")
            
            # Volume par période
            today = date.today()
            last_month = today - timedelta(days=30)
            
            monthly_stats = self._make_request(
                "/analytics/volume", 
                {"exercise": top_exercise, "start_date": last_month.isoformat()}
            )
            
            if monthly_stats:
                stats = monthly_stats[0]
                print(f"   Volume dernier mois: {stats.get('total_volume', 0):.1f}kg")
                print(f"   Moyenne par set: {stats.get('avg_volume_per_set', 0):.1f}kg")
                print(f"   Moyenne par session: {stats.get('avg_volume_per_session', 0):.1f}kg")
        
        print()
    
    def demo_one_rm_analytics(self):
        """Démo des analytics de 1RM"""
        print("🎯 ANALYTICS DE 1RM")
        print("=" * 50)
        
        one_rm_stats = self._make_request("/analytics/one-rm")
        if not one_rm_stats:
            print("❌ Aucune donnée de 1RM disponible")
            return
        
        # Filtrer les exercices avec des données de 1RM
        valid_stats = [s for s in one_rm_stats if s.get('best_1rm_average')]
        
        if not valid_stats:
            print("❌ Aucun 1RM calculé disponible")
            return
        
        # Tri par 1RM moyen
        valid_stats.sort(key=lambda x: x.get('best_1rm_average', 0), reverse=True)
        
        print(f"💪 Top 10 exercices par 1RM estimé:")
        for i, stats in enumerate(valid_stats[:10], 1):
            exercise = stats.get('exercise', 'N/A')
            best_1rm = stats.get('best_1rm_average', 0)
            current_1rm = stats.get('current_1rm_average', 0)
            evolution = current_1rm - best_1rm if current_1rm and best_1rm else 0
            evolution_str = f"({evolution:+.1f}kg)" if evolution != 0 else ""
            
            print(f"   {i:2d}. {exercise:<25} {best_1rm:>6.1f}kg → {current_1rm:>6.1f}kg {evolution_str}")
        
        print()
        
        # Comparaison des formules pour le meilleur exercice
        if valid_stats:
            top_exercise = valid_stats[0]
            exercise_name = top_exercise['exercise']
            print(f"🧮 Comparaison des formules pour: {exercise_name}")
            
            formulas = ['epley', 'brzycki', 'lander', 'oconner']
            for formula in formulas:
                key = f'best_1rm_{formula}'
                value = top_exercise.get(key)
                if value:
                    print(f"   {formula.capitalize():<10}: {value:>6.1f}kg")
        
        print()
    
    def demo_progression_analytics(self):
        """Démo des analytics de progression"""
        print("📊 ANALYTICS DE PROGRESSION")
        print("=" * 50)
        
        progression_stats = self._make_request("/analytics/progression")
        if not progression_stats:
            print("❌ Aucune donnée de progression disponible")
            return
        
        # Tri par nombre de sessions
        progression_stats.sort(key=lambda x: x.get('total_sessions', 0), reverse=True)
        
        print(f"🔄 Progression par exercice:")
        for stats in progression_stats[:15]:
            exercise = stats.get('exercise', 'N/A')
            sessions = stats.get('total_sessions', 0)
            trend = stats.get('progression_trend', 'N/A')
            plateau = "🔴 PLATEAU" if stats.get('plateau_detected') else "🟢 Progression"
            days_since_pr = stats.get('days_since_last_pr')
            
            trend_str = f"({trend})" if trend and trend != 'N/A' else ""
            pr_str = f" - {days_since_pr}j depuis PR" if days_since_pr else ""
            
            print(f"   {exercise:<25} {sessions:>3} sessions {plateau} {trend_str}{pr_str}")
        
        print()
        
        # Résumé des plateaux
        plateaus = [s for s in progression_stats if s.get('plateau_detected')]
        if plateaus:
            print(f"⚠️ Plateaux détectés ({len(plateaus)} exercices):")
            for stats in plateaus:
                exercise = stats.get('exercise', 'N/A')
                days = stats.get('days_since_last_pr', 'N/A')
                print(f"   • {exercise} (dernier PR: il y a {days} jours)")
        else:
            print("🎉 Aucun plateau détecté - belle progression!")
        
        print()
    
    def demo_dashboard(self):
        """Démo du dashboard"""
        print("🎛️ DASHBOARD PRINCIPAL")
        print("=" * 50)
        
        dashboard = self._make_request("/analytics/dashboard")
        if not dashboard:
            print("❌ Données du dashboard indisponibles")
            return
        
        # Métriques principales
        print("📊 MÉTRIQUES PRINCIPALES")
        print(f"   Sessions totales: {dashboard.get('total_sessions', 0)}")
        print(f"   Exercices pratiqués: {dashboard.get('total_exercises', 0)}")
        print(f"   Volume cette semaine: {dashboard.get('total_volume_this_week', 0):.1f}kg")
        print(f"   Volume ce mois: {dashboard.get('total_volume_this_month', 0):.1f}kg")
        print()
        
        # Sessions récentes
        recent_sessions = dashboard.get('recent_sessions', [])
        if recent_sessions:
            print("📝 SESSIONS RÉCENTES")
            for session in recent_sessions:
                date_str = session.get('date', 'N/A')
                name = session.get('training_name', 'Sans nom')
                print(f"   {date_str}: {name}")
            print()
        
        # Top exercices
        top_exercises = dashboard.get('top_exercises_by_volume', [])
        if top_exercises:
            print("🏆 TOP EXERCICES (volume)")
            for i, exercise in enumerate(top_exercises[:5], 1):
                name = exercise.get('exercise', 'N/A')
                volume = exercise.get('total_volume', 0)
                print(f"   {i}. {name}: {volume:.1f}kg")
            print()
        
        # Alertes plateaux
        plateaus = dashboard.get('exercises_with_plateau', [])
        if plateaus:
            print(f"⚠️ ALERTES PLATEAUX ({len(plateaus)} exercices)")
            for exercise in plateaus:
                print(f"   • {exercise}")
        else:
            print("🎉 Aucune alerte plateau")
        
        print()
    
    def demo_exercise_deep_dive(self):
        """Démo d'analyse approfondie d'un exercice"""
        print("🔍 ANALYSE APPROFONDIE D'EXERCICE")
        print("=" * 50)
        
        # Récupérer un exercice avec beaucoup de données
        volume_stats = self._make_request("/analytics/volume")
        if not volume_stats:
            print("❌ Aucune donnée disponible pour analyse")
            return
        
        # Prendre l'exercice avec le plus de volume
        top_exercise = max(volume_stats, key=lambda x: x.get('total_volume', 0))
        exercise_name = top_exercise['exercise']
        
        print(f"🎯 Exercice analysé: {exercise_name}")
        print()
        
        # Analytics complètes
        analytics = self._make_request(f"/analytics/exercise/{exercise_name}")
        if not analytics:
            print("❌ Analytics détaillées indisponibles")
            return
        
        # Volume
        vol_stats = analytics.get('volume_stats', {})
        print("📈 VOLUME")
        print(f"   Total: {vol_stats.get('total_volume', 0):.1f}kg")
        print(f"   Moyenne par set: {vol_stats.get('avg_volume_per_set', 0):.1f}kg")
        print(f"   Moyenne par session: {vol_stats.get('avg_volume_per_session', 0):.1f}kg")
        print()
        
        # 1RM
        one_rm_stats = analytics.get('one_rm_stats', {})
        if one_rm_stats.get('best_1rm_average'):
            print("🎯 1RM ESTIMÉ")
            print(f"   Meilleur: {one_rm_stats.get('best_1rm_average', 0):.1f}kg")
            print(f"   Actuel: {one_rm_stats.get('current_1rm_average', 0):.1f}kg")
            
            # Détail par formule
            formulas = ['epley', 'brzycki', 'lander', 'oconner']
            for formula in formulas:
                key = f'best_1rm_{formula}'
                value = one_rm_stats.get(key)
                if value:
                    print(f"     {formula.capitalize()}: {value:.1f}kg")
            print()
        
        # Progression
        prog_stats = analytics.get('progression_stats', {})
        print("📊 PROGRESSION")
        print(f"   Sessions totales: {prog_stats.get('total_sessions', 0)}")
        print(f"   Tendance: {prog_stats.get('progression_trend', 'N/A')}")
        
        if prog_stats.get('plateau_detected'):
            days = prog_stats.get('days_since_last_pr', 'N/A')
            print(f"   ⚠️ Plateau détecté (dernier PR: il y a {days} jours)")
        else:
            print("   🟢 Progression normale")
        
        print()
        
        # Données temporelles si disponibles
        today = date.today()
        last_3_months = today - timedelta(days=90)
        
        sets_data = self._make_request(
            "/sets", 
            {"exercise": exercise_name, "start_date": last_3_months.isoformat()}
        )
        
        if sets_data:
            print(f"📅 HISTORIQUE (3 derniers mois)")
            print(f"   Sets effectués: {len(sets_data)}")
            
            # Analyse des poids
            weights = [s.get('weight_kg') for s in sets_data if s.get('weight_kg')]
            if weights:
                weights = [float(w) for w in weights]
                print(f"   Poids min/max: {min(weights):.1f}kg - {max(weights):.1f}kg")
                print(f"   Poids moyen: {sum(weights)/len(weights):.1f}kg")
            
            # Analyse des répétitions
            reps = [s.get('reps') for s in sets_data if s.get('reps')]
            if reps:
                print(f"   Répétitions min/max: {min(reps)} - {max(reps)}")
                print(f"   Répétitions moyennes: {sum(reps)/len(reps):.1f}")
        
        print()
    
    def run_complete_demo(self):
        """Lance la démonstration complète"""
        print("🎯 DÉMONSTRATION COMPLÈTE - API MUSCLE-ANALYTICS")
        print("=" * 60)
        print()
        
        # Vérification de la connexion
        health = self._make_request("/health")
        if not health or health.get('status') != 'healthy':
            print("❌ API non disponible. Vérifiez que l'API est démarrée.")
            print("   Commande: python run_api.py")
            return False
        
        print("✅ API disponible et fonctionnelle")
        print()
        
        # Exécuter toutes les démos
        demos = [
            self.demo_basic_data,
            self.demo_volume_analytics,
            self.demo_one_rm_analytics,
            self.demo_progression_analytics,
            self.demo_dashboard,
            self.demo_exercise_deep_dive
        ]
        
        for demo in demos:
            try:
                demo()
            except Exception as e:
                print(f"❌ Erreur dans {demo.__name__}: {e}")
                print()
        
        print("🎉 Démonstration terminée!")
        print("📚 Pour plus d'informations, consultez: http://localhost:8000/docs")
        
        return True


def main():
    """Fonction principale"""
    # URL de base (peut être modifiée via argument)
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    demo = MuscleAnalyticsAPIDemo(base_url)
    success = demo.run_complete_demo()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
