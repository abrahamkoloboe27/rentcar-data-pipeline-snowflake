import os
from dotenv import load_dotenv
import logging
import pandas as pd
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL

load_dotenv()
# Configuration du système de logs
# Create logs directory first
os.makedirs('logs', exist_ok=True)

# Then configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Répertoires pour sauvegarder les fichiers parquet
BRONZE_DIR = "bronze"
SILVER_DIR = "silver"
GOLD_DIR = "gold"  # Optionnel, par exemple si vous souhaitez garder une copie locale "finale"

# Création des dossiers si nécessaire
for dossier in [BRONZE_DIR, SILVER_DIR, GOLD_DIR]:
    logging.info(f"Création du dossier {dossier}")
    os.makedirs(dossier, exist_ok=True)

# =====================================
# 1. Extraction des données depuis Postgres (Bronze)
# =====================================

# Configuration de la connexion Postgres
POSTGRES_URL = "postgresql://postgres:postgres@localhost:6543/rentcar"  # à ajuster
engine_pg = create_engine(POSTGRES_URL)

def extract_data():
    logger.info("Début de l'extraction des données depuis PostgreSQL")
    try:
        clients_df = pd.read_sql("SELECT * FROM Clients", engine_pg)
        logging.info("Extraction des clients réussie")
        Vehicles_df = pd.read_sql("SELECT * FROM Vehicles", engine_pg)
        logging.info("Extraction des véhicules réussie")
        branches_df = pd.read_sql("SELECT * FROM Branches", engine_pg)  # si applicable
        logging.info("Extraction des branches réussie")
        locations_df = pd.read_sql("SELECT * FROM Locations", engine_pg)
        logging.info("Extraction des locations réussie")
        factures_df = pd.read_sql("SELECT * FROM Factures", engine_pg)
        logging.info("Extraction des factures réussie")
        entretiens_df = pd.read_sql("SELECT * FROM Entretiens", engine_pg)
        logging.info("Extraction des entretiens réussie")

        # Sauvegarde des données brutes au format parquet (Bronze)
        clients_df.to_parquet(os.path.join(BRONZE_DIR, "clients.parquet"), index=False)
        logging.info("Clients sauvegardés au format parquet")
        Vehicles_df.to_parquet(os.path.join(BRONZE_DIR, "Vehicles.parquet"), index=False)
        logging.info("Véhicules sauvegardés au format parquet")
        branches_df.to_parquet(os.path.join(BRONZE_DIR, "branches.parquet"), index=False)
        logging.info("Branches sauvegardées au format parquet")
        locations_df.to_parquet(os.path.join(BRONZE_DIR, "locations.parquet"), index=False)
        logging.info("Locations sauvegardées au format parquet")
        factures_df.to_parquet(os.path.join(BRONZE_DIR, "factures.parquet"), index=False)
        logging.info("Factures sauvegardées au format parquet")
        entretiens_df.to_parquet(os.path.join(BRONZE_DIR, "entretiens.parquet"), index=False)
        logging.info("Entretiens sauvegardés au format parquet")

        return {
            "clients": clients_df,
            "Vehicles": Vehicles_df,
            "branches": branches_df,
            "locations": locations_df,
            "factures": factures_df,
            "entretiens": entretiens_df
        }
    except Exception as e:
        logger.error(f"Échec de l'extraction: {str(e)}")
        raise

# =====================================
# 2. Transformation vers le modèle en étoile (Silver)
# =====================================

def generate_dim_date(start, end):
    # Génère une dimension date couvrant toute la période
    logging.info(f"Génération de la dimension Date {start} à {end} ")
    date_range = pd.date_range(start=start, end=end)
    records = []
    for date in date_range:
        records.append({
            "date_key": int(date.strftime("%Y%m%d")),
            "date_complete": date.date(),
            "day": date.day,
            "month": date.month,
            "year": date.year,
            "quarter": date.quarter,
            "day_of_week": date.day_name(),
            "label_date": date.strftime("%d %B %Y")
        })
    return pd.DataFrame(records)

