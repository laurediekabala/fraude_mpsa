import streamlit as st
from streamlit_option_menu import option_menu
import importlib

# Configuration de la page
st.set_page_config(
    page_title="Data Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injection du CSS personnalisé
def load_css():
    st.markdown("""
    <style>
        /* Masquer la sidebar par défaut */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        /* Style du header */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .main-header h1 {
            color: white;
            margin: 0;
            font-size: 2rem;
        }
        
        /* Style des cartes */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
        }
        
        /* Animation de transition */
        .stApp {
            transition: all 0.3s ease;
        }
        
        /* Style du menu de navigation */
        .nav-link {
            font-weight: 500 !important;
        }
        
        .nav-link-selected {
            background-color: #667eea !important;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 3rem;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# ═══════════════════════════════════════════════════════════════
# 🎯 BARRE DE NAVIGATION HORIZONTALE EN HAUT
# ═══════════════════════════════════════════════════════════════

def create_navbar():
    selected = option_menu(
        menu_title=None,  # Pas de titre pour un look épuré
        options=["🏠 Accueil", "📊 Analyse", "🤖 Business Decision", "💰 Coût Business", "📈 Explications SHAP", "🔍 Drift Monitoring"],
        icons=["house-fill", "graph-up", "robot", "cash-coin", "bar-chart", "activity"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",  # ← Navigation horizontale
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#fafafa",
                "border-radius": "10px",
                "box-shadow": "0 2px 10px rgba(0,0,0,0.1)"
            },
            "icon": {
                "color": "#667eea",
                "font-size": "18px"
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "center",
                "margin": "0px",
                "padding": "15px 25px",
                "--hover-color": "#e8e8e8",
                "font-weight": "500",
                "color": "#333"
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "color": "white",
                "font-weight": "600"
            },
        }
    )
    return selected

# Header de l'application
st.markdown("""
<div class="main-header">
    <h1>📊 Data Analytics Pro</h1>
    <p style="color: rgba(255,255,255,0.8); margin: 0;">Plateforme d'analyse de données et Machine Learning</p>
</div>
""", unsafe_allow_html=True)

# Barre de navigation
selected_page = create_navbar()

st.markdown("<br>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 📄 ROUTAGE DES PAGES
# ═══════════════════════════════════════════════════════════════

if "🏠 Accueil" in selected_page:
    from pages.prediction import show_page
    show_page()
elif "📊 Analyse" in selected_page:
    from pages.busines_decision import show_page
    show_page()
elif "🤖 Business Decision" in selected_page:
    from pages.busines_decision import show_page
    show_page()
elif "💰 Coût Business" in selected_page:
    from pages.cost_analys_bus import show_page
    show_page()
elif "📈 Explications SHAP" in selected_page:
    from pages.shap import show_page
    show_page()
elif "🔍 Drift Monitoring" in selected_page:
    from pages.drift_monitoring import show_page
    show_page()
    

# Footer
st.markdown("""
<div class="footer">
    <p>© 2024 Data Analytics Pro | Développé avec ❤️ et Streamlit</p>
</div>
""", unsafe_allow_html=True)
