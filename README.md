# API REST Flask avec MongoDB Atlas

Une API RESTful professionnelle construite avec Flask et MongoDB Atlas, avec import de données CSV depuis Kaggle.

## 🚀 Fonctionnalités

- **API REST complète** : CRUD complet avec pagination et recherche
- **Architecture modulaire** : Code organisé en modules réutilisables
- **Import CSV** : Script d'importation de données depuis Kaggle
- **Validation robuste** : Validation des données et gestion d'erreurs
- **Logging avancé** : Système de logs complet
- **Configuration flexible** : Support des environnements dev/prod
- **CORS activé** : Prêt pour les applications frontend

## 📋 Prérequis

- Python 3.8+
- MongoDB Atlas (compte gratuit)
- Compte Kaggle (pour les données de test)

## 🛠️ Installation

### 1. Cloner le projet

```bash
git clone flask_api
cd flask_api
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration de MongoDB Atlas

1. Aller sur [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Créer un **cluster gratuit** (Shared - M0)
3. Créer une **base de données** (ex: `mydatabase`)
4. Créer une **collection** (ex: `items`)
5. Créer un **utilisateur** avec mot de passe
6. Récupérer l'**URI de connexion**

### 5. Configuration des variables d'environnement

```bash
cp .env.example .env
```

Éditer le fichier `.env` avec vos informations :

```env
MONGO_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
DATABASE_NAME=mydatabase
COLLECTION_NAME=items
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

## 🚀 Démarrage

### Lancer l'API

```bash
python app.py
```

L'API sera disponible sur `http://localhost:5000`

### Importer des données CSV

```bash
# Télécharger un dataset depuis Kaggle
# Exemple : https://www.kaggle.com/datasets/...

# Importer le fichier CSV
python scripts/import_data.py votre_fichier.csv

# Avec options avancées
python scripts/import_data.py votre_fichier.csv --drop-existing --batch-size 500
```

## 📊 Endpoints de l'API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/` | Page d'accueil avec documentation |
| `GET` | `/api/v1/items` | Récupérer tous les items (avec pagination) |
| `GET` | `/api/v1/items?search=query` | Rechercher des items |
| `GET` | `/api/v1/items/<id>` | Récupérer un item par ID |
| `POST` | `/api/v1/items` | Créer un nouvel item |
| `PUT` | `/api/v1/items/<id>` | Mettre à jour un item |
| `DELETE` | `/api/v1/items/<id>` | Supprimer un item |
| `POST` | `/api/v1/items/bulk` | Créer plusieurs items |
| `GET` | `/api/v1/health` | Vérification de santé |

## 🔍 Exemples d'utilisation

### Récupérer tous les items avec pagination

```bash
curl "http://localhost:5000/api/v1/items?page=1&per_page=10"
```

### Rechercher des items

```bash
curl "http://localhost:5000/api/v1/items?search=python&page=1&per_page=5"
```

### Créer un nouvel item

```bash
curl -X POST "http://localhost:5000/api/v1/items" \
  -H "Content-Type: application/json" \
  -d '{"name": "Nouvel Item", "description": "Description de l\"item"}'
```

### Mettre à jour un item

```bash
curl -X PUT "http://localhost:5000/api/v1/items/60f7b3b3b3b3b3b3b3b3b3b3" \
  -H "Content-Type: application/json" \
  -d '{"name": "Item Modifié", "description": "Nouvelle description"}'
```

## 🏗️ Structure du projet

```
flask_api/
├── app.py                 # Application Flask principale
├── config.py              # Configuration centralisée
├── models/
│   └── item.py           # Modèle Item avec logique métier
├── routes/
│   └── items.py          # Routes API pour les items
├── utils/
│   ├── database.py       # Gestionnaire de base de données
│   └── validators.py     # Validateurs de données
├── scripts/
│   └── import_data.py    # Script d'importation CSV
├── requirements.txt      # Dépendances Python
├── .env.example         # Exemple de variables d'environnement
└── README.md           # Documentation
```

## 🔧 Fonctionnalités avancées

### Pagination

Tous les endpoints de liste supportent la pagination :

```
GET /api/v1/items?page=2&per_page=20
```

### Recherche

Recherche textuelle dans les champs `name` et `description` :

```
GET /api/v1/items?search=python
```

### Validation

- Validation automatique des ObjectId MongoDB
- Nettoyage des données d'entrée
- Gestion des erreurs avec messages explicites

### Logging

- Logs structurés avec niveaux (DEBUG, INFO, ERROR)
- Logs sauvegardés dans des fichiers
- Tracking des erreurs et performances

## 🧪 Tests

```bash
# Installer les dépendances de test
pip install pytest pytest-flask pytest-cov

# Lancer les tests
pytest

# Avec couverture de code
pytest --cov=.
```

## 📦 Déploiement

### Avec Gunicorn (Production)

```bash
# Installer Gunicorn
pip install gunicorn

# Lancer en production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Variables d'environnement pour production

```env
FLASK_ENV=production
FLASK_CONFIG=production
SECRET_KEY=your-very-secure-secret-key
```

## 🛡️ Sécurité

- Validation stricte des données d'entrée
- Gestion sécurisée des variables d'environnement
- Protection contre les injections NoSQL
- CORS configuré pour les domaines autorisés

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :

1. Vérifier la [documentation](#-endpoints-de-lapi)
2. Consulter les [logs](#-fonctionnalités-avancées)
3. Ouvrir une issue sur GitHub

## 📈 Roadmap

- [ ] Authentification JWT
- [ ] Rate limiting
- [ ] Cache Redis
- [ ] Tests automatisés
- [ ] Documentation Swagger/OpenAPI
- [ ] Monitoring avec Prometheus
- [ ] Container Docker
