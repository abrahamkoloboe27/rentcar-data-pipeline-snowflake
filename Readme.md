# 🚗📊 ETL Pipeline pour le Data Warehouse de Location de Véhicules

Ce projet met en œuvre une chaîne ETL complète pour extraire des données depuis une base de données PostgreSQL, les transformer selon un schéma en étoile (star schema) et les charger dans Snowflake. Le pipeline suit une architecture en **médallion** avec trois niveaux : **Bronze**, **Silver** et **Gold**, garantissant la traçabilité et la qualité des données.


## Table des Matières

| Section                   | Description                                        |
| ------------------------- | -------------------------------------------------- |
| [Introduction](#introduction)      | Contexte et objectifs du projet                  |
| [Architecture](#architecture)      | Schéma en étoile et architecture en médallion    |
| [Technologies](#technologies)      | Outils et frameworks utilisés                    |
| [Installation](#installation)      | Pré-requis et configuration environnementale      |
| [Usage](#usage)                    | Exécution du pipeline ETL et déploiement           |
| [Structure du Projet](#structure-du-projet)  | Organisation des fichiers et dossiers            |
| [Configuration](#configuration)    | Paramétrage des connexions et variables d'environnement |
| [Journalisation](#journalisation)  | Gestion des logs                                   |
| [Contributeurs](#contributeurs)    | Qui a contribué au projet                          |
| [Licence](#licence)                | Licence du projet                                  |

## Introduction

Ce projet vise à :
- **Extraire** les données depuis une base PostgreSQL,  
- **Transformer** ces données en un format exploitable pour l'analyse (via un schéma en étoile),  
- **Charger** les données transformées dans Snowflake pour un reporting et une analyse avancée.

L'usage de **Parquet** à chaque étape garantit une conservation historique et une traçabilité des données (architecture en médallion).

## Architecture

L'architecture adoptée est à la fois modulaire et performante. Voici un schéma simplifié :
Diagramme de l'Architecture

```mermaid
graph TD
    A[PostgreSQL (Source)] --> B[Extraction (Bronze)]
    B --> C[Transformation (Silver)]
    C --> D[Chargement (Gold) dans Snowflake]
```

### Schéma en Étoile (Star Schema)

Les données sont organisées en :
- **Tables de Dimensions** (clients, véhicules, branches, dates, paiements)
- **Tables de Faits** (locations, factures, maintenances)

| Tables de Dimensions    | Tables de Faits           |
| ----------------------- | ------------------------- |
| `DIM_CLIENT`            | `FACT_LOCATION`         |
| `DIM_VEHICULE`          | `FACT_FACTURE`          |
| `DIM_BRANCH`            | `FACT_MAINTENANCE`      |
| `DIM_DATE`              |                           |
| `DIM_PAIEMENT` (Optionnel)|                           |


## Technologies

- **Extraction et Transformation :** Python, Pandas, Polars (optionnel), SQLAlchemy  
- **Stockage Intermédiaire :** Format Parquet (Bronze, Silver, Gold)  
- **Chargement :** Snowflake via `snowflake-sqlalchemy`  
- **Journalisation :** module `logging` de Python  
- **Environnements & Gestion de Variables :** Dotenv

## Installation

### Prérequis

- Python 3.10+
- PostgreSQL (base source)
- Compte Snowflake et accès approprié
- Environnement virtuel (optionnel mais recommandé)

### Installation des dépendances

Exécutez la commande suivante :
```bash
pip install pandas pyarrow sqlalchemy snowflake-sqlalchemy python-dotenv
```

## Usage

### Configuration des Variables d'Environnement

Créez un fichier `.env` à la racine du projet avec les paramètres suivants :
```dotenv
# PostgreSQL
POSTGRES_URL=postgresql://postgres:postgres@localhost:6543/rentcar

# Snowflake
SNOWFLAKE_ACCOUNT=<your_account>
SNOWFLAKE_USER=<your_user>
SNOWFLAKE_PASSWORD=<your_password>
SNOWFLAKE_DATABASE=LOCATION_ETL
SNOWFLAKE_SCHEMA=LOCATION
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_ROLE=<your_role>
```

### Exécution du Pipeline ETL

Pour lancer le processus ETL, exécutez :
```bash
python etl.py
```
Le script suit les étapes suivantes :
1. **Extraction (Bronze) :** Récupération des données depuis PostgreSQL et sauvegarde au format Parquet.
2. **Transformation (Silver) :** Transformation des données en schéma en étoile, création des dimensions et des faits, sauvegarde en Parquet.
3. **Chargement (Gold) :** Importation des données dans Snowflake avec un contexte configuré via SQL Worksheet.

Les logs sont enregistrés dans le dossier `logs` pour un suivi détaillé.

## Structure du Projet

```plaintext
├── etl.py                   # Script principal ETL
├── .env                     # Fichier de configuration (à créer)
├── logs/                    # Répertoire des logs
│   └── etl.log              # Journalisation du pipeline
├── bronze/                  # Données brutes extraites (format Parquet)
├── silver/                  # Données transformées (format Parquet)
├── gold/                    # Données chargées dans Snowflake (format Parquet)
├── README.md                # Ce fichier Readme
└── requirements.txt         # Liste des dépendances
```

## Configuration

### Postgres

- **URL de Connexion :** définie dans `.env` sous `POSTGRES_URL`
- **Tables Sources :** `Clients`, `Vehicles`, `Branches`, `Locations`, `Factures`, `Entretiens`

### Snowflake

- **Paramètres de Connexion :** configurés via `SNOWFLAKE_CONN_PARAMS` dans le script ETL
- **Schéma Ciblé :** `LOCATION` dans la base `LOCATION_ETL`
- **Contexte d'Exécution :**
  - Database : `LOCATION_ETL`
  - Warehouse : `COMPUTE_WH`
  - Schéma : `LOCATION`

## Journalisation

Les logs détaillés sont générés et stockés dans le dossier `logs/etl.log`. Ils permettent de suivre l'exécution, le succès ou les erreurs des différentes étapes du pipeline ETL. Utilisez ce fichier pour déboguer et surveiller l'état du pipeline.

## Contributeurs

- **Abraham KOLOBOE** – Data Engineer & Data Scientist  
  [LinkedIn](https://www.linkedin.com/in/abraham-zacharie-koloboe-data-science-ia-generative-llms-machine-learning/)


## Licence

Ce projet est sous licence [MIT](LICENSE).


## Remarques Finales

- 💡 **Conseil :** Pour des mises à jour incrémentales ultérieures, considérez l'ajout de mécanismes de CDC (Change Data Capture) ou de batchs incrémentaux.
- 🚀 **Prochaines étapes :** Implémenter des dashboards interactifs directement dans Snowflake ou via un outil BI (Tableau, Power BI).


N'hésitez pas à contribuer ou à proposer des améliorations !

Happy ETL-ing! 🚀✨