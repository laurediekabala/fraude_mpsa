import joblib
import os

# Utilisation de os.path.dirname(__file__) pour un chemin relatif fiable
# Cela fonctionne peu importe le répertoire depuis lequel on exécute le script
pipeline_filename = "model_xboost.joblib"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", pipeline_filename)

def load_pipeline():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"❌ Le pipeline est introuvable à l'emplacement : {MODEL_PATH}")
    
    try:
        model = joblib.load(MODEL_PATH)
        print(f"✅ Modèle chargé avec succès depuis {MODEL_PATH}")
        return model
    except Exception as e:
        print(f"❌ Erreur lors du chargement : {e}")
        return None

