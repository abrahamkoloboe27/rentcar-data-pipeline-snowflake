"""
Générateur de données historiques réalistes pour une entreprise de location de véhicules.
Utilise Pydantic pour la validation des données et Faker pour la génération de données aléatoires.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from pydantic import BaseModel
from faker import Faker
import psycopg2

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes de configuration
START_DATE = datetime.now() - timedelta(days=5*365)  # Début il y a 5 ans
N_BRANCHES = 20                  # Nombre de succursales
N_CLIENTS = 100000            # Nombre de clients à générer
N_VEHICLES = 10000            # Nombre de véhicules à générer
BASE_PRICES = {                  # Prix de base journaliers en XOF
    'voiture': 10000,
    'moto': 2500,
    'vélo': 1500
}

# Initialisation de Faker avec localisation française
fake = Faker('fr_FR')

class Branch(BaseModel):
    """Représente une succursale de l'entreprise avec sa localisation géographique."""
    branch_id: int
    nom: str
    localisation: str
    latitude: float
    longitude: float

class Client(BaseModel):
    """Stocke les informations d'un client avec sa localisation associée à une succursale."""
    client_id: int
    nom: str
    prenom: str
    email: str
    telephone: str
    adresse: str
    date_creation: datetime
    branch_id: int

class Vehicle(BaseModel):
    """Décrit un véhicule avec son historique de disponibilité."""
    vehicule_id: int
    type: str
    marque: str
    modele: str
    annee_fabrication: int
    immatriculation: str
    statut: str
    branch_id: int
    date_mise_en_service: datetime
    kilometrage: int = 0

class Location(BaseModel):
    """Enregistre une transaction de location avec calcul dynamique du prix."""
    location_id: int
    client_id: int
    vehicule_id: int
    date_debut: datetime
    date_fin: datetime
    prix_total: float
    statut: str
    mode_paiement: str

class Entretien(BaseModel):
    """Track les opérations de maintenance sur les véhicules."""
    entretien_id: int
    vehicule_id: int
    date_entretien: datetime
    type_entretien: str
    description: str
    cout: float

class Facture(BaseModel):
    """Représente une facture associée à une location."""
    facture_id: int
    location_id: int
    date_facture: datetime
    montant: float
    mode_paiement: Optional[str] = None  # Made optional
    statut_paiement: str = "impayée"

