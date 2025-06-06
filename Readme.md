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
graph TD
    %% Dimensions
    DCL[DIM_CLIENT]:::dim
    DVH[DIM_VEHICULE]:::dim
    DBR[DIM_BRANCH]:::dim
    DDT[DIM_DATE]:::dim
    DPA[DIM_PAIEMENT]:::dim
    
    %% Faits
    FLOC(FACT_LOCATION):::fact
    FFAC(FACT_FACTURE):::fact
    FMAINT(FACT_MAINTENANCE):::fact
    
    %% Relations
    DCL --> FLOC
    DVH --> FLOC
    DBR --> FLOC
    DDT --> FLOC
    
    DCL --> FFAC
    DVH --> FFAC
    DDT --> FFAC
    DPA --> FFAC
    
    DVH --> FMAINT
    DBR --> FMAINT
    DDT --> FMAINT

    classDef dim fill:#4CAF50,color:white
    classDef fact fill:#2196F3,color:white
```


## 🛠 Technologies

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?logo=snowflake&logoColor=white)](https://snowflake.com)
[![Parquet](https://img.shields.io/badge/Apache_Parquet-4EA94B?logo=apacheparquet&logoColor=white)](https://parquet.apache.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1C1C1C?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Dotenv](https://img.shields.io/badge/Python_Dotenv-ECD53F?logo=python&logoColor=black)](https://pypi.org/project/python-dotenv/)
[![Apache Superset](https://img.shields.io/badge/Superset-EC6A37?logo=apache&logoColor=white)](https://superset.apache.org/)

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
SNOWFLAKE_DATABASE="votre-database"
SNOWFLAKE_SCHEMA="votre-schema"
SNOWFLAKE_WAREHOUSE="votre-warehouse"
```

### A faire avant de lancer les scripts
- Créer les tables dans la base de données PostgreSQL
  - Installer postgresql avec docker :
    ```ini
    docker run --name postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres
    ```
  - Créer les tables dans la base de données PostgreSQL
    ```ini
    docker exec -it postgres psql -U postgres 
    psql -f postgres-init.sql -d rentcar
    ```
- Créer les tables dans Snowflake
  - Créer un compte Snowflake
  - Créer une base de données
  - Créer un schéma
  - Créer un warehouse
  - Créer les tables dans Snowflake à l'aide d'un worksheet: Utiliser le fichier `snowflake-init.sql` 
### Exécution

```ini
# Data Generation (PostgreSQL)
python data_generation.py
# ETL Pipeline : Bronze -> Silver -> Gold 
# PostgreSQL -> Snowflake
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
| `SNOWFLAKE_USER`         | Utilisateur Snowflake      |
| `SNOWFLAKE_PASSWORD`     | Mot de passe Snowflake     |
| `SNOWFLAKE_DATABASE`     | Base de données Snowflake  |
| `SNOWFLAKE_SCHEMA`       | Schéma Snowflake          |

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


**Fait avec ❤️ par Abraham KOLOBOE**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?logo=linkedin)](https://www.linkedin.com/in/abraham-zacharie-koloboe-data-science-ia-generative-llms-machine-learning/)
