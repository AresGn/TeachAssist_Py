"""
Gestionnaire de base de données SQLite pour TeachAssist.
Permet de stocker les informations sur les fichiers ZIP et les dossiers extraits.
"""

import os
import sqlite3
import datetime
from pathlib import Path
import json

class DatabaseManager:
    """Gestionnaire de base de données SQLite pour l'application TeachAssist."""
    
    def __init__(self, db_path=None):
        """
        Initialise le gestionnaire de base de données.
        
        Args:
            db_path (str, optional): Chemin vers le fichier de base de données.
                Si None, utilise le dossier data à la racine du projet.
        """
        if db_path is None:
            # Utilise le dossier data à la racine du projet
            project_root = Path(__file__).parent.parent.parent.parent
            data_dir = project_root / "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            self.db_path = str(data_dir / "teachassist.db")
        else:
            self.db_path = db_path
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialise la structure de la base de données si elle n'existe pas."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table pour les fichiers ZIP
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS zip_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            md5_hash TEXT,
            description TEXT
        )
        ''')
        
        # Table pour les dossiers extraits
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zip_id INTEGER NOT NULL,
            folder_path TEXT NOT NULL,
            extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (zip_id) REFERENCES zip_files (id)
        )
        ''')
        
        # Table pour les fichiers individuels dans les dossiers extraits
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_id INTEGER NOT NULL,
            filepath TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_type TEXT,
            FOREIGN KEY (folder_id) REFERENCES extracted_folders (id)
        )
        ''')
        
        # Table pour les configurations d'exercices
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercise_configs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            difficulty INTEGER DEFAULT 1,
            test_inputs TEXT,  -- Stockage JSON des entrées de test
            rules TEXT,        -- Stockage JSON des règles
            grading_criteria TEXT,  -- Stockage JSON des critères d'évaluation
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table pour les configurations d'évaluations
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessment_configs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            exercises TEXT,     -- Stockage JSON des exercices
            total_max_points INTEGER DEFAULT 0,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table pour les paramètres de l'application
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS application_settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            description TEXT,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_zip_file(self, filename, filepath, file_size, md5_hash=None, description=None):
        """
        Ajoute un fichier ZIP à la base de données.
        
        Args:
            filename (str): Nom du fichier ZIP
            filepath (str): Chemin complet vers le fichier
            file_size (int): Taille du fichier en octets
            md5_hash (str, optional): Hash MD5 du fichier pour vérification
            description (str, optional): Description du contenu du ZIP
            
        Returns:
            int: ID du fichier ZIP dans la base de données
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO zip_files (filename, filepath, file_size, md5_hash, description)
        VALUES (?, ?, ?, ?, ?)
        ''', (filename, filepath, file_size, md5_hash, description))
        
        zip_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return zip_id
    
    def add_extracted_folder(self, zip_id, folder_path):
        """
        Ajoute un dossier extrait à la base de données.
        
        Args:
            zip_id (int): ID du fichier ZIP d'origine
            folder_path (str): Chemin vers le dossier extrait
            
        Returns:
            int: ID du dossier extrait
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO extracted_folders (zip_id, folder_path)
        VALUES (?, ?)
        ''', (zip_id, folder_path))
        
        folder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return folder_id
    
    def add_extracted_file(self, folder_id, filepath, file_size, file_type=None):
        """
        Ajoute un fichier extrait à la base de données.
        
        Args:
            folder_id (int): ID du dossier contenant le fichier
            filepath (str): Chemin vers le fichier
            file_size (int): Taille du fichier en octets
            file_type (str, optional): Type du fichier (extension)
            
        Returns:
            int: ID du fichier extrait
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO extracted_files (folder_id, filepath, file_size, file_type)
        VALUES (?, ?, ?, ?)
        ''', (folder_id, filepath, file_size, file_type))
        
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return file_id
    
    def get_all_zip_files(self):
        """
        Récupère tous les fichiers ZIP stockés dans la base de données.
        
        Returns:
            list: Liste de tuples contenant les informations des fichiers ZIP
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, filename, filepath, file_size, upload_date, md5_hash, description
        FROM zip_files
        ORDER BY upload_date DESC
        ''')
        
        result = cursor.fetchall()
        conn.close()
        
        return result
    
    def get_extracted_folders_by_zip(self, zip_id):
        """
        Récupère tous les dossiers extraits pour un fichier ZIP donné.
        
        Args:
            zip_id (int): ID du fichier ZIP
            
        Returns:
            list: Liste de tuples contenant les informations des dossiers
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, folder_path, extraction_date, status
        FROM extracted_folders
        WHERE zip_id = ?
        ORDER BY extraction_date DESC
        ''', (zip_id,))
        
        result = cursor.fetchall()
        conn.close()
        
        return result
    
    def get_files_by_folder(self, folder_id):
        """
        Récupère tous les fichiers d'un dossier extrait.
        
        Args:
            folder_id (int): ID du dossier
            
        Returns:
            list: Liste de tuples contenant les informations des fichiers
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, filepath, file_size, file_type
        FROM extracted_files
        WHERE folder_id = ?
        ''', (folder_id,))
        
        result = cursor.fetchall()
        conn.close()
        
        return result
    
    def delete_zip_file(self, zip_id):
        """
        Supprime un fichier ZIP et tous ses dossiers/fichiers associés.
        
        Args:
            zip_id (int): ID du fichier ZIP à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Récupère tous les dossiers extraits
            cursor.execute('SELECT id FROM extracted_folders WHERE zip_id = ?', (zip_id,))
            folder_ids = [row[0] for row in cursor.fetchall()]
            
            # Supprime les fichiers extraits
            for folder_id in folder_ids:
                cursor.execute('DELETE FROM extracted_files WHERE folder_id = ?', (folder_id,))
            
            # Supprime les dossiers extraits
            cursor.execute('DELETE FROM extracted_folders WHERE zip_id = ?', (zip_id,))
            
            # Supprime le fichier ZIP
            cursor.execute('DELETE FROM zip_files WHERE id = ?', (zip_id,))
            
            conn.commit()
            return True
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_extracted_folder_status(self, folder_id, status):
        """
        Met à jour le statut d'un dossier extrait.
        
        Args:
            folder_id (int): ID du dossier
            status (str): Nouveau statut ('active', 'archived', etc.)
            
        Returns:
            bool: True si la mise à jour a réussi
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE extracted_folders
            SET status = ?
            WHERE id = ?
            ''', (status, folder_id))
            
            conn.commit()
            return True
        except sqlite3.Error:
            conn.rollback()
            return False
        finally:
            conn.close()
            
    # Méthodes pour gérer les configurations d'exercices
    
    def add_exercise_config(self, config_dict):
        """
        Ajoute ou met à jour une configuration d'exercice dans la base de données.
        
        Args:
            config_dict (dict): Dictionnaire de configuration de l'exercice
            
        Returns:
            bool: True si l'opération a réussi
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        exercise_id = config_dict.get('id')
        if not exercise_id:
            conn.close()
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
        finally:
            conn.close()
            
    def get_exercise_config(self, exercise_id):
        """
        Récupère une configuration d'exercice par son ID.
        
        Args:
            exercise_id (str): ID de l'exercice
            
        Returns:
            dict: Configuration de l'exercice, None si non trouvé
        """
        conn = sqlite3.connect(self.db_path)
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
        finally:
            conn.close()
            
    def get_all_exercise_configs(self):
        """
        Récupère toutes les configurations d'exercices.
        
        Returns:
            dict: Dictionnaire de configurations {id: config_dict}
        """
        conn = sqlite3.connect(self.db_path)
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
        finally:
            conn.close()
            
    def delete_exercise_config(self, exercise_id):
        """
        Supprime une configuration d'exercice.
        
        Args:
            exercise_id (str): ID de l'exercice à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM exercise_configs WHERE id = ?', (exercise_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la suppression de l'exercice {exercise_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
            
    # Méthodes pour gérer les configurations d'évaluations
    
    def add_assessment_config(self, config_dict):
        """
        Ajoute ou met à jour une configuration d'évaluation dans la base de données.
        
        Args:
            config_dict (dict): Dictionnaire de configuration de l'évaluation
            
        Returns:
            bool: True si l'opération a réussi
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        assessment_id = config_dict.get('assessmentId')
        if not assessment_id:
            conn.close()
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
        finally:
            conn.close()
            
    def get_assessment_config(self, assessment_id):
        """
        Récupère une configuration d'évaluation par son ID.
        
        Args:
            assessment_id (str): ID de l'évaluation
            
        Returns:
            dict: Configuration de l'évaluation, None si non trouvée
        """
        conn = sqlite3.connect(self.db_path)
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
        finally:
            conn.close()
            
    def get_all_assessment_configs(self):
        """
        Récupère toutes les configurations d'évaluations.
        
        Returns:
            dict: Dictionnaire de configurations {id: config_dict}
        """
        conn = sqlite3.connect(self.db_path)
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
        finally:
            conn.close()
        
    def delete_assessment_config(self, assessment_id):
        """
        Supprime une configuration d'évaluation.
        
        Args:
            assessment_id (str): ID de l'évaluation à supprimer
            
        Returns:
            bool: True si la suppression a réussi
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM assessment_configs WHERE id = ?', (assessment_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la suppression de l'évaluation {assessment_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    # Méthodes pour gérer les paramètres de l'application
    
    def save_setting(self, key, value, description=None):
        """
        Sauvegarde un paramètre dans la base de données.
        
        Args:
            key (str): Clé du paramètre
            value (str): Valeur du paramètre
            description (str, optional): Description du paramètre
            
        Returns:
            bool: True si l'opération a réussi
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Vérifier si le paramètre existe déjà
            cursor.execute('SELECT key FROM application_settings WHERE key = ?', (key,))
            existing = cursor.fetchone()
            
            if existing:
                # Mise à jour
                cursor.execute('''
                UPDATE application_settings
                SET value = ?, description = ?,
                    last_modified = CURRENT_TIMESTAMP
                WHERE key = ?
                ''', (value, description, key))
            else:
                # Insertion
                cursor.execute('''
                INSERT INTO application_settings 
                (key, value, description)
                VALUES (?, ?, ?)
                ''', (key, value, description))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la sauvegarde du paramètre {key}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_setting(self, key, default_value=None):
        """
        Récupère la valeur d'un paramètre.
        
        Args:
            key (str): Clé du paramètre
            default_value: Valeur par défaut si le paramètre n'existe pas
            
        Returns:
            str: Valeur du paramètre ou default_value si non trouvé
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT value FROM application_settings
            WHERE key = ?
            ''', (key,))
            
            row = cursor.fetchone()
            
            if row:
                return row[0]
            return default_value
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération du paramètre {key}: {e}")
            return default_value
        finally:
            conn.close()
    
    def delete_setting(self, key):
        """
        Supprime un paramètre.
        
        Args:
            key (str): Clé du paramètre
            
        Returns:
            bool: True si l'opération a réussi
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            DELETE FROM application_settings
            WHERE key = ?
            ''', (key,))
            
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la suppression du paramètre {key}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_all_settings(self):
        """
        Récupère tous les paramètres.
        
        Returns:
            dict: Dictionnaire {clé: valeur} de tous les paramètres
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT key, value FROM application_settings
            ''')
            
            settings = {}
            for row in cursor.fetchall():
                settings[row[0]] = row[1]
            
            return settings
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération des paramètres: {e}")
            return {}
        finally:
            conn.close() 