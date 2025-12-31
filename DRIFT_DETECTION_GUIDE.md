# 📊 Guide Complet: Détecter les Changements dans les Données (Data Drift)

## 🎯 Concept Principal

Le **Data Drift** détecte quand les données changent significativement par rapport à la baseline (données d'entraînement).

### Pourquoi c'est important?
- ❌ Si les données changent → le modèle devient moins précis
- ✅ Détection du drift → signal pour réentraîner le modèle

---

## 📈 Méthodes de Détection

### 1️⃣ **Pour les Données NUMÉRIQUES**
Test: **Kolmogorov-Smirnov (KS)**

**Idea**: Compare deux distributions
- **Baseline**: Distribution des données d'entraînement
- **Current**: Distribution des données actuelles

**Exemple**:
```
Baseline: Age moyen = 35 ans, Std = 10
Current:  Age moyen = 50 ans, Std = 15  ❌ DRIFT!
```

**Formule KS**:
```
D = max |F_baseline(x) - F_current(x)|
p_value = probabilité que D soit dû au hasard

Si p_value < 0.05 → DRIFT DÉTECTÉ ✅
```

### 2️⃣ **Pour les Données CATÉGORIQUES**
Test: **Chi-carré (χ²)**

**Idea**: Compare les distributions de catégories

**Exemple**:
```
Baseline: 
  Type A: 60%, Type B: 30%, Type C: 10%

Current:
  Type A: 40%, Type B: 40%, Type C: 20%  ❌ DRIFT!
```

**Interprétation**:
```
Si p_value < 0.05 → DRIFT DÉTECTÉ ✅
```

---

## 🚀 Comment Utiliser le Système

### **Étape 1: Créer une Baseline**

#### Option A: Via Streamlit
1. Allez à l'onglet "🔍 Drift Monitoring"
2. Cliquez sur "📤 Streamlit Upload"
3. Uploadez votre fichier CSV d'entraînement (< 200 MB)
4. Cliquez "🔄 Créer baseline"

#### Option B: Via API Python
```bash
python upload_training_data.py "E:\pipeline\MPSA.csv"
```

#### Option C: Via PowerShell
```powershell
.\upload_data.ps1 -CsvFile "E:\pipeline\MPSA.csv"
```

### **Étape 2: Faire des Prédictions**

1. Allez à "🏠 Accueil" (page de prédiction)
2. Remplissez les données de transaction
3. Cliquez "Prédire"

### **Étape 3: Vérifier le Drift**

1. Allez à "🔍 Drift Monitoring"
2. Cherchez la section "🔍 Vérification du Drift"
3. Le système compare automatiquement avec la baseline

---

## 📋 Interprétation des Résultats

### **Tableau de Drift Detection**

| Status | P-Value | Signification |
|--------|---------|---------------|
| 🟢 OK | > 0.05 | Pas de drift, données normales |
| 🟡 Attention | 0.02-0.05 | Drift faible, à surveiller |
| 🔴 DRIFT | < 0.02 | Drift significatif, réentraîner |

### **Exemple de Résultat**

```
Status Global:      🔴 DRIFT DÉTECTÉ
Features affectées: 3/10
Pourcentage drift:  30%

Détail par feature:
  amount        🔴 Drift   p=0.001  (Mean: 5000 → 8000)
  hour          🟢 OK      p=0.42
  balance_orig  🔴 Drift   p=0.015  (Mean: 50000 → 35000)
  type          🟢 OK      p=0.87
```

---

## 🔧 Configuration Technique

### **Seuil de Drift**
```python
drift_threshold = 0.05  # p-value < 0.05 = DRIFT
```

### **Ce que le Système Mesure**

#### Numériques:
- Mean (moyenne)
- Std (écart-type)
- Min/Max
- Quartiles (Q25, Q50, Q75)

#### Catégoriques:
- Distribution des catégories
- Fréquence de chaque classe

---

## 📊 Exemple Complet

### **Baseline créée** (données d'entraînement)
```
amount:
  type: numeric
  mean: 5000.0
  std: 2000.0
  min: 100.0
  max: 25000.0

type:
  type: categorical
  distribution: {
    "TRANSFER": 0.6,
    "PAYMENT": 0.3,
    "OTHER": 0.1
  }
```

### **Nouvelle prédiction**
```
{
  "step": 500,
  "amount": 12000,  # Même plage
  "type": "TRANSFER",
  "hour": 14,
  "balance_orig": 30000,
  ...
}
```

### **Résultat Drift Check**
```json
{
  "overall_drift": false,
  "drift_count": 0,
  "total_features": 10,
  "drift_percentage": 0.0,
  "features": {
    "amount": {
      "drift": false,
      "p_value": 0.45,
      "type": "numeric",
      "baseline_mean": 5000.0,
      "current_mean": 12000.0
    },
    "type": {
      "drift": false,
      "p_value": 0.82,
      "type": "categorical"
    }
  }
}
```

---

## ⚠️ Quand Réentraîner?

**Réentraîner le modèle si:**

1. ✅ **Drift >= 30%** des features affectées
2. ✅ **P-value < 0.01** sur une feature importante
3. ✅ **Performance baisse** (moins de 5% de prédictions correctes)
4. ✅ **Changement domaine** (nouvelle région, saison, produit)

### Processus de Réentraînement:

```mermaid
1. Détecter drift ❌
   ↓
2. Collecter nouvelles données
   ↓
3. Réentraîner le modèle (ML pipeline)
   ↓
4. Valider la nouvelle version
   ↓
5. Créer nouvelle baseline
   ↓
6. Deployer nouveau modèle
```

---

## 🛠️ API Endpoints

### **Créer une Baseline**
```bash
POST /drift/baseline/create
Content-Type: application/json

[
  {"amount": 5000, "type": "TRANSFER", ...},
  {"amount": 8000, "type": "PAYMENT", ...},
  ...
]

Response:
{
  "status": "SUCCESS",
  "baseline_summary": {
    "total_samples": 1000,
    "features": ["amount", "type", ...],
    "created_at": "2025-12-31T10:00:00"
  }
}
```

### **Vérifier le Drift**
```bash
POST /drift/check
Content-Type: application/json

{
  "amount": 12000,
  "type": "TRANSFER",
  "hour": 14,
  ...
}

Response:
{
  "overall_drift": false,
  "drift_percentage": 15.0,
  "features": {
    "amount": {"drift": false, "p_value": 0.45}
  }
}
```

### **État de la Baseline**
```bash
GET /drift/summary

Response:
{
  "status": "BASELINE_EXISTS",
  "baseline_created": "2025-12-31T10:00:00",
  "baseline_samples": 1000,
  "features": ["amount", "type", ...]
}
```

---

## 📈 Visualisation dans Streamlit

La page "🔍 Drift Monitoring" affiche:

1. **État actuel**
   - ✅ Baseline disponible ou ❌ Non
   - Nombre de samples
   - Features disponibles

2. **Tableau de drift**
   - Status (🟢/🟡/🔴)
   - P-Value
   - Baseline vs Current

3. **Recommandations**
   - Actions à prendre
   - Si réentraînement nécessaire

---

## 💡 Tips & Tricks

### **Optimiser la Détection**

1. **Baseline volumineuse** (10K+ samples)
   ```bash
   python upload_training_data.py "data.csv" --max-rows 50000
   ```

2. **Rééchantillonner** si trop de données
   ```bash
   python upload_training_data.py "data.csv" --sample-ratio 0.5
   ```

3. **Monitorer régulièrement**
   - Vérifier le drift après chaque prédiction batch
   - Consulter les graphiques de tendance

### **Déboguer un Drift**

Si drift détecté:
1. Vérifie les valeurs p-value (< 0.01 = fort drift)
2. Identifie les features affectées
3. Analyse les changements métier (saison? région? prix?)
4. Décide si c'est normal (pattern) ou anomalie

---

## 📞 Questions Fréquentes

**Q: Pourquoi p-value = 0.05?**
R: Standard statistique (95% de confiance)

**Q: Comment gérer les valeurs manquantes?**
R: Exclure les NaN avant le drift check

**Q: Baseline vs Model?**
R: Baseline = données, Model = prédictions

**Q: Fréquence de vérification?**
R: Après chaque batch de prédictions (idéalement)

**Q: Comment recalibrer?**
R: Créer nouvelle baseline après réentraînement

---

## 🎓 Résumé

| Concept | Explication |
|---------|-------------|
| **Data Drift** | Changement de distribution des données |
| **Baseline** | Distribution de référence (entraînement) |
| **KS Test** | Test pour données numériques |
| **Chi² Test** | Test pour données catégoriques |
| **P-Value** | Probabilité que différence soit au hasard |
| **Seuil** | P < 0.05 = Drift détecté |
| **Action** | Si drift → Réentraîner le modèle |

