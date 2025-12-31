import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def show_page():
    st.markdown("## 📊 Analyse pour la Prise de Décision")
    st.markdown("---")
    
    st.info("ℹ️ Cette page affiche l'analyse des décisions basée sur vos prédictions")
    
    # Vérifier s'il y a une dernière prédiction
    if 'last_probability' not in st.session_state:
        st.warning("⚠️ Aucune prédiction effectuée. Allez à l'onglet '🏠 Accueil' pour faire une prédiction d'abord!")
        st.markdown("---")
        st.subheader("📌 Comment ça marche?")
        st.markdown("""
        1. **Allez à l'onglet Accueil** et remplissez les informations de la transaction
        2. **Cliquez sur Soumettre** pour obtenir une prédiction
        3. **Revenez ici** pour voir l'analyse détaillée de la décision
        """)
        return
    
    probability = st.session_state.last_probability
    decision = st.session_state.last_decision
    cost = st.session_state.last_cost
    
    # Section 1: Vue d'ensemble avec résultats
    st.subheader("🎯 Résultats Actuels")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Probabilité de Fraude",
            value=f"{probability*100:.2f}%",
            delta=f"Risque {'élevé' if probability > 0.7 else 'moyen' if probability > 0.3 else 'faible'}"
        )
    
    with col2:
        if decision == "ACCEPT":
            st.metric("Décision", "✅ ACCEPTER", delta="Confiance élevée")
        elif decision == "REVIEW":
            st.metric("Décision", "⚠️ RÉVISER", delta="Intervention manuelle requise")
        else:
            st.metric("Décision", "❌ REJETER", delta="Risque inacceptable")
    
    with col3:
        st.metric("Coût Estimé", f"${cost:.2f}", delta="Impact financier")
    
    st.markdown("---")
    
    # Section 2: Matrice de décision avec couleurs
    st.subheader("📋 Règles de Décision")
    
    decision_data = {
        "Décision": ["ACCEPT", "REVIEW", "REJECT"],
        "Seuil de Probabilité": ["< 30%", "30% - 70%", "> 70%"],
        "Signification": ["Transaction valide (faible risque)", "Vérifier manuellement", "Fraude détectée (haut risque)"],
        "Action": ["✅ Approuver", "🔍 Examiner", "❌ Bloquer"]
    }
    
    df_decisions = pd.DataFrame(decision_data)
    st.dataframe(df_decisions, use_container_width=True)
    
    st.markdown("---")
    
    # Section 3: Graphiques de distribution
    st.subheader("📊 Distribution des Décisions")
    
    # Créer des données fictives pour montrer la tendance
    if 'prediction_history' in st.session_state and len(st.session_state.prediction_history) > 0:
        history = st.session_state.prediction_history
        hist_df = pd.DataFrame(history)
        
        # Compter les décisions
        decision_counts = hist_df['decision'].value_counts()
        
        fig = go.Figure(data=[
            go.Bar(
                x=decision_counts.index,
                y=decision_counts.values,
                marker=dict(color=['green' if x == 'ACCEPT' else 'orange' if x == 'REVIEW' else 'red' 
                                   for x in decision_counts.index]),
                text=decision_counts.values,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Distribution des Décisions (Historique)",
            xaxis_title="Type de Décision",
            yaxis_title="Nombre de Transactions",
            height=350,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True, key="decision_distribution")
        
        # Graphique de la tendance de probabilité
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=list(range(len(hist_df))),
            y=hist_df['probability'],
            mode='lines+markers',
            name='Probabilité de Fraude',
            line=dict(color='red', width=2),
            marker=dict(size=8)
        ))
        
        fig2.add_hline(y=0.3, line_dash="dash", line_color="orange", annotation_text="Seuil REVIEW")
        fig2.add_hline(y=0.7, line_dash="dash", line_color="red", annotation_text="Seuil REJECT")
        
        fig2.update_layout(
            title="Tendance des Probabilités de Fraude",
            xaxis_title="Numéro de Prédiction",
            yaxis_title="Probabilité",
            height=350,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig2, use_container_width=True, key="probability_trend")
    else:
        st.info("📊 Les graphiques apparaîtront après plusieurs prédictions")
    
    st.markdown("---")
    
    # Section 4: Recommandations
    st.subheader("💡 Recommandations")
    
    if probability < 0.3:
        st.success("✅ **Confiance élevée** - Recommandation: Approuver rapidement")
    elif probability < 0.7:
        st.warning("⚠️ **Vérification requise** - Recommandation: Examiner les détails (SHAP peut aider)")
    else:
        st.error("❌ **Alerte fraude** - Recommandation: Rejeter et enquêter")

