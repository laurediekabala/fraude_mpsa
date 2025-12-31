import joblib
import os 

# Utilisation de os.path.dirname(__file__) pour un chemin relatif fiable
shap_filename = "shap.joblib"
filename = os.path.join(os.path.dirname(__file__), "..", shap_filename)

def shap_loader():
    if not os.path.exists(filename):
        raise FileNotFoundError(f"❌ Le fichier SHAP est introuvable à l'emplacement : {filename}")

    try:
        shap = joblib.load(filename)
        print(f"✅ Fichier SHAP chargé avec succès depuis {filename}")
        return shap
    except Exception as e:
        print(f"❌ Erreur lors du chargement : {e}")
        return None