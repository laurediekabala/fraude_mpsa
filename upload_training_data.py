#!/usr/bin/env python3
"""
Script pour uploader un fichier CSV volumineux vers l'API Flask
pour créer une baseline de drift detection

Supports streaming et chargement dynamique pour les fichiers > 1GB
"""

import requests
import argparse
import sys
from pathlib import Path
import pandas as pd
import json

def load_csv_chunks(csv_file: str, chunksize: int = 10000, max_rows: int = None):
    """
    Générateur pour lire un fichier CSV par chunks
    
    Args:
        csv_file: Chemin du fichier CSV
        chunksize: Nombre de lignes par chunk (défaut: 10000)
        max_rows: Nombre max de lignes à lire (None = tout)
    
    Yields:
        pd.DataFrame de chaque chunk
    """
    try:
        for chunk in pd.read_csv(csv_file, chunksize=chunksize, nrows=max_rows):
            yield chunk
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier: {e}")
        return

def upload_training_data_streaming(
    csv_file: str,
    api_url: str = "http://localhost:5000",
    max_rows: int = 50000,
    sample_ratio: float = 1.0,
    chunksize: int = 10000
):
    """
    Upload un fichier CSV volumineux via streaming (lecture par chunks)
    Pas de limite de taille pratique!
    
    Args:
        csv_file: Chemin du fichier CSV
        api_url: URL de l'API Flask (défaut: http://localhost:5000)
        max_rows: Nombre max de lignes à traiter (défaut: 50000)
        sample_ratio: Ratio d'échantillonnage 0.0-1.0 (défaut: 1.0)
        chunksize: Taille des chunks en lignes (défaut: 10000)
    
    Returns:
        Réponse JSON de l'API
    """
    csv_path = Path(csv_file)
    
    # Vérifications
    if not csv_path.exists():
        print(f"❌ Fichier non trouvé: {csv_file}")
        return None
    
    if csv_path.stat().st_size == 0:
        print(f"❌ Fichier vide: {csv_file}")
        return None
    
    file_size_mb = csv_path.stat().st_size / (1024 * 1024)
    print(f"📤 Upload en cours (STREAMING)...")
    print(f"  📄 Fichier: {csv_path.name}")
    print(f"  📊 Taille: {file_size_mb:.2f} MB")
    print(f"  📈 Lignes max: {max_rows}")
    print(f"  🎯 Sampling: {sample_ratio*100:.1f}%")
    print()
    
    try:
        endpoint = f"{api_url}/drift/upload/training-data"
        
        # Charger et traiter par chunks
        chunks_data = []
        rows_processed = 0
        
        print("📖 Lecture du fichier par chunks...")
        for i, chunk in enumerate(load_csv_chunks(csv_file, chunksize, max_rows)):
            rows_processed += len(chunk)
            chunks_data.append(chunk)
            
            # Afficher progression tous les 5 chunks
            if (i + 1) % 5 == 0:
                print(f"  ✓ Chunk {i+1}: {rows_processed} lignes traitées")
        
        print(f"✅ Fichier chargé: {rows_processed} lignes au total\n")
        
        # Concaténer tous les chunks
        print("🔗 Fusion des chunks...")
        df = pd.concat(chunks_data, ignore_index=True)
        print(f"✅ {len(df)} lignes fusionnées\n")
        
        # Appliquer le ratio d'échantillonnage
        if sample_ratio < 1.0:
            print(f"🎲 Échantillonnage à {sample_ratio*100:.1f}%...")
            df = df.sample(frac=sample_ratio, random_state=42)
            print(f"✅ {len(df)} lignes retenues après échantillonnage\n")
        
        # Convertir en liste de dictionnaires
        data_list = df.to_dict('records')
        
        # Upload via multipart form-data pour fichiers volumineux
        print("📤 Envoi des données à l'API...")
        
        with open(csv_path, 'rb') as f:
            files = {'file': (csv_path.name, f)}
            data = {
                'max_rows': max_rows,
                'sample_ratio': sample_ratio
            }
            
            response = requests.post(
                endpoint,
                files=files,
                data=data,
                timeout=600  # 10 minutes
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload réussi!")
            print(f"  ✓ Baseline créée avec {result['baseline_summary']['total_samples']} échantillons")
            print(f"  ✓ Créée le: {result['baseline_summary']['created_at']}")
            print(f"  ✓ Features: {', '.join(result['baseline_summary']['features'][:5])}...")
            return result
        else:
            print(f"❌ Erreur API ({response.status_code}): {response.text}")
            return None
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Erreur de connexion: Impossible de contacter {api_url}")
        print("   Vérifiez que le serveur Flask est en cours d'exécution:")
        print("   cd api_flask && python app.py")
        return None
    
    except requests.exceptions.Timeout:
        print("❌ Timeout: L'upload a pris trop longtemps (>10 minutes)")
        print("   Essayez avec un max_rows plus petit")
        return None
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None

def upload_training_data(
    csv_file: str,
    api_url: str = "http://localhost:5000",
    max_rows: int = 50000,
    sample_ratio: float = 1.0
):
    """
    Upload un fichier CSV volumineux vers l'endpoint /drift/upload/training-data
    (Utilise la version streaming pour les gros fichiers)
    """
    return upload_training_data_streaming(
        csv_file,
        api_url=api_url,
        max_rows=max_rows,
        sample_ratio=sample_ratio
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload un fichier CSV volumineux pour créer une baseline de drift detection"
    )
    parser.add_argument(
        "csv_file",
        help="Chemin du fichier CSV à uploader"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:5000",
        help="URL de l'API Flask (défaut: http://localhost:5000)"
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=50000,
        help="Nombre max de lignes à traiter (défaut: 50000)"
    )
    parser.add_argument(
        "--sample-ratio",
        type=float,
        default=1.0,
        help="Ratio d'échantillonnage 0.0-1.0 (défaut: 1.0)"
    )
    
    args = parser.parse_args()
    
    result = upload_training_data(
        args.csv_file,
        api_url=args.api_url,
        max_rows=args.max_rows,
        sample_ratio=args.sample_ratio
    )
    
    sys.exit(0 if result else 1)
