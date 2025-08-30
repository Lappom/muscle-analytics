"""
Test rapide de l'API containerisée
"""

import sys
import urllib.request
import json


def test_endpoint(url, endpoint_name):
    """Test d'un endpoint"""
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print(f"✅ {endpoint_name}: {response.status} - {data}")
            return True
    except Exception as e:
        print(f"❌ {endpoint_name}: Erreur - {e}")
        return False


def main():
    """Test de l'API containerisée"""
    base_url = "http://localhost:8000"
    
    print("🐳 Test de l'API Muscle-Analytics containerisée")
    print("=" * 50)
    
    tests = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/", "Root Endpoint"),
        (f"{base_url}/status", "Status"),
        (f"{base_url}/sessions", "Sessions"),
        (f"{base_url}/exercises/practiced", "Exercices pratiqués"),
        (f"{base_url}/analytics/dashboard", "Dashboard")
    ]
    
    results = []
    for url, name in tests:
        result = test_endpoint(url, name)
        results.append(result)
        print()
    
    print("=" * 50)
    print(f"📊 RÉSULTATS: {sum(results)}/{len(results)} tests réussis")
    
    if all(results):
        print("🎉 L'API containerisée fonctionne parfaitement !")
        print("🌐 Accès: http://localhost:8000")
        print("📚 Documentation: http://localhost:8000/docs")
    else:
        print("⚠️ Certains tests ont échoué")
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
