import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from services.api_client import predict, explain
import time

def show_page():
    # ═══════════════════════════════════════════════════════════════
    # 🏠 PAGE D'ACCUEIL
    # ═══════════════════════════════════════════════════════════════
    
    st.markdown("## 🏠 Tableau de Bord")
    st.markdown("---")
    
    def dataset(step,transaction_type,amount, oldbalanceOrg, newbalanceOrig,oldbalanceDest,newbalanceDest) :
        try : 
            if amount is None :
                st.warning("veuillez remplir le champs amount",icon="🚨")
            elif oldbalanceOrg is None : 
                 st.warning("veuillez remplir le champs  oldbalanceOrg ",icon="🚨") 
            elif  newbalanceOrig is None :    
                 st.warning("veuillez remplir le champs newbalanceOrig",icon="🚨") 
            elif oldbalanceDest is None :    
                 st.warning("veuillez remplir le champs oldbalanceDest ",icon="🚨") 
            elif newbalanceDest is None :     
                 st.warning("veuillez remplir le champs newbalanceDest ",icon="🚨") 
            else :     
                amount= float(amount)
                oldbalanceOrg=float(oldbalanceOrg)
                newbalanceOrig=float(newbalanceOrig)
                oldbalanceDest=float(oldbalanceDest)
                newbalanceDest=float(newbalanceDest)     
                hour =int(step%24)
                erreur_orig=float(abs(newbalanceOrig-(oldbalanceOrg-amount))) 
                erreur_dst=float(abs(newbalanceDest-(oldbalanceDest+amount)))
                videur_orig=1 if((oldbalanceOrg>0.0)&(newbalanceOrig==0.0)) else 0
                videur_orig=int(videur_orig)
                videur_dest =1 if((amount>0.0)&(newbalanceDest==0.0))  else 0
                videur_dest=int(videur_dest)
                step =int(step)
                data={"step":step,"type":transaction_type,"amount":amount,"oldbalanceOrg":oldbalanceOrg,"newbalanceOrig":newbalanceOrig,"oldbalanceDest":oldbalanceDest,"newbalanceDest":newbalanceDest,"hour":hour
                    ,"erreur_orig": erreur_orig, "erreur_dst":erreur_dst,"videur_orig":videur_orig,"videur_dest":videur_dest}
                return data
            st.error("veuillez remplir tous les champs vide",icon="🔥")
            return None
        except Exception:
            st.error("erreur lors de la creation de données",icon="🔥")
            return None
            
    
    # Métriques principales
    col1, col2 = st.columns(2)
    with st.form("form") :
        with col1 :
            step =st.number_input("intervall de transaction",min_value=1,max_value=743,key=1)
            transaction_type =st.selectbox("selectionner le type de transaction ",options=["TRANSFER","CASH_OUT"],index=1,key=2)
            amount= st.number_input("montant de transaction",placeholder="veuillez entrer le montant de transaction",value=None,key=3)
            oldbalanceOrg=st.number_input("solde initial de l'emetteur",placeholder="veuillez entrer le montant",value=None,key=4)
        with col2 :
                newbalanceOrig=st.number_input("solde final de l'emetteur",placeholder="veuillez entrer le montant",value=None,key=5)
                oldbalanceDest=st.number_input("solde initial du recepteur",placeholder="veuillez entrer le montant",value=None,key=6)
                newbalanceDest=st.number_input("solde final du  recepteur",placeholder="veuillez entrer le montant",value=None,key=7)
        bouton =st.form_submit_button()
        if bouton :
            data=dataset(step,transaction_type,amount, oldbalanceOrg, newbalanceOrig,oldbalanceDest,newbalanceDest)
            if data is not None :
               with st.spinner("Prediction en cours ..."):
                    time.sleep(2)
                    try:
                        proba=predict(data)
                        expl=explain(data)
                        
                        # Debug: afficher ce qu'on reçoit
                        #st.write("DEBUG - Données envoyées:", data)
                        #st.write("DEBUG - Réponse proba:", proba)
                        #st.write("DEBUG - Type de expl:", type(expl))
                        #st.write("DEBUG - Contenu expl:", expl)
                        # Sauvegarder les résultats en session state pour la page SHAP
                        if isinstance(expl, dict) and 'shap_values' in expl:
                            st.session_state.last_shap_values = expl['shap_values']
                        elif isinstance(expl, list):
                            st.session_state.last_shap_values = expl
                        else:
                            st.session_state.last_shap_values = []
                        
                        st.session_state.last_feature_names = list(data.keys())
                        
                        # Sauvegarder dans l'historique
                        if 'prediction_history' not in st.session_state:
                            st.session_state.prediction_history = []
                        
                        st.session_state.prediction_history.append({
                            'probability': proba['probability'],
                            'decision': proba['decision'],
                            'cost': proba['estimated_cost']
                        })
                        
                        # Sauvegarder les données envoyées pour le drift detection
                        st.session_state.last_data_sent = data

                        # Sauvegarder les dernières valeurs pour les autres pages
                        st.session_state.last_probability = proba['probability']
                        st.session_state.last_decision = proba['decision']
                        st.session_state.last_cost = proba['estimated_cost']
                        st.session_state.last_amount = amount  # Sauvegarder le montant aussi
                        
                        # Afficher les résultats
                        st.markdown("---")
                        st.subheader("🎯 Résultats de la Prédiction")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Probabilité de Fraude", f"{proba['probability']*100:.2f}%")
                        
                        with col2:
                            decision = proba['decision']
                            if decision == "ACCEPT":
                                st.metric("Décision", "✅ ACCEPTER", delta="Faible risque")
                            elif decision == "REVIEW":
                                st.metric("Décision", "⚠️ RÉVISER", delta="Risque moyen")
                            else:
                                st.metric("Décision", "❌ REJETER", delta="Risque élevé")
                        
                        with col3:
                            st.metric("Coût Estimé", f"${proba['estimated_cost']:.6f}", delta="Impact calculé")
                        
                        st.success("✅ Prédiction effectuée avec succès! Allez à l'onglet '📈 Explications SHAP' pour voir les détails.")
                        
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la prédiction: {str(e)}")
                   
    
    
    
    st.markdown("<br>", unsafe_allow_html=True)