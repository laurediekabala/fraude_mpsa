#!/usr/bin/env python
"""Script de test pour lancer Flask et diagnostiquer les problèmes"""

import sys
import os

# Changer le répertoire de travail vers api_flask
os.chdir(os.path.join(os.path.dirname(__file__), 'api_flask'))
print(f"📂 Répertoire courant: {os.getcwd()}")

# Importer et tester le chargement du modèle
print("\n✅ Étape 1: Chargement du modèle...")
try:
    from core.pipeline_utils import load_pipeline
    pipeline = load_pipeline()
    print(f"✅ Modèle chargé: {type(pipeline)}")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle: {e}")
    sys.exit(1)

# Importer et tester la route predict
print("\n✅ Étape 2: Chargement des routes...")
try:
    from routes.predict import predict_bp
    print("✅ Route predict chargée")
except Exception as e:
    print(f"❌ Erreur lors du chargement de predict: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Importer et créer l'app Flask
print("\n✅ Étape 3: Création de l'app Flask...")
try:
    from app import app
    print("✅ App Flask créée")
except Exception as e:
    print(f"❌ Erreur lors de la création de l'app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Tester une prédiction
print("\n✅ Étape 4: Test de prédiction...")
try:
    test_data = {
        "step": 100,
        "type": "TRANSFER",
        "amount": 1000.0,
        "oldbalanceOrg": 5000.0,
        "newbalanceOrig": 4000.0,
        "oldbalanceDest": 2000.0,
        "newbalanceDest": 3000.0,
        "hour": 10,
        "erreur_orig": 0.0,
        "erreur_dst": 0.0,
        "videur_orig": 0,
        "vider_dest": 0
    }
    
    from services.prediction_service import predict_instance
    proba = predict_instance(test_data)
    print(f"✅ Prédiction réussie: {proba}")
except Exception as e:
    print(f"❌ Erreur lors de la prédiction: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Lancer Flask
print("\n🚀 Lancement de Flask...")
print("=" * 60)
app.run(host="0.0.0.0", port=5000, debug=True)
