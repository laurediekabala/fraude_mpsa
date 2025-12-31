"""
Script pour monitorer le drift en temps réel
Affiche un dashboard simple avec les statistiques de drift
"""

import requests
import json
import time
from datetime import datetime

class DriftMonitor:
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
        self.drift_history = []
        
    def check_drift_status(self):
        """Vérifier l'état du drift"""
        try:
            response = requests.get(f"{self.api_url}/drift/summary")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_baseline_info(self):
        """Récupérer les infos de la baseline"""
        status = self.check_drift_status()
        
        if "error" in status:
            print("❌ Erreur: Impossible de contacter l'API")
            return None
        
        if status.get("status") == "NO_BASELINE":
            print("⚠️  Aucune baseline disponible")
            print("   Créez une baseline d'abord avec:")
            print("   python upload_training_data.py 'E:\\pipeline\\MPSA.csv'")
            return None
        
        return {
            "status": "✅ Baseline disponible",
            "created": status.get("baseline_created", "N/A"),
            "samples": status.get("baseline_samples", "N/A"),
            "features": status.get("features", [])
        }
    
    def simulate_drift_detection(self, transaction_data):
        """
        Simuler la détection de drift pour une transaction
        
        Args:
            transaction_data: Dict avec les features de la transaction
        
        Returns:
            Rapport de drift
        """
        try:
            response = requests.post(
                f"{self.api_url}/drift/check",
                json=transaction_data
            )
            report = response.json()
            
            # Stocker dans l'historique
            self.drift_history.append({
                "timestamp": datetime.now().isoformat(),
                "drift_detected": report.get("overall_drift", False),
                "drift_percentage": report.get("drift_percentage", 0),
                "affected_features": report.get("drift_count", 0)
            })
            
            return report
        except Exception as e:
            return {"error": str(e)}
    
    def print_dashboard(self):
        """Afficher un dashboard simplifié"""
        baseline = self.get_baseline_info()
        
        if not baseline:
            return
        
        print("\n" + "="*60)
        print("📊 DRIFT DETECTION DASHBOARD")
        print("="*60)
        
        print(f"\n{baseline['status']}")
        print(f"  📅 Créée le: {baseline['created']}")
        print(f"  📈 Échantillons baseline: {baseline['samples']}")
        print(f"  ✨ Features: {len(baseline['features'])} détectées")
        
        if self.drift_history:
            print(f"\n📋 Historique Drift ({len(self.drift_history)} checks):")
            
            total_drifts = sum(1 for h in self.drift_history if h['drift_detected'])
            avg_drift_pct = sum(h['drift_percentage'] for h in self.drift_history) / len(self.drift_history)
            
            print(f"  🔴 Drifts détectés: {total_drifts}/{len(self.drift_history)}")
            print(f"  📊 Drift moyen: {avg_drift_pct:.1f}%")
            
            # Afficher les 5 derniers
            print(f"\n  5 derniers checks:")
            for h in self.drift_history[-5:]:
                status = "🔴 DRIFT" if h['drift_detected'] else "🟢 OK"
                print(f"    {h['timestamp']} - {status} ({h['drift_percentage']:.1f}%)")
        
        print("\n" + "="*60 + "\n")


def example_usage():
    """Exemple d'utilisation"""
    
    monitor = DriftMonitor()
    
    # Afficher l'état actuel
    print("\n🔍 Vérification de l'état du drift...\n")
    monitor.print_dashboard()
    
    # Exemples de transactions
    sample_transactions = [
        {
            "step": 100,
            "type": "TRANSFER",
            "amount": 5000,
            "oldbalanceOrg": 50000,
            "newbalanceOrig": 45000,
            "oldbalanceDest": 10000,
            "newbalanceDest": 15000,
            "hour": 10,
            "erreur_orig": 0.0,
            "erreur_dst": 0.0,
            "videur_orig": 0,
            "videur_dest": 0
        },
        {
            "step": 101,
            "type": "PAYMENT",
            "amount": 2000,  # Montant faible
            "oldbalanceOrg": 30000,
            "newbalanceOrig": 28000,
            "oldbalanceDest": 0,
            "newbalanceDest": 2000,
            "hour": 14,
            "erreur_orig": 0.0,
            "erreur_dst": 0.0,
            "videur_orig": 0,
            "videur_dest": 1
        },
        {
            "step": 102,
            "type": "TRANSFER",
            "amount": 100000,  # Montant très élevé - POSSIBLE DRIFT
            "oldbalanceOrg": 200000,
            "newbalanceOrig": 100000,
            "oldbalanceDest": 50000,
            "newbalanceDest": 150000,
            "hour": 2,  # Heure inhabituelle
            "erreur_orig": 0.0,
            "erreur_dst": 0.0,
            "videur_orig": 0,
            "videur_dest": 0
        }
    ]
    
    print("📊 Simulation: Vérification de 3 transactions...\n")
    
    for i, transaction in enumerate(sample_transactions, 1):
        print(f"Transaction {i}:")
        print(f"  Amount: {transaction['amount']}, Type: {transaction['type']}")
        
        report = monitor.simulate_drift_detection(transaction)
        
        if "error" in report:
            print(f"  ❌ Erreur: {report['error']}")
        else:
            drift = report.get('overall_drift', False)
            status = "🔴 DRIFT DÉTECTÉ" if drift else "🟢 Pas de drift"
            print(f"  {status}")
            print(f"  Drift: {report.get('drift_percentage', 0):.1f}%")
            
            # Afficher les features avec drift
            affected = []
            for feat_name, feat_info in report.get('features', {}).items():
                if feat_info.get('drift') and 'error' not in feat_info:
                    p_val = feat_info.get('p_value', 1.0)
                    affected.append(f"{feat_name} (p={p_val:.4f})")
            
            if affected:
                print(f"  ⚠️  Features affectées: {', '.join(affected[:3])}")
        
        print()
    
    # Afficher le dashboard final
    print("\n")
    monitor.print_dashboard()


if __name__ == "__main__":
    # Vérifie que Flask est actif
    print("🚀 Vérification de connexion à l'API Flask...\n")
    
    monitor = DriftMonitor()
    baseline = monitor.get_baseline_info()
    
    if baseline:
        print("✅ Connexion OK!\n")
        # Lancer l'exemple
        example_usage()
    else:
        print("\n⚠️  Flask n'est pas actif ou baseline pas créée")
        print("\nCommandes pour démarrer:")
        print("1. Terminal 1 - Démarrer Flask:")
        print("   cd e:\\fraude_mpsa")
        print("   python api_flask/app.py")
        print("\n2. Terminal 2 - Uploader les données:")
        print("   cd e:\\fraude_mpsa")
        print("   python upload_training_data.py 'E:\\pipeline\\MPSA.csv' --max-rows 10000")
        print("\n3. Terminal 3 - Lancer ce script:")
        print("   python drift_monitor.py")
