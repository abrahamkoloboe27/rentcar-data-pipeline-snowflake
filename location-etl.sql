-- Fichier : create_dw_schema.sql

-- =======================================
-- 1. TABLES DE DIMENSIONS
-- =======================================

-- Dimension Date
CREATE OR REPLACE TABLE DIM_DATE (
    DATE_KEY      INT PRIMARY KEY,         -- Format YYYYMMDD ou entier représentant la date
    DATE_COMPLETE DATE,                    -- Date complète
    DAY           INT,                     -- Jour (numérique)
    MONTH         INT,                     -- Mois (numérique)
    YEAR          INT,                     -- Année
    QUARTER       INT,                     -- Trimestre
    DAY_OF_WEEK   VARCHAR(10),             -- Jour de la semaine (ex. "Lundi")
    LABEL_DATE    VARCHAR(50)              -- Libellé formaté (ex. "01 Janvier 2020")
);

-- Dimension Client
CREATE OR REPLACE TABLE DIM_CLIENT (
    CLIENT_KEY     INT PRIMARY KEY,         -- Clé de dimension unique
    CLIENT_ID      INT,                     -- Identifiant source du client
    NOM            VARCHAR(100),
    PRENOM         VARCHAR(100),
    EMAIL          VARCHAR(150),
    TELEPHONE      VARCHAR(20),
    ADRESSE        VARCHAR(255),
    DATE_CREATION  DATE                     -- Date de création du client
    BRANCH_ID      INT                      -- Référence à DIM_BRANCH (si applicable)
    -- CONSTRAINT FK_DIM_BRANCH FOREIGN KEY (BRANCH_ID) REFERENCES DIM_BRANCH(BRANCH_ID)
);

-- Dimension Véhicule
CREATE OR REPLACE TABLE DIM_VEHICULE (
    VEHICULE_KEY       INT PRIMARY KEY,     -- Clé de dimension unique
    VEHICULE_ID        INT,                 -- Identifiant source du véhicule
    TYPE               VARCHAR(50),         -- Type : voiture, vélo, moto, etc.
    MARQUE             VARCHAR(100),
    MODELE             VARCHAR(100),
    ANNEE_FABRICATION  INT,
    IMMATRICULATION    VARCHAR(50),
    STATUT             VARCHAR(50)          -- Statut initial (disponible, en location, etc.)
    BRANCH_ID          INT                   -- Référence à DIM_BRANCH (si applicable)
    -- CONSTRAINT FK_DIM_BRANCH FOREIGN KEY (BRANCH_ID) REFERENCES DIM_BRANCH(BRANCH_ID)
);

-- Dimension Branch
CREATE OR REPLACE TABLE DIM_BRANCH (
    BRANCH_KEY    INT PRIMARY KEY,          -- Clé de dimension unique
    BRANCH_ID     INT,                      -- Identifiant source de la branche
    NOM_BRANCH    VARCHAR(100),
    LOCALISATION  VARCHAR(150)
);

-- Dimension Paiement (Optionnelle)
CREATE OR REPLACE TABLE DIM_PAIEMENT (
    PAIEMENT_KEY    INT PRIMARY KEY,         -- Clé de dimension unique
    MODE_PAIEMENT   VARCHAR(50),             -- Mode de paiement : carte, espèces, virement, etc.
    STATUT_PAIEMENT VARCHAR(20)              -- État : payée, impayée, remboursée
);

-- =======================================
-- 2. TABLES DE FAITS
-- =======================================

-- Fait Location
CREATE OR REPLACE TABLE FACT_LOCATION (
    RENTAL_ID         INT PRIMARY KEY,       -- Identifiant de la location
    DATE_KEY_DEBUT    INT,                   -- Clé de la date de début (référence à DIM_DATE)
    DATE_KEY_FIN      INT,                   -- Clé de la date de fin (référence à DIM_DATE)
    CLIENT_KEY        INT,                   -- Référence à DIM_CLIENT
    VEHICULE_KEY      INT,                   -- Référence à DIM_VEHICULE
    BRANCH_KEY        INT,                   -- Référence à DIM_BRANCH (si applicable)
    DUREE_LOCATION    FLOAT,                 -- Durée en heures (calculée à partir de date_debut et date_fin)
    PRIX_TOTAL        DECIMAL(10,2),         -- Montant total de la location
    STATUT_LOCATION   VARCHAR(50)            -- Statut de la location (confirmée, en cours, terminée, annulée)
    -- CONSTRAINT FK_DIM_CLIENT FOREIGN KEY (CLIENT_KEY) REFERENCES DIM_CLIENT(CLIENT_KEY),
    -- CONSTRAINT FK_DIM_VEHICULE FOREIGN KEY (VEHICULE_KEY) REFERENCES DIM_VEHICULE(VEHICULE_KEY),
    -- CONSTRAINT FK_DIM_BRANCH FOREIGN KEY (BRANCH_KEY) REFERENCES DIM_BRANCH(BRANCH_KEY)
);

-- Fait Facture
CREATE OR REPLACE TABLE FACT_FACTURE (
    FACTURE_ID        INT PRIMARY KEY,       -- Identifiant de la facture
    RENTAL_ID         INT,                   -- Référence à la location (peut être utile pour les analyses transverses)
    CLIENT_KEY        INT,                   -- Référence à DIM_CLIENT pour la traçabilité directe
    DATE_KEY_FACTURE  INT,                   -- Clé de la date de facturation (référence à DIM_DATE)
    MONTANT           DECIMAL(10,2),         -- Montant facturé
    MODE_PAIEMENT     VARCHAR(50),           -- Mode de paiement
    STATUT_PAIEMENT   VARCHAR(20)            -- Statut du paiement (payée, impayée, remboursée)
    -- CONSTRAINT FK_FACT_CLIENT FOREIGN KEY (CLIENT_KEY) REFERENCES DIM_CLIENT(CLIENT_KEY)
);

-- Fait Maintenance
CREATE OR REPLACE TABLE FACT_MAINTENANCE (
    ENTRETIEN_ID         INT PRIMARY KEY,   -- Identifiant de l'opération de maintenance
    VEHICULE_KEY         INT,               -- Référence à DIM_VEHICULE
    DATE_KEY_ENTRETIEN   INT,               -- Clé de la date d'entretien (référence à DIM_DATE)
    BRANCH_KEY           INT,               -- Référence à DIM_BRANCH (si le véhicule change de branche)
    COUT                 DECIMAL(10,2),     -- Coût de l'entretien
    TYPE_ENTRETIEN       VARCHAR(100)       -- Type d'entretien (réparation, préventif, nettoyage)
    -- CONSTRAINT FK_MAINT_VEHICULE FOREIGN KEY (VEHICULE_KEY) REFERENCES DIM_VEHICULE(VEHICULE_KEY),
    -- CONSTRAINT FK_MAINT_BRANCH FOREIGN KEY (BRANCH_KEY) REFERENCES DIM_BRANCH(BRANCH_KEY)
);
