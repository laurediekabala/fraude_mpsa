# 🎯 DÉTECTION DE CHANGEMENTS DANS LES DONNÉES - Guide Complet

## 📌 TL;DR (Trop Long, Pas Lu)

**La détection de drift vous dit si vos données ont changé!**

```
Baseline (données d'entraînement)
    ↓
    Comparaison statistique
    ↓
Nouvelles données
    ↓
    🟢 PAS DE CHANGEMENT = Modèle OK
    🔴 CHANGEMENT DÉTECTÉ = Réentraîner le modèle
```

---

## 🔍 Qu'est-ce que le Data Drift?

Le **Data Drift** est un changement dans la **distribution statistique des données** entre la phase d'entraînement et la phase de production.

### Exemple Simple:

**Entraînement** (Baseline):
```
Montants: 100€ à 10,000€ (moyenne = 5,000€)
Types: TRANSFER (60%), PAYMENT (30%), CASH (10%)
Heure: Surtout entre 8h-20h
```

**Production** (Après 3 mois):
```
Montants: 50€ à 50,000€ (moyenne = 8,000€)  ⚠️ CHANGÉ!
Types: TRANSFER (40%), PAYMENT (40%), CASH (20%)  ⚠️ CHANGÉ!
Heure: Aussi la nuit (0h-6h)  ⚠️ CHANGÉ!
```

**Résultat**: 🔴 **DRIFT DÉTECTÉ!** → Réentraîner le modèle

---

## 🚀 Mise en Place - 3 Étapes

### **Étape 1: Démarrer Flask (Terminal 1)**

```powershell
cd E:\fraude_mpsa
python api_flask/app.py
```

Vous devriez voir:
```
 * Running on http://localhost:5000
```

### **Étape 2: Uploader les Données (Terminal 2)**

Pour créer une **baseline** à partir de MPSA.csv (470 MB):

**Option A - Python (recommandé):**
```powershell
cd E:\fraude_mpsa
python upload_training_data.py "E:\pipeline\MPSA.csv" --max-rows 50000 --sample-ratio 1.0
```

**Option B - PowerShell:**
```powershell
cd E:\fraude_mpsa
.\upload_data.ps1 -CsvFile "E:\pipeline\MPSA.csv" -MaxRows 50000 -SampleRatio 1.0
```

**Option C - Interface Streamlit:**
1. Lancez Streamlit: `streamlit run streamlit/app.py`
2. Allez à "🔍 Drift Monitoring"
3. Onglet "🚀 API Upload"
4. Suivez les instructions

### **Étape 3: Vérifier le Drift (Terminal 3)**

```powershell
cd E:\fraude_mpsa
python drift_monitor.py
```

Vous verrez:
```
📊 DRIFT DETECTION DASHBOARD
✅ Baseline disponible
  📅 Créée le: 2025-12-31T10:00:00
  📈 Échantillons baseline: 50000
  ✨ Features: 10 détectées

📋 Historique Drift (3 checks):
  🟢 OK (12.5%)
  🟢 OK (8.3%)
  🔴 DRIFT (35.7%)
```

---

## 📊 Comment Ça Marche Techniquement

### **Pour Données NUMÉRIQUES** (ex: montants, âge)

**Test utilisé**: **Kolmogorov-Smirnov (KS)**

```
BASELINE:           CURRENT:
│  ▁▂▃▄▅            │  ▂▃▄█▅
│ ▁█▅▂              │▂▃█▇▂
│▂█▃                │▁▂█▆
└────────────      └────────────
Moyenne: 5000     Moyenne: 8000
Écart: 2000       Écart: 3000

KS-Test: "Ces deux courbes sont-elles identiques?"
Résultat: p-value = 0.02 < 0.05 → 🔴 DRIFT
```

### **Pour Données CATÉGORIQUES** (ex: type de transaction)

**Test utilisé**: **Chi-carré (χ²)**