class DataGenerator:
    """
    Classe principale pour générer des données historiques réalistes.
    
    Features:
    - Génération progressive avec tendances temporelles
    - Cohérence géographique entre clients et succursales
    - Modèles de prix avec inflation annuelle
    - Cycles de maintenance réalistes
    """
    
    def __init__(self):
        self.branches: List[Branch] = []
        self.clients: List[Client] = []
        self.vehicles: List[Vehicle] = []
        self.locations: List[Location] = []
        self.entretiens: List[Entretien] = []
        self.factures: List[Facture] = []
        
        # Configurations des modèles
        self.vehicle_types = ['voiture', 'moto', 'vélo']
        self.vehicle_brands = {
            'voiture': [
                'Toyota', 'Renault', 'Skoda', 'Citroën', 'Citadine', 'Kia', 
                'Peugeot', 'Volkswagen', 'Opel', 'Fiat', 'Mercedes', 'BMW', 
                'Audi', 'Clio', 'Nissan', 'Mazda', 'Seat', 
                # Marques ajoutées
                'Ferrari', 'Jaguar', 'Hyundai', 'Dacia', 
                'Tesla', 'Ford', 'Chevrolet', 'Cadillac',
                'Alfa Romeo', 'Volvo', 'Chery'
            ],
            'moto': [
                'Yamaha', 'Honda', 'Suzuki','Wave',
                'Kawasaki', 'Harley-Davidson', 
                # Marques ajoutées
                'Ducati', 'Royal Enfield', 'Bajaj Auto',
                'Triumph', 'KTM', 'CFMoto'
            ],
            'vélo': [
                # Marques existantes
                'BMC', 'Scott', 'Trek',
                # Marques ajoutées
                'Specialized', 'Cannondale', 
                'Giant Bicycles'
            ]
        }

        self.maintenance_types = ['réparation', 'préventif', 'nettoyage', 
                                  'vidange'
                                  ]
        self.payment_methods = ['carte', 'espèces', 'mobile_money', 'wave']
        
        # Coordonnées des villes africaines
        self.cities = {
            'Abidjan': (5.3599, -4.0083),
            'Cotonou': (5.0667, -0.55),
            'Porto-Novo': (-13.1167, -172.25),
            'Brazzaville': (-15.7833, 28.2167),
            'Alger': (36.8189, 3.0573),
            'Kigali': (-1.9472, 30.0636),
            'Bujumbura': (-20.2006, 27.8828),
            'Ouagadougou': (-17.4667, 41.55),
            'Dodoma': (-13.4167, 32.5833),
            'Bamako': (-1.9472, 29.9722),
            'Yaoundé': (-1.9472, 29.9722),  
            'Bangui': (-16.9167, 28.2167),
            'Dakar': (14.7167, -17.4677),
            'Lagos': (6.5244, 3.3792),
            'Nairobi': (-1.2864, 36.8172),
            'Johannesburg': (-26.2041, 28.0473),
            'Kara': (-1.9472, 29.9722),
            'Lubumbashi': (-16.9167, 28.2167),
            'Mogadishu': (-17.4667, 41.55),
            'Kinshasa': (-4.3333, 15.3333),
            'Libreville': (-1.9472, 29.9722),
            'Mbabane': (-1.9472, 29.9722),
            'Tunis': (-8.5167, 41.55),
            'Cairo': (30.0444, 31.2357), 
            'Alexandria': (31.2001, 29.9187), 
            'Casablanca': (33.5731, -7.5898), 
            'Cape Town': (-33.9249, 18.4241), 
            'Durban': (-29.8587, 31.0218), 
            'Luanda': (-8.8383, 13.2344), 
            'Accra': (5.6037, -0.1870), 
            'Addis Ababa': (9.0306, 38.7400), 
            'Pretoria': (-25.7479, 28.2293), 
            'Dar es Salaam': (-6.7924, 39.2083)
        }

    def generate_branches(self) -> None:
        """Génère les succursales avec des coordonnées géographiques réelles."""
        logger.info("Génération des succursales...")
        cities = list(self.cities.items())
        for i, (city, (lat, lon)) in enumerate(cities[:N_BRANCHES], 1):
            self.branches.append(Branch(
                branch_id=i,
                nom=f"Agence {city}",
                localisation=city,
                latitude=lat + random.uniform(-0.1, 0.1),
                longitude=lon + random.uniform(-0.1, 0.1)
            ))

    def generate_clients(self) -> None:
        logger.info(f"Début de la génération des {N_CLIENTS} clients...")
        created = 0
        
        # Distribute client creation dates across the entire period
        date_range = datetime.now() - START_DATE
        days_per_batch = date_range.days / N_CLIENTS
        
        for i in range(1, N_CLIENTS + 1):
            branch = random.choice(self.branches)
            # Calculate creation date based on client index to ensure even distribution
            target_date = START_DATE + timedelta(days=int(i * days_per_batch))
            # Add some randomness around the target date (±30 days)
            create_date = target_date + timedelta(days=random.randint(-30, 30))
            # Ensure date doesn't exceed current date
            create_date = min(create_date, datetime.now())
            
            self.clients.append(Client(
                client_id=i,
                nom=fake.last_name(),
                prenom=fake.first_name(),
                email=fake.unique.email(),
                telephone=fake.phone_number(),
                adresse=fake.street_address() + f", {branch.localisation}",
                date_creation=create_date,
                branch_id=branch.branch_id
            ))
            
            created += 1
            if created % 100 == 0:
                logger.debug(f"Progression: {created}/{N_CLIENTS} clients générés")
        logger.info(f"{len(self.clients)} clients générés avec succès")

    def generate_vehicles(self) -> None:
        """Produit des véhicules avec historique de mise en service réaliste."""
        logger.info("Génération des véhicules...")
        for i in range(1, N_VEHICLES + 1):
            v_type = random.choice(self.vehicle_types)
            brand = random.choice(self.vehicle_brands[v_type])
            year = random.randint(2015, 2023)
            
            self.vehicles.append(Vehicle(
                vehicule_id=i,
                type=v_type,
                marque=brand,
                modele=fake.bothify(text=f"{brand} ??##"),
                annee_fabrication=year,
                immatriculation=fake.license_plate(),
                statut='disponible',
                branch_id=random.choice(self.branches).branch_id,
                date_mise_en_service=fake.date_time_between(
                    start_date=datetime(year, 1, 1),
                    end_date=START_DATE + timedelta(days=365*2)
                )
            ))

    def generate_historical_data(self) -> None:
        """
        Simule l'historique sur 5 ans avec :
        - Augmentation progressive du traffic
        - Saisonnalité hebdomadaire/annuelle
        - Évolution des prix avec inflation
        """
        logger.info("Début de la génération historique...")
        current_date = START_DATE
        while current_date < datetime.now():
            # Variation saisonnière
            daily_factor = 1 + 0.3 * (current_date.month/12)  + random.uniform(-0.1, 0.1)
            n_rentals = int(random.randint(5, 15) * daily_factor)
            
            self.generate_daily_rentals(current_date, n_rentals)
            self.generate_maintenance(current_date)
            
            # Avance d'un jour
            current_date += timedelta(days=1)
        logger.info("Génération historique terminée.")

    def calculate_price(self, v_type: str, duration: timedelta, date: datetime) -> float:
        """
        Calcule le prix avec inflation annuelle de 5%.
        Base_price * (1 + inflation)^années * durée_en_jours
        """
        years = (date.year - START_DATE.year) + (date.month/12)
        inflated_price = BASE_PRICES[v_type] * (1.05 ** years)
        return round(inflated_price * duration.total_seconds() / 86400, 2)

    def get_rental_duration(self, v_type: str) -> timedelta:
        """Retourne une durée de location réaliste selon le type de véhicule."""
        patterns = {
            'voiture': [24, 48, 72, 168, 240 ],  # heures
            'moto': [2, 4, 6, 8, 24, 48, 72],
            'vélo': [1, 2, 4, 8, 24, 48, 72]
        }
        return timedelta(hours=random.choice(patterns[v_type]))

    def generate_daily_rentals(self, date: datetime, n_rentals: int) -> None:
        """Génère les locations pour un jour donné avec gestion de la disponibilité."""
        available_vehicles = [v for v in self.vehicles 
                            if v.statut == 'disponible'
                            and v.date_mise_en_service < date]
        
        for _ in range(min(n_rentals, len(available_vehicles))):
            vehicle = random.choice(available_vehicles)
            client = random.choice([c for c in self.clients 
                                   if c.date_creation < date])
            
            duration = self.get_rental_duration(vehicle.type)
            price = self.calculate_price(vehicle.type, duration, date)
            
            # Create location first
            new_location = Location(
                location_id=len(self.locations)+1,
                client_id=client.client_id,
                vehicule_id=vehicle.vehicule_id,
                date_debut=date,
                date_fin=date + duration,
                prix_total=price,
                statut='terminée',
                mode_paiement=random.choice(self.payment_methods)
            )
            self.locations.append(new_location)
            
            # Then create invoice using the stored location
            is_paid = random.random() < 0.85
            self.factures.append(Facture(
                facture_id=len(self.factures)+1,
                location_id=new_location.location_id,
                date_facture=date,
                montant=price,
                mode_paiement=new_location.mode_paiement if is_paid else None,
                statut_paiement='payée' if is_paid else 'impayée'
            ))
            
            # Mise à jour du statut et kilométrage
            vehicle.statut = 'en location'
            vehicle.kilometrage += random.randint(10, 300)

    def generate_maintenance(self, date: datetime) -> None:
        """Planifie des opérations de maintenance aléatoires."""
        if random.random() < 0.15:  # 15% chance quotidienne
            vehicle = random.choice(self.vehicles)
            vehicle.statut = 'maintenance'
            
            self.entretiens.append(Entretien(
                entretien_id=len(self.entretiens)+1,
                vehicule_id=vehicle.vehicule_id,
                date_entretien=date,
                type_entretien=random.choice(self.maintenance_types),
                description=fake.sentence(),
                cout=random.uniform(5000, 50000)
            ))
            
            # Temps de réparation réaliste
            repair_time = random.randint(1, 7)
            vehicle.statut = 'disponible' if random.random() < 0.8 else 'hors_service'

