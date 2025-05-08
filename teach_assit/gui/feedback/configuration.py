"""
Gestion de la configuration et des paramètres pour le module de feedback.
"""

import os
import re
import logging

class ConfigManager:
    """Gestionnaire de configuration pour le module de feedback."""
    
    API_KEY_SETTING = "api_key_gemini"
    
    def __init__(self, db_manager=None):
        """
        Initialise le gestionnaire de configuration.
        
        Args:
            db_manager: Gestionnaire de base de données pour stocker/charger les paramètres
        """
        self.db_manager = db_manager
        self.api_key = ""
        
    def load_settings(self):
        """
        Charge les paramètres depuis la base de données.
        
        Returns:
            dict: Dictionnaire des paramètres chargés
        """
        settings = {}
        
        try:
            if self.db_manager:
                # Charger la clé API
                self.api_key = self.db_manager.get_setting(self.API_KEY_SETTING, "")
                settings["api_key"] = self.api_key
                logging.info("Clé API chargée depuis la base de données")
        except Exception as e:
            logging.error(f"Erreur lors du chargement des paramètres: {str(e)}")
            
        return settings
    
    def save_api_key(self, api_key):
        """
        Sauvegarde la clé API dans la base de données.
        
        Args:
            api_key: Clé API à sauvegarder
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        self.api_key = api_key
        
        try:
            if self.db_manager:
                self.db_manager.save_setting(
                    self.API_KEY_SETTING, 
                    self.api_key, 
                    "Clé API Gemini pour la génération de feedback"
                )
                logging.info("Clé API sauvegardée dans la base de données")
                return True
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de la clé API: {str(e)}")
            
        return False
    
    def get_api_key(self):
        """
        Récupère la clé API.
        
        Returns:
            str: Clé API
        """
        return self.api_key


class ExerciseIdNormalizer:
    """Utilitaire pour normaliser les identifiants d'exercices."""
    
    @staticmethod
    def normalize(exercise_id):
        """
        Normalise un identifiant d'exercice pour le rendre plus facilement comparable.
        
        Args:
            exercise_id: Identifiant d'exercice à normaliser
            
        Returns:
            str: Identifiant normalisé
        """
        if not exercise_id:
            return ""
            
        # Supprimer les caractères spéciaux sauf les tirets et les soulignés
        normalized = re.sub(r'[^\w\-]', '', exercise_id)
        
        # Remplacer les tirets et soulignés multiples par un seul
        normalized = re.sub(r'[-_]+', '-', normalized)
        
        # Mettre en minuscules
        normalized = normalized.lower()
        
        # Supprimer les préfixes numériques communs comme "01-", "02-", etc.
        normalized = re.sub(r'^[0-9]+-', '', normalized)
        
        # Si l'ID contient des mots clés spécifiques, les normaliser
        keyword_map = {
            'racinecarree': 'racine-carree',
            'racine': 'racine-carree',
            'comptage': 'comptage-mots',
            'mots': 'comptage-mots',
            'comptage-mot': 'comptage-mots',
            'calcul-moyenne': 'moyenne',
            'moyenne': 'calcul-moyenne',
            'intervalle': 'intervalle'
        }
        
        for keyword, replacement in keyword_map.items():
            if keyword in normalized:
                normalized = replacement
                break
                
        logging.debug(f"ID normalisé: {exercise_id} -> {normalized}")
        return normalized 