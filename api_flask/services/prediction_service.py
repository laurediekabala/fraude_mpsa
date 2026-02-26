import pandas as pd
from core.pipeline_utils import load_pipeline

# Chargement du pipeline entraîné
pipeline = load_pipeline()

def predict_instance(data: dict) -> float:
    """
    Retourne la PROBABILITÉ DE FRAUDE (classe = 1)
    Version robuste et indépendante de l'ordre des classes.
    """

    try:
        # ==================================================
        # 1️⃣ Création du DataFrame
        # ==================================================
        X = pd.DataFrame([data])

        # ==================================================
        # 2️⃣ Vérification de la capacité du modèle
        # ==================================================
        if not hasattr(pipeline, "predict_proba"):
            raise ValueError("Le modèle chargé ne supporte pas predict_proba")

        # ==================================================
        # 3️⃣ Identification correcte de la classe FRAUDE
        # ==================================================
        classes = pipeline.classes_

        if 1 not in classes:
            raise ValueError(
                f"Classe fraude (1) absente du modèle. Classes trouvées : {classes}"
            )

        fraud_class_index = list(classes).index(1)

        # ==================================================
        # 4️⃣ Extraction de la probabilité FRAUDE
        # ==================================================
        proba_fraud = pipeline.predict_proba(X)[0][fraud_class_index]

        # ==================================================
        # 5️⃣ Sécurisation finale
        # ==================================================
        proba_fraud = float(proba_fraud)

        if proba_fraud > 1:
            proba_fraud = proba_fraud / 100

        proba_fraud = min(max(proba_fraud, 0.0), 1.0)

        return proba_fraud

    except Exception as e:
        print(f"❌ Erreur lors de la prédiction fraude : {e}")
        raise