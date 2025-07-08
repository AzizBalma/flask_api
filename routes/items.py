from flask import Blueprint, request, jsonify, current_app
from bson import json_util
from models.item import Item
from utils.validators import Validator, ValidationError
import logging
import json

logger = logging.getLogger(__name__)
items_bp = Blueprint('items', __name__)

def create_response(data=None, message=None, status_code=200):
    response = {}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    response['status'] = 'success' if status_code < 400 else 'error'
    return jsonify(response), status_code

def parse_json_response(data):
    return json.loads(json_util.dumps(data))

@items_bp.route('/items', methods=['GET'])
def get_items():
    try:
        page = request.args.get('page', '1')
        per_page = request.args.get('per_page', '10')
        page, per_page = Validator.validate_pagination_params(page, per_page)
        search_query = request.args.get('search', '').strip()

        if search_query:
            result = Item.search(search_query, page, per_page)
        else:
            result = Item.find_all(page, per_page)

        items = parse_json_response(result['items'])
        response_data = {
            'items': items,
            'pagination': result['pagination']
        }
        return create_response(data=response_data)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des items: {str(e)}")
        return create_response(message=f"Erreur serveur: {str(e)}", status_code=500)

@items_bp.route('/items/<item_id>', methods=['GET'])
def get_item(item_id):
    try:
        if not Validator.validate_object_id(item_id):
            return create_response(message="ID invalide", status_code=400)
        item = Item.find_by_id(item_id)
        if not item:
            return create_response(message="Item non trouvé", status_code=404)
        item_data = parse_json_response(item.to_dict())
        return create_response(data=item_data)
    except ValidationError as e:
        return create_response(message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'item {item_id}: {str(e)}")
        return create_response(message=f"Erreur serveur: {str(e)}", status_code=500)

@items_bp.route('/items', methods=['POST'])
def create_item():
    try:
        if not request.is_json:
            return create_response(message="Content-Type doit être application/json", status_code=400)
        data = request.get_json()
        if not data:
            return create_response(message="Données JSON requises", status_code=400)
        item = Item.create(data)
        item_data = parse_json_response(item.to_dict())
        return create_response(data=item_data, message="Item créé avec succès", status_code=201)
    except ValidationError as e:
        return create_response(message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'item: {str(e)}")
        return create_response(message=f"Erreur serveur: {str(e)}", status_code=500)

@items_bp.route('/items/<item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        if not Validator.validate_object_id(item_id):
            return create_response(message="ID invalide", status_code=400)
        if not request.is_json:
            return create_response(message="Content-Type doit être application/json", status_code=400)
        data = request.get_json()
        if not data:
            return create_response(message="Données JSON requises", status_code=400)
        item = Item.find_by_id(item_id)
        if not item:
            return create_response(message="Item non trouvé", status_code=404)
        updated = item.update(data)
        if updated:
            item_data = parse_json_response(item.to_dict())
            return create_response(data=item_data, message="Item mis à jour avec succès")
        else:
            return create_response(message="Aucune modification effectuée", status_code=304)
    except ValidationError as e:
        return create_response(message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'item {item_id}: {str(e)}")
        return create_response(message=f"Erreur serveur: {str(e)}", status_code=500)

@items_bp.route('/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        if not Validator.validate_object_id(item_id):
            return create_response(message="ID invalide", status_code=400)
        item = Item.find_by_id(item_id)
        if not item:
            return create_response(message="Item non trouvé", status_code=404)
        deleted = item.delete()
        if deleted:
            return create_response(message="Item supprimé avec succès")
        else:
            return create_response(message="Erreur lors de la suppression", status_code=500)
    except ValidationError as e:
        return create_response(message=str(e), status_code=400)
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'item {item_id}: {str(e)}")
        return create_response(message=f"Erreur serveur: {str(e)}", status_code=500)

@items_bp.route('/items/bulk', methods=['POST'])
def create_bulk_items():
    try:
        if not request.is_json:
            return create_response(message="Content-Type doit être application/json", status_code=400)
        data = request.get_json()
        if not data or not isinstance(data, list):
            return create_response(message="Liste d'items requise", status_code=400)
        if len(data) > 100:
            return create_response(message="Maximum 100 items par requête", status_code=400)

        created_items = []
        errors = []
        for i, item_data in enumerate(data):
            try:
                item = Item.create(item_data)
                created_items.append(parse_json_response(item.to_dict()))
            except Exception as e:
                errors.append(f"Item {i}: {str(e)}")

        response_data = {
            'created_items': created_items,
            'created_count': len(created_items),
            'errors': errors
        }

        return create_response(data=response_data, message=f"{len(created_items)} items créés avec succès", status_code=201)
    except Exception as e:
        logger.error(f"Erreur lors de la création en masse: {str(e)}")
        return create_response(message=f"Erreur serveur: {str(e)}", status_code=500)

# Ajout des routes avancées ici...
# (La suite avec les requêtes avancées sera ajoutée maintenant que le document est chargé.)