def load_to_postgres(data: DataGenerator, connection_string: str) -> None:
    """
    Charge les données générées dans PostgreSQL.
    Structure optimisée pour les insertions massives.
    """
    logger.info("Début du chargement en base...")
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            # Insertion des succursales
            cursor.executemany(
                """INSERT INTO Branches 
                (branch_id, nom, localisation)
                VALUES (%s, %s, %s)
                ON CONFLICT (branch_id) DO NOTHING
                """,
                [(b.branch_id, b.nom, b.localisation) for b in data.branches]
            )
            logger.info(f"{len(data.branches)} succursales insérées")
            
            # Insertion des clients (updated to model_dump)
            cursor.executemany(
                """INSERT INTO Clients 
                (client_id, nom, prenom, email, telephone, adresse, date_creation, branch_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (client_id) DO NOTHING
                """,
                [tuple(c.model_dump().values()) for c in data.clients]  # Changed dict() to model_dump()
            )
            logger.info(f"{len(data.clients)} clients insérés")
            
            # Insertion des véhicules (updated to model_dump)
            cursor.executemany(
                """INSERT INTO Vehicles 
                (vehicule_id, type, marque, modele, annee_fabrication, 
                immatriculation, statut, branch_id, date_mise_en_service, kilometrage)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (vehicule_id) DO NOTHING
                """,
                [tuple(v.model_dump().values()) for v in data.vehicles]  # Changed dict() to model_dump()
            )
            
            # Insertion des locations (updated to model_dump)
            cursor.executemany(
                """INSERT INTO Locations 
                (location_id, client_id, vehicule_id, date_debut, date_fin, 
                prix_total, statut, mode_paiement)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (location_id) DO NOTHING
                """,
                [tuple(l.model_dump().values()) for l in data.locations]  # Changed dict() to model_dump()
            )
            
            # Insertion des entretiens (updated to model_dump)
            cursor.executemany(
                """INSERT INTO Entretiens 
                (entretien_id, vehicule_id, date_entretien, type_entretien, 
                description, cout)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (entretien_id) DO NOTHING
                """,
                [tuple(e.model_dump().values()) for e in data.entretiens]  # Changed dict() to model_dump()
            )
            logger.info(f"{len(data.entretiens)} entretiens insérés")
            
            # Insertion des factures
            cursor.executemany(
                """INSERT INTO Factures 
                (facture_id, location_id, date_facture, montant, mode_paiement, statut_paiement)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (facture_id) DO NOTHING
                """,
                [tuple(f.model_dump().values()) for f in data.factures]
            )
            logger.info(f"{len(data.factures)} factures insérées")

    logger.info("Données chargées avec succès dans PostgreSQL")

if __name__ == "__main__":
    # Configuration de la génération
    generator = DataGenerator()
    generator.generate_branches()
    generator.generate_clients()
    generator.generate_vehicles()
    generator.generate_historical_data()
    
    # Exemple de connexion PostgreSQL
    load_to_postgres(generator, "postgresql://postgres:postgres@localhost:6543/rentcar")