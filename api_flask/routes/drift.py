from flask import Blueprint, request, jsonify
from services.drift_detection import DriftDetector
import pandas as pd
import io
import os

drift_bp = Blueprint("drift", __name__)
detector = DriftDetector()

@drift_bp.route("/check", methods=["POST"])
def check_drift():
    """
    Vérifie le drift pour une nouvelle prédiction
    POST /drift/check avec JSON data
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Données JSON vides"}), 400
        
        drift_report = detector.check_drift(data)
        
        return jsonify(drift_report)
    
    except Exception as e:
        print(f"❌ Erreur dans /drift/check : {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@drift_bp.route("/summary", methods=["GET"])
def drift_summary():
    """
    Retourne un résumé de l'état du drift
    GET /drift/summary
    """
    try:
        summary = detector.get_drift_summary()
        return jsonify(summary)
    
    except Exception as e:
        print(f"❌ Erreur dans /drift/summary : {e}")
        return jsonify({"error": str(e)}), 500


@drift_bp.route("/baseline/create", methods=["POST"])
def create_baseline():
    """
    Crée une nouvelle baseline à partir d'une liste de données
    POST /drift/baseline/create avec JSON list
    """
    try:
        data_list = request.json
        
        if not isinstance(data_list, list):
            return jsonify({"error": "Les données doivent être une liste"}), 400
        
        baseline = detector.create_baseline(data_list)
        detector.save_baseline(baseline)
        
        # Extraire les features (exclure les métadonnées)
        features = [f for f in baseline.get('features', []) if f not in ['timestamp', 'n_samples']]
        
        return jsonify({
            "status": "SUCCESS",
            "message": f"Baseline créée avec {len(data_list)} échantillons",
            "baseline": baseline,
            "baseline_summary": {
                "total_samples": baseline.get('n_samples', len(data_list)),
                "features": features,
                "created_at": baseline.get('created_at', 'N/A')
            }
        })
    
    except Exception as e:
        print(f"❌ Erreur dans /drift/baseline/create : {e}")
        return jsonify({"error": str(e)}), 500


@drift_bp.route("/upload/training-data", methods=["POST"])
def upload_training_data():
    """
    Upload un fichier CSV volumineux et crée une baseline
    POST /drift/upload/training-data (multipart/form-data)
    
    Paramètres:
        - file: Fichier CSV
        - max_rows: Nombre max de lignes à traiter (défaut: 50000)
        - sample_ratio: Ratio d'échantillonnage (défaut: 1.0 = 100%)
    """
    try:
        # Vérifier que le fichier est présent
        if "file" not in request.files:
            return jsonify({"error": "Aucun fichier fourni"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "Fichier vide"}), 400
        
        if not file.filename.endswith(".csv"):
            return jsonify({"error": "Seuls les fichiers CSV sont acceptés"}), 400
        
        # Récupérer les paramètres
        max_rows = request.form.get("max_rows", 50000, type=int)
        sample_ratio = request.form.get("sample_ratio", 1.0, type=float)
        
        print(f"📤 Upload reçu: {file.filename} ({max_rows} lignes max, {sample_ratio*100}% sampling)")
        
        # Lire le fichier par chunks pour économiser la mémoire
        chunks = []
        chunk_size = 10000
        rows_read = 0
        
        for chunk in pd.read_csv(file, chunksize=chunk_size, nrows=max_rows):
            chunks.append(chunk)
            rows_read += len(chunk)
            print(f"  ✓ Chunk lu: {rows_read} lignes")
        
        if not chunks:
            return jsonify({"error": "Fichier CSV vide"}), 400
        
        df = pd.concat(chunks, ignore_index=True)
        
        # Appliquer le ratio d'échantillonnage si demandé
        if sample_ratio < 1.0:
            df = df.sample(frac=sample_ratio, random_state=42)
            print(f"  ✓ Échantillonnage appliqué: {len(df)} lignes retenues")
        
        # Convertir en liste de dictionnaires
        data_list = df.to_dict("records")
        
        # Créer et sauvegarder la baseline
        baseline = detector.create_baseline(data_list)
        detector.save_baseline(baseline)
        
        return jsonify({
            "status": "SUCCESS",
            "message": f"Baseline créée avec {len(data_list)} échantillons",
            "baseline_summary": {
                "total_samples": len(data_list),
                "features": baseline.get("features", []),
                "created_at": baseline.get("created_at")
            }
        }), 200
    
    except Exception as e:
        print(f"❌ Erreur dans /drift/upload/training-data : {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
