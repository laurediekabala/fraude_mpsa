import pandas as pd
from core.pipeline_utils import load_pipeline
from core.shap_loader import shap_loader

pipeline = load_pipeline()
explainer = shap_loader()

def explain_instance(data: dict):
    try:
        X = pd.DataFrame([data])
        
        # Récupérer les features d'entraînement
        training_features = list(pipeline.feature_names_in_) if hasattr(pipeline, 'feature_names_in_') else list(X.columns)
        
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
            shap_array = shap_values[0][0] if len(shap_values) > 0 else []
        else:
            shap_array = shap_values[0]
        
        # Créer un dictionnaire avec features et SHAP values
        result_dict = {
            feature: float(shap_array[i])
            for i, feature in enumerate(training_features)
        }
        
        return result_dict
    
    except Exception as e:
        print(f"❌ Erreur lors de l'explication : {e}")
        raise


