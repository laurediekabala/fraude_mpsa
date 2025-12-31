import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from services.api_client import explain
import time

def show_page():
    st.markdown("## 📈 Explications SHAP")
    st.markdown("---")
    
    st.info("ℹ️ Cette page affiche les valeurs SHAP pour expliquer les prédictions du modèle")
    
    # Vérifier s'il y a des données SHAP en session
    if 'last_shap_values' not in st.session_state or st.session_state.last_shap_values is None:
        st.warning("⚠️ Aucune prédiction effectuée. Allez à l'onglet 'Accueil' pour faire une prédiction d'abord!")
        st.markdown("---")
        st.subheader("💡 Guide SHAP")
        st.markdown("""
        **Qu'est-ce que SHAP?**
        - SHAP (SHapley Additive exPlanations) explique comment chaque variable contribue à la prédiction
        
        **Interprétation:**
        - **Valeurs positives (rouge)** → augmentent la probabilité de fraude 🔴
        - **Valeurs négatives (bleu)** → diminuent la probabilité de fraude 🔵
        - **Plus grande magnitude** → plus d'impact sur la prédiction 📊
        """)
        return
    
    shap_values = st.session_state.last_shap_values
    feature_names = st.session_state.get('last_feature_names', [])
    
    # Convertir en liste si nécessaire
    if isinstance(shap_values, np.ndarray):
        shap_values = shap_values.tolist()
    
    if not isinstance(shap_values, list):
        shap_values = [shap_values]
    
    if not isinstance(feature_names, list):
        feature_names = list(feature_names)
    
    # Assurer que les longueurs correspondent
    if len(feature_names) != len(shap_values):
        st.warning(f"⚠️ Mismatch de données: {len(feature_names)} features vs {len(shap_values)} SHAP values")
        st.write(f"Features: {feature_names}")
        st.write(f"SHAP values: {shap_values}")
        
        # Ajuster à la longueur la plus courte
        min_len = min(len(feature_names), len(shap_values))
        feature_names = feature_names[:min_len]
        shap_values = shap_values[:min_len]
    
    # Créer un DataFrame pour les SHAP values
    shap_df = pd.DataFrame({
        'Feature': feature_names,
        'SHAP Value': shap_values,
        'Abs Value': np.abs(shap_values)
    }).sort_values('Abs Value', ascending=True)
    
    # 1. Graphique en barres horizontal
    st.subheader("📊 Valeurs SHAP par Feature")
    
    fig = go.Figure()
    
    colors = ['red' if x > 0 else 'blue' for x in shap_df['SHAP Value']]
    
    fig.add_trace(go.Bar(
        y=shap_df['Feature'],
        x=shap_df['SHAP Value'],
        orientation='h',
        marker=dict(color=colors),
        text=shap_df['SHAP Value'].round(4),
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>SHAP Value: %{x:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Impact des Features sur la Prédiction",
        xaxis_title="SHAP Value",
        yaxis_title="Features",
        height=400,
        showlegend=False,
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True, key="shap_bar_chart")
    
    # 2. Tableau détaillé
    st.subheader("📋 Valeurs SHAP Détaillées")
    
    display_df = shap_df.copy()
    display_df['SHAP Value'] = display_df['SHAP Value'].round(6)
    display_df['Abs Value'] = display_df['Abs Value'].round(6)
    display_df = display_df.drop('Abs Value', axis=1)
    
    st.dataframe(display_df.sort_values('SHAP Value', ascending=False), use_container_width=True)
    
    # 3. Statistiques
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Somme SHAP", f"{shap_df['SHAP Value'].sum():.4f}")
    
    with col2:
        st.metric("Max SHAP", f"{shap_df['SHAP Value'].max():.4f}")
    
    with col3:
        st.metric("Min SHAP", f"{shap_df['SHAP Value'].min():.4f}")
    
    st.markdown("---")
    
    # 4. Guide
    st.subheader("💡 Comment interpréter?")
    st.markdown("""
    - Les barres **rouges** indiquent que la feature augmente le risque de fraude
    - Les barres **bleues** indiquent que la feature diminue le risque de fraude
    - L'ordre vertical montre l'importance relative des features
    - Les valeurs plus grandes en magnitude = plus d'impact sur la décision
    """)
