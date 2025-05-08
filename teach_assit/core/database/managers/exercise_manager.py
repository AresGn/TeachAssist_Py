"""
Gestionnaire des configurations d'exercices dans la base de données.
"""

import json
import sqlite3

class ExerciseManager:
    """Gestionnaire des configurations d'exercices."""
    
    def __init__(self, connection_provider):
        """
        Initialise le gestionnaire de configurations d'exercices.
        
        Args:
            connection_provider: Fournisseur de connexion à la base de données
        """
        self.connection_provider = connection_provider
    
    def add_exercise_config(self, config_dict):
        """
        Ajoute ou met à jour une configuration d'exercice dans la base de données.
        
        Args:
            config_dict (dict): Dictionnaire de configuration de l'exercice
            
        Returns:
            bool: True si l'opération a réussi
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        exercise_id = config_dict.get('id')
        if not exercise_id:
            return False
            
        name = config_dict.get('name', '')
        description = config_dict.get('description', '')
        test_inputs = json.dumps(config_dict.get('testInputs', []))
        rules = json.dumps(config_dict.get('rules', {}))
        grading_criteria = json.dumps(config_dict.get('grading_criteria', []))
        
        try:
            # Vérifier si l'exercice existe déjà
            cursor.execute('SELECT id FROM exercise_configs WHERE id = ?', (exercise_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Mise à jour
                cursor.execute('''
                UPDATE exercise_configs
                SET name = ?, description = ?, 
                    test_inputs = ?, rules = ?, grading_criteria = ?,
                    last_modified = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (name, description, test_inputs, rules, grading_criteria, exercise_id))
            else:
                # Insertion
                cursor.execute('''
                INSERT INTO exercise_configs 
                (id, name, description, test_inputs, rules, grading_criteria)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (exercise_id, name, description, test_inputs, rules, grading_criteria))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de l'ajout de l'exercice {exercise_id}: {e}")
            conn.rollback()
            return False
    
    def get_exercise_config(self, exercise_id):
        """
        Récupère une configuration d'exercice par son ID.
        
        Args:
            exercise_id (str): ID de l'exercice
            
        Returns:
            dict: Configuration de l'exercice, None si non trouvé
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, name, description, test_inputs, rules, grading_criteria
            FROM exercise_configs
            WHERE id = ?
            ''', (exercise_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'testInputs': json.loads(row[3]),
                    'rules': json.loads(row[4]),
                    'grading_criteria': json.loads(row[5])
                }
            return None
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération de l'exercice {exercise_id}: {e}")
            return None
    
    def get_all_exercise_configs(self):
        """
        Récupère toutes les configurations d'exercices.
        
        Returns:
            dict: Dictionnaire de configurations {id: config_dict}
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, name, description, test_inputs, rules, grading_criteria
            FROM exercise_configs
            ORDER BY name
            ''')
            
            result = {}
            for row in cursor.fetchall():
                config = {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'testInputs': json.loads(row[3]),
                    'rules': json.loads(row[4]),
                    'grading_criteria': json.loads(row[5])
                }
                result[row[0]] = config
                
            return result
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération des exercices: {e}")
            return {}
    
    def delete_exercise_config(self, exercise_id):
        """
        Supprime une configuration d'exercice.
        
        Args:
            exercise_id (str): ID de l'exercice à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM exercise_configs WHERE id = ?', (exercise_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la suppression de l'exercice {exercise_id}: {e}")
            conn.rollback()
            return False 