"""
Gestionnaire des feedbacks dans la base de données.
"""

import hashlib
import sqlite3

class FeedbackManager:
    """Gestionnaire des feedbacks stockés."""
    
    def __init__(self, connection_provider):
        """
        Initialise le gestionnaire de feedbacks.
        
        Args:
            connection_provider: Fournisseur de connexion à la base de données
        """
        self.connection_provider = connection_provider
    
    def add_feedback(self, student_name, assessment_id, feedback_content, global_grade=None):
        """
        Ajoute un feedback dans la base de données.
        
        Args:
            student_name (str): Nom de l'étudiant
            assessment_id (str): ID de l'évaluation (peut être None)
            feedback_content (str): Contenu du feedback
            global_grade (str, optional): Note globale
            
        Returns:
            int: ID du feedback dans la base de données, ou -1 en cas d'erreur
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            # Générer un hash du feedback pour éviter les doublons
            # On combine le nom de l'étudiant, l'ID de l'évaluation et le contenu
            content_to_hash = f"{student_name}_{assessment_id}_{feedback_content[:100]}"
            hash_id = hashlib.md5(content_to_hash.encode('utf-8')).hexdigest()
            
            # Vérifier si un feedback avec ce hash existe déjà
            cursor.execute('SELECT id FROM feedbacks WHERE hash_id = ?', (hash_id,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"Un feedback similaire existe déjà pour {student_name} (ID: {existing[0]})")
                # Mettre à jour le feedback existant
                cursor.execute('''
                UPDATE feedbacks
                SET feedback_content = ?, global_grade = ?, creation_date = CURRENT_TIMESTAMP
                WHERE hash_id = ?
                ''', (feedback_content, global_grade, hash_id))
                feedback_id = existing[0]
            else:
                # Ajouter un nouveau feedback
                cursor.execute('''
                INSERT INTO feedbacks (student_name, assessment_id, feedback_content, global_grade, hash_id)
                VALUES (?, ?, ?, ?, ?)
                ''', (student_name, assessment_id, feedback_content, global_grade, hash_id))
                feedback_id = cursor.lastrowid
            
            conn.commit()
            return feedback_id
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de l'ajout du feedback pour {student_name}: {e}")
            conn.rollback()
            return -1
    
    def get_feedback(self, feedback_id):
        """
        Récupère un feedback par son ID.
        
        Args:
            feedback_id (int): ID du feedback
            
        Returns:
            dict: Données du feedback, None si non trouvé
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, student_name, assessment_id, feedback_content, global_grade, creation_date
            FROM feedbacks
            WHERE id = ?
            ''', (feedback_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'student_name': row[1],
                    'assessment_id': row[2],
                    'feedback_content': row[3],
                    'global_grade': row[4],
                    'creation_date': row[5]
                }
            return None
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération du feedback {feedback_id}: {e}")
            return None
    
    def get_student_feedbacks(self, student_name):
        """
        Récupère tous les feedbacks d'un étudiant.
        
        Args:
            student_name (str): Nom de l'étudiant
            
        Returns:
            list: Liste des feedbacks de l'étudiant
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, student_name, assessment_id, feedback_content, global_grade, creation_date
            FROM feedbacks
            WHERE student_name = ?
            ORDER BY creation_date DESC
            ''', (student_name,))
            
            result = []
            for row in cursor.fetchall():
                feedback = {
                    'id': row[0],
                    'student_name': row[1],
                    'assessment_id': row[2],
                    'feedback_content': row[3],
                    'global_grade': row[4],
                    'creation_date': row[5]
                }
                result.append(feedback)
                
            return result
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération des feedbacks pour {student_name}: {e}")
            return []
    
    def get_assessment_feedbacks(self, assessment_id):
        """
        Récupère tous les feedbacks d'une évaluation.
        
        Args:
            assessment_id (str): ID de l'évaluation
            
        Returns:
            list: Liste des feedbacks de l'évaluation
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, student_name, assessment_id, feedback_content, global_grade, creation_date
            FROM feedbacks
            WHERE assessment_id = ?
            ORDER BY student_name, creation_date DESC
            ''', (assessment_id,))
            
            result = []
            for row in cursor.fetchall():
                feedback = {
                    'id': row[0],
                    'student_name': row[1],
                    'assessment_id': row[2],
                    'feedback_content': row[3],
                    'global_grade': row[4],
                    'creation_date': row[5]
                }
                result.append(feedback)
                
            return result
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération des feedbacks pour l'évaluation {assessment_id}: {e}")
            return []
    
    def get_all_feedbacks(self):
        """
        Récupère tous les feedbacks de la base de données.
        
        Returns:
            list: Liste de tous les feedbacks
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT id, student_name, assessment_id, feedback_content, global_grade, creation_date
            FROM feedbacks
            ORDER BY creation_date DESC
            ''')
            
            result = []
            for row in cursor.fetchall():
                feedback = {
                    'id': row[0],
                    'student_name': row[1],
                    'assessment_id': row[2],
                    'feedback_content': row[3],
                    'global_grade': row[4],
                    'creation_date': row[5]
                }
                result.append(feedback)
                
            return result
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération de tous les feedbacks: {e}")
            return []
    
    def delete_feedback(self, feedback_id):
        """
        Supprime un feedback.
        
        Args:
            feedback_id (int): ID du feedback à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        conn = self.connection_provider.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM feedbacks WHERE id = ?', (feedback_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la suppression du feedback {feedback_id}: {e}")
            conn.rollback()
            return False 