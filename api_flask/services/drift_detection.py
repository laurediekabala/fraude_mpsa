import numpy as np
import pandas as pd
from scipy.stats import ks_2samp, chi2_contingency
import os
import json
from datetime import datetime

class DriftDetector:
    """
    Détecte le Data Drift en comparant les distributions actuelles 
    avec les distributions de base (baseline).
    """
    
    def __init__(self, baseline_file="drift_baseline.json"):
        self.baseline_file = os.path.join(os.path.dirname(__file__), "..", baseline_file)
        self.baseline = self.load_baseline()
        self.predictions_buffer = []
        self.drift_threshold = 0.05  # seuil p-value pour détecter drift
        
    def load_baseline(self):
        """Charge la baseline (données de référence)"""
        if os.path.exists(self.baseline_file):
            try:
                with open(self.baseline_file, 'r') as f:
                    content = f.read().strip()
                    if not content:  # Fichier vide
                        print(f"⚠️ Fichier baseline vide: {self.baseline_file}")
                        return None
                    return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"⚠️ Fichier baseline corrompu: {e}")
                return None
            except Exception as e:
                print(f"⚠️ Erreur lors du chargement de la baseline: {e}")
                return None
        else:
            print(f"ℹ️ Aucune baseline trouvée. Chemin attendu: {self.baseline_file}")
            return None
    
    def save_baseline(self, baseline):
        """Sauvegarde la baseline"""
        with open(self.baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2, default=str)
        self.baseline = baseline
    
    def create_baseline(self, data_list):
        """Crée une baseline à partir d'une liste de données"""
        if len(data_list) == 0:
            return None
        
        df = pd.DataFrame(data_list)
        baseline = {}
        
        for column in df.columns:
            col_data = df[column]
            
            # Pour les colonnes numériques
            if pd.api.types.is_numeric_dtype(col_data):
                baseline[column] = {
                    'type': 'numeric',
                    'mean': float(col_data.mean()),
                    'std': float(col_data.std()),
                    'min': float(col_data.min()),
                    'max': float(col_data.max()),
                    'q25': float(col_data.quantile(0.25)),
                    'q50': float(col_data.quantile(0.50)),
                    'q75': float(col_data.quantile(0.75))
                }
            else:
                # Pour les colonnes catégoriques
                baseline[column] = {
                    'type': 'categorical',
                    'distribution': col_data.value_counts().to_dict()
                }
        
        baseline['timestamp'] = datetime.now().isoformat()
        baseline['n_samples'] = len(df)
        
        return baseline
    
    def detect_numeric_drift(self, column_name, current_values, baseline_stats):
        """
        Détecte le drift pour une colonne numérique 
        en utilisant le test Kolmogorov-Smirnov
        """
        if len(current_values) == 0:
            return {'drift': False, 'p_value': 1.0, 'alert': 'Pas assez de données'}
        
        # Créer une distribution théorique basée sur la baseline
        baseline_mean = baseline_stats['mean']
        baseline_std = baseline_stats['std']
        
        # Test KS: compare deux distributions
        baseline_dist = np.random.normal(baseline_mean, baseline_std, 1000)
        statistic, p_value = ks_2samp(current_values, baseline_dist)
        
        drift_detected = bool(p_value < self.drift_threshold)
        
        return {
            'drift': drift_detected,
            'p_value': float(p_value),
            'statistic': float(statistic),
            'baseline_mean': float(baseline_mean),
            'current_mean': float(np.mean(current_values)),
            'baseline_std': float(baseline_std),
            'current_std': float(np.std(current_values)),
            'type': 'numeric',
            'alert': 'DRIFT DÉTECTÉ ⚠️' if drift_detected else 'Pas de drift'
        }
    
    def detect_categorical_drift(self, column_name, current_values, baseline_dist):
        """
        Détecte le drift pour une colonne catégorique
        en utilisant le test du Chi-carré
        """
        if len(current_values) == 0:
            return {'drift': False, 'p_value': 1.0, 'alert': 'Pas assez de données'}
        
        # Créer une table de contingence
        current_dist = pd.Series(current_values).value_counts().to_dict()
        
        # Aligner les catégories
        all_categories = set(list(baseline_dist.keys()) + list(current_dist.keys()))
        baseline_counts = [baseline_dist.get(cat, 0) for cat in sorted(all_categories)]
        current_counts = [current_dist.get(cat, 0) for cat in sorted(all_categories)]
        
        # Éviter les divisions par zéro
        baseline_counts = [max(c, 1) for c in baseline_counts]
        current_counts = [max(c, 1) for c in current_counts]
        
        # Test du chi-carré
        chi2, p_value, dof, expected = chi2_contingency([baseline_counts, current_counts])
        
        drift_detected = bool(p_value < self.drift_threshold)
        
        return {
            'drift': drift_detected,
            'p_value': float(p_value),
            'chi2': float(chi2),
            'baseline_dist': baseline_dist,
            'current_dist': current_dist,
            'type': 'categorical',
            'alert': 'DRIFT DÉTECTÉ ⚠️' if drift_detected else 'Pas de drift'
        }
    
    def check_drift(self, data: dict):
        """
        Vérifie le drift pour un nouvel enregistrement
        Retourne un rapport de drift pour chaque colonne
        """
        if self.baseline is None:
            return {
                'status': 'NO_BASELINE',
                'message': 'Pas de baseline. Créez d\'abord une baseline avec des données d\'entraînement.',
                'overall_drift': False
            }
        
        drift_report = {
            'timestamp': datetime.now().isoformat(),
            'features': {},
            'overall_drift': False,
            'drift_count': 0,
            'total_features': 0
        }
        
        for column, value in data.items():
            if column not in self.baseline:
                continue
            
            baseline_info = self.baseline[column]
            drift_report['total_features'] += 1
            
            try:
                if baseline_info['type'] == 'numeric':
                    result = self.detect_numeric_drift(
                        column, 
                        [value], 
                        baseline_info
                    )
                else:  # categorical
                    result = self.detect_categorical_drift(
                        column, 
                        [value], 
                        baseline_info['distribution']
                    )
                
                drift_report['features'][column] = result
                
                if result['drift']:
                    drift_report['drift_count'] += 1
                    drift_report['overall_drift'] = bool(True)  # Convertir explicitement en bool
                    
            except Exception as e:
                drift_report['features'][column] = {
                    'error': str(e),
                    'drift': False
                }
        
        # Calculer un score de drift global (% de features avec drift)
        if drift_report['total_features'] > 0:
            drift_report['drift_percentage'] = float(
                drift_report['drift_count'] / drift_report['total_features'] * 100
            )
        else:
            drift_report['drift_percentage'] = 0.0
        
        # Convertir tous les bools en Python natifs
        drift_report['overall_drift'] = bool(drift_report['overall_drift'])
        
        return drift_report
    
    def get_drift_summary(self):
        """Retourne un résumé de l'état du drift"""
        if self.baseline is None:
            return {
                'status': 'NO_BASELINE',
                'message': 'Pas de baseline disponible'
            }
        
        return {
            'status': 'BASELINE_AVAILABLE',
            'baseline_created': self.baseline.get('timestamp'),
            'baseline_samples': self.baseline.get('n_samples'),
            'features': list(self.baseline.keys())
        }
