import requests
import streamlit as st

API_URL = "http://localhost:5000"

def predict(data):
    try:
        response = requests.post(f"{API_URL}/predict", json=data, timeout=10)
        response.raise_for_status()  # Lève une erreur si status >= 400
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Erreur de connexion: Impossible de se connecter à l'API Flask")
        st.stop()
    except requests.exceptions.Timeout:
        st.error("❌ Timeout: L'API Flask ne répond pas à temps")
        st.stop()
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Erreur HTTP: {e.response.status_code} - {e.response.text}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Erreur lors de la prédiction: {str(e)}")
        st.stop()

def explain(data):
    try:
        response = requests.post(f"{API_URL}/explain", json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Erreur de connexion: Impossible de se connecter à l'API Flask")
        st.stop()
    except requests.exceptions.Timeout:
        st.error("❌ Timeout: L'API Flask ne répond pas à temps")
        st.stop()
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Erreur HTTP: {e.response.status_code} - {e.response.text}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Erreur lors de l'explication: {str(e)}")
        st.stop()
