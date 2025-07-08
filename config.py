import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration de base pour l'application"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    MONGO_URI = os.environ.get('MONGO_URI')
    DATABASE_NAME = os.environ.get('DATABASE_NAME', 'mydatabase')
    COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'items')
    
    # Validation des variables d'environnement
    @staticmethod
    def validate_config():
        """Valide que les variables d'environnement requises sont présentes"""
        required_vars = ['MONGO_URI']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            raise ValueError(f"Variables d'environnement manquantes: {', '.join(missing_vars)}")

class DevelopmentConfig(Config):
    """Configuration pour le développement"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Configuration pour la production"""
    DEBUG = False
    FLASK_ENV = 'production'

# Dictionnaire des configurations
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}