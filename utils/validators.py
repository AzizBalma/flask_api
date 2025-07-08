from bson.objectid import ObjectId
from bson.errors import InvalidId
import re
from typing import Dict, Any, List, Optional

class ValidationError(Exception):
    """Exception personnalisée pour les erreurs de validation"""
    pass

class Validator:
    """Classe pour valider les données"""
    
    @staticmethod
    def validate_object_id(object_id: str) -> bool:
        """Valide un ObjectId MongoDB"""
        try:
            ObjectId(object_id)
            return True
        except (InvalidId, TypeError):
            return False
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """Valide que les champs requis sont présents"""
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            raise ValidationError(f"Champs requis manquants: {', '.join(missing_fields)}")
    
    @staticmethod
    def validate_string_length(value: str, min_length: int = 1, max_length: int = 255) -> bool:
        """Valide la longueur d'une chaîne"""
        if not isinstance(value, str):
            return False
        return min_length <= len(value.strip()) <= max_length
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valide un format d'email"""
        if not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie les données en supprimant les champs vides et en trimant les chaînes"""
        sanitized = {}
        
        for key, value in data.items():
            if value is not None:
                if isinstance(value, str):
                    value = value.strip()
                    if value:  # Ajouter seulement si non vide après trim
                        sanitized[key] = value
                else:
                    sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def validate_pagination_params(page: str, per_page: str) -> tuple:
        """Valide et convertit les paramètres de pagination"""
        try:
            page = int(page) if page else 1
            per_page = int(per_page) if per_page else 10
            
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 100:  # Limite maximale
                per_page = 10
                
            return page, per_page
        except (ValueError, TypeError):
            return 1, 10