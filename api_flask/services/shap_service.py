import pandas as pd
from core.pipeline_utils import load_pipeline
from core.shap_loader import shap_loader

pipeline = load_pipeline()
explainer = shap_loader()

def explain_instance(data: dict):
    try:
        X = pd.DataFrame([data])
        
        # Vérifier si c'est un sklearn Pipeline ou un modèle simple
        if hasattr(pipeline, 'steps'):
            # C'est un sklearn Pipeline
            preprocessing = pipeline[:-1]
            X_trans = preprocessing.transform(X)
        else:
            # C'est un modèle simple, pas de preprocessing
            X_trans = X
        
        shap_values = explainer.shap_values(X_trans)
        
        # Gérer différents formats de retour SHAP
        if isinstance(shap_values, list):
            return shap_values[0].tolist() if len(shap_values) > 0 else []
        else:
            return shap_values[0].tolist() if hasattr(shap_values[0], 'tolist') else shap_values[0]
    except Exception as e:
        print(f"❌ Erreur lors de l'explication : {e}")
        raise
