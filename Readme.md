# 🚗💾 ETL Pipeline pour le Data Warehouse de Location de Véhicules

![ETL Pipeline](https://img.shields.io/badge/ETL-Pipeline-009688?style=for-the-badge&logo=apachespark&logoColor=white)
![License MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

🌟 **Un pipeline de données complet pour optimiser la gestion des locations de véhicules** 🌟

## 🎯 Table des Matières

| Section                       | Description                                                      |
| ----------------------------- | ---------------------------------------------------------------- |
| [✨ Fonctionnalités](#-fonctionnalités) | Points clés du projet                                          |
| [🏗 Architecture](#-architecture)      | Structure technique du pipeline                                |
| [🛠 Technologies](#-technologies)      | Stack technique et badges                                      |
| [🚀 Démarrage Rapide](#-démarrage-rapide)| Lancer le projet en 2 minutes                                |
| [📦 Structure du Projet](#-structure-du-projet) | Organisation des fichiers                |
| [⚙ Configuration](#-configuration)    | Guide de paramétrage détaillé                                  |

## ✨ Fonctionnalités

- 🧱 **Architecture Médaille** (Bronze/Silver/Gold) garantissant la qualité des données
- 🚀 **Extraction haute performance** depuis PostgreSQL
- 🌟 **Modélisation en étoile** avec dimensions et faits
- 📊 **Analyse temporelle** avancée via la dimension date
- 🔒 **Sécurité** grâce à la gestion des variables d'environnement
- 📈 **Optimisation des coûts** avec stockage Parquet

## 🏗 Architecture

```mermaid
graph LR
    A[(📁 PostgreSQL)] -->|Extraction| B[[🟤 Bronze]]
    B -->|Transformation| C[[⚪ Silver]]
    C -->|Chargement| D[[🟡 Gold]]
    D --> E[(❄️ Snowflake)]
```

### 📐 Schéma en Étoile

```mermaid
pie
    title Répartition des Tables
    "Dimensions" : 5
    "Faits" : 3
```

## 🛠 Technologies

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake&logoColor=white)](https://snowflake.com)
[![Parquet](https://img.shields.io/badge/Apache_Parquet-4EA94B?logo=apacheparquet&logoColor=white)](https://parquet.apache.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1C1C1C?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Dotenv](https://img.shields.io/badge/Python_Dotenv-ECD53F?logo=python&logoColor=black)](https://pypi.org/project/python-dotenv/)

## 🚀 Démarrage Rapide

### Prérequis

- 🐍 Python 3.10+
- 📦 Paquets requis :

```bash
pip install -r requirements.txt
```

### Configuration Initiale

1. Créez votre fichier `.env` :

```bash
cp .env.example .env
```

2. Modifiez les variables d'environnement :

```ini
# 🐘 PostgreSQL
POSTGRES_URL="postgresql://user:password@localhost:5432/rentcar"

# ❄️ Snowflake
SNOWFLAKE_ACCOUNT="votre-compte"
SNOWFLAKE_USER="votre-user"
SNOWFLAKE_PASSWORD="votre-password"
```

### Exécution

```bash
python etl.py
```

## 📦 Structure du Projet

```plaintext
📁 location-pipeline-project/
├── 📁 bronze/      # Données brutes
├── 📁 silver/      # Données transformées
├── 📁 gold/        # Données prêtes pour l'analyse
├── 📜 etl.py       # 🐍 Script principal
└── 📜 README.md    # 📖 Documentation
```

## ⚙ Configuration Avancée

### 🔌 Connexion PostgreSQL

| Paramètre          | Valeur par défaut       |
|--------------------|-------------------------|
| `POSTGRES_URL`     | postgresql://user:password@localhost:5432/rentcar |

### ❄️ Paramètres Snowflake

| Variable d'Environnement | Description                |
|--------------------------|----------------------------|
| `SNOWFLAKE_ACCOUNT`      | Identifiant du compte      |
| `SNOWFLAKE_WAREHOUSE`    | Entrepôt de calcul         |

## 🤝 Contribuer

[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat)](https://makeapullrequest.com)

1. 🍴 Fork le projet
2. 📥 Clone le repository
3. ✨ Crée une branche (`git checkout -b feature/ma-fonctionnalité`)
4. 💾 Fais tes modifications
5. 📤 Push les changements (`git push origin feature/ma-fonctionnalité`)
6. 🔄 Ouvre une Pull Request

## 📄 Licence

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

**Fait avec ❤️ par Abraham KOLOBOE**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin)](https://www.linkedin.com/in/abraham-zacharie-koloboe-data-science-ia-generative-llms-machine-learning/)
