# 🐍 FRAUDE MPSA - Configuration Python Local

## ⚡ Démarrage Rapide (30 secondes)

### **Option 1: Script Automatique (Recommandé)**

```powershell
cd E:\fraude_mpsa
.\start-local.ps1
```

C'est tout! Le script:
- ✅ Crée le venv s'il n'existe pas
- ✅ Installe les dépendances
- ✅ Démarre l'API Flask
- ✅ Démarre Streamlit
- ✅ Ouvre les ports automatiquement

### **Option 2: Manuel (3 Terminaux)**

**Terminal 1 - API Flask:**
```powershell
cd E:\fraude_mpsa
.\.venv\Scripts\Activate.ps1
python api_flask/app.py
```

**Terminal 2 - Streamlit:**
```powershell
cd E:\fraude_mpsa
.\.venv\Scripts\Activate.ps1
streamlit run streamlit/app.py
```

**Terminal 3 - Uploader la baseline (optionnel):**
```powershell
cd E:\fraude_mpsa
.\.venv\Scripts\Activate.ps1
python upload_training_data.py "E:\pipeline\MPSA.csv" --max-rows 10000
```

---

## 🎯 URLs d'Accès

| Service | URL | Port |
|---------|-----|------|
| 🎨 Dashboard Streamlit | http://localhost:8501 | 8501 |
| 📊 API Flask | http://localhost:5000 | 5000 |
| 📊 Health API | http://localhost:5000/health | 5000 |

---

## ✨ Fonctionnalités Disponibles

### 🏠 Accueil
- Vue d'ensemble de l'application
- Statistiques globales
- Liens rapides

### 🎯 Prédictions
- Saisir les données de transaction
- Obtenir la probabilité de fraude
- Score entre 0 et 1

### 📈 Explications SHAP
- Visualiser les raisons de chaque prédiction
- Importance des variables
- Impact de chaque feature

### 💼 Analyse Métier
- Décisions basées sur seuils
- Analyse coûts-bénéfices
- Dynamiques de la fraude

### 💰 Analyse des Coûts
- Graphiques de coûts
- Étude de rentabilité
- Comparaison des seuils

### 🔍 Drift Monitoring
- Créer une baseline
- Détecter les changements de données
- Alertes automatiques

### 📤 Upload de Fichiers
- Uploader des fichiers CSV volumineux
- Créer des baselines
- Configurer le monitoring

---

## 📦 Configuration Minimale

### **Python**
- Version: 3.11+
- Vérifier: `python --version`

### **Virtual Environment**
```powershell
# Créer
python -m venv .venv

# Activer
.\.venv\Scripts\Activate.ps1

# Désactiver
deactivate
```

### **Dépendances**
```powershell
# Installer
pip install -r requirements.txt

# Vérifier
pip list | grep flask
pip list | grep streamlit
```

---

## 🔧 Maintenance

### **Réinstaller les dépendances**
```powershell
pip install --upgrade -r requirements.txt
```

### **Ajouter un nouveau package**
```powershell
pip install nom-du-package
pip freeze > requirements.txt
```

### **Nettoyer les fichiers de cache**
```powershell
# Python cache
python -m py_compile .

# Streamlit cache
Remove-Item -Recurse -Force $env:USERPROFILE\.streamlit\cache

# Virtual env (et réinstaller)
Remove-Item -Recurse .venv
python -m venv .venv
```

---

## 🚨 Troubleshooting

### **"Module not found"**
```powershell
# Vérifier activation
# (.venv) doit être dans le prompt

# Réinstaller
pip install -r requirements.txt
```

### **"Port already in use"**
```powershell
# Trouver le processus
netstat -ano | findstr :5000

# Tuer le processus
taskkill /PID <PID> /F
```

### **"API not responding"**
```powershell
# Vérifier l'API
curl http://localhost:5000/health

# Relancer
python api_flask/app.py
```

### **"Streamlit not loading"**
```powershell
# Réinstaller Streamlit
pip install --upgrade streamlit

# Vider le cache
streamlit cache clear

# Relancer
streamlit run streamlit/app.py
```

---

## 📁 Structure du Projet

```
fraude_mpsa/
├── .venv/                        ← Environment virtuel
├── api_flask/
│   ├── app.py                   ← API Flask principal
│   ├── model_xboost.joblib      ← Modèle ML
│   ├── shap.joblib              ← SHAP explainer
│   ├── drift_baseline.json       ← Baseline drift
│   └── ...
├── streamlit/
│   ├── app.py                   ← App Streamlit principale
│   ├── pages/                   ← Pages dynamiques
│   │   ├── prediction.py
│   │   ├── shap.py
│   │   ├── busines_decision.py
│   │   ├── cost_analys_bus.py
│   │   ├── drift_monitoring.py
│   │   └── ...
│   └── ...
├── requirements.txt             ← Dépendances Python
├── start-local.ps1              ← Script démarrage automatique
└── ...
```

---

## ✅ Checklist Démarrage

- [ ] Python 3.11+ installé
- [ ] Répertoire `E:\fraude_mpsa` accessible
- [ ] Virtual env créé (`.venv`)
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Fichier modèle présent: `api_flask/model_xboost.joblib`
- [ ] Fichier SHAP présent: `api_flask/shap.joblib`
- [ ] Ports 5000 et 8501 libres

## ▶️ Démarrage

```powershell
.\start-local.ps1
```

Puis ouvrir: http://localhost:8501

---

## 📊 Données d'Entrée

### **Format CSV**
```
transaction_id,montant,devise,devise_montant,produit,situation_motif,vente_motif,...
```

### **Localisation**
```
E:\pipeline\MPSA.csv (470.67 MB)
```

### **Upload via API**
```powershell
python upload_training_data.py "E:\pipeline\MPSA.csv" --max-rows 10000
```

---

## 🎓 Tutoriel Rapide

1. **Démarrer l'app**: `.\start-local.ps1`
2. **Ouvrir**: http://localhost:8501
3. **Aller à "Prédictions"**
4. **Remplir les données** (ou utiliser des données de test)
5. **Cliquer "Prédire"**
6. **Voir le résultat** (probabilité de fraude)
7. **Aller à "Explications SHAP"** pour voir pourquoi
8. **Créer une baseline**: Aller à "Drift Monitoring"
9. **Upload MPSA.csv**: Via Streamlit ou `upload_training_data.py`
10. **Vérifier le drift**: Les prédictions futures seront comparées

---

## 📚 Documentation Complète

Pour plus de détails: Voir `PYTHON_LOCAL_SETUP.md`

---

## 🆘 Besoin d'Aide?

### **Vérifier l'installation**
```powershell
python --version
pip list
.\.venv\Scripts\Activate.ps1
python -c "import flask, streamlit; print('OK')"
```

### **Diagnostiquer les problèmes**
```powershell
# Vérifier les logs de l'API
# Vérifier les logs de Streamlit (terminal)

# Tester l'API manuellement
curl http://localhost:5000/health
curl http://localhost:5000/predict -X POST -d '{"data": "..."}' -H "Content-Type: application/json"
```

### **Réinitialiser complètement**
```powershell
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

**Status**: ✅ Prêt pour démarrage  
**Dernière mise à jour**: 2026-01-01  
**Version**: 1.0 (Local Python, Sans Docker)
