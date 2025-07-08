from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os
from config import config, Config
from utils.database import db_manager
from routes.items import items_bp

def create_app(config_name=None):
    """Factory function pour créer l'application Flask"""
    
    # Créer l'application Flask
    app = Flask(__name__)
    
    # Configuration
    config_name = config_name or os.getenv('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])
    
    # Valider la configuration
    try:
        Config.validate_config()
    except ValueError as e:
        app.logger.error(f"Erreur de configuration: {str(e)}")
        raise
    
    # Configuration CORS
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
    
    # Configuration des logs
    configure_logging(app)
    
    # Enregistrer les blueprints
    app.register_blueprint(items_bp, url_prefix='/api/v1')
    
    # Gestionnaire d'erreurs globaux
    register_error_handlers(app)
    
    # Initialiser la base de données
    with app.app_context():
        try:
            db_manager.connect()
            app.logger.info("Base de données initialisée avec succès")
        except Exception as e:
            app.logger.error(f"Erreur d'initialisation de la base de données: {str(e)}")
            raise
    
    # Route de base
    @app.route('/')
    def index():
        return jsonify({
            'message': 'API Flask MongoDB - Bienvenue!',
            'version': '1.0.0',
            'endpoints': [
                'GET /api/v1/items - Récupérer tous les items',
                'GET /api/v1/items/<id> - Récupérer un item par ID',
                'POST /api/v1/items - Créer un nouvel item',
                'PUT /api/v1/items/<id> - Mettre à jour un item',
                'DELETE /api/v1/items/<id> - Supprimer un item',
                'POST /api/v1/items/bulk - Créer plusieurs items',
                'GET /api/v1/health - Vérification de santé'
            ]
        })
    
    return app

def configure_logging(app):
    """Configure les logs de l'application"""
    if not app.debug:
        # Configuration pour la production
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )
    else:
        # Configuration pour le développement
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )

def register_error_handlers(app):
    """Enregistre les gestionnaires d'erreurs globaux"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Endpoint non trouvé',
            'error': 'Not Found'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'status': 'error',
            'message': 'Méthode non autorisée',
            'error': 'Method Not Allowed'
        }), 405
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'status': 'error',
            'message': 'Requête invalide',
            'error': 'Bad Request'
        }), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Erreur serveur: {str(error)}')
        return jsonify({
            'status': 'error',
            'message': 'Erreur interne du serveur',
            'error': 'Internal Server Error'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Exception non gérée: {str(error)}')
        return jsonify({
            'status': 'error',
            'message': 'Une erreur inattendue s\'est produite',
            'error': 'Internal Server Error'
        }), 500

if __name__ == '__main__':
    app = create_app()
    
    # Nettoyage à la fermeture
    import atexit
    atexit.register(lambda: db_manager.close())
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        app.logger.error(f"Erreur lors du démarrage de l'application: {str(e)}")
        raise