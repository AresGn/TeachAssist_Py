"""
Gestionnaire des configurations d'évaluations dans la base de données.
"""

import json
import sqlite3

class AssessmentManager:
    """Gestionnaire des configurations d'évaluations."""
    
    def __init__(self, connection_provider):
        """
        Initialise le gestionnaire de configurations d'évaluations.
        
        Args:
            connection_provider: Fournisseur de connexion à la base de données
        """
        self.connection_provider = connection_provider
    
    def add_assessment_config(self, config_dict):
        """
        Ajoute ou met à jour une configuration d'évaluation dans la base de données.
        
        Args:
            config_dict (dict): Dictionnaire de configuration de l'évaluation
            
        Returns:
            bool: True si l'opération a réussi
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        assessment_id = config_dict.get('assessmentId')
        if not assessment_id:
            return False
            
        name = config_dict.get('name', '')
        exercises = json.dumps(config_dict.get('exercises', []))
        total_max_points = config_dict.get('totalMaxPoints', 0)
        
        try:
            # Vérifier si l'évaluation existe déjà
            cursor.execute('SELECT id FROM assessment_configs WHERE id = ?', (assessment_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Mise à jour
                cursor.execute('''
                UPDATE assessment_configs
                SET name = ?, exercises = ?, total_max_points = ?,
                    last_modified = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (name, exercises, total_max_points, assessment_id))
            else:
                # Insertion
                cursor.execute('''
                INSERT INTO assessment_configs 
                (id, name, exercises, total_max_points)
                VALUES (?, ?, ?, ?)
                ''', (assessment_id, name, exercises, total_max_points))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de l'ajout de l'évaluation {assessment_id}: {e}")
            conn.rollback()
            return False
    
    def get_assessment_config(self, assessment_id):
        """
        Récupère une configuration d'évaluation par son ID.
        
        Args:
            assessment_id (str): ID de l'évaluation
            
        Returns:
            dict: Configuration de l'évaluation, None si non trouvée
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, name, exercises, total_max_points
            FROM assessment_configs
            WHERE id = ?
            ''', (assessment_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'assessmentId': row[0],
                    'name': row[1],
                    'exercises': json.loads(row[2]),
                    'totalMaxPoints': row[3]
                }
            return None
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération de l'évaluation {assessment_id}: {e}")
            return None
    
    def get_all_assessment_configs(self):
        """
        Récupère toutes les configurations d'évaluations.
        
        Returns:
            dict: Dictionnaire de configurations {id: config_dict}
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, name, exercises, total_max_points
            FROM assessment_configs
            ORDER BY name
            ''')
            
            result = {}
            for row in cursor.fetchall():
                config = {
                    'assessmentId': row[0],
                    'name': row[1],
                    'exercises': json.loads(row[2]),
                    'totalMaxPoints': row[3]
                }
                result[row[0]] = config
                
            return result
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération des évaluations: {e}")
            return {}
    
    def delete_assessment_config(self, assessment_id):
        """
        Supprime une configuration d'évaluation.
        
        Args:
            assessment_id (str): ID de l'évaluation à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM assessment_configs WHERE id = ?', (assessment_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la suppression de l'évaluation {assessment_id}: {e}")
            conn.rollback()
            return False 