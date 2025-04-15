CREATE TABLE  IF NOT EXISTS Clients (
    client_id INT PRIMARY KEY,
    nom VARCHAR(255),
    prenom VARCHAR(255),
    email VARCHAR(255),
    telephone VARCHAR(20),
    adresse TEXT,
    date_creation TIMESTAMP,
    branch_id INT
);

CREATE TABLE IF NOT EXISTS Branches (
    branch_id INT PRIMARY KEY,
    nom VARCHAR(255),
    localisation VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT
);

-- Table Véhicules
CREATE TABLE IF NOT EXISTS Vehicles (
    vehicule_id INT PRIMARY KEY,
    type VARCHAR(50),
    marque VARCHAR(100),
    modele VARCHAR(100),
    annee_fabrication INT,
    immatriculation VARCHAR(20),
    statut VARCHAR(50),
    branch_id INT REFERENCES Branches(branch_id),
    date_mise_en_service TIMESTAMP,
    kilometrage INT
);

-- Table Locations
CREATE TABLE IF NOT EXISTS Locations (
    location_id SERIAL PRIMARY KEY,
    client_id INT NOT NULL,
    vehicule_id INT NOT NULL,
    date_debut TIMESTAMP NOT NULL,
    date_fin TIMESTAMP,
    prix_total DECIMAL(10,2) NOT NULL,
    statut VARCHAR(50) DEFAULT 'confirmée',
    mode_paiement VARCHAR(50),  -- Added missing column
    FOREIGN KEY (client_id) REFERENCES Clients(client_id),
    FOREIGN KEY (vehicule_id) REFERENCES Vehicles(vehicule_id)
);

-- Table Factures
CREATE TABLE IF NOT EXISTS Factures (
    facture_id SERIAL PRIMARY KEY,
    location_id INT NOT NULL,
    date_facture TIMESTAMP DEFAULT NOW(),
    montant DECIMAL(10,2) NOT NULL,
    mode_paiement VARCHAR(50),
    statut_paiement VARCHAR(20) DEFAULT 'impayée' CHECK (statut_paiement IN ('payée', 'impayée', 'remboursée')),
    FOREIGN KEY (location_id) REFERENCES Locations(location_id)
);

-- Table Entretiens
CREATE TABLE IF NOT EXISTS Entretiens (
    entretien_id SERIAL PRIMARY KEY,
    vehicule_id INT NOT NULL,
    date_entretien TIMESTAMP DEFAULT NOW(),
    type_entretien VARCHAR(100),
    description TEXT,
    cout DECIMAL(10,2),
    FOREIGN KEY (vehicule_id) REFERENCES Vehicles(vehicule_id)
);