```
BASELINE:               CURRENT:
TRANSFER: 60% ████      TRANSFER: 40% ██
PAYMENT:  30% ███       PAYMENT:  40% ████
CASH:     10% █         CASH:     20% ██

Chi-carré Test: "Ces distributions sont-elles identiques?"
Résultat: p-value = 0.04 < 0.05 → 🔴 DRIFT
```

---

## 📋 Interprétation des Résultats

### **Status Principal**

```
🟢 PAS DE DRIFT (p-value > 0.05)
└─ Les données sont cohérentes avec la baseline
   → Continuer à utiliser le modèle

🟡 DRIFT FAIBLE (p-value 0.02-0.05)
└─ Quelques changements détectés
   → Surveiller, réentraîner bientôt

🔴 DRIFT SIGNIFICATIF (p-value < 0.02)
└─ Changements importants détectés
   → RÉENTRAÎNER LE MODÈLE MAINTENANT
```

### **Tableau Détaillé**

Quand vous vérifiez le drift, vous verrez:

```
📊 Vérification du Drift
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status Global:      🔴 DRIFT DÉTECTÉ
Features affectées: 3 sur 10
Pourcentage drift:  30%

┌─────────────┬─────────┬────────┬──────────┬────────┐
│ Feature     │ Status  │ P-Val  │ Baseline │ Actuel │
├─────────────┼─────────┼────────┼──────────┼────────┤
│ amount      │ 🔴DRIFT │ 0.001  │ 5000     │ 8000   │
│ hour        │ 🟢 OK   │ 0.42   │ 14:00    │ 14:15  │
│ type        │ 🔴DRIFT │ 0.015  │ TRANSFER │ CASH   │
│ balance_    │ 🟢 OK   │ 0.87   │ 50000    │ 52000  │
│ orig        │         │        │          │        │
│ erreur_orig │ 🟡ALRT  │ 0.08   │ 0.0      │ 0.15   │
└─────────────┴─────────┴────────┴──────────┴────────┘

📌 RECOMMANDATION:
   ⚠️  Drift détecté sur amount et type
   → Analyser les changements métier
   → Réentraîner le modèle si persistant
```

---

## ⚙️ Configuration Technique

### **Seuils par Défaut**

```python
drift_threshold = 0.05  # Niveau de confiance 95%
```

**Ce que cela signifie:**
- p-value < 0.05 = Les données ont **moins de 5% de chance** d'être identiques → DRIFT
- p-value > 0.05 = Les données sont probablement similaires → Pas de drift

### **Statistiques Calculées**

#### Pour Numériques:
- `mean`: Moyenne
- `std`: Écart-type
- `min`, `max`: Valeurs extrêmes
- `q25`, `q50`, `q75`: Quartiles (25%, 50%, 75%)

#### Pour Catégoriques:
- Distribution: Fréquence de chaque catégorie
- Comparaison: Chi-carré

---

## 🎯 Cas d'Usage Pratiques

### **Cas 1: Détection Automatique**

```python
# Lors d'une prédiction
data = {
    "amount": 15000,
    "type": "TRANSFER",
    ...
}

response = requests.post("http://localhost:5000/drift/check", json=data)
report = response.json()

if report['overall_drift']:
    print("⚠️  DRIFT DÉTECTÉ!")
    print(f"   {report['drift_percentage']}% des features affectées")
    # → Alerter le data scientist
    # → Programmer un réentraînement
```

### **Cas 2: Monitoring Batch**

```python
# Vérifier le drift sur 1000 transactions
predictions = []
for i in range(1000):
    # Faire prédiction
    report = check_drift(transaction_i)
    predictions.append(report)

drift_rate = sum(p['overall_drift'] for p in predictions) / len(predictions)
print(f"📊 Taux de drift: {drift_rate*100:.1f}%")

if drift_rate > 0.20:  # > 20%
    print("🔴 DRIFT BATCH DÉTECTÉ - Réentraîner!")
```

