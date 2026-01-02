# 🐍 Guide: Retour à Python Local (Sans Docker)

## 📋 Résumé

Ce guide vous montre comment utiliser l'application **sans Docker**, directement avec Python sur votre machine Windows.

---

## ✅ Prérequis

- **Python 3.11+** installé
- **pip** (inclus avec Python)
- **Git** (optionnel, pour les commandes)

### Vérifier l'installation

```powershell
python --version      # Doit afficher Python 3.11.x
pip --version         # Doit afficher pip 24.x ou plus
```

---

## 🚀 Installation (Sans Docker)

### **Étape 1: Créer un Virtual Environment**

```powershell
# Aller au répertoire du projet
cd E:\fraude_mpsa

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
.\.venv\Scripts\Activate.ps1
```

**Résultat attendu:**
```
(.venv) PS E:\fraude_mpsa>
```

### **Étape 2: Installer les Dépendances**

```powershell
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer tous les packages
pip install -r requirements.txt
```

**⏳ Cela peut prendre 5-10 minutes la première fois.**

### **Étape 3: Vérifier l'Installation**

```powershell
# Vérifier tous les packages
pip list

# Vérifier les imports
python -c "import flask, streamlit, xgboost, shap; print('✅ All OK!')"
```

---

## ▶️ Démarrage de l'Application

### **Terminal 1: Démarrer l'API Flask**

```powershell
cd E:\fraude_mpsa
.\.venv\Scripts\Activate.ps1
python api_flask/app.py
```

**Résultat attendu:**
```
✅ Modèle chargé avec succès
✅ Fichier SHAP chargé avec succès
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

**L'API est maintenant disponible à:** http://localhost:5000

### **Terminal 2: Démarrer Streamlit**

```powershell
cd E:\fraude_mpsa
.\.venv\Scripts\Activate.ps1
streamlit run streamlit/app.py
```

**Résultat attendu:**
```
  You can now view your Streamlit app in your browser.

  URL: http://localhost:8501
```

**Le Dashboard est maintenant disponible à:** http://localhost:8501

---

## 📊 Utiliser l'Application

### **1. Faire une Prédiction**

1. Allez à http://localhost:8501
2. Remplissez les données de transaction
3. Cliquez "Prédire"
4. Voyez le résultat instantanément

### **2. Voir les Explications**

1. Allez à l'onglet "📈 Explications SHAP"
2. Visualisez les raisons de la prédiction
3. Comprenez l'impact de chaque variable

### **3. Uploader une Baseline**

Pour créer une baseline de drift detection:

```powershell
# Méthode 1: Via Python
python upload_training_data.py "E:\pipeline\MPSA.csv" --max-rows 10000

# Méthode 2: Via Streamlit
# Allez à "🔍 Drift Monitoring" → "📤 Streamlit Upload"
```

### **4. Vérifier le Drift**

1. Allez à "🔍 Drift Monitoring"
2. Après une prédiction, le drift est automatiquement vérifié
3. Voyez si les données ont changé

---

## 🔧 Commandes Útiles

### **Gestion de l'Environnement Virtual**

```powershell
# Activer l'environnement
.\.venv\Scripts\Activate.ps1

# Désactiver l'environnement
deactivate

# Voir les packages installés
pip list

# Réinstaller tous les packages
pip install --upgrade -r requirements.txt

# Geler les dépendances actuelles
pip freeze > requirements.txt
```

### **Démarrage Rapide**

```powershell
# Script pour démarrer les deux services
# Créer un fichier: start.ps1

$ErrorActionPreference = "Stop"

# Terminal 1: API
Start-Process powershell -ArgumentList {
    cd E:\fraude_mpsa
    .\.venv\Scripts\Activate.ps1
    python api_flask/app.py
}

# Terminal 2: Streamlit
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList {
    cd E:\fraude_mpsa
    .\.venv\Scripts\Activate.ps1
    streamlit run streamlit/app.py
}

Write-Host "✅ Services démarrés!"
Write-Host "🎨 Streamlit:  http://localhost:8501"
Write-Host "📊 API:        http://localhost:5000"
```

**Utiliser le script:**
```powershell
.\start.ps1
```

---

## 🐛 Troubleshooting

### **"ModuleNotFoundError: No module named 'flask'"**

```powershell
# Vérifier que l'environnement est activé
# Le prompt doit commencer par (.venv)

# Réinstaller les dépendances
pip install -r requirements.txt
```

### **"Port 5000 already in use"**

```powershell
# Trouver le processus utilisant le port
netstat -ano | findstr :5000

# Tuer le processus
taskkill /PID <PID> /F

