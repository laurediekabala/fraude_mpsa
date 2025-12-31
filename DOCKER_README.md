# 🐳 Docker Deployment - Quick Start

## 🚀 Démarrage Rapide

### **Windows (PowerShell)**

```powershell
# Démarrer les services
.\docker-management.ps1 up

# Arrêter les services
.\docker-management.ps1 down

# Voir les logs
.\docker-management.ps1 logs
```

### **Linux/Mac (Makefile)**

```bash
# Démarrer les services
make up

# Arrêter les services
make down

# Voir les logs
make logs
```

### **Docker Compose Direct**

```bash
# Build et démarrer
docker-compose up --build -d

# Arrêter
docker-compose down

# Voir logs
docker-compose logs -f
```

---

## 📍 Accès aux Services

Une fois les services lancés:

```
API:        http://localhost:5000
Streamlit:  http://localhost:8501
```

**Vérifier la santé:**
```bash
curl http://localhost:5000/health
```

---

## 📋 Commandes Principales

| Windows (PowerShell) | Linux/Mac (Makefile) | Utilité |
|---|---|---|
| `.\docker-management.ps1 up` | `make up` | Démarrer |
| `.\docker-management.ps1 down` | `make down` | Arrêter |
| `.\docker-management.ps1 restart` | `make restart` | Redémarrer |
| `.\docker-management.ps1 logs` | `make logs` | Voir logs |
| `.\docker-management.ps1 status` | `make status` | État services |
| `.\docker-management.ps1 health` | `make health` | Santé services |

---

## 🐛 Troubleshooting

### Les services ne se lancent pas

```bash
# Vérifier les logs
docker-compose logs -f

# Rebuild sans cache
docker-compose build --no-cache
docker-compose up -d
```

### Port 5000 ou 8501 déjà utilisé

```bash
# Voir quel processus utilise le port
lsof -i :5000                    # Linux/Mac
netstat -ano | findstr :5000     # Windows
```

### Erreur "connection refused" entre conteneurs

```bash
# Vérifier que les deux conteneurs tournent
docker-compose ps

# Redémarrer
docker-compose restart
```

---

## 📚 Documentation Complète

Voir: **[DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md)**

Contient:
- Architecture complète
- Configuration production
- Monitoring avec Prometheus
- Déploiement cloud (AWS, GCP, etc.)
- Bonnes pratiques de sécurité

---

## ✅ Checklist Pré-Production

- [ ] Images testées localement
- [ ] Health checks configurés
- [ ] Volumes persistants pour baseline
- [ ] Logs limités (max 10MB)
- [ ] Utilisateur non-root actif
- [ ] Multi-stage build optimisé
- [ ] Reverse proxy (Nginx) configuré
- [ ] Certificats SSL si HTTPS

---

**Status**: ✅ Prêt pour production  
**Version**: 1.0  
**Dernière mise à jour**: 2025-12-31