### **Cas 3: Monitoring Temps Réel**

```bash
# Terminal 1: Flask actif
python api_flask/app.py

# Terminal 2: Streamlit actif
streamlit run streamlit/app.py

# Interface: Allez à "🔍 Drift Monitoring"
# Vous verrez automatiquement le drift de chaque prédiction
```

---

## 🔧 Fichiers Clés

### **Code de Détection**
- `api_flask/services/drift_detection.py` - Logique principale
- `api_flask/routes/drift.py` - Endpoints API

### **Interface Web**
- `streamlit/pages/drift_monitoring.py` - Dashboard drift

### **Scripts Utilitaires**
- `upload_training_data.py` - Upload données
- `upload_data.ps1` - Upload PowerShell
- `drift_monitor.py` - Monitoring CLI

### **Données**
- `api_flask/drift_baseline.json` - Baseline sauvegardée

---

## 📞 Dépannage

### **"Aucune baseline disponible"**

**Solution**:
```bash
python upload_training_data.py "E:\pipeline\MPSA.csv"
```

### **"Connexion refusée http://localhost:5000"**

**Solution**:
```bash
cd E:\fraude_mpsa
python api_flask/app.py
```

### **"Fichier trop volumineux"**

**Solution - Option A** (réduire les données):
```bash
python upload_training_data.py "data.csv" --max-rows 10000 --sample-ratio 0.5
```

**Solution - Option B** (utiliser Streamlit upload):
```bash
streamlit run streamlit/app.py  # → Onglet "Streamlit Upload"
```

### **"p_value = NaN"**

**Cause**: Pas assez de données ou écart-type = 0

**Solution**: Augmenter la taille de la baseline

---

## 📈 Exemple Complet

```bash
# Terminal 1: Démarrer Flask
cd E:\fraude_mpsa
python api_flask/app.py

# Terminal 2: Créer baseline (attendre que Flask soit actif)
# Attendre ~30 secondes
python upload_training_data.py "E:\pipeline\MPSA.csv" --max-rows 20000

# Terminal 3: Lancer Streamlit
streamlit run streamlit/app.py

# Dans le navigateur:
# 1. Allez à "🏠 Accueil" (prediction)
# 2. Entrez des données et cliquez "Prédire"
# 3. Allez à "🔍 Drift Monitoring"
# 4. Vous verrez automatiquement le drift check!
```

---

## 🎓 Résumé Technique

| Concept | Definition | Exemple |
|---------|-----------|---------|
| **Baseline** | Distribution de référence (données d'entraînement) | 50K transactions |
| **Current** | Nouvelles données à vérifier | 1 nouvelle transaction |
| **Drift** | Changement significatif de distribution | Amount: 5K → 8K |
| **P-Value** | Probabilité que différence soit au hasard | 0.001 = 0.1% chance |
| **Seuil** | Limite pour déclarer drift | < 0.05 = drift |
| **KS-Test** | Test pour numériques | Kolmogorov-Smirnov |
| **Chi²-Test** | Test pour catégoriques | Chi-carré |
| **Action** | Réaction recommandée | Réentraîner modèle |

---

## 💡 Bonnes Pratiques

1. ✅ Créer baseline de **10K+ samples**
2. ✅ Vérifier drift **après chaque batch** (500+ prédictions)
3. ✅ **Alerter** si drift > 30%
4. ✅ **Réentraîner** dès que drift significatif
5. ✅ **Archiver** les baselines pour comparaison temporelle
6. ✅ **Monitorer** les features importantes en priorité

---

## 📞 Support

Si tu as besoin d'aide:

1. **Consulte** `DRIFT_DETECTION_GUIDE.md`
2. **Exécute** `python drift_monitor.py` pour un test
3. **Vérifies** les logs Flask pour les erreurs
4. **Checks** `api_flask/drift_baseline.json` existe

---

**Créé le**: 2025-12-31  
**Version**: 1.0  
**Status**: ✅ Production Ready
