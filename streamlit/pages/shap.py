import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def show_page():
    st.markdown("## 📈 Explications SHAP")
    st.markdown("---")
    
    st.info("ℹ️ Cette page affiche les valeurs SHAP pour expliquer les prédictions du modèle")
    
    # Vérifier s'il y a des données SHAP en session
    if 'last_shap_values' not in st.session_state or st.session_state.last_shap_values is None:
        st.warning("⚠️ Aucune prédiction effectuée. Allez à l'onglet 'Accueil' pour faire une prédiction d'abord!")
        return
    
    shap_data = st.session_state.last_shap_values
    
    # Extraire les features et valeurs
    feature_names = []
    shap_values_list = []
    
    if isinstance(shap_data, dict):
        # Cas 1 : {"shap_values": {features_dict}}
        if 'shap_values' in shap_data and isinstance(shap_data['shap_values'], dict):
            shap_dict = shap_data['shap_values']
            feature_names = list(shap_dict.keys())
            shap_values_list = [float(v) for v in shap_dict.values()]
        
        # Cas 2 : {feature: shap_value, ...} (dictionnaire simple)
        else:
            first_value = next(iter(shap_data.values())) if shap_data else None
            
            if isinstance(first_value, (int, float)):
                feature_names = list(shap_data.keys())
                shap_values_list = [float(v) for v in shap_data.values()]
            else:
                st.error(f"❌ Format inattendu: {type(shap_data)}")
                st.write(shap_data)
                return
    else:
        st.error(f"❌ Format inattendu: {type(shap_data)}")
        st.write(shap_data)
        return
    
    if not feature_names or not shap_values_list:
        st.error("❌ Impossible d'extraire les données SHAP")
        return
    
    st.success(f"✅ {len(feature_names)} features extraites")
    
    # Créer un DataFrame
    shap_df = pd.DataFrame({
        'Feature': feature_names,
        'SHAP Value': shap_values_list,
        'Abs Value': np.abs(shap_values_list)
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