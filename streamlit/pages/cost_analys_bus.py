import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def show_page():
    st.markdown("## 💰 Analyse des Coûts Business")
    st.markdown("---")
    
    st.info("ℹ️ Cette page analyse l'impact financier des décisions (faux positifs/négatifs)")
    
    # Vérifier s'il y a une dernière prédiction
    if 'last_probability' not in st.session_state:
        st.warning("⚠️ Aucune prédiction effectuée. Allez à l'onglet '🏠 Accueil' pour faire une prédiction d'abord!")
        st.markdown("---")
        st.subheader("💡 Guide des Coûts")
        st.markdown("""
        **Faux Positif (FP):** Rejeter une transaction valide
        - Impact: Client mécontent, perte de confiance
        - Coût: Moyen mais réputation endommagée
        
        **Faux Négatif (FN):** Accepter une transaction frauduleuse
        - Impact: Perte directe d'argent
        - Coût: Élevé et direct
        
        **Équilibre:** Trouver le bon ratio FP/FN pour optimiser le profit
        """)
        return
    
    probability = st.session_state.last_probability
    decision = st.session_state.last_decision
    cost = st.session_state.last_cost
    
    # Définir les coûts standards
    cost_fp = 50  # Coût d'un faux positif
    cost_fn = 500  # Coût d'un faux négatif
    
    # Section 1: Coûts estimés actuels
    st.subheader("💸 Impact Financier de la Décision Actuelle")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Coût FP (si rejeté à tort)", value=f"${cost_fp}", delta="Transaction valide rejetée")
    
    with col2:
        st.metric(label="Coût FN (si accepté à tort)", value=f"${cost_fn}", delta="Fraude non détectée")
    
    with col3:
        st.metric(label="Coût Décision Actuelle", value=f"${cost:.6f}", delta="Basé sur la décision et le montant")
    
    st.info(f"""
    **Explication du calcul du coût:**
    - Probabilité de fraude: **{probability*100:.4f}%**
    - Décision prise: **{decision}**
    - Montant de la transaction: Inclus dans le calcul (factor: {min(st.session_state.get('last_amount', 0) / 10000, 2.0):.2f}x)
    - Coût calculé: **${cost:.6f}**
    
    *Note: Les coûts sont faibles car la probabilité de fraude détectée par le modèle est très basse*
    """)
    
    st.markdown("---")
    
    # Section 2: Matrice Coût-Bénéfice
    st.subheader("� Analyse Coût-Bénéfice")
    
    # Créer une matrice de confusion théorique
    scenarios = {
        "Scénario": ["Vrais Négatifs (TN)", "Faux Positifs (FP)", "Faux Négatifs (FN)", "Vrais Positifs (TP)"],
        "Description": [
            "Transaction valide → Acceptée ✅",
            "Transaction valide → Rejetée ❌",
            "Transaction frauduleuse → Acceptée ❌",
            "Transaction frauduleuse → Rejetée ✅"
        ],
        "Impact": [
            "Profit: +1 transaction",
            f"Perte: ${cost_fp} + réputation",
            f"Perte directe: ${cost_fn}",
            "Risque évité: Profit sauvegardé"
        ]
    }
    
    df_scenarios = pd.DataFrame(scenarios)
    st.dataframe(df_scenarios, use_container_width=True)
    
    st.markdown("---")
    
    # Section 3: Graphique d'impact
    st.subheader("📈 Comparaison des Coûts par Type d'Erreur")
    
    error_types = ["Faux Positif\n(Rejeter à tort)", "Faux Négatif\n(Accepter à tort)"]
    costs_list = [cost_fp, cost_fn]
    colors_cost = ['orange', 'red']
    
    fig = go.Figure(data=[
        go.Bar(
            x=error_types,
            y=costs_list,
            marker=dict(color=colors_cost),
            text=[f"${c}" for c in costs_list],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Coût: $%{y:.0f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Impact Financier des Erreurs",
        yaxis_title="Coût ($)",
        height=350,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True, key="cost_comparison")
    
    st.markdown("---")
    
    # Section 4: Historique des coûts
    st.subheader("💹 Historique des Coûts")
    
    if 'prediction_history' in st.session_state and len(st.session_state.prediction_history) > 0:
        history = st.session_state.prediction_history
        hist_df = pd.DataFrame(history)
        
        # Graphique cumulatif des coûts
        cumulative_cost = hist_df['cost'].cumsum()
        
        fig_cumulative = go.Figure()
        fig_cumulative.add_trace(go.Scatter(
            x=list(range(len(hist_df))),
            y=cumulative_cost,
            mode='lines+markers',
            name='Coût Cumulatif',
            line=dict(color='red', width=2),
            fill='tozeroy',
            marker=dict(size=8)
        ))
        
        fig_cumulative.update_layout(
            title="Coût Cumulatif des Prédictions",
            xaxis_title="Numéro de Prédiction",
            yaxis_title="Coût Cumulatif ($)",
            height=350,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_cumulative, use_container_width=True, key="cumulative_cost")
        
        # Statistiques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Coût Total", f"${cumulative_cost.iloc[-1]:.2f}")
        
        with col2:
            st.metric("Coût Moyen", f"${hist_df['cost'].mean():.2f}")
        
        with col3:
            st.metric("Coût Max", f"${hist_df['cost'].max():.2f}")
        
        with col4:
            st.metric("Nombre de Prédictions", len(hist_df))
    else:
        st.info("📊 Les données d'historique apparaîtront après plusieurs prédictions")
    
    st.markdown("---")
    
    # Section 5: Recommandations
    st.subheader("💡 Recommandations d'Optimisation")
    
    st.markdown(f"""
    **Situation actuelle:**
    - Probabilité de fraude: **{probability*100:.2f}%**
    - Décision prise: **{decision}**
    - Coût estimé: **${cost:.2f}**
    
    **Analyse:**
    """)
    
    if probability < 0.3:
        st.success("""
        ✅ **Très confiant** - Risque minimal
        - Accepter cette transaction
        - Ratio coût/bénéfice favorable
        """)
    elif probability < 0.7:
        st.warning("""
        ⚠️ **Zone de décision critique**
        - Considérer: Coût FP ($50) vs bénéfice transaction
        - Recommandation: Vérifier manuellement pour les montants élevés
        - Les données SHAP peuvent aider à la décision
        """)
    else:
        st.error("""
        ❌ **Risque très élevé**
        - Rejeter pour éviter coût FN ($500)
        - La probabilité de fraude justifie le rejet
        - Envisager des mesures supplémentaires
        """)

