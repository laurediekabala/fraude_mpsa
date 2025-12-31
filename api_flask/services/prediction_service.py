import pandas as pd
from core.pipeline_utils import load_pipeline

pipeline = load_pipeline()

def predict_instance(data: dict):
    try:
        X = pd.DataFrame([data])
        # Vérifier si c'est un pipeline sklearn ou un modèle simple
        if hasattr(pipeline, 'steps'):
            # C'est un sklearn Pipeline
            proba = pipeline.predict_proba(X)[0, 1]
        elif hasattr(pipeline, 'predict_proba'):
            # C'est un modèle avec predict_proba directement
            proba = pipeline.predict_proba(X)[0, 1]
        else:
            raise ValueError("Le modèle n'a pas la méthode predict_proba")
        return float(proba)
    except Exception as e:
        print(f"❌ Erreur lors de la prédiction : {e}")
        raise
        raise

