import sys
import os
from pathlib import Path
import json
import numpy as np

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from routes.predict import predict_bp
from routes.explain import explain_bp
from routes.health import health_bp
from routes.drift import drift_bp

# JSON Encoder personnalisé pour gérer les types numpy
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

def create_app():
    app = Flask(__name__)
    
    # Utiliser le encoder personnalisé
    app.json_encoder = NumpyEncoder

    app.register_blueprint(predict_bp, url_prefix="/predict")
    app.register_blueprint(explain_bp, url_prefix="/explain")
    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(drift_bp, url_prefix="/drift")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
