from datetime import datetime
from typing import Dict, Any, Optional, List
from bson.objectid import ObjectId
from utils.database import db_manager
from utils.validators import Validator, ValidationError
import logging

logger = logging.getLogger(__name__)

class Item:
    """Modèle pour représenter un item"""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self._id = data.get('_id')

    @classmethod
    def find_all(cls, page: int = 1, per_page: int = 10, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """Récupère tous les items avec pagination et filtres"""
        try:
            collection = db_manager.get_collection()
            query = filters or {}
            skip = (page - 1) * per_page
            cursor = collection.find(query).skip(skip).limit(per_page)
            items = list(cursor)
            total = collection.count_documents(query)
            total_pages = (total + per_page - 1) // per_page
            has_next = page < total_pages
            has_prev = page > 1

            return {
                'items': items,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'has_next': has_next,
                    'has_prev': has_prev
                }
            }

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des items: {str(e)}")
            raise

    @classmethod
    def find_by_id(cls, item_id: str) -> Optional['Item']:
        """Trouve un item par son ID"""
        try:
            if not Validator.validate_object_id(item_id):
                raise ValidationError("ID invalide")
            collection = db_manager.get_collection()
            data = collection.find_one({"_id": ObjectId(item_id)})
            return cls(data) if data else None

        except Exception as e:
            logger.error(f"Erreur lors de la recherche de l'item {item_id}: {str(e)}")
            raise

    @classmethod
    def create(cls, data: Dict[str, Any]) -> 'Item':
        """Crée un nouvel item"""
        try:
            sanitized_data = Validator.sanitize_data(data)
            sanitized_data['created_at'] = datetime.utcnow()
            sanitized_data['updated_at'] = datetime.utcnow()
            collection = db_manager.get_collection()
            result = collection.insert_one(sanitized_data)
            sanitized_data['_id'] = result.inserted_id
            logger.info(f"Item créé avec l'ID: {result.inserted_id}")
            return cls(sanitized_data)

        except Exception as e:
            logger.error(f"Erreur lors de la création de l'item: {str(e)}")
            raise

    def update(self, data: Dict[str, Any]) -> bool:
        """Met à jour l'item"""
        try:
            if not self._id:
                raise ValidationError("Impossible de mettre à jour un item sans ID")
            sanitized_data = Validator.sanitize_data(data)
            sanitized_data['updated_at'] = datetime.utcnow()
            collection = db_manager.get_collection()
            result = collection.update_one(
                {"_id": ObjectId(self._id)},
                {"$set": sanitized_data}
            )
            if result.modified_count > 0:
                self.data.update(sanitized_data)
                logger.info(f"Item {self._id} mis à jour")
                return True
            return False

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'item {self._id}: {str(e)}")
            raise

    def delete(self) -> bool:
        """Supprime l'item"""
        try:
            if not self._id:
                raise ValidationError("Impossible de supprimer un item sans ID")
            collection = db_manager.get_collection()
            result = collection.delete_one({"_id": ObjectId(self._id)})
            if result.deleted_count > 0:
                logger.info(f"Item {self._id} supprimé")
                return True
            return False

        except Exception as e:
            logger.error(f"Erreur lors de la suppression de l'item {self._id}: {str(e)}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'item en dictionnaire"""
        return self.data

    @classmethod
    def search(cls, query: str, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Recherche d'items par texte"""
        try:
            collection = db_manager.get_collection()
            search_filter = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
            }
            return cls.find_all(page, per_page, search_filter)

        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {str(e)}")
            raise

    @classmethod
    def find_by_country(cls, country_code: str) -> List[Dict[str, Any]]:
        """Trouve tous les items ayant un code pays spécifique"""
        try:
            collection = db_manager.get_collection()
            query = {"country": country_code.upper()}
            cursor = collection.find(query)
            return list(cursor)

        except Exception as e:
            logger.error(f"Erreur lors de la recherche par pays '{country_code}': {str(e)}")
            raise

    # 🔍 Requêtes d’analyse avancées

    @classmethod
    def top_countries(cls, limit: int = 5) -> List[Dict[str, Any]]:
        """Top pays avec le plus de réservations"""
        try:
            collection = db_manager.get_collection()
            pipeline = [
                {"$group": {"_id": "$country", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]
            return list(collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Erreur top_countries: {str(e)}")
            raise

    @classmethod
    def top_hotels(cls, limit: int = 5) -> List[Dict[str, Any]]:
        """Top hôtels en nombre de réservations"""
        try:
            collection = db_manager.get_collection()
            pipeline = [
                {"$group": {"_id": "$hotel", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]
            return list(collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Erreur top_hotels: {str(e)}")
            raise

    @classmethod
    def cancellation_stats(cls) -> List[Dict[str, Any]]:
        """Statistiques sur les annulations (is_canceled)"""
        try:
            collection = db_manager.get_collection()
            pipeline = [
                {"$group": {"_id": "$is_canceled", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
            return list(collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Erreur cancellation_stats: {str(e)}")
            raise

    @classmethod
    def average_adr_by_hotel(cls) -> List[Dict[str, Any]]:
        """Tarif moyen (ADR) par type d’hôtel"""
        try:
            collection = db_manager.get_collection()
            pipeline = [
                {"$group": {"_id": "$hotel", "average_adr": {"$avg": "$adr"}}},
                {"$sort": {"average_adr": -1}}
            ]
            return list(collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Erreur average_adr_by_hotel: {str(e)}")
            raise