# Ou utiliser un autre port
python -m flask run --port 5001
```

### **"Streamlit ne se connecte pas à l'API"**

Vérifier que:
1. L'API tourne sur http://localhost:5000
2. Tester avec: `curl http://localhost:5000/health`
3. Vérifier que le pare-feu n'est pas bloquant

### **"Out of Memory" avec gros fichiers**

```powershell
# Uploader par chunks
python upload_training_data.py "data.csv" --max-rows 10000 --sample-ratio 0.5
```

---

## 📁 Structure Sans Docker

```
fraude_mpsa/
├── .venv/                    ← Virtual environment local
│   ├── Scripts/
│   │   ├── Activate.ps1
│   │   ├── python.exe
│   │   └── pip.exe
│   └── Lib/python3.11/site-packages/  ← Packages installés
│
├── api_flask/                ← Backend API
│   ├── app.py               ← Point d'entrée Flask
│   ├── model_xboost.joblib  ← Modèle ML
│   ├── shap.joblib          ← SHAP explainer
│   └── ...
│
├── streamlit/               ← Frontend Streamlit
│   ├── app.py              ← Point d'entrée Streamlit
│   └── ...
│
├── requirements.txt         ← Dépendances Python
├── .gitignore              ← Fichiers à ignorer
├── README.md               ← Documentation générale
└── start.ps1               ← Script démarrage rapide
```

---

## 💾 Sauvegarder l'Environnement

### **Exporter les dépendances**

```powershell
# Créer un requirements.txt avec les versions exactes
pip freeze > requirements.txt
```

### **Recréer l'environnement ailleurs**

```powershell
# Sur une autre machine
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🆚 Comparaison: Local vs Docker

| Aspect | Local Python | Docker |
|--------|--------------|--------|
| **Démarrage** | ~5s | ~30s |
| **Installation** | Facile | Plus complexe |
| **Espace disque** | ~2GB | ~1.2GB (optimisé) |
| **Portabilité** | Dépend OS | Identique partout |
| **Développement** | ✅ Idéal | ❌ Moins pratique |
| **Production** | ❌ Non | ✅ Idéal |
| **Isolation** | ❌ Non | ✅ Oui |

---

## 📚 Fichiers de Configuration

### **.venv/pyvenv.cfg**
```ini
home = C:\Users\YourName\AppData\Local\Programs\Python\Python311
include-system-site-packages = false
version_info = 3.11.x
```

### **requirements.txt** (Simplifié)
```
scikit-learn==1.5.1
numpy==1.26.4
pandas==2.2.2
matplotlib==3.8.4
seaborn==0.13.2
xgboost==2.0.3
flask==3.0.0
shap==0.45.1
joblib==1.4.2
streamlit>=1.28.0,<2.0.0
plotly==5.20.0
scipy==1.13.1
requests==2.32.3
```

---

## 🎯 Workflow Typique

```powershell
# Jour 1: Installation
cd E:\fraude_mpsa
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Jour 2+: Démarrage rapide
.\.venv\Scripts\Activate.ps1
# Terminal 1
python api_flask/app.py
# Terminal 2
streamlit run streamlit/app.py
```

---

## 💡 Tips

### **Créer un Raccourci Windows**

1. Click droit sur le bureau
2. New → Shortcut
3. Location: `C:\Windows\System32\cmd.exe /k cd E:\fraude_mpsa && .venv\Scripts\Activate.ps1`
4. Name: "Fraude MPSA"

### **Alias PowerShell**

```powershell
# Ajouter à votre profile PowerShell
# $PROFILE
Add-Content $PROFILE -Value @'
function fraude { cd E:\fraude_mpsa; .\.venv\Scripts\Activate.ps1 }
'@
```

Puis utiliser: `fraude`

### **Automatiser le démarrage**

```powershell
# Créer start.bat
@echo off
cd /d E:\fraude_mpsa
call .venv\Scripts\activate.bat
start cmd /k "python api_flask/app.py"
start cmd /k "streamlit run streamlit/app.py"
```

---

## 🚀 Prochaines Étapes

1. ✅ Installation terminée
2. ▶️ Démarrer l'application
3. 📊 Faire une prédiction
4. 📈 Voir les explications SHAP
5. 🔍 Uploader une baseline drift
6. 💾 Sauvegarder votre configuration

---

## 📞 Support

Si vous rencontrez des problèmes:

1. Vérifiez que Python 3.11+ est installé
2. Vérifiez l'activation de l'environnement virtual (prompt `(.venv)`)
3. Réinstallez les dépendances: `pip install --upgrade -r requirements.txt`
4. Consultez les logs de l'API et Streamlit
5. Vérifiez les ports 5000 et 8501 sont libres

---

**Status**: ✅ Prêt pour Python Local  
**Version**: 1.0  
**Date**: 2026-01-01
