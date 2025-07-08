#!/usr/bin/env python3
"""
Script d'importation de données CSV vers MongoDB
Usage: python scripts/import_data.py <fichier_csv>
"""

import pandas as pd
import sys
import os
import logging
from datetime import datetime
from typing import List, Dict, Any
import argparse

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils.database import db_manager
from utils.validators import Validator

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import_data.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DataImporter:
    """Classe pour importer des données CSV vers MongoDB"""

    def __init__(self):
        self.batch_size = 1000  # Taille des lots pour l'insertion
        self.total_imported = 0
        self.total_errors = 0

    def validate_csv_file(self, file_path: str) -> bool:
        """Valide l'existence et la lisibilité du fichier CSV"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"Fichier non trouvé: {file_path}")
                return False

            if not os.path.isfile(file_path):
                logger.error(f"Le chemin spécifié n'est pas un fichier: {file_path}")
                return False

            if not file_path.lower().endswith('.csv'):
                logger.error(f"Le fichier doit être au format CSV: {file_path}")
                return False

            # Test de lecture
            pd.read_csv(file_path, nrows=1)
            logger.info(f"Fichier CSV validé: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Erreur lors de la validation du fichier CSV: {str(e)}")
            return False

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les données du DataFrame"""
        logger.info("Nettoyage des données...")

        # Supprimer les lignes complètement vides
        df = df.dropna(how='all')

        # Nettoyer les noms de colonnes
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        # Remplacer les valeurs NaN par None
        df = df.where(pd.notnull(df), None)

        # Supprimer les colonnes complètement vides
        df = df.dropna(axis=1, how='all')

        logger.info(f"Données nettoyées: {len(df)} lignes, {len(df.columns)} colonnes")
        return df

    def prepare_documents(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Prépare les documents pour l'insertion dans MongoDB"""
        logger.info("Préparation des documents...")

        documents = []
        current_time = datetime.utcnow()

        for index, row in df.iterrows():
            try:
                doc = row.to_dict()
                doc = Validator.sanitize_data(doc)
                doc['created_at'] = current_time
                doc['updated_at'] = current_time
                doc['import_source'] = 'csv_import'
                doc['import_row_number'] = index + 2  # +2 pour ignorer l'en-tête

                documents.append(doc)
            except Exception as e:
                logger.warning(f"Erreur ligne {index + 2}: {str(e)}")
                self.total_errors += 1

        logger.info(f"Documents préparés: {len(documents)}")
        return documents

    def import_in_batches(self, documents: List[Dict[str, Any]]) -> bool:
        """Importe les documents par lots"""
        logger.info(f"Importation par lots de {self.batch_size} documents...")

        try:
            collection = db_manager.get_collection()

            if collection is not None:
                for i in range(0, len(documents), self.batch_size):
                    batch = documents[i:i + self.batch_size]
                    try:
                        result = collection.insert_many(batch, ordered=False)
                        self.total_imported += len(result.inserted_ids)
                        logger.info(f"Lot {i//self.batch_size + 1}: {len(result.inserted_ids)} documents importés")
                    except Exception as e:
                        logger.error(f"Erreur lors du lot {i//self.batch_size + 1}: {str(e)}")
                        self.total_errors += len(batch)
                return True
            else:
                logger.error("❌ La collection MongoDB n’a pas été trouvée")
                return False

        except Exception as e:
            logger.error(f"Erreur générale lors de l'importation: {str(e)}")
            return False

    def import_csv(self, file_path: str, drop_existing: bool = False) -> bool:
        """Importe un fichier CSV complet"""
        logger.info(f"Début de l'importation: {file_path}")
        start_time = datetime.now()

        try:
            if not self.validate_csv_file(file_path):
                return False

            if drop_existing:
                logger.info("Suppression des données existantes...")
                collection = db_manager.get_collection()
                if collection is not None:
                    result = collection.delete_many({})
                    logger.info(f"Supprimées: {result.deleted_count} documents")
                else:
                    logger.error("❌ Impossible de supprimer : collection MongoDB introuvable")
                    return False

            logger.info("Lecture du fichier CSV...")
            df = pd.read_csv(file_path, encoding='utf-8')
            logger.info(f"Fichier lu: {len(df)} lignes, {len(df.columns)} colonnes")

            df = self.clean_data(df)
            if len(df) == 0:
                logger.warning("Aucune donnée à importer après nettoyage")
                return False

            documents = self.prepare_documents(df)
            if len(documents) == 0:
                logger.warning("Aucun document à importer")
                return False

            success = self.import_in_batches(documents)

            end_time = datetime.now()
            duration = end_time - start_time

            logger.info("=" * 50)
            logger.info("RAPPORT D'IMPORTATION")
            logger.info("=" * 50)
            logger.info(f"Fichier: {file_path}")
            logger.info(f"Durée: {duration}")
            logger.info(f"Total lignes CSV: {len(df)}")
            logger.info(f"Documents importés: {self.total_imported}")
            logger.info(f"Erreurs: {self.total_errors}")
            logger.info(f"Taux de réussite: {(self.total_imported / len(documents)) * 100:.2f}%")
            logger.info("=" * 50)

            return success

        except Exception as e:
            logger.error(f"Erreur fatale lors de l'importation: {str(e)}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Importer des données CSV vers MongoDB')
    parser.add_argument('csv_file', help='Chemin vers le fichier CSV')
    parser.add_argument('--drop-existing', action='store_true', help='Supprimer les données existantes avant import')
    parser.add_argument('--batch-size', type=int, default=1000, help='Taille des lots (défaut: 1000)')

    args = parser.parse_args()

    try:
        Config.validate_config()
        db_manager.connect()
        logger.info("Connexion à MongoDB établie")

        importer = DataImporter()
        importer.batch_size = args.batch_size

        success = importer.import_csv(args.csv_file, args.drop_existing)

        if success:
            logger.info("Importation terminée avec succès!")
            sys.exit(0)
        else:
            logger.error("Importation échouée!")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Erreur critique: {str(e)}")
        sys.exit(1)
    finally:
        db_manager.close()


if __name__ == '__main__':
    main()
