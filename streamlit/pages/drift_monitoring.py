import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from pathlib import Path

def api_call(endpoint, method="GET", data=None):
    """Helper pour appeler l'API"""
    try:
        url = f"http://localhost:5000{endpoint}"
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def load_csv_streaming(csv_path, max_rows=None, sample_ratio=1.0, chunksize=10000):
    """
    Charger un fichier CSV volumineux par chunks (streaming)
    """
    chunks = []
    rows_read = 0
    
    progress_bar = st.progress(0)
    status = st.empty()
    
    try:
        for i, chunk in enumerate(pd.read_csv(csv_path, chunksize=chunksize, nrows=max_rows)):
            chunks.append(chunk)
            rows_read += len(chunk)
            
            # Mise à jour de la barre de progression
            progress = min(int((rows_read / max_rows) * 100) if max_rows else (i+1)*10, 95)
            progress_bar.progress(progress)
            status.text(f"📖 {rows_read:,} lignes chargées...")
            
            if max_rows and rows_read >= max_rows:
                break
        
        progress_bar.progress(100)
        status.text(f"✅ {rows_read:,} lignes chargées avec succès!")
        
        if chunks:
            df = pd.concat(chunks, ignore_index=True)
            
            # Appliquer le sampling si nécessaire
            if sample_ratio < 1.0:
                df = df.sample(frac=sample_ratio, random_state=42)
                status.text(f"✅ {len(df):,} lignes après échantillonnage")
            
            return df
        else:
            st.error("❌ Aucune donnée chargée")
            return None
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement: {e}")
        return None

