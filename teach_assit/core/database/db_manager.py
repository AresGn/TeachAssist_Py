"""
Gestionnaire de base de données SQLite pour TeachAssist.
Permet de stocker les informations sur les fichiers ZIP et les dossiers extraits.
"""

import os
import sqlite3
import datetime
from pathlib import Path

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
            
            # Supprime les dossiers
            cursor.execute('DELETE FROM extracted_folders WHERE zip_id = ?', (zip_id,))
            
            # Supprime le fichier ZIP
            cursor.execute('DELETE FROM zip_files WHERE id = ?', (zip_id,))
            
            conn.commit()
            success = True
        except sqlite3.Error:
            conn.rollback()
            success = False
        finally:
            conn.close()
        
        return success
    
    def update_extracted_folder_status(self, folder_id, status):
        """
        Met à jour le statut d'un dossier extrait.
        
        Args:
            folder_id (int): ID du dossier
            status (str): Nouveau statut ('active', 'archived', 'deleted')
            
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
            success = True
        except sqlite3.Error:
            conn.rollback()
            success = False
        finally:
            conn.close()
        
        return success 