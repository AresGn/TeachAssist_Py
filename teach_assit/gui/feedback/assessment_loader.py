"""
Module pour charger dynamiquement les informations sur les TDs et les exercices depuis les fichiers de configuration.
"""

import os
import json
import glob
import logging
from pathlib import Path
import re

class AssessmentLoader:
    """Classe pour charger dynamiquement les informations des TDs et exercices."""
    
    def __init__(self, base_dir=None):
        """Initialise le chargeur d'évaluations.
        
        Args:
            base_dir: Répertoire de base du projet (optionnel)
        """
        self.base_dir = base_dir or os.getcwd()
        self.assessments_dir = os.path.join(self.base_dir, "assessments")
        self.configs_dir = os.path.join(self.base_dir, "configs")
        
        # Cache pour les données chargées
        self.assessments_cache = {}
        self.exercise_configs_cache = {}
        
        # Charger les TDs et les exercices au démarrage
        self.load_all_assessments()
        self.load_all_exercise_configs()
    
    def load_all_assessments(self):
        """Charge tous les fichiers d'évaluation depuis le répertoire assessments."""
        self.assessments_cache = {}
        
        if not os.path.exists(self.assessments_dir):
            logging.warning(f"Le répertoire d'évaluations n'existe pas: {self.assessments_dir}")
            return
        
        for assessment_file in glob.glob(os.path.join(self.assessments_dir, "*.json")):
            try:
                with open(assessment_file, 'r', encoding='utf-8') as f:
                    assessment_data = json.load(f)
                    
                assessment_id = assessment_data.get("assessmentId") or Path(assessment_file).stem
                self.assessments_cache[assessment_id] = assessment_data
                logging.info(f"Évaluation chargée: {assessment_id}")
            except Exception as e:
                logging.error(f"Erreur lors du chargement de l'évaluation {assessment_file}: {e}")
        
        logging.info(f"Nombre total d'évaluations chargées: {len(self.assessments_cache)}")
    
    def load_all_exercise_configs(self):
        """Charge toutes les configurations d'exercices depuis le répertoire configs."""
        self.exercise_configs_cache = {}
        
        if not os.path.exists(self.configs_dir):
            logging.warning(f"Le répertoire de configurations n'existe pas: {self.configs_dir}")
            return
        
        # Recherche des fichiers de configuration dans configs/
        config_files = glob.glob(os.path.join(self.configs_dir, "*.json"))
        logging.info(f"Nombre de fichiers de configuration trouvés dans {self.configs_dir}: {len(config_files)}")
        
        for config_file in config_files:
            try:
                file_name = os.path.basename(config_file)
                logging.info(f"Chargement de la configuration: {file_name}")
                
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                # L'ID est soit défini dans le JSON, soit c'est le nom du fichier sans extension
                exercise_id = config_data.get("id") or Path(config_file).stem
                self.exercise_configs_cache[exercise_id] = config_data
                logging.info(f"Configuration d'exercice chargée: {exercise_id}")
                
                # Stocker également sous forme normalisée pour faciliter la recherche
                normalized_id = self._normalize_exercise_id(exercise_id)
                if normalized_id and normalized_id != exercise_id:
                    self.exercise_configs_cache[normalized_id] = config_data
                    logging.info(f"Configuration également stockée sous forme normalisée: {normalized_id}")
                    
                # Stocker également avec les variantes courantes d'identifiants
                # Par exemple, pour "09-fonction-racine-carree", stocker aussi "fonction-racine-carree", "racine-carree", etc.
                variants = self._generate_id_variants(exercise_id)
                for variant in variants:
                    if variant not in self.exercise_configs_cache:
                        self.exercise_configs_cache[variant] = config_data
                        logging.info(f"Configuration également stockée sous la variante: {variant}")
                
                # Si le fichier a un préfixe numérique comme "09-", stocker aussi sans le préfixe
                if re.match(r'^[0-9]+-', exercise_id):
                    unprefixed_id = re.sub(r'^[0-9]+-', '', exercise_id)
                    self.exercise_configs_cache[unprefixed_id] = config_data
                    logging.info(f"Configuration également stockée sans préfixe: {unprefixed_id}")
                
            except Exception as e:
                logging.error(f"Erreur lors du chargement de la configuration {config_file}: {e}")
        
        logging.info(f"Nombre total de configurations d'exercices chargées: {len(self.exercise_configs_cache)}")
        
    def _normalize_exercise_id(self, exercise_id):
        """Normalise un ID d'exercice pour éviter les problèmes de correspondance."""
        if not exercise_id:
            return ""
            
        # Supprimer les caractères spéciaux sauf les tirets et les soulignés
        normalized = re.sub(r'[^\w\-]', '', exercise_id)
        
        # Remplacer les tirets et soulignés multiples par un seul
        normalized = re.sub(r'[-_]+', '-', normalized)
        
        # Tout en minuscules
        normalized = normalized.lower()
        
        # Supprimer les préfixes numériques communs
        normalized = re.sub(r'^[0-9]+-', '', normalized)
        
        # Gestion des cas spécifiques connus
        if 'racine' in normalized:
            normalized = 'racine-carree'
        elif 'comptage' in normalized or 'mot' in normalized:
            normalized = 'comptage-mots'
        elif 'moyenne' in normalized:
            normalized = 'calcul-moyenne'
        
        return normalized
        
    def _generate_id_variants(self, exercise_id):
        """Génère des variantes d'ID d'exercice pour une meilleure correspondance."""
        variants = []
        
        # Version sans préfixe numérique
        unprefixed = re.sub(r'^[0-9]+-', '', exercise_id)
        if unprefixed != exercise_id:
            variants.append(unprefixed)
            
        # Version avec tirets remplacés par des espaces
        spaced = exercise_id.replace('-', ' ')
        if spaced != exercise_id:
            variants.append(spaced)
            
        # Version sans tirets ni espaces
        plain = exercise_id.replace('-', '').replace(' ', '')
        if plain != exercise_id:
            variants.append(plain)
            
        # Variantes courantes pour certains exercices
        lower_id = exercise_id.lower()
        if 'racine' in lower_id:
            variants.extend(['racine', 'racinecarree', 'racine-carree', 'fonction-racine', 'fonction-racine-carree'])
        elif 'mot' in lower_id or 'comptage' in lower_id:
            variants.extend(['comptage', 'mots', 'comptage-mot', 'comptage-mots', 'comptage-de-mots'])
        elif 'moyenne' in lower_id:
            variants.extend(['moyenne', 'calcul-moyenne', 'calculmoyenne'])
        elif 'intervalle' in lower_id:
            variants.extend(['intervalle', 'intervalles'])
            
        return variants
    
    def get_all_assessments(self):
        """Récupère toutes les évaluations chargées.
        
        Returns:
            dict: Dictionnaire des évaluations (ID -> données)
        """
        return self.assessments_cache
    
    def get_assessment(self, assessment_id):
        """Récupère une évaluation spécifique par son ID.
        
        Args:
            assessment_id: ID de l'évaluation à récupérer
            
        Returns:
            dict: Données de l'évaluation ou None si non trouvée
        """
        return self.assessments_cache.get(assessment_id)
    
    def get_all_exercise_configs(self):
        """Récupère toutes les configurations d'exercices chargées.
        
        Returns:
            dict: Dictionnaire des configurations (ID -> données)
        """
        return self.exercise_configs_cache
    
    def get_exercise_config(self, exercise_id):
        """Récupère une configuration d'exercice spécifique par son ID.
        
        Args:
            exercise_id: ID de l'exercice à récupérer
            
        Returns:
            dict: Configuration de l'exercice ou None si non trouvée
        """
        return self.exercise_configs_cache.get(exercise_id)
    
    def get_exercise_ids_for_assessment(self, assessment_id):
        """Récupère les IDs des exercices pour une évaluation spécifique.
        
        Args:
            assessment_id: ID de l'évaluation
            
        Returns:
            list: Liste des IDs d'exercices pour cette évaluation
        """
        assessment = self.get_assessment(assessment_id)
        if not assessment:
            return []
        
        exercises = assessment.get("exercises", [])
        return [ex.get("exerciseId") for ex in exercises if "exerciseId" in ex]
    
    def get_exercise_patterns(self, exercise_id):
        """Récupère les patterns de recherche pour un exercice.
        
        Args:
            exercise_id: ID de l'exercice
            
        Returns:
            list: Liste de patterns de recherche pour les fichiers de cet exercice
        """
        config = self.get_exercise_config(exercise_id)
        if not config:
            # Extraire le nom de base sans préfixe numérique
            base_name = exercise_id.split('-', 1)[1] if '-' in exercise_id else exercise_id
            return [exercise_id, base_name]
        
        # Patterns de base
        patterns = [exercise_id]
        
        # Ajouter le nom de l'exercice
        name = config.get("name", "")
        if name:
            patterns.append(name.lower().replace(" ", "-"))
            patterns.append(name.lower().replace(" ", ""))
        
        # Extraire les mots-clés de l'ID et de la description
        base_name = exercise_id.split('-', 1)[1] if '-' in exercise_id else exercise_id
        patterns.append(base_name)
        
        description = config.get("description", "")
        if description:
            # Extraire des mots-clés pertinents de la description
            important_keywords = [word.lower() for word in description.split() 
                                if len(word) > 4 and word.lower() not in ["ecrire", "fonction", "methode", "classe"]]
            patterns.extend(important_keywords[:3])  # Limiter aux 3 premiers mots-clés importants
        
        return patterns 