def transform_data(raw_data):
    try:
        # Dimension Client (ajout de branch_id)
        dim_client = raw_data["clients"].copy()
        dim_client["client_key"] = dim_client["client_id"]
        dim_client = dim_client[["client_key", "client_id", "nom", "prenom", "email", 
                                "telephone", "adresse", "date_creation", "branch_id"]]
        
        # Dimension Véhicule (ajout de branch_id)
        dim_vehicule = raw_data["Vehicles"].copy()
        dim_vehicule["vehicule_key"] = dim_vehicule["vehicule_id"]
        dim_vehicule = dim_vehicule[["vehicule_key", "vehicule_id", "type", "marque", 
                                    "modele", "annee_fabrication", "immatriculation", 
                                    "statut", "branch_id"]]

        # Dimension Branch (correction du nom)
        dim_branch = raw_data["branches"].copy()
        dim_branch["branch_key"] = dim_branch["branch_id"]
        dim_branch.rename(columns={"nom": "nom_branch"}, inplace=True)
        dim_branch = dim_branch[["branch_key", "branch_id", "nom_branch", "localisation"]]

        # Dimension Paiement (nouvelle)
        paiement_data = pd.concat([
            raw_data["factures"][["mode_paiement", "statut_paiement"]].drop_duplicates()
        ])
        dim_paiement = pd.DataFrame(paiement_data).reset_index(drop=True)
        dim_paiement["paiement_key"] = dim_paiement.index + 1
        dim_paiement = dim_paiement[["paiement_key", "mode_paiement", "statut_paiement"]]
        dim_paiement.to_parquet(os.path.join(SILVER_DIR, "dim_paiement.parquet"), index=False)

        # Fact Location - Corrected version
        fact_location = raw_data["locations"].copy()
        
        # Standardize column names (include date columns)
        column_renames = {
            'location_id': 'rental_id',
            'vehicle_id': 'vehicule_id',
            'statut': 'statut_location',
            'client_id': 'client_key',
            'start_date': 'date_debut',  # Add if source uses different names
            'end_date': 'date_fin'       # Add if source uses different names
        }
        fact_location = fact_location.rename(columns=column_renames, errors='ignore')
        
        # Verify date columns exist
        if 'date_debut' not in fact_location or 'date_fin' not in fact_location:
            missing = [col for col in ['date_debut', 'date_fin'] if col not in fact_location]
            raise KeyError(f"Missing date columns: {missing}")

        # Standardize column names (preserve vehicule_id for merge)
        column_renames = {
            'location_id': 'rental_id',
            'vehicle_id': 'vehicule_id',  # Ensure source column is correctly mapped
            'statut': 'statut_location',
            'client_id': 'client_key',
        }
        fact_location = fact_location.rename(columns=column_renames, errors='ignore')
        
        # Create vehicule_key after renaming
        fact_location['vehicule_key'] = fact_location['vehicule_id']
        
        # Merge branch key from vehicles
        vehicles = raw_data["Vehicles"].rename(columns={
            'vehicle_id': 'vehicule_id',
            'branch_id': 'branch_key'
        }, errors='ignore')
        
        # Debugging log
        logger.info(f"Fact location columns before merge: {fact_location.columns.tolist()}")
        
        fact_location = fact_location.merge(
            vehicles[['vehicule_id', 'branch_key']],
            on='vehicule_id',
            how='left'
        )

        # Process dates and duration
        for time_col in ['date_debut', 'date_fin']:
            fact_location[time_col] = pd.to_datetime(fact_location[time_col])
            fact_location[f'date_key_{time_col.split("_")[1]}'] = fact_location[time_col].dt.strftime('%Y%m%d').astype(int)
        
        fact_location['duree_location'] = (fact_location['date_fin'] - fact_location['date_debut']).dt.total_seconds() / 3600

        # Select final columns
        final_columns = [
            'rental_id', 'date_key_debut', 'date_key_fin',
            'client_key', 'vehicule_key', 'branch_key',
            'duree_location', 'prix_total', 'statut_location'
        ]
        fact_location = fact_location[final_columns]
        
        fact_location.to_parquet(os.path.join(SILVER_DIR, "fact_location.parquet"), index=False)


        # Fait Facture
        # Facture: Factures
        fact_facture = raw_data['factures'].merge(  # Changed from 'Factures' to 'factures'
            raw_data['locations'][['location_id', 'client_id', 'vehicule_id']],
            on='location_id',
            how='left'
        )
        
        # Create surrogate keys using dimension tables
        fact_facture = fact_facture.merge(
            dim_client[['client_id', 'client_key']],
            on='client_id',
            how='left'
        )
        
        fact_facture = fact_facture.merge(
            dim_vehicule[['vehicule_id', 'vehicule_key']],
            on='vehicule_id',
            how='left'
        )
        
        
        fact_facture["date_facture"] = pd.to_datetime(fact_facture["date_facture"])
        fact_facture["date_key_facture"] = fact_facture["date_facture"].dt.strftime("%Y%m%d").astype(int)
        fact_facture = fact_facture[["facture_id", "location_id", "client_key", "date_key_facture",
                                     "montant", "mode_paiement", "statut_paiement"]]
        logging.info(f"Dimension Facture transformée : {fact_facture.head(5)} ")
        fact_facture.to_parquet(os.path.join(SILVER_DIR, "fact_facture.parquet"), index=False)
        logging.info("Dimension Facture sauvegardée au format parquet")
        
        # Fait Maintenance (ajout de branch_key)
        fact_maintenance = raw_data["entretiens"].copy()
        fact_maintenance["vehicule_key"] = fact_maintenance["vehicule_id"]
        
        # Récupérer branch_key depuis dim_vehicule
        vehicle_branch_mapping = dim_vehicule[["vehicule_key", "branch_id"]].copy()
        vehicle_branch_mapping.rename(columns={"branch_id": "branch_key"}, inplace=True)
        fact_maintenance = fact_maintenance.merge(
            vehicle_branch_mapping,
            on="vehicule_key",
            how="left"
        )
        
        fact_maintenance["date_entretien"] = pd.to_datetime(fact_maintenance["date_entretien"])
        fact_maintenance["date_key_entretien"] = fact_maintenance["date_entretien"].dt.strftime("%Y%m%d").astype(int)
        fact_maintenance = fact_maintenance[["entretien_id", "vehicule_key", "date_key_entretien", 
                                           "branch_key", "cout", "type_entretien"]]

        # Generate date dimension - FIXED VERSION
        # Convert integer dates back to datetime format
        start_date = pd.to_datetime(
            fact_location['date_key_debut'].astype(str), 
            format='%Y%m%d'
        ).min().date()
        
        end_date = pd.to_datetime(
            fact_location['date_key_fin'].astype(str), 
            format='%Y%m%d'
        ).max().date()
        
        dim_date = generate_dim_date(start_date, end_date)
        dim_date.to_parquet(os.path.join(SILVER_DIR, "dim_date.parquet"), index=False)

        # Return updated dictionary with new dim_paiement
        return {
            "dim_client": dim_client,
            "dim_vehicule": dim_vehicule,
            "dim_branch": dim_branch,
            "dim_date": dim_date,
            "dim_paiement": dim_paiement,
            "fact_location": fact_location,
            "fact_facture": fact_facture,
            "fact_maintenance": fact_maintenance
        }
    except Exception as e:
        logger.error(f"Échec de la transformation: {str(e)}")
        raise