def show_page():
    st.markdown("## 📊 Drift Detection & Model Monitoring")
    st.markdown("---")
    
    st.info("""
    🔍 **Data Drift Detection** surveille si les données changent au fil du temps.
    Si le drift est détecté, le modèle doit être réentraîné!
    """)
    
    # ═══════════════════════════════════════════════════════════════
    # SECTION: Charger les données d'entraînement
    # ═══════════════════════════════════════════════════════════════
    
    st.subheader("📥 Charger les Données d'Entraînement")
    
    # Créer des onglets pour les deux options d'upload
    tab1, tab2, tab3 = st.tabs(["📤 Streamlit Upload (<200MB)", "🚀 API Upload (fichiers volumineux)", "💾 Chemin Local (Streaming)"])
    
    with tab1:
        st.markdown("""
        ✅ **Avantages**: Simple et intuitif dans Streamlit
        ⚠️ **Limitation**: Maximum 200 MB
        """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Option pour limiter le nombre de lignes
            max_rows = st.slider(
                "Nombre max de lignes à charger",
                min_value=100,
                max_value=50000,
                value=5000,
                step=500,
                help="Charge seulement N premières lignes pour économiser la mémoire",
                key="max_rows_1"
            )
        
        with col2:
            # Option pour échantillonner
            sample_ratio = st.slider(
                "Ratio d'échantillonnage",
                min_value=0.1,
                max_value=1.0,
                value=0.5,
                step=0.1,
                help="Utiliser qu'un pourcentage des données (ex: 0.5 = 50%)",
                key="sample_ratio_1"
            )
        
        with col3:
            st.write("")  # Spacing
        
        uploaded_file = st.file_uploader(
            "📤 Uploadez un fichier CSV (< 200 MB)",
            type=['csv'],
            help="Format: CSV avec les colonnes de features",
            key="file_uploader_1"
        )
        
        if uploaded_file is not None:
            st.success("✅ Fichier détecté!")
            
            try:
                # Afficher la progression
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Lire seulement les premières lignes
                status_text.text(f"📖 Chargement des {max_rows} premières lignes...")
                
                # Lire par chunks pour économiser la mémoire
                chunks = []
                chunk_size = 10000
                
                for i, chunk in enumerate(pd.read_csv(uploaded_file, chunksize=chunk_size, nrows=max_rows)):
                    chunks.append(chunk)
                    progress = int((i + 1) / (max_rows / chunk_size) * 30)
                    progress_bar.progress(min(progress, 30))
                
                df = pd.concat(chunks, ignore_index=True) if chunks else pd.DataFrame()
                progress_bar.progress(40)
                
                if len(df) == 0:
                    st.error("❌ Aucune donnée chargée!")
                else:
                    status_text.text(f"📊 {len(df)} lignes chargées, {len(df.columns)} colonnes")
                    
                    # Afficher un aperçu
                    with st.expander("👁️ Aperçu des données"):
                        st.dataframe(df.head(10), use_container_width=True)
                        st.write(f"**Colonnes**: {list(df.columns)}")
                    
                    progress_bar.progress(60)
                    
                    # Échantillonner si nécessaire
                    if sample_ratio < 1.0:
                        status_text.text(f"🎲 Échantillonnage à {sample_ratio*100:.0f}%...")
                        df = df.sample(frac=sample_ratio, random_state=42)
                        status_text.text(f"✅ {len(df)} lignes après échantillonnage")
                    
                    progress_bar.progress(80)
                    
                    # Bouton pour créer la baseline
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("🔄 Créer baseline à partir de ce fichier", key="create_baseline_1"):
                            # Convertir DataFrame en liste de dictionnaires
                            data_list = df.to_dict('records')
                            
                            status_text.text("⏳ Envoi des données à l'API...")
                            progress_bar.progress(90)
                            
                            # Appeler l'API pour créer la baseline
                            result = api_call("/drift/baseline/create", method="POST", data=data_list)
                            
                            progress_bar.progress(100)
                            
                            if "error" in result:
                                st.error(f"❌ Erreur: {result['error']}")
                                status_text.text("❌ Erreur lors de la création de la baseline")
                            else:
                                st.success(f"✅ Baseline créée avec {len(data_list)} échantillons!")
                                status_text.text("✅ Baseline créée avec succès!")
                                st.balloons()
                                
                                # Afficher les stats
                                with st.expander("📊 Détails de la baseline"):
                                    st.json(result.get('baseline', {}))
                    
                    with col2:
                        st.info(f"💡 Données chargées: ~{len(df) * 0.001:.1f} MB")
                        
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture du fichier: {e}")
                status_text.text("❌ Erreur!")
    
    with tab2:
        st.markdown("""
        ✅ **Avantages**: Accepte fichiers > 200 MB, plus rapide, pas de limite pratique
        ℹ️ **Utilisation**: Python script ou PowerShell command
        """)
        
        st.info("""
        **Pour uploader des fichiers volumineux (> 200 MB):**
        
        1. **Via Python**: 
           ```bash
           python upload_training_data.py "C:\\chemin\\vers\\MPSA.csv" --max-rows 50000 --sample-ratio 1.0
           ```
        
        2. **Via PowerShell**:
           ```powershell
           .\\upload_data.ps1 -CsvFile "C:\\chemin\\vers\\MPSA.csv" -MaxRows 50000 -SampleRatio 1.0
           ```
        
        **Paramètres optionnels:**
        - `--max-rows`: Nombre max de lignes à traiter (défaut: 50000)
        - `--sample-ratio`: Ratio d'échantillonnage 0.0-1.0 (défaut: 1.0)
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_rows_2 = st.number_input(
                "Nombre max de lignes à traiter",
                min_value=100,
                max_value=1000000,
                value=50000,
                step=1000,
                help="Plus cette valeur est élevée, plus l'upload prendra de temps",
                key="max_rows_2"
            )
        
        with col2:
            sample_ratio_2 = st.slider(
                "Ratio d'échantillonnage (optionnel)",
                min_value=0.1,
                max_value=1.0,
                value=1.0,
                step=0.1,
                help="Utiliser qu'un pourcentage des données",
                key="sample_ratio_2"
            )
        
        st.markdown("---")
        
        st.subheader("📌 Commandes Rapides")
        
        # Exemple de commande Python
        st.code(
            f'python upload_training_data.py "C:\\\\data\\\\MPSA.csv" --max-rows {int(max_rows_2)} --sample-ratio {sample_ratio_2}',
            language="bash"
        )
        
        # Exemple de commande PowerShell
        st.code(
            f'.\\upload_data.ps1 -CsvFile "C:\\data\\MPSA.csv" -MaxRows {int(max_rows_2)} -SampleRatio {sample_ratio_2}',
            language="powershell"
        )
        
        st.markdown("---")
        
        st.subheader("📥 Suivi de l'Upload")
        
        if st.button("🔄 Vérifier l'état de la baseline", key="check_baseline_api"):
            summary = api_call("/drift/summary")
            
            if "error" not in summary and summary.get("status") != "NO_BASELINE":
                st.success(f"✅ Baseline disponible depuis: {summary.get('baseline_created', 'N/A')}")
                st.metric("Échantillons", summary.get('baseline_samples', 'N/A'))
            else:
                st.warning("⚠️ Aucune baseline trouvée. Lancez d'abord un upload!")
    
    with tab3:
        st.markdown("""
        ✅ **Avantages**: Ultra rapide, pas d'upload réseau, streaming en mémoire
        💾 **Utilisation**: Pour fichiers locaux (même réseau local)
        """)
        
        st.success("""
        ⚡ **MÉTHODE LA PLUS RAPIDE!**
        
        Charger directement depuis un chemin local avec streaming en mémoire.
        Ideal pour les fichiers > 500 MB!
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_path = st.text_input(
                "📁 Chemin local du fichier CSV",
                value="E:/pipeline/MPSA.csv",
                help="Exemple: E:/pipeline/MPSA.csv ou C:/data/file.csv",
                key="local_csv_path"
            )
        
        with col2:
            st.write("")  # Spacing
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            max_rows_3 = st.number_input(
                "Nombre max de lignes",
                min_value=100,
                max_value=1000000,
                value=50000,
                step=1000,
                help="Limite du nombre de lignes à charger",
                key="max_rows_3"
            )
        
        with col2:
            sample_ratio_3 = st.slider(
                "Ratio d'échantillonnage",
                min_value=0.1,
                max_value=1.0,
                value=1.0,
                step=0.1,
                help="Pourcentage de données à utiliser",
                key="sample_ratio_3"
            )
        
        with col3:
            chunksize_3 = st.number_input(
                "Taille des chunks",
                min_value=1000,
                max_value=50000,
                value=10000,
                step=1000,
                help="Lignes par chunk (plus bas = moins de RAM)",
                key="chunksize_3"
            )
        
        st.markdown("---")
        
        if st.button("📂 Charger et créer baseline", key="load_local_file"):
            # Vérifier que le fichier existe
            file_path = Path(csv_path)
            
            if not file_path.exists():
                st.error(f"❌ Fichier non trouvé: {csv_path}")
                st.info(f"💡 Vérifiez le chemin. Fichier existe? {file_path.exists()}")
            else:
                file_size_mb = file_path.stat().st_size / (1024 * 1024)
                st.info(f"📊 Fichier: {file_path.name} ({file_size_mb:.2f} MB)")
                
                try:
                    # Charger les données par streaming
                    st.subheader("⏳ Chargement en cours...")
                    df = load_csv_streaming(
                        str(file_path),
                        max_rows=max_rows_3,
                        sample_ratio=sample_ratio_3,
                        chunksize=int(chunksize_3)
                    )
                    
                    if df is not None and len(df) > 0:
                        st.success(f"✅ {len(df):,} lignes chargées!")
                        
                        # Afficher aperçu
                        with st.expander("👁️ Aperçu des données"):
                            st.dataframe(df.head(10), use_container_width=True)
                            st.write(f"**Colonnes**: {list(df.columns)}")
                            st.write(f"**Types**: {dict(df.dtypes)}")
                        
                        # Créer la baseline
                        st.subheader("🔄 Création de la baseline...")
                        
                        progress_bar = st.progress(0)
                        status = st.empty()
                        
                        # Convertir en liste de dictionnaires
                        status.text("📝 Conversion des données...")
                        progress_bar.progress(30)
                        data_list = df.to_dict('records')
                        
                        # Appeler l'API
                        status.text("📤 Envoi à l'API...")
                        progress_bar.progress(70)
                        result = api_call("/drift/baseline/create", method="POST", data=data_list)
                        progress_bar.progress(100)
                        
                        if "error" in result:
                            st.error(f"❌ Erreur API: {result['error']}")
                            status.text("❌ Erreur!")
                        else:
                            st.success("✅ Baseline créée avec succès!")
                            status.text("✅ Baseline créée!")
                            st.balloons()
                            
                            # Afficher les détails (même format pour tous les endpoints)
                            summary = result.get('baseline_summary', {})
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Échantillons", summary.get('total_samples', 'N/A'))
                            with col2:
                                st.metric("Features", len(summary.get('features', [])))
                            with col3:
                                created_at = summary.get('created_at', 'N/A')
                                created_at = created_at[:10] if isinstance(created_at, str) and len(created_at) > 10 else created_at
                                st.metric("Créée le", created_at)
                            
                            with st.expander("📊 Détails complets"):
                                st.json(result)
                    else:
                        st.error("❌ Erreur lors du chargement des données")
                
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    
    st.markdown("---")
    
    summary = api_call("/drift/summary")
    
    if "error" in summary:
        st.error(f"❌ Erreur: {summary['error']}")
        st.warning("La baseline doit être créée d'abord. Voir la section ci-dessous.")
    elif summary.get("status") == "NO_BASELINE":
        st.warning("⚠️ Aucune baseline disponible. Créez-en une avec les données d'entraînement!")
        
        if st.button("📥 Créer une baseline de test"):
            # Créer une baseline de test
            test_data = [
                {
                    "step": 100 + i,
                    "type": "TRANSFER",
                    "amount": 1000 + i*100,
                    "oldbalanceOrg": 5000,
                    "newbalanceOrig": 4000,
                    "oldbalanceDest": 1000,
                    "newbalanceDest": 2000,
                    "hour": 10,
                    "erreur_orig": 0.1,
                    "erreur_dst": 0.1,
                    "videur_orig": 0,
                    "videur_dest": 0
                }
                for i in range(100)
            ]
            
            result = api_call("/drift/baseline/create", method="POST", data=test_data)
            
            if "error" in result:
                st.error(f"❌ Erreur: {result['error']}")
            else:
                st.success("✅ Baseline créée avec succès!")
                st.json(result)
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", "✅ Baseline disponible")
        
        with col2:
            st.metric("Créée le", summary.get("baseline_created", "N/A")[:10])
        
        with col3:
            st.metric("Échantillons", summary.get("baseline_samples", "N/A"))
        
        # Afficher les features dans la baseline
        st.subheader("📋 Features dans la Baseline")
        features_list = summary.get("features", [])
        features_list = [f for f in features_list if f not in ['timestamp', 'n_samples']]
        
        col_count = 4
        cols = st.columns(col_count)
        for idx, feature in enumerate(features_list):
            with cols[idx % col_count]:
                st.write(f"✓ {feature}")
        
        st.markdown("---")
        
        # Section 2: Vérifier le drift sur la dernière prédiction
        st.subheader("🔍 Vérification du Drift")
        
        if 'last_probability' in st.session_state and 'last_data_sent' in st.session_state:
            st.info("Vérification en cours sur la dernière prédiction...")
            
            # Appeler l'API de drift
            drift_report = api_call("/drift/check", method="POST", data=st.session_state.last_data_sent)
            
            if "error" in drift_report:
                st.error(f"❌ Erreur: {drift_report['error']}")
            else:
                # Afficher le résumé du drift
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    status = "🔴 DRIFT DÉTECTÉ" if drift_report.get('overall_drift') else "🟢 Pas de drift"
                    st.metric("Status Global", status)
                
                with col2:
                    st.metric(
                        "Features affectées",
                        f"{drift_report.get('drift_count', 0)}/{drift_report.get('total_features', 0)}"
                    )
                
                with col3:
                    st.metric(
                        "Pourcentage de drift",
                        f"{drift_report.get('drift_percentage', 0):.1f}%"
                    )
                
                st.markdown("---")
                
                # Tableau détaillé des drifts par feature
                st.subheader("📋 Analyse par Feature")
                
                features_data = []
                for feature_name, feature_info in drift_report.get('features', {}).items():
                    if 'error' not in feature_info:
                        drift_status = "🔴 Drift" if feature_info.get('drift') else "🟢 OK"
                        p_value = feature_info.get('p_value', 'N/A')
                        
                        if feature_info.get('type') == 'numeric':
                            baseline_val = feature_info.get('baseline_mean', 'N/A')
                            current_val = feature_info.get('current_mean', 'N/A')
                        else:
                            baseline_val = "Catégorique"
                            current_val = "Catégorique"
                        
                        features_data.append({
                            'Feature': feature_name,
                            'Status': drift_status,
                            'P-Value': f"{p_value:.4f}" if isinstance(p_value, float) else p_value,
                            'Baseline': baseline_val,
                            'Current': current_val,
                            'Alert': feature_info.get('alert', '')
                        })
                
                if features_data:
                    df_drift = pd.DataFrame(features_data)
                    st.dataframe(df_drift, use_container_width=True)
                
                st.markdown("---")
                
                # Recommandations
                st.subheader("📌 Recommandations")
                
                if drift_report.get('overall_drift'):
                    st.error("""
                    ⚠️ **DRIFT DÉTECTÉ!**
                    
                    Actions recommandées:
                    1. 📊 Analyser les changements dans les données
                    2. 🔄 Vérifier la qualité des données
                    3. 🔄 **Réentraîner le modèle** avec les nouvelles données
                    4. ✅ Créer une nouvelle baseline après réentraînement
                    """)
                else:
                    st.success("""
                    ✅ **Pas de drift détecté**
                    
                    Le modèle est stable et les données sont cohérentes avec la baseline.
                    Continuez à monitorer régulièrement.
                    """)
        else:
            st.info("💡 Faites une prédiction d'abord pour tester le drift detection!")
    
    st.markdown("---")
    
    # Section 3: Guide
    st.subheader("📚 Comment ça marche?")
    
    st.markdown("""
    **Data Drift** = Changement dans la distribution des données
    
    ### Types de Drift:
    - **Covariate Drift**: Changement des features (X)
    - **Concept Drift**: Changement de la relation entre X et Y
    - **Prior Probability Drift**: Changement de la distribution de Y
    
    ### Détection:
    - **Numériques**: Test Kolmogorov-Smirnov (KS)
    - **Catégoriques**: Test Chi-carré (χ²)
    
    ### Quand Réentraîner:
    1. P-value < 0.05 → Drift significatif
    2. Plus de 30% des features affectées
    3. Baisse de performance observée
    4. Changement de domaine (ex: nouvelle région, saison)
    """)
