from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import logging
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestionnaire de connexion à MongoDB"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
    
    def connect(self):
        """Établit la connexion à MongoDB"""
        try:
            self.client = MongoClient(
                Config.MONGO_URI,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000
            )
            
            # Test de la connexion
            self.client.admin.command('ping')
            
            self.db = self.client[Config.DATABASE_NAME]
            self.collection = self.db[Config.COLLECTION_NAME]
            
            logger.info("Connexion à MongoDB établie avec succès")
            return True
            
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            logger.error(f"Erreur de connexion à MongoDB: {str(e)}")
            raise ConnectionError(f"Impossible de se connecter à MongoDB: {str(e)}")
    
    def close(self):
        """Ferme la connexion à MongoDB"""
        if self.client is not None:
            self.client.close()
            logger.info("Connexion à MongoDB fermée")
    
    def get_collection(self):
        """Retourne la collection MongoDB"""
        if self.collection is None:
            raise RuntimeError("Base de données non initialisée. Appelez connect() d'abord.")
        return self.collection
    
    def ping(self):
        """Vérifie la connexion à MongoDB"""
        try:
            self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Erreur lors du ping MongoDB: {str(e)}")
            return False

# Instance globale du gestionnaire de base de données
db_manager = DatabaseManager()