# =====================================
# 3. Chargement vers Snowflake (Gold)
# =====================================

from sqlalchemy import create_engine, text  # Add text import

def load_to_snowflake(tables: dict):
    logger.info("Initialisation du chargement Snowflake")
    try:
        # Configuration de la connexion Snowflake (adaptée à vos paramètres)
        SNOWFLAKE_CONN_PARAMS = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'database': os.getenv('SNOWFLAKE_DATABASE'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'role': os.getenv('SNOWFLAKE_ROLE'),
        }
        snowflake_url = URL(**SNOWFLAKE_CONN_PARAMS)
        engine_sf = create_engine(snowflake_url)
        logging.info("Connexion Snowflake établie")
    
        # Create schema if not exists with proper SQL syntax
        with engine_sf.begin() as conn:
            conn.execute(text("USE DATABASE LOCATION_ETL"))
            conn.execute(text("USE WAREHOUSE COMPUTE_WH"))
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS LOCATION"))
            conn.execute(text("USE SCHEMA LOCATION"))
            logger.info("Contexte Snowflake configuré")

        # Pour chaque table...
        for table_name, df in tables.items():
            logger.info(f"Chargement de la table {table_name} ...")
            
            # Save local copy first
            df.to_parquet(os.path.join(GOLD_DIR, f"{table_name}.parquet"), index=False)
            
            # Fully qualified table name
            qualified_table_name = f"LOCATION_ETL.LOCATION.{table_name.upper()}"
            
            try:
                # Create and load data with schema specification
                df.to_sql(
                    name=table_name,
                    schema='LOCATION',
                    con=engine_sf,
                    if_exists='replace',
                    index=False,
                    chunksize=10000,
                    method='multi'
                )
                logging.info(f"Table {qualified_table_name} chargée avec succès")
            except Exception as table_error:
                logger.error(f"Erreur lors du chargement de {qualified_table_name}: {str(table_error)}")
                raise
            logging.info(f"Table {table_name} sauvegardée localement")
            
            # Create and load data in one step
            df.to_sql(
                table_name, 
                engine_sf, 
                if_exists='replace', 
                index=False, 
                chunksize=10000
            )
            logging.info(f"Table {table_name} chargée dans Snowflake")
            
        logger.info("Chargement terminé.")
        
    except Exception as e:
        logger.error(f"Échec du chargement Snowflake: {str(e)}")
        raise
    finally:
        logger.info("Nettoyage des ressources Snowflake")
        engine_sf.dispose() if 'engine_sf' in locals() else None

# =====================================
# 4. Pipeline Principal
# =====================================

def main():
    """Main ETL pipeline function that orchestrates the extraction, transformation and loading of data."""
    try:
        logger.info("=== Démarrage du pipeline ETL ===")
        raw_data = extract_data()
        transformed_tables = transform_data(raw_data)
        load_to_snowflake(transformed_tables)
        logger.info("=== Pipeline ETL terminé avec succès ===")
    except Exception as e:
        logger.error(f"Échec critique du pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    main()
